"""Helpers: extração de áudio, timestamps, validações e progress."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}
SUPPORTED_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS

MODELS = {
    "tiny": {"size": "~75 MB", "vram": "~1 GB"},
    "base": {"size": "~145 MB", "vram": "~1 GB"},
    "small": {"size": "~488 MB", "vram": "~2 GB"},
    "medium": {"size": "~1.5 GB", "vram": "~5 GB"},
    "large-v3": {"size": "~3.1 GB", "vram": "~10 GB"},
    "large-v3-turbo": {"size": "~1.6 GB", "vram": "~6 GB"},
}


def check_ffmpeg() -> None:
    """Verifica se ffmpeg está instalado no sistema."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg não encontrado no PATH. Instale com: sudo apt install ffmpeg"
        )


def check_cuda_available() -> bool:
    """Retorna True se CUDA estiver disponível via CTranslate2."""
    try:
        import ctranslate2

        # Se get_supported_compute_types("cuda") não lançar exceção,
        # significa que o device CUDA é suportado.
        ctranslate2.get_supported_compute_types("cuda")
        return True
    except Exception:
        return False


def is_supported_file(path: Path) -> bool:
    """Verifica se o arquivo tem extensão suportada."""
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def collect_media_files(path: Path) -> list[Path]:
    """Coleta arquivos de mídia de um arquivo ou diretório."""
    if path.is_file():
        if not is_supported_file(path):
            raise ValueError(
                f"Formato não suportado: {path.suffix}\n"
                f"Formatos suportados: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )
        return [path]

    if path.is_dir():
        files = sorted(
            f for f in path.iterdir() if f.is_file() and is_supported_file(f)
        )
        if not files:
            raise ValueError(f"Nenhum arquivo de mídia encontrado em: {path}")
        return files

    raise FileNotFoundError(f"Arquivo ou diretório não encontrado: {path}")


def extract_audio(input_path: Path) -> Path:
    """Extrai áudio de vídeo para WAV 16kHz mono usando ffmpeg.

    Se o input já for áudio, retorna o caminho original.
    """
    if input_path.suffix.lower() in AUDIO_EXTENSIONS:
        return input_path

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    tmp_path = Path(tmp.name)

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                str(input_path),
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                "-y",
                str(tmp_path),
            ],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"Erro ao extrair áudio de {input_path.name}:\n{e.stderr.decode()}"
        ) from e

    return tmp_path


def get_audio_duration(path: Path) -> float:
    """Retorna a duração do áudio/vídeo em segundos usando ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def format_timestamp_srt(seconds: float) -> str:
    """Formata segundos para timestamp SRT: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Formata segundos para timestamp VTT: HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def format_duration(seconds: float) -> str:
    """Formata duração de forma legível: 1h 23min 45s."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}min {s}s"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}min {s}s"
