#!/bin/bash
# ============================================
#  Fábrica de Vídeos Dark - Script de Arranque
#  Correr: ./start.sh
# ============================================

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🏭  Fábrica de Vídeos Dark — a iniciar..."
echo ""

# === Verificar pré-requisitos ===
echo "▸ A verificar pré-requisitos..."

if ! command -v python3 &>/dev/null; then
    echo "  ✗ Python3 não encontrado. Instale: brew install python"
    exit 1
fi

if ! command -v node &>/dev/null; then
    echo "  ✗ Node.js não encontrado. Instale: brew install node"
    exit 1
fi

if ! command -v ffmpeg &>/dev/null; then
    echo "  ✗ ffmpeg não encontrado. Instale: brew install ffmpeg"
    exit 1
fi

echo "  ✓ Python3    $(python3 --version 2>&1)"
echo "  ✓ Node.js    $(node --version 2>&1)"
echo "  ✓ ffmpeg     $(ffmpeg -version 2>&1 | head -1)"
echo ""

# === Verificar/instalar dependências backend ===
echo "▸ A verificar dependências do backend..."
cd "$ROOT_DIR/backend"

# Verificar se as dependências estão instaladas
if ! python3 -c "import fastapi" &>/dev/null 2>&1; then
    echo "  A instalar dependências Python..."
    pip3 install -r requirements.txt --quiet
fi
echo "  ✓ Dependências backend OK"
echo ""

# === Verificar/instalar dependências frontend ===
echo "▸ A verificar dependências do frontend..."
cd "$ROOT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "  A instalar dependências Node..."
    npm install --silent
fi
echo "  ✓ Dependências frontend OK"
echo ""

# === Limpar processos anteriores ===
echo "▸ A limpar processos anteriores..."
pkill -f "uvicorn.*8000" 2>/dev/null || true
pkill -f "vite.*5173" 2>/dev/null || true
sleep 1
echo "  ✓ Limpo"
echo ""

# === Iniciar backend ===
echo "▸ A iniciar backend (FastAPI) na porta 8000..."
cd "$ROOT_DIR/backend"
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
echo "  ✓ Backend PID: $BACKEND_PID"
echo ""

# === Aguardar backend ===
echo "▸ A aguardar backend iniciar..."
for i in $(seq 1 10); do
    if curl -s http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
        echo "  ✓ Backend pronto em http://127.0.0.1:8000"
        break
    fi
    sleep 1
    if [ $i -eq 10 ]; then
        echo "  ✗ Backend não respondeu a tempo"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
done
echo ""

# === Verificar saúde do sistema ===
echo "▸ Saúde do sistema:"
HEALTH=$(curl -s http://127.0.0.1:8000/api/dashboard/health 2>/dev/null || echo '{}')
echo "  ffmpeg:     $(echo "$HEALTH" | python3 -c 'import sys,json; d=json.load(sys.stdin); print("✓" if d.get("ffmpeg_available") else "✗")' 2>/dev/null || echo '?')"
echo "  edge-tts:   $(echo "$HEALTH" | python3 -c 'import sys,json; d=json.load(sys.stdin); print("✓" if d.get("edge_tts_available") else "✗")' 2>/dev/null || echo '?')"
echo "  yfinance:   $(echo "$HEALTH" | python3 -c 'import sys,json; d=json.load(sys.stdin); print("✓" if d.get("yfinance_available") else "✗")' 2>/dev/null || echo '?')"
echo "  YouTube:    $(echo "$HEALTH" | python3 -c 'import sys,json; d=json.load(sys.stdin); print("✓" if d.get("youtube_authenticated") else "✗")' 2>/dev/null || echo '?')"
echo ""

# === Iniciar frontend ===
echo "▸ A iniciar frontend (Vite) na porta 5173..."
cd "$ROOT_DIR/frontend"
npx vite --host 127.0.0.1 --port 5173 &
FRONTEND_PID=$!
echo "  ✓ Frontend PID: $FRONTEND_PID"
echo ""

# === Aguardar frontend ===
echo "▸ A aguardar frontend iniciar..."
for i in $(seq 1 10); do
    if curl -s http://127.0.0.1:5173 >/dev/null 2>&1; then
        echo "  ✓ Frontend pronto em http://127.0.0.1:5173"
        break
    fi
    sleep 1
    if [ $i -eq 10 ]; then
        echo "  ! Frontend pode ainda estar a compilar..."
    fi
done
echo ""

# === Pronto ===
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  🏭  FÁBRICA DE VÍDEOS DARK — PRONTO!"
echo ""
echo "  📺  Interface (UI):    http://127.0.0.1:5173"
echo "  🔌  API:               http://127.0.0.1:8000"
echo "  📚  Docs Swagger:      http://127.0.0.1:8000/docs"
echo ""
echo "  Para PARAR tudo:       Ctrl+C"
echo ""
echo "═══════════════════════════════════════════════════════════"

# === Manter o processo a correr ===
trap "echo ''; echo 'A parar servidores...'; kill $BACKEND_PID 2>/dev/null; kill $FRONTEND_PID 2>/dev/null; echo 'Parado.'; exit 0" SIGINT SIGTERM

# Aguardar indefinidamente (Ctrl+C para parar)
wait
