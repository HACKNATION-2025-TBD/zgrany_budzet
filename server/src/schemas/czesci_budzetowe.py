from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class CzescBudzetowa(Base):
    __tablename__ = "czesci_budzetowe"

    kod: Mapped[str] = mapped_column(String(10), primary_key=True)
    nazwa: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"CzescBudzetowa(kod={self.kod!r}, nazwa={self.nazwa!r})"
