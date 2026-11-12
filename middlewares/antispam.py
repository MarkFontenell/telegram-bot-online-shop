from random import choice

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any
import time
import pytz
from datetime import datetime

from message.user_message import spam_warnings


class AntiSpam(BaseMiddleware):
    def __init__(self, delsec: float = 1.5):
        self.delsec = delsec
        self.user_timestamps: dict[int, float] = {}  # ✅ создаём словарь

    async def __call__(
        self,
        handler: Callable,
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_name = event.from_user.first_name
        user_id = event.from_user.id
        now = time.time()

        # Проверка: если пользователь спамит
        if user_id in self.user_timestamps:
            elapsed = now - self.user_timestamps[user_id]
            if elapsed < self.delsec:
                await event.answer(choice(spam_warnings))
                tz = pytz.timezone('Asia/Yekaterinburg')
                tm = datetime.now(tz)
                print(f'{tm} Пользователь {user_name} спамит! Tg_id : {user_id} ')
                return

        self.user_timestamps[user_id] = now
        return await handler(event, data)
