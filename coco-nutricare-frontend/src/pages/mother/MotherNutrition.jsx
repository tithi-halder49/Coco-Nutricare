import { useState } from "react";
import { Link } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { generatePregnancyPlan, getPregnancy, getPregnancyPlan } from "../../services/api";
import { orNull, useLoad } from "../../hooks/useLoad";
import PlanView from "../../components/PlanView";
import { Empty, ErrorText, Loader, PageHeader } from "../../components/ui";

export default function MotherNutrition() {
  const profile = useLoad(() => orNull(getPregnancy()));
  const plan = useLoad(() => orNull(getPregnancyPlan()));
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const generate = async () => {
    setBusy(true);
    setError("");
    try {
      plan.setData(await generatePregnancyPlan());
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  if (profile.loading || plan.loading) return <Loader />;
  if (!profile.data) {
    return <Empty>Fill in your pregnancy profile on the <Link to="/mother" className="text-coco-accent underline">dashboard</Link> first.</Empty>;
  }

  return (
    <>
      <PageHeader title="Nutrition plan" subtitle={`Week ${profile.data.week}, trimester ${profile.data.trimester}`}
        action={<button className="btn-orange" onClick={generate} disabled={busy}><Sparkles className="h-4 w-4" /> {plan.data ? "Create a new plan" : "Create my plan"}</button>} />
      <ErrorText error={error || plan.error} />
      {plan.data ? <PlanView plan={plan.data} /> : <Empty>No plan yet. Create one for your current trimester.</Empty>}
    </>
  );
}
