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


def get_latest_version_for_field(db: Session, entity_type: str, entity_id: int, field_name: str, field_type: str):
    """Get latest version for a specific field - optimized to query only latest"""
    if field_type == "string":
        version = db.query(VersionedStringField).filter(
            VersionedStringField.entity_type == entity_type,
            VersionedStringField.entity_id == entity_id,
            VersionedStringField.field_name == field_name
        ).order_by(desc(VersionedStringField.timestamp)).first()
        return version.value if version else None
    elif field_type == "numeric":
        version = db.query(VersionedNumericField).filter(
            VersionedNumericField.entity_type == entity_type,
            VersionedNumericField.entity_id == entity_id,
            VersionedNumericField.field_name == field_name
        ).order_by(desc(VersionedNumericField.timestamp)).first()
        return float(version.value) if version else None
    elif field_type == "fk_string":
        version = db.query(VersionedForeignKeyField).filter(
            VersionedForeignKeyField.entity_type == entity_type,
            VersionedForeignKeyField.entity_id == entity_id,
            VersionedForeignKeyField.field_name == field_name
        ).order_by(desc(VersionedForeignKeyField.timestamp)).first()
        return version.value_string if version else None
    elif field_type == "fk_int":
        version = db.query(VersionedForeignKeyField).filter(
            VersionedForeignKeyField.entity_type == entity_type,
            VersionedForeignKeyField.entity_id == entity_id,
            VersionedForeignKeyField.field_name == field_name
        ).order_by(desc(VersionedForeignKeyField.timestamp)).first()
        return version.value_int if version else None
    return None


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
        result.append({
            "id": p.id,
            "nazwa_projektu": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "nazwa_projektu", "string"),
            "nazwa_zadania": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "nazwa_zadania", "string"),
            "szczegolowe_uzasadnienie_realizacji": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "szczegolowe_uzasadnienie_realizacji", "string"),
            "budzet": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "budzet", "string"),
            "czesc_budzetowa_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "czesc_budzetowa_kod", "fk_string"),
            "dzial_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "dzial_kod", "fk_string"),
            "rozdzial_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "rozdzial_kod", "fk_string"),
            "paragraf_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "paragraf_kod", "fk_string"),
            "zrodlo_finansowania_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "zrodlo_finansowania_kod", "fk_string"),
            "grupa_wydatkow_id": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "grupa_wydatkow_id", "fk_int"),
            "komorka_organizacyjna_id": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "komorka_organizacyjna_id", "fk_int")
        })
    
    return result


@router.get("/planowanie_budzetu/{planowanie_id}")
async def get_planowanie_budzetu(planowanie_id: int, db: Session = Depends(get_db)):
    p = db.query(PlanowanieBudzetu).filter(PlanowanieBudzetu.id == planowanie_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="PlanowanieBudzetu not found")
    
    return {
        "id": p.id,
        "nazwa_projektu": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "nazwa_projektu", "string"),
        "nazwa_zadania": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "nazwa_zadania", "string"),
        "szczegolowe_uzasadnienie_realizacji": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "szczegolowe_uzasadnienie_realizacji", "string"),
        "budzet": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "budzet", "string"),
        "czesc_budzetowa_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "czesc_budzetowa_kod", "fk_string"),
        "dzial_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "dzial_kod", "fk_string"),
        "rozdzial_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "rozdzial_kod", "fk_string"),
        "paragraf_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "paragraf_kod", "fk_string"),
        "zrodlo_finansowania_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "zrodlo_finansowania_kod", "fk_string"),
        "grupa_wydatkow_id": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "grupa_wydatkow_id", "fk_int"),
        "komorka_organizacyjna_id": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "komorka_organizacyjna_id", "fk_int")
    }


