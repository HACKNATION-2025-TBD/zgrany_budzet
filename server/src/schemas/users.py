from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstname: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    komorka_organizacyjna_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("komorki_organizacyjne.id"),
        nullable=False
    )

    # Relationships
    komorka_organizacyjna: Mapped["KomorkaOrganizacyjna"] = relationship(
        "KomorkaOrganizacyjna",
        back_populates="users"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, firstname={self.firstname!r}, lastname={self.lastname!r}, email={self.email!r})"
