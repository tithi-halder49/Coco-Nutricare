import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { HOME_BY_ROLE, ROLE_LABEL, useAuth } from "../context/AuthContext";
import { ErrorText, Field } from "../components/ui";

const ROLES = ["parent", "doctor", "pregnant_mother"];
const SLUG = { parent: "parent", doctor: "doctor", pregnant_mother: "mother" };

export default function Register() {
  const [params] = useSearchParams();
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    role: ROLES.includes(params.get("role")) ? params.get("role") : "parent",
    full_name: "", email: "", phone: "", password: "", specialization: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const u = await register({
        ...form,
        phone: form.phone || null,
        specialization: form.role === "doctor" ? form.specialization || null : null,
      });
      navigate(HOME_BY_ROLE[u.role], { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-8">
      <form onSubmit={submit} className="w-full max-w-md space-y-4 rounded-2xl bg-coco-panel p-8">
        <h1 className="text-3xl font-bold text-white">Create account</h1>
        <p className="text-sm text-coco-muted">Choose your role to get started</p>
        <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Role">
          {ROLES.map((r) => (
            <button type="button" key={r} role="radio" aria-checked={form.role === r}
              onClick={() => setForm({ ...form, role: r })}
              className={`rounded-full px-4 py-2 text-sm font-semibold ${form.role === r ? "bg-coco-orange text-white" : "bg-white text-slate-900"}`}>
              {ROLE_LABEL[r]}
            </button>
          ))}
        </div>
        <Field label="Full name"><input className="input" required placeholder="Nadia Rahman" value={form.full_name} onChange={set("full_name")} /></Field>
        <Field label="Email address"><input type="email" className="input" required placeholder="you@example.com" value={form.email} onChange={set("email")} /></Field>
        <Field label="Phone number"><input className="input" placeholder="+880 1XXX-XXXXXX" value={form.phone} onChange={set("phone")} /></Field>
        {form.role === "doctor" && (
          <Field label="Specialization"><input className="input" placeholder="Pediatrics" value={form.specialization} onChange={set("specialization")} /></Field>
        )}
        <Field label="Password"><input type="password" className="input" required minLength={6} maxLength={72} placeholder="At least 6 characters" value={form.password} onChange={set("password")} /></Field>
        <ErrorText error={error} />
        <button className="btn-orange w-full" disabled={busy}>{busy ? "Creating..." : "Create account"}</button>
        <p className="text-center text-sm text-coco-muted">
          Already have an account?{" "}
          <Link to={`/login/${SLUG[form.role]}`} className="font-semibold text-coco-orange">Log in</Link>
        </p>
      </form>
    </div>
  );
}
