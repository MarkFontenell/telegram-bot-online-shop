from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import Product

PRODUCTS_PER_PAGE = 1

async def send_products_page(target, session: AsyncSession, page: int):
    products = await session.execute(select(Product))
    products = products.scalars().all()

    if not products:
        await target.answer("😔 Сейчас в магазине нет товаров.")
        return

    total_pages = (len(products) - 1) // PRODUCTS_PER_PAGE + 1
    start = (page - 1) * PRODUCTS_PER_PAGE
    product = products[start]

    text = (
        f"<b>{product.name}</b>\n"
        f"💰 <b>Цена:</b> {int(product.price)} ₽\n"
        f"📦 <b>В наличии:</b> {product.count} шт.\n"
        f"🆔 <b>ID:</b> {product.id}\n"
        f"📝 <b>Описание:</b> {product.description or '—'}"
    )

    keyboard = InlineKeyboardBuilder()
    if page > 1:
        keyboard.button(text="⬅ Назад", callback_data=f"page:{page-1}")
    if page < total_pages:
        keyboard.button(text="➡ Далее", callback_data=f"page:{page+1}")
    keyboard.row(InlineKeyboardButton(text="🛒 В корзину", callback_data=f"add_to_cart:{product.id}"))
    keyboard.adjust(2)

    if isinstance(target, Message):
        await target.answer_photo(photo=product.image, caption=text, parse_mode="HTML", reply_markup=keyboard.as_markup())
    elif isinstance(target, CallbackQuery):
        await target.message.edit_media(
            media=InputMediaPhoto(media=product.image, caption=text, parse_mode="HTML"),
            reply_markup=keyboard.as_markup()
        )
        await target.answer()
