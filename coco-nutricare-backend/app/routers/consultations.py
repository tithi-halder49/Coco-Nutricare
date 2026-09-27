from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..access import get_child_for_user
from ..database import get_db
from ..models import Consultation, ConsultationMessage, ConsultationStatus, Role, User
from ..schemas import (ConsultationIn, ConsultationOut, ConsultationUpdate, DoctorOut, MessageIn,
                       MessageOut)
from ..security import get_current_user, require_roles

router = APIRouter(tags=["Consultations"])


@router.get("/doctors", response_model=list[DoctorOut])
def list_doctors(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.scalars(select(User).where(User.role == Role.doctor).order_by(User.full_name)).all()


@router.post("/consultations", response_model=ConsultationOut, status_code=201)
def request_consultation(data: ConsultationIn, db: Session = Depends(get_db),
                         user: User = Depends(require_roles(Role.parent, Role.pregnant_mother))):
    doctor = db.get(User, data.doctor_id)
    if not doctor or doctor.role != Role.doctor:
        raise HTTPException(404, "Doctor not found")
    if data.child_id:
        get_child_for_user(db, data.child_id, user, write=True)
    c = Consultation(patient_id=user.id, **data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.get("/consultations", response_model=list[ConsultationOut])
def list_consultations(status: ConsultationStatus | None = None, db: Session = Depends(get_db),
                       user: User = Depends(get_current_user)):
    stmt = select(Consultation).where(or_(Consultation.patient_id == user.id,
                                          Consultation.doctor_id == user.id))
    if status:
        stmt = stmt.where(Consultation.status == status)
    return db.scalars(stmt.order_by(Consultation.created_at.desc())).all()


@router.get("/consultations/{cid}", response_model=ConsultationOut)
def get_consultation(cid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    c = db.get(Consultation, cid)
    if not c or user.id not in (c.patient_id, c.doctor_id):
        raise HTTPException(404, "Consultation not found")
    return c


@router.patch("/consultations/{cid}", response_model=ConsultationOut)
def update_consultation(cid: int, data: ConsultationUpdate, db: Session = Depends(get_db),
                        user: User = Depends(get_current_user)):
    c = db.get(Consultation, cid)
    if not c or user.id not in (c.patient_id, c.doctor_id):
        raise HTTPException(404, "Consultation not found")
    changes = data.model_dump(exclude_unset=True)
    if user.id == c.patient_id and user.id != c.doctor_id:
        # patients may only cancel
        if set(changes) - {"status"} or changes.get("status") != ConsultationStatus.cancelled:
            raise HTTPException(403, "Patients can only cancel a consultation")
    for k, v in changes.items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


# ---------- Chat ----------
def _member(db: Session, cid: int, user: User) -> Consultation:
    c = db.get(Consultation, cid)
    if not c or user.id not in (c.patient_id, c.doctor_id):
        raise HTTPException(404, "Consultation not found")
    return c


@router.get("/consultations/{cid}/messages", response_model=list[MessageOut])
def list_messages(cid: int, after_id: int = 0, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    """Poll with after_id=<last id you have> to get only new messages."""
    _member(db, cid, user)
    stmt = select(ConsultationMessage).where(ConsultationMessage.consultation_id == cid,
                                             ConsultationMessage.id > after_id)
    return db.scalars(stmt.order_by(ConsultationMessage.id)).all()


@router.post("/consultations/{cid}/messages", response_model=MessageOut, status_code=201)
def send_message(cid: int, data: MessageIn, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    c = _member(db, cid, user)
    if c.status in (ConsultationStatus.cancelled, ConsultationStatus.completed):
        raise HTTPException(400, "This consultation is closed")
    m = ConsultationMessage(consultation_id=cid, sender_id=user.id, text=data.text.strip())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m
