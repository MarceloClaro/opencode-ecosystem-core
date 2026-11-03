"""R1049: contratos das skills adotadas, catálogos e pin de fontes."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".opencode/skills"
NEW_SKILLS = {
    "superpowers-sdd-tdd": "MIT",
    "rigor-academico-chgagne": "MIT",
    "kdense-ciencia-seletiva": "MIT",
    "motion-design-seletivo": "MIT",
    "video-director-qa": "MIT",
    "video-shotcraft-selecao": "Apache-2.0",
    "agentes-engenharia-selecao": "MIT",
    "laboratorio-pesquisa-isolado": "MIT",
}


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    _, raw, _ = text.split("---", 2)
    data = yaml.safe_load(raw)
    assert isinstance(data, dict)
    return data


@pytest.mark.parametrize("slug,license", sorted(NEW_SKILLS.items()))
def test_new_skill_frontmatter_and_guardrails(slug, license):
    directory = SKILLS / slug
    path = directory / "SKILL.md"
    assert path.is_file(), f"skill ausente: {slug}"
    data = frontmatter(path)
    assert data["name"] == slug
    assert isinstance(data.get("description"), str) and len(data["description"]) >= 40
    metadata = data.get("metadata") or {}
    assert metadata.get("round") == "R1049"
    assert metadata.get("source")
    assert metadata.get("license") == license
    assert metadata.get("adaptation")
    text = path.read_text(encoding="utf-8").lower()
    for forbidden in ("curl | bash", "curl -fsSL", "npm install -g", "pip install "):
        assert forbidden.lower() not in text
    assert "não copia" in text or "nao copia" in text or "não copiar" in text or "nao copiar" in text


def test_kdense_has_eight_selected_protocols():
    refs = sorted((SKILLS / "kdense-ciencia-seletiva/references").glob("*.md"))
    assert len(refs) == 8, [p.name for p in refs]
    names = " ".join(p.name for p in refs)
    for token in ("literatura", "citacao", "hipotese", "delineamento",
                  "estatistica", "poder", "peer", "explorat"):
        assert token in names, token


def test_motion_has_five_protocols():
    refs = sorted((SKILLS / "motion-design-seletivo/references").glob("*.md"))
    assert len(refs) == 5, [p.name for p in refs]
    names = " ".join(p.name for p in refs)
    for token in ("kinetic", "data", "explainer", "lower", "broll"):
        assert token in names, token


def test_shotcraft_catalog_is_selected_and_attributed():
    data = json.loads((SKILLS / "video-shotcraft-selecao/references/receitas.json").read_text())
    assert len(data["recipes"]) == 10
    for recipe in data["recipes"]:
        assert recipe["id"] and recipe["name"] and recipe["use_when"]
        assert recipe["qa"] and recipe["risk"]
        assert recipe["source"].startswith("https://github.com/Vincentwei1021/video-shotcraft")
    assert data["license"] == "Apache-2.0"
    assert "commit" in data and len(data["commit"]) >= 40


def test_engineering_agents_catalog_is_selected():
    data = json.loads((SKILLS / "agentes-engenharia-selecao/references/agents.json").read_text())
    assert len(data["agents"]) == 10
    for agent in data["agents"]:
        assert agent["id"] and agent["role"] and agent["use_when"]
        assert agent["source"].startswith("https://github.com/wshobson/agents")
        assert agent["license"] == "MIT"


def test_sources_are_pinned_with_commit_and_license():
    data = json.loads((ROOT / "reports/r1049/sources.json").read_text())
    assert len(data["sources"]) >= 10
    for source in data["sources"]:
        assert source["repo"].startswith(("anthropics/", "obra/", "chgagne/",
                                          "K-Dense-AI/", "iart-ai/", "win4r/",
                                          "Vincentwei1021/", "wshobson/",
                                          "panjose/", "wanshuiyin/",
                                          "remotion-dev/"))
        assert re.fullmatch(r"[0-9a-f]{40}", source["commit"]), source
        assert source["license"]
        assert source["url"].startswith("https://github.com/")


def test_new_skills_do_not_ship_third_party_code():
    for slug in NEW_SKILLS:
        for path in (SKILLS / slug).rglob("*"):
            if path.is_file():
                assert path.suffix not in {".py", ".sh", ".js", ".ts", ".pth", ".onnx"}, path
