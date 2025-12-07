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

#### GET `/api/planowanie_budzetu/{id}/field_history/{field_name}`
**NOWY ENDPOINT** - Zwraca historię zmian dla konkretnego pola.

Przykładowe wywołanie:
```
GET /api/planowanie_budzetu/1/field_history/nazwa_projektu
```

Odpowiedź:
```json
{
  "field_name": "nazwa_projektu",
  "history": [
    {
      "value": "Nowa nazwa projektu v3",
      "timestamp": "2024-01-15T16:00:00"
    },
    {
      "value": "Nowa nazwa projektu v2",
      "timestamp": "2024-01-15T14:30:00"
    },
    {
      "value": "Projekt testowy",
      "timestamp": "2024-01-15T10:00:00"
    }
  ]
}
```

**Obsługiwane pola dla planowanie_budzetu:**
- Pola tekstowe: `nazwa_projektu`, `nazwa_zadania`, `szczegolowe_uzasadnienie_realizacji`, `budzet`
- Klucze obce (string): `czesc_budzetowa_kod`, `dzial_kod`, `rozdzial_kod`, `paragraf_kod`, `zrodlo_finansowania_kod`
- Klucze obce (int): `grupa_wydatkow_id`, `komorka_organizacyjna_id`

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

**Uwaga:** Ten endpoint jest użyteczny gdy potrzebujesz historii wszystkich pól naraz, ale może być wolniejszy dla dużych zbiorów danych. Jeśli potrzebujesz historii tylko jednego pola, użyj `/field_history/{field_name}`.

#### GET `/api/rok_budzetowy`
Zwraca wszystkie lata budżetowe z najnowszymi wersjami pól.

#### GET `/api/rok_budzetowy/{id}`
Zwraca pojedynczy rok budżetowy z najnowszymi wersjami pól.

#### GET `/api/rok_budzetowy/{id}/field_history/{field_name}`
**NOWY ENDPOINT** - Zwraca historię zmian dla konkretnego pola numerycznego.

Przykładowe wywołanie:
```
GET /api/rok_budzetowy/1/field_history/limit
```

Odpowiedź:
```json
{
  "field_name": "limit",
  "history": [
    {
      "value": 80000.00,
      "timestamp": "2024-01-15T15:00:00"
    },
    {
      "value": 70000.00,
      "timestamp": "2024-01-15T13:00:00"
    },
    {
      "value": 50000.00,
      "timestamp": "2024-01-15T10:00:00"
    }
  ]
}
```

**Obsługiwane pola dla rok_budzetowy:**
- `limit`
- `potrzeba`

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
1. System query'uje bazę danych z `ORDER BY timestamp DESC LIMIT 1` dla każdego pola
2. Wybiera tylko najnowszą wersję bezpośrednio z SQL (bez ładowania wszystkich wersji)
3. Zwraca wartość z najnowszej wersji

**Optymalizacja:** System NIE ładuje wszystkich wersji do pamięci - query SQL pobiera tylko najnowszą wersję, co jest bardzo wydajne.

### 4. Odczyt Historii

**Endpoint pełnej historii (`/history`):**
1. System pobiera wszystkie wersje wszystkich pól dla danego wiersza
2. Sortuje je po timestamp (od najnowszych)
3. Zwraca listę zmian z timestampami dla każdego pola

**Endpoint historii pojedynczego pola (`/field_history/{field_name}`):**
1. System pobiera tylko wersje wybranego pola
2. Sortuje je po timestamp (od najnowszych)
3. Zwraca listę zmian z timestampami

**Zalecenie:** Używaj `/field_history/{field_name}` gdy potrzebujesz historii tylko jednego pola - jest szybsze i bardziej wydajne.

## Performance i Optymalizacje

### Indeksy Bazodanowe

Dla optymalnej wydajności, w tabelach wersjonowanych powinny być utworzone indeksy:

```sql
-- Dla versioned_string_fields
CREATE INDEX idx_versioned_string_lookup 
ON versioned_string_fields(entity_type, entity_id, field_name, timestamp DESC);

-- Dla versioned_numeric_fields
CREATE INDEX idx_versioned_numeric_lookup 
ON versioned_numeric_fields(entity_type, entity_id, field_name, timestamp DESC);

-- Dla versioned_foreign_key_fields
CREATE INDEX idx_versioned_fk_lookup 
ON versioned_foreign_key_fields(entity_type, entity_id, field_name, timestamp DESC);
```

### Query Optimization

System używa zoptymalizowanych query SQL:
- Zamiast pobierać wszystkie wersje i wybierać najnowszą w Pythonie
- Query SQL bezpośrednio pobiera tylko najnowszą wersję: `ORDER BY timestamp DESC LIMIT 1`
- Brak eager loadingu relacji - wszystkie wersje są query'owane on-demand

### Best Practices

1. **Dla UI tabeli/spreadsheet:** Używaj `GET /api/planowanie_budzetu` - pobiera wszystkie wiersze z aktualnymi wartościami
2. **Dla historii jednego pola:** Używaj `GET /api/.../field_history/{field_name}` - szybsze i bardziej wydajne
3. **Dla pełnego audytu:** Używaj `GET /api/.../history` - zwraca wszystkie zmiany wszystkich pól
4. **Dla edycji komórki:** Używaj `PATCH` - aktualizuje tylko jedno pole
