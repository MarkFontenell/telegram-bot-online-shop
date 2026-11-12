from sqlalchemy import String, Float, BigInteger, func, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import expression
from datetime import datetime
import pytz

ekb_tz = pytz.timezone("Asia/Yekaterinburg")

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nick: Mapped[str] = mapped_column(String(30))
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(12))
    created: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ekb_tz)
    )
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    qr_code: Mapped[str] = mapped_column(default='')
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    bonus_balance: Mapped[int] = mapped_column(default=0)


class Category(Base):
    __tablename__ = 'category'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

class Product(Base):
    __tablename__ = 'product'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000))
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
    count: Mapped[int] = mapped_column(default=0)
    image: Mapped[str] = mapped_column(default='')
    created: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ekb_tz)
    )
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'), nullable=False)
    category: Mapped['Category'] = relationship(backref='product')

class Cart(Base):
    __tablename__ = 'cart'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.tg_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int]

    user: Mapped['Users'] = relationship(backref='cart')
    product: Mapped['Product'] = relationship(backref='cart')


class OrderItem(Base):
    __tablename__ = 'order_item'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"))
    quantity: Mapped[int]

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship()

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ekb_tz)
    )
    total_amount: Mapped[int]
    payment_method: Mapped[str] = mapped_column(String)
    is_paid: Mapped[bool] = mapped_column(default=False)
    is_issued: Mapped[bool] = mapped_column(default=False)
    user_confirmed: Mapped[bool] = mapped_column(default=False)

    user: Mapped["Users"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete")

    bonus_used: Mapped[int] = mapped_column(default=0)
    raw_total: Mapped[int]
