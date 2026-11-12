from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from token_api import TOKEN
from aiogram import Bot


bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode='HTML')
)