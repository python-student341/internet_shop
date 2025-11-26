from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger
from pydantic import EmailStr
from datetime import datetime

from database.database import Base


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()

    card = relationship('CardModel', back_populates='user')
    cart = relationship('CartModel', back_populates='user')


class CardModel(Base):
    __tablename__ = 'card'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    card: Mapped[int] = mapped_column(BigInteger, unique=True)
    card_password: Mapped[str] = mapped_column()
    balance: Mapped[int] = mapped_column()

    user = relationship('UserModel', back_populates='card')


class CategoryModel(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    products = relationship('ProductModel', back_populates='category')


class ProductModel(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    image_path: Mapped[str] = mapped_column(nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete="CASCADE"))

    category = relationship('CategoryModel', back_populates='products')


class CartModel(Base):
    __tablename__ = 'cart'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    total_price: Mapped[int] = mapped_column(default=0)

    user = relationship('UserModel', back_populates='cart')
    items = relationship('CartItemModel', back_populates='cart')


class CartItemModel(Base):
    __tablename__ = 'cart_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey('cart.id', ondelete='CASCADE'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column(default=1)

    cart = relationship('CartModel', back_populates='items')
    product = relationship('ProductModel')