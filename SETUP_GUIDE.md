# Coco NutriCare – Step by step setup (Windows)

## 1. Ja install korte hobe (ekbar)
1. **Python 3.12** – python.org/downloads. Install er somoy **"Add python.exe to PATH"** tick dite hobe.
2. **Node.js (LTS)** – nodejs.org → LTS version download → Next, Next, Install.
3. **VS Code** – code.visualstudio.com.

Check: Command Prompt khule
```
python --version
node --version
npm --version
```
Tinta version dekhale thik ache.

## 2. Project khola
1. `coco-nutricare.zip` extract korun (right-click → Extract All), Desktop e rakhun.
2. VS Code khulun → File → Open Folder → `coco-nutricare` folder select korun.
3. Bhitore thakbe: `coco-nutricare-backend`, `coco-nutricare-frontend`, `jira-tasks.csv`, ei guide.

## 3. Backend chalano (Terminal 1)
VS Code e **Terminal → New Terminal**. Upore dane dropdown theke **Command Prompt** select korun (PowerShell na).
```
cd coco-nutricare-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
```
`Uvicorn running on http://127.0.0.1:8000` dekhale backend ready. Ei terminal bondho korben na.

## 4. Frontend chalano (Terminal 2)
Terminal panel e **+** chepe notun terminal khulun (Command Prompt).
```
cd coco-nutricare-frontend
npm install
npm run dev
```
`Local: http://localhost:5173/` dekhale browser e oi link open korun.

## 5. Test kora
| Role | Email | Password |
|---|---|---|
| Parent | parent@coco.app | password123 |
| Pregnant Mother | mother@coco.app | password123 |
| Doctor | doctor@coco.app | password123  |

Home page e Parent card e click → login → Parent dashboard. Log out kore Doctor diye login → Doctor dashboard. Mother er jonno same.

## 6. Porer bar chalate
Terminal 1: `cd coco-nutricare-backend` → `venv\Scripts\activate` → `uvicorn app.main:app --reload`
Terminal 2: `cd coco-nutricare-frontend` → `npm run dev`

## Common problems
- **"Cannot reach the server"** on login page → backend (Terminal 1) chalu nei.
- **'npm' is not recognized** → Node.js install er por VS Code bondho kore abar khulun.
- **activate e laal error** → terminal PowerShell e ache; Command Prompt select korun.
- Demo data reset korte: backend terminal e Ctrl+C → `python seed.py` → abar `uvicorn ...`.

## Jira te task import
Jira project → **⋯ / Settings → System → External System Import → CSV** (ba Filters menu te "Import issues from CSV") → `jira-tasks.csv` upload →
column mapping: Issue ID → Issue ID, Parent → Parent, Issue Type, Summary, Description, Priority, Story Points, Labels .
