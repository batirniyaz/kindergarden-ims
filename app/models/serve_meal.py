from sqlalchemy import ForeignKey, Float, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
import datetime

from app.db.base import Base
from app.config import now_tashkent

if TYPE_CHECKING:
    from app.models.meal_ingredient import Meal
    from app.auth.model import User


class MealServing(Base):
    __tablename__ = "meal_serving"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meal.id"), nullable=False)
    served_by: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent,
                                                          onupdate=now_tashkent)

    meal: Mapped["Meal"] = relationship(back_populates="servings", lazy="selectin")
    user: Mapped["User"] = relationship(back_populates="servings", lazy="selectin")