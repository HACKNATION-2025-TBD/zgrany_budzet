"""
Skrypt do ładowania danych z plików JSON (fixtures) do bazy danych.

Skrypt automatycznie tworzy tabele w bazie danych i wczytuje dane z plików JSON
znajdujących się w katalogu fixtures/.

Użycie:
-------
1. Załadowanie fixtures bez usuwania istniejących danych:
   ```bash
   python src/load_fixtures.py
   ```

2. Załadowanie fixtures z uprzednim usunięciem wszystkich tabel:
   ```bash
   python src/load_fixtures.py --drop
   ```

3. Programowe użycie w kodzie Python:
   ```python
   from load_fixtures import load_all_fixtures
   
   # Załaduj fixtures
   load_all_fixtures()
   
   # Lub z uprzednim usunięciem tabel
   load_all_fixtures(drop_existing=True)
   ```

Struktura danych:
-----------------
- czesci_budzetowe.json - Części budżetowe (kod jako PK)
- dzialy.json - Działy budżetowe (kod jako PK)
- rozdzialy.json - Rozdziały budżetowe (kod jako PK)
- paragrafy.json - Paragrafy budżetowe (kod jako PK)
- zrodla_finansowania.json - Źródła finansowania (kod jako PK)
- grupy_wydatkow.json - Grupy wydatków (id jako PK)
- komorki_organizacyjne.json - Komórki organizacyjne (id jako PK)
- users.json - Użytkownicy (id jako PK)

Wymagania:
----------
- Poprawnie skonfigurowane połączenie z bazą danych w pliku database.py
- Pliki JSON z fixtures w katalogu src/fixtures/
- Zainstalowane zależności: sqlalchemy, psycopg2 (lub psycopg2-binary)

Uwagi:
------
- Użycie flagi --drop spowoduje USUNIĘCIE wszystkich tabel z bazy danych
- Dane są ładowane w określonej kolejności, aby zachować spójność
- W przypadku błędu transakcja jest wycofywana (rollback)
"""
import json
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from src.database import engine, SessionLocal
from src.schemas.base import Base
from src.schemas.czesci_budzetowe import CzescBudzetowa
from src.schemas.dzialy import Dzial
from src.schemas.rozdzialy import Rozdzial
from src.schemas.paragrafy import Paragraf
from src.schemas.zrodla_finansowania import ZrodloFinansowania
from src.schemas.grupy_wydatkow import GrupaWydatkow
from src.schemas.planowanie_budzetu import PlanowanieBudzetu
from src.schemas.rok_budzetowy import RokBudzetowy
from src.schemas.komorki_organizacyjne import KomorkaOrganizacyjna
from src.schemas.users import User
from src.versioning_utils import (
    create_string_version,
    create_numeric_version,
    create_fk_version
)


