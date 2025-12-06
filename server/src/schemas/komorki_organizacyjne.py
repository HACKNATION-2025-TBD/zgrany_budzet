from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class KomorkaOrganizacyjna(Base):
    __tablename__ = "komorki_organizacyjne"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nazwa: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"KomorkaOrganizacyjna(id={self.id!r}, nazwa={self.nazwa!r})"
