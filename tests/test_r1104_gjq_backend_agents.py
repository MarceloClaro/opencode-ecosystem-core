"""R1104: catálogo GJQ, MCP de pesquisa e 19 agentes de backend."""
from __future__ import annotations

import re
from pathlib import Path

from agents.lifecycle import AgentLifecycleService
from integrations.gjq_backend_registry import (
    BACKENDS,
    backend_limits,
    calibration_snapshot,
    compare_plan,
    is_hardware_name,
    normalize_name,
    provenance_template,
    research_plan,
    resolve_backend,
    snapshot_summary,
)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "agents" / "catalog"
TEST_FILE = "tests/test_r1104_gjq_backend_agents.py"


def _tools():
    from integrations.gjq_backend_research_mcp import create_server

    return create_server()._tool_manager._tools


def test_registry_tem_19_recursos_e_familias_corretas():
    assert len(BACKENDS) == 19
    assert len({b.id for b in BACKENDS}) == 19
    summary = snapshot_summary()
    assert summary["families"] == {"hardware": 6, "cpu": 4, "gpu": 4, "mps": 1, "npu": 4}
    assert summary["total"] == 19
    assert summary["max_qubits"] == 997
    assert summary["online"] + summary["maintenance"] == 19


def test_resolve_aliases_da_ui_e_da_api():
    assert [b["id"] for b in resolve_backend("Guoji No.8 (simulate)")] == ["guoji-08-sim"]
    assert [b["id"] for b in resolve_backend("FAS-GPU")] == ["qilv-fas-gpu"]
    assert [b["id"] for b in resolve_backend("SAS-CPU")] == ["jiuyuan-sas-cpu"]
    assert [b["id"] for b in resolve_backend("MPS")] == ["mps"]
    assert [b["id"] for b in resolve_backend("Baihua")] == ["baihua"]
    assert [b["id"] for b in resolve_backend("Guoji No.1")] == ["guoji-01"]
    assert resolve_backend("backend-inexistente") == []
    assert normalize_name("Guoji No.8（simulate）").startswith("guoji8")


def test_gate_de_hardware_e_conservador():
    for name in ("Guoji No.1", "Guoji No.4", "Guoji No.7", "Guoji No.8 (simulate)",
                 "Baihua", "Yudu"):
        assert is_hardware_name(name) is True, name
    for name in ("FAS-CPU", "SAS-CPU", "FAS-GPU", "MPS", "Jiuxiao"):
        assert is_hardware_name(name) is False, name


def test_planos_respeitam_gates_e_capacidade():
    sim = research_plan("Bell", 2, hardware_allowed=False)
    assert sim["status"] == "planned"
    assert sim["recommended"]["id"] == "jiuxiao-fas-cpu"
    assert sim["executed"] is False

    hw = research_plan("Bell", 2, hardware_allowed=True, prefer="hardware")
    assert hw["recommended"]["id"] == "baihua"
    assert hw["recommended"]["requires_allow_hardware"] is True

    single = research_plan("SAS", 2, needs_single_amplitude=True)
    assert single["recommended"]["id"] == "jiuyuan-sas-cpu"
    assert single["recommended"]["amplitude_index_required"] is True

    mps = research_plan("MPS", 500)
    assert mps["recommended"]["id"] == "mps"
    assert mps["recommended"]["simulator_config_required"] is True

    blocked = research_plan("grande", 998)
    assert blocked["status"] == "blocked"


def test_compare_plan_simulador_e_hardware():
    plano = compare_plan(2, include_hardware=True)
    assert plano["simulator"]["id"] == "jiuxiao-fas-cpu"
    assert plano["hardware"]["id"] == "baihua"
    assert plano["executed"] is False


