from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from docxtpl import DocxTemplate


@dataclass
class DocumentRecipient:
    """Reprezentuje dane odbiorcy pisma."""
    title: str
    name: str
    role: str


@dataclass
class DocumentMetadata:
    """
    Reprezentuje metadane nagłówka i daty.
    Pola r1-r4 tutaj oznaczają etykiety lat (np. '2026').
    """
    r1: str
    r2: str
    r3: str
    r4: str
    EZD_Nr: str
    Data: str
    recipient: DocumentRecipient


@dataclass
class DocumentRow:
    """
    Reprezentuje jeden wiersz danych finansowych.
    Pola r1-r4 tutaj oznaczają wartości liczbowe (kwoty).
    """
    czesc: str
    dzial: str
    rozdzial: str
    grupa: str
    r1: float
    r2: float
    r3: float
    r4: float


@dataclass
class DocumentData:
    """Główna klasa spinająca metadane i rekordy."""
    metadata: DocumentMetadata
    records: List[DocumentRow]

    @property
    def sums(self) -> Dict[str, float]:
        """Oblicza sumy kolumn dynamicznie."""
        return {
            'suma_r1': sum(r.r1 for r in self.records),
            'suma_r2': sum(r.r2 for r in self.records),
            'suma_r3': sum(r.r3 for r in self.records),
            'suma_r4': sum(r.r4 for r in self.records),
        }

    def get_context(self) -> Dict[str, Any]:
        """
        Przygotowuje pełny słownik kontekstowy dla silnika Jinja2.
        Spłaszcza struktury zagnieżdżone dla łatwiejszego dostępu w Wordzie.
        """
        # 1. Pobierz podstawowe metadane jako słownik
        context = asdict(self.metadata)

        recipient_data = context.pop('recipient', {})

        # 3. Mapowanie nazw kluczy na te oczekiwane przez szablon Worda (zgodnie z Twoim przykładem)
        final_context = {
            # Pola z DocumentMetadata (r1..r4 lata, ezd_nr, date)
            **context,

            # Pola z DocumentRecipient (spłaszczone)
            "Title": self.metadata.recipient.title,
            "Name": self.metadata.recipient.name,
            "Role": self.metadata.recipient.role,

            # Pola wyliczeniowe i lista
            "rows": [asdict(r) for r in self.records],
            **self.sums,  # Rozpakowuje słownik sum (dodaje klucze suma_r1, suma_r2...)
            "DK": "DK"
        }
        return final_context


def generate_docx(input_path: str, output_path: str, document: DocumentData):
    """Generuje plik Word na podstawie szablonu i obiektu danych."""
    template_file = Path(input_path)

    if not template_file.exists():
        raise FileNotFoundError(f"Błąd: Nie znaleziono pliku szablonu: {template_file.absolute()}")

    doc = DocxTemplate(template_file)

    context = document.get_context()

    doc.render(context)
    doc.save(output_path)


# if __name__ == "__main__":
#     recipient = DocumentRecipient(
#         title="Pan",
#         name="Jan Nowak",
#         role="Dyrektor Działu XYZ"
#     )
#
#     metadata = DocumentMetadata(
#         r1="2026", r2="2027", r3="2028", r4="2029",
#         ezd_nr="1/1/1/1/ezd",
#         date="01.01.2026 r.",
#         recipient=recipient
#     )
#
#     rows = [
#         DocumentRow("200", "2001", "21", "Dotacje celowe", 90.0, 90.0, 90.0, 90.0),
#         DocumentRow("200", "2001", "21", "Wydatki bieżące", 50.0, 50.0, 50.0, 50.0),
#     ]
#
#     doc_data = DocumentData(metadata, rows)
#
#     try:
#         generate_docx("zal.docx", "Wypelniony_Dokument.docx", doc_data)
#     except FileNotFoundError as e:
#         print(e)
