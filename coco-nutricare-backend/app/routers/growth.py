from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..access import get_child_for_user
from ..database import get_db
from ..models import GrowthMeasurement, Role, User
from ..schemas import GrowthSummary, MeasurementIn, MeasurementOut
from ..security import get_current_user, require_roles
from ..services.growth import analyze_growth

router = APIRouter(prefix="/children/{child_id}/growth", tags=["Growth Tracking"])


@router.get("", response_model=GrowthSummary)
def growth_summary(child_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return analyze_growth(get_child_for_user(db, child_id, user))


@router.post("/measurements", response_model=MeasurementOut, status_code=201)
def add_measurement(child_id: int, data: MeasurementIn, db: Session = Depends(get_db),
                    user: User = Depends(require_roles(Role.parent))):
    child = get_child_for_user(db, child_id, user, write=True)
    if data.measured_on < child.date_of_birth:
        raise HTTPException(422, "Measurement date is before date of birth")
    m = GrowthMeasurement(child_id=child.id, **data.model_dump())
    db.add(m)
    latest = max([x.measured_on for x in child.measurements] + [data.measured_on])
    if data.measured_on == latest:  # keep profile in sync with the newest reading
        child.weight_kg = data.weight_kg
        if data.height_cm:
            child.height_cm = data.height_cm
    db.commit()
    db.refresh(m)
    return m


@router.get("/measurements", response_model=list[MeasurementOut])
def list_measurements(child_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_child_for_user(db, child_id, user).measurements


@router.delete("/measurements/{measurement_id}", status_code=204)
def delete_measurement(child_id: int, measurement_id: int, db: Session = Depends(get_db),
                       user: User = Depends(require_roles(Role.parent))):
    get_child_for_user(db, child_id, user, write=True)
    m = db.get(GrowthMeasurement, measurement_id)
    if not m or m.child_id != child_id:
        raise HTTPException(404, "Measurement not found")
    db.delete(m)
    db.commit()
