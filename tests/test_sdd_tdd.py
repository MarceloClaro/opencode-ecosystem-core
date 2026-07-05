# -*- coding: utf-8 -*-
"""
Testes SDD/TDD (SPEC-006) — Protocolo obrigatório de todos os componentes.

Execução:
    pytest tests/test_sdd_tdd.py -v
"""

import os
import re
import sys
import glob
import tempfile

os.environ.setdefault("MCI_STATE_DIR", tempfile.mkdtemp(prefix="mci_test_sdd_"))

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from sdd.spec_engine import spec_registry, spec_verifier, SpecRegistry  # noqa: E402
from sdd.tdd_runner import TDDRunner  # noqa: E402
from marceloclaro.orchestrator import MarceloClaroOrchestrator  # noqa: E402
from marceloclaro.agent_loader import load_agent_definitions  # noqa: E402
from mci.blackboard import blackboard  # noqa: E402


# ----------------------------------------------------------------------
# RF-006.1 a RF-006.3 — Conformidade dos agentes
# ----------------------------------------------------------------------

def _agent_files():
    return sorted(glob.glob(os.path.join(REPO_ROOT, "agents", "*.md")))


def test_all_agents_have_valid_frontmatter():
    """RF-006.1: todo agente declara id, name, description e capabilities."""
    agents = load_agent_definitions()
    assert len(agents) >= 5, "O ecossistema deve ter os 5 agentes essenciais"
    for agent in agents:
        assert agent.get("agent_id"), "Agente sem agent_id"
        assert agent.get("name"), f"Agente {agent.get('agent_id')} sem name"
        assert agent.get("description"), f"Agente {agent.get('agent_id')} sem description"
        assert agent.get("capabilities"), f"Agente {agent.get('agent_id')} sem capabilities"


def test_all_agents_declare_sdd_protocol():
    """RF-006.2: todo agente declara a seção 'Protocolo SDD'."""
    for path in _agent_files():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Protocolo SDD" in content, f"{os.path.basename(path)} sem Protocolo SDD"
        assert "SpecVerifier" in content, f"{os.path.basename(path)} não referencia o SpecVerifier"


def test_all_agents_declare_tdd_protocol():
    """RF-006.3: todo agente declara a seção 'Protocolo TDD' (Red-Green-Refactor)."""
    for path in _agent_files():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Protocolo TDD" in content, f"{os.path.basename(path)} sem Protocolo TDD"
        for phase in ("RED", "GREEN", "REFACTOR"):
            assert phase in content, f"{os.path.basename(path)} sem fase {phase}"


# ----------------------------------------------------------------------
# SpecRegistry e SpecVerifier
# ----------------------------------------------------------------------

def test_spec_registry_loads_formal_specs():
    """As especificações formais SPEC-001..006 devem ser carregadas de specs/."""
    registry = SpecRegistry()
    formal = [sid for sid in registry.specs if sid.startswith("SPEC-")]
    assert len(formal) >= 6, f"Esperado >= 6 specs formais, encontrado {len(formal)}"
    # Cada spec formal deve apontar para um arquivo de teste existente
    for sid in formal:
        spec = registry.get(sid)
        assert spec.test_file, f"{sid} sem test_file vinculado"
        assert os.path.exists(os.path.join(REPO_ROOT, spec.test_file)), \
            f"{sid}: arquivo de teste {spec.test_file} não existe"


def test_every_formal_spec_has_component_coverage():
    """Auditoria SDD: componentes centrais devem estar cobertos por spec."""
    covered = {spec_registry.get(sid).component for sid in spec_registry.specs
               if sid.startswith("SPEC-")}
    for component in ("mci.metabus", "mci.blackboard", "mci.reflexion",
                      "transformer", "marceloclaro.orchestrator", "agents"):
        assert component in covered, f"Componente {component} sem especificação formal"


def test_verifier_blocks_bad_output():
    """INV-006.2: critérios verificáveis reprovam entregas inadequadas."""
    spec = spec_registry.create_task_spec(
        "gerar relatório", "gerar relatório com no mínimo 100 caracteres")
    spec.criteria = []
    spec.add_criterion("Entrega possui >= 100 caracteres",
                       lambda out: isinstance(out, str) and len(out) >= 100)

    bad = spec_verifier.verify(spec.spec_id, "curto demais")
    assert not bad["verified"]
    assert spec.status == "red"

    good = spec_verifier.verify(spec.spec_id, "x" * 120)
    assert good["verified"]
    assert spec.status == "green"


