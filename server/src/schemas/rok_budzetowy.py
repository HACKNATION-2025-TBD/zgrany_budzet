from sqlalchemy import Integer, ForeignKey
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
    rok: Mapped[int] = mapped_column(Integer, nullable=False)
    
    limit_versions: Mapped[list["VersionedNumericField"]] = relationship(
        primaryjoin="and_(RokBudzetowy.id == foreign(VersionedNumericField.entity_id), "
                   "VersionedNumericField.entity_type == 'rok_budzetowy', "
                   "VersionedNumericField.field_name == 'limit')",
        viewonly=True
    )
    potrzeba_versions: Mapped[list["VersionedNumericField"]] = relationship(
        primaryjoin="and_(RokBudzetowy.id == foreign(VersionedNumericField.entity_id), "
                   "VersionedNumericField.entity_type == 'rok_budzetowy', "
                   "VersionedNumericField.field_name == 'potrzeba')",
        viewonly=True
    )

    planowanie_budzetu: Mapped["PlanowanieBudzetu"] = relationship(back_populates="lata_budzetowe")

    def __repr__(self) -> str:
        return f"RokBudzetowy(id={self.id!r}, rok={self.rok!r})"
