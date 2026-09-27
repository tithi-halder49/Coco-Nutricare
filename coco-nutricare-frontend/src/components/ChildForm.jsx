import { useState } from "react";
import { addChild, updateChild } from "../services/api";
import { splitList } from "../utils";
import { ErrorText, Field, Modal } from "./ui";

const empty = {
  name: "", date_of_birth: "", gender: "female", height_cm: "", weight_kg: "",
  food_allergies: "", medicine_allergies: "", dietary_habits: "", medical_conditions: "",
};

const fromChild = (c) => ({
  ...c,
  height_cm: c.height_cm ?? "",
  weight_kg: c.weight_kg ?? "",
  food_allergies: (c.food_allergies || []).join(", "),
  medicine_allergies: (c.medicine_allergies || []).join(", "),
  dietary_habits: c.dietary_habits ?? "",
  medical_conditions: c.medical_conditions ?? "",
});

/** Add Child / Edit Profile modal. Pass `child` to edit. */
export default function ChildForm({ open, onClose, onSaved, child }) {
  const [form, setForm] = useState(child ? fromChild(child) : empty);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    const payload = {
      name: form.name.trim(),
      date_of_birth: form.date_of_birth,
      gender: form.gender,
      height_cm: form.height_cm ? Number(form.height_cm) : null,
      weight_kg: form.weight_kg ? Number(form.weight_kg) : null,
      food_allergies: splitList(form.food_allergies),
      medicine_allergies: splitList(form.medicine_allergies),
      dietary_habits: form.dietary_habits || null,
      medical_conditions: form.medical_conditions || null,
    };
    try {
      const saved = child ? await updateChild(child.id, payload) : await addChild(payload);
      if (!child) setForm(empty);
      onSaved(saved);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={child ? "Edit profile" : "Add child"}>
      <form onSubmit={submit} className="space-y-3">
        <Field label="Child name"><input className="input" required value={form.name} onChange={set("name")} /></Field>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Date of birth">
            <input type="date" className="input" required max={new Date().toISOString().slice(0, 10)}
              value={form.date_of_birth} onChange={set("date_of_birth")} />
          </Field>
          <Field label="Gender">
            <select className="input" value={form.gender} onChange={set("gender")}>
              <option value="female">Female</option>
              <option value="male">Male</option>
            </select>
          </Field>
          <Field label="Height (cm)">
            <input type="number" step="0.1" className="input" value={form.height_cm} onChange={set("height_cm")} />
          </Field>
          <Field label="Weight (kg)">
            <input type="number" step="0.1" className="input" value={form.weight_kg} onChange={set("weight_kg")} />
          </Field>
        </div>
        <Field label="Food allergies (comma separated)">
          <input className="input" placeholder="Peanut, egg" value={form.food_allergies} onChange={set("food_allergies")} />
        </Field>
        <Field label="Medicine allergies">
          <input className="input" placeholder="None" value={form.medicine_allergies} onChange={set("medicine_allergies")} />
        </Field>
        <Field label="Dietary habits">
          <input className="input" placeholder="Vegetarian-leaning" value={form.dietary_habits} onChange={set("dietary_habits")} />
        </Field>
        <Field label="Medical conditions">
          <textarea className="input" value={form.medical_conditions} onChange={set("medical_conditions")} />
        </Field>
        <ErrorText error={error} />
        <div className="flex gap-2 pt-2">
          <button className="btn-orange flex-1" disabled={busy}>{child ? "Save changes" : "Add child"}</button>
          <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
        </div>
      </form>
    </Modal>
  );
}
