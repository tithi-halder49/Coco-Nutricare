import { useState } from "react";
import { Plus } from "lucide-react";
import { getChildren, getConsultations, getDoctors, requestConsultation, updateConsultation } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { useLoad } from "../../hooks/useLoad";
import { cap, fmtDateTime } from "../../utils";
import ChatPanel from "../../components/ChatPanel";
import { Badge, CONSULT_TONE, Empty, ErrorText, Field, Loader, Modal, PageHeader } from "../../components/ui";

function RequestForm({ open, onClose, onSaved }) {
  const { user } = useAuth();
  const doctors = useLoad(getDoctors);
  const kids = useLoad(() => (user.role === "parent" ? getChildren() : Promise.resolve([])));
  const [form, setForm] = useState({ doctor_id: "", child_id: "", reason: "", preferred_time: "" });
  const [error, setError] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    try {
      const c = await requestConsultation({
        doctor_id: Number(form.doctor_id),
        child_id: form.child_id ? Number(form.child_id) : null,
        reason: form.reason,
        preferred_time: form.preferred_time || null,
      });
      onSaved(c);
      onClose();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Book a consultation">
      <form onSubmit={submit} className="space-y-3">
        <Field label="Doctor">
          <select className="input" required value={form.doctor_id} onChange={set("doctor_id")}>
            <option value="">Choose a doctor</option>
            {doctors.data?.map((d) => (
              <option key={d.id} value={d.id}>{d.full_name}{d.specialization ? `, ${d.specialization}` : ""}</option>
            ))}
          </select>
        </Field>
        {kids.data?.length > 0 && (
          <Field label="About which child?">
            <select className="input" value={form.child_id} onChange={set("child_id")}>
              <option value="">General</option>
              {kids.data.map((k) => <option key={k.id} value={k.id}>{k.name}</option>)}
            </select>
          </Field>
        )}
        <Field label="Reason"><textarea className="input" required minLength={3} value={form.reason} onChange={set("reason")} /></Field>
        <Field label="Preferred time (optional)"><input type="datetime-local" className="input" value={form.preferred_time} onChange={set("preferred_time")} /></Field>
        <ErrorText error={error} />
        <button className="btn-orange w-full">Send request</button>
      </form>
    </Modal>
  );
}

/** Patient side (parent or pregnant mother): list + chat. */
export default function ConsultationsPage() {
  const { data, loading, error, reload, setData } = useLoad(() => getConsultations());
  const [selectedId, setSelectedId] = useState(null);
  const [open, setOpen] = useState(false);
  const selected = data?.find((c) => c.id === selectedId);

  const cancel = async (c) => {
    const updated = await updateConsultation(c.id, { status: "cancelled" });
    setData((list) => list.map((x) => (x.id === c.id ? updated : x)));
  };

  return (
    <>
      <PageHeader title="Consultations" action={<button className="btn-orange" onClick={() => setOpen(true)}><Plus className="h-4 w-4" /> Book consultation</button>} />
      <ErrorText error={error} />
      {loading ? <Loader /> : data?.length === 0 ? <Empty>No consultations yet. Book one with a doctor.</Empty> : (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-3">
            {data?.map((c) => (
              <button key={c.id} onClick={() => setSelectedId(c.id)}
                className={`card block w-full text-left ${selectedId === c.id ? "border-coco-accent" : ""}`}>
                <div className="flex items-center justify-between gap-2">
                  <p className="font-semibold text-white">{c.doctor_name}</p>
                  <Badge tone={CONSULT_TONE[c.status]}>{cap(c.status)}</Badge>
                </div>
                <p className="mt-1 text-sm text-coco-muted">{c.child_name ? `${c.child_name}: ` : ""}{c.reason}</p>
                {c.scheduled_at && <p className="mt-1 text-xs text-coco-accent">Scheduled {fmtDateTime(c.scheduled_at)}</p>}
                {c.doctor_notes && <p className="mt-1 text-xs text-slate-300">Doctor's notes: {c.doctor_notes}</p>}
                {["requested", "accepted"].includes(c.status) && (
                  <span role="button" tabIndex={0} className="mt-2 inline-block text-xs text-orange-300 hover:underline"
                    onClick={(e) => { e.stopPropagation(); cancel(c); }}
                    onKeyDown={(e) => e.key === "Enter" && (e.stopPropagation(), cancel(c))}>
                    Cancel consultation
                  </span>
                )}
              </button>
            ))}
          </div>
          {selected ? <ChatPanel consultation={selected} /> : <Empty>Choose a consultation to open the chat.</Empty>}
        </div>
      )}
      <RequestForm open={open} onClose={() => setOpen(false)} onSaved={(c) => { reload(); setSelectedId(c.id); }} />
    </>
  );
}
