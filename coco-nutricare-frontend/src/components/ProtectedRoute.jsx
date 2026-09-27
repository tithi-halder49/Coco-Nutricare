import { Navigate } from "react-router-dom";
import { HOME_BY_ROLE, useAuth } from "../context/AuthContext";
import { Loader } from "./ui";

/** Only lets the given role through; other logged-in roles go to their own dashboard. */
export default function ProtectedRoute({ role, loginPath, children }) {
  const { user, ready } = useAuth();
  if (!ready) return <Loader />;
  if (!user) return <Navigate to={loginPath} replace />;
  if (user.role !== role) return <Navigate to={HOME_BY_ROLE[user.role]} replace />;
  return children;
}
