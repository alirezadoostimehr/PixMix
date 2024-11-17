import os
import json
import random
import time

from utils import rabbit

RABBITMQ_QUEUE = os.getenv("RABBITMQ_CRAWLER_QUEUE", "crawler_queue")

current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(current_dir, "..", "assets")
data_path = os.path.join(assets_dir, "data.json")


def _read_data():
    print("Reading data from data.json")
    data_file = open(data_path, "r")
    data = json.load(data_file)
    data_file.close()
    return data


def start():
    data = _read_data()
    channel = rabbit.create_channel(queue=RABBITMQ_QUEUE)

    while True:
        time.sleep(10)
        random_chosen_data = random.choice(data)
        try:
            rabbit.send_to_queue(
                channel=channel,
                queue=RABBITMQ_QUEUE,
                body=json.dumps(random_chosen_data),
            )
        except Exception as e:
            print(f"Failed to send data to queue: {e}")
            rabbit.close_connection(channel=channel)
            break
