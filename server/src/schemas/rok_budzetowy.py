from sqlalchemy import Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class RokBudzetowy(Base):
    __tablename__ = "rok_budzetowy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    planowanie_budzetu_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("planowanie_budzetu.id"),
        nullable=False
    )
    limit: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    potrzeba: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    
    # Relationship
    planowanie_budzetu: Mapped["PlanowanieBudzetu"] = relationship(back_populates="lata_budzetowe")

    def __repr__(self) -> str:
        return f"RokBudzetowy(id={self.id!r}, limit={self.limit!r}, potrzeba={self.potrzeba!r})"
