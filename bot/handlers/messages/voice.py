from __future__ import annotations

import asyncio
import os
from datetime import datetime

from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import get_text
from bot.keyboards.inline import subscription_keyboard
from bot.state_store import user_languages
from bot.utils import check_subscription, detect_language, normalize_channel
from data.constants import CHANNELS
from data.history import append_history
from data.users import user_manager
from services.openai_service import chatgpt_text, speech_to_text

router = Router()


@router.message(F.voice)
async def voice_handler(message: types.Message):
    user_id = message.from_user.id

    if user_manager.is_blocked(user_id):
        await message.answer(get_text(user_id, "blocked_msg"))
        return

    if not await check_subscription(message.bot, user_id):
        await message.answer(
            f"{get_text(user_id, 'subscribe_msg')}\n" + "\n".join([normalize_channel(ch) for ch in CHANNELS]),
            reply_markup=subscription_keyboard(user_id),
        )
        return

    if not user_manager.check_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await message.answer(get_text(user_id, "limit_reached"), reply_markup=kb.as_markup())
        return
    user_manager.increment_usage(user_id)

    os.makedirs("voices", exist_ok=True)
    voice = message.voice
    file = await message.bot.get_file(voice.file_id)
    save_path = f"voices/{voice.file_id}.ogg"
    await message.bot.download_file(file.file_path, save_path)

    prompt = await asyncio.to_thread(speech_to_text, save_path)

    user_lang = user_languages.get(user_id)
    if not user_lang:
        user_lang = detect_language(prompt)
        user_languages[user_id] = user_lang

    first_msg = await message.bot.send_message(message.chat.id, get_text(user_id, "thinking"))
    response = await asyncio.to_thread(chatgpt_text, user_id, prompt, user_lang)
    await first_msg.delete()
    await message.bot.send_message(message.chat.id, response)

    append_history(
        user_id,
        {
            "ts": datetime.utcnow().isoformat(),
            "type": "voice",
            "prompt": prompt,
            "response": response,
            "role": "Assistant",
        },
    )

