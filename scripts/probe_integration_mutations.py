"""R659/R660/R661: injeta três defeitos em processos de teste isolados."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

MUTANTS = {
    "ignore_pre_tool_hooks": ("tests/test_r659_sdk_hooks_contract.py::test_global_matchers_deny", """
from integrations import opencode_agent_sdk as sdk
original = sdk._event_hooks
sdk._event_hooks = lambda hooks, event, *args, **kwargs: ({'allow': True, 'reason': ''} if event == 'PreToolUse' else original(hooks, event, *args, **kwargs))
"""),
    "accept_invalid_mci_arguments": ("tests/test_r660_mcp_validation.py::test_mci_invalid_payload_never_publishes", """
from mci import mcp_server
mcp_server.validate_arguments = lambda name, args, schema=None: {'valid': True, 'errors': [], 'tool': name, 'args': args}
"""),
    "loosen_skill_invocation_policy": ("tests/test_r661_artifact_integration.py::test_emitted_skill_preserves_policy_and_contained_references", """
from dataclasses import replace
from reversa_universal.skill_dispatch import ReversaSkillDispatcher
original = ReversaSkillDispatcher.plan_path
def loose(self, *args, **kwargs):
    return replace(original(self, *args, **kwargs), user_invoked=False, execution_mode='native-or-read')
ReversaSkillDispatcher.plan_path = loose
"""),
}


def main():
    import tempfile
    results = []
    for name, (target, mutation) in MUTANTS.items():
        with tempfile.TemporaryDirectory(prefix="integration-mutant-state-") as state:
            code = ("import os\nos.environ['MCI_STATE_DIR'] = " + repr(state) +
                    "\nos.environ['MCI_AUTOREGISTER'] = '0'\n" + mutation +
                    "\nimport pytest\nraise SystemExit(pytest.main(['-q', '--tb=short', " + repr(target) + "]))")
            proc = subprocess.run([sys.executable, "-c", code], cwd=ROOT,
                                  capture_output=True, text=True, timeout=90)
            output = proc.stdout + proc.stderr
            contract_failure = "AssertionError" in output or "KeyError: 'isError'" in output
            detected = proc.returncode == 1 and contract_failure and "failed" in output
            results.append({"mutation": name, "target": target, "detected": detected,
                            "returncode": proc.returncode, "contract_failure": contract_failure,
                            "output": output})
    report = {"ts": datetime.now(timezone.utc).isoformat(),
              "evidence_kind": "fault_injection_contract_tests_not_live_inference",
              "production_files_modified": False, "success": all(r["detected"] for r in results),
              "results": results}
    path = ROOT / "docs/evidence/R659_R662_MUTATIONS.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"success": report["success"], "mutants_detected": sum(r["detected"] for r in results)}))
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
