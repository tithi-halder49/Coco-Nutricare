import { useState } from "react";
import { Link } from "react-router-dom";
import { Plus } from "lucide-react";
import ChildForm from "./ChildForm";
import { Badge, Empty } from "./ui";

/** Child cards + "Add Child" button. `kids` items: {id, name, age, weight_kg, status?} */
export default function ChildrenList({ kids, onAdded }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="space-y-3">
      {kids.length === 0 && <Empty>No children added yet.</Empty>}
      {kids.map((k) => (
        <Link key={k.id} to={`/parent/children/${k.id}`} className="card block hover:border-coco-accent">
          <p className="font-semibold text-white">
            {k.name} <span className="ml-2 text-sm font-normal text-coco-muted">Age {k.age}{k.weight_kg ? `, ${k.weight_kg} kg` : ""}</span>
          </p>
          {k.status && (
            <div className="mt-2">
              <Badge tone={k.status === "Healthy" ? "green" : "orange"}>{k.status}</Badge>
            </div>
          )}
        </Link>
      ))}
      <button className="btn-orange w-full" onClick={() => setOpen(true)}>
        <Plus className="h-4 w-4" /> Add child
      </button>
      <ChildForm open={open} onClose={() => setOpen(false)} onSaved={onAdded} />
    </div>
  );
}
