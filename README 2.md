# Oriun Desktop AI

Oriun Desktop AI is a hybrid online/offline desktop assistant for Windows. It bundles an Electron + React frontend with a Python + FastAPI backend for local model hosting, automation, memory, and tools.

This repo is a developer-focused scaffold and demo designed to run in Replit or a local Windows dev environment. It includes a minimal placeholder offline model so the app can run without huge downloads (for testing only).

See `installer/build_instructions.md` for step-by-step packaging guidance.

Security: this app can read and write files and run automation. Permissions and explicit user consent are required in the UI before any destructive actions. Read the Security & Privacy section in the README and `installer/build_instructions.md` before granting elevated permissions.

---

Project structure (top-level):

See the full tree in this repository. Files include frontend, backend, installer, samples, and tests.

Quickstart (dev):

1. Start the Python backend

   On Windows (PowerShell):

   ```powershell
   cd oriun-desktop/backend
   python -m venv .venv; .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   uvicorn app:app --host 127.0.0.1 --port 8000 --reload
   ```

2. Start the frontend (Electron + React dev)

   Open a separate terminal and:

   ```powershell
   cd oriun-desktop/frontend
   npm install
   npm run electron:dev
   ```

This will open the Electron app that talks to the backend over localhost.

For detailed packaging and Windows installer steps, see `installer/build_instructions.md`.

---

This README is a summary. For file-level documentation, see docstrings and inline comments.
