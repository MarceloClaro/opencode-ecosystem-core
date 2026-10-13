"""SPEC-935-R816: argumentos são dados; provas locais não são chamadas LLM."""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import shutil
import time

import pytest

from integrations.opencode_cli import build_config

ROOT = Path(__file__).resolve().parents[1]


def _call(command, arguments="", **extra):
    process = subprocess.run(
        [sys.executable, "-m", "integrations.opencode_commands"],
        input=json.dumps({"command": command, "arguments": arguments, **extra}, ensure_ascii=False),
        capture_output=True, text=True, cwd=ROOT, timeout=90,
    )
    return process, json.loads(process.stdout)


def test_apostrophe_query_reaches_real_reasoning_engine():
    process, report = _call("reason", "a hipótese d'água é válida?")
    assert process.returncode == 0 and report["success"]
    assert report["result"]["engine"]
    assert report["result"]["conclusion"]
    assert report["coordinator"] == "marceloclaro"


@pytest.mark.parametrize("name", ["reason", "maswos", "route", "pypi"])
def test_metacharacters_unicode_quotes_are_data_and_do_not_execute_target(tmp_path, name):
    marker = tmp_path / "unexpected execution"
    text = f"d'água e \"São João\"; $(touch '{marker}'); `touch '{marker}'` & < > | \\\n"
    if name == "pypi":
        # Não consulta serviços externos: a prova desta fronteira não precisa
        # de pesquisa remota e usa a implementação real com índice vazio.
        module = importlib.import_module("integrations.opencode_commands")
        from skills.tooling import pypi_search
        original = pypi_search.search
        pypi_search.search = lambda query, limit: pypi_search.SearchResult(query, 0, [], 0, "hermetic empty index")
        try:
            report = module.execute_request({"command": name, "arguments": text})
        finally:
            pypi_search.search = original
    else:
        process, report = _call(name, text)
        assert process.returncode == 0
    assert report["success"]
    assert report["input"]["arguments"] == text
    assert not marker.exists()


def test_diagnose_reads_apostrophe_unicode_and_space_path_as_inert_text(tmp_path):
    target = tmp_path / 'd\'água "João" com espaços.py'
    target.write_text("raise RuntimeError('NEVER EXECUTE INPUT')\n", encoding="utf-8")
    process, report = _call("diagnose", str(target))
    assert process.returncode == 0 and report["success"]
    assert report["input"]["arguments"] == str(target)
    assert "evolutionary" in report["result"]
    assert "error" not in report["result"].get("reversa", {})


def test_invalid_tdd_target_is_rejected_before_test_process(tmp_path):
    marker = tmp_path / "unexpected"
    process, report = _call("tdd", f"--help; touch {marker}")
    assert process.returncode != 0 and not report["success"]
    assert report["result"]["error"] == "invalid_test_target"
    assert not marker.exists()


def test_tdd_executes_existing_real_test_file():
    process, report = _call("tdd", "tests/test_r233_cli_ecosystem_unification.py")
    assert process.returncode == 0 and report["success"]
    assert report["result"]["all_passed"]
    assert report["result"]["passed_count"] > 0


def test_pypi_json_option_is_separate_from_query(monkeypatch):
    module = importlib.import_module("integrations.opencode_commands")
    from skills.tooling import pypi_search
    captured = {}
    def search(query, limit):
        captured.update(query=query, limit=limit)
        return pypi_search.SearchResult(query, 0, [], 0, "hermetic empty index")
    monkeypatch.setattr(pypi_search, "search", search)
    result = module.execute_request({"command": "pypi", "arguments": "d'água --json"})
    assert captured == {"query": "d'água", "limit": 10}
    assert json.loads(result["result"]["rendered"])["query"] == "d'água"


def test_cli_argv_is_explicit_and_not_shell_interpolation(monkeypatch, tmp_path):
    module = importlib.import_module("integrations.opencode_commands")
    captured = {}
    marker = tmp_path / "unexpected"
    argv = ["run", f"d'água; touch '{marker}'", "--model", "nome com espaços"]
    def run(command, **kwargs):
        captured.update(command=command, kwargs=kwargs)
        return subprocess.CompletedProcess(command, 0, "real boundary fixture", "")
    monkeypatch.setattr(module.subprocess, "run", run)
    result = module.execute_request({"command": "gemini", "arguments": "literal", "argv": argv})
    assert result["success"]
    assert captured["command"] == [sys.executable, "-m", "integrations.gemini_cli", *argv]
    assert captured["kwargs"]["shell"] is False
    assert captured["kwargs"]["timeout"] > 0
    assert not marker.exists()
    with pytest.raises(ValueError):
        module.execute_request({"command": "gemini", "arguments": "unparsed CLI text"})


@pytest.mark.parametrize("payload", [
    {"command": "unknown"}, {"command": "reason", "module": "os"},
    {"command": "reason", "arguments": False},
    {"command": "reason", "argv": ["ignored"]},
    {"command": "gemini", "argv": "run prompt"},
    {"command": "gemini", "argv": [False]},
])
def test_transport_admission_is_fail_closed(payload):
    module = importlib.import_module("integrations.opencode_commands")
    with pytest.raises(ValueError):
        module.execute_request(payload)


def test_custom_tool_is_primary_only_and_every_legacy_name_is_preserved():
    config = build_config()
    assert config["tools"]["core_command"] is False
    assert config["agent"]["marceloclaro"]["tools"]["core_command"] is True
    assert all(agent.get("tools", {}).get("core_command") is not True for name, agent in config["agent"].items() if name != "marceloclaro")
    module = importlib.import_module("integrations.opencode_commands")
    for name in module.COMMAND_NAMES:
        command = config["command"][name]
        assert command["agent"] == "marceloclaro"
        assert "core_command" in command["template"]
        assert "$ARGUMENTS" in command["template"]
        assert "python3 -c" not in command["template"]
        assert "!`" not in command["template"]


