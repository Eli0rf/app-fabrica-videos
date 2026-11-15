"""
Serviço de Upload para YouTube - Estágio final do Pipeline.
Usa YouTube Data API v3 com autenticação OAuth 2.0.
Consome o ficheiro local client_secrets.json.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
from typing import Optional
from loguru import logger
import pickle

from config import settings


# Scopes necessários para upload de vídeos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Ficheiro para guardar o token de autenticação
TOKEN_FILE = settings.temp_dir / "youtube_token.pkl"


def get_authenticated_service():
    """
    Autentica no YouTube usando OAuth 2.0.
    Usa o ficheiro client_secrets.json na raiz do projeto.
    Se o token já existir e for válido, reutiliza-o.
    """
    creds = None

    # Tentar carregar token existente
    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, "rb") as f:
                creds = pickle.load(f)
        except Exception:
            creds = None

    # Renovar token se expirado
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_FILE, "wb") as f:
                pickle.dump(creds, f)
        except Exception as e:
            logger.warning(f"[YouTube] Erro ao renovar token: {e}")
            creds = None

    # Autenticar se não há credenciais válidas
    if not creds or not creds.valid:
        secrets_path = settings.client_secrets_file
        if not secrets_path.exists():
            raise FileNotFoundError(
                f"Ficheiro client_secrets.json não encontrado em: {secrets_path}\n"
                f"Coloque o ficheiro de credenciais do Google Cloud Console na raiz do projeto."
            )

        logger.info(f"[YouTube] Iniciando fluxo OAuth com: {secrets_path}")
        flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
        creds = flow.run_local_server(port=0)

        # Guardar token para uso futuro
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    service = build("youtube", "v3", credentials=creds)
    return service


def upload_video(
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "22",  # 22 = People & Blogs
    privacy_status: str = "private",
) -> dict:
    """
    Faz upload de um vídeo para o YouTube.

    Args:
        video_path: Caminho do ficheiro de vídeo.
        title: Título do vídeo (máx 100 caracteres).
        description: Descrição do vídeo (máx 5000 caracteres).
        tags: Lista de tags.
        category_id: ID da categoria do YouTube.
        privacy_status: "private", "public" ou "unlisted".

    Returns:
        Resposta da API com o video_id.
    """
    logger.info(f"[YouTube] Iniciando upload: {video_path}")

    service = get_authenticated_service()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],  # Limite de tags
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10MB chunks
    )

    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logger.info(f"[YouTube] Upload: {int(status.progress() * 100)}%")

    video_id = response.get("id", "")
    logger.info(f"[YouTube] Upload concluído! Video ID: {video_id}")
    return response


def check_authentication() -> bool:
    """Verifica se a autenticação do YouTube está configurada."""
    secrets_path = settings.client_secrets_file
    return secrets_path.exists()


def build_video_title(ticker: str, price: float, change_percent: float) -> str:
    """Gera um título otimizado para o vídeo."""
    direction = "ALTA" if change_percent >= 0 else "QUEDA"
    emoji = "📈" if change_percent >= 0 else "📉"
    return f"{emoji} {ticker}: {direction} de {abs(change_percent):.2f}% | Análise do Dia"


def build_video_description(ticker: str, price: float, change_percent: float, script: str) -> str:
    """Gera uma descrição otimizada para o vídeo."""
    return (
        f"📊 Análise automatizada de {ticker}\n"
        f"💰 Preço: R$ {price:.2f}\n"
        f"📈 Variação: {change_percent:+.2f}%\n\n"
        f"🔔 Inscreva-se para mais análises diárias!\n\n"
        f"⚠️ Este vídeo foi gerado automaticamente pela Fábrica de Vídeos Dark.\n"
        f"Não constitui recomendação de investimento.\n\n"
        f"#finanças #investimentos #{ticker.replace('.SA', '').replace('-', '')} #análise #bolsa"
    )
