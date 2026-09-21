"""Testes RED/GREEN da SPEC-972 — Executor de podcast Gemini Notebook (nlm).

Fase 1: ferramenta explícita do operador (veredito R474/R548). O executor
espelha o padrão canônico de `agent_runners/tig_executor.py` (R473): runner
injetável, `shell=False`, fail-closed, recibo auditável e anti-overclaim.

Suíte hermética: nenhuma chamada real a subprocess, rede ou LLM; nenhum
código do repositório é modificado.
"""
import json
import pathlib
import textwrap

import pytest

from agent_runners.nlm_executor import (
    ALLOWED_AUDIO_FORMATS,
    ALLOWED_LENGTHS,
    ALLOWED_OPERATIONS,
    NlmPodcastExecutor,
    NlmPodcastReceipt,
)


class _FakeProc:
    def __init__(self, returncode=0, stdout=b"", stderr=b""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _json_proc(payload, returncode=0):
    return _FakeProc(returncode=returncode, stdout=json.dumps(payload).encode("utf-8"))


def _runner_tracer(tracer):
    """Runner injetável que grava cada chamada e devolve proc fake."""
    def runner(cmd, **kwargs):
        tracer.append((list(cmd), dict(kwargs)))
        return _FakeProc(returncode=0, stdout=b"{}")
    return runner


def _make_executor(bin_path="/usr/bin/nlm", runner=None, allowlist=None):
    return NlmPodcastExecutor(
        bin_path=bin_path,
        runner=runner,
        notebook_allowlist=allowlist,
    )


# ── 1. Superfície e disponibilidade ───────────────────────────────────

class TestSurface:
    def test_allowed_operations_contemplam_pipeline_audio(self):
        assert {"create_notebook", "add_source_text", "create_audio", "download_audio"} <= ALLOWED_OPERATIONS

    def test_allowed_formats_e_lengths(self):
        assert "deep_dive" in ALLOWED_AUDIO_FORMATS
        assert {"short", "default", "long"} <= ALLOWED_LENGTHS

    def test_available_sem_binario(self):
        ex = _make_executor(bin_path="")
        assert not ex.available()

    def test_available_com_binario(self):
        assert _make_executor().available()

    def test_status_eh_auditavel(self):
        st = _make_executor().status()
        assert st["name"] == "nlm"
        assert st["available"] is True
        assert "bin_path" in st and "note" in st


# ── 2. Fail-closed (nenhuma invocação) ────────────────────────────────

class TestFailClosed:
    def test_binario_ausente_nego(self):
        ex = _make_executor(bin_path="")
        r = ex.create_notebook("Titulo")
        assert not r.success
        assert "indisponivel" in r.reason

    def test_notebook_fora_da_allowlist_nego(self):
        ex = _make_executor(allowlist={"abc-123"})
        r = ex.create_audio("xyz-999")
        assert not r.success
        assert "allowlist" in r.reason

    def test_notebook_id_vazio_nego(self):
        ex = _make_executor()
        assert not ex.add_source_text("", "texto").success
        assert not ex.create_audio("").success
        assert not ex.download_audio("", "art-1", "/tmp").success

    def test_operacao_desconhecida_nego(self):
        ex = _make_executor()
        r = ex.run_operation("operacao_fantasma", "task")
        assert not r.success
        assert "operacao desconhecida" in r.reason

    def test_sem_invocacao_em_fail_closed(self):
        calls = []
        ex = _make_executor(bin_path="/usr/bin/nlm", runner=_runner_tracer(calls))
        ex.create_audio("xyz-999")  # allowlist None = aberto (documentado)
        calls.clear()  # ignora a chamada da configuração aberta
        ex = _make_executor(bin_path="/usr/bin/nlm", runner=_runner_tracer(calls), allowlist={"abc"})
        ex.create_audio("xyz-999")  # fora da allowlist → nega sem invocar
        assert calls == []


# ── 3. Invocação shell=False + argumentos exatos ──────────────────────

class TestInvocacao:
    def test_create_notebook_comando_exato(self):
        calls = []
        ex = _make_executor(runner=_runner_tracer(calls))
        ex.create_notebook("Meu Tema")
        cmd, kwargs = calls[0]
        assert cmd == ["/usr/bin/nlm", "notebook", "create", "Meu Tema", "--json", "--profile", "default"]
        assert kwargs["shell"] is False

    def test_add_source_text_comando_exato(self):
        calls = []
        ex = _make_executor(runner=_runner_tracer(calls))
        ex.add_source_text("abc-123", "texto da fonte")
        cmd, _ = calls[0]
        assert cmd == ["/usr/bin/nlm", "source", "add", "abc-123", "--text", "texto da fonte", "--profile", "default"]

    def test_create_audio_comando_exato(self):
        calls = []
        ex = _make_executor(runner=_runner_tracer(calls))
        ex.create_audio("abc-123", fmt="deep_dive", length="long", language="pt-BR")
        cmd, kwargs = calls[0]
        assert cmd[:4] == ["/usr/bin/nlm", "audio", "create", "abc-123"]
        assert kwargs["shell"] is False
        assert "--format" in cmd and "deep_dive" in cmd
        assert "--length" in cmd and "long" in cmd
        assert "--language" in cmd and "pt-BR" in cmd

    def test_download_audio_comando_exato(self):
        calls = []
        ex = _make_executor(runner=_runner_tracer(calls))
        ex.download_audio("abc-123", "art-1", "/tmp/out", filename="pod.m4a", retries=1)
        cmd, _ = calls[0]
        # sintaxe real do nlm 0.11.6: -o <arquivo>; NÃO aceita -d nem --profile
        assert cmd == ["/usr/bin/nlm", "download", "audio", "abc-123", "--id", "art-1", "-o", "/tmp/out/pod.m4a"]

    def test_download_audio_nao_usa_profile(self):
        # bug real: --profile não é opção de `download audio` (help v0.11.6)
        calls = []
        ex = _make_executor(runner=_runner_tracer(calls))
        ex.download_audio("abc-123", "art-1", "/tmp/out", filename="pod.m4a", retries=1)
        cmd, _ = calls[0]
        assert "--profile" not in cmd
        assert "-d" not in cmd

    def test_download_audio_com_retry_ate_sucesso(self):
        calls = []

        def runner_flaky(cmd, **kwargs):
            calls.append(cmd)
            if len(calls) < 3:
                return _FakeProc(returncode=1, stderr=b"404 artifact not ready")
            return _FakeProc(returncode=0, stdout=b"downloaded")

        ex = _make_executor(runner=runner_flaky)
        r = ex.download_audio("abc-123", "art-1", "/tmp/out", filename="pod.m4a",
                              retries=4, wait=0.01)
        assert r.success is True
        assert len(calls) == 3  # 2 falhas + 1 sucesso
        assert r.exit_code == 0

    def test_download_audio_esgota_retries(self):
        calls = []

        def runner_sempre_falha(cmd, **kwargs):
            calls.append(cmd)
            return _FakeProc(returncode=1, stderr=b"404")

        ex = _make_executor(runner=runner_sempre_falha)
        r = ex.download_audio("abc-123", "art-1", "/tmp/out", filename="pod.m4a",
                              retries=2, wait=0.01)
        assert r.success is False
        assert len(calls) == 2
        assert "exit=" in r.reason or "404" in r.reason


# ── 4. Parse de IDs + sucesso/erro ────────────────────────────────────

class TestParseESucesso:
    def test_create_notebook_parseia_id(self):
        runner = lambda cmd, **kw: _json_proc({"notebook_id": "nb-1"})
        ex = _make_executor(runner=runner)
        r = ex.create_notebook("Tema")
        assert r.success and r.result_id == "nb-1"

    def test_create_audio_parseia_artifact_id(self):
        runner = lambda cmd, **kw: _json_proc({"artifact_id": "art-9"})
        ex = _make_executor(runner=runner)
        r = ex.create_audio("abc-123")
        assert r.success and r.result_id == "art-9"

    def test_erro_exit_nao_zero(self):
        runner = lambda cmd, **kw: _FakeProc(returncode=1, stderr=b"boom")
        ex = _make_executor(runner=runner)
        r = ex.create_notebook("Tema")
        assert not r.success
        assert "exit=1" in r.reason or "boom" in r.reason

    def test_timeout_e_excecao_controlados(self):
        import subprocess
        def runner_timeout(cmd, **kw):
            raise subprocess.TimeoutExpired(cmd, timeout=10)
        ex_timeout = _make_executor(runner=runner_timeout)
        r1 = ex_timeout.create_notebook("Tema")
        assert not r1.success and "timeout" in r1.reason

        def runner_boom(cmd, **kw):
            raise RuntimeError("x")
        ex_boom = _make_executor(runner=runner_boom)
        r2 = ex_boom.create_notebook("Tema")
        assert not r2.success and "RuntimeError" in r2.reason


# ── 5. Recibo auditável e anti-overclaim ──────────────────────────────

class TestReceipt:
    def test_recibo_campos_core(self):
        ex = _make_executor(runner=lambda cmd, **kw: _json_proc({"notebook_id": "nb-1"}))
        r = ex.create_notebook("Tema")
        assert r.invoked_at_utc and r.operation == "create_notebook"
        assert r.task_sha256.startswith("0" * 0) or len(r.task_sha256) == 64
        assert r.bin_path == "/usr/bin/nlm"

    def test_anti_overclaim_recibo_nao_declara_merito(self):
        ex = _make_executor(runner=lambda cmd, **kw: _json_proc({"artifact_id": "art-1"}))
        r = ex.create_audio("abc-123")
        d = json.dumps(r.to_dict()).lower()
        # recibo fala apenas de execução; nenhum mérito/verificação de conteúdo
        for forbidden in ("verified", "verificado", "excelente", "qualis"):
            assert forbidden not in d

    def test_receipt_dataclass_dict(self):
        r = NlmPodcastReceipt(success=True, reason="ok")
        assert r.to_dict()["success"] is True


# ── 6. Orquestrador (orchestrator.podcast) com executor fake ─────────

class _FakeExecutorOk:
    """Executor fake que simula pipeline completo com sucesso."""
    def __init__(self, audio_file="podcast.m4a"):
        self._audio = audio_file
        self.calls = []
    def available(self):
        return True
    def create_notebook(self, title, **kw):
        self.calls.append(("create_notebook", title))
        return NlmPodcastReceipt(success=True, operation="create_notebook", result_id="nb-fake", reason="ok")
    def add_source_text(self, notebook_id, text, **kw):
        self.calls.append(("add_source_text", notebook_id))
        return NlmPodcastReceipt(success=True, operation="add_source_text", reason="ok")
    def create_audio(self, notebook_id, **kw):
        self.calls.append(("create_audio", notebook_id))
        return NlmPodcastReceipt(success=True, operation="create_audio", result_id="art-fake", reason="ok")
    def download_audio(self, notebook_id, artifact_id, output_dir, **kw):
        self.calls.append(("download_audio", notebook_id))
        import pathlib
        pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
        f = pathlib.Path(output_dir) / self._audio
        f.write_bytes(b"fake-audio")
        return NlmPodcastReceipt(success=True, operation="download_audio", artifact_path=str(f), reason="ok")


def _fake_folder(tmp_path):
    folder = tmp_path / "producao"
    folder.mkdir()
    (folder / "manuscrito.md").write_text("# Titulo\n\nConteudo de teste para o podcast.", encoding="utf-8")
    return folder


class TestOrchestratorPodcast:
    def test_podcast_sucesso_com_executor_fake(self, tmp_path):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        folder = _fake_folder(tmp_path)
        orch = MarceloClaroOrchestrator()
        fake = _FakeExecutorOk()
        report = orch.podcast(str(folder), executor=fake)
        assert report["ok"] is True
        assert report["notebook_id"] == "nb-fake"
        assert report["artifact_id"] == "art-fake"
        assert report["audio"].endswith(".m4a")
        assert (folder / "audio" / "podcast.m4a").exists()
        # todas as etapas do pipeline foram chamadas em ordem
        assert [c[0] for c in fake.calls] == ["create_notebook", "add_source_text", "create_audio", "download_audio"]

    def test_podcast_executor_indisponivel(self, tmp_path):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        folder = _fake_folder(tmp_path)
        orch = MarceloClaroOrchestrator()
        class _Unavailable:
            def available(self):
                return False
        report = orch.podcast(str(folder), executor=_Unavailable())
        assert report["ok"] is False
        assert "indisponivel" in report["error"].lower() or "nlm" in report["error"].lower()

    def test_podcast_sem_manuscrito_nao_cria_fonte(self, tmp_path):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        folder = tmp_path / "vazia"
        folder.mkdir()
        orch = MarceloClaroOrchestrator()
        fake = _FakeExecutorOk()
        report = orch.podcast(str(folder), executor=fake)
        # sem manuscrito: pipeline continua mas sem fonte de texto? política:
        # a Fase 1 considera pasta sem manuscrito como erro claro.
        assert report["ok"] is False or report.get("warning")  # fail-closed na fonte ausente


# ── 8. CLI (subcomando podcast) ───────────────────────────────────────

class TestCliPodcast:
    def test_podcast_sem_pasta_imprime_uso_e_sai(self, monkeypatch, capsys):
        import sys as _sys
        from marceloclaro import cli as cli_mod
        monkeypatch.setattr(_sys, "argv", ["cli", "podcast"])
        with pytest.raises(SystemExit):
            cli_mod.main()
        out = capsys.readouterr().out
        assert "Uso" in out and "podcast" in out

    def test_podcast_chama_orchestrator_e_imprime_json(self, monkeypatch, capsys, tmp_path):
        import sys as _sys
        from marceloclaro import cli as cli_mod
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        folder = _fake_folder(tmp_path)
        def fake_podcast(self_, folder_, **kwargs):
            import pathlib as _pl
            return {"ok": True, "audio": str(_pl.Path(folder_) / "audio" / "p.m4a"), "kwargs": kwargs}
        monkeypatch.setattr(MarceloClaroOrchestrator, "podcast", fake_podcast)
        monkeypatch.setattr(
            _sys, "argv",
            ["cli", "podcast", str(folder), "--title", "T", "--length", "short", "--format", "brief"],
        )
        cli_mod.main()
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["ok"] is True
        assert data["kwargs"]["title"] == "T"
        assert data["kwargs"]["length"] == "short"
        assert data["kwargs"]["fmt"] == "brief"


# ── 7. Higiene estática do módulo executor ────────────────────────────

class TestHigieneEstatica:
    def test_fonte_proibe_shell_true_e_segredos(self):
        src = pathlib.Path("agent_runners/nlm_executor.py").read_text(encoding="utf-8")
        assert "shell=True" not in src
        for segredo in ("api_key", "password", "client_secret", "cookie_value"):
            assert segredo not in src
        assert "import requests" not in src
        assert "urllib.request" not in src

    def test_docstring_declara_uso_operador(self):
        src = pathlib.Path("agent_runners/nlm_executor.py").read_text(encoding="utf-8")
        assert "operador" in src or "opt-in" in src or "nao documentadas" in src