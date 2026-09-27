from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..access import get_child_for_user
from ..database import get_db
from ..models import Reminder, ReminderStatus, ReminderType, Role, User
from ..schemas import ReminderIn, ReminderOut, ReminderUpdate, SnoozeIn
from ..security import require_roles

router = APIRouter(prefix="/reminders", tags=["Reminders"])
patient_only = require_roles(Role.parent, Role.pregnant_mother)


def _own(db: Session, rid: int, user: User) -> Reminder:
    r = db.get(Reminder, rid)
    if not r or r.user_id != user.id:
        raise HTTPException(404, "Reminder not found")
    return r


@router.get("", response_model=list[ReminderOut])
def list_reminders(type: ReminderType | None = None, status: ReminderStatus | None = ReminderStatus.pending,
                   db: Session = Depends(get_db), user: User = Depends(patient_only)):
    """Filter chips: All (no type) / Vaccination / Medicine."""
    stmt = select(Reminder).where(Reminder.user_id == user.id)
    if type:
        stmt = stmt.where(Reminder.type == type)
    if status:
        stmt = stmt.where(Reminder.status == status)
    return db.scalars(stmt.order_by(Reminder.due_at)).all()


@router.post("", response_model=ReminderOut, status_code=201)
def create_reminder(data: ReminderIn, db: Session = Depends(get_db), user: User = Depends(patient_only)):
    if data.child_id:
        get_child_for_user(db, data.child_id, user, write=True)
    r = Reminder(user_id=user.id, **data.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.patch("/{reminder_id}", response_model=ReminderOut)
def update_reminder(reminder_id: int, data: ReminderUpdate, db: Session = Depends(get_db),
                    user: User = Depends(patient_only)):
    r = _own(db, reminder_id, user)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r


@router.post("/{reminder_id}/complete", response_model=ReminderOut)
def complete(reminder_id: int, db: Session = Depends(get_db), user: User = Depends(patient_only)):
    r = _own(db, reminder_id, user)
    r.status = ReminderStatus.completed
    db.commit()
    db.refresh(r)
    return r


@router.post("/{reminder_id}/snooze", response_model=ReminderOut)
def snooze(reminder_id: int, data: SnoozeIn = SnoozeIn(), db: Session = Depends(get_db),
           user: User = Depends(patient_only)):
    r = _own(db, reminder_id, user)
    r.due_at = r.due_at + timedelta(minutes=data.minutes)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{reminder_id}", status_code=204)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db), user: User = Depends(patient_only)):
    db.delete(_own(db, reminder_id, user))
    db.commit()
