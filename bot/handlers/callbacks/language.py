from __future__ import annotations

from aiogram import F, Router, types

from bot.i18n import get_text
from bot.keyboards.inline import main_menu_keyboard
from bot.state_store import user_languages
from data.users import user_manager

router = Router()


@router.callback_query(F.data.startswith("lang_"))
async def language_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang_code = callback.data.split("_", 1)[1]

    user_languages[user_id] = lang_code
    try:
        user_manager.set_language(user_id, lang_code)
    except Exception:
        pass

    await callback.answer(get_text(user_id, "language_selected"), show_alert=True)
    await callback.message.edit_text(
        f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
        reply_markup=main_menu_keyboard(user_id),
    )

