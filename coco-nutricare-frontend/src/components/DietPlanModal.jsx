import { useState } from "react";
import { Sparkles } from "lucide-react";
import { getDietPlan } from "../services/api";
import { ageMonthsFromDob, splitList } from "../utils";
import PlanView from "./PlanView";
import { ErrorText, Field, Modal } from "./ui";

/**
 * Quick diet check (integration example for getDietPlan()).
 * Pre-fills from a child profile if one is passed; nothing is saved.
 */
export default function DietPlanModal({ open, onClose, child }) {
  const [form, setForm] = useState(() => ({
    age_months: child ? ageMonthsFromDob(child.date_of_birth) : "",
    gender: child?.gender ?? "female",
    weight_kg: child?.weight_kg ?? "",
    height_cm: child?.height_cm ?? "",
    allergies: (child?.food_allergies || []).join(", "),
    dietary_habits: child?.dietary_habits ?? "",
  }));
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const result = await getDietPlan({
        age_months: Number(form.age_months),
        gender: form.gender,
        weight_kg: form.weight_kg ? Number(form.weight_kg) : null,
        height_cm: form.height_cm ? Number(form.height_cm) : null,
        allergies: splitList(form.allergies),
        dietary_habits: form.dietary_habits || null,
      });
      setPlan(result); // -> re-render with the plan
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={child ? `Diet check for ${child.name}` : "Diet check"} wide>
      <form onSubmit={handleSubmit} className="mb-6 space-y-3">
        <div className="grid gap-3 sm:grid-cols-3">
          <Field label="Age (months)">
            <input type="number" min="0" max="216" required className="input" value={form.age_months} onChange={set("age_months")} />
          </Field>
          <Field label="Weight (kg)">
            <input type="number" step="0.1" className="input" value={form.weight_kg} onChange={set("weight_kg")} />
          </Field>
          <Field label="Height (cm)">
            <input type="number" step="0.1" className="input" value={form.height_cm} onChange={set("height_cm")} />
          </Field>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Gender">
            <select className="input" value={form.gender} onChange={set("gender")}>
              <option value="female">Female</option>
              <option value="male">Male</option>
            </select>
          </Field>
          <Field label="Dietary habits">
            <input className="input" value={form.dietary_habits} onChange={set("dietary_habits")} />
          </Field>
        </div>
        <Field label="Allergies (comma separated)">
          <input className="input" placeholder="Peanut, egg" value={form.allergies} onChange={set("allergies")} />
        </Field>
        <ErrorText error={error} />
        <button className="btn-orange w-full" disabled={loading}>
          <Sparkles className="h-4 w-4" /> {loading ? "Calculating..." : "Get diet plan"}
        </button>
      </form>
      {plan && <PlanView plan={plan} />}
    </Modal>
  );
}