@router.get("/planowanie_budzetu/{planowanie_id}/field_history/{field_name}")
async def get_planowanie_budzetu_field_history(planowanie_id: int, field_name: str, db: Session = Depends(get_db)):
    p = db.query(PlanowanieBudzetu).filter(PlanowanieBudzetu.id == planowanie_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="PlanowanieBudzetu not found")
    
    string_fields = ["nazwa_projektu", "nazwa_zadania", "szczegolowe_uzasadnienie_realizacji", "budzet"]
    fk_string_fields = ["czesc_budzetowa_kod", "dzial_kod", "rozdzial_kod", "paragraf_kod", "zrodlo_finansowania_kod"]
    fk_int_fields = ["grupa_wydatkow_id", "komorka_organizacyjna_id"]
    
    if field_name in string_fields:
        versions = db.query(VersionedStringField).filter(
            VersionedStringField.entity_type == "planowanie_budzetu",
            VersionedStringField.entity_id == planowanie_id,
            VersionedStringField.field_name == field_name
        ).order_by(desc(VersionedStringField.timestamp)).all()
        return {
            "field_name": field_name,
            "history": [{"value": v.value, "timestamp": v.timestamp} for v in versions]
        }
    elif field_name in fk_string_fields:
        versions = db.query(VersionedForeignKeyField).filter(
            VersionedForeignKeyField.entity_type == "planowanie_budzetu",
            VersionedForeignKeyField.entity_id == planowanie_id,
            VersionedForeignKeyField.field_name == field_name
        ).order_by(desc(VersionedForeignKeyField.timestamp)).all()
        return {
            "field_name": field_name,
            "history": [{"value": v.value_string, "timestamp": v.timestamp} for v in versions]
        }
    elif field_name in fk_int_fields:
        versions = db.query(VersionedForeignKeyField).filter(
            VersionedForeignKeyField.entity_type == "planowanie_budzetu",
            VersionedForeignKeyField.entity_id == planowanie_id,
            VersionedForeignKeyField.field_name == field_name
        ).order_by(desc(VersionedForeignKeyField.timestamp)).all()
        return {
            "field_name": field_name,
            "history": [{"value": v.value_int, "timestamp": v.timestamp} for v in versions]
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unknown field: {field_name}")


@router.get("/planowanie_budzetu/{planowanie_id}/history")
async def get_planowanie_budzetu_history(planowanie_id: int, db: Session = Depends(get_db)):
    p = db.query(PlanowanieBudzetu).filter(PlanowanieBudzetu.id == planowanie_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="PlanowanieBudzetu not found")
    
    string_fields = ["nazwa_projektu", "nazwa_zadania", "szczegolowe_uzasadnienie_realizacji", "budzet"]
    fk_string_fields = ["czesc_budzetowa_kod", "dzial_kod", "rozdzial_kod", "paragraf_kod", "zrodlo_finansowania_kod"]
    fk_int_fields = ["grupa_wydatkow_id", "komorka_organizacyjna_id"]
    
    result = {"id": planowanie_id}
    
    for field in string_fields:
        versions = db.query(VersionedStringField).filter(
            VersionedStringField.entity_type == "planowanie_budzetu",
            VersionedStringField.entity_id == planowanie_id,
            VersionedStringField.field_name == field
        ).order_by(desc(VersionedStringField.timestamp)).all()
        result[f"{field}_history"] = [{"value": v.value, "timestamp": v.timestamp} for v in versions]
    
    for field in fk_string_fields:
        versions = db.query(VersionedForeignKeyField).filter(
            VersionedForeignKeyField.entity_type == "planowanie_budzetu",
            VersionedForeignKeyField.entity_id == planowanie_id,
            VersionedForeignKeyField.field_name == field
        ).order_by(desc(VersionedForeignKeyField.timestamp)).all()
        result[f"{field}_history"] = [{"value": v.value_string, "timestamp": v.timestamp} for v in versions]
    
    for field in fk_int_fields:
        versions = db.query(VersionedForeignKeyField).filter(
            VersionedForeignKeyField.entity_type == "planowanie_budzetu",
            VersionedForeignKeyField.entity_id == planowanie_id,
            VersionedForeignKeyField.field_name == field
        ).order_by(desc(VersionedForeignKeyField.timestamp)).all()
        result[f"{field}_history"] = [{"value": v.value_int, "timestamp": v.timestamp} for v in versions]
    
    return result


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
        result.append({
            "id": rok.id,
            "planowanie_budzetu_id": rok.planowanie_budzetu_id,
            "limit": get_latest_version_for_field(db, "rok_budzetowy", rok.id, "limit", "numeric"),
            "potrzeba": get_latest_version_for_field(db, "rok_budzetowy", rok.id, "potrzeba", "numeric")
        })
    
    return result


@router.get("/rok_budzetowy/{rok_id}")
async def get_rok_budzetowy(rok_id: int, db: Session = Depends(get_db)):
    rok = db.query(RokBudzetowy).filter(RokBudzetowy.id == rok_id).first()
    if not rok:
        raise HTTPException(status_code=404, detail="RokBudzetowy not found")
    
    return {
        "id": rok.id,
        "planowanie_budzetu_id": rok.planowanie_budzetu_id,
        "limit": get_latest_version_for_field(db, "rok_budzetowy", rok.id, "limit", "numeric"),
        "potrzeba": get_latest_version_for_field(db, "rok_budzetowy", rok.id, "potrzeba", "numeric")
    }


@router.get("/rok_budzetowy/{rok_id}/field_history/{field_name}")
async def get_rok_budzetowy_field_history(rok_id: int, field_name: str, db: Session = Depends(get_db)):
    rok = db.query(RokBudzetowy).filter(RokBudzetowy.id == rok_id).first()
    if not rok:
        raise HTTPException(status_code=404, detail="RokBudzetowy not found")
    
    numeric_fields = ["limit", "potrzeba"]
    
    if field_name in numeric_fields:
        versions = db.query(VersionedNumericField).filter(
            VersionedNumericField.entity_type == "rok_budzetowy",
            VersionedNumericField.entity_id == rok_id,
            VersionedNumericField.field_name == field_name
        ).order_by(desc(VersionedNumericField.timestamp)).all()
        return {
            "field_name": field_name,
            "history": [{"value": float(v.value), "timestamp": v.timestamp} for v in versions]
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unknown field: {field_name}")


@router.get("/rok_budzetowy/{rok_id}/history")
async def get_rok_budzetowy_history(rok_id: int, db: Session = Depends(get_db)):
    rok = db.query(RokBudzetowy).filter(RokBudzetowy.id == rok_id).first()
    if not rok:
        raise HTTPException(status_code=404, detail="RokBudzetowy not found")
    
    result = {
        "id": rok.id,
        "planowanie_budzetu_id": rok.planowanie_budzetu_id
    }
    
    for field in ["limit", "potrzeba"]:
        versions = db.query(VersionedNumericField).filter(
            VersionedNumericField.entity_type == "rok_budzetowy",
            VersionedNumericField.entity_id == rok_id,
            VersionedNumericField.field_name == field
        ).order_by(desc(VersionedNumericField.timestamp)).all()
        result[f"{field}_history"] = [{"value": float(v.value), "timestamp": v.timestamp} for v in versions]
    
    return result
