import { Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import NotFound from "./pages/NotFound";
import ParentHome from "./pages/parent/ParentHome";
import ChildrenPage from "./pages/parent/ChildrenPage";
import ChildDetail from "./pages/parent/ChildDetail";
import NutritionPage from "./pages/parent/NutritionPage";
import GrowthPage from "./pages/parent/GrowthPage";
import MotherHome from "./pages/mother/MotherHome";
import SymptomsPage from "./pages/mother/SymptomsPage";
import MotherNutrition from "./pages/mother/MotherNutrition";
import DoctorHome from "./pages/doctor/DoctorHome";
import DoctorConsultation from "./pages/doctor/DoctorConsultation";
import RemindersPage from "./pages/shared/RemindersPage";
import ConsultationsPage from "./pages/shared/ConsultationsPage";

const guard = (role, slug) => (
  <ProtectedRoute role={role} loginPath={`/login/${slug}`}>
    <AppLayout />
  </ProtectedRoute>
);

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login/:roleSlug" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route path="/parent" element={guard("parent", "parent")}>
        <Route index element={<ParentHome />} />
        <Route path="children" element={<ChildrenPage />} />
        <Route path="children/:id" element={<ChildDetail />} />
        <Route path="nutrition" element={<NutritionPage />} />
        <Route path="growth" element={<GrowthPage />} />
        <Route path="reminders" element={<RemindersPage />} />
        <Route path="consultations" element={<ConsultationsPage />} />
      </Route>

      <Route path="/mother" element={guard("pregnant_mother", "mother")}>
        <Route index element={<MotherHome />} />
        <Route path="symptoms" element={<SymptomsPage />} />
        <Route path="nutrition" element={<MotherNutrition />} />
        <Route path="reminders" element={<RemindersPage />} />
        <Route path="consultations" element={<ConsultationsPage />} />
      </Route>

      <Route path="/doctor" element={guard("doctor", "doctor")}>
        <Route index element={<DoctorHome />} />
        <Route path="consultations/:id" element={<DoctorConsultation />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
