from __future__ import annotations

from datetime import datetime

from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.inline import admin_menu_keyboard, main_menu_keyboard
from bot.i18n import get_text
from bot.state_store import ADMIN_STATES
from data.config import ADMIN_IDS
from data.stats import get_stats_text
from data.users import user_manager

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not _is_admin(user_id):
        await callback.answer()
        return
    await callback.message.edit_text("⚙️ Admin Paneliga xush kelibsiz!", reply_markup=admin_menu_keyboard(user_id))
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not _is_admin(user_id):
        await callback.answer()
        return
    total_users = len(user_manager.users)
    today = datetime.now().date().isoformat()
    active_today = sum(1 for u in user_manager.users.values() if u.get("usage_date") == today)
    text = (
        "📊 **Bot Statistikasi**\n\n"
        f"👤 Jami foydalanuvchilar: {total_users}\n"
        f"🔥 Bugun faol: {active_today}\n"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="Orqaga", callback_data="admin_panel")
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "admin_api")
async def admin_api(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not _is_admin(user_id):
        await callback.answer()
        return
    text = get_stats_text()
    kb = InlineKeyboardBuilder()
    kb.button(text="Orqaga", callback_data="admin_panel")
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "admin_gift_start")
async def admin_gift_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not _is_admin(user_id):
        await callback.answer()
        return
    ADMIN_STATES[user_id] = {"state": "waiting_gift_id"}
    kb = InlineKeyboardBuilder()
    kb.button(text="Bekor qilish", callback_data="admin_cancel")
    await callback.message.edit_text(
        "Iltimos, hadya qilmoqchi bo'lgan odamingizni telegram akkaunt chat idsini kiriting:",
        reply_markup=kb.as_markup(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_block_start")
async def admin_block_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not _is_admin(user_id):
        await callback.answer()
        return
    ADMIN_STATES[user_id] = {"state": "waiting_block_id"}
    kb = InlineKeyboardBuilder()
    kb.button(text="Bekor qilish", callback_data="admin_cancel")
    await callback.message.edit_text(get_text(user_id, "enter_id_block"), reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "admin_unblock_start")
async def admin_unblock_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not _is_admin(user_id):
        await callback.answer()
        return
    ADMIN_STATES[user_id] = {"state": "waiting_unblock_id"}
    kb = InlineKeyboardBuilder()
    kb.button(text="Bekor qilish", callback_data="admin_cancel")
    await callback.message.edit_text(get_text(user_id, "enter_id_unblock"), reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "admin_remove_premium_start")
async def admin_remove_premium_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not _is_admin(user_id):
        await callback.answer()
        return
    ADMIN_STATES[user_id] = {"state": "waiting_remove_premium_id"}
    kb = InlineKeyboardBuilder()
    kb.button(text="Bekor qilish", callback_data="admin_cancel")
    await callback.message.edit_text(get_text(user_id, "enter_id_remove_premium"), reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "admin_cancel")
async def admin_cancel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id in ADMIN_STATES:
        del ADMIN_STATES[user_id]
    await callback.message.edit_text("Bekor qilindi.", reply_markup=main_menu_keyboard(user_id))
    await callback.answer()


@router.callback_query(F.data.startswith("gift_plan_"))
async def gift_plan(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not _is_admin(user_id):
        await callback.answer()
        return

    parts = callback.data.split("_")
    target_uid = int(parts[-1])
    plan_parts = parts[2:-1]
    plan = "_".join(plan_parts)

    if plan == "custom":
        ADMIN_STATES[user_id] = {"state": "waiting_custom_limit", "target_uid": target_uid}
        kb = InlineKeyboardBuilder()
        kb.button(text="Bekor qilish", callback_data="admin_cancel")
        await callback.message.edit_text(get_text(user_id, "enter_limit"), reply_markup=kb.as_markup())
        await callback.answer()
        return

    duration = 30
    user_manager.set_plan(target_uid, plan, duration, None)
    dur_text = f"{duration} kun"

    await callback.message.edit_text(
        f"✅ Bajarildi!\nID: {target_uid}\nPlan: {plan.upper()}\nMuddat: {dur_text}",
        reply_markup=main_menu_keyboard(user_id),
    )
    try:
        await callback.bot.send_message(
            target_uid,
            f"🎁 Tabriklaymiz! Admin sizga {plan.upper()} obunasini {dur_text} muddatga hadya qildi! 🎉",
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("gift_dur_"))
async def gift_duration(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if not _is_admin(user_id):
        await callback.answer()
        return

    parts = callback.data.split("_")
    duration = int(parts[2])
    target_uid = int(parts[-1])
    plan_parts = parts[3:-1]
    plan = "_".join(plan_parts)

    custom_limit = None
    if plan.startswith("custom-"):
        custom_limit = int(plan.split("-")[1])
        plan = "custom"

    user_manager.set_plan(target_uid, plan, duration, custom_limit)
    dur_text = f"{duration} kun"

    await callback.message.edit_text(
        f"✅ Bajarildi!\nID: {target_uid}\nPlan: {plan}\nMuddat: {dur_text}\nLimit: {custom_limit if custom_limit else 'Standart'}",
        reply_markup=main_menu_keyboard(user_id),
    )
    try:
        await callback.bot.send_message(
            target_uid,
            f"🎁 Tabriklaymiz! Admin sizga {plan.upper()} obunasini {dur_text} muddatga hadya qildi! 🎉",
        )
    except Exception:
        pass
    await callback.answer()

