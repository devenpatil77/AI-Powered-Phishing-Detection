# Email Guardian — Next UI (React prototype)

This is a **new React/Vite frontend direction**, not another CSS skin over Streamlit. It has a dark security-console shell, sidebar navigation, scan workspace, threat-signal cards, activity table, responsive layout, and file validation.

## Run it
1. Install Node.js if it is not installed.
2. Extract this folder.
3. Open a terminal in this folder.
4. Run:
   ```bash
   npm install
   npm run dev
   ```
5. Open the local URL printed by Vite.

## Important integration note
This is currently a frontend prototype. The upload control validates `.eml`, `.txt`, and `.pdf` and the button demonstrates the scan workflow, but it does **not** call your existing Python phishing model yet. The recent activity rows are clearly labeled demo data. The next step is to expose the existing Python model through a FastAPI endpoint and connect this UI to that endpoint before using it for real predictions.
