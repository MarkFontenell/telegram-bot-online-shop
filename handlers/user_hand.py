import os
from random import choice, random
from typing import Union, Optional

from aiogram import Dispatcher, Bot, types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold, hitalic
from sqlalchemy import select, delete, update

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, relationship

from bot_instance import bot
from database.models import Users, Product, Cart, Order, OrderItem
from message.user_message import welcome_messages, long_name_responses, returning_welcome_messages
from states.user_fsm import Registration
from keyboards.user_keyboard import start_button, request_phone_keyboard, consent_keyboard, user_main_keyboard
from config import BotConfig
from utils.product_pages import send_products_page

user_router = Router()

@user_router.message(CommandStart())
async def cmd_start(msg: Message, config: BotConfig, session: AsyncSession) -> None:
    if msg.from_user.id not in config.admin_ids:

        result = await session.execute(select(Users).where(Users.tg_id == msg.from_user.id))
        user = result.scalars().first()
        if user:
            text = choice(returning_welcome_messages).format(name=user.nick)
            await msg.answer(text, reply_markup=user_main_keyboard)
        else:
            await msg.answer(config.welcome_message, reply_markup=start_button)
    else:
        await msg.answer(f"{hbold('Добро пожаловать, администратор!')} 👑\n\n"
                         "Вы вошли в панель управления ботом «Территория чая и кофе» 🍃.\n\n"
                         "Вот что доступно вам:\n"
                         "🔹 Управление заказами\n"
                         "🔹 Обновление ассортимента чая\n"
                         "🔹 Просмотр статистики и отчётов\n"
                         "🔹 Ответы на вопросы пользователей\n\n"
                         "Используйте команды, чтобы быстро и эффективно управлять ботом:\n"
                         "/orders - посмотреть все заказы\n"
                         "/inventory - обновить ассортимент\n"
                         "/stats - получить статистику бота\n\n"
                         "✨ Спасибо за управление «Территорией чая и кофе»! 🍵", reply_markup=user_main_keyboard
                         )


@user_router.callback_query(F.data == "start_journey")
async def start_registration(callback: types.CallbackQuery, state: FSMContext) :
    await callback.message.delete()

    await callback.message.answer(choice(welcome_messages))
    await state.set_state(Registration.name)
    await callback.answer()

# Принимаем имя и спрашиваем номер
@user_router.message(Registration.name)
async def get_name(msg: types.Message, state: FSMContext):
    name = msg.text.strip()

    if len(name) > 30:
        await msg.answer(choice(long_name_responses))
        return

    await state.update_data(name=name)
    # Запрашиваем согласие
    await msg.answer(
        f"Отлично, {name}! 🍃\n"
        "Перед тем как продолжить, пожалуйста, согласись на обработку персональных данных.",
        reply_markup=consent_keyboard
    )
    await state.set_state(Registration.consent_given)


# Принимаем согласие
@user_router.message(Registration.consent_given)
async def get_consent(msg: types.Message, state: FSMContext):
    if msg.text != "Согласен на обработку персональных данных":
        await msg.answer("Для продолжения регистрации нужно согласиться на обработку персональных данных.")
        return
    await state.update_data(consent_given=True)

    # После согласия запрашиваем номер телефона
    await msg.answer(
        "Спасибо! Теперь, пожалуйста, отправь свой номер телефона, нажав кнопку ниже 📲",
        reply_markup=request_phone_keyboard
    )
    await state.set_state(Registration.number)


