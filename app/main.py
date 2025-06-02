# main.py
"""
Главная точка входа FastAPI-приложения для запуска анализа по UUID отчёта
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import traceback


from report_fetcher import fetch_report_json
from analyzer import analyze_report

app = FastAPI(
    title="RAG Allure Analyzer",
    description="RAG-система анализа тестов Allure на базе локальных моделей",
    version="1.0.0"
)

class UUIDRequest(BaseModel):
    uuid: str

class UUIDPayload(BaseModel):
    uuid: str = Field(..., example="abc123-uuid", description="UUID отчёта для анализа")

@app.post(
    "/uuid/analyze",
    summary="Анализ отчета по UUID",
    response_description="Результаты анализа в формате JSON",
    tags=["Анализ"]
)
def analyze_uuid(request: UUIDRequest):
    try:
        print(f"[API] Получен UUID: {request.uuid}")
        result = analyze_report(request.uuid)
        print(f"[API] Анализ завершён, количество правил: {len(result)}")
        return {"result": result}
    except Exception as e:
        print(f"[ERROR] Ошибка анализа UUID {request.uuid}: {e}")
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
