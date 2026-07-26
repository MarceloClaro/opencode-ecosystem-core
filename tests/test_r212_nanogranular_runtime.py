# -*- coding: utf-8 -*-
"""Testes RED do runtime nanogranular da SPEC-935-R212.

Este arquivo formaliza os contratos de CA17–CA21 antes da implementação de
``mci.task_runtime`` e de sua integração em ``MarceloClaroOrchestrator``.
Todos os relógios e candidatos são doubles determinísticos; rede, subprocessos
e esperas reais são proibidos durante os testes.
"""

from __future__ import annotations

import http.client
import importlib
import socket
import subprocess
import sys
import time
from dataclasses import FrozenInstanceError, dataclass
from pathlib import Path
from typing import Any
from unittest import mock
from urllib import request as urllib_request

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


PUBLIC_RUNTIME_API = {
    "AcceptanceCriterion",
    "NanoTaskSpec",
    "RuntimeLimits",
    "TaskGraph",
    "TaskRuntime",
}


class _MissingRuntimeAPI:
    """Proxy que mantém a coleta RED mesmo antes de o módulo existir."""

    def __init__(self, error: ModuleNotFoundError):
        self.error = error

    def __getattr__(self, name: str) -> Any:
        pytest.fail(
            "Contrato RED pendente: mci.task_runtime ainda não existe "
            f"(símbolo solicitado: {name}; erro: {self.error})"
        )


@pytest.fixture
def runtime_api() -> Any:
    """Carrega a API-alvo sem transformar sua ausência em skip."""

    try:
        return importlib.import_module("mci.task_runtime")
    except ModuleNotFoundError as error:
        if error.name != "mci.task_runtime":
            raise
        return _MissingRuntimeAPI(error)


@pytest.fixture(autouse=True)
def no_external_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Falha imediatamente se o runtime tentar sair do processo de teste."""

    def blocked(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Testes R212 não permitem rede, subprocesso ou espera real")

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(http.client.HTTPConnection, "connect", blocked)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", blocked)
    monkeypatch.setattr(urllib_request, "urlopen", blocked)
    monkeypatch.setattr(subprocess, "Popen", blocked)
    monkeypatch.setattr(time, "sleep", blocked)


@dataclass
class _FakeClock:
    """Relógio monotônico controlado pelo teste."""

    value: float = 1_000.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


@dataclass
class _RuntimeHarness:
    api: Any
    runtime: Any
    clock: _FakeClock
    outcome_recorder: mock.Mock


def _make_runtime(api: Any, **limit_overrides: Any) -> _RuntimeHarness:
    limit_values = {
        "max_depth": 3,
        "max_fan_out": 4,
        "max_nodes": 20,
        "max_attempts": 3,
        "max_reassignments": 1,
        "lease_seconds": 10.0,
        "wall_clock_seconds": 60.0,
    }
    limit_values.update(limit_overrides)
    clock = _FakeClock()
    outcome_recorder = mock.Mock(name="outcome_recorder")
    runtime = api.TaskRuntime(
        limits=api.RuntimeLimits(**limit_values),
        clock=clock,
        outcome_recorder=outcome_recorder,
    )
    return _RuntimeHarness(api, runtime, clock, outcome_recorder)


def _criterion(api: Any, suffix: str) -> Any:
    return api.AcceptanceCriterion(
        criterion_id=f"criterion-{suffix}",
        description=f"O artefato de {suffix} deve existir e ser verificável.",
        verification=f"artifact:{suffix}:exists",
    )


def _node(
    api: Any,
    task_id: str,
    *,
    dependencies: tuple[str, ...] = (),
    required_capabilities: tuple[str, ...] = ("python",),
    max_attempts: int = 3,
) -> Any:
    return api.NanoTaskSpec(
        task_id=task_id,
        description=f"Produzir o artefato atômico {task_id}.",
        expected_artifact=f"artifacts/{task_id}.json",
        required_capabilities=required_capabilities,
        dependencies=dependencies,
        acceptance_criteria=(_criterion(api, task_id),),
        risk="low",
        budget={"wall_clock_seconds": 30.0, "token_limit": 512},
        max_attempts=max_attempts,
        atomic=True,
    )


def _graph(api: Any, graph_id: str, *nodes: Any) -> Any:
    return api.TaskGraph(graph_id=graph_id, nodes=tuple(nodes))


def _ready_ids(runtime: Any, graph_id: str) -> tuple[str, ...]:
    return tuple(task.task_id for task in runtime.ready_tasks(graph_id))


def _complete(
    runtime: Any,
    graph_id: str,
    task_id: str,
    agent_id: str,
    *,
    idempotency_key: str | None = None,
) -> Any:
    lease = runtime.lease_task(graph_id, task_id, agent_id)
    return runtime.complete_task(
        graph_id=graph_id,
        task_id=task_id,
        agent_id=agent_id,
        lease_token=lease.token,
        result={"artifact": f"{task_id}.json", "ok": True},
        idempotency_key=idempotency_key or f"complete:{graph_id}:{task_id}",
    )


def _chain_graph(api: Any, graph_id: str, node_count: int) -> Any:
    nodes = []
    for index in range(node_count):
        task_id = f"{graph_id}-n{index}"
        dependency = () if index == 0 else (f"{graph_id}-n{index - 1}",)
        nodes.append(_node(api, task_id, dependencies=dependency))
    return _graph(api, graph_id, *nodes)


def _fan_out_graph(api: Any, graph_id: str, child_count: int) -> Any:
    root = _node(api, f"{graph_id}-root")
    children = tuple(
        _node(
            api,
            f"{graph_id}-child-{index}",
            dependencies=(root.task_id,),
        )
        for index in range(child_count)
    )
    return _graph(api, graph_id, root, *children)


def _sized_graph(api: Any, graph_id: str, node_count: int) -> Any:
    """Gera até 21 nós sem exceder profundidade 2 ou fan-out 4."""

    root = _node(api, f"{graph_id}-root")
    parents = tuple(
        _node(
            api,
            f"{graph_id}-parent-{index}",
            dependencies=(root.task_id,),
        )
        for index in range(4)
    )
    leaves = []
    for parent in parents:
        for child_index in range(4):
            leaves.append(
                _node(
                    api,
                    f"{parent.task_id}-leaf-{child_index}",
                    dependencies=(parent.task_id,),
                )
            )
    selected_leaves = leaves[: node_count - 1 - len(parents)]
    return _graph(api, graph_id, root, *parents, *selected_leaves)


def _diamond_graph(api: Any, graph_id: str = "diamond") -> Any:
    root = _node(api, "root")
    left = _node(api, "left", dependencies=("root",))
    right = _node(api, "right", dependencies=("root",))
    join = _node(api, "join", dependencies=("left", "right"))
    return _graph(api, graph_id, root, left, right, join)


def _new_orchestrator(runtime: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    orchestrator_module = importlib.import_module("marceloclaro.orchestrator")
    monkeypatch.setattr(orchestrator_module.metabus, "subscribe", lambda *args: None)
    orchestrator = orchestrator_module.MarceloClaroOrchestrator(
        auto_load_agents=False
    )
    orchestrator.task_runtime = runtime
    return orchestrator


def test_task_runtime_expoe_contrato_publico_r212(runtime_api: Any):
    """CA17–CA20: o módulo deve publicar os tipos canônicos do runtime."""

    # Arrange: define a superfície mínima descrita pela SPEC-935-R212.
    expected = PUBLIC_RUNTIME_API

    # Act: consulta os símbolos sem aceitar skip quando o módulo estiver ausente.
    missing = sorted(name for name in expected if not hasattr(runtime_api, name))

    # Assert: todos os contratos públicos precisam ser importáveis.
    assert not missing, f"Símbolos ausentes em mci.task_runtime: {missing}"


def test_grafo_valido_com_dependencias_existentes_e_aceito(runtime_api: Any):
    """CA17 positivo: dependências internas válidas permitem submissão."""

    # Arrange: cria um DAG linear pequeno e um runtime inteiramente local.
    harness = _make_runtime(runtime_api)
    graph = _chain_graph(runtime_api, "valid-dependencies", 3)

    # Act: submete o grafo e consulta sua primeira fronteira pronta.
    submitted_id = harness.runtime.submit_graph(graph)
    ready = _ready_ids(harness.runtime, graph.graph_id)

    # Assert: o grafo é aceito e somente a raiz fica pronta.
    assert submitted_id == graph.graph_id
    assert ready == ("valid-dependencies-n0",)


def test_grafo_rejeita_dependencia_ausente(runtime_api: Any):
    """CA17 negativo: referência a nó inexistente deve falhar fechado."""

    # Arrange: o único nó referencia deliberadamente uma dependência ausente.
    harness = _make_runtime(runtime_api)
    graph = _graph(
        runtime_api,
        "missing-dependency",
        _node(runtime_api, "orphan", dependencies=("does-not-exist",)),
    )

    # Act + Assert: a submissão inválida é recusada sem estado parcial.
    with pytest.raises(ValueError):
        harness.runtime.submit_graph(graph)


@pytest.mark.parametrize("cycle_kind", ["self", "mutual"])
def test_grafo_rejeita_ciclos(runtime_api: Any, cycle_kind: str):
    """CA17 negativo: ciclos próprios ou entre nós nunca são agendáveis."""

    # Arrange: constrói duas formas mínimas de ciclo.
    harness = _make_runtime(runtime_api)
    if cycle_kind == "self":
        graph = _graph(
            runtime_api,
            "self-cycle",
            _node(runtime_api, "a", dependencies=("a",)),
        )
    else:
        graph = _graph(
            runtime_api,
            "mutual-cycle",
            _node(runtime_api, "a", dependencies=("b",)),
            _node(runtime_api, "b", dependencies=("a",)),
        )

    # Act + Assert: nenhum ciclo é aceito como TaskGraph executável.
    with pytest.raises(ValueError):
        harness.runtime.submit_graph(graph)


@pytest.mark.parametrize("limit_name", ["depth", "fan_out", "nodes"])
def test_limites_aceitam_fronteira_e_rejeitam_excesso(
    runtime_api: Any,
    limit_name: str,
):
    """CA19: profundidade 3, fan-out 4 e 20 nós são limites inclusivos."""

    # Arrange: cria um grafo exatamente no limite e outro uma unidade acima.
    accepted_runtime = _make_runtime(runtime_api).runtime
    rejected_runtime = _make_runtime(runtime_api).runtime
    if limit_name == "depth":
        accepted = _chain_graph(runtime_api, "depth-ok", 4)
        exceeded = _chain_graph(runtime_api, "depth-over", 5)
    elif limit_name == "fan_out":
        accepted = _fan_out_graph(runtime_api, "fanout-ok", 4)
        exceeded = _fan_out_graph(runtime_api, "fanout-over", 5)
    else:
        accepted = _sized_graph(runtime_api, "nodes-ok", 20)
        exceeded = _sized_graph(runtime_api, "nodes-over", 21)

    # Act: submete primeiro o caso de fronteira permitido.
    submitted_id = accepted_runtime.submit_graph(accepted)

    # Assert: a fronteira passa, mas qualquer excesso falha fechado.
    assert submitted_id == accepted.graph_id
    with pytest.raises(ValueError):
        rejected_runtime.submit_graph(exceeded)


def test_dag_diamante_libera_juncao_somente_apos_ambos_os_ramos(
    runtime_api: Any,
):
    """CA18: a junção do diamante exige a conclusão de todas as dependências."""

    # Arrange: submete root → (left, right) → join.
    harness = _make_runtime(runtime_api)
    graph = _diamond_graph(runtime_api)
    harness.runtime.submit_graph(graph)

    # Act: conclui a raiz e depois somente o ramo esquerdo.
    assert _ready_ids(harness.runtime, graph.graph_id) == ("root",)
    _complete(harness.runtime, graph.graph_id, "root", "agent-root")
    branches = _ready_ids(harness.runtime, graph.graph_id)
    _complete(harness.runtime, graph.graph_id, "left", "agent-left")
    before_right_finishes = _ready_ids(harness.runtime, graph.graph_id)

    # Assert: os ramos são paralelos, mas join ainda não pode ser liberado.
    assert branches == ("left", "right")
    assert before_right_finishes == ("right",)
    assert "join" not in before_right_finishes

    # Act: conclui a segunda dependência da junção.
    _complete(harness.runtime, graph.graph_id, "right", "agent-right")

    # Assert: join passa a ser a única tarefa pronta.
    assert _ready_ids(harness.runtime, graph.graph_id) == ("join",)


def test_conclusao_exige_lease_vigente_token_e_agente_corretos(
    runtime_api: Any,
):
    """CA20: apenas o detentor do lease vigente pode concluir uma tarefa."""

    # Arrange: cria e arrenda uma tarefa a um agente conhecido.
    harness = _make_runtime(runtime_api)
    graph = _graph(runtime_api, "lease-contract", _node(runtime_api, "task-a"))
    harness.runtime.submit_graph(graph)
    lease = harness.runtime.lease_task(graph.graph_id, "task-a", "agent-a")
    completion = {
        "graph_id": graph.graph_id,
        "task_id": "task-a",
        "result": {"ok": True},
        "idempotency_key": "task-a-success",
    }

    # Act + Assert: token ou agente divergente é rejeitado.
    with pytest.raises(RuntimeError):
        harness.runtime.complete_task(
            **completion,
            agent_id="agent-a",
            lease_token="invalid-token",
        )
    with pytest.raises(RuntimeError):
        harness.runtime.complete_task(
            **completion,
            agent_id="agent-b",
            lease_token=lease.token,
        )

    # Act: o proprietário conclui dentro do prazo usando o token correto.
    receipt = harness.runtime.complete_task(
        **completion,
        agent_id="agent-a",
        lease_token=lease.token,
    )

    # Assert: a conclusão válida é aceita e possui recibo auditável.
    assert lease.expires_at == pytest.approx(1_010.0)
    assert receipt.task_id == "task-a"
    assert receipt.status == "completed"


def test_lease_expirado_e_reatribuido_e_conclusao_atrasada_e_rejeitada(
    runtime_api: Any,
):
    """CA20: lease vencido não autoriza uma conclusão após reatribuição."""

    # Arrange: arrenda a tarefa ao primeiro agente e avança o relógio fake.
    harness = _make_runtime(runtime_api)
    graph = _graph(runtime_api, "expired-lease", _node(runtime_api, "task-a"))
    harness.runtime.submit_graph(graph)
    old_lease = harness.runtime.lease_task(graph.graph_id, "task-a", "agent-a")
    harness.clock.advance(10.001)

    # Act: o runtime recupera o lease e o entrega, uma única vez, a outro agente.
    current_lease = harness.runtime.lease_task(
        graph.graph_id,
        "task-a",
        "agent-b",
    )

    # Assert: o token muda e o resultado atrasado do agente anterior é recusado.
    assert current_lease.token != old_lease.token
    with pytest.raises(RuntimeError):
        harness.runtime.complete_task(
            graph_id=graph.graph_id,
            task_id="task-a",
            agent_id="agent-a",
            lease_token=old_lease.token,
            result={"source": "late"},
            idempotency_key="late-completion",
        )

    # Act: o detentor atual conclui a tarefa.
    receipt = harness.runtime.complete_task(
        graph_id=graph.graph_id,
        task_id="task-a",
        agent_id="agent-b",
        lease_token=current_lease.token,
        result={"source": "current"},
        idempotency_key="current-completion",
    )

    # Assert: a conclusão atual prevalece e uma reatribuição foi contabilizada.
    state = harness.runtime.task_state(graph.graph_id, "task-a")
    assert receipt.status == "completed"
    assert state.reassignments == 1


def test_conclusao_duplicada_e_idempotente_e_nao_registra_outcome_duas_vezes(
    runtime_api: Any,
):
    """CA20: repetir a mesma conclusão não pode alterar trust duas vezes."""

    # Arrange: prepara uma conclusão válida com chave idempotente fixa.
    harness = _make_runtime(runtime_api)
    graph = _graph(runtime_api, "idempotency", _node(runtime_api, "task-a"))
    harness.runtime.submit_graph(graph)
    lease = harness.runtime.lease_task(graph.graph_id, "task-a", "agent-a")
    completion = {
        "graph_id": graph.graph_id,
        "task_id": "task-a",
        "agent_id": "agent-a",
        "lease_token": lease.token,
        "result": {"artifact": "result.json", "digest": "sha256:abc"},
        "idempotency_key": "completion-key-1",
    }

    # Act: envia duas vezes exatamente a mesma conclusão.
    first = harness.runtime.complete_task(**completion)
    duplicate = harness.runtime.complete_task(**completion)

    # Assert: o mesmo recibo é devolvido e o efeito de outcome ocorre uma vez.
    assert duplicate.completion_id == first.completion_id
    assert duplicate.result == first.result
    harness.outcome_recorder.assert_called_once()

    # Act + Assert: reutilizar a chave com payload divergente é conflito, não retry.
    with pytest.raises(RuntimeError):
        harness.runtime.complete_task(
            **{**completion, "result": {"artifact": "different.json"}}
        )
    harness.outcome_recorder.assert_called_once()


def test_falha_transitoria_permite_retry_e_uma_reatribuicao(runtime_api: Any):
    """CA20 positivo: recuperação transitória respeita o orçamento disponível."""

    # Arrange: arrenda a primeira tentativa ao agente A.
    harness = _make_runtime(runtime_api)
    graph = _graph(runtime_api, "retry-ok", _node(runtime_api, "task-a"))
    harness.runtime.submit_graph(graph)
    first_lease = harness.runtime.lease_task(graph.graph_id, "task-a", "agent-a")

    # Act: registra falha transitória e reatribui a segunda tentativa ao agente B.
    harness.runtime.fail_task(
        graph_id=graph.graph_id,
        task_id="task-a",
        agent_id="agent-a",
        lease_token=first_lease.token,
        error="timeout simulado",
        retryable=True,
    )
    ready_after_failure = _ready_ids(harness.runtime, graph.graph_id)
    second_lease = harness.runtime.lease_task(
        graph.graph_id,
        "task-a",
        "agent-b",
    )
    receipt = harness.runtime.complete_task(
        graph_id=graph.graph_id,
        task_id="task-a",
        agent_id="agent-b",
        lease_token=second_lease.token,
        result={"ok": True},
        idempotency_key="retry-success",
    )

    # Assert: há retry, apenas uma reatribuição e término bem-sucedido.
    state = harness.runtime.task_state(graph.graph_id, "task-a")
    assert ready_after_failure == ("task-a",)
    assert second_lease.token != first_lease.token
    assert receipt.status == "completed"
    assert state.attempts == 2
    assert state.reassignments == 1


def test_retry_e_reassign_falham_fechado_ao_esgotar_orcamento(runtime_api: Any):
    """CA19/CA20 negativo: três tentativas e uma reatribuição são tetos reais."""

    # Arrange: configura os limites padrão explícitos da R212.
    harness = _make_runtime(runtime_api)
    graph = _graph(runtime_api, "retry-exhausted", _node(runtime_api, "task-a"))
    harness.runtime.submit_graph(graph)

    # Act: falha A, reatribui uma vez a B e falha a segunda tentativa.
    lease_a = harness.runtime.lease_task(graph.graph_id, "task-a", "agent-a")
    harness.runtime.fail_task(
        graph.graph_id,
        "task-a",
        "agent-a",
        lease_a.token,
        error="transient-a",
        retryable=True,
    )
    lease_b1 = harness.runtime.lease_task(graph.graph_id, "task-a", "agent-b")
    harness.runtime.fail_task(
        graph.graph_id,
        "task-a",
        "agent-b",
        lease_b1.token,
        error="transient-b1",
        retryable=True,
    )

    # Assert: uma segunda reatribuição para C é recusada.
    with pytest.raises(RuntimeError):
        harness.runtime.lease_task(graph.graph_id, "task-a", "agent-c")

    # Act: B usa a terceira e última tentativa, que também falha.
    lease_b2 = harness.runtime.lease_task(graph.graph_id, "task-a", "agent-b")
    harness.runtime.fail_task(
        graph.graph_id,
        "task-a",
        "agent-b",
        lease_b2.token,
        error="transient-b2",
        retryable=True,
    )

    # Assert: não existe quarta tentativa nem tarefa pronta após o esgotamento.
    state = harness.runtime.task_state(graph.graph_id, "task-a")
    assert state.attempts == 3
    assert state.reassignments == 1
    assert state.status in {"blocked", "failed", "quarantined"}
    assert _ready_ids(harness.runtime, graph.graph_id) == ()
    with pytest.raises(RuntimeError):
        harness.runtime.lease_task(graph.graph_id, "task-a", "agent-b")


def test_falha_nao_transitoria_nao_recebe_retry_automatico(runtime_api: Any):
    """CA20 negativo: erro permanente deve encerrar sem consumir retries extras."""

    # Arrange: cria a primeira tentativa de uma tarefa local.
    harness = _make_runtime(runtime_api)
    graph = _graph(runtime_api, "permanent-failure", _node(runtime_api, "task-a"))
    harness.runtime.submit_graph(graph)
    lease = harness.runtime.lease_task(graph.graph_id, "task-a", "agent-a")

    # Act: reporta uma falha explicitamente não transitória.
    harness.runtime.fail_task(
        graph.graph_id,
        "task-a",
        "agent-a",
        lease.token,
        error="violação permanente de critério",
        retryable=False,
    )

    # Assert: a tarefa termina após uma tentativa e não volta à fila pronta.
    state = harness.runtime.task_state(graph.graph_id, "task-a")
    assert state.attempts == 1
    assert state.status in {"blocked", "failed", "quarantined"}
    assert _ready_ids(harness.runtime, graph.graph_id) == ()


def test_decomposicao_gera_ids_estaveis_dependencias_validas_e_criterios(
    runtime_api: Any,
):
    """CA17 positivo: a decomposição é determinística, atômica e verificável."""

    # Arrange: usa duas instâncias independentes com a mesma entrada canônica.
    first_runtime = _make_runtime(runtime_api).runtime
    second_runtime = _make_runtime(runtime_api).runtime
    request = {
        "objective": "Implementar e testar um endpoint local de status.",
        "required_capabilities": ("python", "testing"),
        "expected_artifact": "mci/local_status.py",
    }

    # Act: decompõe a mesma solicitação duas vezes, sem LLM ou rede.
    first = first_runtime.nanogranulate(**request)
    second = second_runtime.nanogranulate(**request)

    # Assert: IDs e relações permanecem estáveis entre execuções.
    assert first.graph_id == second.graph_id
    assert tuple(node.task_id for node in first.nodes) == tuple(
        node.task_id for node in second.nodes
    )
    assert tuple(node.dependencies for node in first.nodes) == tuple(
        node.dependencies for node in second.nodes
    )
    assert len(first.nodes) > 1
    assert len(first.nodes) <= 20

    node_ids = {node.task_id for node in first.nodes}
    criterion_ids = []
    for node in first.nodes:
        assert node.atomic is True
        assert node.expected_artifact.strip()
        assert set(node.dependencies) <= node_ids
        assert node.acceptance_criteria
        for criterion in node.acceptance_criteria:
            criterion_ids.append(criterion.criterion_id)
            assert criterion.description.strip()
            assert criterion.verification.strip()
    assert len(criterion_ids) == len(set(criterion_ids))


def test_decomposicao_nao_colide_ids_de_objetivos_distintos(runtime_api: Any):
    """CA17 negativo: estabilidade não pode causar colisão entre objetivos."""

    # Arrange: cria duas solicitações semanticamente distintas.
    runtime = _make_runtime(runtime_api).runtime

    # Act: decompõe cada objetivo pelo algoritmo determinístico local.
    graph_a = runtime.nanogranulate(objective="Criar parser JSON local.")
    graph_b = runtime.nanogranulate(objective="Criar validador de DAG local.")

    # Assert: namespaces de grafo e de nós não colidem.
    assert graph_a.graph_id != graph_b.graph_id
    assert {node.task_id for node in graph_a.nodes}.isdisjoint(
        node.task_id for node in graph_b.nodes
    )


def test_decomposicao_rejeita_objetivo_ou_criterio_nao_verificavel(
    runtime_api: Any,
):
    """CA17 negativo: entradas vazias não podem produzir um DAG aparente."""

    # Arrange: prepara o runtime sem qualquer dependência externa.
    runtime = _make_runtime(runtime_api).runtime

    # Act + Assert: objetivo vazio é inválido.
    with pytest.raises(ValueError):
        runtime.nanogranulate(objective="   ")

    # Act + Assert: critério sem procedimento verificável também é inválido.
    with pytest.raises(ValueError):
        criterion = runtime_api.AcceptanceCriterion(
            criterion_id="criterion-invalid",
            description="Critério sem verificação.",
            verification="",
        )
        runtime.nanogranulate(
            objective="Criar artefato local.",
            acceptance_criteria=(criterion,),
        )


def test_nano_task_spec_e_imutavel(runtime_api: Any):
    """CA17: NanoTaskSpec aceito não pode mudar após entrar no DAG."""

    # Arrange: constrói uma especificação atômica válida.
    task = _node(runtime_api, "immutable")

    # Act + Assert: tentativa de mutação direta é recusada.
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        task.description = "Descrição alterada após validação."


def test_orquestrador_inicializa_runtime_nanogranular_sem_remover_delegate(
    runtime_api: Any,
    monkeypatch: pytest.MonkeyPatch,
):
    """CA21 positivo/negativo: integra o novo runtime e preserva delegate legado."""

    # Arrange: neutraliza somente inscrições globais durante a construção local.
    orchestrator_module = importlib.import_module("marceloclaro.orchestrator")
    monkeypatch.setattr(orchestrator_module.metabus, "subscribe", lambda *args: None)

    # Act: cria a instância leve, sem carregar agentes ou acessar serviços.
    orchestrator = orchestrator_module.MarceloClaroOrchestrator(
        auto_load_agents=False
    )

    # Assert: o runtime novo existe e a API legada não foi removida.
    assert isinstance(orchestrator.task_runtime, runtime_api.TaskRuntime)
    assert callable(orchestrator.delegate)


def test_orquestrador_nanogranulate_e_submit_graph_encaminham_ao_runtime(
    runtime_api: Any,
    monkeypatch: pytest.MonkeyPatch,
):
    """CA21 positivo: fachadas de decomposição e submissão preservam o contrato."""

    # Arrange: injeta runtime com relógio fake na instância do orquestrador.
    harness = _make_runtime(runtime_api)
    orchestrator = _new_orchestrator(harness.runtime, monkeypatch)

    # Act: decompõe e submete exclusivamente pelas duas APIs públicas.
    graph = orchestrator.nanogranulate(
        objective="Implementar runtime determinístico local.",
        required_capabilities=("python", "testing"),
    )
    submitted_id = orchestrator.submit_graph(graph)

    # Assert: a fachada retorna TaskGraph e o runtime expõe nós prontos.
    assert isinstance(graph, runtime_api.TaskGraph)
    assert submitted_id == graph.graph_id
    assert _ready_ids(harness.runtime, graph.graph_id)


def test_orquestrador_nanogranulate_e_submit_graph_rejeitam_entradas_invalidas(
    runtime_api: Any,
    monkeypatch: pytest.MonkeyPatch,
):
    """CA17/CA21 negativo: as fachadas não contornam validação fail-closed."""

    # Arrange: cria orquestrador local e um grafo cíclico explícito.
    harness = _make_runtime(runtime_api)
    orchestrator = _new_orchestrator(harness.runtime, monkeypatch)
    cyclic = _graph(
        runtime_api,
        "orchestrator-cycle",
        _node(runtime_api, "a", dependencies=("b",)),
        _node(runtime_api, "b", dependencies=("a",)),
    )

    # Act + Assert: objetivo vazio e grafo cíclico são recusados na fachada.
    with pytest.raises(ValueError):
        orchestrator.nanogranulate(objective="")
    with pytest.raises(ValueError):
        orchestrator.submit_graph(cyclic)


def test_dispatch_ready_atribui_e_explain_assignment_audita_decisao(
    runtime_api: Any,
    monkeypatch: pytest.MonkeyPatch,
):
    """CA21 positivo: dispatch e explicação usam candidatos locais determinísticos."""

    # Arrange: uma tarefa exige duas capacidades; apenas um candidato possui ambas.
    harness = _make_runtime(runtime_api)
    orchestrator = _new_orchestrator(harness.runtime, monkeypatch)
    graph = _graph(
        runtime_api,
        "dispatch-positive",
        _node(
            runtime_api,
            "task-a",
            required_capabilities=("python", "testing"),
        ),
    )
    orchestrator.submit_graph(graph)
    candidates = (
        {
            "agent_id": "agent-complete",
            "description": "Implementação e testes locais",
            "capabilities": ("python", "testing"),
            "status": "available",
            "trust_score": 0.90,
            "confidence_score": 0.80,
            "load": 0.10,
            "circuit_open": False,
        },
        {
            "agent_id": "agent-missing-capability",
            "description": "Somente implementação",
            "capabilities": ("python",),
            "status": "available",
            "trust_score": 0.99,
            "confidence_score": 0.99,
            "load": 0.0,
            "circuit_open": False,
        },
    )

    # Act: despacha a fronteira pronta e solicita a explicação persistida.
    assignments = orchestrator.dispatch_ready(
        graph.graph_id,
        candidates=candidates,
    )
    explanation = orchestrator.explain_assignment(graph.graph_id, "task-a")

    # Assert: hard gate precede score e a decisão contém dados auditáveis.
    assert len(assignments) == 1
    assert assignments[0].task_id == "task-a"
    assert assignments[0].agent_id == "agent-complete"
    assert assignments[0].lease_token
    assert explanation["selected_agent_id"] == "agent-complete"
    assert explanation["eligible_agents"] == ["agent-complete"]
    assert "agent-missing-capability" in explanation["excluded_agents"]
    selected_scores = explanation["scores"]["agent-complete"]
    assert {"semantic", "capability", "confidence", "load", "utility"} <= set(
        selected_scores
    )
    assert sum(explanation["weights"].values()) == pytest.approx(1.0)


def test_dispatch_ready_sem_elegivel_bloqueia_sem_atribuicao(
    runtime_api: Any,
    monkeypatch: pytest.MonkeyPatch,
):
    """CA21 negativo: nenhum candidato elegível não pode gerar fallback permissivo."""

    # Arrange: todos os candidatos falham no hard gate de capacidade.
    harness = _make_runtime(runtime_api)
    orchestrator = _new_orchestrator(harness.runtime, monkeypatch)
    graph = _graph(
        runtime_api,
        "dispatch-blocked",
        _node(
            runtime_api,
            "task-a",
            required_capabilities=("python", "security"),
        ),
    )
    orchestrator.submit_graph(graph)
    candidates = (
        {
            "agent_id": "agent-ineligible",
            "description": "Agente sem security",
            "capabilities": ("python",),
            "status": "available",
            "trust_score": 1.0,
            "confidence_score": 1.0,
            "load": 0.0,
            "circuit_open": False,
        },
    )

    # Act: tenta despachar e consulta tanto estado quanto explicação.
    assignments = orchestrator.dispatch_ready(
        graph.graph_id,
        candidates=candidates,
    )
    state = harness.runtime.task_state(graph.graph_id, "task-a")
    explanation = orchestrator.explain_assignment(graph.graph_id, "task-a")

    # Assert: não há fallback, seleção ou lease quando todos falham no gate.
    assert list(assignments) == []
    assert state.status == "blocked"
    assert explanation["selected_agent_id"] is None
    assert explanation["eligible_agents"] == []
    assert "agent-ineligible" in explanation["excluded_agents"]


def test_explain_assignment_rejeita_tarefa_desconhecida(
    runtime_api: Any,
    monkeypatch: pytest.MonkeyPatch,
):
    """CA21 negativo: explicação inexistente não pode ser fabricada."""

    # Arrange: submete um grafo válido sem despachar a tarefa solicitada.
    harness = _make_runtime(runtime_api)
    orchestrator = _new_orchestrator(harness.runtime, monkeypatch)
    graph = _graph(runtime_api, "explain-unknown", _node(runtime_api, "known"))
    orchestrator.submit_graph(graph)

    # Act + Assert: uma tarefa que não pertence ao grafo produz erro explícito.
    with pytest.raises(KeyError):
        orchestrator.explain_assignment(graph.graph_id, "unknown")
