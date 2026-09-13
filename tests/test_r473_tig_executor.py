"""Testes RED/GREEN da SPEC-935-R473 — Executor alternativo multi-provedor (tig), M7 da R471.

Suíte hermética: nenhuma chamada real a subprocess, rede ou LLM. O runner é
injetado no TigExecutor; as invocações são verificadas via mocks.
"""
import hashlib
import importlib
import pathlib

import pytest

from agent_runners.tig_executor import (
    ALLOWED_PROVIDERS,
    DEFAULT_PROVIDER_FALLBACK,
    MODES,
    TigExecutionReceipt,
    TigExecutor,
)


class _FakeProc:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _runner_ok(*, returncode=0, tracer=None):
    """Runner injetável que devolve sucesso e grava os kwargs de cada chamada."""
    def runner(cmd, **kwargs):
        if tracer is not None:
            tracer.append((cmd, kwargs))
        return _FakeProc(returncode)
    return runner


def _make_executor(runner=None, bin_path="/usr/bin/tig", allowlist=None):
    return TigExecutor(
        bin_path=bin_path,
        allowlist=allowlist,
        runner=runner or _runner_ok(),
    )


class TestDisponibilidade:
    def test_binario_ausente_nao_disponivel_e_nao_executa(self):
        ex = TigExecutor(bin_path="", runner=_runner_ok())
        assert ex.available() is False
        receipt = ex.run(task="pesquisa", mode="architect")
        assert receipt.success is False
        assert receipt.provider is None
        assert receipt.exit_code is None

    def test_executor_disponivel_com_binario(self):
        ex = _make_executor(bin_path="/usr/bin/tig")
        assert ex.available() is True


class TestInvocacaoSemShell:
    def test_modo_architect_invoca_sem_shell_confirma_args(self):
        tracer = []
        ex = _make_executor(bin_path="/usr/bin/tig", runner=_runner_ok(tracer=tracer))
        receipt = ex.run(task="planejar estudo", mode="architect",
                         provider_fallback=["ollama"])
        assert receipt.success is True
        assert receipt.provider == "ollama"
        assert len(tracer) == 1
        cmd, kwargs = tracer[0]
        assert cmd == ["/usr/bin/tig", "--mode", "architect", "--provider", "ollama"]
        assert kwargs.get("shell") is False
        assert kwargs.get("input") == "planejar estudo".encode("utf-8")
        assert kwargs.get("timeout") is not None

    def test_modo_code_invoca_mode_code(self):
        tracer = []
        ex = _make_executor(runner=_runner_ok(tracer=tracer))
        receipt = ex.run(task="implementar módulo", mode="code",
                         provider_fallback=["deepseek"])
        assert receipt.success is True
        assert tracer[0][0] == ["/usr/bin/tig", "--mode", "code", "--provider", "deepseek"]


class TestFallback:
    def test_fallback_para_proximo_provedor_quando_primario_falha(self):
        tracer = []

        def runner(cmd, **kwargs):
            tracer.append(cmd)
            provider = cmd[-1]
            return _FakeProc(0 if provider == "deepseek" else 1)

        ex = _make_executor(runner=runner)
        receipt = ex.run(task="x", mode="code",
                         provider_fallback=["ollama", "deepseek"])
        assert receipt.success is True
        assert receipt.provider == "deepseek"
        assert receipt.attempted_providers == ["ollama", "deepseek"]
        assert len(tracer) == 2

    def test_todos_provedores_falham_retorna_recibo_insucesso(self):
        tracer = []
        ex = _make_executor(runner=_runner_ok(returncode=2, tracer=tracer))
        receipt = ex.run(task="x", mode="code",
                         provider_fallback=["ollama", "groq"])
        assert receipt.success is False
        assert receipt.attempted_providers == ["ollama", "groq"]
        assert receipt.exit_code == 2
        assert len(tracer) == 2

    def test_timeout_controlado_prossegue_para_proximo_provedor(self):
        import subprocess
        tracer = []

        def runner(cmd, **kwargs):
            tracer.append(cmd)
            provider = cmd[-1]
            if provider == "ollama":
                raise subprocess.TimeoutExpired(cmd=cmd, timeout=1)
            return _FakeProc(0)

        ex = _make_executor(runner=runner)
        receipt = ex.run(task="x", mode="code",
                         provider_fallback=["ollama", "gemini"])
        assert receipt.success is True
        assert receipt.provider == "gemini"
        assert len(tracer) == 2

    def test_timeout_total_registra_motivo(self):
        import subprocess

        def runner(cmd, **kwargs):
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=1)

        ex = _make_executor(runner=runner)
        receipt = ex.run(task="x", mode="code",
                         provider_fallback=["ollama", "openai"])
        assert receipt.success is False
        assert "timeout" in receipt.reason.lower()


