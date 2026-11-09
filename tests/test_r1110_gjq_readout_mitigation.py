#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos de comparação e mitigação de leitura GJQ (R1110)."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1110-gjq-readout-mitigation.md"
DOC = RAIZ / "docs" / "GJQ_MITIGACAO_LEITURA_R1110.md"
MITIGATION = RAIZ / "gjq_hardware_opt" / "mitigation.py"
COMPARISON = RAIZ / "gjq_hardware_opt" / "comparison.py"
COMPARACAO = (
    RAIZ
    / "harnesses"
    / "gjq-hardware-optimizers"
    / "resultados"
    / "baihua"
    / "E05_comparacao"
)


def _profile():
    from gjq_hardware_opt import HardwareProfile

    return HardwareProfile(
        name="teste_leitura",
        num_qubits=2,
        coupling_map=((0, 1), (1, 0)),
        basis_gates=("h", "cz"),
        oneq_gates=("h",),
        twoq_gates=("cz",),
        oneq_error={"h": {0: 1e-3, 1: 1e-3}},
        twoq_error={"cz": {(0, 1): 1e-2, (1, 0): 1e-2}},
        readout_error={0: 0.1, 1: 0.1},
    )


def test_arquivos_existem():
    for caminho in (SPEC, DOC, MITIGATION, COMPARISON):
        assert caminho.exists(), caminho
        assert caminho.stat().st_size > 400, caminho


def test_estados():
    from gjq_hardware_opt import states_for

    assert states_for(1) == ["0", "1"]
    assert states_for(2) == ["00", "01", "10", "11"]


def test_matriz_simetrica():
    from gjq_hardware_opt import readout_confusion_matrix

    model = readout_confusion_matrix(_profile(), (1, 0))
    matrix = np.array(model.matrix)
    assert matrix.shape == (4, 4)
    assert model.source == "profile_symmetric"
    assert np.allclose(matrix.sum(axis=0), 1.0)
    assert matrix[0, 1] == pytest.approx(0.1 * 0.9)
    assert matrix[1, 0] == pytest.approx(0.1 * 0.9)


def test_mitigacao_recupera_ideal():
    from gjq_hardware_opt import mitigate_probabilities, readout_confusion_matrix

    model = readout_confusion_matrix(_profile(), (1, 0))
    ideal = {"00": 0.5, "01": 0.0, "10": 0.0, "11": 0.5}
    vector = np.array(model.matrix) @ np.array([ideal[s] for s in ("00", "01", "10", "11")])
    observed = {
        state: float(vector[index])
        for index, state in enumerate(("00", "01", "10", "11"))
    }
    result = mitigate_probabilities(observed, model)
    assert result["probabilities"]["00"] == pytest.approx(0.5, abs=1e-9)
    assert result["probabilities"]["11"] == pytest.approx(0.5, abs=1e-9)
    assert result["probabilities"]["01"] == pytest.approx(0.0, abs=1e-9)
    assert result["probabilities"]["10"] == pytest.approx(0.0, abs=1e-9)
    assert result["method"] == "inverse"
    assert result["negative_mass_clipped"] == pytest.approx(0.0, abs=1e-9)


def test_submatriz_e_leakage():
    from gjq_hardware_opt import mitigate_subspace, subspace_matrix_from_calibration

    matrix, leakage = subspace_matrix_from_calibration(
        {
            "00": {"00": 900, "11": 100, "01": 0, "10": 0},
            "11": {"00": 100, "11": 900, "01": 0, "10": 0},
        },
        ("00", "11"),
    )
    assert matrix == [[0.9, 0.1], [0.1, 0.9]]
    assert leakage == {"00": 0.0, "11": 0.0}
    result = mitigate_subspace(
        {"00": 0.41, "11": 0.41, "01": 0.09, "10": 0.09},
        matrix,
        ("00", "11"),
    )
    assert result["probabilities"]["00"] == pytest.approx(0.5)
    assert result["probabilities"]["11"] == pytest.approx(0.5)
    assert result["leakage_outside_subspace"] == pytest.approx(0.18)


def test_matriz_completa_calibrada():
    from gjq_hardware_opt import confusion_from_calibration_counts

    perfect = {
        state: {state: 1000}
        for state in ("00", "01", "10", "11")
    }
    model = confusion_from_calibration_counts(perfect, (1, 0))
    assert model.source == "hardware_calibration"
    assert np.allclose(np.array(model.matrix), np.eye(4))


def test_circuito_de_calibracao():
    from qiskit import qasm2
    from gjq_hardware_opt import calibration_circuit, measurement_order

    circuit = calibration_circuit([1, 0], "10")
    assert circuit.num_qubits == 2
    assert circuit.num_clbits == 2
    text = qasm2.dumps(circuit)
    assert "rx(pi) q[1];" in text
    assert "measure q[1] -> c[1];" in text
    assert "measure q[0] -> c[0];" in text
    assert measurement_order(circuit) == [1, 0]


def test_limite_de_qubits():
    from gjq_hardware_opt import readout_confusion_matrix

    profile = _profile()
    with pytest.raises(ValueError):
        readout_confusion_matrix(profile, list(range(7)))


def test_comparacao_real_registrada():
    if not COMPARACAO.exists():
        pytest.skip("comparação real ausente")
    data = json.loads((COMPARACAO / "comparacao.json").read_text(encoding="utf-8"))
    assert "baseline" in data and "optimized" in data
    for name in ("baseline", "optimized"):
        case = data[name]
        assert sum(int(v) for v in case["counts"].values()) == 4096
        assert case["audit"]["ok"] is True
        assert case["task_id"]
        assert len(case["calibration_task_ids"]) == 2
        assert case["mitigation"]["matrix"]
        assert case["mitigation"]["probabilities"]["00"] > 0.5
    assert data["comparison"]["delta_raw_correlation"] == pytest.approx(-0.03466796875)
    assert data["comparison"]["delta_mitigated_tvd"] == pytest.approx(0.002844354267)
    assert data["baseline"]["mitigation"]["leakage_by_prepared"]["11"] == pytest.approx(0.140625)
    assert data["optimized"]["mitigation"]["leakage_by_prepared"]["11"] == pytest.approx(0.150146484375)
    report = (COMPARACAO / "RELATORIO_COMPARACAO.md").read_text(encoding="utf-8")
    assert "não confirmou" in report
    assert "0,0028" in report or "0.0028" in report


def test_sem_segredo():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    for caminho in (SPEC, DOC, MITIGATION, COMPARISON):
        if not caminho.exists():
            continue
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
        "layout otimizado comprovadamente superior",
    )
    for caminho in (SPEC, DOC):
        if not caminho.exists():
            continue
        texto = caminho.read_text(encoding="utf-8").lower()
        for termo in proibidos:
            assert termo not in texto, f"overclaim em {caminho}: {termo}"
