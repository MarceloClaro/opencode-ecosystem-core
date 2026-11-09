#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos de mitigação e correção de erro quântico (R1114)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1114-quantum-error-mitigation-correction.md"
SKILL = RAIZ / ".opencode" / "skills" / "mitigacao-e-correcao-quantica" / "SKILL.md"
RUNNER = RAIZ / "harnesses" / "quantum-error-mitigation" / "runner.py"
WRAPPER = RAIZ / "harnesses" / "quantum-error-mitigation" / "agent_qem.py"
PERFIL = (
    RAIZ
    / "harnesses"
    / "gjq-hardware-optimizers"
    / "resultados"
    / "baihua"
    / "E05"
    / "perfil.json"
)
AGENTES = [
    RAIZ / "agents" / "catalog" / "quantum-error-mitigation.md",
    RAIZ / "agents" / "catalog" / "quantum-error-correction.md",
    RAIZ / "agents" / "catalog" / "quantum-noise-characterization.md",
]


def _run(*args: str, timeout: int = 600):
    return subprocess.run(
        [sys.executable, *args],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    assert match, f"frontmatter ausente: {path}"
    return yaml.safe_load(match.group(1))


def test_arquivos_existem():
    for caminho in (SPEC, SKILL, RUNNER, WRAPPER, *AGENTES):
        assert caminho.exists(), caminho
        assert caminho.stat().st_size > 400, caminho


def test_zne_folding_e_extrapolacao():
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    from quantum_mitigation import extrapolate, fold_circuit

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    folded_1 = fold_circuit(qc, 1)
    folded_3 = fold_circuit(qc, 3)
    assert folded_1.num_qubits == 2
    assert folded_3.depth() >= folded_1.depth()
    left = Statevector.from_instruction(folded_1)
    right = Statevector.from_instruction(folded_3)
    assert abs(abs(left.inner(right)) - 1.0) < 1e-9
    result = extrapolate([1, 3, 5], [0.3, 0.2, 0.1], "linear")
    assert result["extrapolated"] == pytest.approx(0.35)
    assert extrapolate([1, 3, 5], [0.3, 0.2, 0.1], "quadratic")["method"] == "quadratic"


def test_dd_identidade():
    from qiskit import QuantumCircuit
    from quantum_mitigation import dd_plan, verify_identity

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    plan = dd_plan(qc, [0, 1], "xy4")
    assert plan["identity_ok"] is True
    assert plan["identity_fidelity"] >= 1.0 - 1e-9
    assert verify_identity(qc, [0, 1], "cpmg") >= 1.0 - 1e-9


def test_pec_planejador():
    from quantum_mitigation import depolarizing_quasiprobabilities, pec_plan
    from gjq_hardware_opt import HardwareProfile, load_circuit

    quasi = depolarizing_quasiprobabilities(0.01)
    assert quasi["gamma"] > 1.0
    assert quasi["I"] > 1.0
    assert quasi["X"] < 0.0
    assert quasi["Y"] == pytest.approx(quasi["X"])
    profile = HardwareProfile.from_dict(json.loads(PERFIL.read_text(encoding="utf-8")))
    plan = pec_plan(load_circuit("E05")["circuit"], profile)
    assert plan["gamma_total"] > 1.0
    assert plan["samples_required"] > 1.0
    assert any("PEC 2q" in warning for warning in plan["warnings"])


def test_qec_repeticao():
    from quantum_mitigation import qec_plan, run_repetition_code

    plan = qec_plan(distance=3, p=0.01)
    assert plan["logical_error_theory"] == pytest.approx(3 * 0.01**2 - 2 * 0.01**3)
    result = run_repetition_code(0.01, shots=5000, seed=42)
    assert result["counts_total"] == 5000
    assert result["logical_error_simulated"] is not None
    assert result["logical_error_simulated"] < 0.01
    assert "bit-flip" in result["limits"]


def test_caracterizacao():
    from quantum_mitigation import (
        bootstrap_ci,
        crosstalk_metric,
        drift_detection,
        fit_spam,
        spam_circuits,
        uncertainty_report,
        wilson_interval,
    )

    spam = fit_spam({"0": 990, "1": 10}, {"0": 30, "1": 970})
    assert spam["p1_given_prep0"] == pytest.approx(0.01)
    assert spam["p0_given_prep1"] == pytest.approx(0.03)
    assert spam["readout_error_symmetric"] == pytest.approx(0.02)
    circuits = spam_circuits([0, 1])
    assert "rx(pi)" in circuits["1"]
    crosstalk = crosstalk_metric(0.01, 0.02)
    assert crosstalk["ratio"] == pytest.approx(2.0)
    assert crosstalk["excess"] == pytest.approx(0.01)
    drift = drift_detection([0.01, 0.011, 0.013, 0.016, 0.020])
    assert drift["slope_per_step"] > 0
    interval = wilson_interval(10, 100)
    assert interval["low"] < 0.1 < interval["high"]
    bootstrap = bootstrap_ci([0.020, 0.025, 0.022, 0.024])
    assert bootstrap["low"] <= bootstrap["mean"] <= bootstrap["high"]
    report = uncertainty_report([0.020, 0.025, 0.022, 0.024])
    assert report["n"] == 4
    assert report["bootstrap"] is not None


def test_harness_zne_dd_pec(tmp_path: Path):
    if not PERFIL.exists():
        pytest.skip("perfil real ausente")
    commands = [
        (
            ["zne", "--profile", str(PERFIL), "--circuit", "E05",
             "--scales", "1", "3", "--shots", "256", "--out", str(tmp_path / "zne")],
            "zne",
        ),
        (
            ["dd", "--circuit", "E05", "--qubits", "0", "1",
             "--sequence", "xy4", "--out", str(tmp_path / "dd")],
            "dd",
        ),
        (
            ["pec", "--profile", str(PERFIL), "--circuit", "E05",
             "--out", str(tmp_path / "pec")],
            "pec",
        ),
    ]
    for args, name in commands:
        result = _run(str(RUNNER), *args, timeout=600)
        assert result.returncode == 0, result.stderr[-2000:]
        payload = json.loads((tmp_path / name / "resultado.json").read_text(encoding="utf-8"))
        assert payload["schema_version"] == 1
        assert (tmp_path / name / "RELATORIO.md").exists()


def test_harness_qec_e_incerteza(tmp_path: Path):
    qec = _run(
        str(RUNNER), "qec", "--p", "0.01", "--shots", "2000",
        "--out", str(tmp_path / "qec"), timeout=300,
    )
    assert qec.returncode == 0, qec.stderr[-2000:]
    payload = json.loads((tmp_path / "qec" / "resultado.json").read_text(encoding="utf-8"))
    assert payload["logical_error_simulated"] < 0.01
    unc = _run(
        str(RUNNER), "uncertainty", "--values", "0.020", "0.025", "0.022",
        "--out", str(tmp_path / "unc"), timeout=120,
    )
    assert unc.returncode == 0, unc.stderr[-2000:]


def test_agentes_managed_v1():
    from agents.lifecycle import validate_managed_card

    for path in AGENTES:
        meta = _frontmatter(path)
        assert meta["lifecycle"] == "managed-v1"
        assert meta["spec_file"] == "specs/SPEC-935-R1114-quantum-error-mitigation-correction.md"
        assert meta["test_file"] == "tests/test_r1114_quantum_error_mitigation.py"
        assert meta["allow_edit"] is True
        assert meta["tools"] == {
            "read": True, "glob": True, "grep": True,
            "bash": True, "edit": True, "write": True,
        }
        assert meta["output_contract"]["evidence_required"] is True
        bash = meta["permission"]["bash"]
        assert bash["*"] == "deny"
        assert not any("runner.py" in key for key in bash)
        result = validate_managed_card(RAIZ, path, path.read_bytes())
        assert result["definition_validated"] is True


def test_permissões_especificas():
    expected = {
        "quantum-error-mitigation": {"zne", "dd", "pec", "audit", "lessons"},
        "quantum-error-correction": {"qec", "audit", "lessons"},
        "quantum-noise-characterization": {
            "spam", "crosstalk", "drift", "uncertainty", "audit", "lessons",
        },
    }
    for path in AGENTES:
        meta = _frontmatter(path)
        agent_id = meta["agent_id"]
        bash = meta["permission"]["bash"]
        for command in expected[agent_id]:
            key = (
                ".venv-quantum/bin/python harnesses/quantum-error-mitigation/"
                f"agent_qem.py {command}*"
            )
            assert bash[key] == "allow", (agent_id, command)
        assert bash["python3 -m marceloclaro.cli doctor"] == "allow"


def test_registro_no_opencode():
    cfg = json.loads((RAIZ / "opencode.json").read_text(encoding="utf-8"))
    for path in AGENTES:
        agent_id = _frontmatter(path)["agent_id"]
        assert agent_id in cfg["agent"], agent_id
        assert cfg["agent"][agent_id]["prompt"] == f"{{file:./agents/catalog/{path.name}}}"


def test_wrapper_rejeita_desconhecido():
    result = _run(str(WRAPPER), "run", "--backend", "Baihua", timeout=60)
    assert result.returncode == 2
    assert "não permitido" in result.stderr


def test_skill_conteudo():
    text = SKILL.read_text(encoding="utf-8").lower()
    for termo in ("zne", "pec", "dd", "qec", "spam", "crosstalk", "drift", "limites"):
        assert termo in text, termo


def test_sem_segredo():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    for caminho in [SPEC, SKILL, RUNNER, WRAPPER, *AGENTES]:
        text = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(text), f"segredo em {caminho}"


def test_sem_overclaim():
    proibidos = (
        "fidelidade medida com sucesso",
        "vantagem quântica comprovada",
        "speedup garantido",
        "prova experimental de emaranhamento",
        "benchmark definitivo",
        "correção total de erro",
        "threshold de superfície comprovado",
    )
    for caminho in [SPEC, SKILL, *AGENTES]:
        text = caminho.read_text(encoding="utf-8").lower()
        for termo in proibidos:
            assert termo not in text, f"overclaim em {caminho}: {termo}"
