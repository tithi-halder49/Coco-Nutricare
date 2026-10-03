from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime


# ==========================================
# 1. Auth Schemas
# ==========================================

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# 2. Child Profile Schemas
# ==========================================

class ChildProfileBase(BaseModel):
    name: str
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None


class ChildProfileCreate(ChildProfileBase):
    pass


class ChildProfileUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None


class ChildProfileResponse(ChildProfileBase):
    id: int
    parent_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# 3. Growth Tracking Schemas
# ==========================================

class MeasurementIn(BaseModel):
    measured_on: date
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    head_circumference_cm: Optional[float] = None


class MeasurementOut(BaseModel):
    id: int
    child_id: int
    measured_on: date
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    head_circumference_cm: Optional[float] = None

    class Config:
        from_attributes = True


class GrowthSummary(BaseModel):
    latest_height: Optional[float] = None
    latest_weight: Optional[float] = None
    height_percentile: Optional[float] = None
    weight_percentile: Optional[float] = None
    status_notes: Optional[str] = None


# ==========================================
# 4. Diet Plan Schemas
# ==========================================

class DietPlanIn(BaseModel):
    child_id: int
    title: str
    description: Optional[str] = None
    calories: Optional[float] = None
    meal_type: Optional[str] = None


class DietPlanOut(BaseModel):
    id: int
    child_id: int
    title: str
    description: Optional[str] = None
    calories: Optional[float] = None
    meal_type: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# 5. Consultations & Messages Schemas
# ==========================================

class DoctorOut(BaseModel):
    id: int
    name: str
    specialty: Optional[str] = None
    experience_years: Optional[int] = None
    contact_number: Optional[str] = None

    class Config:
        from_attributes = True


class ConsultationIn(BaseModel):
    doctor_id: int
    topic: Optional[str] = None
    notes: Optional[str] = None


class ConsultationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class ConsultationOut(BaseModel):
    id: int
    user_id: int
    doctor_id: int
    status: Optional[str] = None
    topic: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageIn(BaseModel):
    consultation_id: int
    sender_type: str
    message: str


class MessageOut(BaseModel):
    id: int
    consultation_id: int
    sender_type: str
    message: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# 6. Nutrition Schemas
# ==========================================

class NutritionTipOut(BaseModel):
    id: int
    title: str
    category: Optional[str] = None
    content: str

    class Config:
        from_attributes = True


class NutritionPlanOut(BaseModel):
    id: int

    # Plan owner
    child_id: Optional[int] = None
    pregnancy_id: Optional[int] = None

    # Generated nutrition information
    targets: dict
    meals: dict
    removed_foods: list
    notes: list

    # Clinical review information
    status: str

    reviewed_by: Optional[int] = None
    review_note: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PlanReviewIn(BaseModel):
    approve: bool
    note: Optional[str] = None


# ==========================================
# 7. Pregnancy & Symptom Schemas
# ==========================================

class PregnancyTrackerIn(BaseModel):
    due_date: date
    notes: Optional[str] = None


class PregnancyTrackerOut(BaseModel):
    id: int
    user_id: int
    due_date: date
    week_number: Optional[int] = None

    class Config:
        from_attributes = True


class PregnancyIn(BaseModel):
    due_date: date
    notes: Optional[str] = None


class PregnancyOut(BaseModel):
    id: int
    user_id: int
    due_date: date
    week_number: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SymptomIn(BaseModel):
    symptom_name: str
    severity: Optional[str] = None
    notes: Optional[str] = None


class SymptomOut(BaseModel):
    id: int
    user_id: int
    symptom_name: str
    severity: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# 8. Reminders Schemas
# ==========================================

class ReminderIn(BaseModel):
    title: str
    remind_at: datetime
    notes: Optional[str] = None


class ReminderOut(BaseModel):
    id: int
    user_id: int
    title: str
    remind_at: datetime
    is_completed: bool = False

    class Config:
        from_attributes = True


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    remind_at: Optional[datetime] = None
    notes: Optional[str] = None
    is_completed: Optional[bool] = None


class SnoozeIn(BaseModel):
    snooze_minutes: Optional[int] = 5