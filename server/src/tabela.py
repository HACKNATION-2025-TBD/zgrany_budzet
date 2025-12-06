from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from src.database import get_db
from src.schemas.planowanie_budzetu import PlanowanieBudzetu
from src.schemas.rok_budzetowy import RokBudzetowy
from src.schemas.versioned_fields import (
    VersionedStringField,
    VersionedNumericField,
    VersionedForeignKeyField
)

router = APIRouter()


# Pydantic models for requests
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


class RokBudzetowyCreate(BaseModel):
    planowanie_budzetu_id: int
    limit: float
    potrzeba: float


# Helper functions
def create_string_version(db: Session, entity_type: str, entity_id: int, field_name: str, value: Optional[str]):
    version = VersionedStringField(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        value=value
    )
    db.add(version)


def create_numeric_version(db: Session, entity_type: str, entity_id: int, field_name: str, value: float):
    version = VersionedNumericField(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        value=value
    )
    db.add(version)


def create_fk_version(db: Session, entity_type: str, entity_id: int, field_name: str, value_string: Optional[str] = None, value_int: Optional[int] = None):
    version = VersionedForeignKeyField(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        value_string=value_string,
        value_int=value_int
    )
    db.add(version)


def get_latest_version(versions: List):
    if not versions:
        return None
    return max(versions, key=lambda v: v.timestamp)


# PlanowanieBudzetu endpoints
@router.post("/planowanie_budzetu")
async def create_planowanie_budzetu(data: PlanowanieBudzetuCreate, db: Session = Depends(get_db)):
    # Create main record
    planowanie = PlanowanieBudzetu()
    db.add(planowanie)
    db.flush()
    
    # Create versioned fields
    create_string_version(db, "planowanie_budzetu", planowanie.id, "nazwa_projektu", data.nazwa_projektu)
    create_string_version(db, "planowanie_budzetu", planowanie.id, "nazwa_zadania", data.nazwa_zadania)
    create_string_version(db, "planowanie_budzetu", planowanie.id, "szczegolowe_uzasadnienie_realizacji", data.szczegolowe_uzasadnienie_realizacji)
    create_string_version(db, "planowanie_budzetu", planowanie.id, "budzet", data.budzet)
    
    create_fk_version(db, "planowanie_budzetu", planowanie.id, "czesc_budzetowa_kod", value_string=data.czesc_budzetowa_kod)
    create_fk_version(db, "planowanie_budzetu", planowanie.id, "dzial_kod", value_string=data.dzial_kod)
    create_fk_version(db, "planowanie_budzetu", planowanie.id, "rozdzial_kod", value_string=data.rozdzial_kod)
    create_fk_version(db, "planowanie_budzetu", planowanie.id, "paragraf_kod", value_string=data.paragraf_kod)
    create_fk_version(db, "planowanie_budzetu", planowanie.id, "zrodlo_finansowania_kod", value_string=data.zrodlo_finansowania_kod)
    create_fk_version(db, "planowanie_budzetu", planowanie.id, "grupa_wydatkow_id", value_int=data.grupa_wydatkow_id)
    create_fk_version(db, "planowanie_budzetu", planowanie.id, "komorka_organizacyjna_id", value_int=data.komorka_organizacyjna_id)
    
    db.commit()
    db.refresh(planowanie)
    
    return {"id": planowanie.id, "message": "Created successfully"}


