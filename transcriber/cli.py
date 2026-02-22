"""Entry point CLI com argparse."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .utils import MODELS, check_ffmpeg, collect_media_files, format_duration

console = Console()


def list_models() -> None:
    """Lista modelos disponíveis com tamanho e VRAM estimada."""
    table = Table(title="Modelos disponíveis")
    table.add_column("Modelo", style="bold cyan")
    table.add_column("Tamanho", justify="right")
    table.add_column("VRAM estimada", justify="right")

    for name, info in MODELS.items():
        table.add_row(name, info["size"], info["vram"])

    console.print(table)
    console.print(
        "\n[dim]Default: large-v3-turbo. "
        "Modelos menores são mais rápidos mas menos precisos.[/dim]"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="transcriber",
        description="Transcrição local de vídeos/áudios usando faster-whisper.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Arquivo de vídeo/áudio ou diretório para batch.",
    )
    parser.add_argument(
        "--lang",
        "-l",
        default=None,
        help="Código do idioma (pt, en, es, etc). Default: auto-detect.",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="large-v3-turbo",
        choices=list(MODELS.keys()),
        help="Modelo whisper. Default: large-v3-turbo.",
    )
    parser.add_argument(
        "--format",
        "-f",
        default="txt",
        choices=["txt", "srt", "vtt", "json"],
        dest="output_format",
        help="Formato de saída. Default: txt.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Arquivo de saída. Default: mesmo nome do input com extensão do formato.",
    )
    parser.add_argument(
        "--device",
        default="cuda",
        choices=["cuda", "cpu"],
        help="Device para inferência. Default: cuda.",
    )
    parser.add_argument(
        "--compute-type",
        default="float16",
        choices=["float16", "int8_float16", "int8"],
        help="Tipo de computação. Default: float16.",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=5,
        help="Beam size para decodificação. Default: 5.",
    )
    parser.add_argument(
        "--vad",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Ativar/desativar VAD filter (Silero). Default: ativado.",
    )
    parser.add_argument(
        "--word-timestamps",
        action="store_true",
        default=False,
        help="Incluir timestamps por palavra.",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Lista modelos disponíveis com tamanho e VRAM estimada.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Modo verboso com detalhes de cada segmento.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_models:
        list_models()
        return

    if args.input is None:
        parser.print_help()
        sys.exit(1)

    try:
        check_ffmpeg()
    except RuntimeError as e:
        console.print(f"[bold red]Erro:[/bold red] {e}")
        sys.exit(1)

    try:
        files = collect_media_files(args.input)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Erro:[/bold red] {e}")
        sys.exit(1)

    from .transcribe import load_model, process_file

    try:
        model, device = load_model(args.model, args.device, args.compute_type)
    except Exception as e:
        console.print(f"[bold red]Erro ao carregar modelo:[/bold red] {e}")
        sys.exit(1)

    batch = len(files) > 1
    total_start = time.time()

    for i, file_path in enumerate(files, start=1):
        if batch:
            console.print(
                f"\n[bold cyan]Arquivo {i} de {len(files)}[/bold cyan]"
            )

        output_path = args.output if not batch else None

        try:
            process_file(
                model,
                file_path,
                language=args.lang,
                beam_size=args.beam_size,
                vad_filter=args.vad,
                word_timestamps=args.word_timestamps,
                verbose=args.verbose,
                output_format=args.output_format,
                output_path=output_path,
            )
        except Exception as e:
            console.print(f"[bold red]Erro processando {file_path.name}:[/bold red] {e}")
            if batch:
                continue
            sys.exit(1)

    total_elapsed = time.time() - total_start

    if batch:
        console.print(
            f"\n[bold green]Concluído![/bold green] "
            f"{len(files)} arquivos em {format_duration(total_elapsed)}"
        )


if __name__ == "__main__":
    main()
