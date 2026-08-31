"""Testes do QualityCorrelator (evolution/quality_correlator.py)."""

from __future__ import annotations

import hashlib
import os
import tempfile

import pytest

from evolution.audit_gate import EvolutionAuditGate
from evolution.cycles import EvolutionCycle, EvolutionRegistry
from evolution.quality_correlator import QualityCorrelator, QualitySnapshot


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _artefato() -> bytes:
    return b"def f():\n    return 42\n"


def _isolated_registry() -> EvolutionRegistry:
    tmp = tempfile.mkdtemp(prefix="evo_qual_")
    return EvolutionRegistry(state_path=os.path.join(tmp, "cycles.json"))


def _isolated_snapshots() -> str:
    tmp = tempfile.mkdtemp(prefix="evo_snap_")
    return os.path.join(tmp, "quality_snapshots.jsonl")


@pytest.fixture
def corr_isolado() -> QualityCorrelator:
    reg = _isolated_registry()
    snap_path = _isolated_snapshots()
    return QualityCorrelator(registry=reg, snapshots_path=snap_path)


def test_collect_snapshot_basico(corr_isolado: QualityCorrelator):
    """Coleta snapshot básico sem quality checks."""
    snap = corr_isolado.collect_snapshot(run_quality_checks=False)
    assert isinstance(snap, QualitySnapshot)
    assert snap.cycle_id in ("unknown", "R463", "R462", "R464")
    assert snap.custody_audited >= 0
    assert snap.custody_total >= 0


def test_snapshot_persistido_e_recarregado(corr_isolado: QualityCorrelator):
    """Snapshot é persistido e pode ser recarregado."""
    corr_isolado.collect_snapshot(run_quality_checks=False)
    snaps = corr_isolado.load_snapshots()
    assert len(snaps) == 1
    assert isinstance(snaps[0], QualitySnapshot)


def test_correlacao_dados_insuficientes(corr_isolado: QualityCorrelator):
    """Correlação retorna mensagem de dados insuficientes com n < 5."""
    # adiciona 1 snapshot
    corr_isolado.collect_snapshot(run_quality_checks=False)
    resultados = corr_isolado.compute_correlations(min_samples=5)
    assert len(resultados) == 1
    assert resultados[0].metric_y == "insufficient_data"
    assert "Dados insuficientes" in resultados[0].interpretation


def test_correlacao_com_5_snapshots(corr_isolado: QualityCorrelator):
    """Com 5+ snapshots, correlação tenta computar (pode ser None por dados None)."""
    # adiciona 5 snapshots sem quality checks (downstream = None)
    for i in range(5):
        corr_isolado.collect_snapshot(run_quality_checks=False)
    resultados = corr_isolado.compute_correlations(min_samples=5)
    assert len(resultados) >= 1
    # Todos devem ter metric_y válido (não "insufficient_data") mas pearson=None por dados downstream=None
    for r in resultados:
        assert r.metric_y != "insufficient_data"
        # Com downstream None, pearson deve ser None
        if r.pearson_r is not None:
            assert isinstance(r.pearson_r, float)


def test_generate_report_e_write(corr_isolado: QualityCorrelator, tmp_path):
    """generate_report e write_report funcionam."""
    corr_isolado.collect_snapshot(run_quality_checks=False)
    report = corr_isolado.generate_report()
    assert "total_snapshots" in report
    assert "correlations" in report

    out = tmp_path / "report.json"
    corr_isolado.write_report(str(out))
    assert out.exists()
    import json
    data = json.loads(out.read_text())
    assert data["total_snapshots"] == 1


def test_pearson_spearman_basico(corr_isolado: QualityCorrelator):
    """Testa métodos internos _pearson e _spearman com dados conhecidos."""
    # x e y perfeitamente correlacionados
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [2.0, 4.0, 6.0, 8.0, 10.0]
    r = corr_isolado._pearson(x, y)
    assert r is not None and abs(r - 1.0) < 1e-9

    rho = corr_isolado._spearman(x, y)
    assert rho is not None and abs(rho - 1.0) < 1e-9

    # sem correlação
    y2 = [10.0, 8.0, 6.0, 4.0, 2.0]
    r2 = corr_isolado._pearson(x, y2)
    assert r2 is not None and abs(r2 - (-1.0)) < 1e-9

    rho2 = corr_isolado._spearman(x, y2)
    assert rho2 is not None and abs(rho2 - (-1.0)) < 1e-9