@router.patch("/planowanie_budzetu/{planowanie_id}")
async def update_planowanie_budzetu_cell(planowanie_id: int, data: CellUpdate, db: Session = Depends(get_db)):
    planowanie = db.query(PlanowanieBudzetu).filter(PlanowanieBudzetu.id == planowanie_id).first()
    if not planowanie:
        raise HTTPException(status_code=404, detail="PlanowanieBudzetu not found")
    
    # String fields
    string_fields = ["nazwa_projektu", "nazwa_zadania", "szczegolowe_uzasadnienie_realizacji", "budzet"]
    # Foreign key string fields
    fk_string_fields = ["czesc_budzetowa_kod", "dzial_kod", "rozdzial_kod", "paragraf_kod", "zrodlo_finansowania_kod"]
    # Foreign key int fields
    fk_int_fields = ["grupa_wydatkow_id", "komorka_organizacyjna_id"]
    
    if data.field in string_fields:
        create_string_version(db, "planowanie_budzetu", planowanie_id, data.field, str(data.value) if data.value is not None else None)
    elif data.field in fk_string_fields:
        if data.value is None:
            raise HTTPException(status_code=400, detail=f"Field {data.field} cannot be null")
        create_fk_version(db, "planowanie_budzetu", planowanie_id, data.field, value_string=str(data.value))
    elif data.field in fk_int_fields:
        if data.value is None:
            raise HTTPException(status_code=400, detail=f"Field {data.field} cannot be null")
        create_fk_version(db, "planowanie_budzetu", planowanie_id, data.field, value_int=int(data.value))
    else:
        raise HTTPException(status_code=400, detail=f"Unknown field: {data.field}")
    
    db.commit()
    
    return {"id": planowanie_id, "field": data.field, "value": data.value, "message": "Updated successfully"}


@router.get("/planowanie_budzetu")
async def get_all_planowanie_budzetu(db: Session = Depends(get_db)):
    planowania = db.query(PlanowanieBudzetu).all()
    result = []
    
    for p in planowania:
        nazwa_projektu_ver = get_latest_version(p.nazwa_projektu_versions)
        nazwa_zadania_ver = get_latest_version(p.nazwa_zadania_versions)
        uzasadnienie_ver = get_latest_version(p.szczegolowe_uzasadnienie_realizacji_versions)
        budzet_ver = get_latest_version(p.budzet_versions)
        czesc_ver = get_latest_version(p.czesc_budzetowa_kod_versions)
        dzial_ver = get_latest_version(p.dzial_kod_versions)
        rozdzial_ver = get_latest_version(p.rozdzial_kod_versions)
        paragraf_ver = get_latest_version(p.paragraf_kod_versions)
        zrodlo_ver = get_latest_version(p.zrodlo_finansowania_kod_versions)
        grupa_ver = get_latest_version(p.grupa_wydatkow_id_versions)
        komorka_ver = get_latest_version(p.komorka_organizacyjna_id_versions)
        
        result.append({
            "id": p.id,
            "nazwa_projektu": nazwa_projektu_ver.value if nazwa_projektu_ver else None,
            "nazwa_zadania": nazwa_zadania_ver.value if nazwa_zadania_ver else None,
            "szczegolowe_uzasadnienie_realizacji": uzasadnienie_ver.value if uzasadnienie_ver else None,
            "budzet": budzet_ver.value if budzet_ver else None,
            "czesc_budzetowa_kod": czesc_ver.value_string if czesc_ver else None,
            "dzial_kod": dzial_ver.value_string if dzial_ver else None,
            "rozdzial_kod": rozdzial_ver.value_string if rozdzial_ver else None,
            "paragraf_kod": paragraf_ver.value_string if paragraf_ver else None,
            "zrodlo_finansowania_kod": zrodlo_ver.value_string if zrodlo_ver else None,
            "grupa_wydatkow_id": grupa_ver.value_int if grupa_ver else None,
            "komorka_organizacyjna_id": komorka_ver.value_int if komorka_ver else None
        })
    
    return result


