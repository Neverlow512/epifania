#!/bin/bash

set -e

echo "=========================================="
echo "Epifania Environment Setup"
echo "=========================================="
echo ""

echo "[1/4] Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..
echo "Python virtual environment created and dependencies installed."
echo ""

echo "[2/4] Setting up Node.js environment..."
cd frontend
if command -v nvm &> /dev/null; then
    echo "Using nvm to manage Node.js version..."
    nvm install 20
    nvm use 20
else
    echo "nvm not found. Using system Node.js version."
fi
echo ""

echo "[3/4] Installing frontend dependencies..."
npm install
cd ..
echo "Frontend dependencies installed."
echo ""

echo "[4/4] Setup complete!"
echo ""
echo "=========================================="
echo "To start the application:"
echo "=========================================="
echo "Option 1: Use the launcher (recommended)"
echo "  python launcher.py"
echo ""
echo "Option 2: Run services manually"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo "=========================================="

