from sqlalchemy import ForeignKey, Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Notification(Base):
    __tablename__ = 'notification'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(length=50), nullable=True)
    message: Mapped[str] = mapped_column(String(length=255), nullable=True)
    month: Mapped[int] = mapped_column(Integer, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    difference_rate: Mapped[float] = mapped_column(Float, nullable=True)
    threshold: Mapped[float] = mapped_column(Float, nullable=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meal.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    timestamp: Mapped[str] = mapped_column(String, nullable=True)
