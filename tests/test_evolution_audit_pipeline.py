"""Testes do Pipeline de Auditoria Contínua (evolution/audit_pipeline.py)."""

from __future__ import annotations

import hashlib
import os
import tempfile

import pytest

from evolution.audit_gate import EvolutionAuditGate
from evolution.audit_pipeline import AuditPipeline, AuditReport
from evolution.cycles import EvolutionCycle, EvolutionRegistry


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _artefato() -> bytes:
    return b"def f():\n    return 42\n"


def _isolated_registry() -> EvolutionRegistry:
    tmp = tempfile.mkdtemp(prefix="evo_audit_")
    return EvolutionRegistry(state_path=os.path.join(tmp, "cycles.json"))


@pytest.fixture
def pipeline_isolado() -> AuditPipeline:
    reg = _isolated_registry()
    return AuditPipeline(registry_path=reg.state_path)


def test_pipeline_retorna_relatorio_estruturado(pipeline_isolado: AuditPipeline):
    """Pipeline executa e retorna relatório com estrutura esperada."""
    report = pipeline_isolado.run()
    assert isinstance(report, AuditReport)
    assert report.total_cycles >= 0
    assert "audited" in report.custody_global
    assert "pct" in report.custody_recent
    assert isinstance(report.integrity_checks, list)
    assert isinstance(report.alerts, list)


def test_pipeline_com_ciclos_auditados_eleva_custodia(pipeline_isolado: AuditPipeline):
    """Pipeline detecta Custódia elevada quando há ciclos auditados."""
    reg = EvolutionRegistry(state_path=pipeline_isolado.registry_path)
    gate = EvolutionAuditGate()
    art = _artefato()

    # registra 1 ciclo auditado
    v = gate.verify_cycle(
        objective="teste pipeline",
        changes=["z"],
        artifact_files={"m.py": art},
        verifier_identity="auditor",
        generator_identity="gerador",
        evidence_trail=["test"],
    )
    reg.record_audited(
        objective="teste pipeline",
        changes=["z"],
        artifact_hashes={"m.py": _sha(art.decode())},
        external_verdict={"passed": True},
        verifier_identity="auditor",
        generator_identity="gerador",
        round_id="R463",
    )

    pipe = AuditPipeline(registry_path=pipeline_isolado.registry_path)
    report = pipe.run()
    assert report.custody_global["audited"] == 1
    assert report.custody_recent["pct"] == 100.0


def test_pipeline_alerta_custodia_recente_baixa(pipeline_isolado: AuditPipeline):
    """Pipeline gera alerta CRITICAL se custódia recente < threshold."""
    # configura threshold alto (100%) mas sem ciclos auditados recentes
    pipe = AuditPipeline(registry_path=pipeline_isolado.registry_path, custody_recent_min_pct=90.0)
    report = pipe.run()
    critical_alerts = [a for a in report.alerts if a.level == "critical"]
    assert any(a.code == "CUSTODY_RECENT_LOW" for a in critical_alerts)


def test_pipeline_integridade_merkle_consistency(pipeline_isolado: AuditPipeline):
    """Pipeline detecta merkle_root inconsistente (tamper lógico)."""
    reg = EvolutionRegistry(state_path=pipeline_isolado.registry_path)
    gate = EvolutionAuditGate()
    art = _artefato()

    # registra ciclo auditado com merkle correto
    v = gate.verify_cycle(
        objective="merkle test",
        changes=["z"],
        artifact_files={"m.py": art},
        verifier_identity="auditor",
        generator_identity="gerador",
        evidence_trail=["test"],
    )
    ciclo = reg.record_audited(
        objective="merkle test",
        changes=["z"],
        artifact_hashes=gate.resolve_artifacts({"m.py": art}),
        external_verdict={"passed": True},
        verifier_identity="auditor",
        generator_identity="gerador",
        round_id="R464",
    )
    # corrompe o merkle_root do ciclo (simula tamper lógico no registro)
    ciclo.merkle_root = "0" * 64
    reg.save()

    pipe = AuditPipeline(registry_path=pipeline_isolado.registry_path)
    report = pipe.run()
    failed = [c for c in report.integrity_checks if c["name"] == "merkle_consistency" and not c["passed"]]
    assert len(failed) == 1


def test_pipeline_saida_json_e_markdown(pipeline_isolado: AuditPipeline, tmp_path):
    """Pipeline grava JSON e Markdown corretamente."""
    pipe = AuditPipeline(registry_path=pipeline_isolado.registry_path)

    json_out = tmp_path / "report.json"
    pipe.write_report(str(json_out), fmt="json")
    assert json_out.exists()
    import json as _json
    data = _json.loads(json_out.read_text())
    assert "custody_global" in data

    md_out = tmp_path / "report.md"
    pipe.write_report(str(md_out), fmt="md")
    assert md_out.exists()
    md_text = md_out.read_text()
    assert "Cadeia de Custódia" in md_text


def test_pipeline_exit_code_ci(pipeline_isolado: AuditPipeline):
    """Código de saída para CI: 0=OK, 1=warn, 2=critical."""
    # Teste 1: com ciclo auditado + threshold alto que NÃO dispara (100% >= 90%)
    reg = EvolutionRegistry(state_path=pipeline_isolado.registry_path)
    gate = EvolutionAuditGate()
    art = _artefato()
    v = gate.verify_cycle(
        objective="test exit code ok",
        changes=["z"],
        artifact_files={"m.py": art},
        verifier_identity="auditor",
        generator_identity="gerador",
        evidence_trail=["test"],
    )
    reg.record_audited(
        objective="test exit code ok",
        changes=["z"],
        artifact_hashes={"m.py": _sha(art.decode())},
        external_verdict={"passed": True},
        verifier_identity="auditor",
        generator_identity="gerador",
        round_id="R463",
    )

    pipe_ok = AuditPipeline(registry_path=pipeline_isolado.registry_path)
    assert pipe_ok.cli_exit_code() == 0  # 100% >= 90% => sem critical

    # Teste 2: NOVO registro isolado SEM ciclos auditados recentes + threshold 90% => critical
    reg2 = _isolated_registry()
    pipe_crit = AuditPipeline(registry_path=reg2.state_path, custody_recent_min_pct=90.0)
    assert pipe_crit.cli_exit_code() == 2  # 0% < 90% => critical

    # Teste 3: registro COM ciclo auditado + threshold 0% => OK (exit 0)
    reg3 = _isolated_registry()
    gate2 = EvolutionAuditGate()
    art2 = _artefato()
    v2 = gate2.verify_cycle(
        objective="test exit zero",
        changes=["z"],
        artifact_files={"m.py": art2},
        verifier_identity="auditor",
        generator_identity="gerador",
        evidence_trail=["test"],
    )
    reg3.record_audited(
        objective="test exit zero",
        changes=["z"],
        artifact_hashes={"m.py": _sha(art2.decode())},
        external_verdict={"passed": True},
        verifier_identity="auditor",
        generator_identity="gerador",
        round_id="R464",
    )
    pipe_zero = AuditPipeline(registry_path=reg3.state_path, custody_recent_min_pct=0.0)
    assert pipe_zero.cli_exit_code() == 0  # 100% >= 0%, âncoras OK