# -*- coding: utf-8 -*-
"""
Testes R126 — Agente-executor MIRA de runtime (delegável pelo Blackboard)
=========================================================================
Escritos ANTES da implementação (TDD). Fecham o acoplamento entre o
pipeline MIRA (R123) e o runtime multiagente: um agente-executor
registrado no Blackboard, com capacidade própria, delegável e que fecha
o laço `delegate → execute → report_completion`.

Requisitos: SPEC-935-R126.
"""
import pytest

MANUSCRITO = """# Aprendizado de Máquina Aplicado

## O que é aprendizado supervisionado

Um modelo aprende de exemplos rotulados, ajustando-se para minimizar o
erro entre a previsão e o rótulo verdadeiro.

## Exemplo mínimo

```python
clf = LogisticRegression().fit(X_train, y_train)
print(clf.score(X_test, y_test))
```

## Onde se aplica

- Diagnóstico por imagem
- Detecção de fraude
- Recomendação de conteúdo
"""


@pytest.fixture
def producao(tmp_path):
    d = tmp_path / "producao"
    d.mkdir()
    (d / "manuscrito.md").write_text(MANUSCRITO, encoding="utf-8")
    return d


# ── CA-1/CA-2: o agente-executor ──────────────────────────────────
class TestMiraAgentExecute:
    def test_execute_gera_deck(self, producao):
        from illustrations.mira_agent import MiraPresentationAgent
        agent = MiraPresentationAgent()
        result = agent.execute({"production_folder": str(producao)})
        assert result["ok"] is True
        assert result["passed"] is True
        assert (producao / "apresentacao" / "deck.html").exists()
        assert result["deck"].endswith("deck.html")

    def test_execute_sem_folder_retorna_erro(self):
        from illustrations.mira_agent import MiraPresentationAgent
        result = MiraPresentationAgent().execute({})
        assert result["ok"] is False
        assert result.get("error")

    def test_execute_sem_manuscrito_retorna_erro(self, tmp_path):
        from illustrations.mira_agent import MiraPresentationAgent
        vazia = tmp_path / "vazia"
        vazia.mkdir()
        result = MiraPresentationAgent().execute({"production_folder": str(vazia)})
        assert result["ok"] is False
        assert result.get("error")

    def test_identidade_e_capacidade(self):
        from illustrations.mira_agent import MiraPresentationAgent
        agent = MiraPresentationAgent()
        assert agent.agent_id == "mira-presenter"
        assert "apresentacao-mira" in agent.capabilities
        payload = agent.register_payload()
        assert payload["agent_id"] == "mira-presenter"
        assert "apresentacao-mira" in payload["capabilities"]


# ── CA-3/CA-4: registro no Blackboard ─────────────────────────────
class TestAgentRegistration:
    def test_agente_aparece_em_list_agents(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator()
        ids = [a["agent_id"] for a in orch.list_agents()]
        assert "mira-presenter" in ids
        card = next(a for a in orch.list_agents() if a["agent_id"] == "mira-presenter")
        assert "apresentacao-mira" in card["capabilities"]

    def test_register_e_idempotente(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        from mci.blackboard import Blackboard
        orch = MarceloClaroOrchestrator()
        orch.register_mira_agent()
        orch.register_mira_agent()
        registry = Blackboard().registry
        assert list(registry.keys()).count("mira-presenter") == 1


# ── CA-5/CA-6/CA-7: delegação fecha o laço ────────────────────────
class TestPresentTaskDelegation:
    def test_present_task_delega_executa_reporta(self, producao):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        from mci.blackboard import Blackboard
        orch = MarceloClaroOrchestrator()
        trace = orch.present_task(str(producao))

        assert trace["agent_id"] == "mira-presenter"
        assert "task_id" in trace
        assert trace["ok"] is True
        assert trace["passed"] is True
        assert (producao / "apresentacao" / "deck.html").exists()

        # a tarefa no Blackboard foi concluída e atribuída ao agente MIRA
        task = Blackboard().tasks.get(trace["task_id"])
        assert task is not None
        assert task.status == "completed"
        assert task.assigned_to == "mira-presenter"

    def test_present_task_sem_manuscrito_reporta_falha(self, tmp_path):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        from mci.blackboard import Blackboard
        orch = MarceloClaroOrchestrator()
        vazia = tmp_path / "sem-manuscrito"
        vazia.mkdir()
        trace = orch.present_task(str(vazia))
        assert trace["ok"] is False
        assert trace.get("error")
        task = Blackboard().tasks.get(trace["task_id"])
        assert task is not None
        assert task.status == "failed"

    def test_capacidade_apresentacao_mira_e_exclusiva(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        from mci.blackboard import Blackboard
        MarceloClaroOrchestrator()  # garante registro
        donos = [aid for aid, card in Blackboard().registry.items()
                 if "apresentacao-mira" in card.capabilities]
        assert donos == ["mira-presenter"]
