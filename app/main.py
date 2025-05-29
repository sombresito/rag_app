from fastapi import FastAPI, Request
from app.processor import process_report_by_uuid

app = FastAPI()

@app.get("/healthcheck")
def health():
    return {"status": "ok"}

@app.post("/uuid/analyze")
async def analyze_uuid(request: Request):
    body = await request.json()
    uuid = body.get("uuid")
    
    print(f"[LOG] Получен UUID: {uuid}")  # 👈 лог входящего UUID
    
    result = process_report_by_uuid(uuid)
    
    print(f"[LOG] Ответ анализа: {result}")  # 👈 лог возвращаемого результата
    
    return result
