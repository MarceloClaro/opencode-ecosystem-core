from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CATALOG = ROOT / "agents" / "catalog"
REPORT_DIR = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia" / "_archive" / "relatorios"
JSON_REPORT = REPORT_DIR / "literary_agent_runtime_isolation_R275.json"
MD_REPORT = REPORT_DIR / "literary_agent_runtime_isolation_R275.md"
MINIMAL_AGENT = CATALOG / "literary-smoke-minimal.md"


def test_r275_minimal_agent_exists_and_has_reduced_contract():
    assert MINIMAL_AGENT.exists(), "Agente literário mínimo R275 não foi criado."
    text = MINIMAL_AGENT.read_text(encoding="utf-8")
    assert "name: literary-smoke-minimal" in text
    assert "mode: subagent" in text
    assert "model:" not in text.split("---", 2)[1], "Agente mínimo não deve ter model explícito."
    for term in ["Contrato de saída obrigatório", "nunca pode ser vazia", "veredito", "strengths", "risks", "recommendations", "safe_claim", "limites"]:
        assert term.lower() in text.lower()


def test_r275_opencode_config_contains_minimal_agent():
    from integrations.opencode_cli import build_config

    cfg = build_config()
    agent = cfg["agent"].get("literary-smoke-minimal")
    assert agent is not None
    assert agent["mode"] == "subagent"
    assert agent["prompt"] == "{file:./agents/catalog/literary-smoke-minimal.md}"
    assert "model" not in agent


def test_r275_reports_exist_and_have_contract():
    assert JSON_REPORT.exists(), "Relatório JSON R275 não foi gerado."
    assert MD_REPORT.exists(), "Relatório Markdown R275 não foi gerado."
    data = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    assert data["spec_id"] == "SPEC-935-R275"
    assert "hypothesis_assessment" in data
    assert "agent_results" in data
    assert "anti-overclaim" in data["anti_overclaim_guard"].lower()
    for result in data["agent_results"].values():
        assert "returned_content" in result
        assert "content_length" in result
        assert "summary" in result


def test_r275_markdown_safe_sections():
    text = MD_REPORT.read_text(encoding="utf-8")
    for section in ["Resultado do isolamento", "Tabela comparativa", "Hipótese mais provável", "Próxima remediação", "Guarda anti-overclaim"]:
        assert section in text
    for unsafe in ["falha resolvida sem evidência", "validada internacionalmente", "excelência objetiva"]:
        assert unsafe not in text.lower()
