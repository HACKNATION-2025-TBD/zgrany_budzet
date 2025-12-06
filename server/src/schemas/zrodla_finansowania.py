from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ZrodloFinansowania(Base):
    __tablename__ = "zrodla_finansowania"

    kod: Mapped[str] = mapped_column(String(10), primary_key=True)
    nazwa: Mapped[str] = mapped_column(String(1000), nullable=False)
    opis: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"ZrodloFinansowania(kod={self.kod!r}, nazwa={self.nazwa!r})"
