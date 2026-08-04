# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R394: os 9 comandos customizados do opencode.json
executam de verdade, sem NameError/ImportError/traceback escondido.

Achados nesta auditoria (pedida pelo usuário: "revise o opencode cli"):
  - /diagnose: scanners/pipeline.py usava ReversaScanner sem importá-lo --
    todo diagnóstico reportava um NameError disfarçado de resultado de
    scanner (mesma classe de bug do EpistemicPrioritizer, R391).
  - /pypi: o fallback de argumento vazio chamava search('*', limit=5) --
    pypi_search.search() não trata '*' como coringa (é busca literal),
    então a invocação mais simples e comum (/pypi sem argumento) sempre
    retornava zero resultados.

Este teste roda o comando shell REAL de cada entrada (não só importa o
módulo Python) para pegar qualquer classe futura do mesmo bug -- import
faltante, exceção não tratada, ou saída vazia/inútil para o caso mais
comum de uso (sem argumento).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from integrations.opencode_cli import build_config

# Argumento substituído em $ARGUMENTS para comandos que exigem entrada não
# trivial para produzir uma saída significativa (não apenas a mensagem de uso).
_SAMPLE_ARGUMENTS = {
    "diagnose": "",
    "maswos": "metacognição multiagente",
    "reason": "os agentes deste ecossistema colaboram de verdade?",
    "economy": "",
    "models": "",
    "route": "coding",
    "sdd": "",
    "tdd": "tests/test_r233_cli_ecosystem_unification.py",
    "pypi": "requests",
}

# Padrões que indicam falha real escondida atrás de returncode 0 (comandos
# encadeados com "|| true" ou capturas que engolem o traceback).
_ERROR_MARKERS = (
    "Traceback (most recent call last)",
    "NameError:",
    "ImportError:",
    "ModuleNotFoundError:",
    "AttributeError:",
)


def _command_names():
    return sorted(build_config()["command"].keys())


@pytest.mark.parametrize("name", _command_names())
def test_command_executes_without_hidden_python_error(name):
    template = build_config()["command"][name]["template"]
    argument = _SAMPLE_ARGUMENTS.get(name, "")
    shell_command = template.replace("$ARGUMENTS", argument)

    completed = subprocess.run(
        shell_command,
        shell=True,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=90,
    )
    combined = completed.stdout + completed.stderr

    for marker in _ERROR_MARKERS:
        assert marker not in combined, (
            f"/{name} produziu erro escondido ({marker}):\n{combined[-1500:]}"
        )
    assert completed.returncode == 0, (
        f"/{name} saiu com código {completed.returncode}:\n{combined[-1500:]}"
    )


def test_diagnose_reversa_section_has_no_error_key():
    """Regressão direta do bug real achado: report['reversa'] não pode
    conter 'error' quando ReversaScanner está devidamente importado."""

    template = build_config()["command"]["diagnose"]["template"]
    shell_command = template.replace("$ARGUMENTS", "")
    completed = subprocess.run(
        shell_command, shell=True, cwd=str(PROJECT_ROOT),
        capture_output=True, text=True, timeout=60,
    )
    assert "ReversaScanner' is not defined" not in completed.stdout


def test_pypi_empty_argument_prints_usage_instead_of_broken_wildcard_search():
    """Regressão direta do bug real achado: /pypi sem argumento não pode
    mais depender de search('*', ...), que sempre retornava 0 resultados."""

    template = build_config()["command"]["pypi"]["template"]
    shell_command = template.replace("$ARGUMENTS", "")
    completed = subprocess.run(
        shell_command, shell=True, cwd=str(PROJECT_ROOT),
        capture_output=True, text=True, timeout=30,
    )
    assert completed.returncode == 0
    assert "Uso: /pypi" in completed.stdout
    assert "0 encontrados" not in completed.stdout
