"""
Modelos Pydantic (schemas) para a API da Fábrica de Vídeos Dark.
Define todas as estruturas de dados trocadas entre frontend e backend.
"""

from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional


# === Enums ===

class VideoStage(str, Enum):
    """Estágios do pipeline de produção de vídeo."""
    INGESTION = "ingestao"
    AI_SCRIPT = "ia_roteriro"
    IMAGE_PROCESSING = "processamento_imagem"
    RENDERING = "renderizacao"
    COMPLETED = "concluido"
    FAILED = "falhou"


class VideoStatus(str, Enum):
    """Status de um vídeo na fila."""
    QUEUED = "queued"
    PROCESSING = "processing"
    READY = "ready"
    UPLOADED = "uploaded"
    ERROR = "error"


class OperationMode(str, Enum):
    """Modo de operação da fábrica."""
    MANUAL = "manual"
    AUTONOMOUS = "autonomous"


# === Schemas de Requisição ===

class CreateVideoRequest(BaseModel):
    """Requisição para criar um novo vídeo."""
    ticker: str = Field(..., description="Ticker do ativo financeiro (ex: PETR4.SA)")
    topic: Optional[str] = Field(None, description="Tópico específico para o roteiro")
    auto_upload: bool = Field(False, description="Se true, faz upload automático ao concluir")


class UpdateOperationModeRequest(BaseModel):
    """Requisição para alterar o modo de operação."""
    mode: OperationMode


# === Schemas de Resposta ===

class StageInfo(BaseModel):
    """Informação sobre um estágio do pipeline."""
    name: str
    status: VideoStage
    progress: float = Field(0.0, ge=0.0, le=1.0)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error: Optional[str] = None


class VideoItem(BaseModel):
    """Representação de um vídeo na fila."""
    id: str
    ticker: str
    topic: Optional[str] = None
    status: VideoStatus
    current_stage: VideoStage
    stages: list[StageInfo] = []
    created_at: datetime
    updated_at: datetime
    script: Optional[str] = None
    audio_path: Optional[str] = None
    video_path: Optional[str] = None
    youtube_video_id: Optional[str] = None
    error_log: list[str] = []


class TickerData(BaseModel):
    """Dados de um ticker financeiro."""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: Optional[int] = None
    news: list[dict] = []
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    debt_to_equity: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    sma_5: Optional[float] = None
    sma_20: Optional[float] = None
    momentum_5: Optional[float] = None
    volatility_5: Optional[float] = None
    price_vs_sma5: Optional[float] = None


class DashboardMetrics(BaseModel):
    """Métricas do dashboard."""
    total_videos: int = 0
    completed_videos: int = 0
    failed_videos: int = 0
    processing_videos: int = 0
    total_views: int = 0
    trending_topics: list[dict] = []
    adsense_revenue: float = 0.0
    adsense_currency: str = "BRL"
    system_health: str = "healthy"
    uptime_seconds: int = 0
    pipeline_active: bool = False


class SystemHealth(BaseModel):
    """Estado de saúde do sistema."""
    status: str = "healthy"
    ffmpeg_available: bool = False
    edge_tts_available: bool = False
    yfinance_available: bool = False
    youtube_authenticated: bool = False
    disk_space_mb: float = 0.0
    active_jobs: int = 0


class ErrorResponse(BaseModel):
    """Resposta de erro padrão."""
    detail: str
    error_code: Optional[str] = None
