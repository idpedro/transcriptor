"""Formatadores de saída: SRT, VTT, TXT, JSON."""

from __future__ import annotations

import json
from typing import Any

from .utils import format_timestamp_srt, format_timestamp_vtt


def format_srt(segments: list[dict[str, Any]]) -> str:
    """Gera saída no formato SRT."""
    lines: list[str] = []
    for i, seg in enumerate(segments, start=1):
        start = format_timestamp_srt(seg["start"])
        end = format_timestamp_srt(seg["end"])
        lines.append(f"{i}")
        lines.append(f"{start} --> {end}")
        lines.append(seg["text"].strip())
        lines.append("")
    return "\n".join(lines)


def format_vtt(segments: list[dict[str, Any]]) -> str:
    """Gera saída no formato WebVTT."""
    lines: list[str] = ["WEBVTT", ""]
    for seg in segments:
        start = format_timestamp_vtt(seg["start"])
        end = format_timestamp_vtt(seg["end"])
        lines.append(f"{start} --> {end}")
        lines.append(seg["text"].strip())
        lines.append("")
    return "\n".join(lines)


def format_txt(segments: list[dict[str, Any]]) -> str:
    """Gera saída em texto puro."""
    return "\n".join(seg["text"].strip() for seg in segments) + "\n"


def format_json(segments: list[dict[str, Any]]) -> str:
    """Gera saída em JSON com timestamps."""
    data = []
    for seg in segments:
        entry: dict[str, Any] = {
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
        }
        if seg.get("words"):
            entry["words"] = [
                {
                    "start": round(w["start"], 2),
                    "end": round(w["end"], 2),
                    "word": w["word"],
                }
                for w in seg["words"]
            ]
        data.append(entry)
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


FORMATTERS = {
    "srt": format_srt,
    "vtt": format_vtt,
    "txt": format_txt,
    "json": format_json,
}

FORMAT_EXTENSIONS = {
    "srt": ".srt",
    "vtt": ".vtt",
    "txt": ".txt",
    "json": ".json",
}
