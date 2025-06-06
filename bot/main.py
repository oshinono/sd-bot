import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from loguru import logger
from aiogram.fsm.storage.redis import RedisStorage

from cmnds import commands
from config import settings
from images.router import router as images_router
from index.router import router as index_router
from settings.router import router as settings_router
from lora.router import router as lora_router

default_bot_settings = DefaultBotProperties(parse_mode=ParseMode.HTML)

async def main():
    try:
        storage = RedisStorage.from_url(f'redis://default:{settings.redis_password}@redis:6379', connection_kwargs={"password": settings.redis_password})
        async with Bot(token=settings.token, default=default_bot_settings, storage=storage) as bot:
            dp = Dispatcher(storage=storage)

            dp.include_routers(
                index_router,
                images_router,
                lora_router,
                settings_router,
                
            )

            bot_info = await bot.get_me()
            logger.info(f"Бот запущен 💫  | {bot_info.full_name}, @{bot_info.username}")
            
            await bot.set_my_commands(commands)
            await bot.delete_webhook(drop_pending_updates=True)

            ALLOWED_UPDATES = ["message", "edited_message", "callback_query", "inline_query"]

            await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)
    finally:
        await dp.storage.close()

if __name__ == "__main__":
    asyncio.run(main())