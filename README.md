# 🏭 Fábrica de Vídeos Dark

Sistema autônomo de criação de vídeos de finanças com pipeline de 4 estágios, otimizado para rodar localmente em macOS.

> **Stack 100% gratuita** — sem APIs pagas, sem custos de IA de terceiros.

---

## 📋 Stack Tecnológica

| Camada | Tecnologia | Custo |
|--------|-----------|-------|
| **Frontend** | React 18 + Vite + TypeScript + Tailwind CSS + Recharts | Gratuito |
| **Backend** | Python + FastAPI + Uvicorn (assíncrono) | Gratuito |
| **Ingestão de Dados** | yfinance — notícias e cotações do mercado | Gratuito |
| **Voz/Locução** | edge-tts — voz realista pt-BR (Microsoft Edge) | Gratuito |
| **Imagem** | Pillow (PIL) — geração de gráficos visuais | Gratuito |
| **Renderização** | moviepy 2.x + ffmpeg — composição de vídeo | Gratuito |
| **Upload** | YouTube Data API v3 — OAuth 2.0 | Gratuito (quota) |

---

## 🏗️ Arquitetura — Pipeline de 4 Estágios

```
┌──────────────┐    ┌──────────────────┐    ┌─────────────────────┐    ┌──────────────┐
│  1. INGESTÃO │ -> │  2. IA: ROTEIRO  │ -> │  3. IMG: GRÁFICO   │ -> │ 4. RENDERIZ. │
│   (yfinance) │    │   E + VOZ        │    │   VISUAL (PIL)      │    │ (moviepy+ff) │
│              │    │   (edge-tts)     │    │                     │    │              │
│ Preço, var.  │    │ Roteiro auto +   │    │ PNG 1920x1080 com   │    │ MP4 final    │
│ Notícias     │    │ Locução MP3 +    │    │ tema dark + barras  │    | h264 + aac   │
│ Tickers      │    │ Legendas SRT     │    │ de volume          │    │ + legendas   │
└──────────────┘    └──────────────────┘    └─────────────────────┘    └──────────────┘
```

**Fluxo completo:** O utilizador escolhe um ticker (ex: `PETR4.SA`) → o backend executa os 4 estágios em background (assíncrono) → o vídeo MP4 é gerado → opcionalmente upload para YouTube.

---

## 📁 Estrutura de Pastas

```
app-fabrica-videos/
├── backend/
│   ├── main.py                  # App FastAPI (entrypoint)
│   ├── config.py                # Configurações, caminhos e constantes
│   ├── requirements.txt         # Dependências Python
│   ├── .env                     # Variáveis de ambiente
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py            # Modelos Pydantic (VideoItem, StageInfo, etc.)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_ingestion.py     # Estágio 1: yfinance
│   │   ├── voice_generation.py   # Estágio 2: edge-tts + legendas
│   │   ├── video_renderer.py     # Estágio 3+4: PIL gráfico + moviepy render
│   │   └── youtube_upload.py     # Upload via YouTube Data API v3
│   └── routers/
│       ├── __init__.py
│       ├── pipeline.py           # Orquestração dos 4 estágios (async)
│       ├── videos.py             # Fila de renderização, logs, deletar
│       ├── dashboard.py           # Métricas, tópicos em alta, saúde
│       └── youtube.py            # Auth e upload manual
├── frontend/
│   ├── package.json
│   ├── vite.config.ts            # Proxy /api -> backend
│   ├── tailwind.config.js         # Tema dark customizado
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx                # Rotas (Factory / Dashboard)
│       ├── index.css              # Tailwind + animações de esteira
│       ├── vite-env.d.ts
│       ├── types/
│       │   └── index.ts           # Tipos partilhados frontend/backend
│       ├── services/
│       │   └── api.ts             # Cliente HTTP (axios)
│       ├── components/
│       │   ├── Sidebar.tsx        # Menu lateral + toggle de modo
│       │   ├── FactoryConveyor.tsx # Esteira de produção visual
│       │   ├── StageCard.tsx       # Card de cada estágio
│       │   ├── VideoQueue.tsx      # Fila de vídeos + ações
│       │   ├── ErrorLog.tsx        # Log de erros com alertas vermelhos
│       │   └── ToggleSwitch.tsx    # Switch Manual/Autônomo
│       └── pages/
│           ├── FactoryPage.tsx    # UI principal da fábrica
│           └── DashboardPage.tsx  # Dashboard com gráficos
├── assets/
│   ├── backgrounds/               # Imagens de fundo (1920x1080)
│   ├── fonts/                     # Fontes TTF/OTF
│   └── templates/                 # Overlays, logos e assets visuais
├── output/                        # Vídeos e áudios gerados (gitignored)
├── temp/                          # Ficheiros temporários (gitignored)
├── .gitignore
└── README.md
```

