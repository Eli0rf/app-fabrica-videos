"""
Router do Pipeline - Orquestra os 4 estágios de criação de vídeo.
Estágios: Ingestão de Dados -> IA (Roteiro e Voz) -> Processamento de Imagem -> Renderização
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from loguru import logger
from datetime import datetime
import uuid
import asyncio

from models.schemas import (
    CreateVideoRequest,
    VideoItem,
    VideoStage,
    VideoStatus,
    StageInfo,
    OperationMode,
)
from services.data_ingestion import fetch_ticker_data
from services.script_service import generate_structured_script
from services.voice_generation import generate_voice, generate_subtitles
from services.video_renderer import render_video, create_chart_image
from services.youtube_upload import upload_video, build_video_title, build_video_description
from config import settings

router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])

# Estado em memória (substituir por DB em produção)
_video_queue: dict[str, VideoItem] = {}
_operation_mode: OperationMode = OperationMode.MANUAL


def get_queue_state() -> dict[str, VideoItem]:
    """Retorna o dicionario de videos em memoria (uso interno)."""
    return _video_queue


def get_operation_mode() -> OperationMode:
    return _operation_mode


def set_operation_mode(mode: OperationMode):
    global _operation_mode
    _operation_mode = mode
    logger.info(f"[Pipeline] Modo de operação alterado para: {mode}")


async def run_pipeline(video_id: str, ticker: str, topic: str | None, auto_upload: bool):
    """
    Executa o pipeline completo de criação de vídeo de forma assíncrona.
    Cada estágio atualiza o estado do vídeo em memória.
    """
    video = _video_queue[video_id]

    # === ESTÁGIO 1: Ingestão de Dados ===
    stage1 = StageInfo(name="Ingestão de Dados", status=VideoStage.INGESTION, started_at=datetime.now())
    video.stages.append(stage1)
    video.current_stage = VideoStage.INGESTION
    video.status = VideoStatus.PROCESSING
    video.updated_at = datetime.now()

    try:
        logger.info(f"[Pipeline:{video_id}] Estágio 1 - Ingestão de dados para {ticker}")
        ticker_data = await fetch_ticker_data(ticker)
        stage1.progress = 1.0
        stage1.finished_at = datetime.now()
    except Exception as e:
        stage1.error = str(e)
        stage1.finished_at = datetime.now()
        video.status = VideoStatus.ERROR
        video.current_stage = VideoStage.FAILED
        video.error_log.append(f"[Ingestão] {e}")
        video.updated_at = datetime.now()
        logger.error(f"[Pipeline:{video_id}] Falha na ingestão: {e}")
        return

    # === ESTÁGIO 2: IA - Roteiro e Voz ===
    stage2 = StageInfo(name="IA: Roteiro e Voz", status=VideoStage.AI_SCRIPT, started_at=datetime.now())
    video.stages.append(stage2)
    video.current_stage = VideoStage.AI_SCRIPT
    video.updated_at = datetime.now()

    try:
        logger.info(f"[Pipeline:{video_id}] Estágio 2 - Gerando roteiro")
        script = generate_structured_script(ticker_data, topic)
        video.script = script
        stage2.progress = 0.5

        logger.info(f"[Pipeline:{video_id}] Estágio 2 - Gerando voz com edge-tts")
        audio_path = settings.audio_dir / f"{video_id}.mp3"
        await generate_voice(script, audio_path)
        video.audio_path = str(audio_path)

        # Gerar legendas
        subtitles_path = settings.subtitles_dir / f"{video_id}.srt"
        try:
            await generate_subtitles(script, subtitles_path)
        except Exception as e:
            logger.warning(f"[Pipeline:{video_id}] Legendas opcionais falharam: {e}")

        stage2.progress = 1.0
        stage2.finished_at = datetime.now()
    except Exception as e:
        stage2.error = str(e)
        stage2.finished_at = datetime.now()
        video.status = VideoStatus.ERROR
        video.current_stage = VideoStage.FAILED
        video.error_log.append(f"[IA/Voz] {e}")
        video.updated_at = datetime.now()
        logger.error(f"[Pipeline:{video_id}] Falha na geração de voz: {e}")
        return

    # === ESTÁGIO 3: Processamento de Imagem ===
    stage3 = StageInfo(name="Processamento de Imagem", status=VideoStage.IMAGE_PROCESSING, started_at=datetime.now())
    video.stages.append(stage3)
    video.current_stage = VideoStage.IMAGE_PROCESSING
    video.updated_at = datetime.now()

    try:
        logger.info(f"[Pipeline:{video_id}] Estágio 3 - Gerando imagem de gráfico")
        chart_path = settings.temp_dir / f"chart_{video_id}.png"
        create_chart_image(ticker, ticker_data.price, ticker_data.change_percent, chart_path)
        stage3.progress = 1.0
        stage3.finished_at = datetime.now()
    except Exception as e:
        stage3.error = str(e)
        stage3.finished_at = datetime.now()
        video.status = VideoStatus.ERROR
        video.current_stage = VideoStage.FAILED
        video.error_log.append(f"[Imagem] {e}")
        video.updated_at = datetime.now()
        logger.error(f"[Pipeline:{video_id}] Falha no processamento de imagem: {e}")
        return

    # === ESTÁGIO 4: Renderização ===
    stage4 = StageInfo(name="Renderização", status=VideoStage.RENDERING, started_at=datetime.now())
    video.stages.append(stage4)
    video.current_stage = VideoStage.RENDERING
    video.updated_at = datetime.now()

    try:
        logger.info(f"[Pipeline:{video_id}] Estágio 4 - Renderizando vídeo")
        video_path = settings.videos_dir / f"{video_id}.mp4"
        render_video(
            script_text=script,
            audio_path=video.audio_path and __import__("pathlib").Path(video.audio_path),
            ticker=ticker,
            price=ticker_data.price,
            change_percent=ticker_data.change_percent,
            output_path=video_path,
            chart_image_path=chart_path,
        )
        video.video_path = str(video_path)
        stage4.progress = 1.0
        stage4.finished_at = datetime.now()
        video.status = VideoStatus.READY
        video.current_stage = VideoStage.COMPLETED
        video.updated_at = datetime.now()
        logger.info(f"[Pipeline:{video_id}] Vídeo pronto: {video_path}")
    except Exception as e:
        stage4.error = str(e)
        stage4.finished_at = datetime.now()
        video.status = VideoStatus.ERROR
        video.current_stage = VideoStage.FAILED
        video.error_log.append(f"[Renderização] {e}")
        video.updated_at = datetime.now()
        logger.error(f"[Pipeline:{video_id}] Falha na renderização: {e}")
        return

    # === Upload para YouTube (se aplicável) ===
    should_upload = auto_upload or _operation_mode == OperationMode.AUTONOMOUS
    if should_upload and video.status == VideoStatus.READY:
        try:
            logger.info(f"[Pipeline:{video_id}] Upload para YouTube")
            from pathlib import Path as P
            response = upload_video(
                video_path=P(video.video_path),
                title=build_video_title(ticker, ticker_data.price, ticker_data.change_percent),
                description=build_video_description(ticker, ticker_data.price, ticker_data.change_percent, script),
                tags=[ticker, "finanças", "investimentos", "bolsa", "análise"],
                privacy_status="private",
            )
            video.youtube_video_id = response.get("id")
            video.status = VideoStatus.UPLOADED
            video.updated_at = datetime.now()
        except Exception as e:
            video.error_log.append(f"[YouTube] {e}")
            logger.error(f"[Pipeline:{video_id}] Falha no upload: {e}")
            # O vídeo ainda está pronto, apenas não foi uploaded


@router.post("/create", response_model=VideoItem)
async def create_video(request: CreateVideoRequest, background_tasks: BackgroundTasks):
    """
    Cria um novo vídeo e inicia o pipeline de forma assíncrona.
    Retorna imediatamente com o vídeo na fila.
    """
    video_id = str(uuid.uuid4())[:8]
    now = datetime.now()

    video = VideoItem(
        id=video_id,
        ticker=request.ticker,
        topic=request.topic,
        status=VideoStatus.QUEUED,
        current_stage=VideoStage.INGESTION,
        stages=[],
        created_at=now,
        updated_at=now,
        error_log=[],
    )

    _video_queue[video_id] = video
    logger.info(f"[Pipeline] Vídeo criado: id={video_id}, ticker={request.ticker}")

    # Executar pipeline em background para não bloquear a UI
    background_tasks.add_task(
        run_pipeline,
        video_id=video_id,
        ticker=request.ticker,
        topic=request.topic,
        auto_upload=request.auto_upload,
    )

    return video


@router.get("/status/{video_id}", response_model=VideoItem)
async def get_video_status(video_id: str):
    """Retorna o status atual de um vídeo específico."""
    if video_id not in _video_queue:
        raise HTTPException(status_code=404, detail=f"Vídeo {video_id} não encontrado")
    return _video_queue[video_id]


@router.get("/queue", response_model=list[VideoItem])
async def get_video_queue():
    """Retorna todos os vídeos na fila."""
    return list(_video_queue.values())


@router.get("/mode", response_model=dict)
async def get_mode():
    """Retorna o modo de operação atual."""
    return {"mode": _operation_mode.value}


@router.post("/mode", response_model=dict)
async def set_mode(mode: OperationMode):
    """Altera o modo de operação (manual ou autônomo)."""
    set_operation_mode(mode)
    return {"mode": mode.value, "message": f"Modo alterado para: {mode.value}"}
