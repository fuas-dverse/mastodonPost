import logging
import os
import time
from mastodon import Mastodon
from KafkaManager import KafkaManager
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)


def load_environment():
    load_dotenv()
    required_vars = ['MASTODON_ACCESS_TOKEN', 'MASTODON_API_BASE_URL', 'KAFKA_BOOTSTRAP_SERVER',
                     'KAFKA_SECURITY_PROTOCOL', 'KAFKA_SASL_MECHANISMS', 'KAFKA_SASL_USERNAME', 'KAFKA_SASL_PASSWORD']
    for var in required_vars:
        if not os.environ.get(var):
            raise ValueError(f"Environment variable {var} is not set.")


def create_mastodon_client():
    return Mastodon(
        access_token=os.environ.get('MASTODON_ACCESS_TOKEN'),
        api_base_url=os.environ.get('MASTODON_API_BASE_URL')
    )


def process_nlp_message(message):
    nlp_output = message
    content_item = nlp_output['content'][0]
    intent = content_item['intent']
    steps = content_item['steps']
    last_step = steps[-1]
    return intent, last_step


def format_mastodon_message(intent, results):
    return f"Hoi! Dverse team here! Check out what our bots found about '{intent}': {results}"


def post_to_mastodon(mastodon, message):
    mastodon.status_post(message)


def main():
    load_environment()
    mastodon = create_mastodon_client()
    kafka_manager = KafkaManager()

    try:
        while True:
            msg = kafka_manager.consume_message('nlp.output')
            if msg is None:
                time.sleep(5)
                continue

            intent, last_step = process_nlp_message(msg)
            final_output_topic = f"{last_step}.output"
            if last_step == "google_search_agent":
                final_output_topic = "google_search.output"

            step_output_msg = kafka_manager.consume_message(final_output_topic)
            if step_output_msg is None:
                logging.warning("No message received or error from final output topic.")
                continue

            final_output = step_output_msg
            results = final_output['content'][-1]['message']

            formatted_message = format_mastodon_message(intent, results)
            post_to_mastodon(mastodon, formatted_message)

            time.sleep(5)

    finally:
        kafka_manager.close()


if __name__ == '__main__':
    main()


