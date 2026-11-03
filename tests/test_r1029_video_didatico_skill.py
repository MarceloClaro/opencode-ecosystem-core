"""R1029 — skill de vídeo didático técnico e registro de descobertas."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".opencode/skills/video-didatico-tecnico"
DISCOVERIES = ROOT / "pilots/r1026-quantum/DISCOVERIES.md"


def skill_text() -> str:
    path = SKILL / "SKILL.md"
    assert path.is_file(), "SKILL.md ausente"
    return path.read_text(encoding="utf-8")


def test_skill_structure() -> None:
    text = skill_text()
    front = yaml.safe_load(text.split("---", 2)[1])
    assert front["name"] == "video-didatico-tecnico"
    assert len(front["description"]) >= 40
    for section in (
        "## Princípios didáticos",
        "## Efeitos e motion",
        "## Pipeline",
        "## Metacognição e registro",
        "## Limites",
    ):
        assert section in text, section


def test_references_resolve() -> None:
    assert SKILL.is_dir()
    for file in SKILL.rglob("*.md"):
        for link in re.findall(r"\]\(([^\s)]+)\)", file.read_text(encoding="utf-8")):
            if link.startswith(("https://", "http://", "#")):
                continue
            target = (file.parent / link.split("#")[0]).resolve()
            assert target.is_file(), (file, link)
    for name in (
        "principios-didaticos.md",
        "efeitos-e-motion.md",
        "pipeline-e-erros.md",
        "registro-de-descobertas.md",
    ):
        assert (SKILL / "references" / name).is_file(), name


def test_discoveries_have_evidence_and_impact() -> None:
    assert DISCOVERIES.is_file(), "DISCOVERIES.md ausente"
    text = DISCOVERIES.read_text(encoding="utf-8")
    sections = re.split(r"(?m)^## (\d+)\. ", text)[1:]
    assert len(sections) // 2 >= 10, "menos de 10 descobertas"
    for index in range(0, len(sections), 2):
        body = sections[index + 1]
        assert "Evidência" in body, body[:80]
        assert "Impacto" in body, body[:80]
    for marker in ("Wav2Lip", "XTTS", "Remotion", "SAR", "concat", "watchdog"):
        assert marker in text, marker


def test_pipeline_scripts_exist() -> None:
    base = ROOT / "pilots/r1026-quantum"
    for name in (
        "render-lipsync-cpu.sh",
        "apply-slide-didatico.sh",
        "concat-didatico.sh",
        "make_slide_patch.py",
    ):
        assert (base / name).is_file(), name
    for name in ("render-lipsync-cpu.sh", "apply-slide-didatico.sh", "concat-didatico.sh"):
        assert (base / name).stat().st_mode & 0o111, name


def test_safety_and_anti_overclaim() -> None:
    text = skill_text().lower()
    for phrase in (
        "consentimento",
        "não prova",
        "revisão humana",
        "não comercial",
        "licença",
    ):
        assert phrase in text, phrase
    for forbidden in (
        "qualidade profissional garantida",
        "100% garantido",
        "sincronia perfeita",
        "voz oficial da apresentadora",
    ):
        assert forbidden not in text, forbidden


def test_dispatcher_resolves_skill() -> None:
    from reversa_universal.skill_dispatch import ReversaSkillDispatcher

    dispatcher = ReversaSkillDispatcher(ROOT)
    assert dispatcher.resolve_skill("video-didatico-tecnico") == SKILL / "SKILL.md"


def test_skill_is_text_only() -> None:
    assert SKILL.is_dir()
    for path in SKILL.rglob("*"):
        if path.is_file():
            assert path.suffix == ".md", path


def test_no_duplicate_skill_name() -> None:
    matches = []
    for base in (ROOT / ".opencode/skills", ROOT / ".claude/skills"):
        if not base.is_dir():
            continue
        for path in base.rglob("SKILL.md"):
            text = path.read_text(encoding="utf-8", errors="replace")
            match = re.search(r"(?m)^name:\s*[\"']?video-didatico-tecnico[\"']?\s*$", text)
            if match:
                matches.append(path)
    assert matches == [SKILL / "SKILL.md"], matches
