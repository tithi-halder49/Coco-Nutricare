import { useState } from "react";
import { reviewPlan } from "../services/api";
import { ErrorText } from "./ui";

/** Doctor approves or rejects a nutrition plan. */
export default function PlanReview({ plan, onReviewed }) {
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async (approve) => {
    setBusy(true);
    setError("");
    try {
      onReviewed(await reviewPlan(plan.id, approve, note || null));
      setNote("");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card space-y-3">
      <h3 className="font-semibold text-white">Your review</h3>
      <textarea
        className="input min-h-20"
        placeholder="Note for the family (optional)"
        value={note}
        onChange={(e) => setNote(e.target.value)}
      />
      <ErrorText error={error} />
      <div className="flex gap-2">
        <button className="btn-green" disabled={busy} onClick={() => submit(true)}>Approve plan</button>
        <button className="btn-ghost" disabled={busy} onClick={() => submit(false)}>Request changes</button>
      </div>
    </div>
  );
}