---

## ✅ Pré-requisitos

### Sistema

| Requisito | Versão mínima | Verificar |
|-----------|--------------|-----------|
| macOS | 12+ (Monterey) | — |
| Python | 3.11+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| ffmpeg | qualquer | `ffmpeg -version` |
| pip | — | `pip3 --version` |

### Instalar ffmpeg (se ainda não tem)

```bash
brew install ffmpeg
```

---

## 🚀 Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/app-fabrica-videos.git
cd app-fabrica-videos
```

### 2. Configurar o Backend

```bash
cd backend

# (Recomendado) Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configurar o Frontend

```bash
cd ../frontend

# Instalar dependências
npm install
```

---

## ▶️ Como Iniciar

Precisa de **dois terminais** — um para o backend e outro para o frontend.

### Terminal 1 — Backend

```bash
cd backend
source venv/bin/activate    # se usou venv
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- API: http://127.0.0.1:8000
- Documentação Swagger: http://127.0.0.1:8000/docs

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

- UI: http://127.0.0.1:5173

### Atalho: iniciar ambos num único comando

```bash
# Backend em background + Frontend em foreground
cd backend && uvicorn main:app --host 127.0.0.1 --port 8000 & \
cd ../frontend && npm run dev
```

---

## 🧪 Como Testar

### Teste 1: Verificar Saúde do Sistema

Com o backend a correr, abra no browser ou use curl:

```bash
# Verificar se todos os componentes estão disponíveis
curl -s http://127.0.0.1:8000/api/dashboard/health | python3 -m json.tool
```

Resposta esperada:
```json
{
  "status": "healthy",
  "ffmpeg_available": true,
  "edge_tts_available": true,
  "yfinance_available": true,
  "youtube_authenticated": true,
  "disk_space_mb": 281662.1,
  "active_jobs": 0
}
```

### Teste 2: Criar um Vídeo (Pipeline Completo via API)

```bash
# Criar vídeo do ticker PETR4.SA
curl -s -X POST http://127.0.0.1:8000/api/pipeline/create \
  -H "Content-Type: application/json" \
  -d '{"ticker": "PETR4.SA", "auto_upload": false}' | python3 -m json.tool
```

Resposta esperada (retorna imediatamente):
```json
{
  "id": "a1b2c3d4",
  "ticker": "PETR4.SA",
  "status": "queued",
  "current_stage": "ingestao",
  ...
}
```

### Teste 3: Monitorar o Progresso do Pipeline

```bash
# Substituir {id} pelo ID retornado no Teste 2
curl -s http://127.0.0.1:8000/api/pipeline/status/a1b2c3d4 | python3 -m json.tool
```

O vídeo passa por 4 estágios (cada ~5-15s):
1. `ingestao` → busca dados no yfinance
2. `ia_roteriro` → gera roteiro + áudio (edge-tts)
3. `processamento_imagem` → cria gráfico (PIL)
4. `renderizacao` → renderiza MP4 (moviepy + ffmpeg)

Quando `status` for `"ready"`, o vídeo está pronto em `output/videos/{id}.mp4`.

### Teste 4: Verificar o Vídeo Gerado

```bash
# Listar vídeos gerados no disco
curl -s http://127.0.0.1:8000/api/videos/files/list | python3 -m json.tool

# Verificar o vídeo com ffprobe
ffprobe -v quiet -print_format json -show_streams output/videos/{id}.mp4 | python3 -m json.tool
```

### Teste 5: Testar Cada Estágio Individualmente (Python)

Criar um ficheiro `test_stages.py` na pasta `backend/`:

```python
"""Teste individual de cada estágio do pipeline."""
import sys, os, asyncio
sys.path.insert(0, os.getcwd())

