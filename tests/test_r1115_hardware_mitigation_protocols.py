#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos dos protocolos de mitigação para hardware (R1115)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1115-hardware-mitigation-protocols.md"
DOC = RAIZ / "docs" / "PROTOCOLOS_MITIGACAO_HARDWARE_R1115.md"
RUNNER = RAIZ / "harnesses" / "quantum-error-mitigation" / "runner.py"
HARDWARE = RAIZ / "harnesses" / "quantum-error-mitigation" / "resultados" / "hardware_zne_spam"
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


def _run(*args: str, timeout: int = 300):
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
    for caminho in (SPEC, DOC, RUNNER, HARDWARE / "execucao.json", *AGENTES):
        assert caminho.exists(), caminho
        assert caminho.stat().st_size > 400, caminho


def test_pec_2q_pauli():
    from quantum_mitigation import (
        pauli_channel_inverse,
        pec_plan,
        uniform_depolarizing_rates,
    )
    from gjq_hardware_opt import HardwareProfile, load_circuit

    result = pauli_channel_inverse(
        uniform_depolarizing_rates(0.01, 2), 2
    )
    assert len(result["labels"]) == 16
    assert result["gamma"] > 1.0
    assert abs(sum(result["q"].values()) - 1.0) < 1e-9
    profile = HardwareProfile.from_dict(
        json.loads(PERFIL.read_text(encoding="utf-8"))
    )
    plan = pec_plan(load_circuit("E05")["circuit"], profile)
    assert any(item["n_qubits"] == 2 for item in plan["gates"])
    assert plan["gamma_total"] > 1.0
    assert plan["samples_required"] > 1.0


def test_surface_budget():
    from quantum_mitigation import surface_code_plan

    d3 = surface_code_plan(distance=3, rounds=3, physical_error_rate=0.001)
    assert d3["qubit_budget"] == {
        "data": 9, "ancilla": 8, "total": 17, "syndrome_bits": 24,
    }
    assert d3["logical_error_estimate"] is None
    assert d3["decoder"]["executed"] is False
    d5 = surface_code_plan(distance=5, rounds=5, physical_error_rate=0.001)
    assert d5["qubit_budget"]["total"] == 49
    assert d5["qubit_budget"]["syndrome_bits"] == 120
    with_threshold = surface_code_plan(
        distance=3, rounds=3, physical_error_rate=0.001, threshold=0.01
    )
    assert with_threshold["logical_error_estimate"] == pytest.approx(0.01)


def test_dd_pulse():
    from quantum_mitigation import pulse_dd_plan

    plan = pulse_dd_plan(
        t1_us=70.0, t2_us=20.0, idle_time_us=10.0,
        sequence="cpmg", min_spacing_us=0.1,
    )
    assert plan["n_pulses"] == 100
    assert len(plan["timings_us"]) == 100
    assert plan["idle_over_t2"] == pytest.approx(0.5)
    assert "não expõe" in plan["limits"]
    xy4 = pulse_dd_plan(
        t1_us=70.0, t2_us=20.0, idle_time_us=10.0,
        sequence="xy4", min_spacing_us=0.1,
    )
    assert xy4["n_pulses"] % 4 == 0


def test_spam_separation():
    from quantum_mitigation import fit_spam_separation, spam_separation_plan

    def p1(k, e=0.02, r0=0.01, r1=0.03):
        p0 = (1.0 + (1.0 - 2.0 * e) ** k) / 2.0
        return (1.0 - r1) + p0 * (r0 - (1.0 - r1))

    shots = 200000
    counts = {}
    for k in (1, 3, 5):
        value = p1(k)
        counts[str(k)] = {
            "1": round(value * shots),
            "0": shots - round(value * shots),
        }
    fit = fit_spam_separation(counts)
    assert fit["identified"] is True
    assert fit["prep_error_per_pi"] == pytest.approx(0.02, abs=2e-3)
    assert fit["readout_p1_given_prep0"] == pytest.approx(0.01, abs=2e-3)
    assert fit["readout_p0_given_prep1"] == pytest.approx(0.03, abs=2e-3)
    plan = spam_separation_plan([0, 1], (1, 3, 5))
    assert len(plan) == 6
    assert "rx(pi)" in plan["q0_k1"]


