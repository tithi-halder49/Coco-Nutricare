/**
 * Coco NutriCare API service layer.
 * Every backend call goes through `request()`, so auth headers, JSON parsing
 * and error messages are handled in one place.
 */

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const TOKEN_KEY = "coco_token";

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

/** Error with the HTTP status attached (0 = server not reachable). */
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

// FastAPI returns {detail: "text"} or {detail: [{loc, msg}, ...]} for validation errors.
function readError(body, status) {
  const detail = body?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((e) => `${e.loc?.[e.loc.length - 1] ?? "field"}: ${e.msg}`).join(", ");
  }
  return `Request failed (${status})`;
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = tokenStore.get();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(`Cannot reach the server at ${BASE_URL}. Start the backend and try again.`, 0);
  }

  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    if (res.status === 401 && auth) {
      tokenStore.clear();
      window.dispatchEvent(new Event("coco:logout")); // AuthContext listens and signs out
    }
    throw new ApiError(readError(data, res.status), res.status);
  }
  return data;
}

const qs = (params) => {
  const clean = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
  );
  const s = new URLSearchParams(clean).toString();
  return s ? `?${s}` : "";
};

// ---------- Auth ----------
/** role: "parent" | "pregnant_mother" | "doctor" */
export async function loginUser(email, password, role) {
  const data = await request("/api/auth/login", { method: "POST", body: { email, password, role }, auth: false });
  tokenStore.set(data.access_token);
  return data; // { access_token, token_type, user }
}

export async function registerUser(payload) {
  const data = await request("/api/auth/register", { method: "POST", body: payload, auth: false });
  tokenStore.set(data.access_token);
  return data;
}

export const getMe = () => request("/api/auth/me");
export const getDashboard = () => request("/api/dashboard");

// ---------- Children ----------
export const getChildren = () => request("/api/children");
export const getChild = (id) => request(`/api/children/${id}`);
export const addChild = (child) => request("/api/children", { method: "POST", body: child });
export const updateChild = (id, changes) => request(`/api/children/${id}`, { method: "PATCH", body: changes });
export const deleteChild = (id) => request(`/api/children/${id}`, { method: "DELETE" });

// ---------- Growth ----------
export const getGrowth = (childId) => request(`/api/children/${childId}/growth`);
export const addMeasurement = (childId, m) =>
  request(`/api/children/${childId}/growth/measurements`, { method: "POST", body: m });

// ---------- Nutrition ----------
/** Stateless calculator: { age_months, gender, weight_kg, height_cm, allergies[], dietary_habits } */
export const getDietPlan = (metrics) => request("/api/diet-plan", { method: "POST", body: metrics });
export const getChildPlan = (childId) => request(`/api/children/${childId}/nutrition-plan`);
export const generateChildPlan = (childId) =>
  request(`/api/children/${childId}/nutrition-plan`, { method: "POST" });
export const reviewPlan = (planId, approve, note) =>
  request(`/api/nutrition-plans/${planId}/review`, { method: "POST", body: { approve, note } });

// ---------- Pregnancy ----------
export const getPregnancy = () => request("/api/pregnancy");
export const savePregnancy = (profile) => request("/api/pregnancy", { method: "PUT", body: profile });
export const getPregnancyPlan = () => request("/api/pregnancy/nutrition-plan");
export const generatePregnancyPlan = () => request("/api/pregnancy/nutrition-plan", { method: "POST" });
export const getSymptomOptions = () => request("/api/pregnancy/symptom-options");
export const getSymptoms = () => request("/api/pregnancy/symptoms");
export const logSymptoms = (entry) => request("/api/pregnancy/symptoms", { method: "POST", body: entry });
export const getPatientPregnancy = (patientId) => request(`/api/pregnancy/patient/${patientId}`);

// ---------- Reminders ----------
export const getReminders = (type) => request(`/api/reminders${qs({ type })}`);
export const createReminder = (r) => request("/api/reminders", { method: "POST", body: r });
export const completeReminder = (id) => request(`/api/reminders/${id}/complete`, { method: "POST" });
export const snoozeReminder = (id, minutes = 60) =>
  request(`/api/reminders/${id}/snooze`, { method: "POST", body: { minutes } });
export const deleteReminder = (id) => request(`/api/reminders/${id}`, { method: "DELETE" });

// ---------- Consultations & chat ----------
export const getDoctors = () => request("/api/doctors");
export const getConsultations = (status) => request(`/api/consultations${qs({ status })}`);
export const getConsultation = (id) => request(`/api/consultations/${id}`);
export const requestConsultation = (c) => request("/api/consultations", { method: "POST", body: c });
export const updateConsultation = (id, changes) =>
  request(`/api/consultations/${id}`, { method: "PATCH", body: changes });
export const getMessages = (id, afterId = 0) =>
  request(`/api/consultations/${id}/messages${qs({ after_id: afterId })}`);
export const sendMessage = (id, text) =>
  request(`/api/consultations/${id}/messages`, { method: "POST", body: { text } });
