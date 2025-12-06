# System Wersjonowania Pól - Dokumentacja

## Koncepcja

System działa jak tabela Excel, gdzie każda komórka (pole) może być edytowana niezależnie i każda zmiana jest zapisywana z timestampem. Dzięki temu mamy pełną historię zmian dla każdego pola.

## Architektura

### 1. Tabele Główne

#### `planowanie_budzetu`
- Zawiera tylko `id` (primary key)
- Wszystkie pozostałe dane są przechowywane w tabelach wersjonowanych

#### `rok_budzetowy`
- Zawiera tylko `id` i `planowanie_budzetu_id` (foreign key)
- Pola `limit` i `potrzeba` są wersjonowane

### 2. Tabele Wersjonowane

#### `versioned_string_fields`
Przechowuje wersje pól tekstowych:
- `id` - klucz główny
- `entity_type` - typ encji (`'planowanie_budzetu'`, `'rok_budzetowy'`)
- `entity_id` - id wiersza w tabeli głównej
- `field_name` - nazwa pola (np. `'nazwa_projektu'`)
- `value` - wartość tekstowa (nullable, do 2000 znaków)
- `timestamp` - czas utworzenia wersji

#### `versioned_numeric_fields`
Przechowuje wersje pól numerycznych:
- `id` - klucz główny
- `entity_type` - typ encji
- `entity_id` - id wiersza w tabeli głównej
- `field_name` - nazwa pola (np. `'limit'`, `'potrzeba'`)
- `value` - wartość numeryczna (Numeric(15, 2))
- `timestamp` - czas utworzenia wersji

#### `versioned_foreign_key_fields`
Przechowuje wersje pól będących kluczami obcymi:
- `id` - klucz główny
- `entity_type` - typ encji
- `entity_id` - id wiersza w tabeli głównej
- `field_name` - nazwa pola (np. `'dzial_kod'`)
- `value_string` - wartość dla kluczy typu string (np. kod)
- `value_int` - wartość dla kluczy typu integer (np. id)
- `timestamp` - czas utworzenia wersji

## Pola Wersjonowane

### PlanowanieBudzetu

**Pola tekstowe (string):**
- `nazwa_projektu`
- `nazwa_zadania`
- `szczegolowe_uzasadnienie_realizacji`
- `budzet`

**Klucze obce (string - kod):**
- `czesc_budzetowa_kod`
- `dzial_kod`
- `rozdzial_kod`
- `paragraf_kod`
- `zrodlo_finansowania_kod`

**Klucze obce (integer - id):**
- `grupa_wydatkow_id`
- `komorka_organizacyjna_id`

### RokBudzetowy

**Pola numeryczne:**
- `limit`
- `potrzeba`

## API Endpoints

### Tworzenie Nowego Wiersza

#### POST `/api/planowanie_budzetu`
```json
{
  "nazwa_projektu": "Projekt testowy",
  "nazwa_zadania": "Zadanie 1",
  "szczegolowe_uzasadnienie_realizacji": "Uzasadnienie...",
  "budzet": "2024",
  "czesc_budzetowa_kod": "75",
  "dzial_kod": "750",
  "rozdzial_kod": "75011",
  "paragraf_kod": "4210",
  "zrodlo_finansowania_kod": "1",
  "grupa_wydatkow_id": 1,
  "komorka_organizacyjna_id": 1
}
```

#### POST `/api/rok_budzetowy`
```json
{
  "planowanie_budzetu_id": 1,
  "limit": 50000.00,
  "potrzeba": 75000.00
}
```

### Aktualizacja Pojedynczej Komórki

#### PATCH `/api/planowanie_budzetu/{id}`
```json
{
  "field": "nazwa_projektu",
  "value": "Nowa nazwa projektu"
}
```

Przykłady dla różnych typów pól:

**Pole tekstowe:**
```json
{
  "field": "nazwa_zadania",
  "value": "Zaktualizowane zadanie"
}
```

**Pole tekstowe nullable:**
```json
{
  "field": "szczegolowe_uzasadnienie_realizacji",
  "value": null
}
```

**Klucz obcy (string):**
```json
{
  "field": "dzial_kod",
  "value": "801"
}
```

**Klucz obcy (integer):**
```json
{
  "field": "grupa_wydatkow_id",
  "value": 5
}
```

#### PATCH `/api/rok_budzetowy/{id}`
```json
{
  "field": "limit",
  "value": 60000.00
}
```

### Odczyt Danych

#### GET `/api/planowanie_budzetu`
Zwraca wszystkie wiersze z najnowszymi wersjami wszystkich pól.

```json
[
  {
    "id": 1,
    "nazwa_projektu": "Projekt testowy",
    "nazwa_zadania": "Zadanie 1",
    "szczegolowe_uzasadnienie_realizacji": "Uzasadnienie...",
    "budzet": "2024",
    "czesc_budzetowa_kod": "75",
    "dzial_kod": "750",
    "rozdzial_kod": "75011",
    "paragraf_kod": "4210",
    "zrodlo_finansowania_kod": "1",
    "grupa_wydatkow_id": 1,
    "komorka_organizacyjna_id": 1
  }
]
```

