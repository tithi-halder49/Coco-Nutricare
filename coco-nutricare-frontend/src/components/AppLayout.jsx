import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  AlarmClock, Baby, HeartPulse, LayoutDashboard, Leaf, LineChart, LogOut, MessagesSquare, Salad,
} from "lucide-react";
import { ROLE_LABEL, useAuth } from "../context/AuthContext";

const NAV = {
  parent: [
    ["/parent", "Dashboard", LayoutDashboard],
    ["/parent/children", "My Children", Baby],
    ["/parent/nutrition", "Nutrition Plan", Salad],
    ["/parent/growth", "Growth Tracking", LineChart],
    ["/parent/reminders", "Reminders", AlarmClock],
    ["/parent/consultations", "Consultations", MessagesSquare],
  ],
  pregnant_mother: [
    ["/mother", "Dashboard", LayoutDashboard],
    ["/mother/symptoms", "Symptoms", HeartPulse],
    ["/mother/nutrition", "Nutrition Plan", Salad],
    ["/mother/reminders", "Reminders", AlarmClock],
    ["/mother/consultations", "Consultations", MessagesSquare],
  ],
  doctor: [["/doctor", "Consultations", MessagesSquare]],
};

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const items = NAV[user.role];

  const signOut = () => {
    logout();
    navigate("/", { replace: true });
  };

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="flex shrink-0 flex-col bg-coco-side md:w-60 md:min-h-screen">
        <div className="flex items-center gap-2 px-5 py-5">
          <Leaf className="h-5 w-5 text-coco-orange" />
          <span className="font-semibold text-white">Coco NutriCare</span>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-3 md:flex-1 md:flex-col md:overflow-visible">
          {items.map(([to, label, Icon]) => (
            <NavLink
              key={to}
              to={to}
              end={to.split("/").length === 2}
              className={({ isActive }) =>
                `flex shrink-0 items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium ${
                  isActive ? "bg-coco-mint text-coco-side" : "text-slate-100 hover:bg-white/10"
                }`
              }
            >
              <Icon className="h-4 w-4 text-coco-orange" /> {label}
            </NavLink>
          ))}
        </nav>
        <div className="hidden border-t border-white/10 px-5 py-4 md:block">
          <p className="text-sm font-medium text-white">{user.full_name}</p>
          <p className="text-xs text-coco-mint/70">{ROLE_LABEL[user.role]}</p>
          <button onClick={signOut} className="mt-3 flex items-center gap-2 text-sm text-coco-mint hover:text-white">
            <LogOut className="h-4 w-4" /> Log out
          </button>
        </div>
        <button onClick={signOut} className="mx-3 mb-3 flex items-center gap-2 text-sm text-coco-mint md:hidden">
          <LogOut className="h-4 w-4" /> Log out
        </button>
      </aside>
      <main className="flex-1 px-4 py-6 md:px-10 md:py-8">
        <div className="mx-auto max-w-4xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
