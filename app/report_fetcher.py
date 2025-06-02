# report_fetcher.py
"""
Модуль получения JSON-отчета из Allure по UUID
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

ALLURE_HOST = os.getenv("ALLURE_HOST")
AUTH = (os.getenv("ALLURE_USER"), os.getenv("ALLURE_PASSWORD"))

def fetch_report_json(uuid: str) -> dict:
    url = f"{ALLURE_HOST}/api/report/{uuid}/suites/json"
    print(f"[INFO] Получение отчета по UUID: {uuid}")
    response = httpx.get(url, auth=AUTH)
    response.raise_for_status()
    return response.json()
