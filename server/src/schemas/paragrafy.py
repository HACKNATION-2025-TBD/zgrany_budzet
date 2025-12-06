from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Paragraf(Base):
    __tablename__ = "paragrafy"

    kod: Mapped[str] = mapped_column(String(10), primary_key=True)
    tresc: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"Paragraf(kod={self.kod!r}, tresc={self.tresc[:50]!r}...)"
