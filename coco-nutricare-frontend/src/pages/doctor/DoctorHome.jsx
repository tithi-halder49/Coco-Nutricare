import { useState } from "react";
import { Link } from "react-router-dom";
import { getConsultations, getDashboard, updateConsultation } from "../../services/api";
import { useLoad } from "../../hooks/useLoad";
import { cap, fmtDateTime } from "../../utils";
import { Badge, CONSULT_TONE, Empty, ErrorText, Loader, PageHeader, Stat } from "../../components/ui";

const FILTERS = [["", "All"], ["requested", "New requests"], ["accepted", "Accepted"], ["completed", "Completed"]];

export default function DoctorHome() {
  const dash = useLoad(getDashboard);
  const [status, setStatus] = useState("");
  const list = useLoad(() => getConsultations(status), [status]);
  const [error, setError] = useState("");

  const setStatusOf = async (c, s) => {
    try {
      await updateConsultation(c.id, { status: s });
      list.reload();
      dash.reload();
    } catch (e) {
      setError(e.message);
    }
  };

  if (dash.loading) return <Loader />;
  return (
    <>
      <PageHeader title={dash.data?.greeting ?? "Welcome"} subtitle="Your patients and consultation requests." />
      <div className="mb-6 grid gap-3 sm:grid-cols-3">
        <Stat label="New requests" value={dash.data?.pending_requests ?? 0} tone="orange" />
        <Stat label="Accepted" value={dash.data?.upcoming ?? 0} tone="green" />
        <Stat label="Patients" value={dash.data?.patients ?? 0} />
      </div>
      <div className="mb-4 flex flex-wrap gap-2">
        {FILTERS.map(([v, label]) => (
          <button key={label} className={`chip ${status === v ? "chip-on" : ""}`} onClick={() => setStatus(v)}>{label}</button>
        ))}
      </div>
      <ErrorText error={error || list.error || dash.error} />
      {list.loading ? <Loader /> : list.data?.length === 0 ? <Empty>No consultations here.</Empty> : (
        <div className="space-y-3">
          {list.data?.map((c) => (
            <div key={c.id} className="card">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <Link to={`/doctor/consultations/${c.id}`} className="font-semibold text-white hover:text-coco-accent">
                  {c.patient_name} {c.child_name && <span className="font-normal text-coco-muted">for {c.child_name}</span>}
                </Link>
                <Badge tone={CONSULT_TONE[c.status]}>{cap(c.status)}</Badge>
              </div>
              <p className="mt-1 text-sm text-slate-300">{c.reason}</p>
              <p className="mt-1 text-xs text-coco-muted">Requested {fmtDateTime(c.created_at)}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                <Link to={`/doctor/consultations/${c.id}`} className="btn-green btn-sm">Open</Link>
                {c.status === "requested" && <button className="btn-ghost btn-sm" onClick={() => setStatusOf(c, "accepted")}>Accept</button>}
                {c.status === "accepted" && <button className="btn-ghost btn-sm" onClick={() => setStatusOf(c, "completed")}>Mark completed</button>}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
