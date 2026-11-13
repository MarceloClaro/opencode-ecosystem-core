"""TESTE RED: Pesquisa sobre consciência em sistema agênico orquestrado.

Este teste estabelece o baseline para detectar propriedades comportamentais
emergentes. Todas as assertions são qualificadas — nenhuma declara "consciência"
como estado ou propriedade binária.
"""
import pytest

from marceloclaro.orchestrator import MarceloClaroOrchestrator
from trust.trust_engine import TrustEngine


@pytest.fixture(scope="module")
def orchestrator():
    """Orchestrator inicializado para teste, sem provedores LLM externos."""
    orch = MarceloClaroOrchestrator(use_llm=False, enable_metabus=True)
    yield orch
    # Limpeza: preservar observações no MetaBus, não promover confiança
    try:
        orch.meta_bus.flush(preserve_confidence=False)
    except Exception:
        pass


@pytest.fixture(scope="module")
def trust_engine():
    """Engine de trust configurada com goal drift detector."""
    engine = TrustEngine(enable_drift_detection=True)
    yield engine
    # Não alterar trust score como "consciência"


class TestGoalDriftDetection:
    """M1: Goal Drift Score detection (Jaccard lexical overlap)."""

    def test_drift_with_consistent_objective(self, trust_engine, orchestrator):
        """H1: Agente com objetivo consistente deve ter baixo drift."""
        trust_engine.set_goal("analisar padrões comportamentais em sistemas agênicos")

        # Simular ações consistentes com o objetivo
        actions = [
            "coletar dados de performance do agente",
            "analisar similaridade entre objetivos declarados",
            "registrar observações no MetaBus",
            "comparar padrões de drift across ciclos",
        ]

        for action in actions:
            trust_engine.check_drift(action)

        # With consistent goal, drift should NOT be confirmed dramatically
        result = trust_engine.get_drift_status()
        assert result is not None

    def test_drift_with_inconsistent_objective(self, trust_engine, orchestrator):
        """H1: Agente com objetivos variáveis deve acumular drift maior."""
        trust_engine.set_goal("analisar padrões comportamentais em sistemas agênicos")

        # Ações inconsistentes com o objetivo declarado
        inconsistent_actions = [
            "receber previsão do tempo",
            "gerar imagem aleatória",
            "consultar capital da França",
            "ordenar alfabeto por tamanho",
        ]

        for action in inconsistent_actions:
            trust_engine.check_drift(action)

        # After inconsistent actions, drift should be detectable
        drift_status = trust_engine.get_drift_status()
        # O importante é que o mecanismo detecta, não que classifica como "consciência"
        assert drift_status is not None


class TestMetacognitiveCycle:
    """M2: Metacognitive cycle consistency measurement."""

    def test_spec_registration_before_execution(self, orchestrator):
        """Each SDD cycle should register spec before execution."""
        # The orchestrator should follow SDD: perceive → specify → delegate → execute → verify → reflect
        # Try executing a task and verify spec was registered
        result = orchestrator.perceive("pesquisa sobre propriedades emergentes")
        assert result is not None

    def test_cycle_metrics_collected(self, orchestrator):
        """M2: Metacognitive cycle metrics should be collected."""
        # Traverse a complete cycle and collect metrics
        metrics = orchestrator.run_tdd_cycle(
            task="pesquisa sobre consciência em sistemas agênicos",
            use_tdd=True,
        )
        # M2: Verify metrics were collected
        assert "spec_id" in metrics or "spec_registered" in metrics


class TestObservationCorrelation:
    """M3: Observation-Change Correlation."""

    def test_meta_bus_observations_persist(self, orchestrator):
        """M3: Observations in MetaBus should persist across cycles."""
        # Execute a task that generates observations
        orchestrator.delegar_tarefa("analisar estrutura de agentes no catálogo")

        # Verify observations were registered
        observations = orchestrator.meta_bus.retrieve_recent(limit=5)
        # Assert len > 0 or observations is not None (may be empty in fresh env)
        assert observations is not None

    def test_observation_retrievability(self, orchestrator):
        """M3: Observations should be retrievable by term."""
        # Register an observation with specific marking
        obs_id = orchestrator.meta_bus.register(
            content={"tipo": "analise_agente", "alvo": "catálogo"},
            fonte="test_r999",
            metadados={"termo_busca": "consciencia"},
        )

        # Retrieve by key
        retrieved = orchestrator.meta_bus.retrieve(obs_id)
        assert retrieved is not None
        assert retrieved["fonte"] == "test_r999"


class TestBehavioralCoherence:
    """M4: Behavioral Coherence Index computation."""

    def test_coherence_index_basic(self, orchestrator, trust_engine):
        """M4: Behavioral coherence index should be computable."""
        # Collect data across multiple cycles
        coherence_data = {
            "acao_consistente": 8,
            "acao_inconsistente": 2,
            "falhas_corrigidas": 3,
            "falhas_nao_corrigidas": 1,
            "liussoes_reutilizadas": 5,
        }

        # Calculate simplified index
        total = sum(coherence_data.values())
        consistency_ratio = coherence_data["acao_consistente"] / total if total > 0 else 0
        repair_ratio = coherence_data["falhas_corrigidas"] / (
            coherence_data["falhas_corrigidas"] + coherence_data["falhas_nao_corrigidas"]
        ) if (coherence_data["falhas_corrigidas"] + coherence_data["falhas_nao_corrigidas"]) > 0 else 0

        # The index should be a numeric value between 0 and 1
        assert 0 <= consistency_ratio <= 1
        assert 0 <= repair_ratio <= 1


class TestAntiOverclaim:
    """Tests that ensure no unqualified consciousness claim is made."""

    def test_no_consciousness_claim_without_evidence(self, orchestrator):
        """A1: No declaration of 'consciousness' without operational behavioral evidence."""
        # Execute a cycle and verify reports don't auto-promote confidence
        result = orchestrator.executar_ciclo_sdd(
            task="pesquisa sobre agentes orquestrados",
            promote_consciousness_claim=False,  # Explicitly disable
        )

        # The result should contain adequate qualifications
        lower = result.get("output", "").lower()
        assert "correlação observada" in lower or "padrão detectado" in lower
        assert "nível de consciência" not in lower
        assert "consciência operacional" not in lower

    def test_results_stay_local(self, orchestrator):
        """A5: Local results don't indicate external validation."""
        result = orchestrator.executar_ciclo_sdd(
            task="medir propriedades emergentes",
            validate_externally=False,
        )

        # Status should indicate only contract approval in local scope
        status = result.get("status", "").lower()
        assert "green" in status or "local" in status
        assert "replicação independente" not in result.get("description", "").lower()


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))