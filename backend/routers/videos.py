"""
Router de Vídeos - Fila de renderização e logs.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from loguru import logger

from models.schemas import VideoItem
from config import settings

router = APIRouter(prefix="/api/videos", tags=["Vídeos"])

# Referência à fila partilhada com o router de pipeline
from routers.pipeline import get_queue_state


@router.get("/", response_model=list[VideoItem])
async def list_videos():
    """Lista todos os vídeos (fila de renderização)."""
    queue = get_queue_state()
    return list(queue.values())


@router.get("/{video_id}", response_model=VideoItem)
async def get_video(video_id: str):
    """Detalhes de um vídeo específico."""
    queue = get_queue_state()
    if video_id not in queue:
        raise HTTPException(status_code=404, detail=f"Vídeo {video_id} não encontrado")
    return queue[video_id]


@router.get("/{video_id}/logs", response_model=list[str])
async def get_video_logs(video_id: str):
    """Retorna o log de erros de um vídeo específico."""
    queue = get_queue_state()
    if video_id not in queue:
        raise HTTPException(status_code=404, detail=f"Vídeo {video_id} não encontrado")
    return queue[video_id].error_log


@router.delete("/{video_id}")
async def delete_video(video_id: str):
    """Remove um vídeo da fila."""
    queue = get_queue_state()
    if video_id not in queue:
        raise HTTPException(status_code=404, detail=f"Vídeo {video_id} não encontrado")

    video = queue[video_id]
    # Limpar ficheiros temporários
    if video.video_path:
        p = Path(video.video_path)
        if p.exists():
            p.unlink()
    if video.audio_path:
        p = Path(video.audio_path)
        if p.exists():
            p.unlink()

    del queue[video_id]
    logger.info(f"[Vídeos] Vídeo removido: {video_id}")
    return {"message": f"Vídeo {video_id} removido"}


@router.get("/files/list")
async def list_video_files():
    """Lista os ficheiros de vídeo renderizados no disco."""
    videos_dir = settings.videos_dir
    files = []
    if videos_dir.exists():
        for f in videos_dir.iterdir():
            if f.suffix == ".mp4":
                stat = f.stat()
                files.append({
                    "filename": f.name,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "path": str(f),
                })
    return {"videos": files, "count": len(files)}
