from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..access import doctor_has_patient, get_child_for_user
from ..database import get_db
from ..models import NutritionPlan, PlanStatus, Role, User
from ..schemas import NutritionPlanOut, PlanReviewIn
from ..security import get_current_user, require_roles
from ..services.nutrition import child_plan, pregnancy_plan

router = APIRouter(tags=["Nutrition Plan"])


def _latest(db: Session, **where) -> NutritionPlan | None:
    stmt = select(NutritionPlan).filter_by(**where).order_by(NutritionPlan.created_at.desc(),
                                                             NutritionPlan.id.desc())
    return db.scalars(stmt).first()


@router.post("/children/{child_id}/nutrition-plan", response_model=NutritionPlanOut, status_code=201)
def generate_child_plan(child_id: int, db: Session = Depends(get_db),
                        user: User = Depends(require_roles(Role.parent))):
    child = get_child_for_user(db, child_id, user, write=True)
    plan = NutritionPlan(child_id=child.id, **child_plan(child))
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/children/{child_id}/nutrition-plan", response_model=NutritionPlanOut)
def get_child_plan(child_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_child_for_user(db, child_id, user)
    plan = _latest(db, child_id=child_id)
    if not plan:
        raise HTTPException(404, "No plan yet - generate one with POST")
    return plan


@router.post("/pregnancy/nutrition-plan", response_model=NutritionPlanOut, status_code=201)
def generate_pregnancy_plan(db: Session = Depends(get_db),
                            user: User = Depends(require_roles(Role.pregnant_mother))):
    if not user.pregnancy:
        raise HTTPException(400, "Create your pregnancy profile first")
    plan = NutritionPlan(pregnancy_id=user.pregnancy.id, **pregnancy_plan(user.pregnancy))
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/pregnancy/nutrition-plan", response_model=NutritionPlanOut)
def get_pregnancy_plan(db: Session = Depends(get_db),
                       user: User = Depends(require_roles(Role.pregnant_mother))):
    plan = user.pregnancy and _latest(db, pregnancy_id=user.pregnancy.id)
    if not plan:
        raise HTTPException(404, "No plan yet - generate one with POST")
    return plan


@router.post("/nutrition-plans/{plan_id}/review", response_model=NutritionPlanOut)
def review_plan(plan_id: int, data: PlanReviewIn, db: Session = Depends(get_db),
                doctor: User = Depends(require_roles(Role.doctor))):
    """Clinical validation: a doctor linked by a consultation approves/rejects the plan."""
    plan = db.get(NutritionPlan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    owner_id = plan.child.parent_id if plan.child else plan.pregnancy.user_id
    if not doctor_has_patient(db, doctor.id, owner_id):
        raise HTTPException(403, "You have no consultation with this patient")
    plan.status = PlanStatus.approved if data.approve else PlanStatus.rejected
    plan.review_note = data.note
    plan.reviewed_by = doctor.id
    plan.reviewed_at = datetime.now()
    db.commit()
    db.refresh(plan)
    return plan
