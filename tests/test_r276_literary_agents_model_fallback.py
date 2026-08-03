from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CATALOG = ROOT / "agents" / "catalog"
REPORT_DIR = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia" / "_archive" / "relatorios"
JSON_REPORT = REPORT_DIR / "literary_agents_model_fallback_R276.json"
MD_REPORT = REPORT_DIR / "literary_agents_model_fallback_R276.md"

LITERARY_AGENTS = {
    "literary-orchestrator-phd",
    "literary-narratology-architect-phd",
    "literary-style-voice-phd",
    "literary-character-psychology-phd",
    "literary-symbolic-imagery-phd",
    "literary-ethics-trauma-phd",
    "literary-innovation-editorial-phd",
    "literary-research-scholar-phd",
    "literary-smoke-minimal",
}


def _frontmatter(text: str) -> str:
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    assert match, "frontmatter ausente"
    return match.group(1)


def test_r276_literary_agents_have_no_explicit_model_but_keep_contract():
    for agent_id in LITERARY_AGENTS:
        text = (CATALOG / f"{agent_id}.md").read_text(encoding="utf-8")
        fm = _frontmatter(text)
        assert "model:" not in fm, f"{agent_id} ainda contém model explícito"
        assert "mode: subagent" in fm
        assert "temperature:" in fm
        lower = text.lower()
        for term in ["contrato de saída obrigatório", "nunca pode ser vazia", "veredito", "strengths", "risks", "recommendations", "safe_claim", "limites"]:
            assert term in lower, f"{agent_id} perdeu contrato obrigatório: {term}"


def test_r276_opencode_config_omits_literary_models():
    from integrations.opencode_cli import build_config

    config = build_config()
    for agent_id in LITERARY_AGENTS:
        agent = config["agent"][agent_id]
        assert "model" not in agent, f"{agent_id} ainda tem model no opencode.json"
    json.dumps(config, ensure_ascii=False)


def test_r276_report_exists_and_documents_runtime_limitation():
    assert JSON_REPORT.exists()
    assert MD_REPORT.exists()
    data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    assert data["spec_id"] == "SPEC-935-R276"
    assert data["explicit_model_removed"] is True
    assert data["runtime_validation_requires_new_session"] is True
    assert "anti-overclaim" in data["anti_overclaim_guard"].lower()
    text = MD_REPORT.read_text(encoding="utf-8")
    for section in ["Mudança aplicada", "Limitação runtime", "Próximo teste", "Guarda anti-overclaim"]:
        assert section in text
