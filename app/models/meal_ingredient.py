from sqlalchemy import ForeignKey, Float, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
import datetime

from app.db.base import Base
from app.config import now_tashkent


if TYPE_CHECKING:
    from app.models.serve_meal import MealServing
    from app.models.delivery import IngredientDelivery

class MealIngredient(Base):
    __tablename__ = "meal_ingredient"

    meal_id: Mapped[int] = mapped_column(ForeignKey("meal.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredient.id", ondelete="CASCADE"), primary_key=True)
    weight: Mapped[float] = mapped_column(Float)

    ingredient: Mapped["Ingredient"] = relationship(back_populates="meals", lazy="selectin")
    meal: Mapped["Meal"] = relationship(back_populates="ingredients", lazy="selectin")


class Ingredient(Base):
    __tablename__ = 'ingredient'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(length=255), unique=True)
    weight: Mapped[float] = mapped_column(Float) # Weight in grams
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent,
                                                          onupdate=now_tashkent)

    meals: Mapped[List["MealIngredient"]] = relationship(back_populates="ingredient", lazy="selectin")
    deliveries: Mapped[List["IngredientDelivery"]] = relationship(back_populates="ingredient", lazy="selectin")


class Meal(Base):
    __tablename__ = 'meal'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(length=255), unique=True)
    added_by: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent,
                                                          onupdate=now_tashkent)

    ingredients: Mapped[List["MealIngredient"]] = relationship(back_populates="meal", lazy="selectin")
    servings: Mapped[List["MealServing"]] = relationship(back_populates="meal", lazy="selectin")

