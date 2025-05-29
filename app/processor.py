import os
from dotenv import load_dotenv
import requests
import httpx

# Загружаем переменные из .env
load_dotenv()

ALLURE_HOST = os.getenv("ALLURE_HOST")
ALLURE_USER = os.getenv("ALLURE_USER")
ALLURE_PASSWORD = os.getenv("ALLURE_PASSWORD")
AUTH = (ALLURE_USER, ALLURE_PASSWORD)

def save_analysis_to_file(uuid: str, message: str):
    os.makedirs("logs", exist_ok=True)
    path = f"logs/ai_analysis_{uuid}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(message)
    print(f"[LOG] Сохранил анализ в файл: {path}")

def fetch_report_json(uuid: str):
    url = f"{ALLURE_HOST}/api/report/{uuid}/suites/json"
    print(f"[FETCH] Получаем отчет: {url}")
    resp = requests.get(url, auth=AUTH)
    resp.raise_for_status()
    return resp.json()

# Остальной код остаётся без изменений...

def send_analysis(uuid: str, message: str):
    url = f"{ALLURE_HOST}/api/analysis/report/{uuid}"
    payload = [{
        "rule": "ai_analysis",
        "message": message
    }]
    print(f"[SEND] Отправляем анализ в Allure: {url}")
    try:
        resp = requests.post(url, json=payload, auth=AUTH)
        print(f"[SEND] Статус отправки: {resp.status_code}")
        if resp.status_code != 200:
            print(resp.text)
    except Exception as e:
        print(f"[SEND] Ошибка отправки в Allure: {e}")

    save_analysis_to_file(uuid, message)
