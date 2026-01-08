from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from bot.i18n import get_text


def get_main_menu_reply_kb(user_id: int) -> ReplyKeyboardMarkup:
    button_text = get_text(user_id, "main_menu_button")
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button_text)]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )

