import os
from typing import Optional

from qdrant_client import QdrantClient, models
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


def _sort_results(payloads, top_k):
    payload_id_2_score = {}
    payload_id_2_payload = {}

    for payload in payloads:
        payload_id = payload["id"]

        if payload_id not in payload_id_2_payload:
            payload_id_2_payload[payload_id] = payload

        if payload_id not in payload_id_2_score:
            payload_id_2_score[payload_id] = 0

        payload_id_2_score[payload_id] = max(
            payload_id_2_score[payload_id], payload["score"]
        )

    sorted_payloads = sorted(
        payload_id_2_score.items(), key=lambda x: x[1], reverse=True
    )
    return [
        payload_id_2_payload[payload_id] for payload_id, _ in sorted_payloads[:top_k]
    ]


def search(
    text_vector,
    price_from: Optional[int] = None,
    price_to: Optional[int] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    brand_name: Optional[str] = None,
    status: Optional[str] = None,
    gender: Optional[str] = None,
    top_k=5,
):
    payloads = []

    must = [
        models.FieldCondition(
            key="current_price",
            range=models.Range(
                gte=price_from,
                lte=price_to,
            ),
        )
    ]

    values_to_add = {
        "status": status,
        "region": region,
        "category": category,
        "brand_name": brand_name,
        "gender": gender,
    }
    for key, value in values_to_add.items():
        if value and value != "other...":
            must.append(
                models.FieldCondition(
                    key=key,
                    match=models.MatchValue(
                        value=value,
                    ),
                )
            )

    for i in range(QDRANT_IMAGE_COUNT):
        tmp_result = client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            using=f"image{i}",
            query=text_vector,
            query_filter=models.Filter(must=must),
            limit=top_k,
        ).model_dump()["points"]

        payloads.extend(tmp_result)

    return _sort_results(payloads, top_k)


def get_all_possible_values(data_name: str = None):
    points, _ = client.scroll(QDRANT_COLLECTION_NAME, limit=1000)
    data_values = set()
    for point in points:
        data_value = point.payload.get(data_name)
        if data_value:
            data_values.add(data_value)

    result = list(data_values)
    result.append("other...")
    return result
