"""R1032 — cenário único: sem concatenar o miolo antigo."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilots/r1026-quantum"
TEMPLATE = PILOT / "remotion-template"


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


def test_concat_uses_only_the_new_middle() -> None:
    text = (PILOT / "concat-didatico.sh").read_text(encoding="utf-8")
    for marker in ("didactic-middle-16.mp4", "didactic-middle-9.mp4"):
        assert marker in text, marker
    for legacy in (
        "pilot-16x9-didatico-base.mp4",
        "pilot-9x16-didatico-base.mp4",
    ):
        assert legacy not in text, legacy


def test_new_middle_assets() -> None:
    for name, width, height in (
        ("didactic-middle-16.mp4", 1920, 1080),
        ("didactic-middle-9.mp4", 1080, 1920),
    ):
        data = ffprobe(PILOT / name)
        assert abs(float(data["format"]["duration"]) - 20.0) < 0.35, name
        streams = {s["codec_type"]: s for s in data["streams"]}
        assert streams["video"]["width"] == width
        assert streams["video"]["height"] == height
        assert streams["audio"]["codec_name"] == "aac"

    slide = ffprobe(PILOT / "slide-sequence-dark.mp4")
    assert abs(float(slide["format"]["duration"]) - 20.0) < 0.2
    slide_video = [s for s in slide["streams"] if s["codec_type"] == "video"][0]
    assert slide_video["width"] == 934 and slide_video["height"] == 864
    assert "audio" not in [s["codec_type"] for s in slide["streams"]]

    presenter = ffprobe(PILOT / "presenter-middle-card.mp4")
    assert abs(float(presenter["format"]["duration"]) - 20.0) < 0.2
    presenter_video = [s for s in presenter["streams"] if s["codec_type"] == "video"][0]
    assert presenter_video["width"] == 560 and presenter_video["height"] == 700
    assert "audio" not in [s["codec_type"] for s in presenter["streams"]]


def test_middle_composition_uses_dark_slide_and_presenter() -> None:
    text = (TEMPLATE / "src/DidacticMiddle.tsx").read_text(encoding="utf-8")
    for marker in (
        "slide-sequence-dark.mp4",
        "presenter-middle-card.mp4",
        "middle-clone.wav",
        "DidacticMiddle",
    ):
        assert marker in text, marker
    root = (TEMPLATE / "src/Root.tsx").read_text(encoding="utf-8")
    assert "DidacticMiddle16" in root
    assert "DidacticMiddle9" in root
    dark = (TEMPLATE / "src/DarkSlideSequence.tsx").read_text(encoding="utf-8")
    assert 'const BG = "#0F0B18"' in dark


def test_final_masters_match_r1032_hashes() -> None:
    hashes_path = PILOT / "hashes-r1031.txt"
    assert hashes_path.is_file()
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
        assert abs(float(data["format"]["duration"]) - 44.1) < 0.25
        streams = {s["codec_type"]: s for s in data["streams"]}
        assert streams["video"]["width"] == width
        assert streams["video"]["height"] == height
        assert streams["audio"]["codec_name"] == "aac"


def test_docs_record_single_scenario_and_continuous_pass() -> None:
    readme = (PILOT / "README.md").read_text(encoding="utf-8").lower()
    for phrase in ("não usa", "cenário escuro", "didactic-middle", "passada contínua"):
        assert phrase in readme, phrase

    discoveries = (PILOT / "DISCOVERIES.md").read_text(encoding="utf-8")
    sections = re.split(r"(?m)^## (\d+)\. ", discoveries)[1:]
    assert len(sections) // 2 >= 20, "menos de 20 descobertas"
    lowered = discoveries.lower()
    for phrase in ("passada contínua", "miolo antigo", "mancha"):
        assert phrase in lowered, phrase
