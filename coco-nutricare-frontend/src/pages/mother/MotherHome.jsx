import { useState } from "react";
import { Link } from "react-router-dom";
import { getDashboard, getPregnancy } from "../../services/api";
import { orNull, useLoad } from "../../hooks/useLoad";
import { fmtDate } from "../../utils";
import PregnancyForm from "./PregnancyForm";
import { ErrorText, Loader, PageHeader, Stat } from "../../components/ui";

export default function MotherHome() {
  const dash = useLoad(getDashboard);
  const preg = useLoad(() => orNull(getPregnancy()));
  const [editing, setEditing] = useState(false);

  if (dash.loading || preg.loading) return <Loader />;
  if (dash.error || preg.error) return <ErrorText error={dash.error || preg.error} />;
  const p = preg.data;

  const saved = (profile) => {
    preg.setData(profile);
    setEditing(false);
    dash.reload();
  };

  return (
    <>
      <PageHeader title={dash.data.greeting} subtitle="Your pregnancy at a glance." />
      {!p || editing ? (
        <PregnancyForm initial={p} onSaved={saved} onCancel={p ? () => setEditing(false) : null} />
      ) : (
        <>
          <div className="card mb-4 text-center">
            <p className="text-sm text-coco-muted">You are in week</p>
            <p className="text-5xl font-bold text-coco-accent">{p.week}</p>
            <p className="mt-1 text-sm text-slate-200">Trimester {p.trimester}, due {fmtDate(p.due_date)}</p>
          </div>
          <div className="mb-4 grid gap-3 sm:grid-cols-2">
            <Stat label="Current weight" value={p.current_weight_kg ? `${p.current_weight_kg} kg` : "-"} />
            <Stat label="Weight gained" value={p.current_weight_kg && p.pre_pregnancy_weight_kg ? `${(p.current_weight_kg - p.pre_pregnancy_weight_kg).toFixed(1)} kg` : "-"} />
            <Stat label="Reminders" value={dash.data.reminders} />
            <Stat label="Consultations" value={dash.data.consultations} />
          </div>
          <div className="flex flex-wrap gap-2">
            <Link to="/mother/symptoms" className="btn-orange">Log today's symptoms</Link>
            <Link to="/mother/nutrition" className="btn-green">See nutrition plan</Link>
            <button className="btn-ghost" onClick={() => setEditing(true)}>Edit profile</button>
          </div>
        </>
      )}
    </>
  );
}
