from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


# Request models
class PlanowanieBudzetuCreate(BaseModel):
    nazwa_projektu: Optional[str] = None
    nazwa_zadania: Optional[str] = None
    szczegolowe_uzasadnienie_realizacji: Optional[str] = None
    budzet: Optional[str] = None
    czesc_budzetowa_kod: str
    dzial_kod: str
    rozdzial_kod: str
    paragraf_kod: str
    zrodlo_finansowania_kod: str
    grupa_wydatkow_id: int
    komorka_organizacyjna_id: int


class CellUpdate(BaseModel):
    field: str
    value: Optional[str | int | float] = None
    # If you want to check for merge conflict, pass here the last time you have pulled the information
    last_known_timestamp: Optional[datetime] = None


class RokBudzetowyCreate(BaseModel):
    planowanie_budzetu_id: int
    limit: float
    potrzeba: float


# Base response models
class MessageResponse(BaseModel):
    id: int
    message: str


class UpdateResponse(BaseModel):
    id: int
    field: str
    value: Optional[str | int | float]
    message: str


# PlanowanieBudzetu response models
class PlanowanieBudzetuResponse(BaseModel):
    id: int
    nazwa_projektu: Optional[str] = None
    nazwa_zadania: Optional[str] = None
    szczegolowe_uzasadnienie_realizacji: Optional[str] = None
    budzet: Optional[str] = None
    czesc_budzetowa_kod: Optional[str] = None
    dzial_kod: Optional[str] = None
    rozdzial_kod: Optional[str] = None
    paragraf_kod: Optional[str] = None
    zrodlo_finansowania_kod: Optional[str] = None
    grupa_wydatkow_id: Optional[int] = None
    komorka_organizacyjna_id: Optional[int] = None


class FieldHistoryEntry(BaseModel):
    value: Optional[str | int | float]
    timestamp: datetime


class FieldHistoryResponse(BaseModel):
    field_name: str
    history: List[FieldHistoryEntry]


class FieldsHistoryStatusResponse(BaseModel):
    """Response showing which fields have history (more than 1 version)"""
    fields: Dict[str, bool]


# RokBudzetowy response models
class RokBudzetowyResponse(BaseModel):
    id: int
    planowanie_budzetu_id: int
    limit: Optional[float] = None
    potrzeba: Optional[float] = None
