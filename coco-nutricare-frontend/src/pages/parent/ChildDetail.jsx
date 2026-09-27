import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { deleteChild, getChild } from "../../services/api";
import { useLoad } from "../../hooks/useLoad";
import { cap, fmtDate } from "../../utils";
import ChildForm from "../../components/ChildForm";
import DietPlanModal from "../../components/DietPlanModal";
import GrowthPanel from "../../components/GrowthPanel";
import ChildPlanCard from "../../components/ChildPlanCard";
import { ErrorText, Loader, PageHeader } from "../../components/ui";

const Section = ({ title, rows }) => (
  <div className="card">
    <h3 className="mb-2 font-semibold text-white">{title}</h3>
    {rows.map(([k, v]) => (
      <div className="row" key={k}>
        <span className="text-coco-muted">{k}</span>
        <span className="text-right font-medium text-white">{v || "None"}</span>
      </div>
    ))}
  </div>
);

const TABS = ["Profile", "Growth", "Nutrition plan"];

export default function ChildDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: c, loading, error, setData } = useLoad(() => getChild(id), [id]);
  const [tab, setTab] = useState(TABS[0]);
  const [editing, setEditing] = useState(false);
  const [dietOpen, setDietOpen] = useState(false);

  if (loading) return <Loader />;
  if (error) return <ErrorText error={error} />;

  const remove = async () => {
    if (!window.confirm(`Delete ${c.name}'s profile and all records?`)) return;
    await deleteChild(c.id);
    navigate("/parent/children");
  };

  return (
    <>
      <p className="mb-2 text-sm text-coco-muted">
        <Link to="/parent/children" className="hover:text-white">My children</Link> / {c.name.split(" ")[0]}
      </p>
      <PageHeader
        title={c.name}
        action={
          <button className="btn-orange" onClick={() => setDietOpen(true)}>
            <Sparkles className="h-4 w-4" /> Quick diet check
          </button>
        }
      />
      <div className="mb-5 flex gap-2">
        {TABS.map((t) => (
          <button key={t} className={`chip ${tab === t ? "chip-on" : ""}`} onClick={() => setTab(t)}>{t}</button>
        ))}
      </div>

      {tab === "Profile" && (
        <div className="space-y-4">
          <Section title="Basic information" rows={[["Date of birth", fmtDate(c.date_of_birth)], ["Gender", cap(c.gender)], ["Age", c.age]]} />
          <Section title="Physical information" rows={[["Height", c.height_cm && `${c.height_cm} cm`], ["Weight", c.weight_kg && `${c.weight_kg} kg`]]} />
          <Section title="Allergy information" rows={[["Food allergies", c.food_allergies.join(", ")], ["Medicine allergies", c.medicine_allergies.join(", ")]]} />
          <Section title="Dietary habits" rows={[["Preferences", c.dietary_habits], ["Medical conditions", c.medical_conditions]]} />
          <div className="flex gap-2">
            <button className="btn-green flex-1" onClick={() => setEditing(true)}>Edit profile</button>
            <button className="btn-ghost" onClick={remove}>Delete</button>
          </div>
        </div>
      )}
      {tab === "Growth" && <GrowthPanel childId={c.id} canEdit />}
      {tab === "Nutrition plan" && <ChildPlanCard childId={c.id} canGenerate />}

      {editing && <ChildForm key={c.id} open child={c} onClose={() => setEditing(false)} onSaved={setData} />}
      {dietOpen && <DietPlanModal open child={c} onClose={() => setDietOpen(false)} />}
    </>
  );
}
