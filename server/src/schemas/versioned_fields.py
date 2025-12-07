from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class VersionedStringField(Base):
    __tablename__ = "versioned_string_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'planowanie_budzetu', 'rok_budzetowy'
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_user_id])

    def __repr__(self) -> str:
        return f"VersionedStringField(id={self.id!r}, field_name={self.field_name!r}, value={self.value!r})"


class VersionedNumericField(Base):
    __tablename__ = "versioned_numeric_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_user_id])

    def __repr__(self) -> str:
        return f"VersionedNumericField(id={self.id!r}, field_name={self.field_name!r}, value={self.value!r})"


class VersionedForeignKeyField(Base):
    __tablename__ = "versioned_foreign_key_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value_string: Mapped[str | None] = mapped_column(String(10), nullable=True)  # for kod-based FKs
    value_int: Mapped[int | None] = mapped_column(Integer, nullable=True)  # for id-based FKs
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_user_id])

    def __repr__(self) -> str:
        return f"VersionedForeignKeyField(id={self.id!r}, field_name={self.field_name!r})"
