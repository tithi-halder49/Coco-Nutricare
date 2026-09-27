import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getMe, loginUser, registerUser, tokenStore } from "../services/api";

const AuthContext = createContext(null);

// URL slug <-> backend role
export const ROLE_FROM_SLUG = { parent: "parent", mother: "pregnant_mother", doctor: "doctor" };
export const HOME_BY_ROLE = { parent: "/parent", pregnant_mother: "/mother", doctor: "/doctor" };
export const ROLE_LABEL = { parent: "Parent", pregnant_mother: "Pregnant Mother", doctor: "Doctor" };

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  // Restore the session after a page refresh
  useEffect(() => {
    if (!tokenStore.get()) {
      setReady(true);
      return;
    }
    getMe()
      .then(setUser)
      .catch(() => tokenStore.clear())
      .finally(() => setReady(true));
  }, []);

  // api.js fires this event when any request returns 401
  useEffect(() => {
    const onLogout = () => setUser(null);
    window.addEventListener("coco:logout", onLogout);
    return () => window.removeEventListener("coco:logout", onLogout);
  }, []);

  const login = useCallback(async (email, password, role) => {
    const { user } = await loginUser(email, password, role);
    setUser(user);
    return user;
  }, []);

  const register = useCallback(async (payload) => {
    const { user } = await registerUser(payload);
    setUser(user);
    return user;
  }, []);

  const logout = useCallback(() => {
    tokenStore.clear();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, ready, login, register, logout }}>{children}</AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