# Принимаем номер телефона и завершаем регистрацию (как у тебя)
@user_router.message(Registration.number, F.contact)
async def get_contact(msg: types.Message, state: FSMContext, session : AsyncSession):
    data = await state.get_data()
    name = data.get("name")
    tg_id = msg.from_user.id
    phone = msg.contact.phone_number
    if msg.contact.user_id != msg.from_user.id:
        await msg.answer("Отправьте собственный контакт.")
        return
    consent = data.get("consent_given", False)

    obj = Users(
        nick = name,
        tg_id = tg_id,
        phone_number = phone,
        consent_given = consent,)

    session.add(obj)
    await session.commit()


    # Здесь сохраняем в базу: name, tg_id, phone и consent

    await msg.answer(
        f"Регистрация завершена! 🎉\n\n"
        f"{hbold(f'Добро пожаловать в «Территорию чая и кофе», {name}!')} 🍵\n"
        "Теперь тебе доступны бонусы, каталог и оформление заказов.\n",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await msg.answer('"Желаем ароматных открытий и уютных чайных моментов 🌿✨"', reply_markup=user_main_keyboard)
    await state.clear()

@user_router.message(F.text == '❓ FAQ')
async def FAQ(msg: Message):
    await msg.answer(
        "🍵 *Часто задаваемые вопросы о нашем чайном магазине:*\n\n"
        "🔹 *Что делает этот бот?*\n",
        parse_mode="Markdown"
    )

@user_router.message(F.text == '📞Контакты')
async def contacts(msg: Message):
    await msg.answer(
        "Контакты магазина:\n"
        f"Адрес: {os.getenv('STORE_ADDRESS', 'уточните у продавца')}\n"
        f"Телефон: {os.getenv('STORE_PHONE', 'не указан')}\n"
        f"Telegram: {os.getenv('STORE_TELEGRAM', 'не указан')}"
    )


@user_router.message(F.text == '⚙️ Профиль')
async def profile(msg: Message, session: AsyncSession):
    result = await session.execute(
        select(Users).where(Users.tg_id == msg.from_user.id)
    )
    user = result.scalar_one_or_none()

    if user:
        await msg.answer(
            text=(
                "🧾 <b>Профиль пользователя</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>Имя:</b> <code>{user.nick}</code>\n"
                f"📱 <b>Телефон:</b> <code>{user.phone_number}</code>\n"
                f"🗓 <b>Регистрация:</b> <code>{user.created.strftime('%d.%m.%Y %H:%M')}</code>\n"
                "━━━━━━━━━━━━━━━━━━━━"
            ),
            parse_mode='HTML'
        )
    else:
        await msg.answer("❌ Пользователь не найден. Вы зарегистрированы?")

@user_router.message(F.text == "🎁 Мои бонусы")
async def show_bonus_balance(msg: Message, session: AsyncSession):
    user = await session.scalar(select(Users).where(Users.tg_id == msg.from_user.id))
    if not user:
        await msg.answer("Пользователь не найден.")
        return

    await msg.answer(f"💰 Ваш бонусный баланс: {user.bonus_balance} ₽")

@user_router.message(F.text == '📋 Меню')
async def show_menu(msg: Message, session: AsyncSession):
    await send_products_page(msg, session, page=1)

@user_router.callback_query(F.data.startswith("page:"))
async def paginate_products(callback: CallbackQuery, session: AsyncSession):
    page = int(callback.data.split(":")[1])
    await send_products_page(callback, session, page)

@user_router.callback_query(F.data.startswith("add_to_cart:"))
async def add_to_cart(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split(":")[1])
    user_tg_id = callback.from_user.id

    # Получаем товар
    product = await session.scalar(select(Product).where(Product.id == product_id))
    if not product:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return

    # Проверка наличия
    if product.count == 0:
        await callback.answer("❌ Этого товара нет в наличии!", show_alert=True)
        return

    # Проверяем, есть ли уже этот товар в корзине
    cart_item = await session.scalar(
        select(Cart).where(
            Cart.user_id == user_tg_id,
            Cart.product_id == product_id
        )
    )

    if cart_item:
        if cart_item.quantity >= product.count:
            await callback.answer(
                f"⚠️ Нельзя добавить больше {product.count} шт.",
                show_alert=True
            )
            return
        cart_item.quantity += 1
    else:
        session.add(Cart(user_id=user_tg_id, product_id=product_id, quantity=1))

    await session.commit()
    await callback.answer("✅ Добавлено в корзину!", show_alert=False)


@user_router.message(F.text == '🛒 Корзина')
async def korzina(msg: Message, session: AsyncSession):
    user_tg_id = msg.from_user.id

    result = await session.execute(
        select(Cart, Product)
        .join(Product, Cart.product_id == Product.id)
        .where(Cart.user_id == user_tg_id)
    )
    cart_items = result.all()

    if not cart_items:
        await msg.answer("🛒 Ваша корзина пуста.")
        return

    text, total = "<b>🧺 Ваша корзина:</b>\n\n", 0

    for cart, product in cart_items:
        subtotal = cart.quantity * product.price
        total += subtotal
        text += f"{product.name} — {cart.quantity} шт. × {int(product.price)} ₽ = {int(subtotal)} ₽\n"

    text += f"\n💰 <b>Итого:</b> {int(total)} ₽"

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💳 Оплатить заказ", callback_data="pay_order")]
    ])

    await msg.answer(text, parse_mode="HTML", reply_markup=keyboard)

