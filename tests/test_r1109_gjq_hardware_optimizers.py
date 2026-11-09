#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos do otimizador hardware-aware para GJQ (R1109)."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1109-gjq-hardware-optimizers.md"
DOC = RAIZ / "docs" / "GJQ_OTIMIZADORES_HARDWARE_R1109.md"
HARNESS = RAIZ / "harnesses" / "gjq-hardware-optimizers"
RUNNER = HARNESS / "runner.py"
PERFIL_REAL = HARNESS / "resultados" / "baihua" / "perfil.json"
EXECUCAO_REAL = HARNESS / "resultados" / "baihua" / "E05_execucao"
SKILL = RAIZ / ".opencode" / "skills" / "gjq-hardware-optimizers" / "SKILL.md"
AGENTE = RAIZ / "agents" / "catalog" / "gjq-hardware-optimizer.md"


def _frontmatter(texto: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", texto, flags=re.S)
    assert m, "frontmatter ausente"
    return m.group(1)


def _target_teste():
    from qiskit.circuit import Measure, Parameter
    from qiskit.circuit.library import CZGate, HGate, RXGate, RYGate, RZGate
    from qiskit.transpiler import Target
    from qiskit.transpiler.target import InstructionProperties

    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
    directed = [e for a, b in edges for e in ((a, b), (b, a))]
    oneq = {0: 1.5e-3, 1: 8e-4, 2: 9e-4, 3: 3e-4, 4: 5e-4, 5: 1.1e-3, 6: 1.0e-3}
    readout = {0: 2.8e-2, 1: 1.4e-2, 2: 1.5e-2, 3: 6e-3, 4: 9e-3, 5: 2e-2, 6: 1.8e-2}
    cz = {}
    for index, (a, b) in enumerate(edges):
        base = 5e-3 * (1 + 0.1 * index)
        base *= 1 + 0.4 * abs(a - 3) + 0.4 * abs(b - 3)
        cz[(a, b)] = base
        cz[(b, a)] = base
    target = Target(num_qubits=7, description="gjq-test")
    target.add_instruction(
        HGate(), {(q,): InstructionProperties(error=oneq[q], duration=3e-8) for q in range(7)}
    )
    target.add_instruction(
        RXGate(Parameter("theta")),
        {(q,): InstructionProperties(error=oneq[q], duration=3e-8) for q in range(7)},
    )
    target.add_instruction(
        RYGate(Parameter("theta")),
        {(q,): InstructionProperties(error=oneq[q], duration=3e-8) for q in range(7)},
    )
    target.add_instruction(
        RZGate(Parameter("theta")),
        {(q,): InstructionProperties(error=0.0, duration=0.0) for q in range(7)},
    )
    target.add_instruction(
        CZGate(),
        {(a, b): InstructionProperties(error=cz[(a, b)], duration=3e-7) for a, b in directed},
    )
    target.add_instruction(
        Measure(),
        {(q,): InstructionProperties(error=readout[q], duration=1e-6) for q in range(7)},
    )
    return target


def _circuito_bell(num_qubits=2):
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(0)
    if num_qubits > 1:
        qc.cz(0, 1)
        qc.h(1)
    qc.measure(range(num_qubits), range(num_qubits))
    return qc


def test_arquivos_existem():
    for caminho in (SPEC, DOC, RUNNER, PERFIL_REAL, SKILL, AGENTE):
        assert caminho.exists(), caminho
        assert caminho.stat().st_size > 400, caminho
    for nome in ("__init__.py", "profile.py", "target.py", "layout.py", "optimizer.py", "estimator.py", "execution.py", "export.py"):
        assert (RAIZ / "gjq_hardware_opt" / nome).exists(), nome


def test_perfil_do_target():
    from gjq_hardware_opt import HardwareProfile

    profile = HardwareProfile.from_target(_target_teste(), "gjq-test", profile_kind="synthetic_test")
    assert profile.num_qubits == 7
    assert profile.basis_gates == ("cz", "h", "rx", "ry", "rz")
    assert profile.oneq_gates == ("h", "rx", "ry", "rz")
    assert profile.twoq_gates == ("cz",)
    assert len(profile.coupling_map) == 12
    assert set(profile.operational_qubits) == set(range(7))
    assert profile.target_fingerprint
    assert profile.summary()["edges"] == 12


def test_perfil_filtra_sentinela_e_degradado():
    from qiskit.circuit import Measure, Parameter
    from qiskit.circuit.library import CZGate, HGate, RZGate
    from qiskit.transpiler import Target
    from qiskit.transpiler.target import InstructionProperties
    from gjq_hardware_opt import HardwareProfile

    target = Target(num_qubits=4)
    target.add_instruction(
        HGate(), {(q,): InstructionProperties(error=0.001 if q < 3 else 0.05, duration=3e-8) for q in range(4)}
    )
    target.add_instruction(
        RZGate(Parameter("theta")),
        {(q,): InstructionProperties(error=0.0, duration=0.0) for q in range(4)},
    )
    target.add_instruction(
        CZGate(),
        {
            (0, 1): InstructionProperties(error=0.01, duration=3e-7),
            (1, 0): InstructionProperties(error=1.0, duration=3e-7),
            (1, 2): InstructionProperties(error=0.02, duration=3e-7),
            (2, 3): InstructionProperties(error=0.03, duration=3e-7),
        },
    )
    target.add_instruction(
        Measure(), {(q,): InstructionProperties(error=0.01, duration=1e-6) for q in range(4)}
    )
    profile = HardwareProfile.from_target(
        target,
        "sentinela",
        allowed_edges=[(0, 1), (1, 2)],
        degraded_qubit_threshold=0.05,
    )
    assert 3 not in profile.operational_qubits
    assert (2, 3) not in profile.coupling_map
    assert (1, 0) in profile.coupling_map  # cz simetrizado
    assert profile.twoq_error_for("cz", 1, 0) == pytest.approx(0.01)
    assert any("excluído" in w for w in profile.warnings)


def test_perfil_roundtrip():
    from gjq_hardware_opt import HardwareProfile

    profile = HardwareProfile.from_target(_target_teste(), "gjq-test")
    data = profile.to_dict()
    outro = HardwareProfile.from_dict(data)
    assert outro.to_dict() == data
    assert outro.target_fingerprint == profile.target_fingerprint
    assert outro.operational_qubits == profile.operational_qubits


def test_target_do_perfil():
    from gjq_hardware_opt import HardwareProfile, build_target_from_profile

    profile = HardwareProfile.from_target(_target_teste(), "gjq-test")
    target = build_target_from_profile(profile)
    assert set(target.operation_names) == {"h", "rx", "ry", "rz", "cz", "measure"}
    assert len(target["cz"]) == 12
    assert len(target["measure"]) == 7
    for (a, b) in target["cz"]:
        assert (a, b) in profile.coupling_map or (b, a) in profile.coupling_map


def test_layout_noise_aware():
    from gjq_hardware_opt import HardwareProfile, noise_aware_layout

    profile = HardwareProfile.from_target(_target_teste(), "gjq-test")
    circuit = _circuito_bell(2)
    layout = noise_aware_layout(circuit, profile, seed=42)
    assert layout.cost <= layout.trivial_cost
    assert len(set(layout.layout)) == 2
    assert all(0 <= p < profile.num_qubits for p in layout.layout)
    assert layout.physical_region


def test_otimizador_perfil_real_offline():
    if not PERFIL_REAL.exists():
        pytest.skip("perfil real do Baihua ausente")
    from gjq_hardware_opt import (
        GJQOptimizer,
        HardwareProfile,
        build_target_from_profile,
        load_circuit,
    )

    profile = HardwareProfile.from_dict(json.loads(PERFIL_REAL.read_text(encoding="utf-8")))
    target = build_target_from_profile(profile)
    item = load_circuit("E05")
    result = GJQOptimizer(profile, target=target, strategy="balanced", quick=True).optimize(
        item["circuit"]
    )
    assert result.chosen.status == "pass"
    assert result.chosen.estimate["success_proxy"] <= 1.0
    assert result.chosen.estimate["error_budget_proxy"] <= result.baseline.estimate["error_budget_proxy"]
    basis = set(profile.basis_gates) | {"measure"}
    for name in result.chosen.metrics["ops"]:
        assert name in basis, name
    for instruction in result.chosen.circuit.data:
        if len(instruction.qubits) == 2:
            a = result.chosen.circuit.find_bit(instruction.qubits[0]).index
            b = result.chosen.circuit.find_bit(instruction.qubits[1]).index
            assert (a, b) in profile.coupling_map or (b, a) in profile.coupling_map
    assert set(result.chosen.used_physical) <= set(profile.operational_qubits)


def test_compactacao_preserva_fisico():
    from qiskit import QuantumCircuit
    from gjq_hardware_opt import compact_to_used_physical

    qc = QuantumCircuit(6, 1)
    qc.h(5)
    qc.measure(5, 0)
    compact = compact_to_used_physical(qc)
    assert compact.num_qubits == 6
    assert compact.find_bit(compact.data[0].qubits[0]).index == 5


def test_gate_de_submissao():
    from gjq_hardware_opt import submission_gate

    qc = _circuito_bell(2)
    assert not submission_gate(
        "Baihua", shots=1024, circuit=qc, confirm=True, allow_hardware=True,
        api_key_present=False,
    )["allowed"]
    assert not submission_gate(
        "Baihua", shots=1024, circuit=qc, confirm=False, allow_hardware=True,
        api_key_present=True,
    )["allowed"]
    assert not submission_gate(
        "Baihua", shots=1024, circuit=qc, confirm=True, allow_hardware=False,
        api_key_present=True,
    )["allowed"]
    assert not submission_gate(
        "Baihua", shots=0, circuit=qc, confirm=True, allow_hardware=True,
        api_key_present=True,
    )["allowed"]
    assert submission_gate(
        "Baihua", shots=1024, circuit=qc, confirm=True, allow_hardware=True,
        api_key_present=True,
    )["allowed"]
    assert submission_gate(
        "FAS-CPU", shots=1024, circuit=qc, confirm=True, allow_hardware=False,
        api_key_present=True,
    )["allowed"]


def test_exportacao(tmp_path: Path):
    from gjq_hardware_opt import (
        GJQOptimizer,
        HardwareProfile,
        build_target_from_profile,
        export_result,
        load_circuit,
    )

    profile = HardwareProfile.from_dict(json.loads(PERFIL_REAL.read_text(encoding="utf-8")))
    result = GJQOptimizer(
        profile, target=build_target_from_profile(profile), quick=True
    ).optimize(load_circuit("E05")["circuit"])
    exported = export_result(result, tmp_path)
    for nome in ("otimizado.qasm2", "otimizado.qasm3", "baseline.qasm2", "resultado.json", "RELATORIO.md", "perfil.json"):
        assert (tmp_path / nome).exists(), nome
    assert (tmp_path / "otimizado.qasm2").read_text(encoding="utf-8").startswith("OPENQASM 2.0;")
    assert (tmp_path / "otimizado.qasm3").read_text(encoding="utf-8").startswith("OPENQASM 3.0;")
    assert exported["files"]["otimizado.qasm2"]["sha256"]
    assert "não é execução física" in (tmp_path / "RELATORIO.md").read_text(encoding="utf-8")


def test_cli_optimize_offline(tmp_path: Path):
    if not PERFIL_REAL.exists():
        pytest.skip("perfil real do Baihua ausente")
    r = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "optimize",
            "--profile",
            str(PERFIL_REAL),
            "--circuit",
            "E05",
            "--quick",
            "--out",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=RAIZ,
    )
    assert r.returncode == 0, r.stderr[-2000:]
    dados = json.loads((tmp_path / "resultado.json").read_text(encoding="utf-8"))
    assert dados["hardware_executed"] is False
    assert dados["network"] is False
    assert dados["chosen"]["status"] == "pass"


