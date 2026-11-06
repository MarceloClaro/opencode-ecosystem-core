"""R1080: gate do catálogo de estilos e do contrato de tradução."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/r1080"
CATALOG = REPORT / "style_catalog.json"
README = REPORT / "README.md"
PROMPT = REPORT / "assistant_prompt.md"

REQUIRED_STYLE_KEYS = {
    "id", "name", "lineage", "use_when", "syntax", "lexicon",
    "sensory_channels", "pov", "tension_curve", "motifs",
    "reader_effect", "translation", "risks", "prompt",
}
REQUIRED_LANGS = {"pt-BR", "en", "zh"}


def load() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def test_catalog_schema_and_style_count():
    data = load()
    assert data["schema_version"] == 1
    assert data["name"].startswith("Assistente de Romance Psicológico")
    assert data["version"]
    assert len(data["styles"]) == 16
    ids = [style["id"] for style in data["styles"]]
    assert len(ids) == len(set(ids))
    assert "sepia-visceral" in ids
    assert "laudo-clinico" in ids
    assert "espiral-metaficcional" in ids


def test_each_style_has_craft_and_translation_fields():
    data = load()
    for style in data["styles"]:
        assert REQUIRED_STYLE_KEYS <= set(style), style.get("id")
        assert len(style["sensory_channels"]) >= 3, style["id"]
        assert len(style["motifs"]) >= 2, style["id"]
        assert len(style["risks"]) >= 1, style["id"]
        assert style["prompt"].strip(), style["id"]
        assert set(style["translation"]) == REQUIRED_LANGS, style["id"]
        for lang in REQUIRED_LANGS:
            assert style["translation"][lang].strip(), (style["id"], lang)


def test_ethics_is_explicit_and_non_clinical():
    data = load()
    ethics = data["ethics"]
    for key in (
        "contract", "content_warnings", "no_real_targets", "no_coercion",
        "translation", "attribution", "documents",
    ):
        assert key in ethics, key
        assert ethics[key].strip(), key
    contract = ethics["contract"].lower()
    assert "ficção" in contract
    assert "não é terapia" in contract
    assert "efeito clínico" in contract
    assert "manipulação real" in contract


def test_translation_protocol_covers_three_languages():
    data = load()
    protocol = data["translation_protocol"]
    for key in ("principle", "pt-BR", "en", "zh", "qa"):
        assert key in protocol, key
    assert len(protocol["qa"]) >= 5
    assert any("back-translation" in item for item in protocol["qa"])
    assert any("sensibilidade" in item for item in protocol["qa"])


def test_tagline_engine_and_quality_gates():
    data = load()
    engine = data["tagline_engine"]
    assert len(engine["patterns"]) >= 6
    for pattern in engine["patterns"]:
        assert pattern["id"] and pattern["formula"] and pattern["example"]
    assert len(data["quality_gates"]) >= 8
    joined = " ".join(data["quality_gates"]).lower()
    assert "ética" in joined
    assert "anti-overclaim" in joined


def test_readme_documents_codex_translation_and_limits():
    text = re.sub(r"\s+", " ", README.read_text(encoding="utf-8").lower())
    for term in (
        "codex", "pt-br", "en", "zh", "ética", "não é terapia",
        "não é nlp clínico", "10/10", "16",
    ):
        assert term in text, term
    prompt = PROMPT.read_text(encoding="utf-8").lower()
    assert "não é terapeuta" in prompt
    assert "metáforas de ofício" in prompt
    assert "back-translation" in prompt