@router.get("/planowanie_budzetu/{planowanie_id}")
async def get_planowanie_budzetu(planowanie_id: int, db: Session = Depends(get_db)):
    p = db.query(PlanowanieBudzetu).filter(PlanowanieBudzetu.id == planowanie_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="PlanowanieBudzetu not found")
    
    nazwa_projektu_ver = get_latest_version(p.nazwa_projektu_versions)
    nazwa_zadania_ver = get_latest_version(p.nazwa_zadania_versions)
    uzasadnienie_ver = get_latest_version(p.szczegolowe_uzasadnienie_realizacji_versions)
    budzet_ver = get_latest_version(p.budzet_versions)
    czesc_ver = get_latest_version(p.czesc_budzetowa_kod_versions)
    dzial_ver = get_latest_version(p.dzial_kod_versions)
    rozdzial_ver = get_latest_version(p.rozdzial_kod_versions)
    paragraf_ver = get_latest_version(p.paragraf_kod_versions)
    zrodlo_ver = get_latest_version(p.zrodlo_finansowania_kod_versions)
    grupa_ver = get_latest_version(p.grupa_wydatkow_id_versions)
    komorka_ver = get_latest_version(p.komorka_organizacyjna_id_versions)
    
    return {
        "id": p.id,
        "nazwa_projektu": nazwa_projektu_ver.value if nazwa_projektu_ver else None,
        "nazwa_zadania": nazwa_zadania_ver.value if nazwa_zadania_ver else None,
        "szczegolowe_uzasadnienie_realizacji": uzasadnienie_ver.value if uzasadnienie_ver else None,
        "budzet": budzet_ver.value if budzet_ver else None,
        "czesc_budzetowa_kod": czesc_ver.value_string if czesc_ver else None,
        "dzial_kod": dzial_ver.value_string if dzial_ver else None,
        "rozdzial_kod": rozdzial_ver.value_string if rozdzial_ver else None,
        "paragraf_kod": paragraf_ver.value_string if paragraf_ver else None,
        "zrodlo_finansowania_kod": zrodlo_ver.value_string if zrodlo_ver else None,
        "grupa_wydatkow_id": grupa_ver.value_int if grupa_ver else None,
        "komorka_organizacyjna_id": komorka_ver.value_int if komorka_ver else None
    }


@router.get("/planowanie_budzetu/{planowanie_id}/history")
async def get_planowanie_budzetu_history(planowanie_id: int, db: Session = Depends(get_db)):
    p = db.query(PlanowanieBudzetu).filter(PlanowanieBudzetu.id == planowanie_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="PlanowanieBudzetu not found")
    
    return {
        "id": p.id,
        "nazwa_projektu_history": [{"value": v.value, "timestamp": v.timestamp} for v in sorted(p.nazwa_projektu_versions, key=lambda x: x.timestamp, reverse=True)],
        "nazwa_zadania_history": [{"value": v.value, "timestamp": v.timestamp} for v in sorted(p.nazwa_zadania_versions, key=lambda x: x.timestamp, reverse=True)],
        "szczegolowe_uzasadnienie_realizacji_history": [{"value": v.value, "timestamp": v.timestamp} for v in sorted(p.szczegolowe_uzasadnienie_realizacji_versions, key=lambda x: x.timestamp, reverse=True)],
        "budzet_history": [{"value": v.value, "timestamp": v.timestamp} for v in sorted(p.budzet_versions, key=lambda x: x.timestamp, reverse=True)],
        "czesc_budzetowa_kod_history": [{"value": v.value_string, "timestamp": v.timestamp} for v in sorted(p.czesc_budzetowa_kod_versions, key=lambda x: x.timestamp, reverse=True)],
        "dzial_kod_history": [{"value": v.value_string, "timestamp": v.timestamp} for v in sorted(p.dzial_kod_versions, key=lambda x: x.timestamp, reverse=True)],
        "rozdzial_kod_history": [{"value": v.value_string, "timestamp": v.timestamp} for v in sorted(p.rozdzial_kod_versions, key=lambda x: x.timestamp, reverse=True)],
        "paragraf_kod_history": [{"value": v.value_string, "timestamp": v.timestamp} for v in sorted(p.paragraf_kod_versions, key=lambda x: x.timestamp, reverse=True)],
        "zrodlo_finansowania_kod_history": [{"value": v.value_string, "timestamp": v.timestamp} for v in sorted(p.zrodlo_finansowania_kod_versions, key=lambda x: x.timestamp, reverse=True)],
        "grupa_wydatkow_id_history": [{"value": v.value_int, "timestamp": v.timestamp} for v in sorted(p.grupa_wydatkow_id_versions, key=lambda x: x.timestamp, reverse=True)],
        "komorka_organizacyjna_id_history": [{"value": v.value_int, "timestamp": v.timestamp} for v in sorted(p.komorka_organizacyjna_id_versions, key=lambda x: x.timestamp, reverse=True)]
    }


