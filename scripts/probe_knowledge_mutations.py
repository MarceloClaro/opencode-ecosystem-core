"""Contraprovas R663–R666 em processos isolados; fontes do checkout não são editadas."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUTANTS = [
    {"id": "simulation_export", "module": "marceloclaro.orchestrator", "class": "MarceloClaroOrchestrator",
     "method": "scientific_discovery_pipeline", "old": "if r102_ineligible:", "new": "if False:",
     "test": "tests/test_r666_knowledge_orchestration.py::test_simulated_deep_research_never_reaches_review_or_export"},
    {"id": "declaration_as_execution", "module": "marceloclaro.knowledge_evolution", "class": "KnowledgeEvolutionService",
     "method": "plan", "old": '{"executed", "externally_validated"}',
     "new": '{"declared", "executed", "externally_validated"}',
     "test": "tests/test_r666_knowledge_orchestration.py::test_plan_keeps_declarations_out_of_observed_and_explains_gaps"},
    {"id": "false_persistence_receipt", "module": "mci.metabus", "class": "MetacognitiveMemory",
     "method": "record_observation", "old": "self._save(strict=True)", "new": "self._save()",
     "test": "tests/test_r666_knowledge_orchestration.py::test_observation_cannot_return_persisted_receipt_after_write_failure"},
    {"id": "dominated_pareto", "module": "gametheory.phd_auditor", "class": "NashSolver",
     "method": "pure_nash", "old": "if not dominated:", "new": "if True:",
     "test": "tests/test_r665_evolutionary_sequencing.py::test_pareto_does_not_include_dominated_defection"},
]

CHILD = """
import importlib,inspect,json,sys,textwrap
from pathlib import Path
config=json.loads(sys.argv[1])
module=importlib.import_module(config['module'])
cls=getattr(module,config['class'])
function=getattr(cls,config['method'])
source=textwrap.dedent(inspect.getsource(function))
if config['old'] not in source:
    raise RuntimeError('mutation needle absent')
mutated=source.replace(config['old'],config['new'],1)
namespace=dict(function.__globals__)
exec(compile(mutated,inspect.getfile(function),'exec'),namespace)
setattr(cls,config['method'],namespace[config['method']])
import pytest
raise SystemExit(pytest.main([config['test'],'-q','--tb=short']))
"""


def main() -> None:
    results = []
    directory = ROOT / "docs/evidence/R663_R666_MUTATION_LOGS"
    directory.mkdir(exist_ok=True)
    for mutant in MUTANTS:
        with tempfile.TemporaryDirectory(prefix="r666-mutant-") as state:
            env = {**os.environ, "MCI_STATE_DIR": state,
                   "EVOLUTION_STATE_PATH": str(Path(state) / "cycles.json")}
            process = subprocess.run([sys.executable, "-c", CHILD, json.dumps(mutant)],
                                     cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)
        log = directory / (mutant["id"] + ".txt")
        log.write_text(process.stdout + process.stderr, encoding="utf-8")
        results.append({**mutant, "exit_code": process.returncode,
                        "detected": process.returncode == 1 and "FAILED" in process.stdout,
                        "log": str(log), "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()})
    result = {"scope": "Mutações isoladas em memória; não é validação científica externa.",
              "success": all(item["detected"] for item in results), "mutants": results}
    path = ROOT / "docs/evidence/R663_R666_MUTATIONS.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"path": str(path), "success": result["success"],
                      "detected": sum(item["detected"] for item in results)}))
    if not result["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
