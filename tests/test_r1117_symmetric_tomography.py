#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos da comparação simétrica q0/q1 e da tomografia generalizada (R1117)."""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1117-symmetric-tomography-q0-q1.md"
SCRIPT = RAIZ / "harnesses" / "quantum-error-mitigation" / "hardware_tomography_q1.py"
BASE = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados"
Q0_DIR = BASE / "hardware_tomography_q0"
Q1_DIR = BASE / "hardware_tomography_q1"
COMPARISON = BASE / "comparison_q0_q1.json"
REPORT = BASE / "RELATORIO_Q0_Q1.md"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _module():
    spec = importlib.util.spec_from_file_location("hw_tomography", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_arquivos_existem():
    for caminho in (
        SPEC,
        SCRIPT,
        Q0_DIR / "set1.json",
        Q0_DIR / "set2.json",
        Q0_DIR / "comparison.json",
        Q1_DIR / "set1.json",
        Q1_DIR / "set2.json",
        Q1_DIR / "comparison.json",
        COMPARISON,
        REPORT,
    ):
        assert caminho.exists(), caminho


def test_dois_conjuntos_por_qubit():
    q0 = _load(Q0_DIR / "comparison.json")
    q1 = _load(Q1_DIR / "comparison.json")
    for payload in (q0, q1):
        assert payload["n_sets"] == 2
        assert payload["shots_per_set"] == 4096
        assert payload["fit_combined"]["identified"] is True
        assert payload["bootstrap_combined"]["n_bootstrap"] == 2000
        assert set(payload["sets"]) == {"set1", "set2"}


def test_fit_reproduzido_dos_counts():
    from quantum_mitigation import fit_spam_tomography

    module = _module()
    for prefix, directory in (("q0", Q0_DIR), ("q1", Q1_DIR)):
        set1 = _load(directory / "set1.json")
        set2 = _load(directory / "set2.json")
        fit1 = fit_spam_tomography(set1["counts"], prefix=prefix)
        assert fit1["prep_fidelity"] == pytest.approx(set1["fit"]["prep_fidelity"])
        combined = module._combine(set1, set2)
        fit = fit_spam_tomography(combined, prefix=prefix)
        stored = _load(directory / "comparison.json")["fit_combined"]
        assert fit["prep_fidelity"] == pytest.approx(stored["prep_fidelity"])
        assert fit["readout_p1_given_prep0"] == pytest.approx(
            stored["readout_p1_given_prep0"]
        )
        assert fit["readout_p0_given_prep1"] == pytest.approx(
            stored["readout_p0_given_prep1"]
        )


def test_redundancia_prep_readout():
    for directory in (Q0_DIR, Q1_DIR):
        fit = _load(directory / "comparison.json")["fit_combined"]
        fidelity = fit["prep_fidelity"]
        assert fidelity["0"] == pytest.approx(
            1.0 - fit["readout_p1_given_prep0"], abs=1e-9
        )
        assert fidelity["1"] == pytest.approx(
            1.0 - fit["readout_p0_given_prep1"], abs=1e-9
        )


def test_deltas_e_spread():
    payload = _load(COMPARISON)
    assert payload["q0"]["n_sets"] == 2
    assert payload["q1"]["n_sets"] == 2
    deltas = payload["deltas"]
    for key in ("prep_0", "prep_1", "prep_+", "prep_+i", "r0", "r1"):
        item = deltas[key]
        assert item["delta_q1_minus_q0"] == pytest.approx(
            item["q1"] - item["q0"], abs=1e-12
        )
        assert item["ci_overlap"] is True
        assert item["q0_set_spread"] is not None
        assert item["q1_set_spread"] is not None
    assert deltas["prep_1"]["delta_q1_minus_q0"] < 0
    assert deltas["r1"]["delta_q1_minus_q0"] > 0
    assert abs(deltas["r1"]["delta_q1_minus_q0"]) <= max(
        deltas["r1"]["q0_set_spread"], deltas["r1"]["q1_set_spread"]
    )


def test_simulacao_generalizada():
    from qiskit import qasm2

    from quantum_mitigation import spam_tomography_plan

    module = _module()
    for qubit in (0, 1):
        circuits = {
            key: qasm2.loads(qasm)
            for key, qasm in spam_tomography_plan(qubit).items()
        }
        result = module._run_simulation(circuits, prefix=f"q{qubit}")
        assert result["ok"] is True, result["failures"]


def test_analise_reproduz_em_diretorio_temporario(tmp_path: Path):
    module = _module()
    for name, directory in (("q0", Q0_DIR), ("q1", Q1_DIR)):
        target = tmp_path / name
        target.mkdir()
        for set_name in ("set1.json", "set2.json"):
            (target / set_name).write_text(
                (directory / set_name).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        payload = module._analyze_qubit(target, name, n_bootstrap=50, seed=7)
        assert payload is not None
        assert payload["n_sets"] == 2
        assert (target / "comparison.json").exists()
        assert (target / f"RELATORIO_{name.upper()}.md").exists()


def test_run_set_bloqueado_sem_confirmacao():
    module = _module()
    assert module.main(["--qubit", "0", "--set", "1"]) == 2
    assert module.main(["--qubit", "1", "--set", "2"]) == 2


def test_relatorio_declara_redundancia_e_nao_conclusao():
    text = REPORT.read_text(encoding="utf-8")
    assert "não são evidências independentes" in text
    assert "Sobreposição de IC não equivale" in text
    assert "Nenhuma vantagem quântica" in text
    assert "Δ (q1−q0)" in text


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
        "q1 é definitivamente pior",
    )
    for caminho in (SPEC, SCRIPT, COMPARISON, REPORT):
        text = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(text), f"segredo em {caminho}"
        for termo in proibidos:
            assert termo.lower() not in text.lower(), f"overclaim em {caminho}: {termo}"
