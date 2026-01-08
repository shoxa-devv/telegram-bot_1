"""
In-memory state (legacy).

This project originally used plain dicts for state; we keep it for now to avoid
breaking behavior. Later we can migrate to aiogram FSM cleanly.
"""

from __future__ import annotations

user_languages: dict[int, str] = {}  # user_id -> "uz" | "en" | "ru"

ADMIN_STATES: dict[int, dict] = {}  # admin_id -> {"state": str, ...}
USER_STATES: dict[int, dict] = {}  # user_id -> {"state": str, ...}

