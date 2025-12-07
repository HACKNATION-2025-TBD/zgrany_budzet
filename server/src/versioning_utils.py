"""Utility functions for versioned fields."""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.schemas.versioned_fields import (
    VersionedStringField,
    VersionedNumericField,
    VersionedForeignKeyField
)


def create_string_version(
    db: Session,
    entity_type: str,
    entity_id: int,
    field_name: str,
    value: Optional[str],
    user_id: Optional[int] = None
) -> VersionedStringField:
    """Create a new version for a string field."""
    version = VersionedStringField(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        value=value,
        created_by_user_id=user_id
    )
    db.add(version)
    db.flush()
    return version


def create_numeric_version(
    db: Session,
    entity_type: str,
    entity_id: int,
    field_name: str,
    value: float,
    user_id: Optional[int] = None
) -> VersionedNumericField:
    """Create a new version for a numeric field."""
    version = VersionedNumericField(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        value=value,
        created_by_user_id=user_id
    )
    db.add(version)
    db.flush()
    return version


def create_fk_version(
    db: Session,
    entity_type: str,
    entity_id: int,
    field_name: str,
    value_string: Optional[str] = None,
    value_int: Optional[int] = None,
    user_id: Optional[int] = None
) -> VersionedForeignKeyField:
    """Create a new version for a foreign key field."""
    version = VersionedForeignKeyField(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        value_string=value_string,
        value_int=value_int,
        created_by_user_id=user_id
    )
    db.add(version)
    db.flush()
    return version


def get_latest_version_for_field(db: Session, entity_type: str, entity_id: int, field_name: str, field_type: str):
    """Get latest version for a specific field - optimized to query only latest."""
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


def has_field_history(db: Session, entity_type: str, entity_id: int, field_name: str, field_type: str) -> bool:
    """Check if a field has more than one version (has history)."""
    if field_type == "string":
        count = db.query(VersionedStringField).filter(
            VersionedStringField.entity_type == entity_type,
            VersionedStringField.entity_id == entity_id,
            VersionedStringField.field_name == field_name
        ).count()
    elif field_type == "numeric":
        count = db.query(VersionedNumericField).filter(
            VersionedNumericField.entity_type == entity_type,
            VersionedNumericField.entity_id == entity_id,
            VersionedNumericField.field_name == field_name
        ).count()
    elif field_type in ("fk_string", "fk_int"):
        count = db.query(VersionedForeignKeyField).filter(
            VersionedForeignKeyField.entity_type == entity_type,
            VersionedForeignKeyField.entity_id == entity_id,
            VersionedForeignKeyField.field_name == field_name
        ).count()
    else:
        return False
    
    return count > 1