def test_cli_run_bloqueado_sem_chave(tmp_path: Path):
    env = os.environ.copy()
    env.pop("GJQ_API_KEY", None)
    r = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "run",
            "--backend",
            "Baihua",
            "--circuit",
            "E05",
            "--shots",
            "16",
            "--confirm",
            "--allow-hardware",
            "--out",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=RAIZ,
        env=env,
    )
    assert r.returncode == 2
    assert "credencial GJQ ausente" in r.stdout or "GJQ_API_KEY" in r.stdout
    assert not list(tmp_path.glob("counts.json"))


def test_execucao_real_registrada():
    if not EXECUCAO_REAL.exists():
        pytest.skip("execução real ausente")
    resultado = json.loads((EXECUCAO_REAL / "resultado_task.json").read_text(encoding="utf-8"))
    counts = resultado["result"]
    assert sum(counts.values()) == 1024
    assert resultado["counts_audit"]["ok"] is True
    relatorio = (EXECUCAO_REAL / "RESULTADO_REAL.md").read_text(encoding="utf-8")
    assert "1aeb1d6b-4d5b-4ecf-a434-789c579635d1" in relatorio
    assert "0.9160" in relatorio
    assert "não é fidelidade" in relatorio or "não\nfidelidade" in relatorio


def test_agente_managed_v1():
    fm = _frontmatter(AGENTE.read_text(encoding="utf-8"))
    for termo in (
        "agent_id: gjq-hardware-optimizer",
        "lifecycle: managed-v1",
        "type: specialist",
        "language: pt-BR",
        "parent: marceloclaro",
        "spec_file: specs/SPEC-935-R1109-gjq-hardware-optimizers.md",
        "test_file: tests/test_r1109_gjq_hardware_optimizers.py",
        "external_validation: false",
    ):
        assert termo in fm, termo


def test_registro_no_opencode():
    cfg = json.loads((RAIZ / "opencode.json").read_text(encoding="utf-8"))
    assert "gjq-hardware-optimizer" in cfg["agent"]
    assert cfg["agent"]["gjq-hardware-optimizer"]["prompt"] == (
        "{file:./agents/catalog/gjq-hardware-optimizer.md}"
    )


def test_skill_conteudo():
    texto = SKILL.read_text(encoding="utf-8").lower()
    for termo in ("gjq", "baihua", "allow_hardware", "confirm", "transpile=false", "proxy", "limites"):
        assert termo in texto, termo


def test_sem_segredo():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    for caminho in (SPEC, DOC, SKILL, AGENTE, RUNNER, PERFIL_REAL):
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
    )
    for caminho in (SPEC, DOC, SKILL, AGENTE):
        if not caminho.exists():
            continue
        texto = caminho.read_text(encoding="utf-8").lower()
        for termo in proibidos:
            assert termo not in texto, f"overclaim em {caminho}: {termo}"