class TestFailClosed:
    def test_provedor_fora_da_allowlist_bloqueado_sem_chamada(self):
        tracer = []
        ex = _make_executor(runner=_runner_ok(tracer=tracer))
        receipt = ex.run(task="x", mode="code",
                         provider_fallback=["provedor-malicioso"])
        assert receipt.success is False
        assert receipt.provider is None
        assert tracer == []

    def test_allowlist_vazia_fail_closed(self):
        tracer = []
        ex = _make_executor(runner=_runner_ok(tracer=tracer), allowlist=set())
        receipt = ex.run(task="x", mode="architect",
                         provider_fallback=["ollama"])
        assert receipt.success is False
        assert receipt.provider is None
        assert tracer == []

    def test_modo_desconhecido_negado_sem_chamada(self):
        tracer = []
        ex = _make_executor(runner=_runner_ok(tracer=tracer))
        receipt = ex.run(task="x", mode="hack", provider_fallback=["ollama"])
        assert receipt.success is False
        assert tracer == []

    def test_task_vazia_negada_sem_chamada(self):
        tracer = []
        ex = _make_executor(runner=_runner_ok(tracer=tracer))
        receipt = ex.run(task="", mode="architect", provider_fallback=["ollama"])
        assert receipt.success is False
        assert tracer == []


class TestReceipt:
    def test_task_sha256_deterministico_no_recibo(self):
        ex = _make_executor()
        receipt = ex.run(task="pesquisa replicável", mode="architect",
                         provider_fallback=["ollama"])
        target = hashlib.sha256("pesquisa replicável".encode("utf-8")).hexdigest()
        assert receipt.task_sha256 == target

    def test_recibo_carrega_orquestrador_e_timestamp(self):
        ex = _make_executor()
        receipt = ex.run(task="x", mode="architect", provider_fallback=["ollama"])
        assert receipt.orchestrator == "marceloclaro"
        assert receipt.invoked_at_utc  # não vazio
        assert receipt.bin_path == "/usr/bin/tig"

    def test_recibo_nao_declara_merito_qualitativo(self):
        """Anti-overclaim (CA7): o recibo apenas reporta exit_code/success; não
        proclama qualidade, verificação ou mérito de topo."""
        ex = _make_executor()
        receipt = ex.run(task="x", mode="architect", provider_fallback=["ollama"])
        payload = " ".join(f"{k}={v}" for k, v in receipt.to_dict().items()).lower()
        for banned in ("superhuman", "verificado", "qualis a1", "superação"):
            assert banned not in payload


class TestDoctorIntegracao:
    def test_tig_registrado_no_doctor_external_clis(self):
        from marceloclaro.doctor import EXTERNAL_CLIS
        assert "tig" in EXTERNAL_CLIS
        assert "pip install tig-code" in EXTERNAL_CLIS["tig"]

    def test_check_external_clis_nao_falha_com_tig_ausente(self, monkeypatch):
        import shutil as shutil_mod
        from marceloclaro import doctor as doctor_module
        monkeypatch.setattr(shutil_mod, "which", lambda name: None)
        check = doctor_module._check_external_clis()
        assert check.status == "warn"
        assert "tig" in check.detail


class TestHigieneEstatica:
    def test_modulo_sem_shell_true_sem_segredos_sem_rede(self):
        source = pathlib.Path(importlib.util.find_spec(
            "agent_runners.tig_executor").origin).read_text(encoding="utf-8")
        assert "shell=True" not in source
        assert "requests.get(" not in source
        assert "urlopen(" not in source
        for banned in ("api_key", "password", "token"):
            assert banned not in source

    def test_constantes_de_contrato(self):
        assert MODES == {"architect", "code"}
        assert DEFAULT_PROVIDER_FALLBACK[0] == "ollama"
        assert {"ollama", "deepseek", "groq", "gemini", "openai"} <= ALLOWED_PROVIDERS

    def test_status_consumivel_pelo_doctor(self):
        ex = _make_executor(bin_path="/usr/bin/tig")
        status = ex.status()
        assert status["name"] == "tig"
        assert status["available"] is True
        assert "providers" in status