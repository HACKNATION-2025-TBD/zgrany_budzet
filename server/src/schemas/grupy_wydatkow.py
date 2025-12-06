from sqlalchemy import Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class GrupaWydatkow(Base):
    __tablename__ = "grupy_wydatkow"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nazwa: Mapped[str] = mapped_column(String(255), nullable=False)
    paragrafy: Mapped[dict | list | str] = mapped_column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f"GrupaWydatkow(id={self.id!r}, nazwa={self.nazwa!r})"
