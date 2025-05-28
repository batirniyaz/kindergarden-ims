import datetime

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, Enum, JSON, TIMESTAMP
from enum import Enum as enum

from app.config import now_tashkent
from app.db.base import Base


class OperationType(enum):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'


class ChangeLog(Base):
    __tablename__ = 'change_log'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    table_name: Mapped[str] = mapped_column(String(255))
    operation: Mapped[OperationType] = mapped_column(Enum(OperationType), nullable=False)
    before_data: Mapped[dict] = mapped_column(JSON, default={}, nullable=True)
    after_data: Mapped[dict] = mapped_column(JSON, default={}, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), default=now_tashkent,
                                                          onupdate=now_tashkent)
