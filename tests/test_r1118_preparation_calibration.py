#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos da calibração Rabi da preparação (R1118)."""
from __future__ import annotations

import importlib.util
import json
import math
import re
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1118-rabi-preparation-calibration.md"
MODULE = RAIZ / "quantum_mitigation" / "preparation.py"
SCRIPT = RAIZ / "harnesses" / "quantum-error-mitigation" / "hardware_rabi_calibration.py"
RABI = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "hardware_rabi_q1" / "rabi_q1.json"
RABI_REPORT = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "hardware_rabi_q1" / "RELATORIO_RABI.md"
ANGLES = [math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi,
          5 * math.pi / 4, 3 * math.pi / 2, 7 * math.pi / 4, 2 * math.pi]


def _synthetic_counts(plan: dict, axis: str, *, epsilon: float, r0: float,
                      r1: float, shots: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    counts = {}
    contrast = 1.0 - r0 - r1
    for key, item in plan.items():
        if item["axis"] != axis:
            continue
        p1_true = math.sin((item["theta"] + epsilon) / 2.0) ** 2
        p1 = r0 + contrast * p1_true
        ones = int(rng.binomial(shots, p1))
        counts[key] = {"0": int(shots - ones), "1": ones}
    return counts


def test_arquivos_existem():
    for caminho in (SPEC, MODULE, SCRIPT):
        assert caminho.exists(), caminho


def test_plano_16_circuitos():
    from quantum_mitigation.preparation import rabi_calibration_plan

    default_plan = rabi_calibration_plan(qubit=1)
    assert len(default_plan) == 16
    plan = rabi_calibration_plan(qubit=1, angles=ANGLES, axes=("x", "y"))
    assert len(plan) == 16
    assert sum(1 for item in plan.values() if item["axis"] == "x") == 8
    assert sum(1 for item in plan.values() if item["axis"] == "y") == 8
    angles = sorted(item["theta"] for item in plan.values() if item["axis"] == "x")
    assert angles == pytest.approx(sorted(ANGLES))
    for item in plan.values():
        assert item["qasm"].startswith("OPENQASM")
        assert "measure" in item["qasm"]


def test_simulacao_ideal():
    from qiskit import qasm2
    from qiskit.quantum_info import Statevector

    from quantum_mitigation.preparation import rabi_calibration_plan

    plan = rabi_calibration_plan(qubit=1, angles=ANGLES, axes=("x",))
    for item in plan.values():
        circuit = qasm2.loads(item["qasm"])
        sv = Statevector.from_instruction(circuit.remove_final_measurements(inplace=False))
        p0 = float(sv.probabilities([1])[0])
        assert p0 == pytest.approx(math.cos(item["theta"] / 2.0) ** 2, abs=1e-9)


def test_ajuste_recupera_parametros():
    from quantum_mitigation.preparation import (
        fit_rabi_calibration,
        rabi_calibration_plan,
    )

    plan = rabi_calibration_plan(qubit=1, angles=ANGLES, axes=("x", "y"))
    counts = _synthetic_counts(
        plan, "x", epsilon=0.10, r0=0.016, r1=0.084, shots=200_000, seed=11
    )
    counts.update(
        _synthetic_counts(
            plan, "y", epsilon=-0.20, r0=0.016, r1=0.084, shots=200_000, seed=12
        )
    )
    fit = fit_rabi_calibration(plan, counts)
    x = fit["axes"]["x"]
    y = fit["axes"]["y"]
    assert x["identified"] is True
    assert y["identified"] is True
    assert x["epsilon"] == pytest.approx(0.10, abs=0.02)
    assert y["epsilon"] == pytest.approx(-0.20, abs=0.02)
    assert x["r0"] == pytest.approx(0.016, abs=0.01)
    assert x["r1"] == pytest.approx(0.084, abs=0.01)
    assert x["contrast"] == pytest.approx(0.90, abs=0.01)
    assert x["theta_star"] == pytest.approx(math.pi - 0.10, abs=0.02)
    assert abs(x["epsilon"]) < abs(y["epsilon"])
    assert fit["preferred_axis"] == "x"
    assert fit["gain_vs_pi"] > 0


def test_ajuste_sem_desvio():
    from quantum_mitigation.preparation import (
        fit_rabi_calibration,
        rabi_calibration_plan,
    )

    plan = rabi_calibration_plan(qubit=1, angles=ANGLES, axes=("x",))
    counts = _synthetic_counts(
        plan, "x", epsilon=0.0, r0=0.02, r1=0.07, shots=100_000, seed=3
    )
    fit = fit_rabi_calibration(plan, counts)
    x = fit["axes"]["x"]
    assert abs(x["epsilon"]) < 0.02
    assert x["gain_vs_pi"] < 0.001


def test_contraste_inviavel_nao_identificado():
    from quantum_mitigation.preparation import (
        fit_rabi_calibration,
        rabi_calibration_plan,
    )

    plan = rabi_calibration_plan(qubit=1, angles=ANGLES, axes=("x",))
    counts = {
        key: {"0": 1000, "1": 1000}
        for key in plan
    }
    fit = fit_rabi_calibration(plan, counts)
    assert fit["axes"]["x"]["identified"] is False


def test_script_bloqueado_sem_confirmacao():
    spec = importlib.util.spec_from_file_location("rabi_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert module.main(["--qubit", "1"]) == 2
    assert module.main(["--qubit", "1", "--confirm"]) == 2


def test_sem_segredo_ou_overclaim():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    proibidos = (
        "vantagem quântica comprovada",
        "speedup garantido",
        "prova experimental de emaranhamento",
        "benchmark definitivo",
        "calibração perfeita",
    )
    for caminho in (SPEC, MODULE, SCRIPT):
        text = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(text), f"segredo em {caminho}"
        for termo in proibidos:
            assert termo.lower() not in text.lower(), f"overclaim em {caminho}: {termo}"


def test_artefato_rabi_real():
    assert RABI.exists(), RABI
    assert RABI_REPORT.exists(), RABI_REPORT
    payload = json.loads(RABI.read_text(encoding="utf-8"))
    assert payload["qubit"] == 1
    assert payload["shots"] == 4096
    assert len(payload["counts"]) == 16
    assert len(payload["task_ids"]) == 16
    fit = payload["fit"]
    assert set(fit["axes"]) == {"x", "y"}
    assert fit["preferred_axis"] == "none"
    for axis, item in fit["axes"].items():
        assert item["identified"] is True
        assert abs(item["epsilon"]) < 0.01
        assert 0.05 < item["r1"] < 0.10
    report = RABI_REPORT.read_text(encoding="utf-8")
    assert "Não foi detectado desvio coerente" in report
    assert "Nenhum ângulo corrigido é justificado" in report


def test_scorecard_integra_rabi():
    from quantum_mitigation import resilience_scorecard

    rabi = json.loads(RABI.read_text(encoding="utf-8"))
    payload = resilience_scorecard(
        tomography_q0={
            "prep_fidelity": {"0": 0.98, "1": 0.92, "+": 0.98, "+i": 0.98},
            "readout_p1_given_prep0": 0.016,
            "readout_p0_given_prep1": 0.077,
        },
        tomography_q1={
            "prep_fidelity": {"0": 0.98, "1": 0.92, "+": 0.98, "+i": 0.98},
            "readout_p1_given_prep0": 0.016,
            "readout_p0_given_prep1": 0.077,
        },
        rabi=rabi,
    )
    findings = " ".join(payload["findings"])
    assert "Rabi" in findings
    assert "não detectado" in findings
    actions = " ".join(item["action"] for item in payload["recommendations"])
    assert "manter o pulso π padrão" in actions
    assert payload["rabi"]["coherent_offset_detected"] is False


def test_scorecard_rabi_com_desvio():
    from quantum_mitigation import resilience_scorecard

    fake = {
        "fit": {
            "identified": True,
            "preferred_axis": "x",
            "axes": {
                "x": {
                    "epsilon": 0.10,
                    "epsilon_se": 0.01,
                    "r0": 0.02,
                    "r1": 0.07,
                    "contrast": 0.91,
                    "identified": True,
                }
            },
        }
    }
    payload = resilience_scorecard(rabi=fake)
    actions = " ".join(item["action"] for item in payload["recommendations"])
    assert "validar o ângulo corrigido" in actions
    assert payload["rabi"]["coherent_offset_detected"] is True