def test_mcp_tools_somente_leitura_e_sem_chave():
    tools = _tools()
    assert set(tools) == {
        "gjq_backend_catalog",
        "gjq_backend_snapshot",
        "gjq_resolve_backend",
        "gjq_select_backend",
        "gjq_research_plan",
        "gjq_compare_plan",
        "gjq_backend_limits",
        "gjq_provenance_template",
        "gjq_calibration_snapshot",
    }
    catalog = tools["gjq_backend_catalog"].fn()
    assert catalog["total"] == 19
    assert catalog["executed"] is False
    assert catalog["network_access"] is False
    assert catalog["api_key_required"] is False
    assert tools["gjq_backend_snapshot"].fn()["families"]["hardware"] == 6
    assert tools["gjq_resolve_backend"].fn("FAS-CPU")["matches"][0]["id"] == "jiuxiao-fas-cpu"
    assert tools["gjq_select_backend"].fn("mps", 1, "online", 5)["total"] == 1
    plan = tools["gjq_research_plan"].fn("Bell", 2, 4, 1024, False, None, False, False)
    assert plan["recommended"]["id"] == "jiuxiao-fas-cpu"
    assert tools["gjq_backend_limits"].fn()["runtime_max_qubits_default"] == 200
    assert "task_id" in tools["gjq_provenance_template"].fn()["required"]
    assert tools["gjq_calibration_snapshot"].fn()["rows"]


def test_19_agentes_validos_e_com_capacidade_exclusiva():
    svc = AgentLifecycleService(ROOT)
    vistos = set()
    for backend in BACKENDS:
        agent_id = f"gjq-backend-{backend.id}"
        path = CATALOG / f"{agent_id}.md"
        assert path.is_file(), agent_id
        result = svc.validate(agent_id)
        assert result["definition_validated"] is True, agent_id
        assert result["unique_capability"] == "profile_" + agent_id.replace("-", "_")
        assert result["profile"]["spec_file"] == "specs/SPEC-935-R1104-gjq-backend-agents.md"
        assert result["profile"]["test_file"] == TEST_FILE
        assert agent_id not in vistos
        vistos.add(agent_id)
    assert len(vistos) == 19


def test_nenhum_segredo_nos_cards_registro_ou_mcp():
    texts = [
        (ROOT / "integrations/gjq_backend_registry.py").read_text(encoding="utf-8"),
        (ROOT / "integrations/gjq_backend_research_mcp.py").read_text(encoding="utf-8"),
        (ROOT / TEST_FILE).read_text(encoding="utf-8"),
        *[p.read_text(encoding="utf-8") for p in CATALOG.glob("gjq-backend-*.md")],
    ]
    pattern = re.compile(r"(?:GJQ_API_KEY|api[_-]?key)\s*[:=]\s*[\"'][A-Za-z0-9_\-]{16,}[\"']")
    for text in texts:
        assert not pattern.search(text), "segredo literal encontrado"


def test_limites_e_proveniencia_declaram_limites():
    limits = backend_limits()
    assert limits["runtime_max_qubits_default"] == 200
    assert limits["max_shots_default"] == 100_000
    assert limits["by_family"]["mps"]["max_qubits"] == 997
    prov = provenance_template()
    assert "qasm_sha256" in prov["required"]
    assert "não prova fidelidade" in prov["limits"]
    snap = calibration_snapshot()
    assert any(row["id"] == "baihua" for row in snap["rows"])
    assert "não são promessa de desempenho" in snap["warning"]

def test_opencode_json_registra_os_19_agentes_e_o_mcp():
    import json

    cfg = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    esperados = {f"gjq-backend-{b.id}" for b in BACKENDS}
    assert esperados <= set(cfg["agent"])
    assert "gjq-backend-research" in cfg["mcp"]
    assert cfg["mcp"]["gjq-backend-research"]["enabled"] is True
    assert cfg["mcp"]["gjq-backend-research"]["command"][-1] == "integrations.gjq_backend_research_mcp"


def test_runtime_gate_cobre_hardware_novo():
    from integrations.gjq_runtime_mcp import create_server

    tools = create_server()._tool_manager._tools
    status = tools["gjq_runtime_status"].fn()
    for nome in ("Guoji01", "Guoji04", "Guoji07", "Guoji08", "Baihua", "Yudu"):
        assert nome in status["hardware_backends"], nome
    assert status["max_qubits"] == 200
    assert status["max_qubits_cap"] == 997
