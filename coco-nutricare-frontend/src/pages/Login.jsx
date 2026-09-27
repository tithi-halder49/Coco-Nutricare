import { useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
import { Leaf } from "lucide-react";
import { HOME_BY_ROLE, ROLE_FROM_SLUG, ROLE_LABEL, useAuth } from "../context/AuthContext";
import { ErrorText, Field } from "../components/ui";

const DEMO = { parent: "parent@coco.app", mother: "mother@coco.app", doctor: "doctor@coco.app" };

/** One login page for all roles: /login/parent, /login/mother, /login/doctor */
export default function Login() {
  const { roleSlug } = useParams();
  const role = ROLE_FROM_SLUG[roleSlug];
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (!role) return <Navigate to="/" replace />;
  if (user) return <Navigate to={HOME_BY_ROLE[user.role]} replace />;

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const u = await login(email, password, role);
      navigate(HOME_BY_ROLE[u.role], { replace: true }); // parent -> /parent, doctor -> /doctor ...
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <form onSubmit={submit} className="w-full max-w-sm space-y-4 rounded-2xl bg-coco-panel p-8">
        <Leaf className="mx-auto h-8 w-8 text-coco-accent" />
        <h1 className="text-center text-xl font-semibold text-coco-accent">Welcome back, {ROLE_LABEL[role]}!</h1>
        <Field label="Email">
          <input type="email" className="input" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </Field>
        <Field label="Password">
          <input type="password" className="input" required autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <ErrorText error={error} />
        <button className="btn-green w-full" disabled={busy}>{busy ? "Logging in..." : "Log in"}</button>
        <p className="text-center text-sm text-coco-muted">
          Don't have an account?{" "}
          <Link to={`/register?role=${role}`} className="text-coco-accent hover:underline">Create account</Link>
        </p>
        <p className="rounded-lg bg-white/5 px-3 py-2 text-center text-xs text-coco-muted">
          Demo: {DEMO[roleSlug]} / password123
        </p>
        <Link to="/" className="block text-center text-xs text-coco-muted hover:text-white">Choose a different role</Link>
      </form>
    </div>
  );
}
