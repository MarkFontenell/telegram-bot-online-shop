<div align="center">

# ☕ Территория чая и кофе

### Telegram-магазин: от выбора напитка до выдачи заказа

<p>
  <img alt="Python 3.12+" src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img alt="aiogram 3" src="https://img.shields.io/badge/aiogram-3-26A5E4?style=flat-square&logo=telegram&logoColor=white" />
  <img alt="SQLAlchemy 2" src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square" />
  <img alt="SQLite" src="https://img.shields.io/badge/SQLite-async-003B57?style=flat-square&logo=sqlite&logoColor=white" />
  <img alt="Showcase" src="https://img.shields.io/badge/Status-Portfolio%20showcase-566574?style=flat-square" />
</p>

<p>
  <a href="#ru">Русский</a> ·
  <a href="#demo">Демонстрация / Demo</a> ·
  <a href="#en">English</a> ·
  <a href="https://github.com/MarkFontenell">Автор / Author</a>
</p>

</div>

---

<a id="ru"></a>

## О проекте

**«Территория чая и кофе»** — Telegram-приложение для небольшого магазина с каталогом товаров, корзиной, оформлением заказов, бонусной программой и инструментами администратора.

Проект охватывает **весь пользовательский путь**: от регистрации и выбора товара до обработки заказа сотрудником и подтверждения получения покупателем.

> **О статусе проекта:** это восстановленная и очищенная версия коммерческой разработки для портфолио. Исходный рабочий бот больше недоступен. Публичный репозиторий не содержит клиентскую базу, рабочие секреты и историю приватного проекта.

<a id="demo"></a>

## Демонстрация / Live workflow

Ниже — записи работы интерфейса в Telegram. **Для просмотра не нужно запускать код или создавать аккаунт в демоботе.**

### 01 — Регистрация / Registration

Первый запуск, знакомство с ботом и регистрация пользователя.

<p align="center">
  <img src="./reg%20%282%29%20%281%29.gif" alt="Регистрация пользователя в Telegram-боте «Территория чая и кофе»" width="390" />
</p>

### 02 — Каталог, корзина и заказ / Catalog, cart & checkout

Просмотр ассортимента, добавление товаров в корзину и оформление заказа.

Browse products, add items to the cart, and place an order.

<p align="center">
  <img src="./zakaz%20tovara.gif" alt="Демонстрация каталога, корзины и оформления заказа" width="390" />
</p>

### 03 — Панель администратора / Admin panel

Работа с заказами и административными функциями магазина.

Order management and administrative workflows.

<p align="center">
  <img src="./zakaz%20%281%29.gif" alt="Демонстрация панели администратора и работы с заказами" width="390" />
</p>

> GIF-файлы довольно объёмные; на медленном соединении загрузка может занять время. Все опубликованные демонстрации записаны для портфолио.

## Возможности

| Для покупателя | Для администратора |
| :--- | :--- |
| Регистрация с согласованием обработки данных | Управление товарами и категориями |
| Каталог с изображениями и переключением страниц | Добавление и удаление позиций |
| Корзина и расчёт стоимости | Просмотр заказов и сведений о них |
| Оформление заказа с оплатой при получении | Подтверждение оплаты и выдачи |
| Бонусный баланс, списание и начисление бонусов | Выгрузка списка пользователей в Excel |
| Подтверждение получения заказа | Уведомления о новых заказах |

**Важно:** в проекте реализована **оплата при получении**, а не онлайн-эквайринг.

## Технологии и архитектура

| Компонент | Реализация |
| :--- | :--- |
| Telegram Bot API | **aiogram 3**, асинхронные обработчики |
| Сценарии взаимодействия | **FSM** для регистрации и добавления товаров |
| База данных | **SQLAlchemy 2**, асинхронные сессии, **SQLite** в демоконфигурации |
| Отчёты | **pandas**, **XlsxWriter** |
| Дополнительно | Middleware для сессий БД и ограничения частоты действий |
| Развёртывание | Конфигурация для **Amvera** |

```text
Telegram Bot API
       │
       ▼
  aiogram 3 / Router
       │
       ├── handlers/user_hand.py   → регистрация, каталог, корзина, заказы
       ├── handlers/admin_hand.py  → ассортимент, статусы, отчёты
       ├── states/                 → FSM
       ├── keyboards/              → интерфейс Telegram
       └── middlewares/            → антиспам и сессии БД
                                        │
                                        ▼
                              SQLAlchemy (async)
                                        │
                                        ▼
                                     SQLite
```

## Локальный запуск

