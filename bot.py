import asyncio
from bot_instance import bot
from aiogram import Bot, Dispatcher
from config import BotConfig
from database.database import drop_db, create_db, session_maker
from handlers.admin_hand import admin_router

from handlers.user_hand import user_router
from message.user_message import welcome_message
from middlewares.antispam import AntiSpam
import os
from dotenv import load_dotenv

from middlewares.session import DataBaseSession

load_dotenv()

async def on_startup(bot : Bot):
    run_par = False
    if run_par:
        await drop_db()
    await create_db()

async def on_shutdown(bot : Bot):
    print('Bot умер(ненадолго )')


def register_routers(dp: Dispatcher) -> None:
    dp.include_router(user_router)
    dp.include_router(admin_router)

async def main(bot: Bot) -> None:
    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.message.middleware(AntiSpam(delsec=0.5))  # можно изменить интервал
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    dp.callback_query.middleware(AntiSpam(delsec=0.5))
    config = BotConfig(
        admin_ids=[int(v.strip()) for v in os.getenv("ADMIN_ID", "").split(",") if v.strip().isdigit()],
        welcome_message=welcome_message
    )
    dp['config'] = config
    register_routers(dp)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main(bot))