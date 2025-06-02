# chunker.py
"""
Модуль разбора отчета и выделения чанков по каждому тест-кейсу
"""
from typing import List, Dict

def extract_team_name(suite: dict) -> str:
    for label in suite.get("labels", []):
        if label.get("name") == "suite":
            return label.get("value", "unknown_team")
    return "unknown_team"

def chunk_testcases(report_json: List[dict]) -> List[dict]:
    """
    Выделение чанков из отчета
    """
    chunks = []
    for suite in report_json:
        for case in suite.get("children", []):
            chunks.append({
                "uid": case.get("uid"),
                "name": case.get("name"),
                "status": case.get("status"),
                "duration": case.get("time", {}).get("duration"),
                "labels": case.get("labels", []),
                "description": case.get("description"),
                "steps": case.get("steps", []),
                "attachments": case.get("attachments", []),
                "flaky": case.get("flaky"),
                "statusMessage": case.get("statusMessage"),
                "statusTrace": case.get("statusTrace")
            })
    return chunks
