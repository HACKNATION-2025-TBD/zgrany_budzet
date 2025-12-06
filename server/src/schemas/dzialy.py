from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Dzial(Base):
    __tablename__ = "dzialy"

    kod: Mapped[str] = mapped_column(String(10), primary_key=True)
    nazwa: Mapped[str] = mapped_column(String(255), nullable=False)
    PKD: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"Dzial(kod={self.kod!r}, nazwa={self.nazwa!r})"
