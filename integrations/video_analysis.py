"""R1230: análise local de cenas e propostas de corte revisáveis.

As rotinas não aprovam cortes nem renderizam mídia. PySceneDetect é importado
sob demanda; Auto-Editor é chamado somente com ``--export v1`` em diretório
temporário privado. A conversão para frames aceita apenas limites exatamente
representáveis na taxa CFR da fonte.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path

from integrations import video_editor

VERSION = "R1230-1"
MAX_TIMELINE_BYTES = 2 * 1024 * 1024
MAX_CHUNKS = 10_000
MAX_LOG_CHARS = 4_000
VERSION_TIMEOUT_SECONDS = 10
AUTO_EDITOR_TIMEOUT_SECONDS = 300
_VERSION_RE = re.compile(r"\bversion\s+([^\s,;]+)", re.IGNORECASE)
_BARE_VERSION_RE = re.compile(r"^\s*(\d+\.\d+\.\d+(?:[-+][^\s]+)?)\s*$")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _regular_media(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_symlink():
        raise ValueError("symlink media is not allowed")
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("local media file required") from exc
    if not resolved.is_file():
        raise ValueError("regular local media file required")
    return resolved


def _fraction(value, name: str) -> Fraction:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{name} must be a positive rational number")
    try:
        if isinstance(value, (list, tuple)) and len(value) == 2:
            numerator, denominator = value
            if (type(numerator) is not int or type(denominator) is not int):
                raise ValueError
            parsed = Fraction(numerator, denominator)
        else:
            parsed = Fraction(str(value))
    except (ValueError, ZeroDivisionError, TypeError, OverflowError) as exc:
        raise ValueError(f"invalid {name} rational") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be positive")
    return parsed


def _finite_number(value, name: str) -> Fraction:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{name} must be finite numeric data")
    try:
        number = float(value)
        exact = Fraction(str(value))
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
        raise ValueError(f"invalid {name}") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return exact


def _probe(path: Path, probe_fn: Callable | None) -> dict:
    if probe_fn is None:
        return video_editor.probe_media(path, allow_silent=True)
    result = probe_fn(str(path), allow_silent=True)
    if not isinstance(result, dict):
        raise TypeError("media probe must return an object")
    return result


def _source_details(path: Path, probe: dict) -> dict:
    video = probe.get("video")
    if not isinstance(video, dict):
        raise TypeError("video stream metadata object required")
    vfr = video.get("variable_frame_rate")
    if vfr is not False:
        if vfr is True:
            raise ValueError("VFR media is not supported by frame-based analysis")
        raise ValueError("CFR status is unknown; cannot map analysis to frames")
    frames = video.get("frames")
    if isinstance(frames, bool) or not isinstance(frames, int) or frames <= 0:
        raise ValueError("positive video frame count required")
    fps = _fraction(video.get("fps"), "source fps")
    actual_hash = _sha256_file(path)
    probed_hash = probe.get("sha256")
    if probed_hash is not None and probed_hash != actual_hash:
        raise ValueError("media changed during probe or probe hash mismatch")
    return {
        "path": str(path),
        "sha256": actual_hash,
        "frames": frames,
        "fps": f"{fps.numerator}/{fps.denominator}",
        "fps_fraction": fps,
    }


def diagnose_tools(*, which_fn=shutil.which, runner=subprocess.run,
                   timeout: int = VERSION_TIMEOUT_SECONDS) -> dict:
    """Run bounded version checks and report required and optional tools."""
    if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
            or not math.isfinite(float(timeout)) or not 0 < timeout <= 60):
        raise ValueError("version-check timeout must be between 0 and 60 seconds")
    commands = {
        "ffmpeg": ("ffmpeg", ["-version"], True),
        "ffprobe": ("ffprobe", ["-version"], True),
        "auto-editor": ("auto-editor", ["--version"], False),
    }
    tools: dict[str, dict] = {}
    for key, (binary, args, required) in commands.items():
        executable = which_fn(binary)
        if not executable:
            tools[key] = {"status": "missing", "path": None, "version": None,
                          "returncode": None, "error": "executable not found",
                          "required": required}
            continue
        try:
            proc = runner([str(executable), *args], capture_output=True, text=True,
                          timeout=timeout, shell=False, check=False)
            returncode = getattr(proc, "returncode", None)
            stdout = str(getattr(proc, "stdout", "") or "")
            stderr = str(getattr(proc, "stderr", "") or "")
            combined = stdout + "\n" + stderr
            match = _VERSION_RE.search(combined)
            bare = _BARE_VERSION_RE.match(stdout.splitlines()[0]) if stdout.splitlines() else None
            status = "ready" if returncode == 0 else "failed"
            tools[key] = {
                "status": status,
                "path": str(executable),
                "version": match.group(1) if match else (bare.group(1) if bare else None),
                "returncode": returncode,
                "error": None if returncode == 0 else (stderr or stdout)[:MAX_LOG_CHARS],
                "required": required,
            }
        except (OSError, subprocess.TimeoutExpired) as exc:
            tools[key] = {"status": "failed", "path": str(executable),
                          "version": None, "returncode": None,
                          "error": f"{type(exc).__name__}: {exc}"[:MAX_LOG_CHARS],
                          "required": required}
    required_ready = all(tools[name]["status"] == "ready" for name in ("ffmpeg", "ffprobe"))
    try:
        scenedetect_available = importlib.util.find_spec("scenedetect") is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        scenedetect_available = False
    return {
        "schema_version": 1,
        "version": VERSION,
        "status": "ready" if required_ready else "blocked",
        "tools": tools,
        "python_modules": {"scenedetect": scenedetect_available},
        "note": "ready descreve apenas presença e versão dos executáveis; não valida codecs nem qualidade editorial",
    }


def _default_scene_detect(path: str, *, threshold: float, min_scene_len: int):
    try:
        from scenedetect import ContentDetector, detect
    except ImportError as exc:
        raise RuntimeError(
            "PySceneDetect ausente; instale requirements-video-analysis.txt"
        ) from exc
    return detect(
        path,
        ContentDetector(threshold=threshold, min_scene_len=min_scene_len),
        show_progress=False,
    )


def _frame_number(value) -> int:
    frame = getattr(value, "frame_num", value)
    if isinstance(frame, bool):
        raise TypeError("scene frame number must be an integer")
    try:
        integer = int(frame)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("scene frame number must be an integer") from exc
    if integer != frame:
        raise ValueError("scene frame number must be an integer")
    return integer


def detect_scene_markers(path: str | Path, *, threshold: float = 27.0,
                         min_scene_len: int = 15, probe_fn: Callable | None = None,
                         scene_detect_fn: Callable | None = None) -> dict:
    """Analyze a local CFR video and return contiguous PySceneDetect markers."""
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) \
            or not math.isfinite(float(threshold)) or float(threshold) <= 0:
        raise ValueError("threshold must be a positive finite number")
    if isinstance(min_scene_len, bool) or not isinstance(min_scene_len, int) \
            or min_scene_len <= 0:
        raise ValueError("min_scene_len must be a positive frame count")
    source = _regular_media(path)
    details = _source_details(source, _probe(source, probe_fn))
    detector = scene_detect_fn or _default_scene_detect
    scenes = detector(str(source), threshold=float(threshold), min_scene_len=min_scene_len)
    if not isinstance(scenes, (list, tuple)):
        raise TypeError("scene detector must return a list of scene boundaries")
    if len(scenes) > 10_000:
        raise ValueError("scene count exceeds limit")
    if not scenes:
        scenes = [(0, details["frames"])]
    markers = []
    expected_start = 0
    for index, scene in enumerate(scenes):
        if not isinstance(scene, (list, tuple)) or len(scene) != 2:
            raise ValueError("invalid scene boundary pair")
        start, end = (_frame_number(scene[0]), _frame_number(scene[1]))
        if start != expected_start or end <= start or end > details["frames"]:
            raise ValueError("scene boundaries must be positive, contiguous, and in range")
        markers.append({"index": index, "start_frame": start, "end_frame": end})
        expected_start = end
    if expected_start != details["frames"]:
        raise ValueError("scene boundaries must cover the complete source")
    source_info = {key: details[key] for key in ("path", "sha256", "frames", "fps")}
    return {
        "schema_version": 1,
        "kind": "scene_markers",
        "source": source_info,
        "detector": {"name": "PySceneDetect ContentDetector",
                     "threshold": float(threshold), "min_scene_len": min_scene_len},
        "markers": markers,
        "review_required": True,
        "source_modified": False,
    }


def _source_matches(document_source: str, source: Path) -> bool:
    if not document_source or "\x00" in document_source:
        return False
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", document_source):
        return False
    candidate = Path(document_source)
    if not candidate.is_absolute():
        candidate = source.parent / candidate
    try:
        return candidate.resolve(strict=True) == source
    except (OSError, RuntimeError):
        return False


def parse_auto_editor_v1(document: dict, *, source_path: str | Path,
                         probe: dict) -> dict:
    """Convert Auto-Editor v1 ticks to exact CFR frames, without rendering."""
    source = _regular_media(source_path)
    details = _source_details(source, probe)
    if not isinstance(document, dict):
        raise TypeError("Auto-Editor v1 document must be an object")
    if document.get("version") != "1":
        raise ValueError("Auto-Editor v1 version must be the string '1'")
    if not isinstance(document.get("source"), str) \
            or not _source_matches(document["source"], source):
        raise ValueError("Auto-Editor timeline source does not match registered media")
    raw_chunks = document.get("chunks")
    if not isinstance(raw_chunks, list) or len(raw_chunks) > MAX_CHUNKS:
        raise ValueError("Auto-Editor chunks must be a bounded list")
    if not raw_chunks:
        raise ValueError("empty Auto-Editor timeline cannot form a review proposal")
    timebase = _fraction(document.get("timebase", details["fps"]), "timebase")
    fps = details["fps_fraction"]
    chunks: list[tuple[int, int, str, int | None]] = []
    previous_tick_end: Fraction | None = None
    timeline_frame = 0
    kept_frames = 0
    proposed_cut_frames = 0

    for index, raw in enumerate(raw_chunks):
        if not isinstance(raw, (list, tuple)) or len(raw) != 3:
            raise ValueError(f"chunk {index} must be [start, end, speed]")
        start_tick = _finite_number(raw[0], f"chunk {index} start")
        end_tick = _finite_number(raw[1], f"chunk {index} end")
        speed = _finite_number(raw[2], f"chunk {index} speed")
        if start_tick < 0 or end_tick <= start_tick:
            raise ValueError(f"chunk {index} must have a positive half-open interval")
        if index == 0 and start_tick != 0:
            raise ValueError("first Auto-Editor chunk must start at zero")
        if previous_tick_end is not None and start_tick != previous_tick_end:
            raise ValueError("Auto-Editor chunks must be contiguous without gaps or overlaps")
        previous_tick_end = end_tick
        start_frame_exact = start_tick * fps / timebase
        end_frame_exact = end_tick * fps / timebase
        if start_frame_exact.denominator != 1 or end_frame_exact.denominator != 1:
            raise ValueError("Auto-Editor boundary does not align exactly to a source frame")
        start_frame, end_frame = int(start_frame_exact), int(end_frame_exact)
        if end_frame > details["frames"]:
            raise ValueError("Auto-Editor chunk exceeds source frame count")
        if speed in (Fraction(0), Fraction(99999)):
            action = "cut"
            proposed_cut_frames += end_frame - start_frame
            output_start = None
        elif speed == 1:
            action = "keep"
            output_start = timeline_frame
            kept_frames += end_frame - start_frame
            timeline_frame += end_frame - start_frame
        else:
            raise ValueError("only normal speed or Auto-Editor cut speeds are supported")
        chunks.append((start_frame, end_frame, action, output_start))

    if previous_tick_end is None or previous_tick_end * fps / timebase != details["frames"]:
        raise ValueError("Auto-Editor timeline must cover the complete source")
    segments = [
        {"index": index, "in_frame": start, "out_frame": end,
         "action": action, "timeline_start_frame": output_start}
        for index, (start, end, action, output_start) in enumerate(chunks)
    ]
    source_info = {key: details[key] for key in ("path", "sha256", "frames", "fps")}
    return {
        "schema_version": 1,
        "kind": "rough_cut_proposal",
        "source": source_info,
        "timebase": f"{timebase.numerator}/{timebase.denominator}",
        "segments": segments,
        "summary": {"source_frames": details["frames"],
                    "kept_frames": kept_frames,
                    "proposed_cut_frames": proposed_cut_frames,
                    "output_frames_if_approved": kept_frames},
        "approval_state": "pending",
        "review_required": True,
        "rendered": False,
        "limitations": [
            "Proposta automática não é decisão editorial nem aprovação.",
            "Somente CFR, limites alinhados a frames e velocidade normal/corte são aceitos.",
        ],
    }


def _read_limited(path: Path, limit: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Auto-Editor did not create a regular v1 export")
    if path.stat().st_size > limit:
        raise RuntimeError("Auto-Editor v1 export exceeds size limit")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise RuntimeError("Auto-Editor v1 export exceeds size limit")
    return data


def propose_auto_editor_cuts(path: str | Path, *, probe_fn: Callable | None = None,
                             runner=subprocess.run,
                             timeout: int = AUTO_EDITOR_TIMEOUT_SECONDS) -> dict:
    """Export Auto-Editor v1 to a private temporary file and return a proposal."""
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) \
            or not math.isfinite(float(timeout)) or not 0 < timeout <= 600:
        raise ValueError("Auto-Editor timeout must be between 0 and 600 seconds")
    source = _regular_media(path)
    probe = _probe(source, probe_fn)
    details = _source_details(source, probe)
    executable = shutil.which("auto-editor")
    if not executable:
        raise RuntimeError("auto-editor CLI is not installed or not on PATH")
    original_hash = details["sha256"]
    with tempfile.TemporaryDirectory(prefix="video-analysis-") as temporary:
        temp_root = Path(temporary)
        export_path = temp_root / "proposal.v1"
        argv = [str(executable), str(source), "--export", "v1", "-o", str(export_path)]
        try:
            proc = runner(
                argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, timeout=timeout, shell=False,
                check=False, cwd=str(temp_root),
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("auto-editor export timed out") from exc
        except OSError as exc:
            raise RuntimeError(f"auto-editor could not execute: {exc}") from exc
        returncode = getattr(proc, "returncode", None)
        if returncode != 0:
            raise RuntimeError(f"auto-editor export failed (exit code {returncode})")
        if _sha256_file(source) != original_hash:
            raise RuntimeError("source media changed during Auto-Editor export")
        try:
            resolved_export = export_path.resolve(strict=True)
            if not resolved_export.is_relative_to(temp_root.resolve()):
                raise RuntimeError("Auto-Editor export escaped the temporary directory")
            raw = _read_limited(export_path, MAX_TIMELINE_BYTES)
            document = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"invalid Auto-Editor v1 export: {exc}") from exc
        return parse_auto_editor_v1(document, source_path=source, probe=probe)
