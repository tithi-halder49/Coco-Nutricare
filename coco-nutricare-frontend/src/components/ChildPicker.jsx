import { useEffect } from "react";
import { getChildren } from "../services/api";
import { useLoad } from "../hooks/useLoad";
import { Empty, ErrorText, Loader } from "./ui";

/** Dropdown to choose one of the parent's children. Renders children(childId) once chosen. */
export default function ChildPicker({ value, onChange, children }) {
  const { data: kids, loading, error } = useLoad(getChildren);

  useEffect(() => {
    if (kids?.length && !value) onChange(kids[0].id);
  }, [kids, value, onChange]);

  if (loading) return <Loader />;
  if (error) return <ErrorText error={error} />;
  if (!kids.length) return <Empty>Add a child from the dashboard first.</Empty>;

  return (
    <div className="space-y-5">
      <div className="card">
        <label className="label" htmlFor="child-pick">Child</label>
        <select id="child-pick" className="input" value={value ?? ""} onChange={(e) => onChange(Number(e.target.value))}>
          {kids.map((k) => (
            <option key={k.id} value={k.id}>{k.name}, {k.age}</option>
          ))}
        </select>
      </div>
      {value && children(value)}
    </div>
  );
}
