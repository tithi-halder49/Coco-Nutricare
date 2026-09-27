# Coco NutriCare – Backend (FastAPI + SQLAlchemy)

## Run
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                     # optional demo data (password: password123)
uvicorn app.main:app --reload
```
Swagger UI: http://127.0.0.1:8000/docs  (click **Authorize**, username = email)
Tests: `pytest -q`

Default DB is SQLite. For PostgreSQL set `DATABASE_URL` (see `.env.example`) and `pip install psycopg2-binary`.

## Screen → API map
| UI screen | Endpoint |
|---|---|
| Create Account (Parent / Doctor / Pregnant Mother) | `POST /api/auth/register` |
| Welcome Back {role} login | `POST /api/auth/login` (send `role` to enforce the right login page) |
| Dashboard ("Good morning, Amal!", counts, child cards) | `GET /api/dashboard` |
| My Children / child profile / Edit Profile | `GET/POST /api/children`, `GET/PATCH/DELETE /api/children/{id}` |
| Add Child | `POST /api/children` |
| Nutrition Plan (targets, meals, allergy check, clinical validation) | `POST/GET /api/children/{id}/nutrition-plan` |
| Doctor approves plan | `POST /api/nutrition-plans/{id}/review` |
| Growth Tracking (weight, WHO percentile, trend, alert) | `GET /api/children/{id}/growth`, `POST .../growth/measurements` |
| Reminders (All / Vaccination / Medicine, Complete, Snooze) | `GET /api/reminders?type=`, `POST /api/reminders/{id}/complete`, `/snooze` |
| Consultations | `GET /api/doctors`, `POST/GET/PATCH /api/consultations` |
| Pregnant mother profile & plan | `PUT/GET /api/pregnancy`, `POST/GET /api/pregnancy/nutrition-plan` |
| Quick diet check (nothing saved) | `POST /api/diet-plan` |
| Symptom tracking (danger-sign alert) | `GET /api/pregnancy/symptom-options`, `GET/POST /api/pregnancy/symptoms` |
| Doctor view of a linked mother | `GET /api/pregnancy/patient/{user_id}` |
| Consultation chat | `GET/POST /api/consultations/{id}/messages?after_id=` |

All protected routes need header `Authorization: Bearer <token>`.

## Important notes
- **WHO percentiles**: the built-in table is a coarse approximation (0–5 yrs) for demo only.
  Download the official WHO weight-for-age LMS tables and set `WHO_WFA_BOYS_CSV` / `WHO_WFA_GIRLS_CSV`.
- **Nutrition targets** are reference values (IOM DRIs, energy estimated). Every plan starts as
  `pending_review` until a doctor approves it.
- Growth alerts are screening flags, not diagnoses.
