from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime

from src.database import get_db
from src.schemas.planowanie_budzetu import PlanowanieBudzetu
from src.schemas.rok_budzetowy import RokBudzetowy
from src.schemas.users import User
from src.schemas.versioned_fields import (
    VersionedStringField,
    VersionedNumericField,
    VersionedForeignKeyField
)
from src.models.tabela_models import (
    PlanowanieBudzetuCreate,
    CellUpdate,
    RokBudzetowyCreate,
    MessageResponse,
    UpdateResponse,
    PlanowanieBudzetuResponse,
    FieldHistoryResponse,
    FieldsHistoryStatusResponse,
    RokBudzetowyResponse
)
from src.auth import get_current_user, validate_planowanie_access, validate_rok_budzetowy_access
from src.versioning_utils import (
    create_string_version,
    create_numeric_version,
    create_fk_version,
    get_latest_version_for_field,
    has_field_history
)

router = APIRouter()


def check_field_conflict(
        db: Session,
        entity_type: str,
        entity_id: int,
        field_name: str,
        field_type: str,
        client_timestamp: datetime
):
    """
    Checks if there are any versions of the field created AFTER the client_timestamp.
    If yes, raises HTTP 409 Conflict with the list of changes.
    """
    conflicting_changes = []

    if field_type == "string":
        query = db.query(VersionedStringField).filter(
            VersionedStringField.entity_type == entity_type,
            VersionedStringField.entity_id == entity_id,
            VersionedStringField.field_name == field_name,
            VersionedStringField.timestamp > client_timestamp
        ).order_by(desc(VersionedStringField.timestamp))

        results = query.all()
        conflicting_changes = [{"value": r.value, "timestamp": r.timestamp, "user_id": r.created_by} for r in results]

    elif field_type == "numeric":
        query = db.query(VersionedNumericField).filter(
            VersionedNumericField.entity_type == entity_type,
            VersionedNumericField.entity_id == entity_id,
            VersionedNumericField.field_name == field_name,
            VersionedNumericField.timestamp > client_timestamp
        ).order_by(desc(VersionedNumericField.timestamp))

        results = query.all()
        conflicting_changes = [{"value": float(r.value), "timestamp": r.timestamp, "user_id": r.created_by} for r in
                               results]

    elif field_type in ["fk_string", "fk_int"]:
        query = db.query(VersionedForeignKeyField).filter(
            VersionedForeignKeyField.entity_type == entity_type,
            VersionedForeignKeyField.entity_id == entity_id,
            VersionedForeignKeyField.field_name == field_name,
            VersionedForeignKeyField.timestamp > client_timestamp
        ).order_by(desc(VersionedForeignKeyField.timestamp))

        results = query.all()
        for r in results:
            val = r.value_int if field_type == "fk_int" else r.value_string
            conflicting_changes.append({"value": val, "timestamp": r.timestamp, "user_id": r.created_by})

    if conflicting_changes:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Data has been modified by another user.",
                "field": field_name,
                "changes": conflicting_changes
            }
        )


