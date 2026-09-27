import { useState } from "react";
import { AlertTriangle } from "lucide-react";
import { getSymptomOptions, getSymptoms, logSymptoms } from "../../services/api";
import { useLoad } from "../../hooks/useLoad";
import { cap, fmtDate } from "../../utils";
import { Badge, Empty, ErrorText, Field, Loader, PageHeader } from "../../components/ui";

export default function SymptomsPage() {
  const opts = useLoad(getSymptomOptions);
  const history = useLoad(getSymptoms);
  const [picked, setPicked] = useState([]);
  const [weight, setWeight] = useState("");
  const [notes, setNotes] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const toggle = (s) => setPicked((p) => (p.includes(s) ? p.filter((x) => x !== s) : [...p, s]));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const log = await logSymptoms({ symptoms: picked, weight_kg: weight ? Number(weight) : null, notes: notes || null });
      setResult(log);
      setPicked([]);
      setWeight("");
      setNotes("");
      history.reload();
    } catch (err) {
      setError(err.message);
    }
  };

  if (opts.loading) return <Loader />;
  if (opts.error) return <ErrorText error={opts.error} />;
  const { common, danger_signs, urgent_message } = opts.data;

  const Chips = ({ items, danger }) => (
    <div className="flex flex-wrap gap-2">
      {items.map((s) => (
        <button type="button" key={s} onClick={() => toggle(s)} aria-pressed={picked.includes(s)}
          className={`chip ${picked.includes(s) ? (danger ? "border-red-400 bg-red-500/30 text-white" : "chip-on") : ""}`}>
          {cap(s)}
        </button>
      ))}
    </div>
  );

  return (
    <>
      <PageHeader title="Symptoms" subtitle="Log how you feel. Your doctor can see these entries." />
      {result?.urgent && (
        <div role="alert" className="mb-4 flex gap-3 rounded-xl border border-red-400/50 bg-red-500/15 p-4 text-sm text-red-100">
          <AlertTriangle className="h-5 w-5 shrink-0" /> {urgent_message}
        </div>
      )}
      {result && !result.urgent && <p className="mb-4 text-sm text-coco-accent">Saved. Keep logging daily.</p>}

      <form onSubmit={submit} className="card mb-6 space-y-4">
        <div><p className="label">Common symptoms</p><Chips items={common} /></div>
        <div><p className="label">Get help quickly if you have</p><Chips items={danger_signs} danger /></div>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Today's weight (kg)"><input type="number" step="0.1" className="input" value={weight} onChange={(e) => setWeight(e.target.value)} /></Field>
          <Field label="Notes"><input className="input" value={notes} onChange={(e) => setNotes(e.target.value)} /></Field>
        </div>
        <ErrorText error={error} />
        <button className="btn-orange" disabled={!picked.length && !weight && !notes}>Save entry</button>
      </form>

      <h2 className="mb-3 font-semibold text-white">History</h2>
      {history.loading ? <Loader /> : history.data?.length === 0 ? <Empty>No entries yet.</Empty> : (
        <div className="space-y-3">
          {history.data?.map((h) => (
            <div key={h.id} className="card">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-white">{fmtDate(h.logged_on)}</p>
                {h.urgent && <Badge tone="red">Danger sign</Badge>}
              </div>
              <p className="mt-1 text-sm text-slate-200">{h.symptoms.map(cap).join(", ") || "No symptoms"}</p>
              {(h.weight_kg || h.notes) && <p className="mt-1 text-xs text-coco-muted">{h.weight_kg ? `${h.weight_kg} kg. ` : ""}{h.notes}</p>}
            </div>
          ))}
        </div>
      )}
    </>
  );
}
