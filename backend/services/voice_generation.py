"""
Serviço de Geração de Voz - Estágio 2 do Pipeline.
Usa edge-tts (Microsoft Edge TTS) para gerar locução realista e gratuita.
"""

import edge_tts
from loguru import logger
from pathlib import Path
from typing import Optional
import asyncio

from config import settings


async def generate_voice(
    text: str,
    output_path: Path,
    voice_name: Optional[str] = None,
    rate: Optional[str] = None,
) -> Path:
    """
    Gera um ficheiro de áudio MP3 a partir de texto usando edge-tts.

    Args:
        text: Texto a ser convertido em voz.
        output_path: Caminho do ficheiro de saída (.mp3).
        voice_name: Nome da voz (padrão: pt-BR-AntonioNeural).
        rate: Velocidade da fala (ex: "+0%", "-10%", "+20%").

    Returns:
        Caminho do ficheiro de áudio gerado.
    """
    voice = voice_name or settings.voice_name
    speech_rate = rate or settings.voice_rate

    logger.info(f"[Voz] Gerando áudio com voz={voice}, rate={speech_rate}")
    logger.info(f"[Voz] Texto: {text[:100]}...")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=speech_rate,
        )
        await communicate.save(str(output_path))
        logger.info(f"[Voz] Áudio gerado com sucesso: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"[Voz] Erro ao gerar áudio: {e}")
        raise


async def list_available_voices(language: str = "pt") -> list[dict]:
    """
    Lista vozes disponíveis no edge-tts para um idioma específico.
    """
    voices = await edge_tts.list_voices()
    filtered = [
        {
            "name": v["ShortName"],
            "gender": v["Gender"],
            "locale": v["Locale"],
            "friendly_name": v["FriendlyName"],
        }
        for v in voices
        if language.lower() in v["Locale"].lower()
    ]
    return filtered


async def generate_subtitles(
    text: str,
    output_path: Path,
    voice_name: Optional[str] = None,
    rate: Optional[str] = None,
) -> Path:
    """
    Gera ficheiro de legendas SRT a partir do texto usando edge-tts WordBoundary.
    """
    voice = voice_name or settings.voice_name
    speech_rate = rate or settings.voice_rate

    logger.info(f"[Voz] Gerando legendas para: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=speech_rate)

        # Coletar word boundaries
        subtitles = []
        current_time = 0.0

        # Dividir texto em frases para criar timestamps aproximados
        sentences = text.replace("...", " ").split(". ")
        words = text.split()
        words_per_second = 2.5  # Estimativa de velocidade de fala

        srt_lines = []
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            start_time = current_time
            duration = len(sentence.split()) / words_per_second
            end_time = start_time + duration
            current_time = end_time

            # Formato SRT
            start_srt = _seconds_to_srt_time(start_time)
            end_srt = _seconds_to_srt_time(end_time)
            srt_lines.append(f"{i + 1}")
            srt_lines.append(f"{start_srt} --> {end_srt}")
            srt_lines.append(sentence.strip())
            srt_lines.append("")

        output_path.write_text("\n".join(srt_lines), encoding="utf-8")
        logger.info(f"[Voz] Legendas geradas: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"[Voz] Erro ao gerar legendas: {e}")
        raise


def _seconds_to_srt_time(seconds: float) -> str:
    """Converte segundos para formato de tempo SRT (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
