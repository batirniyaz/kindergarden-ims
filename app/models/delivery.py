from sqlalchemy import ForeignKey, Float, Integer, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
import datetime

from app.db.base import Base
from app.config import now_tashkent

if TYPE_CHECKING:
    from app.models.meal_ingredient import Ingredient
    from app.auth.model import User


class IngredientDelivery(Base):
    __tablename__ = 'ingredient_delivery'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('ingredient.id', ondelete='CASCADE'))
    weight: Mapped[float] = mapped_column(Float)  # Weight in grams
    accepted: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))  # Staff who accepted the delivery
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent,
                                                          onupdate=now_tashkent)

    user: Mapped["User"] = relationship(back_populates="deliveries", lazy="selectin")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="deliveries", lazy="selectin")
