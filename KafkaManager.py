import json
import logging
import os
import threading
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic, TopicPartition, KafkaException, KafkaError
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


class KafkaManager:
    def __init__(self, group_id="default"):
        config = {
            'bootstrap.servers': os.environ.get("KAFKA_BOOTSTRAP_SERVER"),
            'security.protocol': os.environ.get("KAFKA_SECURITY_PROTOCOL"),
            'sasl.mechanisms': os.environ.get("KAFKA_SASL_MECHANISMS"),
            'sasl.username': os.environ.get("KAFKA_SASL_USERNAME"),
            'sasl.password': os.environ.get("KAFKA_SASL_PASSWORD"),
        }

        self.admin = AdminClient(config)
        self.producer = Producer(config)

        config['group.id'] = group_id
        config['auto.offset.reset'] = 'earliest'

        self.consumer = Consumer(config)
        self.subscriptions = {}

    def send_message(self, topic, message, key=None):
        self.__create_non_existing_topics(topic)
        headers = {'requestId': key}
        if isinstance(message, dict):
            message = str(message)
        self.producer.produce(topic, value=message.encode('utf-8'), headers=headers)
        self.producer.flush()

    def start_consuming(self):
        for topic, callback in self.subscriptions.items():
            threading.Thread(target=self.__consume_messages, args=(topic, callback)).start()

    def subscribe(self, topic, callback):
        self.__create_non_existing_topics(topic)
        self.subscriptions[topic] = callback

    def __list_topics(self):
        return self.admin.list_topics().topics

    def __create_topic(self, topic, partitions=1, replication=3):
        new_topic = NewTopic(topic, num_partitions=partitions, replication_factor=replication)
        fs = self.admin.create_topics([new_topic])
        for topic, f in fs.items():
            try:
                f.result()
            except Exception as e:
                logging.error(f"Failed to create topic {topic}: {e}")

    def __create_non_existing_topics(self, topic):
        if "^" not in topic:
            if topic not in self.__list_topics():
                self.__create_topic(topic)

    def consume_message(self, topic, timeout=1.0):
        self.consumer.subscribe([topic])
        while True:
            msg = self.consumer.poll(timeout)
            if msg is None or msg.error():
                if msg and msg.error().code() != KafkaError._PARTITION_EOF:
                    logging.error(f"Error: {msg.error()}")
                continue
            x = msg.value().decode('utf-8')
            x = x.replace("'", "\"")
            message = json.loads(x)
            return message

    def close(self):
        logging.info("Closing Kafka consumer.")
        self.consumer.close()

