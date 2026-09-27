import { AlertTriangle, ShieldCheck } from "lucide-react";
import { Badge, PLAN_STATUS } from "./ui";

const TARGET_LABELS = {
  calories_kcal: ["Calories", "kcal"],
  protein_g: ["Protein", "g"],
  iron_mg: ["Iron", "mg"],
  calcium_mg: ["Calcium", "mg"],
  folate_mcg_dfe: ["Folate", "mcg"],
};
const SLOT_ORDER = ["breakfast", "lunch", "snack", "dinner"];

/**
 * Renders a nutrition plan. Works for saved plans (with status) and for the
 * stateless /api/diet-plan result (with warnings + bmi).
 */
export default function PlanView({ plan }) {
  const warnings = plan.warnings ?? [];
  const slots = SLOT_ORDER.filter((s) => plan.meals?.[s]);

  return (
    <div className="space-y-4">
      <div className="card">
        <h3 className="mb-2 font-semibold text-white">Daily nutrition target</h3>
        {Object.entries(TARGET_LABELS).map(([key, [label, unit]]) =>
          plan.targets?.[key] !== undefined ? (
            <div className="row" key={key}>
              <span className="text-coco-muted">{label}</span>
              <span className="font-semibold text-white">
                {plan.targets[key].toLocaleString()} {unit}
              </span>
            </div>
          ) : null
        )}
        {plan.bmi && (
          <div className="row">
            <span className="text-coco-muted">BMI</span>
            <span className="font-semibold text-white">{plan.bmi}</span>
          </div>
        )}
      </div>

      {slots.map((slot) => (
        <div className="card" key={slot}>
          <h3 className="mb-1 font-semibold capitalize text-white">{slot}</h3>
          <p className="text-sm text-slate-200">
            {plan.meals[slot].length ? plan.meals[slot].join(", ") : "No safe option found - ask your doctor."}
          </p>
        </div>
      ))}

      <div className="card">
        <h3 className="mb-1 flex items-center gap-2 font-semibold text-white">
          <ShieldCheck className="h-4 w-4 text-coco-accent" /> Allergy check
        </h3>
        <p className="text-sm text-coco-accent">
          {plan.removed_foods?.length
            ? `Filtered out safely: ${plan.removed_foods.join(", ")}.`
            : "No foods needed to be removed."}
        </p>
      </div>

      {warnings.length > 0 && (
        <div className="rounded-xl border border-coco-orange/40 bg-coco-orange/10 p-4">
          {warnings.map((w) => (
            <p key={w} className="flex gap-2 text-sm text-orange-200">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" /> {w}
            </p>
          ))}
        </div>
      )}

      <div className="card">
        <h3 className="mb-2 font-semibold text-white">Clinical validation</h3>
        {plan.status ? (
          <Badge tone={PLAN_STATUS[plan.status].tone}>{PLAN_STATUS[plan.status].label}</Badge>
        ) : (
          <Badge tone="orange">Review before feeding</Badge>
        )}
        {plan.review_note && <p className="mt-2 text-sm text-slate-200">Doctor's note: {plan.review_note}</p>}
        <ul className="mt-3 space-y-1 text-xs text-coco-muted">
          {plan.notes?.map((n) => (
            <li key={n}>{n}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
