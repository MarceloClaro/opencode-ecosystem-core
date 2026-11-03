"""R1031 — apresentadora falando nos cartões, com lip sync por vídeo."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilots/r1026-quantum"
TEMPLATE = PILOT / "remotion-template"
TSX = TEMPLATE / "src/DidacticIntroOutro.tsx"


def ffprobe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_lipsync_scripts() -> None:
    for name in ("render-presenter-card-lipsync.sh", "compose-presenter-card.py"):
        path = PILOT / name
        assert path.is_file(), f"{name} ausente"
        assert path.stat().st_mode & 0o111, f"{name} precisa ser executável"

    lip = (PILOT / "render-presenter-card-lipsync.sh").read_text(encoding="utf-8")
    for marker in (
        "Wav2Lip",
        "MAX_RSS_MB",
        "flock",
        "tpad",
        "presenter-$LABEL-1080.mp4",
        "wav2lip_batch_size",
    ):
        assert marker in lip, marker

    whole = (PILOT / "render-presenter-card-whole.sh").read_text(encoding="utf-8")
    for marker in (
        "Wav2Lip",
        "MAX_RSS_MB",
        "flock",
        "tpad",
        "presenter-$LABEL-1080.mp4",
        "inference.py",
    ):
        assert marker in whole, marker

    comp = (PILOT / "compose-presenter-card.py").read_text(encoding="utf-8")
    for marker in (
        "CROP_X, CROP_Y, CROP_W, CROP_H = 1180, 100, 560, 700",
        "score = value * (1.0 - saturation)",
        "card-bg-560x700.png",
        "alpha[-20:, :] = 0",
    ):
        assert marker in comp, marker


def test_talking_presenter_assets() -> None:
    for name, width, height, duration in (
        ("presenter-intro-1080.mp4", 1920, 1080, 14.2),
        ("presenter-outro-1080.mp4", 1920, 1080, 9.8),
        ("presenter-intro-card.mp4", 560, 700, 14.187),
        ("presenter-outro-card.mp4", 560, 700, 9.813),
    ):
        data = ffprobe(PILOT / name)
        assert abs(float(data["format"]["duration"]) - duration) < 0.35, name
        video = [s for s in data["streams"] if s["codec_type"] == "video"][0]
        assert video["width"] == width and video["height"] == height, name
        assert "audio" not in [s["codec_type"] for s in data["streams"]], name


def test_tsx_uses_video_presenter() -> None:
    text = TSX.read_text(encoding="utf-8")
    for marker in (
        "Video",
        "presenter-intro-card.mp4",
        "presenter-outro-card.mp4",
        "muted",
        'objectFit: "cover"',
        "const PresenterCard: React.FC<{ vertical: boolean; video?: string }>",
    ):
        assert marker in text, marker


def test_final_masters_match_r1031_hashes() -> None:
    hashes_path = PILOT / "hashes-r1031.txt"
    assert hashes_path.is_file(), "hashes-r1031.txt ausente"
    hashes = {}
    for line in hashes_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2:
            hashes[parts[1]] = parts[0]
    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    for name, width, height in (
        ("pilot-16x9-didatico-voz.mp4", 1920, 1080),
        ("pilot-9x16-didatico-voz.mp4", 1080, 1920),
    ):
        assert name in hashes, name
        assert manifest["files"][name]["sha256"] == hashes[name], name
        data = ffprobe(PILOT / name)
        assert abs(float(data["format"]["duration"]) - 44.0) < 0.2
        streams = {s["codec_type"]: s for s in data["streams"]}
        assert streams["video"]["width"] == width
        assert streams["video"]["height"] == height
        assert streams["audio"]["codec_name"] == "aac"


def test_docs_record_talking_presenter() -> None:
    readme = (PILOT / "README.md").read_text(encoding="utf-8").lower()
    for phrase in ("lip sync", "apresentadora", "vídeo", "cartões"):
        assert phrase in readme, phrase

    discoveries = (PILOT / "DISCOVERIES.md").read_text(encoding="utf-8")
    sections = re.split(r"(?m)^## (\d+)\. ", discoveries)[1:]
    assert len(sections) // 2 >= 18, "menos de 18 descobertas"
    lowered = discoveries.lower()
    for phrase in ("lip sync", "cartões", "wav2lip"):
        assert phrase in lowered, phrase

    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    files = manifest["files"]
    for name in (
        "presenter-intro-1080.mp4",
        "presenter-outro-1080.mp4",
        "presenter-intro-card.mp4",
        "presenter-outro-card.mp4",
        "render-presenter-card-lipsync.sh",
        "compose-presenter-card.py",
    ):
        assert name in files, name


def test_skill_mentions_talking_presenter() -> None:
    text = (ROOT / ".opencode/skills/video-didatico-tecnico/SKILL.md").read_text(
        encoding="utf-8"
    ).lower()
    for phrase in ("apresentadora", "lip sync", "vídeo"):
        assert phrase in text, phrase
