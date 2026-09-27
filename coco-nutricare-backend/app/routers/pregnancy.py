from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..access import doctor_has_patient
from ..database import get_db
from ..models import NutritionPlan, PregnancyProfile, Role, SymptomLog, User
from ..schemas import NutritionPlanOut, PregnancyIn, PregnancyOut, SymptomIn, SymptomOut
from ..security import require_roles
from ..services.symptoms import COMMON, DANGER_SIGNS, URGENT_MESSAGE, is_urgent

router = APIRouter(prefix="/pregnancy", tags=["Pregnancy"])
mother_only = require_roles(Role.pregnant_mother)


@router.get("", response_model=PregnancyOut)
def get_profile(user: User = Depends(mother_only)):
    if not user.pregnancy:
        raise HTTPException(404, "Pregnancy profile not created yet")
    return user.pregnancy


@router.put("", response_model=PregnancyOut)
def upsert_profile(data: PregnancyIn, db: Session = Depends(get_db), user: User = Depends(mother_only)):
    fields = data.model_dump(exclude={"lmp_date", "due_date"})
    due = data.due_date or (data.lmp_date + timedelta(days=280))
    profile = user.pregnancy or PregnancyProfile(user_id=user.id)
    profile.due_date = due
    for k, v in fields.items():
        setattr(profile, k, v)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


# ---------- Symptom tracking ----------
@router.get("/symptom-options")
def symptom_options():
    return {"common": COMMON, "danger_signs": sorted(DANGER_SIGNS), "urgent_message": URGENT_MESSAGE}


@router.get("/symptoms", response_model=list[SymptomOut])
def list_symptoms(db: Session = Depends(get_db), user: User = Depends(mother_only)):
    stmt = select(SymptomLog).where(SymptomLog.user_id == user.id).order_by(SymptomLog.logged_on.desc(),
                                                                          SymptomLog.id.desc())
    return db.scalars(stmt).all()


@router.post("/symptoms", response_model=SymptomOut, status_code=201)
def log_symptoms(data: SymptomIn, db: Session = Depends(get_db), user: User = Depends(mother_only)):
    log = SymptomLog(user_id=user.id, urgent=is_urgent(data.symptoms), **data.model_dump())
    db.add(log)
    if data.weight_kg and user.pregnancy:
        user.pregnancy.current_weight_kg = data.weight_kg
    db.commit()
    db.refresh(log)
    return log


# ---------- Doctor view of a linked mother ----------
@router.get("/patient/{patient_id}")
def patient_overview(patient_id: int, db: Session = Depends(get_db),
                     doctor: User = Depends(require_roles(Role.doctor))):
    if not doctor_has_patient(db, doctor.id, patient_id):
        raise HTTPException(403, "You have no consultation with this patient")
    patient = db.get(User, patient_id)
    p = patient.pregnancy if patient else None
    if not p:
        raise HTTPException(404, "No pregnancy profile for this patient")
    plan = db.scalars(select(NutritionPlan).where(NutritionPlan.pregnancy_id == p.id)
                      .order_by(NutritionPlan.id.desc())).first()
    logs = db.scalars(select(SymptomLog).where(SymptomLog.user_id == patient_id)
                      .order_by(SymptomLog.logged_on.desc()).limit(10)).all()
    return {
        "profile": PregnancyOut.model_validate(p),
        "latest_plan": NutritionPlanOut.model_validate(plan) if plan else None,
        "recent_symptoms": [SymptomOut.model_validate(l) for l in logs],
    }
