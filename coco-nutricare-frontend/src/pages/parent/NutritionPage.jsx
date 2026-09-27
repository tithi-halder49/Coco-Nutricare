import { useState } from "react";
import ChildPicker from "../../components/ChildPicker";
import ChildPlanCard from "../../components/ChildPlanCard";
import { PageHeader } from "../../components/ui";

export default function NutritionPage() {
  const [childId, setChildId] = useState(null);
  return (
    <>
      <PageHeader title="Nutrition plan" subtitle="Plans are filtered for allergies and checked by a doctor." />
      <ChildPicker value={childId} onChange={setChildId}>
        {(id) => <ChildPlanCard key={id} childId={id} canGenerate />}
      </ChildPicker>
    </>
  );
}
