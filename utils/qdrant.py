import os

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "default")
QDRANT_IMAGE_COUNT = os.getenv("QDRANT_IMAGE_COUNT", 5)


client = QdrantClient(QDRANT_URL)

if not client.collection_exists(QDRANT_COLLECTION_NAME):
    client.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config={
            f"image{i}": VectorParams(size=768, distance=Distance.COSINE)
            for i in range(QDRANT_IMAGE_COUNT)
        },
    )


def get_number_of_images_to_check():
    return QDRANT_IMAGE_COUNT


def add_point(id, vectors, payload):
    client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=[{"id": id, "vector": vectors, "payload": payload}],
    )


def search(text_vector, top_k=5):
    payload_id_2_score = {}
    payload_id_2_payload = {}

    for i in range(QDRANT_IMAGE_COUNT):
        tmp_result = client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            using=f"image{i}",
            query=text_vector,
            limit=top_k,
        ).model_dump()["points"]

        for result in tmp_result:
            payload = result["payload"]
            payload_id = payload["id"]

            if payload_id not in payload_id_2_payload:
                payload_id_2_payload[payload_id] = payload

            if payload_id not in payload_id_2_score:
                payload_id_2_score[payload_id] = 0

            payload_id_2_score[payload_id] = max(
                payload_id_2_score[payload_id], result["score"]
            )

    sorted_payloads = sorted(
        payload_id_2_score.items(), key=lambda x: x[1], reverse=True
    )
    return [payload_id_2_payload[payload_id] for payload_id, _ in sorted_payloads]
