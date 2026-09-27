"""Demo data matching the UI mockups.  Run:  python seed.py"""
from datetime import date, datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models import (Child, Consultation, ConsultationMessage, Gender, GrowthMeasurement, PregnancyProfile,
                        Reminder, ReminderType, Role, SymptomLog, User)
from app.security import hash_password

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
db = SessionLocal()
pw = hash_password("password123")

amal = User(full_name="Amal Rahman", email="parent@coco.app", phone="+8801700000001",
            password_hash=pw, role=Role.parent)
doctor = User(full_name="Dr. Farhana Akter", email="doctor@coco.app", phone="+8801700000002",
              password_hash=pw, role=Role.doctor, specialization="Pediatrics")
nadia = User(full_name="Nadia Rahman", email="mother@coco.app", phone="+8801700000003",
             password_hash=pw, role=Role.pregnant_mother)
db.add_all([amal, doctor, nadia])
db.flush()

today = date.today()
emma = Child(parent_id=amal.id, name="Emma Rahman", date_of_birth=today - timedelta(days=int(28 * 30.44)),
             gender=Gender.female, height_cm=88, weight_kg=12.4, food_allergies=["Peanut"],
             medicine_allergies=[], dietary_habits="Vegetarian-leaning")
adam = Child(parent_id=amal.id, name="Adam Rahman", date_of_birth=today - timedelta(days=7 * 365 + 60),
             gender=Gender.male, height_cm=122, weight_kg=24)
db.add_all([emma, adam])
db.flush()

for months_ago, w, h in [(6, 11.2, 83), (3, 11.9, 86), (0, 12.4, 88)]:
    db.add(GrowthMeasurement(child_id=emma.id, measured_on=today - timedelta(days=months_ago * 30),
                             weight_kg=w, height_cm=h))
db.add(GrowthMeasurement(child_id=adam.id, measured_on=today, weight_kg=24, height_cm=122))

now = datetime.now().replace(second=0, microsecond=0)
db.add_all([
    Reminder(user_id=amal.id, child_id=emma.id, title="MMR - Emma", type=ReminderType.vaccination,
             due_at=now + timedelta(days=3)),
    Reminder(user_id=amal.id, child_id=emma.id, title="Vitamin D", type=ReminderType.medicine,
             due_at=now.replace(hour=20, minute=0)),
    Reminder(user_id=amal.id, child_id=adam.id, title="Deworming tablet - Adam",
             type=ReminderType.medicine, due_at=now + timedelta(days=7)),
    Consultation(patient_id=amal.id, doctor_id=doctor.id, child_id=emma.id,
                 reason="Routine growth check and nutrition plan review"),
    PregnancyProfile(user_id=nadia.id, due_date=today + timedelta(days=140), pre_pregnancy_weight_kg=55,
                     current_weight_kg=61, height_cm=158),
])
db.flush()
cons = db.query(Consultation).first()
db.add_all([
    ConsultationMessage(consultation_id=cons.id, sender_id=amal.id,
                        text="Assalamu alaikum doctor, Emma is eating less these days."),
    ConsultationMessage(consultation_id=cons.id, sender_id=doctor.id,
                        text="Walaikum assalam. Please log her weight every 2 weeks, I will review the plan."),
    Consultation(patient_id=nadia.id, doctor_id=doctor.id, reason="Second trimester diet advice"),
    SymptomLog(user_id=nadia.id, symptoms=["tiredness", "heartburn"], weight_kg=61),
])
db.commit()
print("Seeded. Logins (password: password123): parent@coco.app, mother@coco.app, doctor@coco.app")
