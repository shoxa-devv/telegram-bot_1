from __future__ import annotations

import asyncio
from datetime import datetime

from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import get_text
from bot.keyboards.inline import main_menu_keyboard
from bot.state_store import USER_STATES
from data.history import append_history
from data.users import user_manager
from services.openai_service import text_to_image

router = Router()


@router.callback_query(F.data.startswith("size_"))
async def image_size_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    size = callback.data.split("_", 1)[1]

    if user_id not in USER_STATES or USER_STATES[user_id].get("state") != "waiting_image_size":
        await callback.answer("Error state", show_alert=True)
        return

    prompt = USER_STATES[user_id].get("image_prompt")
    del USER_STATES[user_id]

    if not user_manager.check_image_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await callback.message.edit_text(get_text(user_id, "image_limit_reached"), reply_markup=kb.as_markup())
        return

    user_manager.increment_image_usage(user_id)
    await callback.message.edit_text(get_text(user_id, "thinking"))

    try:
        image_url = await asyncio.to_thread(text_to_image, prompt, size)
        await callback.message.delete()
        from aiogram.types import ReplyKeyboardRemove

        await callback.bot.send_photo(
            callback.message.chat.id,
            image_url,
            caption=f"🎨 {prompt[:100]}...",
            reply_markup=ReplyKeyboardRemove(),
        )

        append_history(
            user_id,
            {
                "ts": datetime.utcnow().isoformat(),
                "type": "image",
                "prompt": prompt,
                "response": image_url,
                "role": "Assistant",
                "size": size,
            },
        )

        await callback.message.answer(get_text(user_id, "main_menu"), reply_markup=main_menu_keyboard(user_id))
    except Exception as e:
        await callback.message.edit_text(f"Xatolik: {str(e)}")
        await callback.message.answer("Menu", reply_markup=main_menu_keyboard(user_id))

