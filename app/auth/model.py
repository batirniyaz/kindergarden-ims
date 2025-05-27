from enum import Enum as enum_Enum
from typing import List, TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, TIMESTAMP, ForeignKey, Enum as sql_Enum

import datetime

from app.db.base import Base
from app.config import now_tashkent

if TYPE_CHECKING:
    from app.models.serve_meal import MealServing
    from app.models.delivery import IngredientDelivery


class UserRole(enum_Enum):
    COOK = 'cook'
    ADMIN = 'admin'
    MANAGER = 'manager'


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone: Mapped[str] = mapped_column(String(length=13), unique=True)
    email: Mapped[str | EmailStr] = mapped_column(String(length=50), unique=True)
    username: Mapped[str] = mapped_column(String(length=25), unique=True)
    first_name: Mapped[str] = mapped_column(String(length=25))
    last_name: Mapped[str] = mapped_column(String(length=25))
    hashed_password: Mapped[str] = mapped_column(String(length=255))

    role: Mapped[UserRole] = mapped_column(sql_Enum(UserRole))
    servings: Mapped[List["MealServing"]] = relationship(back_populates="user", lazy="selectin")
    deliveries: Mapped[List["IngredientDelivery"]] = relationship(back_populates='user', lazy="selectin")

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent,onupdate=now_tashkent)


class LoginInfo(Base):
    __tablename__ = 'login_info'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    email: Mapped[str | EmailStr] = mapped_column(String(length=50))
    phone: Mapped[str] = mapped_column(String(length=13))
    username: Mapped[str] = mapped_column(String(length=25))
    login_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent)


class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    jti: Mapped[str] = mapped_column(String(length=255), unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent)