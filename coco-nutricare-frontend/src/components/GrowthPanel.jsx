import { useState } from "react";
import { AlertTriangle } from "lucide-react";
import { addMeasurement, getGrowth } from "../services/api";
import { useLoad } from "../hooks/useLoad";
import { Badge, ErrorText, Field, Loader, Stat } from "./ui";

function WeightChart({ history }) {
  if (history.length < 2) {
    return <p className="py-8 text-center text-sm text-coco-muted">Add at least two measurements to see the chart.</p>;
  }
  const W = 320, H = 140, P = 24;
  const ws = history.map((h) => h.weight_kg);
  const min = Math.min(...ws) - 0.5, max = Math.max(...ws) + 0.5;
  const pts = history.map((h, i) => [
    P + (i * (W - 2 * P)) / (history.length - 1),
    H - P - ((h.weight_kg - min) / (max - min)) * (H - 2 * P),
  ]);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Weight over time">
      <polyline points={pts.map((p) => p.join(",")).join(" ")} fill="none" stroke="#22b889" strokeWidth="2.5" />
      {pts.map(([x, y], i) => (
        <g key={i}>
          <circle cx={x} cy={y} r="4" fill="#f0932b" />
          <text x={x} y={y - 9} textAnchor="middle" fontSize="10" fill="#d9efe8">{history[i].weight_kg}</text>
          <text x={x} y={H - 6} textAnchor="middle" fontSize="9" fill="#8fb0a6">{history[i].measured_on.slice(5)}</text>
        </g>
      ))}
    </svg>
  );
}

export default function GrowthPanel({ childId, canEdit = false }) {
  const { data: g, loading, error, reload } = useLoad(() => getGrowth(childId), [childId]);
  const [form, setForm] = useState({ measured_on: new Date().toISOString().slice(0, 10), weight_kg: "", height_cm: "" });
  const [saveError, setSaveError] = useState("");
  const [busy, setBusy] = useState(false);

  const save = async (e) => {
    e.preventDefault();
    setBusy(true);
    setSaveError("");
    try {
      await addMeasurement(childId, {
        measured_on: form.measured_on,
        weight_kg: Number(form.weight_kg),
        height_cm: form.height_cm ? Number(form.height_cm) : null,
      });
      setForm((f) => ({ ...f, weight_kg: "", height_cm: "" }));
      reload();
    } catch (err) {
      setSaveError(err.message);
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <Loader />;
  if (error) return <ErrorText error={error} />;

  return (
    <div className="space-y-4">
      <div className="card"><WeightChart history={g.history} /></div>
      <div className="grid gap-3 sm:grid-cols-2">
        <Stat label="Current weight" value={g.current_weight_kg ? `${g.current_weight_kg} kg` : "-"} tone="green" />
        <Stat label="WHO percentile" value={g.who_percentile != null ? `${Math.round(g.who_percentile)}th` : "-"} tone="green" />
      </div>
      <div className="card">
        <h3 className="mb-2 font-semibold text-white">Growth trend</h3>
        {g.trend === "needs_review" ? (
          <Badge tone="orange">Needs review</Badge>
        ) : g.trend === "normal" ? (
          <Badge>Normal</Badge>
        ) : (
          <Badge tone="grey">No data yet</Badge>
        )}
        {g.alerts.map((a) => (
          <p key={a} className="mt-3 flex gap-2 text-sm text-orange-200">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" /> {a}
          </p>
        ))}
        <p className="mt-3 text-xs text-coco-muted">{g.disclaimer}</p>
        <p className="mt-1 text-xs text-coco-muted">{g.reference_note}</p>
      </div>

      {canEdit && (
        <form onSubmit={save} className="card space-y-3">
          <h3 className="font-semibold text-white">Add a measurement</h3>
          <div className="grid gap-3 sm:grid-cols-3">
            <Field label="Date">
              <input type="date" className="input" required value={form.measured_on}
                onChange={(e) => setForm({ ...form, measured_on: e.target.value })} />
            </Field>
            <Field label="Weight (kg)">
              <input type="number" step="0.1" min="0.5" className="input" required value={form.weight_kg}
                onChange={(e) => setForm({ ...form, weight_kg: e.target.value })} />
            </Field>
            <Field label="Height (cm)">
              <input type="number" step="0.1" min="20" className="input" value={form.height_cm}
                onChange={(e) => setForm({ ...form, height_cm: e.target.value })} />
            </Field>
          </div>
          <ErrorText error={saveError} />
          <button className="btn-green" disabled={busy}>Save measurement</button>
        </form>
      )}
    </div>
  );
}
