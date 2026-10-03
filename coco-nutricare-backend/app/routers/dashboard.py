from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..security import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("")
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    kids = []

    for c in user.children:
        # Get latest growth measurement
        latest_measurement = None

        if c.measurements:
            latest_measurement = max(
                c.measurements,
                key=lambda m: m.measured_on
            )

        kids.append({
            "id": c.id,
            "name": c.name,
            "age": c.age,
            "weight_kg": (
                latest_measurement.weight_kg
                if latest_measurement
                else None
            ),
            "height_cm": (
                latest_measurement.height_cm
                if latest_measurement
                else None
            ),
            "date_of_birth": c.date_of_birth,
        })

    return {
        "user": {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
        },
        "children": kids,
        "total_children": len(kids),
    }