@router.get("/admin/planowanie_budzetu", response_model=List[PlanowanieBudzetuResponse])
async def get_admin_all_planowanie_budzetu(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Admin endpoint (user_id=0 only).
    Returns budget planning for ALL organizational units without filtering.
    """
    # 1. Authorization Check
    if current_user.id != 0:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Only administrator (ID 0) can access this data."
        )

    # 2. Get All Records
    planowania = db.query(PlanowanieBudzetu).all()
    result = []

    # 3. Construct Response (Fetching latest versions for all fields)
    for p in planowania:
        result.append({
            "id": p.id,
            "nazwa_projektu": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "nazwa_projektu", "string"),
            "nazwa_zadania": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "nazwa_zadania", "string"),
            "szczegolowe_uzasadnienie_realizacji": get_latest_version_for_field(db, "planowanie_budzetu", p.id,
                                                                                "szczegolowe_uzasadnienie_realizacji",
                                                                                "string"),
            "budzet": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "budzet", "string"),
            "czesc_budzetowa_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "czesc_budzetowa_kod",
                                                                "fk_string"),
            "dzial_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "dzial_kod", "fk_string"),
            "rozdzial_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "rozdzial_kod", "fk_string"),
            "paragraf_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "paragraf_kod", "fk_string"),
            "zrodlo_finansowania_kod": get_latest_version_for_field(db, "planowanie_budzetu", p.id,
                                                                    "zrodlo_finansowania_kod", "fk_string"),
            "grupa_wydatkow_id": get_latest_version_for_field(db, "planowanie_budzetu", p.id, "grupa_wydatkow_id",
                                                              "fk_int"),
            "komorka_organizacyjna_id": get_latest_version_for_field(db, "planowanie_budzetu", p.id,
                                                                     "komorka_organizacyjna_id", "fk_int")
        })

    return result


# PlanowanieBudzetu endpoints
@router.post("/planowanie_budzetu", response_model=MessageResponse)
async def create_planowanie_budzetu(
    data: PlanowanieBudzetuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate that user belongs to the specified komorka_organizacyjna
    if current_user.komorka_organizacyjna_id != data.komorka_organizacyjna_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot create planowanie for a different organizational unit"
        )
    
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
    create_fk_version(db, "planowanie_budzetu", planowanie.id, "user_id", value_int=current_user.id)
    
    db.commit()
    db.refresh(planowanie)
    
    return {"id": planowanie.id, "message": "Created successfully"}


@router.patch("/planowanie_budzetu/{planowanie_id}", response_model=UpdateResponse)
async def update_planowanie_budzetu_cell(
        planowanie_id: int,
        data: CellUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Validate access
    validate_planowanie_access(planowanie_id, current_user, db)

    planowanie = db.query(PlanowanieBudzetu).filter(PlanowanieBudzetu.id == planowanie_id).first()
    if not planowanie:
        raise HTTPException(status_code=404, detail="PlanowanieBudzetu not found")

    # Define field categories
    string_fields = ["nazwa_projektu", "nazwa_zadania", "szczegolowe_uzasadnienie_realizacji", "budzet"]
    fk_string_fields = ["czesc_budzetowa_kod", "dzial_kod", "rozdzial_kod", "paragraf_kod", "zrodlo_finansowania_kod"]
    fk_int_fields = ["grupa_wydatkow_id", "komorka_organizacyjna_id", "user_id"]

    # --- Conflict Detection Logic ---
    if data.last_known_timestamp:
        field_type = None
        if data.field in string_fields:
            field_type = "string"
        elif data.field in fk_string_fields:
            field_type = "fk_string"
        elif data.field in fk_int_fields:
            field_type = "fk_int"

        if field_type:
            check_field_conflict(
                db=db,
                entity_type="planowanie_budzetu",
                entity_id=planowanie_id,
                field_name=data.field,
                field_type=field_type,
                client_timestamp=data.last_known_timestamp
            )
    # -------------------------------

    if data.field in string_fields:
        create_string_version(db, "planowanie_budzetu", planowanie_id, data.field,
                              str(data.value) if data.value is not None else None)
    elif data.field in fk_string_fields:
        if data.value is None:
            raise HTTPException(status_code=400, detail=f"Field {data.field} cannot be null")
        create_fk_version(db, "planowanie_budzetu", planowanie_id, data.field, value_string=str(data.value))
    elif data.field in fk_int_fields:
        if data.value is None:
            raise HTTPException(status_code=400, detail=f"Field {data.field} cannot be null")

        # Validate komorka_organizacyjna_id changes
        if data.field == "komorka_organizacyjna_id" and int(data.value) != current_user.komorka_organizacyjna_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot change planowanie to a different organizational unit"
            )

        create_fk_version(db, "planowanie_budzetu", planowanie_id, data.field, value_int=int(data.value))
    else:
        raise HTTPException(status_code=400, detail=f"Unknown field: {data.field}")

    db.commit()

    return {"id": planowanie_id, "field": data.field, "value": data.value, "message": "Updated successfully"}

@router.get("/planowanie_budzetu", response_model=List[PlanowanieBudzetuResponse])
async def get_all_planowanie_budzetu(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all planowania
    planowania = db.query(PlanowanieBudzetu).all()
    result = []
    
    for p in planowania:
        # Filter by user's komorka_organizacyjna
        komorka_id = get_latest_version_for_field(db, "planowanie_budzetu", p.id, "komorka_organizacyjna_id", "fk_int")
        if komorka_id != current_user.komorka_organizacyjna_id:
            continue
        
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


@router.get("/planowanie_budzetu/{planowanie_id}", response_model=PlanowanieBudzetuResponse)
async def get_planowanie_budzetu(
    planowanie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate access
    validate_planowanie_access(planowanie_id, current_user, db)
    
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


@router.get("/planowanie_budzetu/{planowanie_id}/fields_history_status", response_model=FieldsHistoryStatusResponse)
async def get_planowanie_budzetu_fields_history_status(
    planowanie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get status of which fields have history (more than 1 version)"""
    # Validate access
    validate_planowanie_access(planowanie_id, current_user, db)
    
    p = db.query(PlanowanieBudzetu).filter(PlanowanieBudzetu.id == planowanie_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="PlanowanieBudzetu not found")
    
    fields_status = {
        "nazwa_projektu": has_field_history(db, "planowanie_budzetu", planowanie_id, "nazwa_projektu", "string"),
        "nazwa_zadania": has_field_history(db, "planowanie_budzetu", planowanie_id, "nazwa_zadania", "string"),
        "szczegolowe_uzasadnienie_realizacji": has_field_history(db, "planowanie_budzetu", planowanie_id, "szczegolowe_uzasadnienie_realizacji", "string"),
        "budzet": has_field_history(db, "planowanie_budzetu", planowanie_id, "budzet", "string"),
        "czesc_budzetowa_kod": has_field_history(db, "planowanie_budzetu", planowanie_id, "czesc_budzetowa_kod", "fk_string"),
        "dzial_kod": has_field_history(db, "planowanie_budzetu", planowanie_id, "dzial_kod", "fk_string"),
        "rozdzial_kod": has_field_history(db, "planowanie_budzetu", planowanie_id, "rozdzial_kod", "fk_string"),
        "paragraf_kod": has_field_history(db, "planowanie_budzetu", planowanie_id, "paragraf_kod", "fk_string"),
        "zrodlo_finansowania_kod": has_field_history(db, "planowanie_budzetu", planowanie_id, "zrodlo_finansowania_kod", "fk_string"),
        "grupa_wydatkow_id": has_field_history(db, "planowanie_budzetu", planowanie_id, "grupa_wydatkow_id", "fk_int"),
        "komorka_organizacyjna_id": has_field_history(db, "planowanie_budzetu", planowanie_id, "komorka_organizacyjna_id", "fk_int")
    }
    
    return {"fields": fields_status}


@router.get("/planowanie_budzetu/{planowanie_id}/field_history/{field_name}", response_model=FieldHistoryResponse)
async def get_planowanie_budzetu_field_history(
    planowanie_id: int,
    field_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate access
    validate_planowanie_access(planowanie_id, current_user, db)
    
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


# RokBudzetowy endpoints
@router.post("/rok_budzetowy", response_model=MessageResponse)
async def create_rok_budzetowy(
    data: RokBudzetowyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate access to parent planowanie
    validate_planowanie_access(data.planowanie_budzetu_id, current_user, db)
    
    # Verify planowanie_budzetu exists
    planowanie = db.query(PlanowanieBudzetu).filter(PlanowanieBudzetu.id == data.planowanie_budzetu_id).first()
    if not planowanie:
        raise HTTPException(status_code=404, detail="PlanowanieBudzetu not found")
    
    # Create main record with rok field
    rok = RokBudzetowy(
        planowanie_budzetu_id=data.planowanie_budzetu_id,
        rok=data.rok
    )
    db.add(rok)
    db.flush()
    
    # Create versioned fields
    create_numeric_version(db, "rok_budzetowy", rok.id, "limit", data.limit)
    create_numeric_version(db, "rok_budzetowy", rok.id, "potrzeba", data.potrzeba)
    
    db.commit()
    db.refresh(rok)
    
    return {"id": rok.id, "message": "Created successfully"}


@router.patch("/rok_budzetowy/{rok_id}", response_model=UpdateResponse)
async def update_rok_budzetowy_cell(
        rok_id: int,
        data: CellUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Validate access
    validate_rok_budzetowy_access(rok_id, current_user, db)

    rok = db.query(RokBudzetowy).filter(RokBudzetowy.id == rok_id).first()
    if not rok:
        raise HTTPException(status_code=404, detail="RokBudzetowy not found")

    numeric_fields = ["limit", "potrzeba"]

    # --- Conflict Detection Logic ---
    if data.last_known_timestamp:
        if data.field in numeric_fields:
            check_field_conflict(
                db=db,
                entity_type="rok_budzetowy",
                entity_id=rok_id,
                field_name=data.field,
                field_type="numeric",
                client_timestamp=data.last_known_timestamp
            )
    # -------------------------------

    if data.field in numeric_fields:
        if data.value is None:
            raise HTTPException(status_code=400, detail=f"Field {data.field} cannot be null")
        create_numeric_version(db, "rok_budzetowy", rok_id, data.field, float(data.value))
    else:
        raise HTTPException(status_code=400, detail=f"Unknown field: {data.field}")

    db.commit()

    return {"id": rok_id, "field": data.field, "value": data.value, "message": "Updated successfully"}

@router.get("/rok_budzetowy", response_model=List[RokBudzetowyResponse])
async def get_all_rok_budzetowy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lata = db.query(RokBudzetowy).all()
    result = []
    
    for rok in lata:
        # Check if user has access to the parent planowanie
        try:
            validate_planowanie_access(rok.planowanie_budzetu_id, current_user, db)
        except HTTPException:
            continue  # Skip this rok if no access
        
        result.append({
            "id": rok.id,
            "planowanie_budzetu_id": rok.planowanie_budzetu_id,
            "rok": rok.rok,
            "limit": get_latest_version_for_field(db, "rok_budzetowy", rok.id, "limit", "numeric"),
            "potrzeba": get_latest_version_for_field(db, "rok_budzetowy", rok.id, "potrzeba", "numeric")
        })
    
    return result


@router.get("/rok_budzetowy/{rok_id}", response_model=RokBudzetowyResponse)
async def get_rok_budzetowy(
    rok_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate access
    validate_rok_budzetowy_access(rok_id, current_user, db)
    
    rok = db.query(RokBudzetowy).filter(RokBudzetowy.id == rok_id).first()
    if not rok:
        raise HTTPException(status_code=404, detail="RokBudzetowy not found")
    
    return {
        "id": rok.id,
        "planowanie_budzetu_id": rok.planowanie_budzetu_id,
        "rok": rok.rok,
        "limit": get_latest_version_for_field(db, "rok_budzetowy", rok.id, "limit", "numeric"),
        "potrzeba": get_latest_version_for_field(db, "rok_budzetowy", rok.id, "potrzeba", "numeric")
    }


@router.get("/rok_budzetowy/{rok_id}/fields_history_status", response_model=FieldsHistoryStatusResponse)
async def get_rok_budzetowy_fields_history_status(
    rok_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get status of which fields have history (more than 1 version)"""
    # Validate access
    validate_rok_budzetowy_access(rok_id, current_user, db)
    
    rok = db.query(RokBudzetowy).filter(RokBudzetowy.id == rok_id).first()
    if not rok:
        raise HTTPException(status_code=404, detail="RokBudzetowy not found")
    
    fields_status = {
        "limit": has_field_history(db, "rok_budzetowy", rok_id, "limit", "numeric"),
        "potrzeba": has_field_history(db, "rok_budzetowy", rok_id, "potrzeba", "numeric")
    }
    
    return {"fields": fields_status}


@router.get("/rok_budzetowy/{rok_id}/field_history/{field_name}", response_model=FieldHistoryResponse)
async def get_rok_budzetowy_field_history(
    rok_id: int,
    field_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate access
    validate_rok_budzetowy_access(rok_id, current_user, db)
    
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
