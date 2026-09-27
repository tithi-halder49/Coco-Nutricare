# Coco NutriCare – Frontend (React + Vite + Tailwind)

```bash
npm install
npm run dev        # http://localhost:5173
```
The backend must be running on http://127.0.0.1:8000 (change it in `.env` with `VITE_API_URL`).

## Structure
```
src/
  services/api.js        all backend calls (loginUser, getChildren, addChild, getDietPlan, ...)
  context/AuthContext    logged-in user, login/register/logout
  components/            UI pieces (modals, plan view, growth panel, chat, layout, route guard)
  pages/                 Landing, Login (/login/:role), Register
    parent/  mother/  doctor/  shared/
```

## Role flow
`/` → choose role → `/login/parent | mother | doctor` → dashboard `/parent`, `/mother`, `/doctor`.
Each dashboard is protected: a parent who opens `/doctor` is sent back to `/parent`.
