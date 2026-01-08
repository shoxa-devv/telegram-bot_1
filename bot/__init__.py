from __future__ import annotations

from aiogram import Bot, Dispatcher

from data.config import BOT_TOKEN

# Core instances
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Routers (order matters: commands first, then callbacks, then catch-all messages)
from bot.handlers.callbacks import router as callbacks_router  # noqa: E402
from bot.handlers.commands import router as commands_router  # noqa: E402
from bot.handlers.messages import router as messages_router  # noqa: E402

dp.include_router(commands_router)
dp.include_router(callbacks_router)
dp.include_router(messages_router)