#### GET `/api/planowanie_budzetu/{id}`
Zwraca pojedynczy wiersz z najnowszymi wersjami wszystkich pól.

#### GET `/api/planowanie_budzetu/{id}/history`
Zwraca pełną historię zmian dla wszystkich pól danego wiersza.

```json
{
  "id": 1,
  "nazwa_projektu_history": [
    {
      "value": "Nowa nazwa projektu",
      "timestamp": "2024-01-15T14:30:00"
    },
    {
      "value": "Projekt testowy",
      "timestamp": "2024-01-15T10:00:00"
    }
  ],
  "dzial_kod_history": [
    {
      "value": "801",
      "timestamp": "2024-01-15T12:00:00"
    },
    {
      "value": "750",
      "timestamp": "2024-01-15T10:00:00"
    }
  ]
  // ... pozostałe pola
}
```

#### GET `/api/rok_budzetowy`
Zwraca wszystkie lata budżetowe z najnowszymi wersjami pól.

#### GET `/api/rok_budzetowy/{id}`
Zwraca pojedynczy rok budżetowy z najnowszymi wersjami pól.

#### GET `/api/rok_budzetowy/{id}/history`
Zwraca historię zmian dla pól `limit` i `potrzeba`.

## Jak Działa System

### 1. Tworzenie Nowego Wiersza

Gdy tworzysz nowy wiersz:
1. Tworzy się rekord w tabeli głównej (tylko z `id`)
2. Dla każdego pola tworzy się pierwszy wpis w odpowiedniej tabeli wersjonowanej
3. Wszystkie wpisy dostają ten sam timestamp (czas utworzenia)

### 2. Aktualizacja Komórki

Gdy aktualizujesz pojedynczą komórkę:
1. System identyfikuje typ pola (string, numeric, foreign key)
2. Tworzy nowy wpis w odpowiedniej tabeli wersjonowanej
3. Nowy wpis dostaje aktualny timestamp
4. Poprzednie wersje pozostają w bazie niezmienione

### 3. Odczyt Aktualnych Danych

Gdy pobierasz dane:
1. System dla każdego pola pobiera wszystkie wersje
2. Wybiera wersję z najnowszym timestampem
3. Zwraca wartość z tej wersji

### 4. Odczyt Historii

Gdy pobierasz historię:
1. System pobiera wszystkie wersje wszystkich pól
2. Sortuje je po timestamp (od najnowszych)
3. Zwraca listę zmian z timestampami

## Uwagi Techniczne

- Timestamp jest generowany automatycznie przez bazę danych (`datetime.utcnow`)
- Relationships w SQLAlchemy są `viewonly=True` (tylko do odczytu)
- Wartości nullable są obsługiwane dla pól tekstowych
- Klucze obce nie mogą być null (walidacja w endpointach)
- Numeric fields używają typu `Numeric(15, 2)` dla precyzji
- Baza danych nigdy nie usuwa starych wersji - pełny audit trail

## Testowanie

### Uruchamianie Testów

Testy są napisane przy użyciu pytest i requests, testują rzeczywiste endpointy API:

```bash
# Uruchom wszystkie testy
pytest

# Uruchom testy z verbose output
pytest -v

# Uruchom konkretny plik testów
pytest tests/test_tabela.py

# Uruchom konkretny test
pytest tests/test_tabela.py::TestPlanowanieBudzetuEndpoints::test_create_planowanie_budzetu
```

### Konfiguracja Testów

Przed uruchomieniem testów:

1. Utwórz testową bazę danych
2. Ustaw zmienną środowiskową `DATABASE_URL` w `tests/conftest.py`
3. Upewnij się, że serwer może się uruchomić na porcie 8000

### Co Jest Testowane

**PlanowanieBudzetu:**
- ✓ Tworzenie nowego rekordu
- ✓ Aktualizacja pól tekstowych
- ✓ Aktualizacja kluczy obcych (string i integer)
- ✓ Ustawianie wartości nullable na null
- ✓ Pobieranie wszystkich rekordów
- ✓ Pobieranie pojedynczego rekordu
- ✓ Pobieranie historii zmian
- ✓ Obsługa błędów (nieznane pole, nieistniejący rekord)

**RokBudzetowy:**
- ✓ Tworzenie nowego rekordu
- ✓ Aktualizacja pól numerycznych
- ✓ Pobieranie historii zmian
- ✓ Walidacja foreign key

### Przykład Testu

```python
def test_update_string_field(self, db_session, cleanup_db):
    # Create record
    create_response = requests.post(f"{BASE_URL}/planowanie_budzetu", json=payload)
    planowanie_id = create_response.json()["id"]

    # Update field
    update_payload = {"field": "nazwa_projektu", "value": "Updated Name"}
    requests.patch(f"{BASE_URL}/planowanie_budzetu/{planowanie_id}", json=update_payload)

    # Verify in database
    versions = db_session.query(VersionedStringField).filter_by(
        entity_id=planowanie_id,
        field_name="nazwa_projektu"
    ).order_by(VersionedStringField.timestamp).all()
    
    assert len(versions) == 2
    assert versions[1].value == "Updated Name"
```