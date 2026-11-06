"""R1055 — contrato estático do vídeo didático de qubit.

Não renderiza vídeo. Verifica a timeline, os textos corrigidos, o módulo de
câmera, o mapa e os assets. O QC técnico dos masters é feito por
`scripts/video_qa.py` e registrado em `reports/r1055/`.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "pilots" / "r1055-qubit"
REMOTION = ROOT / "editor-workspace" / "remotion-smoke" / "src" / "r1055-qubit"


def _timeline() -> dict:
    return json.loads((PILOT / "audio" / "timeline.json").read_text(encoding="utf-8"))


def test_timeline_has_seven_scenes_and_26_captions():
    timeline = _timeline()
    assert timeline["voice"] == "pt-BR-FranciscaNeural"
    assert timeline["cloned"] is False
    assert 100 <= timeline["total_duration"] <= 120
    assert [scene["id"] for scene in timeline["scenes"]] == [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
    ]
    captions = [caption for scene in timeline["scenes"] for caption in scene["captions"]]
    assert len(captions) == 26


def test_audio_is_not_repeating_punctuation():
    captions = " ".join(
        caption["text"]
        for scene in _timeline()["scenes"]
        for caption in scene["captions"]
    )
    assert " ponto " not in f" {captions} "
    assert "Bell" in captions
    assert "qubit" in captions
    assert "Aspect" in captions


def test_map_scene_has_five_narration_beats():
    scene = next(scene for scene in _timeline()["scenes"] if scene["id"] == "06")
    assert scene["title"] == "Origem"
    assert len(scene["captions"]) == 5
    assert "Copenhague" in scene["captions"][1]["text"]
    assert "Feynman" in scene["captions"][2]["text"]
    assert "Schumacher" in scene["captions"][3]["text"]
    assert "Nobel" in scene["captions"][4]["text"]


def test_typescript_timeline_matches_frames():
    timeline = (REMOTION / "timeline.ts").read_text(encoding="utf-8")
    assert "export const TOTAL_FRAMES = 3292;" in timeline
    assert len(re.findall(r'id: "0[1-7]"', timeline)) == 7
    assert timeline.count("captions: [") == 7
    assert "O estado de Bell correlaciona" in timeline


def test_camera_module_is_deterministic_and_eased():
    code = (REMOTION / "cinematic.tsx").read_text(encoding="utf-8")
    assert "export const SceneCamera" in code
    assert "export const useSceneCamera" in code
    assert "Easing.inOut(Easing.cubic)" in code
    assert "shakeAt" in code
    assert "performance.now" not in code
    assert "useCurrentFrame" in code
    horizontal = (REMOTION / "QubitExplainer.tsx").read_text(encoding="utf-8")
    vertical = (REMOTION / "QubitVertical.tsx").read_text(encoding="utf-8")
    assert horizontal.count("<SceneCamera index") == 5
    assert vertical.count("<SceneCamera index") == 5
    assert "index=0" not in horizontal
    assert "index=0" not in vertical


def test_map_has_pulsing_markers_and_nobel_sequence():
    code = (REMOTION / "QubitMap.tsx").read_text(encoding="utf-8")
    assert "const Pulse" in code
    assert "const NobelLabel" in code
    assert "cueEurope" in code
    assert "cueNobel" in code
    assert "NOBEL" in code
    assert "r1055-world-map.png" in code


def test_assets_and_dimensions():
    public = ROOT / "editor-workspace" / "remotion-smoke" / "public"
    with Image.open(public / "r1055-world-map.png") as image:
        assert image.size == (4096, 1354)
    with Image.open(public / "r1055-author.png") as image:
        assert image.size == (400, 400)
    with Image.open(public / "r1055-github-qr.png") as image:
        assert image.size == (512, 512)


def test_audio_script_uses_edge_neural_voice():
    code = (PILOT / "generate_audio_edge.py").read_text(encoding="utf-8")
    assert "pt-BR-FranciscaNeural" in code
    assert "edge_tts" in code
    assert "O estado de Bell correlaciona" in code
