"""
Serviço de Renderização de Vídeo - Estágio 4 do Pipeline.
Usa moviepy e ffmpeg para juntar áudio, legendas e gráficos visuais.
"""

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
    CompositeVideoClip,
    ColorClip,
)
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional
import numpy as np
from loguru import logger
import subprocess
import json
import os

from config import settings


def check_ffmpeg() -> bool:
    """Verifica se o ffmpeg está instalado no sistema."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def create_chart_image(
    ticker: str,
    price: float,
    change_percent: float,
    output_path: Path,
) -> Path:
    """
    Cria uma imagem de gráfico simples usando PIL (sem dependências externas).
    Fundo escuro com estilo "Dark" para combinar com o tema.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1920, 1080
    bg_color = (10, 10, 20)  # Fundo escuro
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Título - Ticker
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
    except (OSError, IOError):
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Ticker name (canto superior esquerdo)
    draw.text((80, 60), ticker, fill=(255, 255, 255), font=font_large)

    # Preço
    price_text = f"R$ {price:.2f}"
    draw.text((80, 180), price_text, fill=(100, 200, 255), font=font_large)

    # Variação percentual
    change_color = (50, 255, 100) if change_percent >= 0 else (255, 80, 80)
    change_emoji = "▲" if change_percent >= 0 else "▼"
    change_text = f"{change_emoji} {change_percent:+.2f}%"
    draw.text((80, 300), change_text, fill=change_color, font=font_medium)

    # Linha decorativa
    draw.line([(80, 380), (1840, 380)], fill=(50, 50, 70), width=2)

    # Gráfico de barras simulado (variação ao longo do dia)
    bar_count = 20
    bar_width = 60
    bar_spacing = 30
    start_x = 200
    base_y = 800

    for i in range(bar_count):
        # Dados simulados com variação pseudo-aleatória mas determinística
        seed = (i * 17 + int(abs(change_percent) * 100)) % 100
        bar_height = 100 + (seed % 200)
        bar_x = start_x + i * (bar_width + bar_spacing)
        bar_y = base_y - bar_height

        # Cor baseada na tendência
        is_up = (seed + i) % 3 != 0 if change_percent >= 0 else (seed + i) % 3 == 0
        color = (50, 180, 100) if is_up else (220, 60, 60)

        draw.rectangle(
            [bar_x, bar_y, bar_x + bar_width, base_y],
            fill=color,
            outline=(80, 80, 100),
            width=1,
        )

    # Rodapé
    draw.text((80, 980), "Fábrica de Vídeos Dark", fill=(80, 80, 120), font=font_small)
    draw.text((1500, 980), "Análise Automatizada", fill=(80, 80, 120), font=font_small)

    img.save(str(output_path))
    logger.info(f"[Render] Imagem de gráfico criada: {output_path}")
    return output_path


def render_video(
    script_text: str,
    audio_path: Path,
    ticker: str,
    price: float,
    change_percent: float,
    output_path: Path,
    chart_image_path: Optional[Path] = None,
) -> Path:
    """
    Renderiza o vídeo final juntando:
    - Imagem de gráfico (estágio de processamento de imagem)
    - Áudio de locução (edge-tts)
    - Legendas dinâmicas

    Usa moviepy com chamadas diretas ao ffmpeg.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not check_ffmpeg():
        raise RuntimeError("ffmpeg não encontrado. Instale com: brew install ffmpeg")

    logger.info(f"[Render] Iniciando renderização do vídeo: {output_path}")

    # 1. Carregar áudio de locução
    audio_clip = AudioFileClip(str(audio_path))
    audio_duration = audio_clip.duration
    logger.info(f"[Render] Duração do áudio: {audio_duration:.1f}s")

    # 2. Criar ou usar imagem de gráfico
    if chart_image_path is None or not chart_image_path.exists():
        chart_image_path = settings.temp_dir / f"chart_{ticker}.png"
        create_chart_image(ticker, price, change_percent, chart_image_path)

    # 3. Criar clip de vídeo a partir da imagem (duração = áudio)
    video_clip = (
        ImageClip(str(chart_image_path))
        .with_duration(audio_duration)
        .with_audio(audio_clip)
    )

    # 4. Adicionar legendas dinâmicas
    # Fonte do sistema macOS (moviepy 2.x exige caminho de ficheiro)
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    if not os.path.exists(font_path):
        # Fallback: procurar outra fonte disponivel
        for fp in ["/System/Library/Fonts/SFNS.ttf", "/Library/Fonts/Arial.ttf"]:
            if os.path.exists(fp):
                font_path = fp
                break

    try:
        # Dividir o script em segmentos para legendas
        sentences = [s.strip() for s in script_text.replace("...", " ").split(". ") if s.strip()]
        subtitle_duration = audio_duration / max(len(sentences), 1)

        subtitle_clips = []
        for i, sentence in enumerate(sentences):
            start = i * subtitle_duration
            end = min(start + subtitle_duration, audio_duration)

            # Texto da legenda com estilo dark
            txt_clip = (
                TextClip(
                    text=sentence[:80],
                    font=font_path,
                    font_size=48,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    size=(int(settings.video_width * 0.8), None),
                    text_align="center",
                    method="caption",
                )
                .with_position(("center", "bottom"))
                .with_start(start)
                .with_duration(end - start)
            )
            subtitle_clips.append(txt_clip)

        if subtitle_clips:
            final_video = CompositeVideoClip([video_clip] + subtitle_clips)
        else:
            final_video = video_clip
    except Exception as e:
        logger.warning(f"[Render] Não foi possível adicionar legendas: {e}")
        final_video = video_clip

    # 5. Exportar vídeo final
    final_video.write_videofile(
        str(output_path),
        fps=settings.video_fps,
        codec=settings.video_codec,
        audio_codec=settings.audio_codec,
        temp_audiofile=str(settings.temp_dir / f"temp_audio_{ticker}.m4a"),
        remove_temp=True,
        threads=4,
        preset="medium",
        logger="bar",
    )

    # Limpar clips da memória
    final_video.close()
    video_clip.close()
    audio_clip.close()

    logger.info(f"[Render] Vídeo renderizado com sucesso: {output_path}")
    return output_path


def get_video_duration(video_path: Path) -> float:
    """Retorna a duração de um vídeo em segundos usando ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                str(video_path),
            ],
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception:
        return 0.0
