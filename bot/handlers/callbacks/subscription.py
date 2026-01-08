from __future__ import annotations

from aiogram import F, Router, types

from bot.i18n import get_text
from bot.keyboards.inline import language_select_keyboard, main_menu_keyboard, subscription_keyboard
from bot.state_store import user_languages
from bot.utils import check_subscription

router = Router()


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if await check_subscription(callback.bot, user_id):
        await callback.answer(get_text(user_id, "subscribe_success"), show_alert=True)
        await callback.message.delete()

        if user_id not in user_languages:
            await callback.message.answer(
                get_text(user_id, "select_language"),
                reply_markup=language_select_keyboard(),
            )
        else:
            await callback.message.answer(
                f"{get_text(user_id, 'welcome')}\n\n{get_text(user_id, 'bot_features')}",
                reply_markup=main_menu_keyboard(user_id),
            )
    else:
        await callback.answer(get_text(user_id, "subscribe_fail"), show_alert=True)

