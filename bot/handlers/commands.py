from __future__ import annotations

import asyncio
from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import get_text
from bot.keyboards.inline import (
    main_menu_keyboard,
    subscription_keyboard,
    language_select_keyboard,
)
from bot.state_store import USER_STATES, user_languages
from bot.utils import check_subscription, detect_language, normalize_channel
from data.constants import CHANNELS
from data.history import append_history
from data.users import user_manager
from services.openai_service import chatgpt_text, text_to_image

router = Router()


# =======================
# FIXED /start COMMAND
# =======================
@router.message(CommandStart())
async def start(message: types.Message):
    """Handle /start command ONLY as a command (not as text)."""
    user_id = message.from_user.id

    # Clear all states when /start is called
    USER_STATES.pop(user_id, None)

    # Referral support: /start <referrer_id>
    args = (message.text or "").split()
    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])
        if referrer_id != user_id and user_manager.is_new_user(user_id):
            if user_manager.add_referral(user_id, referrer_id):
                try:
                    await message.bot.send_message(
                        referrer_id
                        , get_text(referrer_id, "referral_new")
                    )
                except Exception:
                    pass

    if user_manager.is_blocked(user_id):
        await message.answer(get_text(user_id, "blocked_msg"))
        return

    # Legacy inviter info
    curr_user = user_manager.get_user(user_id)
    r_id = curr_user.get("referred_by")
    if r_id:
        try:
            await message.answer(
                get_text(user_id, "invited_by").format(referrer_id=r_id)
            )
        except Exception:
            pass

    # Subscription check
    if not await check_subscription(message.bot, user_id):
        await message.answer(
            f"{get_text(user_id, 'welcome')}\n\n"
            f"{get_text(user_id, 'subscribe_msg')}\n"
            f"{chr(10).join(CHANNELS)}\n\n"
            f"{get_text(user_id, 'subscribe_after')}",
            reply_markup=subscription_keyboard(user_id),
        )
        return

    # Ensure language
    lang = (
        user_languages.get(user_id)
        or user_manager.get_language(user_id)
        or "uz"
    )
    user_languages[user_id] = lang
    try:
        user_manager.set_language(user_id, lang)
    except Exception:
        pass

    # Send main menu immediately
    menu_kb = main_menu_keyboard(user_id)
    if menu_kb is None:
        fallback = InlineKeyboardBuilder()
        fallback.button(
            text=get_text(user_id, "profile"),
            callback_data="menu_profile",
        )
        fallback.button(
            text=get_text(user_id, "history"),
            callback_data="menu_history",
        )
        fallback.adjust(2)
        menu_kb = fallback.as_markup()

    await message.answer(
        f"{get_text(user_id, 'welcome')}\n\n"
        f"{get_text(user_id, 'bot_features')}",
        reply_markup=menu_kb,
    )


@router.message(F.text.regexp(r"^/restart"))
async def restart(message: types.Message):
    user_id = message.from_user.id

    if user_manager.is_blocked(user_id):
        await message.answer(get_text(user_id, "blocked_msg"))
        return

    user_languages.pop(user_id, None)

    await message.answer(get_text(user_id, "restart_success"))

    if not await check_subscription(message.bot, user_id):
        await message.answer(
            f"{get_text(user_id, 'welcome')}\n\n"
            f"{get_text(user_id, 'subscribe_msg')}\n"
            f"{chr(10).join(CHANNELS)}\n\n"
            f"{get_text(user_id, 'subscribe_after')}",
            reply_markup=subscription_keyboard(user_id),
        )
        return

    await message.answer(
        f"{get_text(user_id, 'welcome')}\n\n"
        f"{get_text(user_id, 'bot_features')}",
        reply_markup=main_menu_keyboard(user_id),
    )


@router.message(F.text.regexp(r"^/help$"))
async def help_command(message: types.Message):
    user_id = message.from_user.id

    if message.chat.type in ["group", "supergroup"]:
        return

    await message.answer(
        get_text(user_id, "help_command"),
        parse_mode="Markdown",
    )


@router.message(F.text.regexp(r"^/help(\s|$)"))
async def group_help_handler(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    user_id = message.from_user.id
    if user_manager.is_blocked(user_id):
        return

    parts = (message.text or "").split(" ", 1)
    prompt = parts[1] if len(parts) > 1 else ""

    if not prompt.strip():
        await message.reply(
            "Savol yozing: /help Savolingiz\n\n"
            "Misol: /help Python nima?"
        )
        return

    if not user_manager.check_limit(user_id):
        await message.reply(get_text(user_id, "limit_reached"))
        return

    user_manager.increment_usage(user_id)

    user_lang = user_languages.get(user_id) or detect_language(prompt)
    user_languages[user_id] = user_lang

    first_msg = await message.reply(get_text(user_id, "thinking"))
    try:
        response = await asyncio.to_thread(
            chatgpt_text, user_id, prompt, user_lang
        )
        await first_msg.delete()
        await message.reply(response)

        append_history(
            user_id,
            {
                "ts": datetime.utcnow().isoformat(),
                "type": "text",
                "prompt": prompt,
                "response": response,
                "role": "Assistant",
                "chat_type": "group",
                "chat_id": message.chat.id,
            },
        )
    except Exception as e:
        await first_msg.delete()
        await message.reply(f"Xatolik: {str(e)}")


@router.message(F.text.regexp(r"^/image"))
async def image_command(message: types.Message):
    user_id = message.from_user.id

    if user_manager.is_blocked(user_id):
        await message.answer(get_text(user_id, "blocked_msg"))
        return

    if not await check_subscription(message.bot, user_id):
        await message.answer(
            f"{get_text(user_id, 'subscribe_msg')}\n"
            + "\n".join(normalize_channel(ch) for ch in CHANNELS),
            reply_markup=subscription_keyboard(user_id),
        )
        return

    if not user_manager.check_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(
            text=get_text(user_id, "buy_premium"),
            callback_data="menu_premium",
        )
        await message.answer(
            get_text(user_id, "limit_reached"),
            reply_markup=kb.as_markup(),
        )
        return

    user_manager.increment_usage(user_id)

    parts = (message.text or "").split(" ", 1)
    prompt = parts[1] if len(parts) > 1 else ""
    if not prompt:
        await message.answer(get_text(user_id, "image_help"))
        return

    first_msg = await message.answer(get_text(user_id, "thinking"))
    try:
        image_url = await asyncio.to_thread(text_to_image, prompt)
        await first_msg.delete()
        await message.answer_photo(image_url)

        append_history(
            user_id,
            {
                "ts": datetime.utcnow().isoformat(),
                "type": "image",
                "prompt": prompt,
                "response": image_url,
                "role": "Assistant",
            },
        )
    except Exception as e:
        await first_msg.delete()
        await message.answer(f"Xatolik: {str(e)}")
