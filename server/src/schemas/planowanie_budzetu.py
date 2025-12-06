from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.schemas.czesci_budzetowe import CzescBudzetowa

from .base import Base


class PlanowanieBudzetu(Base):
    __tablename__ = "planowanie_budzetu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Versioned relationships
    nazwa_projektu_versions: Mapped[list["VersionedStringField"]] = relationship(
        primaryjoin="and_(PlanowanieBudzetu.id == foreign(VersionedStringField.entity_id), "
                   "VersionedStringField.entity_type == 'planowanie_budzetu', "
                   "VersionedStringField.field_name == 'nazwa_projektu')",
        viewonly=True
    )
    nazwa_zadania_versions: Mapped[list["VersionedStringField"]] = relationship(
        primaryjoin="and_(PlanowanieBudzetu.id == foreign(VersionedStringField.entity_id), "
                   "VersionedStringField.entity_type == 'planowanie_budzetu', "
                   "VersionedStringField.field_name == 'nazwa_zadania')",
        viewonly=True
    )
    szczegolowe_uzasadnienie_realizacji_versions: Mapped[list["VersionedStringField"]] = relationship(
        primaryjoin="and_(PlanowanieBudzetu.id == foreign(VersionedStringField.entity_id), "
                   "VersionedStringField.entity_type == 'planowanie_budzetu', "
                   "VersionedStringField.field_name == 'szczegolowe_uzasadnienie_realizacji')",
        viewonly=True
    )
    budzet_versions: Mapped[list["VersionedStringField"]] = relationship(
        primaryjoin="and_(PlanowanieBudzetu.id == foreign(VersionedStringField.entity_id), "
                   "VersionedStringField.entity_type == 'planowanie_budzetu', "
                   "VersionedStringField.field_name == 'budzet')",
        viewonly=True
    )
    
    # Versioned foreign key relationships
    czesc_budzetowa_kod_versions: Mapped[list["VersionedForeignKeyField"]] = relationship(
        primaryjoin="and_(PlanowanieBudzetu.id == foreign(VersionedForeignKeyField.entity_id), "
                   "VersionedForeignKeyField.entity_type == 'planowanie_budzetu', "
                   "VersionedForeignKeyField.field_name == 'czesc_budzetowa_kod')",
        viewonly=True
    )
    dzial_kod_versions: Mapped[list["VersionedForeignKeyField"]] = relationship(
        primaryjoin="and_(PlanowanieBudzetu.id == foreign(VersionedForeignKeyField.entity_id), "
                   "VersionedForeignKeyField.entity_type == 'planowanie_budzetu', "
                   "VersionedForeignKeyField.field_name == 'dzial_kod')",
        viewonly=True
    )
    rozdzial_kod_versions: Mapped[list["VersionedForeignKeyField"]] = relationship(
        primaryjoin="and_(PlanowanieBudzetu.id == foreign(VersionedForeignKeyField.entity_id), "
                   "VersionedForeignKeyField.entity_type == 'planowanie_budzetu', "
                   "VersionedForeignKeyField.field_name == 'rozdzial_kod')",
        viewonly=True
    )
    paragraf_kod_versions: Mapped[list["VersionedForeignKeyField"]] = relationship(
        primaryjoin="and_(PlanowanieBudzetu.id == foreign(VersionedForeignKeyField.entity_id), "
                   "VersionedForeignKeyField.entity_type == 'planowanie_budzetu', "
                   "VersionedForeignKeyField.field_name == 'paragraf_kod')",
        viewonly=True
    )
    zrodlo_finansowania_kod_versions: Mapped[list["VersionedForeignKeyField"]] = relationship(
        primaryjoin="and_(PlanowanieBudzetu.id == foreign(VersionedForeignKeyField.entity_id), "
                   "VersionedForeignKeyField.entity_type == 'planowanie_budzetu', "
                   "VersionedForeignKeyField.field_name == 'zrodlo_finansowania_kod')",
        viewonly=True
    )
    grupa_wydatkow_id_versions: Mapped[list["VersionedForeignKeyField"]] = relationship(
        primaryjoin="and_(PlanowanieBudzetu.id == foreign(VersionedForeignKeyField.entity_id), "
                   "VersionedForeignKeyField.entity_type == 'planowanie_budzetu', "
                   "VersionedForeignKeyField.field_name == 'grupa_wydatkow_id')",
        viewonly=True
    )
    komorka_organizacyjna_id_versions: Mapped[list["VersionedForeignKeyField"]] = relationship(
        primaryjoin="and_(PlanowanieBudzetu.id == foreign(VersionedForeignKeyField.entity_id), "
                   "VersionedForeignKeyField.entity_type == 'planowanie_budzetu', "
                   "VersionedForeignKeyField.field_name == 'komorka_organizacyjna_id')",
        viewonly=True
    )

    lata_budzetowe: Mapped[list["RokBudzetowy"]] = relationship(back_populates="planowanie_budzetu")

    def __repr__(self) -> str:
        return f"PlanowanieBudzetu(id={self.id!r})"
