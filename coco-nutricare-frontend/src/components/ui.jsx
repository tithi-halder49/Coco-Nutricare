import { useEffect } from "react";
import { Loader2, X } from "lucide-react";

export function PageHeader({ title, subtitle, action }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-2xl font-semibold text-white">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-coco-muted">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function Stat({ label, value, tone = "white" }) {
  const color = { white: "text-white", green: "text-coco-accent", orange: "text-coco-orange" }[tone];
  return (
    <div className="card flex items-center justify-between py-4">
      <span className="text-sm font-medium text-coco-muted">{label}</span>
      <span className={`text-lg font-semibold ${color}`}>{value}</span>
    </div>
  );
}

const TONES = {
  green: "bg-coco-green/30 text-emerald-200",
  orange: "bg-coco-orange/20 text-orange-200",
  red: "bg-red-500/20 text-red-200",
  grey: "bg-white/10 text-coco-muted",
};
export const Badge = ({ tone = "green", children }) => (
  <span className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium ${TONES[tone]}`}>
    {children}
  </span>
);

export const Loader = () => (
  <div className="flex justify-center py-10 text-coco-muted" aria-label="Loading">
    <Loader2 className="h-6 w-6 animate-spin" />
  </div>
);

export const ErrorText = ({ error }) =>
  error ? (
    <p role="alert" className="rounded-lg border border-red-400/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">
      {error}
    </p>
  ) : null;

export const Empty = ({ children }) => (
  <div className="rounded-xl border border-dashed border-coco-line p-8 text-center text-sm text-coco-muted">
    {children}
  </div>
);

export function Modal({ open, onClose, title, children, wide = false }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={`max-h-[90vh] w-full overflow-y-auto rounded-2xl border border-coco-line bg-coco-panel p-6 ${
          wide ? "max-w-2xl" : "max-w-lg"
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">{title}</h2>
          <button onClick={onClose} className="rounded-lg p-1 text-coco-muted hover:bg-white/10" aria-label="Close">
            <X className="h-5 w-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function Field({ label, children }) {
  return (
    <label className="block">
      <span className="label">{label}</span>
      {children}
    </label>
  );
}

export const PLAN_STATUS = {
  pending_review: { tone: "orange", label: "Review before feeding" },
  approved: { tone: "green", label: "Approved by doctor" },
  rejected: { tone: "red", label: "Changes requested by doctor" },
};

export const CONSULT_TONE = { requested: "orange", accepted: "green", completed: "grey", cancelled: "red" };
