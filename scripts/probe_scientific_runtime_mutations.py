"""Contraprovas R667–R671 em memória; não modifica fontes do checkout."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MUTANTS = [
    {"id": "health_as_inference", "module": "integrations.live_scientific_runtime", "class": None,
     "method": "classify_execution", "old": "returncode == 0 and generated and artifact", "new": "returncode == 0 and artifact",
     "test": "tests/test_r667_live_scientific_runtime.py::test_process_exit_and_health_are_insufficient"},
    {"id": "altered_source_as_original", "module": "integrations.dataset_cli", "class": "DatasetCliIntegration",
     "method": "build_custom", "old": 'if _digest(raw) != original["sha256"]:', "new": "if False:",
     "test": "tests/test_r668_dataset_cli.py::test_custom_rejects_modified_source"},
    {"id": "foreign_tool_receipt", "module": "integrations.scientific_plugins", "class": "ScientificPluginService",
     "method": "accept_host_response", "old": 'host_tool != request["host_tool"]', "new": "False",
     "test": "tests/test_r670_scientific_plugins.py::test_receipt_identity_replay_and_failure"},
    {"id": "mutable_plugin_bytecode", "module": "integrations.scientific_plugins", "class": "ScientificPluginService",
     "method": "run_local", "old": '[sys.executable, "-B", str(executable)]', "new": "[sys.executable, str(executable)]",
     "test": "tests/test_r670_scientific_plugins.py::test_local_python_skill_cannot_write_bytecode_into_imported_package"},
]
CHILD = '''
import importlib,inspect,json,sys
c=json.loads(sys.argv[1]); m=importlib.import_module(c['module']); owner=getattr(m,c['class']) if c['class'] else m
fn=getattr(owner,c['method']); source=inspect.getsource(fn)
indent=len(source.splitlines()[0])-len(source.splitlines()[0].lstrip())
source='\\n'.join(line[indent:] if line.startswith(' '*indent) else line for line in source.splitlines())
if c['old'] not in source: raise RuntimeError('mutation needle absent')
namespace=dict(fn.__globals__); exec(compile(source.replace(c['old'],c['new'],1),inspect.getfile(fn),'exec'),namespace)
setattr(owner,c['method'],namespace[c['method']])
import pytest
raise SystemExit(pytest.main([c['test'],'-q','--tb=short']))
'''


def main():
    directory = ROOT / "docs/evidence/R667_R671_MUTATION_LOGS"
    directory.mkdir(exist_ok=True)
    results = []
    for mutant in MUTANTS:
        with tempfile.TemporaryDirectory(prefix="r671-mutant-") as state:
            env = {**os.environ, "MCI_STATE_DIR": state, "EVOLUTION_STATE_PATH": str(Path(state) / "cycles.json")}
            run = subprocess.run([sys.executable, "-c", CHILD, json.dumps(mutant)],
                                 env=env, cwd=ROOT, capture_output=True, text=True, timeout=60)
        path = directory / (mutant["id"] + ".txt")
        path.write_text(run.stdout + run.stderr, encoding="utf-8")
        results.append({**mutant, "exit_code": run.returncode, "detected": run.returncode == 1 and "FAILED" in run.stdout,
                        "log": str(path), "log_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    result = {"success": all(r["detected"] for r in results), "mutants": results,
              "external_validation": False, "scope": "Isolated counterexamples; actual external runs are separate."}
    path = ROOT / "docs/evidence/R667_R671_MUTATIONS.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"success": result["success"], "detected": sum(r["detected"] for r in results), "path": str(path)}))
    if not result["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
