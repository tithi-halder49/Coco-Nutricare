"""Shared ownership/permission checks."""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import ChildProfile, Consultation, Role, User

def get_child_for_user(db: Session, child_id: int, user: User, write: bool = False) -> ChildProfile:
    child = db.get(ChildProfile, child_id)
    if not child:
        raise HTTPException(404, "Child not found")
    if user.role == Role.parent and child.parent_id == user.id:
        return child
    if user.role == Role.doctor and not write:
        linked = db.scalar(
            select(Consultation.id).where(
                Consultation.doctor_id == user.id, Consultation.child_id == child_id
            )
        )
        if linked:
            return child
    raise HTTPException(404, "Child not found")


def doctor_has_patient(db: Session, doctor_id: int, patient_id: int) -> bool:
    return bool(
        db.scalar(
            select(Consultation.id).where(
                Consultation.doctor_id == doctor_id, Consultation.patient_id == patient_id
            )
        )
    )