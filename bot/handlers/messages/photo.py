from __future__ import annotations

import asyncio
import os
from datetime import datetime

from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import get_text
from bot.keyboards.inline import subscription_keyboard
from bot.utils import check_subscription, normalize_channel
from data.constants import CHANNELS
from data.history import append_history
from data.users import user_manager
from services.openai_service import image_to_anime, transform_image_with_instruction

router = Router()


@router.message(F.photo)
async def photo_handler(message: types.Message):
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

    caption = (message.caption or "").strip()
    if not caption:
        await message.reply("Rasm ustida nima qilish kerakligini yozing (masalan: anime uslubida, multserial qahramoni qilib ber).")
        return

    os.makedirs("images", exist_ok=True)
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    save_path = f"images/{photo.file_id}.jpg"
    await message.bot.download_file(file.file_path, save_path)

    first_msg = await message.bot.send_message(message.chat.id, get_text(user_id, "thinking"))
    try:
        caption_lower = caption.lower()
        is_anime = any(word in caption_lower for word in ["anime", "аниме"])
        is_multserial = any(
            word in caption_lower
            for word in ["multserial", "мультсериал", "cartoon", "мультфильм", "qahramon", "персонаж"]
        )

        if is_anime or is_multserial:
            style = "anime" if is_anime else "multserial"
            new_image = await asyncio.to_thread(image_to_anime, save_path, style)
        else:
            new_image = await asyncio.to_thread(transform_image_with_instruction, save_path, caption)

        await first_msg.delete()
        await message.bot.send_photo(message.chat.id, new_image, caption=None)
        append_history(
            user_id,
            {
                "ts": datetime.utcnow().isoformat(),
                "type": "image_transform",
                "prompt": caption,
                "response": new_image,
                "role": "Assistant",
            },
        )
    except Exception as e:
        await first_msg.delete()
        await message.bot.send_message(message.chat.id, f"Xatolik: {str(e)}")

