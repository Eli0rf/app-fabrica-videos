"""
Fábrica de Vídeos Dark - Backend FastAPI
Servidor principal assíncrono para o pipeline de criação de vídeos de finanças.

Para iniciar:
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload --host 127.0.0.1 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
import os

# Garantir que o diretório backend está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from routers import pipeline, videos, dashboard, youtube

# === Configuração de logging ===
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | {message}",
    level="INFO",
)
logger.add(
    settings.temp_dir / "backend.log",
    rotation="5 MB",
    retention="7 days",
    level="DEBUG",
)

# === App FastAPI ===
app = FastAPI(
    title="Fábrica de Vídeos Dark API",
    description="""
    Sistema autônomo de criação de vídeos de finanças.
    
    ## Pipeline de 4 estágios:
    1. **Ingestão de Dados** - Busca notícias e tickers via yfinance
    2. **IA (Roteiro e Voz)** - Gera roteiro e locução via edge-tts
    3. **Processamento de Imagem** - Cria gráficos visuais
    4. **Renderização** - Junta tudo com moviepy + ffmpeg
    
    ## YouTube Data API v3
    - Upload de vídeos autenticado via OAuth 2.0
    """,
    version="1.0.0",
)

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Registar routers ===
app.include_router(pipeline.router)
app.include_router(videos.router)
app.include_router(dashboard.router)
app.include_router(youtube.router)


# === Endpoints raiz ===

@app.get("/")
async def root():
    """Endpoint raiz com informação da API."""
    return {
        "name": "Fábrica de Vídeos Dark API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "pipeline": "/api/pipeline",
            "videos": "/api/videos",
            "dashboard": "/api/dashboard",
            "youtube": "/api/youtube",
        },
    }


@app.get("/api/health")
async def health():
    """Health check simples."""
    return {"status": "ok", "service": "fabrica-videos-dark"}


# === Inicialização ===
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("Fábrica de Vídeos Dark - Backend iniciando...")
    logger.info(f"Host: {settings.api_host}:{settings.api_port}")
    logger.info(f"Base dir: {settings.base_dir}")
    logger.info(f"Assets dir: {settings.assets_dir}")
    logger.info(f"Output dir: {settings.output_dir}")
    logger.info(f"Modo de operação: {settings.operation_mode}")
    logger.info("=" * 50)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
