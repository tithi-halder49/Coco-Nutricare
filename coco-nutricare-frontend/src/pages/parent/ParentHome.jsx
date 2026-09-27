import { getDashboard } from "../../services/api";
import { useLoad } from "../../hooks/useLoad";
import ChildrenList from "../../components/ChildrenList";
import { ErrorText, Loader, PageHeader, Stat } from "../../components/ui";

export default function ParentHome() {
  const { data: d, loading, error, reload } = useLoad(getDashboard);
  if (loading) return <Loader />;
  if (error) return <ErrorText error={error} />;

  return (
    <>
      <PageHeader title={d.greeting} subtitle="Here's your children's health overview." />
      <div className="mb-6 grid gap-3 sm:grid-cols-2">
        <Stat label="Children" value={d.children_count} />
        <Stat label="Growth" value={d.growth} tone={d.growth === "Healthy" ? "green" : "orange"} />
        <Stat label="Reminders" value={d.reminders} />
        <Stat label="Consultations" value={d.consultations} />
      </div>
      <ChildrenList kids={d.children} onAdded={reload} />
    </>
  );
}
