from sqlalchemy import ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
import datetime

from app.db.base import Base
from app.config import now_tashkent


class PortionEstimation(Base):
    __tablename__ = "portion_estimation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meal.id"), nullable=False)
    meal_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    portion_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent,
                                                          onupdate=now_tashkent)
