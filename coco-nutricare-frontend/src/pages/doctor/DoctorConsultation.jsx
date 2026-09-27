import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getChild, getConsultation, getPatientPregnancy, updateConsultation } from "../../services/api";
import { useLoad } from "../../hooks/useLoad";
import { cap, fmtDate } from "../../utils";
import ChatPanel from "../../components/ChatPanel";
import GrowthPanel from "../../components/GrowthPanel";
import ChildPlanCard from "../../components/ChildPlanCard";
import PlanView from "../../components/PlanView";
import PlanReview from "../../components/PlanReview";
import { Badge, CONSULT_TONE, Empty, ErrorText, Field, Loader, PageHeader } from "../../components/ui";

function ChildSection({ childId }) {
  const { data: c, loading, error } = useLoad(() => getChild(childId), [childId]);
  if (loading) return <Loader />;
  if (error) return <ErrorText error={error} />;
  return (
    <div className="space-y-4">
      <div className="card text-sm">
        <h3 className="mb-2 font-semibold text-white">{c.name}</h3>
        <p className="text-slate-200">{cap(c.gender)}, {c.age}. Allergies: {c.food_allergies.join(", ") || "none"}.</p>
        {c.medical_conditions && <p className="mt-1 text-orange-200">Conditions: {c.medical_conditions}</p>}
      </div>
      <h3 className="font-semibold text-white">Growth</h3>
      <GrowthPanel childId={childId} />
      <h3 className="font-semibold text-white">Nutrition plan</h3>
      <ChildPlanCard childId={childId} canReview />
    </div>
  );
}

function MotherSection({ patientId }) {
  const { data, loading, error, setData } = useLoad(() => getPatientPregnancy(patientId), [patientId]);
  if (loading) return <Loader />;
  if (error) return <Empty>{error}</Empty>;
  const { profile: p, latest_plan: plan, recent_symptoms: logs } = data;
  return (
    <div className="space-y-4">
      <div className="card text-sm text-slate-200">
        <h3 className="mb-2 font-semibold text-white">Pregnancy</h3>
        <p>Week {p.week}, trimester {p.trimester}, due {fmtDate(p.due_date)}.</p>
        <p>Weight {p.current_weight_kg ?? "-"} kg (before pregnancy {p.pre_pregnancy_weight_kg ?? "-"} kg).</p>
        {p.medical_conditions && <p className="mt-1 text-orange-200">Conditions: {p.medical_conditions}</p>}
      </div>
      <div className="card">
        <h3 className="mb-2 font-semibold text-white">Recent symptoms</h3>
        {logs.length === 0 && <p className="text-sm text-coco-muted">None logged.</p>}
        {logs.map((l) => (
          <div key={l.id} className="row">
            <span className="text-coco-muted">{fmtDate(l.logged_on)}</span>
            <span className="flex items-center gap-2 text-right text-slate-200">
              {l.symptoms.map(cap).join(", ") || "-"} {l.urgent && <Badge tone="red">Danger sign</Badge>}
            </span>
          </div>
        ))}
      </div>
      {plan ? (
        <>
          <PlanView plan={plan} />
          {plan.status === "pending_review" && (
            <PlanReview plan={plan} onReviewed={(updated) => setData((d) => ({ ...d, latest_plan: updated }))} />
          )}
        </>
      ) : (
        <Empty>This patient hasn't created a nutrition plan yet.</Empty>
      )}
    </div>
  );
}

export default function DoctorConsultation() {
  const { id } = useParams();
  const { data: c, loading, error, setData } = useLoad(() => getConsultation(id), [id]);
  const [notes, setNotes] = useState(null);
  const [when, setWhen] = useState(null);
  const [saveMsg, setSaveMsg] = useState("");

  if (loading) return <Loader />;
  if (error) return <ErrorText error={error} />;

  const save = async (e) => {
    e.preventDefault();
    try {
      const updated = await updateConsultation(c.id, {
        doctor_notes: notes ?? c.doctor_notes,
        scheduled_at: (when ?? c.scheduled_at?.slice(0, 16)) || null,
        ...(c.status === "requested" ? { status: "accepted" } : {}),
      });
      setData(updated);
      setSaveMsg("Saved.");
    } catch (err) {
      setSaveMsg(err.message);
    }
  };

  return (
    <>
      <p className="mb-2 text-sm text-coco-muted"><Link to="/doctor" className="hover:text-white">Consultations</Link> / {c.patient_name}</p>
      <PageHeader title={c.patient_name} subtitle={c.reason} action={<Badge tone={CONSULT_TONE[c.status]}>{cap(c.status)}</Badge>} />
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          {c.child_id ? <ChildSection childId={c.child_id} /> : <MotherSection patientId={c.patient_id} />}
        </div>
        <div className="space-y-4">
          <form onSubmit={save} className="card space-y-3">
            <h3 className="font-semibold text-white">Notes and schedule</h3>
            <Field label="Appointment time">
              <input type="datetime-local" className="input" value={when ?? c.scheduled_at?.slice(0, 16) ?? ""} onChange={(e) => setWhen(e.target.value)} />
            </Field>
            <Field label="Notes for the patient">
              <textarea className="input min-h-24" value={notes ?? c.doctor_notes ?? ""} onChange={(e) => setNotes(e.target.value)} />
            </Field>
            {saveMsg && <p className="text-sm text-coco-accent">{saveMsg}</p>}
            <button className="btn-green">{c.status === "requested" ? "Accept and save" : "Save"}</button>
          </form>
          <ChatPanel consultation={c} />
        </div>
      </div>
    </>
  );
}