@user_router.callback_query(F.data == "pay_order")
async def choose_payment_method(callback: CallbackQuery, session: AsyncSession):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💵 Оплата при получении", callback_data="pay_cash")],
        [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_cart")]
    ])
    await callback.message.edit_text("Выберите способ оплаты:", reply_markup=keyboard)
    await callback.answer()

@user_router.callback_query(F.data == "back_to_cart")
async def back_to_cart(callback: CallbackQuery, session: AsyncSession):
    user_tg_id = callback.from_user.id

    result = await session.execute(
        select(Cart, Product)
        .join(Product, Cart.product_id == Product.id)
        .where(Cart.user_id == user_tg_id)
    )
    cart_items = result.all()

    if not cart_items:
        await callback.message.edit_text("🛒 Ваша корзина пуста.")
        await callback.answer()
        return

    text, total = "<b>🧺 Ваша корзина:</b>\n\n", 0
    for cart, product in cart_items:
        subtotal = cart.quantity * product.price
        total += subtotal
        text += f"{product.name} — {cart.quantity} шт. × {int(product.price)} ₽ = {int(subtotal)} ₽\n"

    text += f"\n💰 <b>Итого:</b> {int(total)} ₽"

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💳 Оплатить заказ", callback_data="pay_order")]
    ])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

