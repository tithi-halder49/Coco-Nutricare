from fastapi import APIRouter, Depends

from ..models import User
from ..schemas import DietPlanIn, DietPlanOut
from ..security import get_current_user
from ..services.nutrition import plan_from_metrics

router = APIRouter(tags=["Nutrition Plan"])


@router.post("/diet-plan", response_model=DietPlanOut)
def calculate_diet_plan(data: DietPlanIn, _: User = Depends(get_current_user)):
    """Stateless calculator: send child metrics + allergies, get targets, meals and warnings back."""
    result = plan_from_metrics(data.age_months, data.gender, data.allergies,
                               data.dietary_habits, data.medical_conditions)
    bmi = None
    if data.weight_kg and data.height_cm:
        bmi = round(data.weight_kg / (data.height_cm / 100) ** 2, 1)
    return {**result, "bmi": bmi}
