from __future__ import annotations

from aiogram import F, Router, types
from aiogram.types import LabeledPrice

from bot.i18n import get_text
from bot.keyboards.inline import main_menu_keyboard
from data.users import PRICES, user_manager

router = Router()


@router.callback_query(F.data.startswith("buy_"))
async def buy_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    plan = callback.data.split("_", 1)[1]

    if plan not in PRICES:
        await callback.answer("Plan not found", show_alert=True)
        return

    price = PRICES[plan]
    prices = [LabeledPrice(label=f"{plan.replace('_', ' ').title()} Plan", amount=price)]

    await callback.bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"Premium {plan.title()}",
        description=f"Purchase {plan.replace('_', ' ').title()} subscription",
        payload=f"sub_{user_id}_{plan}",
        provider_token="",
        currency="XTR",
        prices=prices,
        start_parameter=f"buy_{plan}",
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_query(checkout_query: types.PreCheckoutQuery):
    await checkout_query.bot.answer_pre_checkout_query(checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: types.Message):
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload

    if payload.startswith("sub_"):
        parts = payload.split("_")
        if len(parts) >= 3:
            plan = "_".join(parts[2:])
            user_manager.set_plan(user_id, plan)
            await message.answer(get_text(user_id, "premium_success"))
            await message.answer(
                f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
                reply_markup=main_menu_keyboard(user_id),
            )