@user_router.callback_query(F.data == "pay_cash")
async def ask_bonus_amount(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user_tg_id = callback.from_user.id

    result = await session.execute(
        select(Cart, Product).join(Product).where(Cart.user_id == user_tg_id)
    )
    cart_items = result.all()
    if not cart_items:
        await callback.message.edit_text("🛒 Ваша корзина пуста.")
        await callback.answer()
        return

    user = await session.scalar(select(Users).where(Users.tg_id == user_tg_id))
    total = sum([cart.quantity * float(product.price) for cart, product in cart_items])
    max_bonus = min(float(user.bonus_balance or 0), int(total * 0.3))


    if max_bonus > 0:
        await state.update_data(total=total, cart_items=cart_items)
        await state.set_state("awaiting_bonus_amount")

        await callback.message.edit_text(
            f"💰 Вы можете списать до {max_bonus} бонусных рублей.\n"
            f"Введите сумму для списания (или 0, если не хотите тратить бонусы):"
        )
        await callback.answer()
    else:
        # Передаём bot явно, чтобы process_order всегда имел доступ к отправке сообщений
        await process_order(callback.bot, callback, session, state, bonus_used=0)
        await callback.answer()


# --- handle_bonus_input (теперь принимает Bot и вызывает process_order с реальным bot) ---
@user_router.message(StateFilter("awaiting_bonus_amount"))
async def handle_bonus_input(msg: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    try:
        bonus_used = int(msg.text.strip())
        if bonus_used < 0:
            raise ValueError
    except ValueError:
        await msg.answer("Введите корректное количество бонусных рублей.")
        return

    user = await session.scalar(select(Users).where(Users.tg_id == msg.from_user.id))
    data = await state.get_data()
    total = data.get("total", 0)
    max_bonus = min(int(user.bonus_balance or 0), int(total * 0.3))

    if bonus_used > max_bonus:
        await msg.answer(f"Вы можете списать не более {max_bonus} бонусных рублей.")
        return

    await state.clear()

    # Передаём реальный bot и сам message в process_order
    await process_order(bot, msg, session, state, bonus_used=bonus_used)


# --- process_order: теперь принимает Bot и event (Message или CallbackQuery) ---
async def process_order(bot: Bot,
                        event: Union[Message, CallbackQuery],
                        session: AsyncSession,
                        state: Optional[FSMContext] = None,
                        bonus_used: int = 0):
    user_tg_id = event.from_user.id

    result = await session.execute(
        select(Cart, Product).join(Product).where(Cart.user_id == user_tg_id)
    )
    cart_items = result.all()
    if not cart_items:
        # корректно отвечаем в зависимости от типа события
        if isinstance(event, CallbackQuery):
            await event.message.edit_text("🛒 Ваша корзина пуста.")
        else:
            await bot.send_message(user_tg_id, "🛒 Ваша корзина пуста.")
        return

    user = await session.scalar(select(Users).where(Users.tg_id == user_tg_id))
    if not user:
        if isinstance(event, CallbackQuery):
            await event.message.edit_text("Пользователь не найден в БД.")
        else:
            await bot.send_message(user_tg_id, "Пользователь не найден в БД.")
        return

    total = sum(cart.quantity * product.price for cart, product in cart_items)
    final_amount = total - bonus_used

    # Создаём заказ
    order = Order(
        user_id=user.id,
        total_amount=int(final_amount),
        payment_method="При получении",
        bonus_used=int(bonus_used),
        raw_total=int(total)
    )
    session.add(order)
    await session.flush()  # чтобы order.id стал доступен

    # Добавляем позиции заказа и корректируем остатки (если нужно)
    for cart, product in cart_items:
        session.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=int(cart.quantity)
        ))
        stock_update = await session.execute(
            update(Product)
            .where(Product.id == product.id, Product.count >= int(cart.quantity))
            .values(count=Product.count - int(cart.quantity))
        )
        if int(cart.quantity) <= 0 or stock_update.rowcount != 1:
            await session.rollback()
            await bot.send_message(user_tg_id, f"Недостаточно товара «{product.name}». Обновите корзину.")
            return

    # Очищаем корзину
    await session.execute(delete(Cart).where(Cart.user_id == user_tg_id))

    # Списываем бонусы у пользователя
    if bonus_used > 0:
        user.bonus_balance = (user.bonus_balance or 0) - int(bonus_used)
        if user.bonus_balance < 0:
            user.bonus_balance = 0

    # Убираем кол во товаров из ассортимента

    await session.commit()

    # Сообщаем клиенту
    await bot.send_message(
        user_tg_id,
        f"✅ Заказ принят! Адрес получения: {os.getenv('STORE_ADDRESS', 'уточните у продавца')}"
    )

    # Уведомляем админов — поддерживаю несколько ID разделённых запятой в ENV
    admin_ids = []
    env_admins = os.getenv('ADMIN_ID', '')
    if env_admins:
        for part in env_admins.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                admin_ids.append(int(part))
            except ValueError:
                continue

    # Отправляем уведомление персоналу: кнопка открывает меню /orders (open_orders_page:1)
    for admin_id in admin_ids:
        try:
            await bot.send_message(
                admin_id,
                f"📦 Новый заказ на сумму {int(final_amount)} ₽ (ID #{order.id})",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(
                        text="📋 Открыть список заказов",
                        callback_data=f"open_orders_page:1"
                    )]
                ])
            )
        except Exception:
            # можно логировать ошибку, но не падать
            pass

@user_router.callback_query(F.data.startswith("confirm_user:"))
async def confirm_user(callback: CallbackQuery, session: AsyncSession):
    order_id = int(callback.data.split(":")[1])
    order = await session.get(Order, order_id)

    if not order:
        await callback.answer("Заказ не найден.")
        return

    # Находим пользователя (по tg_id) и сравниваем корректно
    user = await session.scalar(select(Users).where(Users.tg_id == callback.from_user.id))
    if not user or user.id != order.user_id:
        await callback.answer("У вас нет прав подтверждать этот заказ.", show_alert=True)
        return

    if order.user_confirmed:
        await callback.answer("Заказ уже подтверждён.")
        return

    order.user_confirmed = True

    # Начисляем бонусы, если они не были использованы в заказе
    if getattr(order, "bonus_used", 0) == 0:
        # raw_total должен быть в заказе
        earned_bonus = int(getattr(order, "raw_total", 0) * 0.1)
        user.bonus_balance = (user.bonus_balance or 0) + earned_bonus

    await session.commit()
    await callback.message.edit_text("✅ Спасибо! Приходите ещё!")
    await callback.answer()