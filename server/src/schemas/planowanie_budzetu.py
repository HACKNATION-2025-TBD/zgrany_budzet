from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .rok_budzetowy import RokBudzetowy


class PlanowanieBudzetu(Base):
    __tablename__ = "planowanie_budzetu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    lata_budzetowe: Mapped[list["RokBudzetowy"]] = relationship(back_populates="planowanie_budzetu")

    def __repr__(self) -> str:
        return f"PlanowanieBudzetu(id={self.id!r})"
