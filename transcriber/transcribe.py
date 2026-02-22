"""Core de transcrição usando faster-whisper."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from .formatter import FORMAT_EXTENSIONS, FORMATTERS
from .utils import (
    check_cuda_available,
    extract_audio,
    format_duration,
    get_audio_duration,
)

console = Console()


def load_model(
    model_name: str,
    device: str,
    compute_type: str,
) -> Any:
    """Carrega o modelo faster-whisper com fallback para CPU."""
    from faster_whisper import WhisperModel

    if device == "cuda" and not check_cuda_available():
        console.print(
            "[yellow]CUDA não disponível. Usando CPU como fallback.[/yellow]"
        )
        device = "cpu"
        compute_type = "int8"

    console.print(
        f"[bold]Modelo:[/bold] {model_name} | "
        f"[bold]Device:[/bold] {device} | "
        f"[bold]Compute:[/bold] {compute_type}"
    )

    with console.status("[bold green]Carregando modelo..."):
        model = WhisperModel(model_name, device=device, compute_type=compute_type)

    console.print("[green]Modelo carregado.[/green]")
    return model, device


def transcribe_file(
    model: Any,
    input_path: Path,
    *,
    language: str | None = None,
    beam_size: int = 5,
    vad_filter: bool = True,
    word_timestamps: bool = False,
    verbose: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Transcreve um arquivo e retorna (segmentos, info)."""
    duration = get_audio_duration(input_path)
    if duration > 0:
        console.print(f"[bold]Duração:[/bold] {format_duration(duration)}")

    audio_path = extract_audio(input_path)
    temp_audio = audio_path != input_path

    try:
        segments_iter, info = model.transcribe(
            str(audio_path),
            language=language,
            beam_size=beam_size,
            vad_filter=vad_filter,
            vad_parameters={"min_silence_duration_ms": 500},
            word_timestamps=word_timestamps,
        )

        detected_lang = info.language
        lang_prob = info.language_probability
        if language is None:
            console.print(
                f"[bold]Idioma detectado:[/bold] {detected_lang} "
                f"(probabilidade: {lang_prob:.0%})"
            )

        segments: list[dict[str, Any]] = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Transcrevendo...",
                total=duration if duration > 0 else None,
            )

            for seg in segments_iter:
                entry: dict[str, Any] = {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text,
                }
                if word_timestamps and seg.words:
                    entry["words"] = [
                        {"start": w.start, "end": w.end, "word": w.word}
                        for w in seg.words
                    ]
                segments.append(entry)

                if verbose:
                    progress.console.print(
                        f"  [{format_duration(seg.start)} → {format_duration(seg.end)}] "
                        f"{seg.text.strip()}"
                    )

                if duration > 0:
                    progress.update(task, completed=min(seg.end, duration))

            if duration > 0:
                progress.update(task, completed=duration)

        meta = {
            "language": detected_lang,
            "language_probability": lang_prob,
            "duration": duration,
        }
        return segments, meta

    finally:
        if temp_audio:
            audio_path.unlink(missing_ok=True)


def process_file(
    model: Any,
    input_path: Path,
    *,
    language: str | None = None,
    beam_size: int = 5,
    vad_filter: bool = True,
    word_timestamps: bool = False,
    verbose: bool = False,
    output_format: str = "txt",
    output_path: Path | None = None,
) -> Path:
    """Transcreve um arquivo e salva no formato escolhido."""
    console.rule(f"[bold]{input_path.name}")

    start_time = time.time()

    segments, meta = transcribe_file(
        model,
        input_path,
        language=language,
        beam_size=beam_size,
        vad_filter=vad_filter,
        word_timestamps=word_timestamps,
        verbose=verbose,
    )

    elapsed = time.time() - start_time
    duration = meta["duration"]

    formatter = FORMATTERS[output_format]
    content = formatter(segments)

    if output_path is None:
        ext = FORMAT_EXTENSIONS[output_format]
        output_path = input_path.with_suffix(ext)

    output_path.write_text(content, encoding="utf-8-sig")

    console.print(f"[green]Salvo em:[/green] {output_path}")

    if duration > 0 and elapsed > 0:
        speed = duration / elapsed
        console.print(
            f"[bold]{format_duration(duration)}[/bold] de áudio em "
            f"[bold]{format_duration(elapsed)}[/bold] — "
            f"[bold green]{speed:.0f}x realtime[/bold green]"
        )

    return output_path