**Требуется Python 3.12** (или совместимая версия) и новый токен Telegram-бота от [@BotFather](https://t.me/BotFather).

**Windows / PowerShell**

```powershell
git clone https://github.com/MarkFontenell/telegram-bot-online-shop.git
cd telegram-bot-online-shop

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

Copy-Item .env.example .env
# Откройте .env и заполните настройки
python bot.py
```

**Linux / macOS**

```bash
git clone https://github.com/MarkFontenell/telegram-bot-online-shop.git
cd telegram-bot-online-shop

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

cp .env.example .env
# Заполните настройки .env
python bot.py
```

**Переменные окружения**

| Переменная | Назначение |
| :--- | :--- |
| `TOKEN` | Токен **собственного** бота |
| `ADMIN_ID` | Числовой Telegram ID администратора (можно несколько через запятую) |
| `DB_URL` | URL асинхронной БД; пример SQLite уже указан в `.env.example` |
| `STORE_ADDRESS` | Адрес выдачи |
| `STORE_PHONE` | Контактный телефон |
| `STORE_TELEGRAM` | Контакт магазина в Telegram |

Таблицы создаются при старте. Команды администратора: `/inventory`, `/orders`, `/stats`.

## Примечания по безопасности

- Публичная версия **не включает** реальный `.env`, токены, клиентскую БД и историю коммитов закрытого исходного репозитория.
- Скрипты рассчитаны на **учебную и портфолио-демонстрацию**, а не на немедленное использование в действующем магазине.
- Для работы с реальными клиентами необходимы отдельная проверка безопасности, политика обработки и удаления персональных данных, а также проверка соответствия применимым требованиям.

---

<a id="en"></a>

# English version

## Overview

**Tea & Coffee Territory** is a Telegram-based storefront for a small tea and coffee shop. It combines a browsable product catalog, a shopping cart, order processing, a loyalty program, and administrator tools.

The application demonstrates the **complete order lifecycle**: customer registration → product discovery → cart → checkout → staff processing → customer confirmation.

> **Project status:** this is a reconstructed, sanitized showcase of a commercial project. The original live bot is no longer available. This public repository excludes real customer data, production credentials, and the private repository's Git history.

## Demo

The [demo gallery above](#demo) contains three published recordings:

1. **Registration** — first launch, onboarding, and user registration.
2. **Catalog, cart & checkout** — browsing products, managing the cart, and placing an order.
3. **Admin panel** — reviewing orders and working with administrative features.

## Features

| Customer experience | Administration |
| :--- | :--- |
| Registration and consent flow | Product and category management |
| Image-based catalog with pagination | Add and remove products |
| Shopping cart and total calculation | Order review and details |
| Checkout with payment on pickup | Payment and fulfillment confirmation |
| Loyalty points and balance | Excel export of customer records |
| Order receipt confirmation | Notifications about new orders |

**Payment model:** pay on pickup. **No online payment gateway** is implemented.

## Technology & structure

| Layer | Technologies |
| :--- | :--- |
| Bot framework | **Python**, **aiogram 3**, asyncio |
| Interaction flows | **Finite State Machine (FSM)** |
| Persistence | **SQLAlchemy 2**, async sessions, **SQLite** for local demos |
| Reporting | **pandas**, **XlsxWriter** |
| Middleware | Database session injection, basic anti-spam |
| Deployment | **Amvera** configuration |

The project separates user and administrator handlers, FSM states, keyboard layouts, middleware, and database models. Refer to the architecture diagram above for the directory-level overview.

## Run locally

Use **Python 3.12** or another compatible version, and create your **own** Telegram bot via [@BotFather](https://t.me/BotFather).

**Windows / PowerShell**

```powershell
git clone https://github.com/MarkFontenell/telegram-bot-online-shop.git
cd telegram-bot-online-shop

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

Copy-Item .env.example .env
# Edit .env before starting
python bot.py
```

**Linux / macOS**

```bash
git clone https://github.com/MarkFontenell/telegram-bot-online-shop.git
cd telegram-bot-online-shop

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

cp .env.example .env
# Edit .env before starting
python bot.py
```

**Environment variables**

| Variable | Purpose |
| :--- | :--- |
| `TOKEN` | Token for your own Telegram bot |
| `ADMIN_ID` | Numeric administrator Telegram ID(s), comma-separated |
| `DB_URL` | Async SQLAlchemy database connection string |
| `STORE_ADDRESS` | Pickup location |
| `STORE_PHONE` | Public shop phone |
| `STORE_TELEGRAM` | Public shop contact |

The database schema is created at startup. Administrator commands: `/inventory`, `/orders`, `/stats`.

## Security & privacy

- The public showcase includes **no live customer database, private Git history, tokens, or production `.env`**.
- This is a **portfolio demonstration**, not a production security certification.
- Production use requires a privacy policy, secure storage, retention/deletion procedures, an access-control review, and compliance with applicable data-protection laws.

---

<div align="center">
  <sub>Created by <a href="https://github.com/MarkFontenell">MarkFontenell</a> · <a href="./LICENSE">License / Условия использования</a></sub>
</div>
