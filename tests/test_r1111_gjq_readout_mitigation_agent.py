#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos do agente dedicado gjq-readout-mitigation (R1111)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1111-gjq-readout-mitigation-agent.md"
AGENTE = RAIZ / "agents" / "catalog" / "gjq-readout-mitigation.md"
WRAPPER = RAIZ / "harnesses" / "gjq-hardware-optimizers" / "agent_readout.py"
PERFIL = RAIZ / "harnesses" / "gjq-hardware-optimizers" / "resultados" / "baihua" / "E05" / "perfil.json"
COUNT = (
    RAIZ
    / "harnesses"
    / "gjq-hardware-optimizers"
    / "resultados"
    / "baihua"
    / "E05_comparacao"
    / "otimizado"
    / "counts.json"
)
COMPARACAO = (
    RAIZ
    / "harnesses"
    / "gjq-hardware-optimizers"
    / "resultados"
    / "baihua"
    / "E05_comparacao"
    / "comparacao.json"
)


def _frontmatter() -> dict:
    texto = AGENTE.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", texto, flags=re.S)
    assert match, "frontmatter ausente"
    return yaml.safe_load(match.group(1))


def test_arquivos_existem():
    for caminho in (SPEC, AGENTE, WRAPPER, Path(__file__)):
        assert caminho.exists(), caminho
        assert caminho.stat().st_size > 400, caminho


def test_agente_managed_v1():
    meta = _frontmatter()
    assert meta["agent_id"] == "gjq-readout-mitigation"
    assert meta["version"] == "1.0.0"
    assert meta["type"] == "specialist"
    assert meta["category"] == "engineering"
    assert meta["language"] == "pt-BR"
    assert meta["lifecycle"] == "managed-v1"
    assert meta["parent"] == "marceloclaro"
    assert meta["spec_file"] == "specs/SPEC-935-R1111-gjq-readout-mitigation-agent.md"
    assert meta["test_file"] == "tests/test_r1111_gjq_readout_mitigation_agent.py"
    assert meta["allow_edit"] is True
    assert meta["capabilities"] == {"extendedAgentCard": True}
    assert meta["output_contract"] == {
        "required_fields": ["status", "findings", "evidence", "limitations"],
        "evidence_required": True,
        "external_validation": False,
    }
    assert meta["tools"] == {
        "read": True,
        "glob": True,
        "grep": True,
        "bash": True,
        "edit": True,
        "write": True,
    }


def test_permissao_especifica():
    meta = _frontmatter()
    permission = meta["permission"]
    assert permission["read"] == "allow"
    assert permission["edit"] == "allow"
    assert permission["webfetch"] == "deny"
    assert permission["task"] == "deny"
    bash = permission["bash"]
    assert bash["*"] == "deny"
    assert bash["python3 -m marceloclaro.cli doctor"] == "allow"
    assert bash["python3 -m pytest tests/test_r1111_gjq_readout_mitigation_agent.py -q"] == "allow"
    assert bash[
        ".venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py compare-plan*"
    ] == "allow"
    assert bash[
        ".venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py mitigate*"
    ] == "allow"
    assert not any("runner.py run" in key for key in bash)
    assert not any("runner.py compare" in key for key in bash)


def test_lifecycle_validation():
    from agents.lifecycle import validate_managed_card

    result = validate_managed_card(RAIZ, AGENTE, AGENTE.read_bytes())
    assert result["definition_validated"] is True
    assert result["agent_id"] == "gjq-readout-mitigation"
    assert result["external_validation"] is False


def test_registro_no_opencode():
    cfg = json.loads((RAIZ / "opencode.json").read_text(encoding="utf-8"))
    assert "gjq-readout-mitigation" in cfg["agent"]
    entry = cfg["agent"]["gjq-readout-mitigation"]
    assert entry["prompt"] == "{file:./agents/catalog/gjq-readout-mitigation.md}"
    bash = entry["permission"]["bash"]
    assert bash[
        ".venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py compare-plan*"
    ] == "allow"
    assert bash[
        ".venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py mitigate*"
    ] == "allow"


def _run_wrapper(*args: str, timeout: int = 120):
    return subprocess.run(
        [sys.executable, str(WRAPPER), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=RAIZ,
    )


def test_wrapper_rejeita_run_e_compare():
    for command in ("run", "compare"):
        result = _run_wrapper(
            command,
            "--backend",
            "Baihua",
            "--confirm",
            "--allow-hardware",
        )
        assert result.returncode == 2
        assert "não permitido" in result.stderr


def test_wrapper_plan(tmp_path: Path):
    if not PERFIL.exists():
        pytest.skip("perfil real ausente")
    result = _run_wrapper(
        "compare-plan",
        "--profile",
        str(PERFIL),
        "--circuit",
        "E05",
        "--shots",
        "4096",
        "--quick",
        "--out",
        str(tmp_path),
        timeout=300,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    plan_path = tmp_path / "plano_comparacao.json"
    assert plan_path.exists()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan["hardware_executed"] is False
    assert plan["submissions_estimated"] == 6
    assert plan["plan_sha256"]
    assert "OPENQASM 2.0;" in plan["baseline"]["qasm2"]
    assert "OPENQASM 2.0;" in plan["optimized"]["qasm2"]
    assert set(plan["baseline"]["calibration_qasm2"]) == {"00", "11"}
    assert not (tmp_path / "comparacao.json").exists()
    assert not (tmp_path / "counts.json").exists()


def test_wrapper_mitigate(tmp_path: Path):
    if not (COUNT.exists() and PERFIL.exists() and COMPARACAO.exists()):
        pytest.skip("artefatos reais ausentes")
    comparison = json.loads(COMPARACAO.read_text(encoding="utf-8"))
    matrix = comparison["optimized"]["mitigation"]["matrix"]
    matrix_path = tmp_path / "matriz.json"
    matrix_path.write_text(json.dumps({"matrix": matrix}), encoding="utf-8")
    result = _run_wrapper(
        "mitigate",
        "--counts",
        str(COUNT),
        "--profile",
        str(PERFIL),
        "--qubits",
        "107,106",
        "--matrix",
        str(matrix_path),
        "--shots",
        "4096",
        "--out",
        str(tmp_path / "mit"),
        timeout=120,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    payload = json.loads((tmp_path / "mit" / "mitigacao.json").read_text(encoding="utf-8"))
    assert payload["hardware_executed"] is False
    assert payload["network"] is False
    assert payload["audit"]["ok"] is True
    assert payload["mitigation"]["probabilities"]["00"] == pytest.approx(0.5277305513334)
    assert payload["mitigation"]["probabilities"]["11"] == pytest.approx(0.4722694486666)
    assert payload["mitigation"]["condition_number"] > 1.0
    report = (tmp_path / "mit" / "RELATORIO_MITIGACAO.md").read_text(encoding="utf-8")
    assert "fidelidade de estado" in report
    assert "rx(pi)" in report


def test_sem_segredo():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*['\"][A-Za-z0-9_-]{16,}['\"]"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    for caminho in (SPEC, AGENTE, WRAPPER):
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
        "submissão autônoma de hardware",
    )
    for caminho in (SPEC, AGENTE):
        texto = caminho.read_text(encoding="utf-8").lower()
        for termo in proibidos:
            assert termo not in texto, f"overclaim em {caminho}: {termo}"
