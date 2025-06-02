import os
import uuid
import re
import unidecode
from typing import List, Dict, Tuple
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse

# ⛔️ Убрали api_key
QDRANT_HOST = os.getenv("QDRANT_HOST", "http://localhost:6333")
client = QdrantClient(
    url=QDRANT_HOST,
    prefer_grpc=False,
    timeout=60.0,
    check_compatibility=False
)


def normalize_collection_name(name: str) -> str:
    ascii_name = unidecode.unidecode(name)
    ascii_name = ascii_name.lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9_-]", "-", ascii_name)

def store_embedding(team: str, report_uuid: str, test_id: str, vector: List[float], metadata: Dict):
    collection_name = f"{normalize_collection_name(team)}_collection"
    try:
        client.get_collection(collection_name=collection_name)
    except UnexpectedResponse:
        print(f"[QDRANT] Коллекция '{collection_name}' не найдена, создаю...")
        try:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=len(vector), distance=Distance.COSINE)
            )
        except UnexpectedResponse as e:
            print(f"[QDRANT] Ошибка при создании коллекции: {e}")
            raise e

    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={
            "report_uuid": report_uuid,
            "test_id": test_id,
            **metadata
        }
    )

    client.upsert(
        collection_name=collection_name,
        points=[point]
    )
    print(f"[QDRANT] Сохранил эмбеддинг для {test_id} в {collection_name}")

def get_last_reports(team: str, count: int = 3) -> List[Dict]:
    collection_name = f"{normalize_collection_name(team)}_collection"
    try:
        result = client.scroll(
            collection_name=collection_name,
            limit=1000,
            with_payload=True
        )
        points = result[0] if result and result[0] else []
    except Exception as e:
        print(f"[QDRANT] Ошибка при получении коллекции: {e}")
        return []

    by_report = {}
    for point in points:
        payload = point.payload or {}
        report_uuid = payload.get("report_uuid")
        if not report_uuid:
            continue
        by_report.setdefault(report_uuid, []).append(payload)

    sorted_reports = sorted(by_report.items(), key=lambda x: x[0], reverse=True)
    return [r[1] for r in sorted_reports[:count]]


def get_diff_summary(current: List[Dict], previous: List[Dict]) -> str:
    def extract_ids(data: List[Dict]) -> set:
        return {d.get("test_id") for d in data}

    current_ids = extract_ids(current)
    previous_ids = extract_ids(previous)

    new_tests = current_ids - previous_ids
    removed_tests = previous_ids - current_ids
    unchanged = current_ids & previous_ids

    summary = []
    summary.append(f"➕ Новые тесты: {len(new_tests)}")
    summary.append(f"➖ Удалённые тесты: {len(removed_tests)}")
    summary.append(f"✔️ Без изменений: {len(unchanged)}")

    return "\n".join(summary)
