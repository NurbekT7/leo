import asyncio
import os
import django
from redis.asyncio import Redis

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

''' 
Telegram settings
'''

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from django.conf import settings

from bot_core.handlers import router as main_router

async def main():
    redis = Redis(host='localhost', port=6379, db=0)
    storage = RedisStorage(redis=redis)

    bot = Bot(token=settings.TELEGRAM_TOKEN)
    dp = Dispatcher(storage=storage)

    dp.include_router(main_router)

    print("Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        await redis.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")