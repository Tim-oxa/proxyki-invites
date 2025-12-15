from main import dp, bot
import asyncio


async def start_up():
    await dp.start_polling(bot)


asyncio.run(start_up())
