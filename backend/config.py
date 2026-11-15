"""
Configuração central do backend da Fábrica de Vídeos Dark.
Todas as constantes e caminhos de ficheiros são definidos aqui.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# === Caminhos base ===
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"

# Sub-pastas de assets
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
FONTS_DIR = ASSETS_DIR / "fonts"
TEMPLATES_DIR = ASSETS_DIR / "templates"

# Pastas de saída
VIDEOS_DIR = OUTPUT_DIR / "videos"
AUDIO_DIR = OUTPUT_DIR / "audio"
SUBTITLES_DIR = OUTPUT_DIR / "subtitles"

# Criar pastas se não existirem
for d in [ASSETS_DIR, OUTPUT_DIR, TEMP_DIR, BACKGROUNDS_DIR, FONTS_DIR, TEMPLATES_DIR,
          VIDEOS_DIR, AUDIO_DIR, SUBTITLES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# === YouTube API ===
# O ficheiro client_secrets.json deve estar na raiz do projeto
CLIENT_SECRETS_FILE = BASE_DIR / "client_secrets.json"
# Alternativa: o ficheiro do Desktop com nome longo
ALT_CLIENT_SECRETS = BASE_DIR / "client_secret_41170927456-s1cenrss86lvf872r431l4dr4nskbjcb.apps.googleusercontent.com.json"

# === Configuração do pipeline ===
# Modo de operação: "manual" (aprovação manual) ou "autonomous" (postagem autônoma)
OPERATION_MODE = os.getenv("OPERATION_MODE", "manual")

# Configurações de voz (edge-tts)
VOICE_LANGUAGE = "pt-BR"
VOICE_NAME = "pt-BR-AntonioNeural"
VOICE_RATE = "+0%"
VOICE_PITCH = "+0Hz"

# Configurações de vídeo
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
VIDEO_FORMAT = "mp4"

# Configurações de legendas
SUBTITLE_FONT_SIZE = 48
SUBTITLE_FONT = "Arial-Bold"
SUBTITLE_COLOR = "white"
SUBTITLE_STROKE_COLOR = "black"
SUBTITLE_STROKE_WIDTH = 2

# Configurações do servidor
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))

# CORS - permitir o frontend Vite
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
]


class Settings:
    """Classe de configuração acessível em toda a aplicação."""
    base_dir: Path = BASE_DIR
    assets_dir: Path = ASSETS_DIR
    output_dir: Path = OUTPUT_DIR
    temp_dir: Path = TEMP_DIR
    videos_dir: Path = VIDEOS_DIR
    audio_dir: Path = AUDIO_DIR
    subtitles_dir: Path = SUBTITLES_DIR
    backgrounds_dir: Path = BACKGROUNDS_DIR
    fonts_dir: Path = FONTS_DIR
    templates_dir: Path = TEMPLATES_DIR

    client_secrets_file: Path = CLIENT_SECRETS_FILE if CLIENT_SECRETS_FILE.exists() else ALT_CLIENT_SECRETS

    operation_mode: str = OPERATION_MODE
    voice_name: str = VOICE_NAME
    voice_rate: str = VOICE_RATE
    video_width: int = VIDEO_WIDTH
    video_height: int = VIDEO_HEIGHT
    video_fps: int = VIDEO_FPS
    video_codec: str = VIDEO_CODEC
    audio_codec: str = AUDIO_CODEC
    subtitle_font_size: int = SUBTITLE_FONT_SIZE
    subtitle_font: str = SUBTITLE_FONT
    subtitle_color: str = SUBTITLE_COLOR
    subtitle_stroke_color: str = SUBTITLE_STROKE_COLOR
    subtitle_stroke_width: int = SUBTITLE_STROKE_WIDTH
    api_host: str = API_HOST
    api_port: int = API_PORT
    cors_origins: list = CORS_ORIGINS


settings = Settings()
