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
    child = get_child_for_user(db, child_id, user)
    return analyze_growth(child)


@router.post("/measurements", response_model=MeasurementOut, status_code=201)
def add_measurement(
    child_id: int,
    data: MeasurementIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.parent)),
):
    child = get_child_for_user(db, child_id, user, write=True)

    # dynamically handle date field (recorded_at or measured_on)
    measurement_date = getattr(data, "recorded_at", None) or getattr(data, "measured_on", None)

    if measurement_date and hasattr(child, "date_of_birth") and child.date_of_birth:
        if measurement_date < child.date_of_birth:
            raise HTTPException(status_code=422, detail="Measurement date is before date of birth")

    # DB insertion safely using available schema fields
    m_data = data.model_dump(exclude_unset=True)
    if "child_id" not in m_data:
        m_data["child_id"] = child.id

    m = GrowthMeasurement(**m_data)
    db.add(m)

    # Sync child profile with latest measurement logic
    existing_measurements = child.measurements if child.measurements else []
    existing_dates = [
        getattr(x, "recorded_at", None) or getattr(x, "measured_on", None) 
        for x in existing_measurements if (getattr(x, "recorded_at", None) or getattr(x, "measured_on", None))
    ]
    
    all_dates = [d for d in existing_dates if d is not None]
    if measurement_date:
        all_dates.append(measurement_date)

    latest_date = max(all_dates) if all_dates else None

    if measurement_date and measurement_date == latest_date:
        if hasattr(child, "weight_kg") and hasattr(data, "weight_kg"):
            child.weight_kg = data.weight_kg
        if hasattr(data, "height_cm") and data.height_cm and hasattr(child, "height_cm"):
            child.height_cm = data.height_cm

    db.commit()
    db.refresh(m)
    return m


@router.get("/measurements", response_model=list[MeasurementOut])
def list_measurements(child_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    child = get_child_for_user(db, child_id, user)
    return child.measurements


@router.delete("/measurements/{measurement_id}", status_code=204)
def delete_measurement(
    child_id: int,
    measurement_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.parent)),
):
    get_child_for_user(db, child_id, user, write=True)
    m = db.get(GrowthMeasurement, measurement_id)

    if not m or m.child_id != child_id:
        raise HTTPException(status_code=404, detail="Measurement not found")

    db.delete(m)
    db.commit()