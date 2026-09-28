import enum
from datetime import date, datetime, timedelta

from sqlalchemy import JSON, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .utils import age_label


class Role(str, enum.Enum):
    parent = "parent"
    pregnant_mother = "pregnant_mother"
    doctor = "doctor"


class Gender(str, enum.Enum):
    male = "male"
    female = "female"


class ReminderType(str, enum.Enum):
    vaccination = "vaccination"
    medicine = "medicine"
    other = "other"


class ReminderStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"


class ConsultationStatus(str, enum.Enum):
    requested = "requested"
    accepted = "accepted"
    completed = "completed"
    cancelled = "cancelled"


class PlanStatus(str, enum.Enum):
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role))
    specialization: Mapped[str | None] = mapped_column(String(120))  # doctors only
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    children: Mapped[list["Child"]] = relationship(back_populates="parent", cascade="all, delete-orphan")
    pregnancy: Mapped["PregnancyProfile | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Child(Base):
    __tablename__ = "children"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    date_of_birth: Mapped[date] = mapped_column(Date)
    gender: Mapped[Gender] = mapped_column(Enum(Gender))
    height_cm: Mapped[float | None] = mapped_column(Float)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    food_allergies: Mapped[list] = mapped_column(JSON, default=list)
    medicine_allergies: Mapped[list] = mapped_column(JSON, default=list)
    dietary_habits: Mapped[str | None] = mapped_column(String(255))
    medical_conditions: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    parent: Mapped[User] = relationship(back_populates="children")
    measurements: Mapped[list["GrowthMeasurement"]] = relationship(
        back_populates="child", cascade="all, delete-orphan", order_by="GrowthMeasurement.measured_on"
    )
    nutrition_plans: Mapped[list["NutritionPlan"]] = relationship(
        back_populates="child", cascade="all, delete-orphan"
    )

    @property
    def age(self) -> str:
        return age_label(self.date_of_birth)


class GrowthMeasurement(Base):
    __tablename__ = "growth_measurements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    measured_on: Mapped[date] = mapped_column(Date)
    weight_kg: Mapped[float] = mapped_column(Float)
    height_cm: Mapped[float | None] = mapped_column(Float)

    child: Mapped[Child] = relationship(back_populates="measurements")


class PregnancyProfile(Base):
    __tablename__ = "pregnancy_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    due_date: Mapped[date] = mapped_column(Date)
    pre_pregnancy_weight_kg: Mapped[float | None] = mapped_column(Float)
    current_weight_kg: Mapped[float | None] = mapped_column(Float)
    height_cm: Mapped[float | None] = mapped_column(Float)
    food_allergies: Mapped[list] = mapped_column(JSON, default=list)
    dietary_habits: Mapped[str | None] = mapped_column(String(255))
    medical_conditions: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="pregnancy")
    nutrition_plans: Mapped[list["NutritionPlan"]] = relationship(
        back_populates="pregnancy", cascade="all, delete-orphan"
    )

    @property
    def lmp_date(self) -> date:
        return self.due_date - timedelta(days=280)

    @property
    def week(self) -> int:
        return max(0, min(42, (date.today() - self.lmp_date).days // 7))

    @property
    def trimester(self) -> int:
        w = self.week
        return 1 if w < 14 else 2 if w < 28 else 3


class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    child_id: Mapped[int | None] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    pregnancy_id: Mapped[int | None] = mapped_column(
        ForeignKey("pregnancy_profiles.id", ondelete="CASCADE"), index=True
    )
    targets: Mapped[dict] = mapped_column(JSON)
    meals: Mapped[dict] = mapped_column(JSON)
    removed_foods: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[PlanStatus] = mapped_column(Enum(PlanStatus), default=PlanStatus.pending_review)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    review_note: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    child: Mapped[Child | None] = relationship(back_populates="nutrition_plans")
    pregnancy: Mapped[PregnancyProfile | None] = relationship(back_populates="nutrition_plans")


class Reminder(Base):
    __tablename__ = "reminders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    child_id: Mapped[int | None] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(160))
    type: Mapped[ReminderType] = mapped_column(Enum(ReminderType))
    due_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[ReminderStatus] = mapped_column(Enum(ReminderStatus), default=ReminderStatus.pending)
    notes: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="reminders")


class Consultation(Base):
    __tablename__ = "consultations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    child_id: Mapped[int | None] = mapped_column(ForeignKey("children.id", ondelete="SET NULL"))
    reason: Mapped[str] = mapped_column(Text)
    preferred_time: Mapped[datetime | None] = mapped_column(DateTime)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[ConsultationStatus] = mapped_column(
        Enum(ConsultationStatus), default=ConsultationStatus.requested
    )
    doctor_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    patient: Mapped[User] = relationship(foreign_keys=[patient_id])
    doctor: Mapped[User] = relationship(foreign_keys=[doctor_id])
    child: Mapped[Child | None] = relationship()

    @property
    def patient_name(self) -> str:
        return self.patient.full_name

    @property
    def doctor_name(self) -> str:
        return self.doctor.full_name

    @property
    def child_name(self) -> str | None:
        return self.child.name if self.child else None


class SymptomLog(Base):
    """Pregnant mother's daily symptom entry."""
    __tablename__ = "symptom_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    logged_on: Mapped[date] = mapped_column(Date, default=date.today)
    symptoms: Mapped[list] = mapped_column(JSON, default=list)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    urgent: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class ConsultationMessage(Base):
    """Chat message inside a consultation (patient <-> doctor)."""
    __tablename__ = "consultation_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    consultation_id: Mapped[int] = mapped_column(ForeignKey("consultations.id", ondelete="CASCADE"), index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    sender: Mapped[User] = relationship()

    @property
    def sender_name(self) -> str:
        return self.sender.full_name
