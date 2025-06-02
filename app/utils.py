import os
import json
from typing import List, Dict, Tuple
from qdrant_client import QdrantClient
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

client = QdrantClient(os.getenv("QDRANT_HOST", "http://localhost:6333"))

def get_run_summary(report_json: List[Dict]) -> Dict:
    summary = {
        "initiators": set(),
        "environments": set(),
        "run_names": set(),
        "results": {"passed": 0, "failed": 0, "skipped": 0},
        "run_dates": [],
    }

    for case in report_json:
        labels = case.get("labels", [])
        for label in labels:
            if label.get("name") == "executor":
                summary["initiators"].add(label.get("value"))
            if label.get("name") == "env":
                summary["environments"].add(label.get("value"))
            if label.get("name") == "tag":
                summary["run_names"].add(label.get("value"))
            if label.get("name") == "date":
                summary["run_dates"].append(label.get("value"))

        status = case.get("status")
        if status in summary["results"]:
            summary["results"][status] += 1

    summary["initiators"] = list(summary["initiators"])
    summary["environments"] = list(summary["environments"])
    summary["run_names"] = list(summary["run_names"])
    return summary

def cluster_failures(report_json: List[Dict]) -> Dict[int, List[str]]:
    messages = []
    test_ids = []

    for case in report_json:
        if case.get("status") == "failed":
            msg = case.get("statusMessage") or ""
            trace = case.get("statusTrace") or ""
            full_text = f"{msg} {trace}".strip()
            messages.append(full_text)
            test_ids.append(case.get("uid"))

    if not messages:
        return {}

    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(messages)
    clustering = DBSCAN(eps=0.5, min_samples=1).fit(X)

    clusters = defaultdict(list)
    for idx, label in enumerate(clustering.labels_):
        clusters[label].append(test_ids[idx])

    return dict(clusters)

def plot_pass_rate_chart(report_list: List[Tuple[str, Dict]]) -> str:
    uuids = [uuid for uuid, _ in report_list]
    passed = [report["results"]["passed"] for _, report in report_list]
    failed = [report["results"]["failed"] for _, report in report_list]

    plt.figure(figsize=(10, 5))
    plt.plot(uuids, passed, marker="o", label="Passed", linestyle="--")
    plt.plot(uuids, failed, marker="x", label="Failed", linestyle="--")
    plt.xlabel("UUID отчёта")
    plt.ylabel("Количество тестов")
    plt.title("Динамика Passed/Failed по отчётам")
    plt.legend()
    plt.grid(True)

    os.makedirs("static", exist_ok=True)
    chart_path = os.path.join("static", "pass_rate_chart.png")
    plt.savefig(chart_path)
    plt.close()
    return chart_path

def extract_team_name(report_json: list) -> str:
    for case in report_json:
        labels = case.get("labels", [])
        for label in labels:
            if label.get("name") == "suite":
                raw_name = label.get("value", "unknown").strip()
                return normalize_team_name(raw_name)
    return "unknown"

import re

def normalize_team_name(name: str) -> str:
    return re.sub(r"[^\w]+", "-", name.strip().lower())

def chunk_testcases(report_json: list) -> list:
    chunks = []
    for case in report_json:
        name = case.get("name", "unknown_test")
        status = case.get("status", "unknown")
        status_message = case.get("statusMessage", "")
        status_trace = case.get("statusTrace", "")
        body = f"{name}\nStatus: {status}\nMessage: {status_message}\nTrace: {status_trace}"
        chunks.append((name, body))
    return chunks
