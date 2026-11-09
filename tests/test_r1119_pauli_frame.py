#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos do passe de Pauli-frame para RC (R1119)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit.library import CXGate, CZGate, HGate, SGate
from qiskit.quantum_info import Clifford, Pauli

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1119-pauli-frame-rc.md"
MODULE = RAIZ / "quantum_mitigation" / "randomized_compiling.py"
RUNNER = RAIZ / "harnesses" / "quantum-error-mitigation" / "runner.py"


def test_arquivos_existem():
    for caminho in (SPEC, MODULE, RUNNER):
        assert caminho.exists(), caminho


def test_conjugacao_conhecida():
    from quantum_mitigation import conjugate_pauli

    h = Clifford(HGate())
    assert str(conjugate_pauli(h, Pauli("X"))) == "Z"
    assert str(conjugate_pauli(h, Pauli("Y"))) == "Y"
    assert str(conjugate_pauli(h, Pauli("Z"))) == "X"

    s = Clifford(SGate())
    assert str(conjugate_pauli(s, Pauli("X"))) == "Y"
    assert str(conjugate_pauli(s, Pauli("Y"))) == "X"
    assert str(conjugate_pauli(s, Pauli("Z"))) == "Z"

    cx = Clifford(CXGate())
    expected = {
        "IX": "XX",
        "XI": "XI",
        "IZ": "IZ",
        "ZI": "ZZ",
        "XX": "IX",
        "XZ": "XZ",
        "ZX": "YY",
        "ZZ": "ZI",
    }
    for label, result in expected.items():
        assert str(conjugate_pauli(cx, Pauli(label))) == result

    cz = Clifford(CZGate())
    assert str(conjugate_pauli(cz, Pauli("IX"))) == "ZX"
    assert str(conjugate_pauli(cz, Pauli("XI"))) == "XZ"
    assert str(conjugate_pauli(cz, Pauli("ZZ"))) == "ZZ"


def test_random_pauli_cobertura():
    from quantum_mitigation import random_pauli

    rng = np.random.default_rng(7)
    one = {str(random_pauli(1, rng)) for _ in range(200)}
    assert one == {"I", "X", "Y", "Z"}
    two = {str(random_pauli(2, rng)) for _ in range(500)}
    assert len(two) == 16


def _circuit_1q() -> QuantumCircuit:
    circuit = QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.s(0)
    circuit.measure(0, 0)
    return circuit


def _circuit_2q() -> QuantumCircuit:
    circuit = QuantumCircuit(2, 1)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure(1, 0)
    return circuit


def test_twirl_1q_equivalente():
    from quantum_mitigation import pauli_frame_pass, verify_equivalence

    original = _circuit_1q()
    result = pauli_frame_pass(original, seed=11)
    assert result["n_twirls"] == 2
    assert len(result["twirls"]) == 2
    assert result["skipped"] == []
    assert result["circuit"].count_ops().get("measure", 0) == 1
    verification = verify_equivalence(original, result["circuit"])
    assert verification["equivalent_up_to_phase"] is True


def test_twirl_2q_equivalente():
    from quantum_mitigation import pauli_frame_pass, verify_equivalence

    original = _circuit_2q()
    result = pauli_frame_pass(original, seed=12)
    assert result["n_twirls"] == 2
    assert result["circuit"].count_ops().get("measure", 0) == 1
    assert result["circuit"].num_clbits == original.num_clbits
    verification = verify_equivalence(original, result["circuit"])
    assert verification["equivalent_up_to_phase"] is True
    assert verification["overlap"]["abs"] == pytest.approx(1.0, abs=1e-8)


def test_determinismo_por_seed():
    from qiskit import qasm2

    from quantum_mitigation import pauli_frame_pass

    circuit = QuantumCircuit(1)
    circuit.h(0)
    circuit.s(0)
    circuit.h(0)
    first = pauli_frame_pass(circuit, seed=99)
    second = pauli_frame_pass(circuit, seed=99)
    assert qasm2.dumps(first["circuit"]) == qasm2.dumps(second["circuit"])
    sequences = {
        tuple(item["pauli"] for item in pauli_frame_pass(circuit, seed=seed)["twirls"])
        for seed in range(10)
    }
    assert len(sequences) > 1


def test_nao_clifford_estrito_e_tolerante():
    from quantum_mitigation import pauli_frame_pass, verify_equivalence

    circuit = QuantumCircuit(1)
    circuit.rx(0.1, 0)
    with pytest.raises(ValueError, match="não é Clifford|não suportada"):
        pauli_frame_pass(circuit, seed=1)
    tolerated = pauli_frame_pass(circuit, seed=1, strict=False)
    assert tolerated["n_twirls"] == 0
    assert tolerated["skipped"] == ["rx"]
    assert verify_equivalence(circuit, tolerated["circuit"])["equivalent_up_to_phase"] is True


def test_harness_rc(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "rc",
            "--qubit",
            "1",
            "--seed",
            "1234",
            "--out",
            str(tmp_path / "rc"),
        ],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    payload = json.loads(
        (tmp_path / "rc" / "resultado.json").read_text(encoding="utf-8")
    )
    assert payload["n_twirls"] == 1
    assert payload["verification"]["equivalent_up_to_phase"] is True
    assert payload["hardware_executed"] is False
    assert (tmp_path / "rc" / "twirled.qasm").exists()
    assert (tmp_path / "rc" / "RELATORIO.md").exists()


def test_modulo_sem_hardware():
    text = MODULE.read_text(encoding="utf-8")
    for termo in ("gjq_hardware_opt", "connect_gjq", "submit_optimized", "allow_hardware"):
        assert termo not in text, termo


def test_sem_segredo_ou_overclaim():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    proibidos = (
        "rc validado em hardware",
        "redução de erro comprovada",
        "vantagem quântica comprovada",
        "speedup garantido",
        "benchmark definitivo",
    )
    for caminho in (SPEC, MODULE):
        text = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(text), f"segredo em {caminho}"
        for termo in proibidos:
            assert termo.lower() not in text.lower(), f"overclaim em {caminho}: {termo}"