from config import settings
from services.data_ingestion import fetch_ticker_data, generate_script_from_data
from services.voice_generation import generate_voice
from services.video_renderer import create_chart_image, render_video

async def main():
    # Estágio 1: Ingestão
    print("Estágio 1: Ingestão de Dados (yfinance)")
    data = await fetch_ticker_data("PETR4.SA")
    print(f"  {data.name} | R$ {data.price} | {data.change_percent}%")
    script = generate_script_from_data(data)
    print(f"  Roteiro: {script[:100]}...")

    # Estágio 2: Voz
    print("\nEstágio 2: Geração de Voz (edge-tts)")
    audio = settings.audio_dir / "teste.mp3"
    await generate_voice(script, audio)
    print(f"  Áudio: {audio.stat().st_size / 1024:.1f} KB")

    # Estágio 3: Imagem
    print("\nEstágio 3: Processamento de Imagem (PIL)")
    chart = settings.temp_dir / "teste.png"
    create_chart_image(data.symbol, data.price, data.change_percent, chart)
    print(f"  Imagem: {chart}")

    # Estágio 4: Renderização
    print("\nEstágio 4: Renderização (moviepy + ffmpeg)")
    video = settings.videos_dir / "teste.mp4"
    render_video(script, audio, data.symbol, data.price,
                 data.change_percent, video, chart)
    print(f"  Vídeo: {video} ({video.stat().st_size / 1024 / 1024:.2f} MB)")

asyncio.run(main())
```

Executar:
```bash
cd backend
python3 test_stages.py
```

### Teste 6: Testar via Interface Web (UI)

1. Inicie backend e frontend (ver secção "Como Iniciar")
2. Abra http://127.0.0.1:5173
3. Na tela **Fábrica de Vídeos**:
   - Escolha um ticker (ex: `PETR4.SA`, `AAPL`, `BTC-USD`)
   - Clique em **Iniciar Produção**
   - Acompanhe a esteira de produção visual com os 4 estágios
   - Veja a fila de renderização e logs de erro (se houver)
4. Na tela **Dashboard**:
   - Gráficos de tópicos em alta (dados reais do yfinance)
   - Métricas de views, status do AdSense (mockado)
   - Saúde do sistema (ffmpeg, edge-tts, yfinance, YouTube)
5. No **menu lateral**:
   - Toggle entre **Aprovação Manual** e **Postagem Autônoma**

### Teste 7: Verificar Build do Frontend

```bash
cd frontend
npx tsc --noEmit       # Type check
npx vite build          # Build de produção
```

### Teste 8: Listar Endpoints Disponíveis

```bash
# Documentação interativa Swagger
open http://127.0.0.1:8000/docs

