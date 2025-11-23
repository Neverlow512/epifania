#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

cleanup() {
    echo ""
    echo "[Epifania] Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "[Epifania] All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "=========================================="
echo "Starting Epifania"
echo "=========================================="
echo ""

if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "[Error] Virtual environment not found at $BACKEND_DIR/venv"
    echo "[Error] Run ./setup.sh first"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "[Error] Node modules not found at $FRONTEND_DIR/node_modules"
    echo "[Error] Run ./setup.sh first"
    exit 1
fi

echo "[Backend] Starting FastAPI on http://127.0.0.1:8000"
cd "$BACKEND_DIR"
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000 > "$PROJECT_ROOT/logs/server/uvicorn.log" 2>&1 &
BACKEND_PID=$!
deactivate
cd "$PROJECT_ROOT"

echo "[Backend] Waiting for backend to be ready..."
for i in {1..30}; do
    if curl --max-time 2 -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "[Backend] Backend is ready"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "[Backend] Warning: Backend may not be ready yet"
    fi
done

echo "[Frontend] Starting Vite dev server on http://127.0.0.1:5173"
cd "$FRONTEND_DIR"
npm run dev > "$PROJECT_ROOT/logs/server/vite.log" 2>&1 &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

sleep 2

echo ""
echo "=========================================="
echo "Epifania is running"
echo "=========================================="
echo "Backend:  http://127.0.0.1:8000"
echo "Frontend: http://127.0.0.1:5173"
echo "=========================================="
echo ""
echo "Logs:"
echo "  Central:  tail -f logs/central.log"
echo "  Backend:  tail -f logs/backend/backend.log"
echo "  Device:   tail -f logs/device/device.log"
echo "  Errors:   tail -f logs/backend/error.log"
echo "  Uvicorn:  tail -f logs/server/uvicorn.log"
echo "  Vite:     tail -f logs/server/vite.log"
echo ""
echo "Note: Backend has integrated health monitoring"
echo "Press Ctrl+C to stop all services"
echo ""

wait

