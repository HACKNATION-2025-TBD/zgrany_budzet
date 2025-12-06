from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.schemas.czesci_budzetowe import CzescBudzetowa

from .base import Base


class PlanowanieBudzetu(Base):
    __tablename__ = "planowanie_budzetu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nazwa_projektu: Mapped[str | None] = mapped_column(String(500), nullable=True)
    nazwa_zadania: Mapped[str | None] = mapped_column(String(500), nullable=True)
    szczegolowe_uzasadnienie_realizacji: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    budzet: Mapped[str | None] = mapped_column(String(50), nullable=True)

    czesc_budzetowa_kod: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("czesci_budzetowe.kod"),
        nullable=False
    )
    dzial_kod: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("dzialy.kod"),
        nullable=False
    )
    rozdzial_kod: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rozdzialy.kod"),
        nullable=False
    )
    paragraf_kod: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("paragrafy.kod"),
        nullable=False
    )
    zrodlo_finansowania_kod: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("zrodla_finansowania.kod"),
        nullable=False
    )
    grupa_wydatkow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("grupy_wydatkow.id"),
        nullable=False
    )
    komorka_organizacyjna_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("komorki_organizacyjne.id"),
        nullable=False
    )

    czesc_budzetowa: Mapped["CzescBudzetowa"] = relationship()
    dzial: Mapped["Dzial"] = relationship()
    rozdzial: Mapped["Rozdzial"] = relationship()
    paragraf: Mapped["Paragraf"] = relationship()
    zrodlo_finansowania: Mapped["ZrodloFinansowania"] = relationship()
    grupa_wydatkow: Mapped["GrupaWydatkow"] = relationship()
    komorka_organizacyjna: Mapped["KomorkaOrganizacyjna"] = relationship()
    lata_budzetowe: Mapped[list["RokBudzetowy"]] = relationship(back_populates="planowanie_budzetu")

    def __repr__(self) -> str:
        return f"PlanowanieBudzetu(id={self.id!r}, nazwa_projektu={self.nazwa_projektu!r})"
