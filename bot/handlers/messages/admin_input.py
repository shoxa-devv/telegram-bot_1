from __future__ import annotations

from aiogram import Router, types

from bot.i18n import get_text
from bot.keyboards.inline import admin_menu_keyboard, admin_gift_keyboard
from bot.state_store import ADMIN_STATES
from data.users import user_manager

router = Router()


@router.message(lambda msg: msg.from_user and msg.from_user.id in ADMIN_STATES)
async def admin_input_handler(msg: types.Message):
    user_id = msg.from_user.id
    state_data = ADMIN_STATES[user_id]
    state = state_data.get("state")

    if state == "waiting_gift_id":
        try:
            target_uid = int((msg.text or "").strip())
            if target_uid < 0:
                raise ValueError
            del ADMIN_STATES[user_id]
            await msg.answer(
                f"Foydalanuvchi ID: {target_uid}\nQaysi planni bermoqchisiz?",
                reply_markup=admin_gift_keyboard(target_uid),
            )
        except ValueError:
            await msg.answer("Iltimos, to'g'ri raqamli ID kiriting.")

    elif state == "waiting_block_id":
        try:
            target_uid = int((msg.text or "").strip())
            user_manager.block_user(target_uid)
            del ADMIN_STATES[user_id]
            await msg.answer(
                get_text(user_id, "user_blocked").format(user_id=target_uid),
                reply_markup=admin_menu_keyboard(user_id),
            )
        except ValueError:
            await msg.answer("Error ID.")

    elif state == "waiting_unblock_id":
        try:
            target_uid = int((msg.text or "").strip())
            if not user_manager.is_blocked(target_uid):
                await msg.answer(get_text(user_id, "user_not_blocked").format(user_id=target_uid))
            else:
                user_manager.unblock_user(target_uid)
                await msg.answer(
                    get_text(user_id, "user_unblocked").format(user_id=target_uid),
                    reply_markup=admin_menu_keyboard(user_id),
                )
            del ADMIN_STATES[user_id]
        except ValueError:
            await msg.answer("Error ID.")

    elif state == "waiting_remove_premium_id":
        try:
            target_uid = int((msg.text or "").strip())
            user_manager.remove_premium(target_uid)
            del ADMIN_STATES[user_id]
            await msg.answer(
                get_text(user_id, "premium_removed").format(user_id=target_uid),
                reply_markup=admin_menu_keyboard(user_id),
            )
        except ValueError:
            await msg.answer("Error ID.")

    elif state == "waiting_custom_limit":
        try:
            limit = int((msg.text or "").strip())
            if limit > 1000:
                await msg.answer(get_text(user_id, "limit_too_high"))
                return
            target_uid = state_data.get("target_uid")
            duration = 30
            plan = "custom"
            user_manager.set_plan(target_uid, plan, duration, limit)
            dur_text = f"{duration} kun"
            await msg.answer(
                f"✅ Bajarildi!\nID: {target_uid}\nPlan: {plan.upper()}\nLimit: {limit}\nMuddat: {dur_text}",
                reply_markup=admin_menu_keyboard(user_id),
            )
            try:
                await msg.bot.send_message(
                    target_uid,
                    f"🎁 Tabriklaymiz! Admin sizga {plan.upper()} obunasini (Limit: {limit}) {dur_text} muddatga hadya qildi! 🎉",
                )
            except Exception:
                pass
            del ADMIN_STATES[user_id]
        except ValueError:
            await msg.answer("Raqam kiriting.")
    else:
        del ADMIN_STATES[user_id]

