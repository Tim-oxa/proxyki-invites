from aiogram import Bot, Dispatcher
from handlers import rt
from config import *


bot = Bot(BOT_TOKEN)
dp = Dispatcher()


dp.include_router(rt)
