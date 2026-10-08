"""SPEC-935-R640: execução comprovável dos harnesses, sem simular respostas.

Os subprocessos são substituídos nestes testes. Não há chamadas de LLM nem
alterações em aplicações externas; o inventário real é validado separadamente.
"""

import json
import subprocess
from pathlib import Path

import pytest

from integrations.harness_runtime import HarnessRuntime


@pytest.fixture
def runtime(tmp_path, monkeypatch):
    harness = HarnessRuntime(tmp_path)
    monkeypatch.setattr(harness, "_resolve_cli", lambda name: f"/tools/{name}")
    return harness


def completed(output, returncode=0, stderr=""):
    return subprocess.CompletedProcess([], returncode, output, stderr)


def test_status_checks_cli_instead_of_repository_documentation(tmp_path, monkeypatch):
    (tmp_path / "CLAUDE.md").write_text("Documentação", encoding="utf-8")
    (tmp_path / "opencode.json").write_text("{}", encoding="utf-8")
    harness = HarnessRuntime(tmp_path)
    monkeypatch.setattr(harness, "_resolve_cli", lambda name: None)
    state = harness.status()
    assert not state["claude"]["installed"]
    assert not state["codex"]["available"]
    assert not state["chatgpt"]["available"]
    assert state["claude"]["verification"] == "installation_only"


def test_discovery_finds_user_installation_outside_login_path(tmp_path, monkeypatch):
    home = tmp_path / "home"
    binary = home / ".npm-global" / "bin" / "claude"
    binary.parent.mkdir(parents=True)
    binary.write_text("#!/bin/sh\n", encoding="utf-8")
    binary.chmod(0o755)
    monkeypatch.setattr("integrations.harness_runtime.Path.home", lambda: home)
    monkeypatch.setattr("integrations.harness_runtime.shutil.which", lambda name: None)
    harness = HarnessRuntime(tmp_path)
    assert harness.status()["claude"]["path"] == str(binary)


def test_claude_preserves_prompt_and_card_without_hooks(runtime, monkeypatch):
    card = Path(runtime.repo_root) / "agents" / "catalog" / "reviewer.md"
    card.parent.mkdir(parents=True)
    card.write_text("Revisor: critérios específicos", encoding="utf-8")
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return completed(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": "Análise concluída"}))

    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", run)
    result = runtime.execute("claude", "Analise $(id) e `literal`", agent_id="reviewer")
    assert result["success"]
    assert result["output"] == "Análise concluída"
    command, options = calls[0]
    assert command[0] == "/tools/claude"
    assert "--safe-mode" in command
    assert "--permission-mode" in command and "plan" in command
    assert "--tools" in command and "Read,Glob,Grep" in command
    assert "--permission-prompts" in command and "none" in command
    assert "--dangerously-skip-permissions" not in command
    assert options.get("shell", False) is False
    assert "Analise $(id) e `literal`" in options["input"]
    assert "Revisor: critérios específicos" in options["input"]
    assert options["cwd"] == str(runtime.repo_root)


def test_antigravity_uses_supported_print_and_plan_flags(runtime, monkeypatch):
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return completed(json.dumps({"type": "result", "is_error": False, "result": "Parecer real"}))

    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", run)
    result = runtime.execute("antigravity", "Analise o projeto")
    assert result["success"]
    command, options = calls[0]
    assert command[0] == "/tools/agy"
    assert "--print" in command and "run" not in command
    assert "--mode" in command and "plan" in command
    assert "--sandbox" in command
    assert "--dangerously-skip-permissions" not in command


def test_codex_requires_completed_turn_and_final_agent_message(runtime, monkeypatch):
    calls = []
    events = [
        {"type": "thread.started", "thread_id": "x"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "Resultado analisado"}},
        {"type": "turn.completed", "usage": {}},
    ]

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return completed("\n".join(json.dumps(event) for event in events))

    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", run)
    result = runtime.execute("codex", "Explique o roteamento")
    assert result["success"]
    assert result["output"] == "Resultado analisado"
    command, options = calls[0]
    assert command[:2] == ["/tools/codex", "exec"]
    assert "--sandbox" in command and "read-only" in command
    assert "--json" in command and "--ignore-user-config" in command
    assert "--ephemeral" in command and command[-1] == "-"
    assert "Explique o roteamento" in options["input"]


