"""
Router do Dashboard - Métricas, tópicos em alta, AdSense e saúde do sistema.
"""

from fastapi import APIRouter
from loguru import logger
from datetime import datetime
import subprocess
import shutil
import os

from models.schemas import DashboardMetrics, SystemHealth
from services.data_ingestion import fetch_trending_topics
from services.video_renderer import check_ffmpeg
from services.youtube_upload import check_authentication
from config import settings

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# Timestamp de início do servidor
_start_time = datetime.now()


@router.get("/metrics", response_model=DashboardMetrics)
async def get_metrics():
    """
    Retorna métricas do dashboard:
    - Total de vídeos, completos, falhados
    - Tópicos em alta (via yfinance)
    - Views e AdSense (mockado)
    - Saúde do sistema
    """
    from routers.pipeline import get_queue_state

    queue = get_queue_state()
    videos = list(queue.values())

    total = len(videos)
    completed = sum(1 for v in videos if v.status.value in ("ready", "uploaded"))
    failed = sum(1 for v in videos if v.status.value == "error")
    processing = sum(1 for v in videos if v.status.value == "processing")

    # Topicos em alta (busca real via yfinance com timeout)
    import asyncio
    try:
        trending = await asyncio.wait_for(
            fetch_trending_topics(),
            timeout=10.0,
        )
    except asyncio.TimeoutError:
        logger.warning("[Dashboard] Timeout ao buscar topicos - usando dados mockados")
        trending = [
            {"topic": "IBOVESPA", "ticker": "^BVSP", "trend_score": 85, "change_percent": 1.2, "direction": "alta"},
            {"topic": "PETROBRAS", "ticker": "PETR4.SA", "trend_score": 72, "change_percent": -0.8, "direction": "baixa"},
            {"topic": "VALE", "ticker": "VALE3.SA", "trend_score": 65, "change_percent": 0.5, "direction": "alta"},
            {"topic": "BITCOIN", "ticker": "BTC-USD", "trend_score": 90, "change_percent": 3.1, "direction": "alta"},
            {"topic": "ITAU", "ticker": "ITUB4.SA", "trend_score": 40, "change_percent": -0.3, "direction": "baixa"},
            {"topic": "AMBEV", "ticker": "ABEV3.SA", "trend_score": 35, "change_percent": 0.2, "direction": "alta"},
        ]
    except Exception as e:
        logger.warning(f"[Dashboard] Erro ao buscar topicos: {e}")
        trending = []

    # Métricas mockadas (sem custo de API)
    import random
    total_views = sum(random.randint(100, 5000) for _ in range(completed))

    metrics = DashboardMetrics(
        total_videos=total,
        completed_videos=completed,
        failed_videos=failed,
        processing_videos=processing,
        total_views=total_views,
        trending_topics=trending,
        adsense_revenue=round(total_views * 0.0025, 2),  # Estimativa mockada
        adsense_currency="BRL",
        system_health="healthy",
        uptime_seconds=int((datetime.now() - _start_time).total_seconds()),
        pipeline_active=processing > 0,
    )

    return metrics


@router.get("/health", response_model=SystemHealth)
async def get_health():
    """
    Verifica a saúde geral do sistema:
    - ffmpeg instalado
    - edge-tts disponível
    - yfinance disponível
    - YouTube autenticado
    - Espaço em disco
    """
    # Verificar ffmpeg
    ffmpeg_ok = check_ffmpeg()

    # Verificar edge-tts
    try:
        import edge_tts
        edge_tts_ok = True
    except ImportError:
        edge_tts_ok = False

    # Verificar yfinance
    try:
        import yfinance
        yfinance_ok = True
    except ImportError:
        yfinance_ok = False

    # Verificar YouTube auth
    youtube_ok = check_authentication()

    # Espaço em disco
    try:
        stat = os.statvfs(str(settings.base_dir))
        free_bytes = stat.f_frsize * stat.f_bavail
        disk_mb = round(free_bytes / (1024 * 1024), 1)
    except Exception:
        disk_mb = 0.0

    # Jobs ativos
    from routers.pipeline import get_queue_state
    queue = get_queue_state()
    active = sum(1 for v in queue.values() if v.status.value == "processing")

    health = SystemHealth(
        status="healthy" if all([ffmpeg_ok, edge_tts_ok, yfinance_ok]) else "degraded",
        ffmpeg_available=ffmpeg_ok,
        edge_tts_available=edge_tts_ok,
        yfinance_available=yfinance_ok,
        youtube_authenticated=youtube_ok,
        disk_space_mb=disk_mb,
        active_jobs=active,
    )

    return health


@router.get("/adsense", response_model=dict)
async def get_adsense_status():
    """
    Status do AdSense (mockado — sem chamada real à API).
    Em produção, integrar com a YouTube Analytics API.
    """
    return {
        "status": "mocked",
        "message": "Dados do AdSense são simulados. Para dados reais, integre a YouTube Analytics API.",
        "estimated_revenue_brl": round(sum(1 for _ in range(10)) * 12.50, 2),
        "currency": "BRL",
        "period": "last_30_days",
    }