def _tool_call(args, *, agent="marceloclaro", env=None, abort_after_ms=None):
    """Carrega a ferramenta TypeScript real; não simula o protocolo do processo."""
    node = shutil.which("node")
    if not node:
        pytest.skip("Node é necessário para a prova da ferramenta OpenCode real.")
    script = """
import {readFileSync} from 'node:fs';
const {default: operation} = await import(process.argv[1]);
const request = JSON.parse(readFileSync(0, 'utf8'));
const controller = new AbortController();
if (request.abort_after_ms) setTimeout(() => controller.abort(), request.abort_after_ms);
const result = await operation.execute(request.args, {agent: request.agent, worktree: process.argv[2], directory: process.argv[2], abort: controller.signal, sessionID:'R816', messageID:'proof'});
console.log(result);
"""
    process = subprocess.run(
        [node, "--experimental-strip-types", "--input-type=module", "-e", script,
         (ROOT / ".opencode/tools/core_command.ts").as_uri(), str(ROOT)],
        input=json.dumps({"args": args, "agent": agent, "abort_after_ms": abort_after_ms}),
        cwd=ROOT, capture_output=True, text=True, timeout=90, env=env,
    )
    assert process.returncode == 0, process.stderr[-1500:]
    return json.loads(process.stdout)


def test_real_custom_tool_transports_tainted_json_without_executing_tokens(tmp_path):
    marker = tmp_path / "inline parser marker"
    text = f"a hipótese d'água !`touch '{marker}'` e $(touch '{marker}') é válida?"
    report = _tool_call({"command": "reason", "arguments": text})
    assert report["success"] and report["result"]["conclusion"]
    assert report["input"]["arguments"] == text
    assert report["process"]["returncode"] == 0
    assert not marker.exists()


def test_real_custom_tool_denies_readonly_agent_before_process():
    report = _tool_call({"command": "models"}, agent="reviewer")
    assert report == {"success": False, "status": "failed", "error": "primary_agent_required"}


def test_real_custom_tool_cli_options_preserve_tainted_argv_without_inference(tmp_path):
    marker = tmp_path / "CLI marker"
    text = f"d'água e \"João\"; touch '{marker}'; $(touch '{marker}')"
    report = _tool_call({"command": "claude-sdk", "argv": ["options", "--prompt", text, "--max-turns", "1"]})
    assert report["success"] and report["result"]["returncode"] == 0
    options = json.loads(report["result"]["stdout"])
    assert options["prompt"] == text and options["max_turns"] == 1
    assert not marker.exists()


@pytest.mark.parametrize("program", [
    "print('invalid JSON')",
    "import sys; print('{\"success\":true}'); sys.exit(1)",
    "print('{\"success\":true}')",
])
def test_real_custom_tool_fails_closed_on_process_result(tmp_path, program):
    executable = tmp_path / "python3"
    executable.write_text("#!/usr/bin/python3\n" + program + "\n")
    executable.chmod(0o700)
    report = _tool_call({"command": "models"}, env={**os.environ, "PATH": str(tmp_path)})
    assert not report["success"] and report["error"] == "invalid_process_result"


def test_real_custom_tool_process_launch_failure_is_not_success(tmp_path):
    report = _tool_call({"command": "models"}, env={**os.environ, "PATH": str(tmp_path)})
    assert not report["success"] and report["error"] == "process_error"


def test_real_custom_tool_cancellation_cleans_process_group(tmp_path):
    executable = tmp_path / "python3"
    pidfile = tmp_path / "child.pid"
    executable.write_text("#!/usr/bin/python3\nimport subprocess,sys,time\nfrom pathlib import Path\n"
                          "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'])\n"
                          f"Path({str(pidfile)!r}).write_text(str(child.pid))\n"
                          "time.sleep(30)\n")
    executable.chmod(0o700)
    report = _tool_call({"command": "models"}, env={**os.environ, "PATH": str(tmp_path)}, abort_after_ms=500)
    assert not report["success"] and report["error"] == "cancelled"
    assert pidfile.exists(), "A prova deve realmente criar o subprocesso antes de cancelar."
    status = Path(f"/proc/{pidfile.read_text()}/status")
    assert not status.exists() or "State:\tZ" in status.read_text(), "Filho não pode continuar executando após cancelamento."


def test_real_custom_tool_finished_helper_cleans_remaining_descendants(tmp_path):
    executable = tmp_path / "python3"
    pidfile = tmp_path / "child.pid"
    executable.write_text("#!/usr/bin/python3\nimport subprocess,sys\nfrom pathlib import Path\n"
                          "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
                          f"Path({str(pidfile)!r}).write_text(str(child.pid))\n"
                          "print('{\"success\":false,\"status\":\"failed\",\"coordinator\":\"marceloclaro\"}')\n"
                          "sys.exit(1)\n")
    executable.chmod(0o700)
    report = _tool_call({"command": "models"}, env={**os.environ, "PATH": str(tmp_path)})
    assert not report["success"] and report["process"]["returncode"] == 1
    status = Path(f"/proc/{pidfile.read_text()}/status")
    for _ in range(20):
        if not status.exists() or "State:\tZ" in status.read_text():
            break
        time.sleep(0.05)
    assert not status.exists() or "State:\tZ" in status.read_text(), "Descendente do helper finalizado não pode permanecer ativo."
