import { useState } from "react";
import { Sparkles } from "lucide-react";
import { generateChildPlan, getChildPlan } from "../services/api";
import { orNull, useLoad } from "../hooks/useLoad";
import PlanView from "./PlanView";
import PlanReview from "./PlanReview";
import { Empty, ErrorText, Loader } from "./ui";

/** Saved nutrition plan for one child. Parents can generate, doctors can review. */
export default function ChildPlanCard({ childId, canGenerate = false, canReview = false }) {
  const { data: plan, loading, error, setData } = useLoad(() => orNull(getChildPlan(childId)), [childId]);
  const [busy, setBusy] = useState(false);
  const [genError, setGenError] = useState("");

  const generate = async () => {
    setBusy(true);
    setGenError("");
    try {
      setData(await generateChildPlan(childId));
    } catch (e) {
      setGenError(e.message);
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <Loader />;
  return (
    <div className="space-y-4">
      <ErrorText error={error || genError} />
      {canGenerate && (
        <button className="btn-orange" onClick={generate} disabled={busy}>
          <Sparkles className="h-4 w-4" /> {plan ? "Create a new plan" : "Create nutrition plan"}
        </button>
      )}
      {plan ? <PlanView plan={plan} /> : <Empty>No nutrition plan yet.</Empty>}
      {plan && canReview && plan.status === "pending_review" && <PlanReview plan={plan} onReviewed={setData} />}
    </div>
  );
}
