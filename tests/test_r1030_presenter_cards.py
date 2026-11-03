"""R1030 — apresentadora nos cartões didáticos e linha do tempo vertical."""

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
            "format=duration:stream=codec_type,codec_name,width,height",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_presenter_cutout_asset() -> None:
    import cv2

    path = PILOT / "presenter-cutout.png"
    assert path.is_file(), "presenter-cutout.png ausente"
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    assert image is not None and image.shape[2] == 4, "o recorte precisa de canal alfa"
    alpha = image[:, :, 3]
    assert int(alpha.min()) == 0 and int(alpha.max()) == 255
    assert (alpha > 20).mean() > 0.3, "alfa cobriu pouca área; recorte provavelmente falhou"


def test_tsx_uses_presenter_and_timeline() -> None:
    text = TSX.read_text(encoding="utf-8")
    for marker in (
        "PresenterCard",
        "presenter-cutout.png",
        "Timeline",
        "objectFit: \"contain\"",
        "radial-gradient(circle at 50% 40%",
    ):
        assert marker in text, marker
    assert text.count("PresenterCard vertical={vertical}") == 2
    assert text.count("<Timeline steps={steps}") == 2
    assert "0.26 + 0.74 * enter" in text


def test_final_masters_metadata() -> None:
    for name, width, height in (
        ("pilot-16x9-didatico-voz.mp4", 1920, 1080),
        ("pilot-9x16-didatico-voz.mp4", 1080, 1920),
    ):
        data = ffprobe(PILOT / name)
        assert abs(float(data["format"]["duration"]) - 44.0) < 0.2
        streams = {stream["codec_type"]: stream for stream in data["streams"]}
        assert streams["video"]["width"] == width
        assert streams["video"]["height"] == height
        assert streams["audio"]["codec_name"] == "aac"


def test_docs_record_presenter_card() -> None:
    readme = (PILOT / "README.md").read_text(encoding="utf-8").lower()
    for phrase in ("apresentadora", "recorte", "linha do tempo"):
        assert phrase in readme, phrase

    discoveries = (PILOT / "DISCOVERIES.md").read_text(encoding="utf-8")
    sections = re.split(r"(?m)^## (\d+)\. ", discoveries)[1:]
    assert len(sections) // 2 >= 15, "menos de 15 descobertas"
    lowered = discoveries.lower()
    for phrase in ("apresentadora", "recorte", "linha do tempo"):
        assert phrase in lowered, phrase


def test_manifest_has_new_hashes() -> None:
    manifest = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
    files = manifest["files"]
    for name in ("pilot-16x9-didatico-voz.mp4", "pilot-9x16-didatico-voz.mp4"):
        assert len(files[name]["sha256"]) == 64, name
    assert "presenter-cutout.png" in files
    assert "remotion-template/src/DidacticIntroOutro.tsx" in files


def test_concat_pipeline_is_safe() -> None:
    text = (PILOT / "concat-didatico.sh").read_text(encoding="utf-8")
    for marker in ("apad", "atrim", "setsar=1", "concat=n=3:v=1:a=1", "loudnorm"):
        assert marker in text, marker


def test_presenter_cutout_is_reproducible() -> None:
    script = PILOT / "make-presenter-cutout.py"
    assert script.is_file(), "make-presenter-cutout.py ausente"
    assert script.stat().st_mode & 0o111, "script precisa ser executável"
    text = script.read_text(encoding="utf-8")
    for marker in (
        "crop=560:800:1180:130",
        "connectedComponentsWithStats",
        "erode",
        "presenter-cutout.png",
    ):
        assert marker in text, marker


def test_skill_mentions_presenter_and_timeline() -> None:
    text = (ROOT / ".opencode/skills/video-didatico-tecnico/SKILL.md").read_text(
        encoding="utf-8"
    ).lower()
    assert "apresentadora" in text
    assert "linha do tempo" in text
