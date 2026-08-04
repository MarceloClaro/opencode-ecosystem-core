# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R393: sintaxe real do Antigravity CLI (agy).

``AntigravityBridge.delegate()`` montava ``agy run --agent X --prompt Y``,
mas o binário real (``agy`` v1.1.8) não tem subcomando ``run`` nem flag
``--prompt`` nesse formato — a sintaxe real é ``agy --agent X --print Y
--output-format text``. Confirmado ao vivo: o comando antigo faz o agy
tentar abrir uma sessão de TUI interativa e falhar
(``bubbletea: error opening TTY``) — com ``returncode == 0``, então o
bridge relatava ``status: "completed"`` para uma delegação que não fez
nada de verdade.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from integrations.antigravity.bridge import AntigravityBridge


def _bridge_forced_available() -> AntigravityBridge:
    """Cria um bridge com ``available=True`` sem depender do binário real
    estar instalado no ambiente de CI."""

    bridge = AntigravityBridge()
    bridge.available = True
    return bridge


def test_delegate_invokes_real_agy_flag_syntax_not_the_nonexistent_run_subcommand():
    """CA1: o comando montado usa --agent/--print/--output-format, nunca
    o subcomando 'run' nem a flag '--prompt' (que não existem no agy real)."""

    bridge = _bridge_forced_available()
    completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")
    with mock.patch("subprocess.run", return_value=completed) as run_mock:
        bridge.delegate("faça algo", agent="default", timeout=30)

    command = run_mock.call_args.args[0]
    assert "run" not in command, f"comando não deve usar o subcomando inexistente 'run': {command}"
    assert "--prompt" not in command, f"agy real não aceita --prompt: {command}"
    assert "--agent" in command and "default" in command
    assert "--print" in command and "faça algo" in command
    assert "--output-format" in command


def test_delegate_treats_returncode_zero_cli_error_output_as_failed():
    """CA2: mesmo com returncode 0, uma saída que começa com 'CLI error:'
    (comportamento real observado do agy para erros de TTY/args) deve ser
    reportada como falha, nunca como 'completed'."""

    bridge = _bridge_forced_available()
    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="CLI error: bubbletea: error opening TTY: bubbletea: could not open TTY: open /dev/tty: no such device or address\n",
        stderr="",
    )
    with mock.patch("subprocess.run", return_value=completed):
        result = bridge.delegate("faça algo", agent="default", timeout=30)

    assert result["status"] == "failed", result
    assert "CLI error" in result.get("stdout", "")


def test_delegate_still_reports_completed_for_genuine_success():
    """CA3: a detecção de falha silenciosa não pode gerar falso positivo
    para uma resposta real e bem-sucedida."""

    bridge = _bridge_forced_available()
    completed = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="Olá! Tarefa recebida com sucesso.\n", stderr=""
    )
    with mock.patch("subprocess.run", return_value=completed):
        result = bridge.delegate("faça algo", agent="default", timeout=30)

    assert result["status"] == "completed", result


def test_delegate_still_reports_failed_for_nonzero_returncode():
    """CA4: comportamento pré-existente (returncode != 0 => failed) preservado."""

    bridge = _bridge_forced_available()
    completed = subprocess.CompletedProcess(
        args=[], returncode=1, stdout="", stderr="Error: invalid model selection"
    )
    with mock.patch("subprocess.run", return_value=completed):
        result = bridge.delegate("faça algo", agent="default", timeout=30)

    assert result["status"] == "failed", result


@pytest.mark.skipif(shutil.which("agy") is None, reason="binário agy real não instalado neste ambiente")
def test_delegate_real_agy_binary_completes_a_trivial_prompt():
    """Integração real (pulada se o binário não estiver instalado): confirma
    que a sintaxe corrigida de fato funciona contra o agy real, não só mocks.

    Timeout generoso (90s): o agy chama um backend de modelo real pela rede
    -- medido ao vivo entre ~1s e ~29s de latência real, fora do controle
    deste código. Isso não é flakiness de teste, é o comportamento real de
    uma CLI que depende de rede."""

    bridge = AntigravityBridge()
    assert bridge.available is True
    result = bridge.delegate("responda apenas com a palavra: ok", agent="default", timeout=90)

    assert result["status"] == "completed", result
    assert "CLI error" not in result.get("stdout", "")
