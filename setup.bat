@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Epifania Environment Setup
echo ==========================================
echo.

echo [1/4] Setting up Python virtual environment...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
call venv\Scripts\deactivate.bat
cd ..
echo Python virtual environment created and dependencies installed.
echo.

echo [2/4] Node.js environment check...
cd frontend
echo Using system Node.js version.
echo.

echo [3/4] Installing frontend dependencies...
call npm install
cd ..
echo Frontend dependencies installed.
echo.

echo [4/4] Setup complete!
echo.
echo ==========================================
echo To start the application:
echo ==========================================
echo Option 1: Use the launcher (recommended)
echo   python launcher.py
echo.
echo Option 2: Run services manually
echo   Backend:  cd backend ^&^& venv\Scripts\activate ^&^& uvicorn main:app --reload
echo   Frontend: cd frontend ^&^& npm run dev
echo ==========================================
pause

