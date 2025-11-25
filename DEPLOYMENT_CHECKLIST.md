# Deployment Checklist

1. Install Python deps:

   ```powershell
   cd backend
   python -m venv .venv; .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

2. Start backend:

   ```powershell
   uvicorn app:app --host 127.0.0.1 --port 8000 --reload
   ```

3. Start frontend:

   ```powershell
   cd frontend
   npm install
   npm run electron:dev
   ```

4. Build Windows installer:

   ```powershell
   cd frontend
   npm run build
   npm run electron:package
   ```

5. Optional: bundle backend with PyInstaller

   ```powershell
   cd backend
   pip install pyinstaller
   pyinstaller --onefile app.py --add-data "data;data"
   ```

6. Optional: sign the installer with your code signing cert.
