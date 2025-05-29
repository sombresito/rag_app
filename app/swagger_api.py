import requests

def fetch_allure_report(uuid: str) -> dict:
    url = f"http://allure-report-bcc-qa:8080/api/report/{uuid}/suites/json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def post_analysis_result(uuid: str, message: str):
    url = f"http://allure-report-bcc-qa:8080/api/analysis/report/{uuid}"
    payload = [{"rule": "auto-analysis", "message": message}]
    response = requests.post(url, json=payload)
    response.raise_for_status()