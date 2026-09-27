import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
if os.path.exists("test.db"):
    os.remove("test.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

c = TestClient(app)


def reg(role, email):
    r = c.post("/api/auth/register", json={"role": role, "full_name": "Test " + role, "email": email,
                                           "password": "secret123"})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}, r.json()["user"]["id"]


def test_full_flow():
    parent, _ = reg("parent", "p@t.com")
    doctor, doc_id = reg("doctor", "d@t.com")
    mother, _ = reg("pregnant_mother", "m@t.com")

    assert c.post("/api/auth/login", json={"email": "p@t.com", "password": "secret123",
                                           "role": "doctor"}).status_code == 403
    assert c.post("/api/auth/login", json={"email": "p@t.com", "password": "bad"}).status_code == 401

    r = c.post("/api/children", headers=parent, json={
        "name": "Emma Rahman", "date_of_birth": "2024-05-02", "gender": "female",
        "height_cm": 86, "weight_kg": 12.0, "food_allergies": ["Peanut"],
        "dietary_habits": "Vegetarian-leaning"})
    assert r.status_code == 201, r.text
    cid = r.json()["id"]

    r = c.post(f"/api/children/{cid}/growth/measurements", headers=parent,
               json={"measured_on": "2025-11-01", "weight_kg": 11.5})
    assert r.status_code == 201
    g = c.get(f"/api/children/{cid}/growth", headers=parent).json()
    assert g["who_percentile"] is not None and g["trend"] in {"normal", "needs_review"}

    plan = c.post(f"/api/children/{cid}/nutrition-plan", headers=parent).json()
    assert plan["status"] == "pending_review"
    assert all("Peanut" not in f for foods in plan["meals"].values() for f in foods)
    assert "Peanut butter toast" in plan["removed_foods"]

    # doctor can't review without consultation
    assert c.post(f"/api/nutrition-plans/{plan['id']}/review", headers=doctor,
                  json={"approve": True}).status_code == 403
    cons = c.post("/api/consultations", headers=parent,
                  json={"doctor_id": doc_id, "child_id": cid, "reason": "Plan review"}).json()
    assert c.get(f"/api/children/{cid}", headers=doctor).status_code == 200
    r = c.post(f"/api/nutrition-plans/{plan['id']}/review", headers=doctor, json={"approve": True, "note": "OK"})
    assert r.json()["status"] == "approved"
    assert c.patch(f"/api/consultations/{cons['id']}", headers=parent,
                   json={"doctor_notes": "hack"}).status_code == 403
    assert c.patch(f"/api/consultations/{cons['id']}", headers=doctor,
                   json={"status": "accepted"}).json()["status"] == "accepted"

    rem = c.post("/api/reminders", headers=parent, json={
        "title": "MMR - Emma", "type": "vaccination", "due_at": "2026-10-01T10:00:00+06:00",
        "child_id": cid}).json()
    snoozed = c.post(f"/api/reminders/{rem['id']}/snooze", headers=parent, json={"minutes": 30}).json()
    assert snoozed["due_at"] != rem["due_at"]
    assert len(c.get("/api/reminders?type=vaccination", headers=parent).json()) == 1
    c.post(f"/api/reminders/{rem['id']}/complete", headers=parent)
    assert c.get("/api/reminders", headers=parent).json() == []

    d = c.get("/api/dashboard", headers=parent).json()
    assert d["children_count"] == 1 and d["consultations"] == 1

    assert c.put("/api/pregnancy", headers=mother, json={"lmp_date": "2026-05-01"}).status_code == 200
    pp = c.post("/api/pregnancy/nutrition-plan", headers=mother).json()
    assert pp["targets"]["iron_mg"] == 27

    # other parent can't see the child
    other, _ = reg("parent", "o@t.com")
    assert c.get(f"/api/children/{cid}", headers=other).status_code == 404


def test_diet_plan_symptoms_chat():
    parent, _ = reg("parent", "p2@t.com")
    doctor, doc_id = reg("doctor", "d2@t.com")
    mother, mother_id = reg("pregnant_mother", "m2@t.com")

    r = c.post("/api/diet-plan", headers=parent, json={
        "age_months": 28, "gender": "female", "weight_kg": 12.4, "height_cm": 88,
        "allergies": ["Peanut", "kiwi"]}).json()
    assert r["bmi"] == 16.0
    assert "Peanut butter toast" in r["removed_foods"]
    assert any("kiwi" in w for w in r["warnings"])

    c.put("/api/pregnancy", headers=mother, json={"lmp_date": "2026-05-01"})
    s1 = c.post("/api/pregnancy/symptoms", headers=mother, json={"symptoms": ["nausea"]}).json()
    s2 = c.post("/api/pregnancy/symptoms", headers=mother, json={"symptoms": ["Blurred vision"]}).json()
    assert s1["urgent"] is False and s2["urgent"] is True

    assert c.get(f"/api/pregnancy/patient/{mother_id}", headers=doctor).status_code == 403
    cons = c.post("/api/consultations", headers=mother, json={"doctor_id": doc_id, "reason": "Diet"}).json()
    assert c.get(f"/api/pregnancy/patient/{mother_id}", headers=doctor).status_code == 200

    m1 = c.post(f"/api/consultations/{cons['id']}/messages", headers=mother, json={"text": "Hello"}).json()
    c.post(f"/api/consultations/{cons['id']}/messages", headers=doctor, json={"text": "Hi"})
    new = c.get(f"/api/consultations/{cons['id']}/messages?after_id={m1['id']}", headers=mother).json()
    assert [m["text"] for m in new] == ["Hi"]
    assert c.post(f"/api/consultations/{cons['id']}/messages", headers=parent,
                  json={"text": "x"}).status_code == 404
