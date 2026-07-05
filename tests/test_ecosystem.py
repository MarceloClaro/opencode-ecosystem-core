# -*- coding: utf-8 -*-
"""
Testes do OpenCode Ecosystem Core (MCI + orquestrador marceloclaro).

Execução:
    pytest tests/ -v
"""

import os
import sys
import tempfile

# Estado isolado por sessão de teste (deve vir antes dos imports do pacote)
os.environ["MCI_STATE_DIR"] = tempfile.mkdtemp(prefix="mci_test_")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mci.metabus import metabus  # noqa: E402
from mci.blackboard import blackboard  # noqa: E402
from mci.reflexion import reflexion_engine  # noqa: E402, F401
from marceloclaro.orchestrator import MarceloClaroOrchestrator  # noqa: E402
from marceloclaro.agent_loader import load_agent_definitions  # noqa: E402


def test_metabus_publish_subscribe():
    received = []
    metabus.subscribe("test.topic", lambda e: received.append(e))
    dispatched = metabus.publish("test.topic", {"hello": "world"}, source_agent="pytest")
    assert dispatched >= 1
    assert received[0]["payload"]["hello"] == "world"


def test_memory_reflection_updates_confidence():
    initial = metabus.memory.confidence_ledger.get("agent-x", 0.5)
    metabus.memory.add_reflection("agent-x", "tarefa de teste", "reflexão de teste", 1.0)
    updated = metabus.memory.confidence_ledger["agent-x"]
    assert updated > initial
    assert any(e["agent_id"] == "agent-x" for e in metabus.memory.episodic)


def test_agent_loader_reads_frontmatter():
    definitions = load_agent_definitions()
    assert len(definitions) == 5
    ids = {d["agent_id"] for d in definitions}
    assert {"researcher", "coder", "reviewer", "academic_writer", "auditor"} <= ids
    researcher = next(d for d in definitions if d["agent_id"] == "researcher")
    assert "search" in researcher["capabilities"]


def test_blackboard_full_cycle():
    orchestrator = MarceloClaroOrchestrator(auto_load_agents=True)
    assert len(orchestrator.list_agents()) >= 5

    task_id = orchestrator.delegate("Pesquisar padrões A2A", required_capabilities=["search"])

    # O CFP + voluntariado ocorrem sincronamente dentro do publish
    task = blackboard.tasks[task_id]
    assert task.status == "assigned"
    assert task.assigned_to == "researcher"

    orchestrator.report_completion(task_id, "researcher", "ok", success=True)
    assert blackboard.tasks[task_id].status == "completed"

    # A reflexão deve ter atualizado a confiança do researcher
    assert metabus.memory.confidence_ledger.get("researcher", 0) > 0.5


def test_failed_task_lowers_confidence():
    orchestrator = MarceloClaroOrchestrator(auto_load_agents=True)
    task_id = orchestrator.delegate("Implementar parser", required_capabilities=["python"])
    before = metabus.memory.confidence_ledger.get("coder", 0.5)
    orchestrator.report_completion(task_id, "coder", "erro de sintaxe", success=False)
    after = metabus.memory.confidence_ledger["coder"]
    assert after < before
