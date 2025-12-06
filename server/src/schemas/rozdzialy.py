from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Rozdzial(Base):
    __tablename__ = "rozdzialy"

    kod: Mapped[str] = mapped_column(String(10), primary_key=True)
    nazwa: Mapped[str] = mapped_column(String(255), nullable=False)
    dzial: Mapped[str] = mapped_column(String(10), nullable=False)

    def __repr__(self) -> str:
        return f"Rozdzial(kod={self.kod!r}, nazwa={self.nazwa!r}, dzial={self.dzial!r})"
