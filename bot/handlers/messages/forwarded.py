from __future__ import annotations

from aiogram import F, Router, types

from bot.utils import get_ad_text

router = Router()


@router.message(F.forward_from | F.forward_from_chat)
async def forwarded_message_handler(msg: types.Message):
    if not (msg.forward_from or msg.forward_from_chat):
        return
    user_id = msg.from_user.id if msg.from_user else None
    await msg.reply(get_ad_text(user_id))

