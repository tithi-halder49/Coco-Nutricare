import { useState } from "react";
import { savePregnancy } from "../../services/api";
import { splitList } from "../../utils";
import { ErrorText, Field } from "../../components/ui";

export default function PregnancyForm({ initial, onSaved, onCancel }) {
  const [form, setForm] = useState({
    due_date: initial?.due_date ?? "",
    lmp_date: "",
    pre_pregnancy_weight_kg: initial?.pre_pregnancy_weight_kg ?? "",
    current_weight_kg: initial?.current_weight_kg ?? "",
    height_cm: initial?.height_cm ?? "",
    food_allergies: (initial?.food_allergies || []).join(", "),
    dietary_habits: initial?.dietary_habits ?? "",
    medical_conditions: initial?.medical_conditions ?? "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const num = (v) => (v === "" ? null : Number(v));

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      onSaved(await savePregnancy({
        due_date: form.due_date || null,
        lmp_date: form.lmp_date || null,
        pre_pregnancy_weight_kg: num(form.pre_pregnancy_weight_kg),
        current_weight_kg: num(form.current_weight_kg),
        height_cm: num(form.height_cm),
        food_allergies: splitList(form.food_allergies),
        dietary_habits: form.dietary_habits || null,
        medical_conditions: form.medical_conditions || null,
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={submit} className="card space-y-3">
      <h3 className="font-semibold text-white">Pregnancy profile</h3>
      <p className="text-sm text-coco-muted">Enter your due date, or the first day of your last period if you don't know it.</p>
      <div className="grid gap-3 sm:grid-cols-2">
        <Field label="Due date"><input type="date" className="input" value={form.due_date} onChange={set("due_date")} /></Field>
        <Field label="First day of last period"><input type="date" className="input" value={form.lmp_date} onChange={set("lmp_date")} /></Field>
        <Field label="Weight before pregnancy (kg)"><input type="number" step="0.1" className="input" value={form.pre_pregnancy_weight_kg} onChange={set("pre_pregnancy_weight_kg")} /></Field>
        <Field label="Current weight (kg)"><input type="number" step="0.1" className="input" value={form.current_weight_kg} onChange={set("current_weight_kg")} /></Field>
        <Field label="Height (cm)"><input type="number" step="0.1" className="input" value={form.height_cm} onChange={set("height_cm")} /></Field>
        <Field label="Food allergies"><input className="input" placeholder="Shrimp" value={form.food_allergies} onChange={set("food_allergies")} /></Field>
      </div>
      <Field label="Dietary habits"><input className="input" value={form.dietary_habits} onChange={set("dietary_habits")} /></Field>
      <Field label="Medical conditions"><textarea className="input" value={form.medical_conditions} onChange={set("medical_conditions")} /></Field>
      <ErrorText error={error} />
      <div className="flex gap-2">
        <button className="btn-orange" disabled={busy}>Save profile</button>
        {onCancel && <button type="button" className="btn-ghost" onClick={onCancel}>Cancel</button>}
      </div>
    </form>
  );
}
