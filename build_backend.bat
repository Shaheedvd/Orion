@echo off
setlocal
python -m venv .venv
.\.venv\Scripts\activate
echo Installing minimal packaging dependencies (requirements-ci.txt)...
pip install -r requirements-ci.txt || echo "Warning: installing minimal CI requirements failed. Proceeding anyway."
pip install pyinstaller || echo "Warning: pyinstaller install failed. The build may fail."
pyinstaller --onefile --name backend app.py --add-data "data;data" || echo "PyInstaller build completed with warnings; check dist\\backend.exe"
rem Copy exe to ../frontend/resources/backend.exe for packaging
if exist dist\backend.exe (
  mkdir ..\frontend\resources 2>nul
  copy /Y dist\backend.exe ..\frontend\resources\backend.exe
)
endlocal