# RokBudzetowy endpoints
@router.post("/rok_budzetowy")
async def create_rok_budzetowy(data: RokBudzetowyCreate, db: Session = Depends(get_db)):
    # Verify planowanie_budzetu exists
    planowanie = db.query(PlanowanieBudzetu).filter(PlanowanieBudzetu.id == data.planowanie_budzetu_id).first()
    if not planowanie:
        raise HTTPException(status_code=404, detail="PlanowanieBudzetu not found")
    
    # Create main record
    rok = RokBudzetowy(planowanie_budzetu_id=data.planowanie_budzetu_id)
    db.add(rok)
    db.flush()
    
    # Create versioned fields
    create_numeric_version(db, "rok_budzetowy", rok.id, "limit", data.limit)
    create_numeric_version(db, "rok_budzetowy", rok.id, "potrzeba", data.potrzeba)
    
    db.commit()
    db.refresh(rok)
    
    return {"id": rok.id, "message": "Created successfully"}


@router.patch("/rok_budzetowy/{rok_id}")
async def update_rok_budzetowy_cell(rok_id: int, data: CellUpdate, db: Session = Depends(get_db)):
    rok = db.query(RokBudzetowy).filter(RokBudzetowy.id == rok_id).first()
    if not rok:
        raise HTTPException(status_code=404, detail="RokBudzetowy not found")
    
    numeric_fields = ["limit", "potrzeba"]
    
    if data.field in numeric_fields:
        if data.value is None:
            raise HTTPException(status_code=400, detail=f"Field {data.field} cannot be null")
        create_numeric_version(db, "rok_budzetowy", rok_id, data.field, float(data.value))
    else:
        raise HTTPException(status_code=400, detail=f"Unknown field: {data.field}")
    
    db.commit()
    
    return {"id": rok_id, "field": data.field, "value": data.value, "message": "Updated successfully"}


@router.get("/rok_budzetowy")
async def get_all_rok_budzetowy(db: Session = Depends(get_db)):
    lata = db.query(RokBudzetowy).all()
    result = []
    
    for rok in lata:
        limit_ver = get_latest_version(rok.limit_versions)
        potrzeba_ver = get_latest_version(rok.potrzeba_versions)
        
        result.append({
            "id": rok.id,
            "planowanie_budzetu_id": rok.planowanie_budzetu_id,
            "limit": float(limit_ver.value) if limit_ver else None,
            "potrzeba": float(potrzeba_ver.value) if potrzeba_ver else None
        })
    
    return result


@router.get("/rok_budzetowy/{rok_id}")
async def get_rok_budzetowy(rok_id: int, db: Session = Depends(get_db)):
    rok = db.query(RokBudzetowy).filter(RokBudzetowy.id == rok_id).first()
    if not rok:
        raise HTTPException(status_code=404, detail="RokBudzetowy not found")
    
    limit_ver = get_latest_version(rok.limit_versions)
    potrzeba_ver = get_latest_version(rok.potrzeba_versions)
    
    return {
        "id": rok.id,
        "planowanie_budzetu_id": rok.planowanie_budzetu_id,
        "limit": float(limit_ver.value) if limit_ver else None,
        "potrzeba": float(potrzeba_ver.value) if potrzeba_ver else None
    }


@router.get("/rok_budzetowy/{rok_id}/history")
async def get_rok_budzetowy_history(rok_id: int, db: Session = Depends(get_db)):
    rok = db.query(RokBudzetowy).filter(RokBudzetowy.id == rok_id).first()
    if not rok:
        raise HTTPException(status_code=404, detail="RokBudzetowy not found")
    
    return {
        "id": rok.id,
        "planowanie_budzetu_id": rok.planowanie_budzetu_id,
        "limit_history": [{"value": float(v.value), "timestamp": v.timestamp} for v in sorted(rok.limit_versions, key=lambda x: x.timestamp, reverse=True)],
        "potrzeba_history": [{"value": float(v.value), "timestamp": v.timestamp} for v in sorted(rok.potrzeba_versions, key=lambda x: x.timestamp, reverse=True)]
    }
