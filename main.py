import asyncio
import os

from bot import bot, dp


async def main():
    # Ensure runtime folders exist (legacy behavior)
    os.makedirs("images", exist_ok=True)
    os.makedirs("voices", exist_ok=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

