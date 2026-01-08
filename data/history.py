import json
import os
from typing import Any

HISTORY_PATH = "history.json"
MAX_HISTORY = 100  # per user


def load_history() -> dict[str, list[dict[str, Any]]]:
    if not os.path.exists(HISTORY_PATH):
        return {}
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_history(history: dict[str, list[dict[str, Any]]]) -> None:
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def append_history(user_id: int, entry: dict[str, Any]) -> None:
    history = load_history()
    key = str(user_id)
    user_history = history.get(key, [])
    user_history.append(entry)
    history[key] = user_history[-MAX_HISTORY:]
    save_history(history)


def format_history(user_id: int) -> str:
    """Short history format for UI."""
    history = load_history()
    records = history.get(str(user_id), [])
    if not records:
        return "Tarix bo'sh. "

    last_records = records[-5:]
    parts: list[str] = []
    for idx, rec in enumerate(last_records, 1):
        question = (rec.get("prompt") or "")[:120]
        answer = (rec.get("response") or "")[:200]
        parts.append(f"{idx}) Q: {question}\n   A: {answer}")
    return "\n\n".join(parts)


def get_conversation_context(user_id: int, max_messages: int = 20) -> str:
    """Conversation context for GPT from text-only history."""
    history = load_history()
    records = history.get(str(user_id), [])
    if not records:
        return ""

    text_records = [rec for rec in records if rec.get("type") == "text"]
    last_records = text_records[-max_messages:]
    if not last_records:
        return ""

    parts: list[str] = []
    for rec in last_records:
        question = rec.get("prompt", "")
        answer = rec.get("response", "")
        if question and answer:
            parts.append(f"Foydalanuvchi: {question}\nBot: {answer}")
    return "\n\n".join(parts)