def test_zne_applicability():
    from quantum_mitigation import zne_applicability

    good = zne_applicability([1, 3, 5], [0.05, 0.08, 0.11])
    assert good["monotonic"] is True
    assert good["applicable"] is True
    bad = zne_applicability([1, 3, 5], [0.0706, 0.1003, 0.0671])
    assert bad["monotonic"] is False
    assert bad["applicable"] is False


def test_preregister():
    from quantum_mitigation import preregister_ci

    result = preregister_ci(0.92, 0.01)
    assert result["n"] > 1000
    assert result["observed_half_width"] <= 0.01
    assert result["expected_interval"]["low"] < 0.92 < result["expected_interval"]["high"]


def test_harness_surface_dd_prereg(tmp_path: Path):
    commands = [
        (
            ["surface", "--distance", "3", "--rounds", "3", "--p", "0.001",
             "--out", str(tmp_path / "surface")],
            "surface",
        ),
        (
            ["dd-pulse", "--t1-us", "70", "--t2-us", "20", "--idle-us", "10",
             "--sequence", "cpmg", "--out", str(tmp_path / "dd-pulse")],
            "dd-pulse",
        ),
        (
            ["preregister", "--p", "0.92", "--half-width", "0.01",
             "--out", str(tmp_path / "preregister")],
            "preregister",
        ),
        (
            ["spam-plan", "--qubits", "0", "1", "--ks", "1", "3", "5",
             "--out", str(tmp_path / "spam-plan")],
            "spam-plan",
        ),
    ]
    for args, name in commands:
        result = _run(str(RUNNER), *args, timeout=300)
        assert result.returncode == 0, result.stderr[-2000:]
        payload = json.loads((tmp_path / name / "resultado.json").read_text(encoding="utf-8"))
        assert payload["schema_version"] == 1
        assert (tmp_path / name / "RELATORIO.md").exists()


def test_agentes_com_novos_comandos():
    expected = {
        "quantum-error-mitigation": {"zne", "dd", "dd-pulse", "pec", "audit", "lessons"},
        "quantum-error-correction": {"qec", "surface", "audit", "lessons"},
        "quantum-noise-characterization": {
            "spam", "spam-plan", "spam-separation", "crosstalk",
            "drift", "uncertainty", "preregister", "audit", "lessons",
        },
    }
    from agents.lifecycle import validate_managed_card

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
        assert validate_managed_card(RAIZ, path, path.read_bytes())["definition_validated"] is True


def test_opencode_registro():
    cfg = json.loads((RAIZ / "opencode.json").read_text(encoding="utf-8"))
    for path in AGENTES:
        agent_id = _frontmatter(path)["agent_id"]
        assert agent_id in cfg["agent"]
        assert cfg["agent"][agent_id]["prompt"] == f"{{file:./agents/catalog/{path.name}}}"


def test_hardware_artefatos():
    if not (HARDWARE / "execucao.json").exists():
        pytest.skip("hardware ainda não executado")
    data = json.loads((HARDWARE / "execucao.json").read_text(encoding="utf-8"))
    assert data["hardware_executed"] is True
    assert data["submissions"]["total"] == 9
    assert len(data["zne"]["rows"]) == 3
    assert data["zne"]["applicability"]["monotonic"] is False
    for row in data["zne"]["rows"]:
        assert sum(row["counts"].values()) == 4096
    for q in ("q0", "q1"):
        assert data["spam"][q]["identified"] is False
        for counts in data["spam"][q]["counts"].values():
            assert sum(counts.values()) == 4096
    report = (HARDWARE / "RELATORIO.md").read_text(encoding="utf-8")
    assert "não é monotônica" in report
    assert "não são físicos" in report


def test_sem_segredo():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    for caminho in (SPEC, DOC, RUNNER, HARDWARE / "execucao.json", *AGENTES):
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
        "threshold de superfície comprovado",
        "correção total de erro",
    )
    for caminho in (SPEC, DOC, *AGENTES):
        text = caminho.read_text(encoding="utf-8").lower()
        for termo in proibidos:
            assert termo not in text, f"overclaim em {caminho}: {termo}"
