"""R1069 — QA técnico de vídeo com ffprobe/ffmpeg, sem shell e sem rede.

Verifica metadados, quadros pretos, silêncio, loudness integrada e extrai
frames para inspeção humana. Não avalia qualidade estética e não substitui
revisão humana; máquina não promove confiança.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
import shutil
import subprocess
from typing import Any, Dict, List

MAX_TIMEOUT = 180
BLACK_RE = re.compile(r"black_start:([0-9.]+)\s+black_end:([0-9.]+)\s+black_duration:([0-9.]+)")
SILENCE_START_RE = re.compile(r"silence_start:\s*(-?[0-9.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)")
LOUDNESS_RE = re.compile(r"I:\s*(-?[0-9.]+)\s*LUFS")
LRA_RE = re.compile(r"LRA:\s*(-?[0-9.]+)\s*LU")
PEAK_RE = re.compile(r"Peak:\s*(-?[0-9.]+)\s*dBFS")


def _run(argv: List[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, shell=False)


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _probe_metadata(path: Path) -> Dict[str, Any]:
    result = _run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                   "-of", "json", str(path)], 30)
    if result.returncode != 0:
        raise ValueError("ffprobe falhou: " + (result.stderr or "")[-500:])
    data = json.loads(result.stdout or "{}")
    streams = data.get("streams") or []
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    fmt = data.get("format") or {}
    return {
        "duration_seconds": _number(fmt.get("duration")),
        "size_bytes": _number(fmt.get("size")),
        "format_name": fmt.get("format_name"),
        "video": ({key: video.get(key) for key in
                   ("codec_name", "width", "height", "r_frame_rate", "nb_frames")}
                  if video else None),
        "audio": ({key: audio.get(key) for key in
                   ("codec_name", "sample_rate", "channels")}
                  if audio else None),
    }


def _black_intervals(path: Path, timeout: int) -> List[Dict[str, float]]:
    result = _run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                   "-vf", "blackdetect=d=0.1:pix_th=0.10", "-an", "-f", "null", "-"],
                  timeout)
    text = (result.stderr or "") + (result.stdout or "")
    return [
        {"start": float(start), "end": float(end), "duration": float(duration)}
        for start, end, duration in BLACK_RE.findall(text)
    ]


def _silence_intervals(path: Path, timeout: int) -> List[Dict[str, float]]:
    result = _run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                   "-af", "silencedetect=noise=-50dB:d=0.5", "-vn", "-f", "null", "-"],
                  timeout)
    text = (result.stderr or "") + (result.stdout or "")
    starts = [float(value) for value in SILENCE_START_RE.findall(text)]
    ends = [(float(end), float(duration)) for end, duration in SILENCE_END_RE.findall(text)]
    rows = []
    for index, start in enumerate(starts):
        end = ends[index][0] if index < len(ends) else start
        duration = ends[index][1] if index < len(ends) else 0.0
        rows.append({"start": start, "end": end, "duration": duration})
    return rows


def _loudness(path: Path, timeout: int) -> Dict[str, float | None]:
    result = _run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                   "-af", "ebur128=peak=true", "-f", "null", "-"], timeout)
    text = (result.stderr or "") + (result.stdout or "")
    integrated = LOUDNESS_RE.findall(text)
    lra = LRA_RE.findall(text)
    peak = PEAK_RE.findall(text)
    return {
        "integrated_lufs": _number(integrated[-1]) if integrated else None,
        "lra_lu": _number(lra[-1]) if lra else None,
        "true_peak_dbfs": _number(peak[-1]) if peak else None,
    }


def _extract_frames(path: Path, output_dir: Path, duration: float | None,
                    count: int, timeout: int) -> List[Dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    if duration is None or duration <= 0:
        return []
    count = max(1, min(12, count))
    frames = []
    for index in range(count):
        point = duration * (index + 1) / (count + 1)
        target = output_dir / f"frame-{index + 1:02d}.png"
        result = _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                       "-ss", f"{point:.3f}", "-i", str(path), "-frames:v", "1",
                       str(target)], timeout)
        if result.returncode == 0 and target.is_file():
            frames.append({"seconds": round(point, 3), "path": str(target),
                           "size_bytes": target.stat().st_size})
    return frames


def probe(path: str | Path, *, output_dir: str | Path | None = None,
          frames: int = 3, timeout: int = 120) -> Dict[str, Any]:
    """Executa o QA técnico; não executa o vídeo como programa."""
    if not isinstance(path, (str, Path)) or not str(path).strip():
        raise ValueError("caminho do vídeo é obrigatório")
    if type(frames) is not int or not 1 <= frames <= 12:
        raise ValueError("frames deve estar entre 1 e 12")
    if type(timeout) is not int or not 10 <= timeout <= MAX_TIMEOUT:
        raise ValueError(f"timeout deve estar entre 10 e {MAX_TIMEOUT}")
    target = Path(path).expanduser()
    if not target.is_file():
        raise ValueError("vídeo local inexistente")
    if target.stat().st_size <= 0:
        raise ValueError("vídeo vazio")
    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            raise ValueError(f"{binary} ausente")
    metadata = _probe_metadata(target)
    duration = metadata.get("duration_seconds")
    black = _black_intervals(target, timeout)
    silence = _silence_intervals(target, timeout) if metadata.get("audio") else []
    loudness = _loudness(target, timeout) if metadata.get("audio") else {}
    frames_dir = Path(output_dir).expanduser() if output_dir else target.parent / "qa-frames"
    extracted = _extract_frames(target, frames_dir, duration, frames, timeout)
    issues: List[str] = []
    if any(row["duration"] >= 0.2 for row in black):
        issues.append("black_frames")
    if any(row["duration"] >= 1.0 for row in silence):
        issues.append("silence")
    if loudness.get("integrated_lufs") is not None and not -30 <= loudness["integrated_lufs"] <= -10:
        issues.append("loudness_out_of_range")
    return {
        "status": "completed",
        "video": str(target.resolve()),
        "metadata": metadata,
        "black_intervals": black,
        "silence_intervals": silence,
        "loudness": loudness,
        "frames": extracted,
        "issues": issues,
        "human_review_required": True,
        "external_validation": False,
        "limitations": [
            "QA técnico não avalia qualidade estética, narrativa ou correção científica.",
            "Black/silence/loudness são indicadores; exigem inspeção humana dos frames.",
            "Nenhum frame foi julgado automaticamente.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="video-qa", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    probe_cmd = sub.add_parser("probe")
    probe_cmd.add_argument("path")
    probe_cmd.add_argument("--output-dir")
    probe_cmd.add_argument("--frames", type=int, default=3)
    probe_cmd.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args(argv)
    try:
        payload = probe(args.path, output_dir=args.output_dir,
                        frames=args.frames, timeout=args.timeout)
    except (ValueError, OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        payload = {"status": "blocked", "error": str(exc), "executed": False}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
