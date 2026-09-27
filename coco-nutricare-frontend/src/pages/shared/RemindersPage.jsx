import { useState } from "react";
import { Plus, Syringe, Pill, Bell } from "lucide-react";
import { completeReminder, createReminder, getChildren, getReminders, snoozeReminder } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { useLoad } from "../../hooks/useLoad";
import { dueLabel } from "../../utils";
import { Empty, ErrorText, Field, Loader, Modal, PageHeader } from "../../components/ui";

const FILTERS = [["", "All"], ["vaccination", "Vaccination"], ["medicine", "Medicine"]];
const ICON = { vaccination: Syringe, medicine: Pill, other: Bell };

function NewReminder({ open, onClose, onSaved }) {
  const { user } = useAuth();
  const kids = useLoad(() => (user.role === "parent" ? getChildren() : Promise.resolve([])));
  const [form, setForm] = useState({ title: "", type: "vaccination", due_at: "", child_id: "" });
  const [error, setError] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    try {
      await createReminder({ ...form, child_id: form.child_id ? Number(form.child_id) : null });
      setForm({ title: "", type: "vaccination", due_at: "", child_id: "" });
      onSaved();
      onClose();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="New reminder">
      <form onSubmit={submit} className="space-y-3">
        <Field label="Title"><input className="input" required placeholder="MMR vaccine" value={form.title} onChange={set("title")} /></Field>
        <Field label="Type">
          <select className="input" value={form.type} onChange={set("type")}>
            <option value="vaccination">Vaccination</option>
            <option value="medicine">Medicine</option>
            <option value="other">Other</option>
          </select>
        </Field>
        <Field label="Date and time"><input type="datetime-local" className="input" required value={form.due_at} onChange={set("due_at")} /></Field>
        {kids.data?.length > 0 && (
          <Field label="Child (optional)">
            <select className="input" value={form.child_id} onChange={set("child_id")}>
              <option value="">None</option>
              {kids.data.map((k) => <option key={k.id} value={k.id}>{k.name}</option>)}
            </select>
          </Field>
        )}
        <ErrorText error={error} />
        <button className="btn-orange w-full">Save reminder</button>
      </form>
    </Modal>
  );
}

export default function RemindersPage() {
  const [type, setType] = useState("");
  const [open, setOpen] = useState(false);
  const { data, loading, error, reload } = useLoad(() => getReminders(type), [type]);
  const [actionError, setActionError] = useState("");

  const act = async (fn) => {
    try {
      await fn();
      reload();
    } catch (e) {
      setActionError(e.message);
    }
  };

  return (
    <>
      <PageHeader title="Reminders" action={<button className="btn-orange" onClick={() => setOpen(true)}><Plus className="h-4 w-4" /> New reminder</button>} />
      <div className="mb-4 flex gap-2">
        {FILTERS.map(([v, label]) => (
          <button key={label} className={`chip ${type === v ? "chip-on" : ""}`} onClick={() => setType(v)}>{label}</button>
        ))}
      </div>
      <ErrorText error={error || actionError} />
      {loading ? <Loader /> : data?.length === 0 ? <Empty>Nothing due. Add a vaccination or medicine reminder.</Empty> : (
        <div className="space-y-3">
          {data?.map((r) => {
            const Icon = ICON[r.type];
            return (
              <div key={r.id} className="card">
                <div className="flex items-start justify-between gap-3">
                  <p className="flex items-center gap-2 text-sm text-slate-200"><Icon className="h-4 w-4 text-coco-orange" /> {r.title}</p>
                  <p className={`text-sm font-semibold ${dueLabel(r.due_at) === "Overdue" ? "text-orange-300" : "text-white"}`}>{dueLabel(r.due_at)}</p>
                </div>
                <div className="mt-3 flex gap-2">
                  <button className="chip" onClick={() => act(() => completeReminder(r.id))}>Mark done</button>
                  <button className="chip" onClick={() => act(() => snoozeReminder(r.id, 60))}>Snooze 1 hour</button>
                </div>
              </div>
            );
          })}
        </div>
      )}
      <NewReminder open={open} onClose={() => setOpen(false)} onSaved={reload} />
    </>
  );
}
