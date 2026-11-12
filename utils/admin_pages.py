from aiogram import types
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from database.models import Product, Order

PRODUCTS_PER_PAGE = 1

async def send_admin_page(target, session: AsyncSession, page_ad: int):
    result = await session.execute(
        select(Product).options(selectinload(Product.category))
    )
    products = result.scalars().all()

    if not products:
        await target.answer("😔 Сейчас в магазине нет товаров.")
        return

    total_pages = (len(products) - 1) // PRODUCTS_PER_PAGE + 1
    start = (page_ad - 1) * PRODUCTS_PER_PAGE
    product = products[start]

    category_name = product.category.name if product.category else "—"

    text = (
        f"<b>{product.name}</b>\n"
        f"💰 <b>Цена:</b> {int(product.price)} ₽\n"
        f"📦 <b>В наличии:</b> {product.count} шт.\n"
        f"🆔 <b>ID:</b> {product.id}\n"
        f"📝 <b>Описание:</b> {product.description or '—'}\n"
        f"🗄 <b>Категория:</b> {category_name}"
    )

    keyboard_ad = InlineKeyboardBuilder()
    if page_ad > 1:
        keyboard_ad.button(text="⬅ Назад", callback_data=f"page_ad:{page_ad-1}")
    if page_ad < total_pages:
        keyboard_ad.button(text="➡ Далее", callback_data=f"page_ad:{page_ad+1}")
    keyboard_ad.adjust(2)

    if isinstance(target, Message):
        await target.answer_photo(photo=product.image, caption=text, parse_mode="HTML", reply_markup=keyboard_ad.as_markup())
    elif isinstance(target, CallbackQuery):
        await target.message.edit_media(
            media=InputMediaPhoto(media=product.image, caption=text, parse_mode="HTML"),
            reply_markup=keyboard_ad.as_markup()
        )
        await target.answer()

ORDERS_PER_PAGE = 9

async def send_orders_page(chat_id: int, session: AsyncSession, page: int, bot):
    offset = (page - 1) * ORDERS_PER_PAGE

    result = await session.execute(
        select(Order).order_by(Order.created.desc()).offset(offset).limit(ORDERS_PER_PAGE)
    )
    orders = result.scalars().all()

    count_result = await session.execute(select(func.count()).select_from(Order))
    total_orders = count_result.scalar()
    total_pages = (total_orders + ORDERS_PER_PAGE - 1) // ORDERS_PER_PAGE

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(
                text=f"📦 Заказ #{order.id} | {order.total_amount} ₽",
                callback_data=f"view_order:{order.id}:page:{page}"
            )
        ] for order in orders
    ])

    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"open_orders_page:{page-1}"))
    if page < total_pages:
        pagination_buttons.append(types.InlineKeyboardButton(text="➡️ Вперёд", callback_data=f"open_orders_page:{page+1}"))

    if pagination_buttons:
        keyboard.inline_keyboard.append(pagination_buttons)

    await bot.send_message(chat_id, "📦 <b>Список заказов:</b>", reply_markup=keyboard, parse_mode="HTML")