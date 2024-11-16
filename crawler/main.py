import os
import json
import random
import time

import pika

rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
rabbitmq_port = os.getenv("RABBITMQ_PORT", 5672)
rabbitmq_user = os.getenv("RABBITMQ_USERNAME", "user")
rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "password")
rabbitmq_channel = os.getenv("RABBITMQ_CHANNEL", "channel")


def _read_data():
    print("Reading data from data.json")
    data_file = open("data.json", "r")
    data = json.load(data_file)
    data_file.close()
    return data


def _create_rabbitmq_channel():
    print(
        f"Connecting to RabbitMQ at {rabbitmq_host}:{rabbitmq_port} as {rabbitmq_user}"
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password),
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_channel)
    return channel, connection


def _send_to_queue(channel, data):
    channel.basic_publish(exchange="", routing_key=rabbitmq_channel, body=json.dumps(data))
    print(f"Sent {data['id']} to queue")


def main():
    data = _read_data()
    channel, connection = _create_rabbitmq_channel()

    while True:
        time.sleep(5)
        random_chosen_data = random.choice(data)
        try:
            _send_to_queue(channel, random_chosen_data)
        except Exception as e:
            print(f"Failed to send data to queue: {e}")
            connection.close()
            break


if __name__ == "__main__":
    main()