def load_json_fixture(filename: str) -> list[dict]:
    """Load JSON fixture from fixtures directory."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    filepath = fixtures_dir / filename
    
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_czesci_budzetowe(session: Session) -> None:
    """Load części budżetowe fixtures."""
    print("Loading części budżetowe...")
    data = load_json_fixture("czesci_budzetowe.json")
    
    for item in data:
        obj = CzescBudzetowa(**item)
        session.add(obj)
    
    session.commit()
    print(f"Loaded {len(data)} części budżetowe")


def load_dzialy(session: Session) -> None:
    """Load działy fixtures."""
    print("Loading działy...")
    data = load_json_fixture("dzialy.json")
    
    for item in data:
        obj = Dzial(**item)
        session.add(obj)
    
    session.commit()
    print(f"Loaded {len(data)} działy")


def load_rozdzialy(session: Session) -> None:
    """Load rozdziały fixtures."""
    print("Loading rozdziały...")
    data = load_json_fixture("rozdzialy.json")
    
    for item in data:
        obj = Rozdzial(**item)
        session.add(obj)
    
    session.commit()
    print(f"Loaded {len(data)} rozdziały")


def load_paragrafy(session: Session) -> None:
    """Load paragrafy fixtures."""
    print("Loading paragrafy...")
    data = load_json_fixture("paragrafy.json")
    
    for item in data:
        obj = Paragraf(**item)
        session.add(obj)
    
    session.commit()
    print(f"Loaded {len(data)} paragrafy")


def load_zrodla_finansowania(session: Session) -> None:
    """Load źródła finansowania fixtures."""
    print("Loading źródła finansowania...")
    data = load_json_fixture("zrodla_finansowania.json")
    
    for item in data:
        obj = ZrodloFinansowania(**item)
        session.add(obj)
    
    session.commit()
    print(f"Loaded {len(data)} źródła finansowania")


def load_grupy_wydatkow(session: Session) -> None:
    """Load grupy wydatków fixtures."""
    print("Loading grupy wydatków...")
    data = load_json_fixture("grupy_wydatkow.json")
    
    for item in data:
        obj = GrupaWydatkow(**item)
        session.add(obj)
    
    session.commit()
    print(f"Loaded {len(data)} grupy wydatków")


def load_komorki_organizacyjne(session: Session) -> None:
    """Load komórki organizacyjne fixtures."""
    print("Loading komórki organizacyjne...")
    data = load_json_fixture("komorki_organizacyjne.json")
    
    for item in data:
        obj = KomorkaOrganizacyjna(**item)
        session.add(obj)
    
    session.commit()
    print(f"Loaded {len(data)} komórki organizacyjne")


def load_users(session: Session) -> None:
    """Load users fixtures."""
    print("Loading users...")
    data = load_json_fixture("users.json")
    
    for item in data:
        obj = User(**item)
        session.add(obj)
    
    session.commit()
    print(f"Loaded {len(data)} users")


def load_planowanie_budzetu(session: Session) -> None:
    """Load planowanie budżetu fixtures with versioned fields."""
    print("Loading planowanie budżetu...")
    data = load_json_fixture("planowanie_budzetu.json")
    
    for item in data:
        # Extract lata_budzetowe and user_id before creating main record
        lata_budzetowe = item.pop("lata_budzetowe", [])
        user_id = item.get("user_id")
        
        # Create main PlanowanieBudzetu record (empty)
        planowanie = PlanowanieBudzetu()
        session.add(planowanie)
        session.flush()  # Get the ID
        
        # Create versioned fields for planowanie_budzetu
        create_string_version(session, "planowanie_budzetu", planowanie.id, "nazwa_projektu", item.get("nazwa_projektu"), user_id)
        create_string_version(session, "planowanie_budzetu", planowanie.id, "nazwa_zadania", item.get("nazwa_zadania"), user_id)
        create_string_version(session, "planowanie_budzetu", planowanie.id, "szczegolowe_uzasadnienie_realizacji", item.get("szczegolowe_uzasadnienie_realizacji"), user_id)
        create_string_version(session, "planowanie_budzetu", planowanie.id, "budzet", item.get("budzet"), user_id)
        
        create_fk_version(session, "planowanie_budzetu", planowanie.id, "czesc_budzetowa_kod", value_string=item.get("czesc_budzetowa_kod"), user_id=user_id)
        create_fk_version(session, "planowanie_budzetu", planowanie.id, "dzial_kod", value_string=item.get("dzial_kod"), user_id=user_id)
        create_fk_version(session, "planowanie_budzetu", planowanie.id, "rozdzial_kod", value_string=item.get("rozdzial_kod"), user_id=user_id)
        create_fk_version(session, "planowanie_budzetu", planowanie.id, "paragraf_kod", value_string=item.get("paragraf_kod"), user_id=user_id)
        create_fk_version(session, "planowanie_budzetu", planowanie.id, "zrodlo_finansowania_kod", value_string=item.get("zrodlo_finansowania_kod"), user_id=user_id)
        create_fk_version(session, "planowanie_budzetu", planowanie.id, "grupa_wydatkow_id", value_int=item.get("grupa_wydatkow_id"), user_id=user_id)
        create_fk_version(session, "planowanie_budzetu", planowanie.id, "komorka_organizacyjna_id", value_int=item.get("komorka_organizacyjna_id"), user_id=user_id)
        create_fk_version(session, "planowanie_budzetu", planowanie.id, "user_id", value_int=user_id, user_id=user_id)
        
        # Create RokBudzetowy records with versioned fields
        for rok_data in lata_budzetowe:
            rok = RokBudzetowy(
                planowanie_budzetu_id=planowanie.id,
                rok=rok_data["rok"]
            )
            session.add(rok)
            session.flush()  # Get the ID
            
            create_numeric_version(session, "rok_budzetowy", rok.id, "limit", rok_data.get("limit"), user_id)
            create_numeric_version(session, "rok_budzetowy", rok.id, "potrzeba", rok_data.get("potrzeba"), user_id)
    
    session.commit()
    print(f"Loaded {len(data)} planowanie budżetu records")


def create_tables() -> None:
    """Create all tables in the database."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")


def drop_tables() -> None:
    """Drop all tables from the database."""
    print("Dropping tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped successfully")


def load_all_fixtures(drop_existing: bool = False, postgres_url: str = None) -> None:
    """
    Load all fixtures into the database.
    
    Parameters
    ----------
    drop_existing : bool, optional
        If True, drops all existing tables before creating new ones and loading data.
        Use with caution as this will DELETE all data from the database.
        Default is False.
    postgres_url : str, optional
        PostgreSQL connection URL. If provided, overrides the default database connection.
        Format: postgresql://user:password@host:port/database
        Default is None (uses connection from database.py).
    
    Raises
    ------
    Exception
        If any error occurs during loading, the transaction is rolled back
        and the exception is re-raised.
    
    Examples
    --------
    >>> load_all_fixtures()  # Load fixtures without dropping tables
    >>> load_all_fixtures(drop_existing=True)  # Drop tables first, then load
    >>> load_all_fixtures(postgres_url="postgresql://user:pass@localhost/db")  # Custom DB
    """
    # Use custom database URL if provided
    if postgres_url:
        custom_engine = create_engine(postgres_url)
        from sqlalchemy.orm import sessionmaker
        CustomSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=custom_engine)
        
        if drop_existing:
            print(f"Using custom database: {postgres_url.split('@')[1] if '@' in postgres_url else postgres_url}")
            Base.metadata.drop_all(bind=custom_engine)
            print("Tables dropped successfully")
        
        print("Creating tables...")
        Base.metadata.create_all(bind=custom_engine)
        print("Tables created successfully")
        
        session = CustomSessionLocal()
    else:
        if drop_existing:
            drop_tables()
        
        create_tables()
        session = SessionLocal()
    
    try:
        load_czesci_budzetowe(session)
        load_dzialy(session)
        load_rozdzialy(session)
        load_paragrafy(session)
        load_zrodla_finansowania(session)
        load_grupy_wydatkow(session)
        load_komorki_organizacyjne(session)
        load_users(session)
        load_planowanie_budzetu(session)
        
        print("\n✅ All fixtures loaded successfully!")
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error loading fixtures: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load database fixtures")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing tables before loading fixtures"
    )
    parser.add_argument(
        "--postgres-url",
        type=str,
        help="PostgreSQL connection URL (e.g., postgresql://user:password@localhost:5432/dbname)"
    )
    
    args = parser.parse_args()
    load_all_fixtures(drop_existing=args.drop, postgres_url=args.postgres_url)
