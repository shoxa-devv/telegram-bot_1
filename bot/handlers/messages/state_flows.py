from __future__ import annotations

from aiogram import F, Router, types

from bot.i18n import get_text
from bot.keyboards.inline import image_size_keyboard, video_quality_keyboard
from bot.keyboards.reply import get_main_menu_reply_kb
from bot.state_store import USER_STATES

router = Router()


@router.message(
    lambda msg: msg.from_user
    and msg.from_user.id in USER_STATES
    and USER_STATES[msg.from_user.id].get("state") == "waiting_video_description"
)
async def video_description_handler(msg: types.Message):
    user_id = msg.from_user.id
    video_description = (msg.text or "").strip()

    if not video_description or len(video_description) < 10:
        await msg.answer("Iltimos, video tavsifini batafsil yozing (kamida 10 ta belgi)")
        return

    USER_STATES[user_id] = {"state": "waiting_video_quality", "video_description": video_description}
    await msg.answer(get_text(user_id, "video_quality_select"), reply_markup=video_quality_keyboard(user_id))


@router.message(
    lambda msg: msg.from_user
    and msg.from_user.id in USER_STATES
    and USER_STATES[msg.from_user.id].get("state") == "waiting_image_prompt"
)
async def image_prompt_handler(msg: types.Message):
    user_id = msg.from_user.id
    prompt = (msg.text or "").strip()

    if not prompt:
        await msg.answer("Matn kiriting!")
        return

    USER_STATES[user_id] = {"state": "waiting_image_size", "image_prompt": prompt}
    await msg.answer(get_text(user_id, "image_size_select"), reply_markup=image_size_keyboard(user_id))


@router.message(F.text.in_({"🏠 Asosiy Menyu", "🏠 Main Menu", "🏠 Главное Меню"}))
async def main_menu_reply_button_handler(msg: types.Message):
    user_id = msg.from_user.id

    if user_id in USER_STATES:
        del USER_STATES[user_id]

    from aiogram.types import ReplyKeyboardRemove
    from bot.keyboards.inline import main_menu_keyboard

    await msg.answer(get_text(user_id, "main_menu"), reply_markup=ReplyKeyboardRemove())
    await msg.answer(
        f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
        reply_markup=main_menu_keyboard(user_id),
    )

