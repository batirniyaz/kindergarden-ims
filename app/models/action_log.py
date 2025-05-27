import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, TIMESTAMP, ForeignKey

from app.db.base import Base
from app.config import now_tashkent



class ActionLog(Base):
    __tablename__ = 'action_log'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    method: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(255))
    query: Mapped[str] = mapped_column(String(255))
    status_code: Mapped[int] = mapped_column(Integer)
    process_time: Mapped[float] = mapped_column(Integer)
    role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_host: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),default=now_tashkent,onupdate=now_tashkent)
