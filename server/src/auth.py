from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from src.database import get_db
from src.schemas.users import User
from src.schemas.planowanie_budzetu import PlanowanieBudzetu
from src.versioning_utils import get_latest_version_for_field


async def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    """
    Extract and validate user_id from Authorization header.
    Mock authentication - expects header format: Authorization: <user_id>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        user_id = int(authorization)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    return user_id


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from database and validate existence."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def validate_planowanie_access(
    planowanie_id: int,
    user: User,
    db: Session
) -> None:
    """
    Validate that user has access to PlanowanieBudzetu.
    User must be in the same komorka_organizacyjna as the planowanie.
    """
    planowanie = db.query(PlanowanieBudzetu).filter(
        PlanowanieBudzetu.id == planowanie_id
    ).first()
    
    if not planowanie:
        raise HTTPException(status_code=404, detail="PlanowanieBudzetu not found")
    
    # Get current komorka_organizacyjna_id for this planowanie
    planowanie_komorka_id = get_latest_version_for_field(
        db, "planowanie_budzetu", planowanie_id, "komorka_organizacyjna_id", "fk_int"
    )
    
    if planowanie_komorka_id != user.komorka_organizacyjna_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: User's organizational unit does not match planowanie's organizational unit"
        )


def validate_rok_budzetowy_access(
    rok_id: int,
    user: User,
    db: Session
) -> None:
    """
    Validate that user has access to RokBudzetowy through its parent PlanowanieBudzetu.
    """
    from src.schemas.rok_budzetowy import RokBudzetowy
    
    rok = db.query(RokBudzetowy).filter(RokBudzetowy.id == rok_id).first()
    if not rok:
        raise HTTPException(status_code=404, detail="RokBudzetowy not found")
    
    # Validate access through parent planowanie
    validate_planowanie_access(rok.planowanie_budzetu_id, user, db)
