import { Link } from "react-router-dom";
import { Leaf, Stethoscope, User, Users } from "lucide-react";

const ROLES = [
  { slug: "parent", title: "Parent", text: "Manage your children's growth.", Icon: Users, cta: "Parent login" },
  { slug: "mother", title: "Pregnant Mother", text: "Track pregnancy nutrition and health.", Icon: User, cta: "Mother login" },
  { slug: "doctor", title: "Doctor", text: "Review patients and consultations.", Icon: Stethoscope, cta: "Doctor login" },
];

export default function Landing() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-coco-accent">
          <Leaf className="h-5 w-5" /> <span className="font-semibold">Coco NutriCare</span>
        </div>
        <Link to="/register" className="btn-orange">Get started</Link>
      </header>

      <section className="mt-8 rounded-2xl bg-coco-panel px-6 py-14 text-center">
        <h1 className="text-4xl font-bold leading-tight text-coco-accent sm:text-5xl">
          Smart Nutrition.<br />Healthy Growth.<br />Brighter Care.
        </h1>
        <p className="mx-auto mt-4 max-w-md text-coco-muted">
          Nutrition and health support for children and mothers, checked by doctors.
        </p>
      </section>

      <section className="mt-8 grid gap-4 sm:grid-cols-3" aria-label="Choose how you sign in">
        {ROLES.map(({ slug, title, text, Icon, cta }) => (
          <div key={slug} className="card text-center">
            <Icon className="mx-auto h-8 w-8 text-coco-orange" />
            <h2 className="mt-3 font-semibold text-white">{title}</h2>
            <p className="mt-1 text-sm text-coco-muted">{text}</p>
            <Link to={`/login/${slug}`} className="btn-ghost mt-4 w-full border-coco-accent text-coco-accent">
              {cta}
            </Link>
          </div>
        ))}
      </section>
    </div>
  );
}
