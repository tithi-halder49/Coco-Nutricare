from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from .models import ConsultationStatus, Gender, PlanStatus, ReminderStatus, ReminderType, Role


def _to_local_naive(v: Optional[datetime]) -> Optional[datetime]:
    if v is not None and v.tzinfo is not None:
        return v.astimezone().replace(tzinfo=None)
    return v


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Auth ----------
class RegisterIn(BaseModel):
    role: Role
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=20)
    password: str = Field(min_length=6, max_length=72)
    specialization: Optional[str] = Field(default=None, max_length=120)


class LoginIn(BaseModel):
    email: EmailStr
    password: str
    role: Optional[Role] = None  # login screen per role; if given, must match


class UserOut(ORM):
    id: int
    full_name: str
    email: str
    phone: Optional[str]
    role: Role
    specialization: Optional[str]


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Children ----------
class ChildBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    date_of_birth: date
    gender: Gender
    height_cm: Optional[float] = Field(default=None, gt=0, lt=250)
    weight_kg: Optional[float] = Field(default=None, gt=0, lt=200)
    food_allergies: list[str] = []
    medicine_allergies: list[str] = []
    dietary_habits: Optional[str] = None
    medical_conditions: Optional[str] = None

    @field_validator("date_of_birth")
    @classmethod
    def dob_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return v


class ChildCreate(ChildBase):
    pass


class ChildUpdate(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    height_cm: Optional[float] = Field(default=None, gt=0, lt=250)
    weight_kg: Optional[float] = Field(default=None, gt=0, lt=200)
    food_allergies: Optional[list[str]] = None
    medicine_allergies: Optional[list[str]] = None
    dietary_habits: Optional[str] = None
    medical_conditions: Optional[str] = None


class ChildOut(ChildBase, ORM):
    id: int
    age: str


# ---------- Growth ----------
class MeasurementIn(BaseModel):
    measured_on: date = Field(default_factory=date.today)
    weight_kg: float = Field(gt=0, lt=200)
    height_cm: Optional[float] = Field(default=None, gt=0, lt=250)


class MeasurementOut(ORM):
    id: int
    measured_on: date
    weight_kg: float
    height_cm: Optional[float]


class GrowthPoint(BaseModel):
    measured_on: date
    weight_kg: float
    height_cm: Optional[float]
    age_months: float
    z_score: Optional[float]
    percentile: Optional[float]


class GrowthSummary(BaseModel):
    child_id: int
    child_name: str
    current_weight_kg: Optional[float]
    current_height_cm: Optional[float]
    who_percentile: Optional[float]
    trend: str  # no_data | normal | needs_review
    alerts: list[str]
    history: list[GrowthPoint]
    reference_note: str
    disclaimer: str


# ---------- Nutrition ----------
class NutritionPlanOut(ORM):
    id: int
    child_id: Optional[int]
    pregnancy_id: Optional[int]
    targets: dict
    meals: dict
    removed_foods: list[str]
    notes: list[str]
    status: PlanStatus
    review_note: Optional[str]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    created_at: datetime


class PlanReviewIn(BaseModel):
    approve: bool
    note: Optional[str] = None


# ---------- Pregnancy ----------
class PregnancyIn(BaseModel):
    due_date: Optional[date] = None
    lmp_date: Optional[date] = None  # last menstrual period; due date = LMP + 280 days
    pre_pregnancy_weight_kg: Optional[float] = Field(default=None, gt=0, lt=300)
    current_weight_kg: Optional[float] = Field(default=None, gt=0, lt=300)
    height_cm: Optional[float] = Field(default=None, gt=0, lt=250)
    food_allergies: list[str] = []
    dietary_habits: Optional[str] = None
    medical_conditions: Optional[str] = None

    @model_validator(mode="after")
    def need_a_date(self):
        if not self.due_date and not self.lmp_date:
            raise ValueError("Provide due_date or lmp_date")
        return self


class PregnancyOut(ORM):
    id: int
    due_date: date
    lmp_date: date
    week: int
    trimester: int
    pre_pregnancy_weight_kg: Optional[float]
    current_weight_kg: Optional[float]
    height_cm: Optional[float]
    food_allergies: list[str]
    dietary_habits: Optional[str]
    medical_conditions: Optional[str]


# ---------- Reminders ----------
class ReminderIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    type: ReminderType
    due_at: datetime
    child_id: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("due_at")
    @classmethod
    def _local_time(cls, v):
        return _to_local_naive(v)


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[ReminderType] = None
    due_at: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("due_at")
    @classmethod
    def _local_time(cls, v):
        return _to_local_naive(v)


class SnoozeIn(BaseModel):
    minutes: int = Field(default=60, ge=5, le=10080)


class ReminderOut(ORM):
    id: int
    title: str
    type: ReminderType
    due_at: datetime
    status: ReminderStatus
    child_id: Optional[int]
    notes: Optional[str]


# ---------- Consultations ----------
class ConsultationIn(BaseModel):
    doctor_id: int
    reason: str = Field(min_length=3)
    child_id: Optional[int] = None
    preferred_time: Optional[datetime] = None

    @field_validator("preferred_time")
    @classmethod
    def _local_time(cls, v):
        return _to_local_naive(v)


class ConsultationUpdate(BaseModel):
    status: Optional[ConsultationStatus] = None
    scheduled_at: Optional[datetime] = None
    doctor_notes: Optional[str] = None

    @field_validator("scheduled_at")
    @classmethod
    def _local_time(cls, v):
        return _to_local_naive(v)


class ConsultationOut(ORM):
    id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    doctor_name: str
    child_id: Optional[int]
    child_name: Optional[str]
    reason: str
    preferred_time: Optional[datetime]
    scheduled_at: Optional[datetime]
    status: ConsultationStatus
    doctor_notes: Optional[str]
    created_at: datetime


class DoctorOut(ORM):
    id: int
    full_name: str
    specialization: Optional[str]


# ---------- Stateless diet plan calculator ----------
class DietPlanIn(BaseModel):
    """Child metrics sent from the 'AI Diet Plan' modal. Nothing is saved."""
    name: Optional[str] = None
    age_months: int = Field(ge=0, le=216)
    gender: Gender = Gender.female
    weight_kg: Optional[float] = Field(default=None, gt=0, lt=200)
    height_cm: Optional[float] = Field(default=None, gt=0, lt=250)
    allergies: list[str] = []
    dietary_habits: Optional[str] = None
    medical_conditions: Optional[str] = None


class DietPlanOut(BaseModel):
    targets: dict
    meals: dict
    removed_foods: list[str]
    warnings: list[str]
    notes: list[str]
    bmi: Optional[float] = None


# ---------- Symptoms ----------
class SymptomIn(BaseModel):
    logged_on: date = Field(default_factory=date.today)
    symptoms: list[str] = []
    weight_kg: Optional[float] = Field(default=None, gt=0, lt=300)
    notes: Optional[str] = None


class SymptomOut(ORM):
    id: int
    logged_on: date
    symptoms: list[str]
    weight_kg: Optional[float]
    notes: Optional[str]
    urgent: bool


# ---------- Chat ----------
class MessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class MessageOut(ORM):
    id: int
    sender_id: int
    sender_name: str
    text: str
    created_at: datetime
