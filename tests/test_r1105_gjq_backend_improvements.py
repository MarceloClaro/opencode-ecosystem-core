"""R1105: orientação por backend, frescor, drift, proveniência e templates."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from integrations.gjq_backend_registry import (
    BACKENDS,
    catalog,
    resolve_backend,
    snapshot_freshness,
    validate_provenance,
)
from integrations.gjq_experiment_templates import get_template, template_catalog

ROOT = Path(__file__).resolve().parents[1]


def _tools():
    from integrations.gjq_backend_research_mcp import create_server

    return create_server()._tool_manager._tools


def test_todos_os_19_perfis_tem_orientacao():
    for backend in BACKENDS:
        profile = resolve_backend(backend.id)[0]
        guidance = profile["guidance"]
        assert guidance["best_for"], backend.id
        assert guidance["avoid"], backend.id
        assert guidance["recommended_experiments"], backend.id
    mps = resolve_backend("MPS")[0]["guidance"]
    assert any("profundos" in item for item in mps["avoid"])
    emu = resolve_backend("Guoji No.8 (simulate)")[0]["guidance"]
    assert any("ensaiar" in item for item in emu["best_for"])
    hw = resolve_backend("Baihua")[0]["guidance"]
    assert any("hardware real" in item for item in hw["best_for"])


def test_frescor_do_snapshot_e_deterministico():
    recent = snapshot_freshness(date(2026, 11, 10))
    assert recent["age_days"] == 1
    assert recent["stale"] is False
    old = snapshot_freshness(date(2026, 11, 20))
    assert old["age_days"] == 11
    assert old["stale"] is True
    skew = snapshot_freshness(date(2026, 11, 8))
    assert skew["clock_skew"] is True
    assert skew["age_days"] == 0
    assert "freshness" in catalog()


def test_mcp_tem_12_ferramentas_e_perfil_com_orientacao():
    tools = _tools()
    assert len(tools) == 12
    assert {
        "gjq_backend_profile",
        "gjq_provenance_validate",
        "gjq_experiment_template",
    } <= set(tools)
    profile = tools["gjq_backend_profile"].fn("FAS-CPU")
    assert profile["profile"]["guidance"]["best_for"]
    ambiguous = tools["gjq_backend_profile"].fn("Guoji")
    assert ambiguous["ambiguous"] is True
    assert ambiguous["total"] >= 4


def test_proveniencia_valida_e_rejeita_registro_incompleto():
    record = {
        "task_id": "task-1",
        "backend": "FAS-CPU",
        "backend_kind": "simulator",
        "shots": 2,
        "timestamp_utc": "2026-11-09T00:00:00Z",
        "qasm_sha256": "a" * 64,
        "sdk_version": "0.2.1",
        "qiskit_version": "2.3.0",
        "status": "DONE",
        "counts_or_evs": {"00": 1, "11": 1},
        "audit": {"ok": True},
        "limitations": "amostra pequena; não generaliza",
    }
    ok = validate_provenance(record)
    assert ok["ok"] is True
    assert ok["resolved_backend"]["id"] == "jiuxiao-fas-cpu"

    bad = dict(record, qasm_sha256="abc", shots=3,
               counts_or_evs={"00": 1}, limitations="")
    result = validate_provenance(bad)
    assert result["ok"] is False
    joined = " ".join(result["errors"])
    assert "qasm_sha256" in joined
    assert "soma dos counts" in joined
    assert "limitations" in joined


def test_templates_de_experimento():
    catalog = template_catalog()
    assert catalog["total"] == 5
    assert {item["name"] for item in catalog["templates"]} == {
        "bell", "ghz3", "chsh", "qft2", "vqe_ansatz"
    }
    chsh = get_template("chsh")
    assert set(chsh["circuits"]) == {"zz", "zx", "xz", "xx"}
    for qasm in chsh["circuits"].values():
        assert qasm.startswith("OPENQASM 2.0;")
        assert "measure" in qasm
    bell = get_template("bell")
    assert "h q[0]" in bell["qasm"]
    assert "cx q[0],q[1]" in bell["qasm"]
    qft = get_template("qft2")
    assert "swap " not in qft["qasm"]
    assert qft["qasm"].count("cx q[0],q[1]") >= 2
    with pytest.raises(ValueError):
        get_template("inexistente")

    tools = _tools()
    assert tools["gjq_experiment_template"].fn()["total"] == 5
    assert tools["gjq_experiment_template"].fn("bell")["template"]["qubits"] == 2


def test_drift_compara_registro_e_lista_viva(monkeypatch):
    import integrations.gjq_runtime_mcp as runtime

    class FakeService:
        def list_backends(self):
            return [{"name": "FAS-CPU"}, {"name": "Baihua"}, {"name": "BackendNovo"}]

    monkeypatch.setattr(runtime, "_key_present", lambda: True)
    monkeypatch.setattr(runtime, "_get_service", lambda: FakeService())
    tools = runtime.create_server()._tool_manager._tools
    result = tools["gjq_backend_drift"].fn()
    assert result["status"] == "success"
    assert result["live_count"] == 3
    assert result["matched"][0]["registry_id"] == "jiuxiao-fas-cpu"
    assert "BackendNovo" in result["missing_in_registry"]
    assert "mps" in result["missing_live"]
    assert result["network_access"] is True
    assert result["executed"] is False
    assert result["jobs_submitted"] is False


def test_drift_sem_chave_retorna_blocked(monkeypatch):
    import integrations.gjq_runtime_mcp as runtime

    monkeypatch.setattr(runtime, "_key_present", lambda: False)
    tools = runtime.create_server()._tool_manager._tools
    result = tools["gjq_backend_drift"].fn()
    assert result["status"] == "blocked"
    assert result["jobs_submitted"] is False


def test_cards_incluem_melhor_uso_e_evitar():
    for backend in BACKENDS:
        text = (ROOT / "agents" / "catalog" / f"gjq-backend-{backend.id}.md").read_text(encoding="utf-8")
        assert "## Melhor uso" in text, backend.id
        assert "## Evitar" in text, backend.id
        assert "## Experimentos recomendados" in text, backend.id
