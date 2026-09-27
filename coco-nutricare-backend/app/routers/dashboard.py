from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Consultation, ConsultationStatus, Reminder, ReminderStatus, Role, User
from ..security import get_current_user
from ..services.growth import analyze_growth

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
ACTIVE = [ConsultationStatus.requested, ConsultationStatus.accepted]


def _greeting() -> str:
    h = datetime.now().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 17 else "Good evening"


def _count(db: Session, stmt) -> int:
    return db.scalar(select(func.count()).select_from(stmt.subquery())) or 0


@router.get("")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    first = user.full_name.split()[0]
    out = {"greeting": f"{_greeting()}, {first}!", "role": user.role.value}

    if user.role == Role.doctor:
        mine = select(Consultation).where(Consultation.doctor_id == user.id)
        out.update({
            "pending_requests": _count(db, mine.where(Consultation.status == ConsultationStatus.requested)),
            "upcoming": _count(db, mine.where(Consultation.status == ConsultationStatus.accepted)),
            "patients": db.scalar(select(func.count(func.distinct(Consultation.patient_id)))
                                  .where(Consultation.doctor_id == user.id)) or 0,
        })
        return out

    reminders = _count(db, select(Reminder).where(Reminder.user_id == user.id,
                                                  Reminder.status == ReminderStatus.pending))
    consultations = _count(db, select(Consultation).where(Consultation.patient_id == user.id,
                                                          Consultation.status.in_(ACTIVE)))
    out.update({"reminders": reminders, "consultations": consultations})

    if user.role == Role.parent:
        kids = []
        for c in user.children:
            g = analyze_growth(c)
            kids.append({"id": c.id, "name": c.name, "age": c.age, "weight_kg": c.weight_kg,
                         "status": "Needs review" if g["trend"] == "needs_review" else "Healthy"})
        out.update({
            "children_count": len(kids),
            "growth": "Needs review" if any(k["status"] == "Needs review" for k in kids) else "Healthy",
            "children": kids,
        })
    else:
        p = user.pregnancy
        out["pregnancy"] = None if not p else {
            "week": p.week, "trimester": p.trimester, "due_date": p.due_date.isoformat(),
        }
    return out
