from __future__ import annotations

from datetime import datetime

from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import get_text
from bot.keyboards.inline import (
    back_button,
    language_select_keyboard,
    main_menu_keyboard,
    premium_keyboard,
    profile_keyboard,
)
from bot.keyboards.reply import get_main_menu_reply_kb
from bot.state_store import USER_STATES
from bot.utils import is_video_available
from data.history import format_history
from data.users import LIMITS, PLAN_FREE, PLAN_UNLIMITED, user_manager

router = Router()


def _ensure_not_blocked(user_id: int, callback: types.CallbackQuery) -> bool:
    if user_manager.is_blocked(user_id):
        # fire and forget answer; caller returns
        return False
    return True


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_manager.is_blocked(user_id):
        await callback.answer(get_text(user_id, "blocked_msg"), show_alert=True)
        return
    
    # Clear any active states when returning to main menu
    if user_id in USER_STATES:
        del USER_STATES[user_id]
    
    await callback.message.edit_text(
        f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
        reply_markup=main_menu_keyboard(user_id),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_history")
async def menu_history(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_manager.is_blocked(user_id):
        await callback.answer(get_text(user_id, "blocked_msg"), show_alert=True)
        return
    history = format_history(user_id)
    await callback.message.edit_text(
        f"{get_text(user_id, 'history')}:\n\n{history}",
        reply_markup=back_button(user_id),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_language")
async def menu_language(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_manager.is_blocked(user_id):
        await callback.answer(get_text(user_id, "blocked_msg"), show_alert=True)
        return
    await callback.message.edit_text(
        get_text(user_id, "select_language"),
        reply_markup=language_select_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_profile")
async def menu_profile(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_manager.is_blocked(user_id):
        await callback.answer(get_text(user_id, "blocked_msg"), show_alert=True)
        return

    user_info = user_manager.get_user(user_id)
    if "custom_limit" in user_info:
        limit = user_info["custom_limit"]
    else:
        limit = LIMITS.get(user_info.get("plan", PLAN_FREE), 10)
    if not isinstance(limit, (int, float)):
        limit = 10

    extra = user_info.get("referral_count", 0) * 3
    total_limit = limit + extra
    total_limit_str = "♾" if limit == float("inf") else str(total_limit)

    remaining = user_manager.get_remaining_limit(user_id)
    remaining_str = "♾" if remaining > 900000 else str(remaining)

    bot_username = (await callback.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={user_id}"

    plan_name = user_info.get("plan", PLAN_FREE).title()
    expiry = user_info.get("subscription_end")
    if expiry:
        try:
            exp_date = datetime.fromisoformat(expiry)
            if exp_date.year > 3000:
                plan_name += " (Abadiy)"
            else:
                days_left = (exp_date - datetime.now()).days
                plan_name += f" ({days_left} kun qoldi)"
        except Exception:
            pass

    if limit == float("inf") or user_info.get("plan") == PLAN_UNLIMITED:
        image_limit_str = "♾"
    elif user_info.get("plan") == PLAN_FREE:
        image_limit_str = "3"
    else:
        base = user_info.get("custom_limit") or LIMITS.get(user_info.get("plan", PLAN_FREE), 100)
        if not isinstance(base, (int, float)):
            base = 100
        image_limit_str = str(int(base * 0.5))

    text = get_text(user_id, "profile_info").format(
        user_id=user_id,
        plan=plan_name,
        referrals=user_info.get("referral_count", 0),
        limit=total_limit_str,
        image_limit=image_limit_str,
        remaining=remaining_str,
        link=ref_link,
    )
    await callback.message.edit_text(text, reply_markup=profile_keyboard(user_id), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "menu_premium")
async def menu_premium(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_manager.is_blocked(user_id):
        await callback.answer(get_text(user_id, "blocked_msg"), show_alert=True)
        return
    text = f"{get_text(user_id, 'premium_plans')}\n\n{get_text(user_id, 'payment_warning')}"
    await callback.message.edit_text(text, reply_markup=premium_keyboard(user_id))
    await callback.answer()


@router.callback_query(F.data == "menu_video")
async def menu_video(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_manager.is_blocked(user_id):
        await callback.answer(get_text(user_id, "blocked_msg"), show_alert=True)
        return

    if not is_video_available():
        await callback.answer(get_text(user_id, "video_unavailable"), show_alert=True)
        return

    USER_STATES[user_id] = {"state": "waiting_video_description"}
    await callback.message.delete()
    await callback.message.answer(get_text(user_id, "video_prompt"), reply_markup=get_main_menu_reply_kb(user_id))
    await callback.answer()


@router.callback_query(F.data == "menu_image")
async def menu_image(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_manager.is_blocked(user_id):
        await callback.answer(get_text(user_id, "blocked_msg"), show_alert=True)
        return

    if not user_manager.check_image_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await callback.message.edit_text(get_text(user_id, "image_limit_reached"), reply_markup=kb.as_markup())
        await callback.answer()
        return

    USER_STATES[user_id] = {"state": "waiting_image_prompt"}
    await callback.message.delete()
    await callback.message.answer(get_text(user_id, "image_prompt_request"), reply_markup=get_main_menu_reply_kb(user_id))
    await callback.answer()


@router.callback_query(F.data == "menu_help")
async def menu_help(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_manager.is_blocked(user_id):
        await callback.answer(get_text(user_id, "blocked_msg"), show_alert=True)
        return
    await callback.message.edit_text(get_text(user_id, "help_text"), reply_markup=back_button(user_id), parse_mode="Markdown")
    await callback.answer()

