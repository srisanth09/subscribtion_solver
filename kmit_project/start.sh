#!/usr/bin/env bash
# ==============================================================================
# Subscription & Recurring-Spend Guardian Agent - Unified Startup Script
# PRAGYAAN 2.0 Hackathon | KMIT CSE(AI&ML)
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "========================================================================"
echo "🛡️  STARTING SUBSCRIPTION & RECURRING-SPEND GUARDIAN AGENT"
echo "========================================================================"

# 1. Start Backend FastAPI Server
echo "🚀 [1/2] Starting FastAPI Backend on http://127.0.0.1:8000..."
cd "$BACKEND_DIR"

if [ -d "venv" ]; then
    PYTHON_EXE="$BACKEND_DIR/venv/bin/python3"
    UVICORN_EXE="$BACKEND_DIR/venv/bin/uvicorn"
else
    PYTHON_EXE="python3"
    UVICORN_EXE="uvicorn"
fi

# Run backend in background
PYTHONPATH=. "$UVICORN_EXE" app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
echo "✓ Backend launched with PID: $BACKEND_PID"

# Wait a brief moment for backend to initialize
sleep 2

# 2. Start Frontend Vite Dev Server
echo "🎨 [2/2] Starting React Vite Frontend on http://127.0.0.1:5173..."
cd "$FRONTEND_DIR"

# Trap exit to cleanup background processes on CTRL+C
trap 'echo -e "\n🛑 Stopping Guardian Agent services..."; kill $BACKEND_PID 2>/dev/null || true; exit 0' SIGINT SIGTERM EXIT

npm run dev -- --host 127.0.0.1 --port 5173
