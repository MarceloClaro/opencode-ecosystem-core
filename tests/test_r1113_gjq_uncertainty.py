#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos de incerteza e calibração 4x4 no GJQ (R1113)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1113-gjq-uncertainty-full-calibration.md"
DOC = RAIZ / "docs" / "GJQ_INCERTEZA_CALIBRACAO_4X4_R1113.md"
RUNNER = RAIZ / "harnesses" / "gjq-hardware-optimizers" / "runner.py"
LOOP_RUNNER = RAIZ / "harnesses" / "gjq-hardware-optimizers" / "loop_runner.py"
PERFIL = (
    RAIZ
    / "harnesses"
    / "gjq-hardware-optimizers"
    / "resultados"
    / "baihua"
    / "E05"
    / "perfil.json"
)
UNCERTAINTY = (
    RAIZ
    / "harnesses"
    / "gjq-hardware-optimizers"
    / "resultados"
    / "baihua"
    / "E05_loop_uncertainty"
)


def _run(*args: str, timeout: int = 600):
    return subprocess.run(
        [sys.executable, *args],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_arquivos_existem():
    for caminho in (SPEC, DOC, RUNNER, LOOP_RUNNER, PERFIL):
        assert caminho.exists(), caminho
        assert caminho.stat().st_size > 400, caminho


def test_matriz_4x4_e_mitigacao():
    from gjq_hardware_opt import (
        confusion_from_calibration_counts,
        mitigate_probabilities,
    )

    calibration = {
        "00": {"00": 900, "01": 50, "10": 40, "11": 10},
        "01": {"00": 50, "01": 900, "10": 10, "11": 40},
        "10": {"00": 40, "01": 10, "10": 900, "11": 50},
        "11": {"00": 10, "01": 40, "10": 50, "11": 900},
    }
    model = confusion_from_calibration_counts(calibration, (1, 0))
    matrix = np.array(model.matrix)
    assert matrix.shape == (4, 4)
    assert np.allclose(matrix.sum(axis=0), 1.0)
    ideal = {"00": 0.5, "01": 0.0, "10": 0.0, "11": 0.5}
    vector = matrix @ np.array([ideal[s] for s in ("00", "01", "10", "11")])
    observed = {
        state: float(vector[index])
        for index, state in enumerate(("00", "01", "10", "11"))
    }
    result = mitigate_probabilities(observed, model)
    assert result["probabilities"]["00"] == pytest.approx(0.5, abs=1e-9)
    assert result["probabilities"]["11"] == pytest.approx(0.5, abs=1e-9)
    assert result["probabilities"]["01"] == pytest.approx(0.0, abs=1e-9)
    assert result["probabilities"]["10"] == pytest.approx(0.0, abs=1e-9)


def test_plano_4x4_3_repeticoes(tmp_path: Path):
    if not PERFIL.exists():
        pytest.skip("perfil real ausente")
    result = _run(
        str(RUNNER),
        "compare",
        "--plan",
        "--profile",
        str(PERFIL),
        "--circuit",
        "E05",
        "--shots",
        "8192",
        "--repetitions",
        "3",
        "--full-calibration",
        "--quick",
        "--out",
        str(tmp_path),
        timeout=300,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    plan = json.loads((tmp_path / "plano_comparacao.json").read_text(encoding="utf-8"))
    assert plan["shots"] == 8192
    assert plan["repetitions"] == 3
    assert plan["full_calibration"] is True
    assert plan["submissions_estimated"] == 14
    assert set(plan["baseline"]["calibration_qasm2"]) == {"00", "01", "10", "11"}
    assert set(plan["optimized"]["calibration_qasm2"]) == {"00", "01", "10", "11"}


def test_loop_plan_4x4_3_repeticoes(tmp_path: Path):
    if not PERFIL.exists():
        pytest.skip("perfil real ausente")
    result = _run(
        str(LOOP_RUNNER),
        "plan",
        "--profile",
        str(PERFIL),
        "--circuit",
        "E05",
        "--shots",
        "8192",
        "--repetitions",
        "3",
        "--full-calibration",
        "--quick",
        "--out",
        str(tmp_path),
        timeout=300,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    state = json.loads((tmp_path / "loop_state.json").read_text(encoding="utf-8"))
    assert state["repetitions"] == 3
    assert state["full_calibration"] is True
    assert state["submissions_estimated"] == 14
    assert state["status"] == "planned"


def test_artefatos_reais_incerteza():
    if not UNCERTAINTY.exists():
        pytest.skip("loop de incerteza ainda não executado")
    comparison_path = UNCERTAINTY / "comparacao" / "comparacao.json"
    if not comparison_path.exists():
        pytest.skip("comparação de incerteza ausente")
    data = json.loads(comparison_path.read_text(encoding="utf-8"))
    assert data["repetitions"] == 3
    assert data["full_calibration"] is True
    for key in ("baseline", "optimized"):
        case = data[key]
        assert case["repetitions_count"] == 3
        assert len(case["task_ids"]) == 3
        assert case["audit"]["total"] == 3 * 8192
        assert case["audit"]["ok"] is True
        assert case["repetition_stats"]
        assert case["mitigated_tvd_vs_ideal"] is not None
        assert np.array(case["mitigation"]["matrix"]).shape == (4, 4)
    report = (UNCERTAINTY / "comparacao" / "RELATORIO_COMPARACAO.md").read_text(
        encoding="utf-8"
    )
    assert "Repetições" in report


def test_sem_segredo():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    for caminho in (SPEC, DOC, RUNNER, LOOP_RUNNER):
        texto = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(texto), f"segredo em {caminho}"


def test_sem_overclaim():
    proibidos = (
        "fidelidade medida com sucesso",
        "vantagem quântica comprovada",
        "speedup garantido",
        "prova experimental de emaranhamento",
        "benchmark definitivo",
        "incerteza elimina a necessidade de repetir",
    )
    for caminho in (SPEC, DOC):
        texto = caminho.read_text(encoding="utf-8").lower()
        for termo in proibidos:
            assert termo not in texto, f"overclaim em {caminho}: {termo}"
