import pika
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)
RABBITMQ_USER = os.getenv("RABBITMQ_USERNAME", "user")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASSWORD", "password")


def create_channel(queue: str):
    assert queue, "Queue name is required"

    print(
        f"Connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT} as {RABBITMQ_USER}"
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    return channel


def send_to_queue(channel, queue, body):
    channel.basic_publish(exchange="", routing_key=queue, body=body)
    print(f"Sent data to queue {queue}")


def set_consumer(channel, queue, callback):
    channel.basic_consume(queue=queue, on_message_callback=callback)
    print(f"Waiting for messages on queue {queue}")
    channel.start_consuming()


def close_connection(channel):
    channel.connection.close()
    print("Connection closed")
