from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict
import hashlib
import numpy as np
import os

client = QdrantClient(host=os.getenv("QDRANT_HOST", "localhost"), port=int(os.getenv("QDRANT_PORT", 6333)))

def create_collection_if_not_exists(collection: str, vector_size: int = 384):
    if collection not in [c.name for c in client.get_collections().collections]:
        client.recreate_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )

def save_report_vectors(collection: str, uuid: str, vectors: np.ndarray, chunks: List[Dict]):
    create_collection_if_not_exists(collection)
    points = []
    for i, (vector, chunk) in enumerate(zip(vectors, chunks)):
        point_id = int(hashlib.sha256((uuid + str(i)).encode()).hexdigest(), 16) % (10**16)
        payload = {
            "uuid": uuid,
            **chunk["metadata"]
        }
        points.append(PointStruct(id=point_id, vector=vector.tolist(), payload=payload))
    client.upsert(collection_name=collection, points=points)

def get_previous_uuids(collection: str) -> List[str]:
    try:
        response = client.scroll(collection_name=collection, limit=1000)
        return sorted({p.payload["uuid"] for p in response[0]})
    except:
        return []

def delete_oldest_uuid(collection: str, uuids: List[str]):
    if len(uuids) <= 3:
        return
    oldest = uuids[0]
    client.delete(
        collection_name=collection,
        filter=Filter(
            must=[FieldCondition(key="uuid", match=MatchValue(value=oldest))]
        )
    )