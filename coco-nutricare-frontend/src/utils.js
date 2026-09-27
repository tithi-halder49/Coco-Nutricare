export const splitList = (text) =>
  (text || "").split(",").map((s) => s.trim()).filter(Boolean);

export const ageMonthsFromDob = (dob) => {
  const d = new Date(dob);
  const now = new Date();
  let m = (now.getFullYear() - d.getFullYear()) * 12 + (now.getMonth() - d.getMonth());
  if (now.getDate() < d.getDate()) m -= 1;
  return Math.max(m, 0);
};

const startOfDay = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());

/** "Today, 8:00 PM" / "Tomorrow, 9:00 AM" / "Due in 3 days" / "Overdue" */
export function dueLabel(iso) {
  const d = new Date(iso);
  const now = new Date();
  const days = Math.round((startOfDay(d) - startOfDay(now)) / 86400000);
  const time = d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  if (d < now) return "Overdue";
  if (days === 0) return `Today, ${time}`;
  if (days === 1) return `Tomorrow, ${time}`;
  return `Due in ${days} days`;
}

export const fmtDate = (iso) =>
  new Date(iso).toLocaleDateString([], { day: "numeric", month: "short", year: "numeric" });

export const fmtDateTime = (iso) =>
  new Date(iso).toLocaleString([], { day: "numeric", month: "short", hour: "numeric", minute: "2-digit" });

export const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1).replaceAll("_", " ") : "");
