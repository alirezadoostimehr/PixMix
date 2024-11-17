from utils import tokenizer, qdrant, rabbit
import os
import time
import json

RABBITMQ_QUEUE = os.getenv("RABBITMQ_CRAWLER_QUEUE", "crawler_queue")


def _entity_cleaner(entity):
    removing_fields = [
        "brand_id",
        "category_id",
        "gender_id",
        "shop_id",
    ]
    for field in removing_fields:
        entity.pop(field)
    return entity


def callback(ch, method, properties, body):
    print("Consuming created")

    cleaned_entity = _entity_cleaner(entity=json.loads(body.decode("utf-8")))
    image_vectors = [
        tokenizer.get_image_vectors(image_url)
        for image_url in cleaned_entity["images"][
            : qdrant.get_number_of_images_to_check()
        ]
    ]
    entity_vectors = {f"image{i}": vector for i, vector in enumerate(image_vectors)}
    entity_id = cleaned_entity["id"]

    qdrant.add_point(
        id=entity_id,
        vectors=entity_vectors,
        payload=cleaned_entity,
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

    print(f"Consumed {entity_id}")
    time.sleep(20)


def start():
    channel = rabbit.create_channel(RABBITMQ_QUEUE)
    try:
        channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
        channel.start_consuming()
    except KeyboardInterrupt:
        rabbit.close_connection(channel)
        print("Connection closed")
        print("Exiting...")
