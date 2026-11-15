"""
Router do YouTube - Autenticação e upload de vídeos.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from loguru import logger

from models.schemas import VideoItem, VideoStatus
from services.youtube_upload import (
    upload_video,
    check_authentication,
    build_video_title,
    build_video_description,
)
from config import settings

router = APIRouter(prefix="/api/youtube", tags=["YouTube"])

from routers.pipeline import get_queue_state


@router.get("/auth/status", response_model=dict)
async def auth_status():
    """Verifica se a autenticação do YouTube está configurada."""
    ready = check_authentication()
    secrets_path = settings.client_secrets_file
    return {
        "authenticated": ready,
        "secrets_file": str(secrets_path),
        "secrets_file_exists": secrets_path.exists(),
        "message": "Autenticado e pronto" if ready else f"Coloque o ficheiro client_secrets.json em: {settings.base_dir}",
    }


@router.post("/upload/{video_id}", response_model=dict)
async def upload_video_to_youtube(video_id: str, privacy: str = "private"):
    """
    Faz upload manual de um vídeo já renderizado para o YouTube.
    """
    queue = get_queue_state()
    if video_id not in queue:
        raise HTTPException(status_code=404, detail=f"Vídeo {video_id} não encontrado")

    video = queue[video_id]
    if video.status != VideoStatus.READY:
        raise HTTPException(
            status_code=400,
            detail=f"Vídeo não está pronto para upload. Status atual: {video.status}",
        )

    if not video.video_path:
        raise HTTPException(status_code=400, detail="Caminho do vídeo não encontrado")

    try:
        response = upload_video(
            video_path=Path(video.video_path),
            title=build_video_title(video.ticker, 0, 0),  # Simplificado
            description=build_video_description(video.ticker, 0, 0, video.script or ""),
            tags=[video.ticker, "finanças", "investimentos", "bolsa"],
            privacy_status=privacy,
        )

        video.youtube_video_id = response.get("id")
        video.status = VideoStatus.UPLOADED
        logger.info(f"[YouTube] Upload manual concluído: {video.youtube_video_id}")

        return {
            "success": True,
            "video_id": response.get("id"),
            "youtube_url": f"https://www.youtube.com/watch?v={response.get('id')}",
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        video.error_log.append(f"[YouTube Upload] {e}")
        raise HTTPException(status_code=500, detail=f"Erro no upload: {e}")