@pytest.mark.parametrize("output", ["", "Resposta simulada", '{"result":""}', '{"is_error":true,"result":"falha"}', '{"result":"pending"}'])
def test_claude_rejects_empty_invalid_error_and_placeholder_output(runtime, monkeypatch, output):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *args, **kwargs: completed(output))
    result = runtime.execute("claude", "Analise")
    assert not result["success"]
    assert result["error"]


def test_codex_does_not_accept_message_without_completed_turn(runtime, monkeypatch):
    message = {"type": "item.completed", "item": {"type": "agent_message", "text": "Texto parcial"}}
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *args, **kwargs: completed(json.dumps(message)))
    assert not runtime.execute("codex", "Analise")["success"]


def test_nonzero_and_secret_stderr_do_not_claim_success(runtime, monkeypatch):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *args, **kwargs: completed('{"result":"parecer"}', 1, "api_key=secret-value token: another-secret"))
    result = runtime.execute("claude", "Analise")
    assert not result["success"]
    assert "secret-value" not in result["error"]
    assert "another-secret" not in result["error"]


def test_timeout_is_bounded_and_returns_failure(runtime, monkeypatch):
    def run(*args, **kwargs):
        assert kwargs["timeout"] == 600
        raise subprocess.TimeoutExpired(args[0], 600, output="secret partial output")

    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", run)
    result = runtime.execute("claude", "Analise", timeout=100000)
    assert not result["success"]
    assert "secret partial output" not in result["error"]


def test_missing_cli_and_chatgpt_are_explicit_failures(runtime, monkeypatch):
    monkeypatch.setattr(runtime, "_resolve_cli", lambda name: None)
    assert not runtime.execute("claude", "Analise")["success"]
    chatgpt = runtime.execute("chatgpt", "Analise")
    assert not chatgpt["success"]
    assert "codex" in chatgpt["error"].lower()


def test_invalid_agent_cannot_escape_catalog(runtime, monkeypatch):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *args, **kwargs: pytest.fail("Não executar caminho inválido"))
    result = runtime.execute("claude", "Analise", agent_id="../../private")
    assert not result["success"]
    assert "agente" in result["error"].lower()


def test_windows_codex_interop_converts_repo_to_unc(runtime, monkeypatch):
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
    monkeypatch.setattr(runtime, "_resolve_cli", lambda name: "/mnt/c/Users/user/AppData/Local/OpenAI/Codex/bin/version/codex.exe")
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return completed('\n'.join([json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "Parecer"}}), json.dumps({"type": "turn.completed"})]))

    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", run)
    result = runtime.execute("codex", "Analise")
    assert result["success"]
    assert result["execution_mode"] == "cli-read-only-windows-interop"
    command = calls[0]
    execution_root = command[command.index("--cd") + 1]
    assert execution_root == "\\\\wsl.localhost\\Ubuntu" + str(runtime.repo_root).replace("/", "\\")


def test_cli_override_does_not_run_shell_text(tmp_path, monkeypatch):
    monkeypatch.setenv("CODEX_BIN", "codex; echo injected")
    monkeypatch.setattr("integrations.harness_runtime.shutil.which", lambda name: "/tools/codex")
    harness = HarnessRuntime(tmp_path)
    assert harness._resolve_cli("codex") is None


def test_chatgpt_never_claims_control_even_with_codex(runtime):
    state = runtime.status()
    assert state["codex"]["available"]
    assert not state["chatgpt"]["available"]
    assert not runtime.execute("chatgpt", "Analise")["success"]


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), "invalid"])
def test_invalid_timeout_never_starts_process(runtime, monkeypatch, timeout):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *args, **kwargs: pytest.fail("Timeout inválido"))
    assert not runtime.execute("claude", "Analise", timeout=timeout)["success"]


def test_remaining_budget_below_one_second_is_respected(runtime, monkeypatch):
    def run(*args, **kwargs):
        assert kwargs["timeout"] == 0.2
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", run)
    assert not runtime.execute("claude", "Analise", timeout=0.2)["success"]


def test_failure_explains_authentication_without_echoing_credentials(runtime, monkeypatch):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *args, **kwargs: completed("", 1, "authentication failed for api_key=super-secret"))
    result = runtime.execute("claude", "Analise")
    assert "autenticação" in result["error"]
    assert "super-secret" not in result["error"]


