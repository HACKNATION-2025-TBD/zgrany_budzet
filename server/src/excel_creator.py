import openpyxl
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Callable, Any
import os


# --- 1. DATACLASSES (Bez zmian w strukturze danych) ---

@dataclass
class DaneFinansoweRoku:
    """
    Reprezentuje kolumny finansowe powtarzalne dla każdego roku (n, n+1...).
    """
    potrzeby: float = 0.0
    limit: float = 0.0
    niezabezpieczone: float = 0.0

    @property
    def bilans(self) -> float:
        return self.limit - self.potrzeby


@dataclass
class BudgetEntry:
    # --- Klasyfikacja ---
    czesc_budzetowa: str = ""
    dzial: str = ""
    rozdzial: str = ""
    paragraf: str = ""
    zrodlo_finansowania: str = ""
    grupa_wydatkow: str = ""

    # --- Opis Zadania i Organizacja ---
    bz_pelna_szczegolowosc: str = ""
    bz_kody: str = ""
    nazwa_programu_projektu: str = ""
    nazwa_komorki_org: str = ""
    plan_wi: str = ""
    dysponent_srodkow: str = ""
    budzet: str = ""

    nazwa_zadania: str = ""
    szczegolowe_uzasadnienie: str = ""
    obszar_dzialalnosci: str = ""

    # --- Finanse ---
    n: DaneFinansoweRoku = field(default_factory=DaneFinansoweRoku)
    n1: DaneFinansoweRoku = field(default_factory=DaneFinansoweRoku)
    n2: DaneFinansoweRoku = field(default_factory=DaneFinansoweRoku)
    n3: DaneFinansoweRoku = field(default_factory=DaneFinansoweRoku)

    # --- Umowy ---
    kwota_umowy_wniosku: float = 0.0
    nr_umowy_wniosku: Optional[str] = None
    dotacja_kontrahent: Optional[str] = None
    podstawa_prawna_dotacji: Optional[str] = None
    uwagi: Optional[str] = None


# --- 2. KONFIGURACJA EKSPORTU (NOWOŚĆ) ---

@dataclass
class ExportOptions:
    """
    Opcje sterujące tym, które kolumny trafią do Excela.
    """
    # Sekcje główne
    show_classification: bool = True  # Część, Dział, Rozdział...
    show_organization: bool = True  # BZ, Komórka, Dysponent...
    show_task_details: bool = True  # Nazwa, Uzasadnienie...

    # Lata budżetowe
    show_year_n: bool = True  # 2026
    show_year_n1: bool = True  # 2027
    show_year_n2: bool = True  # 2028
    show_year_n3: bool = True  # 2029

    # Inne
    show_contracts: bool = True  # Umowy, Dotacje, Uwagi


# --- 3. FUNKCJA EKSPORTUJĄCA DO EXCELA (ZMODYFIKOWANA) ---