# ----------------------------------------------------------------------
# TDDRunner — Ciclo Red-Green-Refactor
# ----------------------------------------------------------------------

def test_task_spec_red_to_green():
    """O ciclo TDD converge de RED para GREEN com produtor iterativo."""
    spec = spec_registry.create_task_spec("somar lista", "produzir a soma de [1,2,3]")
    spec.criteria = []
    spec.add_criterion("Resultado é 6", lambda out: out == 6)

    attempts = {"n": 0}

    def producer(objective, feedback):
        attempts["n"] += 1
        return 0 if attempts["n"] == 1 else 6  # 1ª iteração falha de propósito

    runner = TDDRunner(max_iterations=3)
    result = runner.run_cycle(spec, producer)
    assert result["success"]
    assert result["phase"] == "verified"
    assert spec.status == "verified"
    # Histórico deve conter a fase RED com 0 critérios passando (definição de TDD)
    red = [h for h in result["history"] if h["phase"] == "red"]
    assert red and red[0]["verification"]["passed_count"] == 0


def test_tdd_refactor_reverts_on_break():
    """REFACTOR que quebra critérios deve ser revertido (INV do ciclo)."""
    spec = spec_registry.create_task_spec("gerar texto", "texto com a palavra 'ok'")
    spec.criteria = []
    spec.add_criterion("Contém 'ok'", lambda out: isinstance(out, str) and "ok" in out)

    runner = TDDRunner()
    result = runner.run_cycle(
        spec,
        producer_fn=lambda obj, fb: "resultado ok",
        refactor_fn=lambda out, ctx: "quebrado",  # refatoração ruim
    )
    assert result["success"]
    assert result["output"] == "resultado ok", "Refatoração que quebra deve ser revertida"


def test_tdd_requires_criteria():
    """TDD sem critérios de aceitação deve ser rejeitado (RED impossível)."""
    spec = spec_registry.create_task_spec("sem critérios", "objetivo qualquer")
    spec.criteria = []
    runner = TDDRunner()
    result = runner.run_cycle(spec, lambda obj, fb: "qualquer coisa")
    assert not result["success"]
    assert result["phase"] == "red"


# ----------------------------------------------------------------------
# RF-006.4 — Integração com o orquestrador (gate SDD)
# ----------------------------------------------------------------------

def test_task_with_spec_lifecycle():
    """delegate_with_spec cria spec RED, injeta no contexto e verifica na conclusão."""
    orch = MarceloClaroOrchestrator(auto_load_agents=True, strict_sdd=True)

    handle = orch.delegate_with_spec(
        "Pesquisar literatura sobre SDD",
        required_capabilities=["search"],
        acceptance_criteria=["A entrega não pode ser vazia."],
    )
    task_id, spec_id = handle["task_id"], handle["spec_id"]

    # A spec nasce em RED e está vinculada à tarefa
    assert orch.task_specs[task_id] == spec_id
    spec = spec_registry.get(spec_id)
    assert spec is not None and spec.criteria

    # O contexto da tarefa carrega o contrato SDD para o agente
    task = blackboard.tasks[task_id]
    assert task.context["sdd"]["spec_id"] == spec_id
    assert task.context["sdd"]["acceptance_criteria"]

    # Conclusão com entrega válida passa no gate SDD
    agent = task.assigned_to
    orch.report_completion(task_id, agent, "Revisão de literatura concluída com 12 fontes.", True)
    assert blackboard.tasks[task_id].status == "completed"
    assert spec_registry.get(spec_id).status == "green"


def test_strict_sdd_gate_fails_empty_delivery():
    """INV-006.1: no modo estrito, entrega vazia é reprovada e vira falha."""
    orch = MarceloClaroOrchestrator(auto_load_agents=True, strict_sdd=True)
    handle = orch.delegate_with_spec(
        "Implementar função de parsing",
        required_capabilities=["python"],
        acceptance_criteria=["A entrega não pode ser vazia."],
    )
    task_id = handle["task_id"]
    agent = blackboard.tasks[task_id].assigned_to

    orch.report_completion(task_id, agent, "", True)  # entrega vazia
    assert blackboard.tasks[task_id].status == "failed", \
        "Gate SDD estrito deve reprovar entrega vazia"


def test_orchestrator_status_exposes_sdd():
    """INV-005.3 estendido: status() expõe métricas SDD para auditoria."""
    orch = MarceloClaroOrchestrator(auto_load_agents=True)
    status = orch.status()
    assert "sdd" in status
    assert status["sdd"]["specs_registered"] >= 6
