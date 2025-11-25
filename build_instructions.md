# Build instructions for Oriun Desktop AI

This document describes how to run the project in development, test the minimal demo on Replit, and package an installer for Windows.

Prerequisites
- Node.js (16+), npm
- Python 3.10+
- git
- Optional: Visual Studio Build Tools for building native deps

Dev run (Replit-friendly minimal flow)

1. Backend

   - Create a virtualenv and install dependencies:

     ```powershell
     cd backend
     python -m venv .venv; .\.venv\Scripts\Activate.ps1
     python -m pip install -r requirements.txt
     uvicorn app:app --host 127.0.0.1 --port 8000 --reload
     ```

   - Note: some heavy packages like faiss-cpu or whisper may not install on Replit without build tools. For Replit use, comment them out in `requirements.txt` or rely on the local stub behavior.

2. Frontend

   - Install node deps and run dev Electron:

     ```powershell
     cd frontend
     npm install
     npm run electron:dev
     ```

3. Packaging for Windows

   - Build frontend bundle and package with electron-builder:

     ```powershell
     cd frontend
     npm run build
     npm run electron:package
     ```

   - Bundle backend into an executable/service (optional):

     ```powershell
     cd backend
     pip install pyinstaller
     pyinstaller --onefile app.py --add-data "data;data"
     ```

   - Combine the backend executable into the Electron resources folder before packaging so the installer drops both frontend and backend runtimes.
    - After building the backend with PyInstaller, copy the produced `backend.exe` into `frontend/resources/backend.exe` so the Electron packaged app can spawn it at runtime. The `frontend/electron-main.js` will try to spawn `backend.exe` from the application resources.

  Signing (optional):
  - To sign the installer, use signtool.exe with your code signing certificate after the electron-builder step. For CI, set up secure storage for your code signing key.

Notes & TODOs
- For full offline GGUF models, follow the instructions in `backend/models/README_models.txt` and obtain models from the official sources. Large models require significant disk and memory.