# Endpoints raiz
curl -s http://127.0.0.1:8000/ | python3 -m json.tool
```

---

## 🎬 YouTube API — Configuração de Upload

### Obter o ficheiro `client_secrets.json`

1. Acesse https://console.cloud.google.com/
2. Crie um novo projeto
3. Ative a **YouTube Data API v3**
4. Vá em **Credenciais** → **Criar credenciais** → **OAuth client ID**
5. Tipo: **Desktop App**
6. Baixe o JSON e coloque na raiz do projeto com o nome `client_secrets.json`

> ⚠️ O ficheiro `client_secrets.json` está no `.gitignore` e **não** deve ser commitado.

### Primeiro upload

No primeiro upload (via UI ou API), o navegador abre para autenticação Google. O token é guardado em `temp/youtube_token.pkl` para uploads subsequentes.

### Upload manual via API

```bash
# Após o vídeo estar "ready"
curl -s -X POST "http://127.0.0.1:8000/api/youtube/upload/{video_id}?privacy=private" | python3 -m json.tool
```

---

## 🔌 Referência de Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Info da API |
| `GET` | `/api/health` | Health check simples |
| `GET` | `/docs` | Documentação Swagger |
| `POST` | `/api/pipeline/create` | Criar vídeo (body: `{"ticker": "PETR4.SA"}`) |
| `GET` | `/api/pipeline/queue` | Lista fila de vídeos |
| `GET` | `/api/pipeline/status/{id}` | Status de um vídeo específico |
| `GET` | `/api/pipeline/mode` | Modo atual (manual/autonomous) |
| `POST` | `/api/pipeline/mode` | Alterar modo (body: `"manual"` ou `"autonomous"`) |
| `GET` | `/api/videos/` | Lista todos os vídeos |
| `GET` | `/api/videos/{id}` | Detalhes de um vídeo |
| `GET` | `/api/videos/{id}/logs` | Log de erros de um vídeo |
| `DELETE` | `/api/videos/{id}` | Remover vídeo da fila |
| `GET` | `/api/videos/files/list` | Ficheiros MP4 no disco |
| `GET` | `/api/dashboard/metrics` | Métricas + tópicos em alta |
| `GET` | `/api/dashboard/health` | Saúde do sistema |
| `GET` | `/api/dashboard/adsense` | Status AdSense (mockado) |
| `GET` | `/api/youtube/auth/status` | Status de autenticação YouTube |
| `POST` | `/api/youtube/upload/{id}` | Upload manual para YouTube |

---

## 🎛️ Modos de Operação

| Modo | Comportamento |
|------|-------------|
| **Manual** (padrão) | Vídeos são gerados, mas o upload para YouTube requer clique manual |
| **Autônomo** | Upload automático para YouTube ao concluir a renderização |

Alternar via toggle no menu lateral da UI ou via API:

```bash
curl -s -X POST http://127.0.0.1:8000/api/pipeline/mode \
  -H "Content-Type: application/json" \
  -d '"autonomous"'
```

---

## 🐛 Troubleshooting

### ffmpeg não encontrado

```bash
brew install ffmpeg
# Verificar
ffmpeg -version
```

### edge-tts erro 403

Atualizar para a versão mais recente:
```bash
pip install --upgrade edge-tts
```

### yfinance erro 429 (Too Many Requests)

Atualizar para a versão mais recente:
```bash
pip install --upgrade yfinance
```

Se persistir, o Yahoo Finance pode estar com rate limiting temporário. O pipeline trata o erro graciosamente e gera o roteiro com valores padrão (zero).

### Erro de conflito Pillow vs moviepy

moviepy 2.x requer Pillow < 11.0:
```bash
pip install "Pillow>=9.2.0,<11.0"
```

### TextClip erro "missing argument: font"

O moviepy 2.x exige o caminho de um ficheiro de fonte. O código já usa `/System/Library/Fonts/Helvetica.ttc` (macOS). Se estiver noutro SO, altere o caminho em `backend/services/video_renderer.py`.

### Porta já em uso

```bash
# Encontrar processo na porta 8000
lsof -i :8000
# Matar processo
kill -9 <PID>

# Ou usar porta diferente
uvicorn main:app --port 8001
```

### Erro de CORS no frontend

Verificar que o backend está a correr em `http://127.0.0.1:8000`. O Vite faz proxy de `/api` para o backend automaticamente (ver `frontend/vite.config.ts`).

---

## 📊 Verificação de Componentes

| Componente | Como verificar | Comando |
|-----------|----------------|---------|
| ffmpeg | Versão instalada | `ffmpeg -version` |
| Python | Versão 3.11+ | `python3 --version` |
| Node.js | Versão 18+ | `node --version` |
| Backend | API responde | `curl http://127.0.0.1:8000/api/health` |
| Frontend | Build sem erros | `cd frontend && npx tsc --noEmit && npx vite build` |
| yfinance | Dados reais | `python3 -c "import yfinance; print(yfinance.Ticker('AAPL').history(period='5d'))"` |
| edge-tts | Gera áudio | `python3 -c "import asyncio, edge_tts; asyncio.run(edge_tts.Communicate('teste','pt-BR-AntonioNeural').save('t.mp3'))"` |
| moviepy | Import OK | `python3 -c "from moviepy import VideoFileClip; print('OK')"` |
| YouTube | Auth file | `curl http://127.0.0.1:8000/api/youtube/auth/status` |

---

## 📝 Licença

Este projeto é de uso livre para fins educacionais e pessoais.

## ⚠️ Aviso

Este sistema gera conteúdo automatizado sobre mercados financeiros. Os vídeos produzidos **não constituem recomendação de investimento**. Use por sua conta e risco.
