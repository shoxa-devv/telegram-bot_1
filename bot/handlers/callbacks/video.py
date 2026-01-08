from __future__ import annotations

import asyncio
import os

from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import get_text
from bot.keyboards.inline import main_menu_keyboard
from bot.state_store import USER_STATES
from data.users import user_manager

router = Router()


@router.callback_query(F.data.startswith("video_quality_"))
async def video_quality_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    quality = callback.data.split("_")[-1]

    if user_id not in USER_STATES or USER_STATES[user_id].get("state") != "waiting_video_quality":
        await callback.answer("Xatolik: Avval video tavsifini yuboring", show_alert=True)
        return

    video_description = USER_STATES[user_id].get("video_description", "")
    del USER_STATES[user_id]

    if not user_manager.check_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await callback.message.edit_text(get_text(user_id, "limit_reached"), reply_markup=kb.as_markup())
        return

    user_manager.increment_usage(user_id)
    await callback.message.edit_text(get_text(user_id, "video_generating"))

    try:
        from services.video_service import download_video, generate_video

        video_url = await asyncio.to_thread(generate_video, video_description, quality)
        os.makedirs("videos", exist_ok=True)
        video_path = f"videos/{user_id}_{quality}.mp4"
        await asyncio.to_thread(download_video, video_url, video_path)

        await callback.message.answer(get_text(user_id, "video_success"))
        from aiogram.types import FSInputFile, ReplyKeyboardRemove

        await callback.bot.send_video(
            callback.message.chat.id,
            FSInputFile(video_path),
            caption=f"🎬 {video_description[:100]}...",
            reply_markup=ReplyKeyboardRemove(),
        )

        try:
            os.remove(video_path)
        except OSError:
            pass

        await callback.message.answer(get_text(user_id, "main_menu"), reply_markup=main_menu_keyboard(user_id))
    except Exception as e:
        await callback.message.answer(f"{get_text(user_id, 'video_error')}\n\nError: {str(e)}")
        await callback.message.answer(get_text(user_id, "main_menu"), reply_markup=main_menu_keyboard(user_id))

    await callback.answer()

