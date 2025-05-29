from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List
import requests
import logging

client = QdrantClient(host="localhost", port=6333)
log = logging.getLogger(__name__)

def get_texts_by_uuid(collection: str, uuid: str) -> List[str]:
    response = client.scroll(
        collection_name=collection,
        limit=1000,
        scroll_filter=Filter(
            must=[FieldCondition(key="uuid", match=MatchValue(value=uuid))]
        )
    )
    return [p.payload.get("path", "") + " → " + p.payload.get("status", "") for p in response[0]]

def build_prompt(current: List[str], previous: List[str]) -> str:
    return (
        "Ты анализируешь автотесты. Вот текущий отчёт:\n\n" +
        "\n".join(current[:20]) +
        "\n\nА вот предыдущие:\n\n" +
        "\n".join(previous[:40]) +
        "\n\nВыведи краткий анализ и изменения."
    )

def call_ollama(prompt: str) -> str:
    log.info("📡 Запрос к Ollama...")
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": "gemma3:4b",
        "prompt": prompt,
        "stream": False
    })
    res.raise_for_status()
    return res.json()["response"].strip()

def analyze_with_history(collection: str, current_uuid: str, previous_uuids: List[str]) -> str:
    current = get_texts_by_uuid(collection, current_uuid)
    previous = []
    for prev in previous_uuids[-2:]:
        previous += get_texts_by_uuid(collection, prev)
    prompt = build_prompt(current, previous)
    return call_ollama(prompt)