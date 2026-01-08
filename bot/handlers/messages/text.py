from __future__ import annotations

import asyncio
from datetime import datetime

from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import get_text
from bot.keyboards.inline import image_size_keyboard, language_select_keyboard, subscription_keyboard
from bot.state_store import USER_STATES, user_languages
from bot.utils import check_subscription, detect_language, is_bot_info_question, is_image_request, normalize_channel
from data.constants import CHANNELS
from data.history import append_history
from data.users import user_manager
from services.openai_service import chatgpt_text, text_to_image

router = Router()


@router.message(F.text & ~F.text.startswith("/") & ~F.forward_from & ~F.forward_from_chat)
async def message_handler(msg: types.Message):
    user_id = msg.from_user.id

    if user_manager.is_blocked(user_id):
        await msg.answer(get_text(user_id, "blocked_msg"))
        return

    # If language not set yet -> require subscription then show language picker
    if user_id not in user_languages:
        if not await check_subscription(msg.bot, user_id):
            await msg.answer(
                f"{get_text(user_id, 'subscribe_msg')}\n" + "\n".join([normalize_channel(ch) for ch in CHANNELS]),
                reply_markup=subscription_keyboard(user_id),
            )
            return
        await msg.answer(get_text(user_id, "select_language"), reply_markup=language_select_keyboard())
        return

    # Subscription check
    if not await check_subscription(msg.bot, user_id):
        await msg.answer(
            f"{get_text(user_id, 'subscribe_msg')}\n" + "\n".join([normalize_channel(ch) for ch in CHANNELS]),
            reply_markup=subscription_keyboard(user_id),
        )
        return

    # Limit check
    if not user_manager.check_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await msg.answer(get_text(user_id, "limit_reached"), reply_markup=kb.as_markup())
        return
    user_manager.increment_usage(user_id)

    user_lang = user_languages.get(user_id)
    if not user_lang:
        user_lang = detect_language(msg.text or "")
        user_languages[user_id] = user_lang

    # Check for bot info questions (creator/name)
    bot_info_type = is_bot_info_question(msg.text or "", user_lang)
    if bot_info_type:
        try:
            bot_info = await msg.bot.get_me()
            bot_username = bot_info.username or "bot"
            
            if bot_info_type == "creator":
                # Answer about creator
                if user_lang == "uz":
                    response = f"Men @shoxa_devv tomonidan yaratilganman."
                elif user_lang == "ru":
                    response = f"Я создан @shoxa_devv."
                else:  # en
                    response = f"I was created by @shoxa_devv."
            elif bot_info_type == "name":
                # Answer about name/username
                if user_lang == "uz":
                    response = f"Mening ismim yo'q, lekin username'im bor: @{bot_username}"
                elif user_lang == "ru":
                    response = f"У меня нет имени, но есть username: @{bot_username}"
                else:  # en
                    response = f"I don't have a name, but I have a username: @{bot_username}"
            else:
                response = None
            
            if response:
                await msg.answer(response)
                append_history(
                    user_id,
                    {"ts": datetime.utcnow().isoformat(), "type": "text", "prompt": msg.text, "response": response, "role": "Assistant"},
                )
                return
        except Exception:
            # If error getting bot info, continue to normal GPT response
            pass

    # Check if user is in waiting_image_size state - they should select size first
    if user_id in USER_STATES and USER_STATES[user_id].get("state") == "waiting_image_size":
        # User is waiting to select image size, don't process as image request
        await msg.answer(get_text(user_id, "image_size_select"), reply_markup=image_size_keyboard(user_id))
        return

    # Inline image request
    if is_image_request(msg.text or "", user_lang):
        image_prompt = msg.text or ""
        image_keywords = {
            "uz": ["rasm yarat", "tasvir yarat", "surat yarat", "rasm chiz", "tasvir chiz", "rasm", "tasvir", "surat"],
            "en": ["create image", "generate image", "make image", "draw picture", "create picture", "image", "picture", "draw"],
            "ru": ["создать изображение", "нарисовать", "создать картинку", "нарисовать картинку", "изображение", "картинка", "рисунок"],
        }
        for keyword in image_keywords.get(user_lang, image_keywords["uz"]):
            image_prompt = image_prompt.replace(keyword, "").strip()
        if not image_prompt:
            image_prompt = msg.text or ""

        first_msg = await msg.bot.send_message(msg.chat.id, get_text(user_id, "thinking"))
        try:
            image_url = await asyncio.to_thread(text_to_image, image_prompt)
            await first_msg.delete()
            await msg.bot.send_photo(msg.chat.id, image_url, caption=None)
            append_history(
                user_id,
                {"ts": datetime.utcnow().isoformat(), "type": "image", "prompt": image_prompt, "response": image_url, "role": "Assistant"},
            )
        except Exception as e:
            await first_msg.delete()
            await msg.bot.send_message(msg.chat.id, f"Xatolik: {str(e)}")
        return

    # Normal text reply
    first_msg = await msg.bot.send_message(msg.chat.id, get_text(user_id, "thinking"))
    response = await asyncio.to_thread(chatgpt_text, user_id, msg.text or "", user_lang)
    await first_msg.delete()
    await msg.bot.send_message(msg.chat.id, response)

    append_history(
        user_id,
        {"ts": datetime.utcnow().isoformat(), "type": "text", "prompt": msg.text, "response": response, "role": "Assistant"},
    )

