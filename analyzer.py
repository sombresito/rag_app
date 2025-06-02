# analyzer.py
import os
import requests
import traceback
from typing import List, Dict
from dotenv import load_dotenv
from embedder import generate_embedding
from qdrant_store import store_embedding, get_last_reports, get_diff_summary
from utils import get_run_summary, cluster_failures, plot_pass_rate_chart

load_dotenv()

ALLURE_HOST = os.getenv("ALLURE_HOST")
ALLURE_USER = os.getenv("ALLURE_USER")
ALLURE_PASSWORD = os.getenv("ALLURE_PASSWORD")
AUTH = (ALLURE_USER, ALLURE_PASSWORD)

def fetch_report_json(uuid: str) -> List[dict]:
    url = f"{ALLURE_HOST}/api/report/{uuid}/test-cases/aggregate"
    print(f"[FETCH] Отправка запроса: {url}")
    try:
        resp = requests.get(url, auth=AUTH, headers={"accept": "application/json"}, timeout=15)
        print(f"[FETCH] Статус ответа: {resp.status_code}")
        resp.raise_for_status()
        json_data = resp.json()
        print(f"[FETCH] Успешно получили JSON (длина: {len(str(json_data))})")
        return json_data
    except requests.exceptions.Timeout:
        raise RuntimeError("⏰ Таймаут при получении отчёта")
    except Exception as e:
        raise RuntimeError(f"❌ Ошибка получения отчёта: {e}")

def extract_team_name(report_json: List[dict]) -> str:
    try:
        for case in report_json:
            labels = case.get("labels", [])
            for label in labels:
                if label.get("name") == "suite":
                    return label.get("value")
        raise ValueError("Не найдена метка 'suite' в labels")
    except Exception as e:
        raise RuntimeError(f"Ошибка извлечения названия команды: {e}")

def analyze_report(uuid: str) -> List[Dict[str, str]]:
    print(f"[ANALYZE] Запущен анализ UUID: {uuid}")
    try:
        report_json = fetch_report_json(uuid)
        print(f"[ANALYZE] Получен отчёт. Элементов: {len(report_json)}")

        team_name = extract_team_name(report_json)
        print(f"[ANALYZE] Название команды: {team_name}")

        # Генерация эмбеддингов
        embeddings = []
        for case in report_json:
            name = case.get("name", "Unnamed")
            status = case.get("status", "unknown")
            text = f"Test name: {name}\nStatus: {status}"
            embedding = generate_embedding(text)
            embeddings.append((name, embedding))
        print(f"[EMBED] Сгенерировано: {len(embeddings)} эмбеддингов")

        # Сохраняем в Qdrant
        for idx, (test_name, vector) in enumerate(embeddings):
            case = report_json[idx]
            metadata = {
                "uuid": uuid,
                "team": team_name,
                "test_name": test_name,
                "status": case.get("status", "unknown"),
            }
            store_embedding(team_name, uuid, test_name, vector, metadata)

        # Сравниваем с предыдущими
        prev_reports = get_last_reports(team_name, exclude_uuid=uuid)
        diff_summary = get_diff_summary(uuid, prev_reports, team_name)

        # Генерируем Summary + графики + кластеризацию
        summary = get_run_summary(report_json)
        clusters = cluster_failures(report_json)
        plot_path = plot_pass_rate_chart(team_name)

        print("[ANALYZE] Анализ завершён")

        return [
            {"rule": "Summary", "message": summary},
            {"rule": "Differences", "message": diff_summary},
            {"rule": "Failure Clusters", "message": clusters},
            {"rule": "Graph", "message": f"Сохранён в {plot_path}"}
        ]

    except Exception as e:
        print(f"[ERROR] Ошибка анализа UUID {uuid}: {e}")
        traceback.print_exc()
        return [{"rule": "Ошибка", "message": str(e)}]
