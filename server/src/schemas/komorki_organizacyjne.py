from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .users import User


class KomorkaOrganizacyjna(Base):
    __tablename__ = "komorki_organizacyjne"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nazwa: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="komorka_organizacyjna"
    )

    def __repr__(self) -> str:
        return f"KomorkaOrganizacyjna(id={self.id!r}, nazwa={self.nazwa!r})"