def test_antigravity_real_json_response_shape_and_active_plan_mode(runtime, monkeypatch):
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return completed(json.dumps({"conversation_id": "example", "status": "SUCCESS", "response": "RUNTIME_PROBE_OK\n", "num_turns": 1}))

    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", run)
    result = runtime.execute("antigravity", "Analise")
    assert result["success"]
    assert result["output"] == "RUNTIME_PROBE_OK"
    assert "--mode" in calls[0] and "plan" in calls[0]
    assert "--disable-slash-commands" not in calls[0]


@pytest.mark.parametrize("status", ["ERROR", "FAILED", "PENDING", "UNKNOWN"])
def test_antigravity_does_not_accept_non_success_status(runtime, monkeypatch, status):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *args, **kwargs: completed(json.dumps({"status": status, "response": "Texto de falha", "result": "Texto de falha"})))
    assert not runtime.execute("antigravity", "Analise")["success"]


def test_claude_credit_error_in_stdout_is_classified_without_echo(runtime, monkeypatch):
    response = {"type": "result", "subtype": "success", "is_error": True, "result": "Credit balance is too low api_key=secret-credit"}
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *args, **kwargs: completed(json.dumps(response), 1))
    result = runtime.execute("claude", "Analise")
    assert not result["success"]
    assert "saldo" in result["error"]
    assert "secret-credit" not in result["error"]


def test_codex_discovery_survives_sanitized_mcp_environment(tmp_path, monkeypatch):
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.delenv("CODEX_BIN", raising=False)
    monkeypatch.setattr("integrations.harness_runtime.shutil.which", lambda name: None)
    monkeypatch.setattr("integrations.harness_runtime.Path.home", lambda: tmp_path / "home")
    binary = tmp_path / "Users" / "user" / "AppData" / "Local" / "OpenAI" / "Codex" / "bin" / "release" / "codex.exe"
    binary.parent.mkdir(parents=True)
    binary.write_text("fixture", encoding="utf-8")
    binary.chmod(0o755)
    users = Path("/mnt/c/Users")
    original_glob = Path.glob
    original_is_dir = Path.is_dir

    def glob(path, pattern):
        if path == users:
            return iter([binary.parent.parent])
        return original_glob(path, pattern)

    monkeypatch.setattr(Path, "glob", glob)
    monkeypatch.setattr(Path, "is_dir", lambda path: True if path == users else original_is_dir(path))
    monkeypatch.setattr(HarnessRuntime, "_is_wsl", staticmethod(lambda: True))
    assert HarnessRuntime(tmp_path).status()["codex"]["path"] == str(binary)


def test_windows_codex_uses_wslpath_when_distro_environment_is_removed(runtime, monkeypatch):
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr("integrations.harness_runtime.shutil.which", lambda name: "/usr/bin/wslpath" if name == "wslpath" else None)
    calls = []
    unc = "\\\\wsl.localhost\\Ubuntu\\home\\user\\repository"

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return completed(unc + "\n")

    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", run)
    assert runtime._execution_root("/mnt/c/Users/user/codex.exe") == unc
    command, kwargs = calls[0]
    assert command == ["/usr/bin/wslpath", "-w", str(runtime.repo_root)]
    assert kwargs["timeout"] == 2
    assert kwargs["shell"] is False


def test_failed_wslpath_does_not_guess_windows_distro(runtime, monkeypatch):
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr("integrations.harness_runtime.shutil.which", lambda name: "/usr/bin/wslpath")
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *args, **kwargs: completed("not a Windows path"))
    with pytest.raises(ValueError, match="WSL"):
        runtime._execution_root("/mnt/c/Users/user/codex.exe")


@pytest.mark.parametrize("response", [{"status": {}, "result": "Parecer"}, {"subtype": [], "result": "Parecer"}])
def test_malformed_json_metadata_returns_failure_instead_of_crashing(runtime, monkeypatch, response):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *args, **kwargs: completed(json.dumps(response)))
    assert not runtime.execute("claude", "Analise")["success"]


def test_none_timeout_returns_failure_instead_of_crashing(runtime, monkeypatch):
    monkeypatch.setattr("integrations.harness_runtime.subprocess.run", lambda *args, **kwargs: pytest.fail("Timeout inválido"))
    assert not runtime.execute("claude", "Analise", timeout=None)["success"]
