import { useState } from "react";
import ChildPicker from "../../components/ChildPicker";
import GrowthPanel from "../../components/GrowthPanel";
import { PageHeader } from "../../components/ui";

export default function GrowthPage() {
  const [childId, setChildId] = useState(null);
  return (
    <>
      <PageHeader title="Growth tracking" />
      <ChildPicker value={childId} onChange={setChildId}>
        {(id) => <GrowthPanel key={id} childId={id} canEdit />}
      </ChildPicker>
    </>
  );
}
