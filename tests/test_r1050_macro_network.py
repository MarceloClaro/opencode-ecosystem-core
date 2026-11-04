"""R1050: macro-rede de orquestração, skills, evidência e gates."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from mci.macro_network import MacroNetwork

ROOT = Path(__file__).resolve().parents[1]


def test_snapshot_has_orchestrator_skills_kdense_and_gates():
    snap = MacroNetwork().snapshot()
    assert snap["counts"]["orchestrator"] == 1
    assert snap["counts"]["skill"] >= 50
    assert snap["counts"]["scientific_skill"] == 177
    assert snap["counts"]["scientific_category"] == 11
    assert snap["counts"]["gate"] == 4
    assert snap["policy"]["read_only"] is True
    assert snap["policy"]["execution_proof"] is False
    assert any(node["id"] == "skill:kdense-ciencia-seletiva" for node in snap["nodes"])
    assert any(edge["relation"] == "contains" for edge in snap["edges"])


def test_paths_and_neighbors_are_deterministic():
    network = MacroNetwork()
    path = network.path("orchestrator:marceloclaro", "kdense:literature-review", 5)
    assert path and path[0] == "orchestrator:marceloclaro"
    assert "kdense-category:literatura-citacao-editorial" in path
    assert network.path("orchestrator:marceloclaro", "gate:metacognitive", 1) == [
        "orchestrator:marceloclaro", "gate:metacognitive"]
    neighbors = network.neighbors("gate:metacognitive", relation="governed_by")
    assert neighbors and all(item["relation"] == "governed_by" for item in neighbors)
    assert network.path("orchestrator:marceloclaro", "nao-existe", 2) is None


def test_risk_summary_and_cli_snapshot(tmp_path):
    network = MacroNetwork()
    risk = network.risk_summary()
    assert risk["categories"]["bioinformatica-genomica"] == 36
    assert risk["risk_flags"]["dual-use-review"] >= 1
    out = tmp_path / "macro.json"
    proc = subprocess.run([sys.executable, "-m", "mci.macro_network", "snapshot",
                           "--out", str(out)], cwd=ROOT, capture_output=True,
                          text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    assert json.loads(out.read_text())["counts"]["scientific_skill"] == 177


def test_orchestrator_exposes_snapshot_without_promoting_confidence():
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    orchestrator = MarceloClaroOrchestrator(auto_load_agents=False)
    snap = orchestrator.macro_network_snapshot()
    assert snap["policy"]["confidence_promoted"] is False
    assert snap["policy"]["network"] is False
