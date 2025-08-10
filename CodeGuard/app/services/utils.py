import os
import re
import threading
import time
from datetime import datetime
import json
import hashlib
from typing import List, Dict, Any

def delete_file_later(path: str, delay: int = 300):
    def delete():
        time.sleep(delay)
        if os.path.exists(path):
            os.remove(path)
    threading.Thread(target=delete).start()

def get_timestamped_filename(base_name="alerts", ext="txt"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{ext}"

def contains_hebrew(text: str) -> bool:
    return re.search(r'[\u0590-\u05FF]', text) is not None

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(PROJECT_DIR, "..", ".."))
HISTORY_FILE = os.path.join(ROOT_DIR, "analysis_history.json")

def save_analysis_to_history(full_path: str, alerts: list[dict]):
    """
    שומר את מספר האזהרות לנתיב מלא של קובץ יחד עם timestamp
    """
    if not os.path.exists(HISTORY_FILE):
        history = {}
    else:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = {}

    if full_path not in history:
        history[full_path] = []

    history[full_path].append({
        "timestamp": datetime.now().isoformat(),
        "issues": len(alerts)
    })

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history_for_file(filepath: str):
    """
    מחזיר שני מערכים: timestamps ו־ issue_counts עבור קובץ מסוים
    """
    if not os.path.exists(HISTORY_FILE):
        return [], []

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return [], []

    file_history = data.get(filepath, [])
    timestamps = []
    issue_counts = []

    for item in file_history:
        try:
            ts = datetime.fromisoformat(item["timestamp"])
            timestamps.append(ts)
            issue_counts.append(item["issues"])
        except Exception:
            continue

    return timestamps, issue_counts

