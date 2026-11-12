"""R1107 - testes do OpenCodeCliAdapter com executável falso e isolamento."""
from __future__ import annotations

import json
import os
import stat

from benchmarks.autonomy_harness import evaluate, load_tasks
from benchmarks.opencode_cli_adapter import OpenCodeCliAdapter


def make_fake_cli(tmp_path, capture_path):
    script = tmp_path / "fake_opencode.py"
    script.write_text(
        """#!/usr/bin/env python3
import json, os, sys, time
capture = os.environ.get("FAKE_CAPTURE")
if capture:
    with open(capture, "w", encoding="utf-8") as handle:
        json.dump({
            "argv": sys.argv,
            "permission": os.environ.get("OPENCODE_PERMISSION"),
            "config": os.environ.get("OPENCODE_CONFIG"),
            "cwd": os.getcwd(),
        }, handle)
mode = os.environ.get("FAKE_MODE", "ok")
if mode == "ok":
    print(json.dumps({"action": "answer", "answer": "supported", "confidence": 0.8, "citations": ["e1"]}))
elif mode == "usage":
    print("Free usage limit reached", file=sys.stderr)
    raise SystemExit(1)
elif mode == "auth":
    print("authentication required: 401 Unauthorized", file=sys.stderr)
    raise SystemExit(1)
elif mode == "generic":
    print("boom", file=sys.stderr)
    raise SystemExit(2)
elif mode == "sleep":
    time.sleep(2)
    print("{}")
elif mode == "invalid":
    print("not json")
elif mode == "missing":
    print(json.dumps({"action": "answer", "confidence": 0.9}))
""",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def make_adapter(tmp_path, capture_path, mode="ok", timeout=5):
    (tmp_path / "opencode.json").write_text("{}", encoding="utf-8")
    return OpenCodeCliAdapter(
        command=str(make_fake_cli(tmp_path, capture_path)),
        project_dir=tmp_path,
        agent="sandboxed-responder",
        model="opencode/test",
        timeout=timeout,
        env={"FAKE_MODE": mode, "FAKE_CAPTURE": str(capture_path)},
    )


def test_success_parses_json_and_applies_isolation(tmp_path):
    capture = tmp_path / "capture.json"
    adapter = make_adapter(tmp_path, capture)
    task = load_tasks()[0]

    response = adapter.run(task.public_view(), 1)

    assert response.action == "answer"
    assert response.answer == task.expected_answer
    assert response.confidence == 0.8
    assert response.citations == ("e1",)
    assert response.cost is None
    assert response.unauthorized_actions == 0
    assert response.error_type is None

    recorded = json.loads(capture.read_text(encoding="utf-8"))
    argv = recorded["argv"]
    assert "--pure" in argv
    assert "--agent" in argv and "sandboxed-responder" in argv
    assert "--dir" in argv and str(tmp_path) in argv
    assert "--model" in argv and "opencode/test" in argv
    assert "--auto" not in argv
    assert recorded["permission"] == '{"*":"deny"}'
    assert recorded["config"] == str(tmp_path / "opencode.json")
    prompt = argv[-1]
    assert task.prompt in prompt
    assert "expected_action" not in prompt
    assert "expected_answer" not in prompt
    assert "required_citations" not in prompt


def test_provider_limit_is_classified_without_fake_answer(tmp_path):
    response = make_adapter(tmp_path, tmp_path / "c.json", mode="usage").run(load_tasks()[0].public_view(), 1)

    assert response.action == "abstain"
    assert response.error_type == "provider_limit"
    assert "usage limit" in response.reason.lower()


def test_auth_error_is_classified(tmp_path):
    response = make_adapter(tmp_path, tmp_path / "c.json", mode="auth").run(load_tasks()[0].public_view(), 1)

    assert response.action == "abstain"
    assert response.error_type == "auth_error"


def test_timeout_is_classified(tmp_path):
    response = make_adapter(tmp_path, tmp_path / "c.json", mode="sleep", timeout=0.2).run(
        load_tasks()[0].public_view(), 1
    )

    assert response.action == "abstain"
    assert response.error_type == "timeout"
    assert response.latency_seconds >= 0.2


def test_invalid_json_and_missing_answer_are_fail_closed(tmp_path):
    invalid = make_adapter(tmp_path, tmp_path / "c1.json", mode="invalid").run(
        load_tasks()[0].public_view(), 1
    )
    missing = make_adapter(tmp_path, tmp_path / "c2.json", mode="missing").run(
        load_tasks()[0].public_view(), 1
    )

    assert invalid.action == "abstain"
    assert invalid.error_type == "invalid_json"
    assert missing.action == "abstain"
    assert missing.error_type == "missing_answer"


def test_generic_nonzero_exit_is_fail_closed(tmp_path):
    response = make_adapter(tmp_path, tmp_path / "c.json", mode="generic").run(
        load_tasks()[0].public_view(), 1
    )

    assert response.action == "abstain"
    assert response.error_type == "nonzero_exit"
    assert "boom" in response.reason


def test_harness_does_not_invent_cost_for_opencode_cli(tmp_path):
    adapter = make_adapter(tmp_path, tmp_path / "c.json")
    task = load_tasks()[0]
    report = evaluate(adapter, [task], attempts=1)

    assert report["task_correctness"] == 1.0
    assert report["cost_complete"] is False
    assert report["cost_attempts_known"] == 0
    assert report["cost_per_correct_task"] is None
    assert report["adapter_kind"] == "opencode_cli"
