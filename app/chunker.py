from typing import List, Dict

def extract_chunks(data: dict, path=None) -> List[Dict]:
    if path is None:
        path = []
    chunks = []

    name = data.get("name", "")
    children = data.get("children", [])

    if "status" in data and "uid" in data and "time" in data:
        test_path = " → ".join(path + [name])
        chunk_text = (
            f"📄 Тест: {name}\n"
            f"🔗 UID: {data['uid']}\n"
            f"✅ Статус: {data['status']}\n"
            f"⏱ Время: {data['time']['duration'] / 1000:.1f} сек\n"
            f"📱 Параметры: {', '.join(data.get('parameters', []))}\n"
            f"🧪 Путь: {test_path}"
        )
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "uid": data["uid"],
                "status": data["status"],
                "path": test_path
            }
        })
    else:
        for child in children:
            chunks.extend(extract_chunks(child, path + [name]))

    return chunks