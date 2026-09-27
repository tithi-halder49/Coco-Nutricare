import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
      <h1 className="text-2xl font-semibold text-white">This page doesn't exist</h1>
      <Link to="/" className="btn-orange">Go to the home page</Link>
    </div>
  );
}
