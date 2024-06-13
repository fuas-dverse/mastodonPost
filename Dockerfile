# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

# Set environment variables
ENV MASTODON_ACCESS_TOKEN=${MASTODON_ACCESS_TOKEN}
ENV MASTODON_API_BASE_URL=${MASTODON_API_BASE_URL}
ENV KAFKA_BOOTSTRAP_SERVER=${KAFKA_BOOTSTRAP_SERVER}
ENV KAFKA_SECURITY_PROTOCOL=${KAFKA_SECURITY_PROTOCOL}
ENV KAFKA_SASL_MECHANISMS=${KAFKA_SASL_MECHANISMS}
ENV KAFKA_SASL_USERNAME=${KAFKA_SASL_USERNAME}
ENV KAFKA_SASL_PASSWORD=${KAFKA_SASL_PASSWORD}

# Run the main.py script when the container launches
CMD ["python", "main.py"]