def export_entries_to_excel(
        template_path: str,
        output_path: str,
        entries: List[BudgetEntry],
        options: ExportOptions = ExportOptions(),  # Domyślne opcje (wszystko włączone)
        start_row: int = 2
):
    """
    Dynamicznie wypełnia Excela, dobierając kolumny na podstawie flag w `options`.
    """

    # --- A. Budowanie mapy kolumn na podstawie opcji ---
    # Lista krotek: (Nagłówek Kolumny, Funkcja wyciągająca dane z obiektu)
    columns_map: List[Tuple[str, Callable[[BudgetEntry], Any]]] = []

    if options.show_classification:
        columns_map.extend([
            ("Część", lambda r: r.czesc_budzetowa),
            ("Dział", lambda r: r.dzial),
            ("Rozdział", lambda r: r.rozdzial),
            ("Paragraf", lambda r: r.paragraf),
            ("Źródło fin.", lambda r: r.zrodlo_finansowania),
            ("Grupa wydatków", lambda r: r.grupa_wydatkow),
        ])

    if options.show_organization:
        columns_map.extend([
            ("BZ (Pełny)", lambda r: r.bz_pelna_szczegolowosc),
            ("BZ (Kody)", lambda r: r.bz_kody),
            ("Program/Projekt", lambda r: r.nazwa_programu_projektu),
            ("Komórka Org.", lambda r: r.nazwa_komorki_org),
            ("Plan WI", lambda r: r.plan_wi),
            ("Dysponent", lambda r: r.dysponent_srodkow),
            ("Budżet", lambda r: r.budzet),
        ])

    if options.show_task_details:
        columns_map.extend([
            ("Nazwa Zadania", lambda r: r.nazwa_zadania),
            ("Uzasadnienie", lambda r: r.szczegolowe_uzasadnienie),
            ("Obszar działania", lambda r: r.obszar_dzialalnosci),
        ])

    # Helper do dodawania kolumn rocznych
    def add_year_cols(suffix: str, accessor: Callable[[BudgetEntry], DaneFinansoweRoku]):
        columns_map.extend([
            (f"Potrzeby ({suffix})", lambda r: accessor(r).potrzeby),
            (f"Limit ({suffix})", lambda r: accessor(r).limit),
            (f"Niezabezpieczone ({suffix})", lambda r: accessor(r).niezabezpieczone),
        ])

    if options.show_year_n: add_year_cols("N", lambda r: r.n)
    if options.show_year_n1: add_year_cols("N+1", lambda r: r.n1)
    if options.show_year_n2: add_year_cols("N+2", lambda r: r.n2)
    if options.show_year_n3: add_year_cols("N+3", lambda r: r.n3)

    if options.show_contracts:
        columns_map.extend([
            ("Kwota Umowy/Wniosku", lambda r: r.kwota_umowy_wniosku),
            ("Nr Umowy", lambda r: r.nr_umowy_wniosku),
            ("Kontrahent (Dotacja)", lambda r: r.dotacja_kontrahent),
            ("Podstawa Prawna", lambda r: r.podstawa_prawna_dotacji),
            ("Uwagi", lambda r: r.uwagi),
        ])

    # --- B. Obsługa szablonu (Template) ---
    if not os.path.exists(template_path):
        print(f"⚠️ Plik {template_path} nie istnieje. Tworzę nowy arkusz z nagłówkami.")
        wb = openpyxl.Workbook()
        ws = wb.active
        # Wpisujemy nagłówki dynamicznie
        headers = [col[0] for col in columns_map]
        ws.append(headers)
        start_row = 2
    else:
        print(f"📂 Ładowanie szablonu: {template_path}")
        wb = openpyxl.load_workbook(template_path)
        ws = wb.active

    # --- C. Zapis danych ---
    print(f"Zapisywanie {len(entries)} wierszy (wybrano {len(columns_map)} kolumn)...")

    current_row = start_row

    for entry in entries:
        # Iterujemy po zdefiniowanej mapie kolumn
        for col_idx, (header_name, data_getter) in enumerate(columns_map, start=1):
            value = data_getter(entry)
            ws.cell(row=current_row, column=col_idx, value=value)

        current_row += 1

    wb.save(output_path)
    print(f"✅ Gotowe! Plik zapisany jako: {output_path}")


# --- PRZYKŁAD UŻYCIA ---

if __name__ == "__main__":
    # 1. Dane testowe
    wpis_1 = BudgetEntry(
        czesc_budzetowa="27",
        dzial="750",
        nazwa_zadania="Zakup licencji",
        uwagi="Pilne",
        n=DaneFinansoweRoku(potrzeby=100.0, limit=80.0)
    )
    dane = [wpis_1]

    plik_szablonu = "template.xlsx"
    plik_wynikowy = "Raport_Dynamiczny.xlsx"

    # 2. Konfiguracja opcji (np. chcemy ukryć lata N+2 i N+3 oraz sekcję Organizacja)
    moje_opcje = ExportOptions(
        show_organization=False,  # Ukryj BZ, Komórkę itp.
        show_year_n2=False,  # Ukryj rok 2028
        show_year_n3=False  # Ukryj rok 2029
        # Reszta domyślnie True
    )

    # 3. Eksport
    export_entries_to_excel(plik_szablonu, plik_wynikowy, dane, options=moje_opcje)