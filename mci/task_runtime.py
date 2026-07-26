# -*- coding: utf-8 -*-
"""Runtime local e determinístico para grafos de tarefas nanogranulares.

O módulo implementa os contratos CA17–CA20 da SPEC-935-R212 sem depender de
rede, subprocessos ou serviços globais. As especificações de entrada são
imutáveis; o estado mutável da execução permanece encapsulado em
``TaskRuntime``.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import secrets
import threading
import time
import unicodedata
from collections import deque
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping


_TERMINAL_FAILURE_STATES = frozenset({"blocked", "failed", "quarantined"})
_RISK_LEVELS = frozenset({"low", "medium", "high", "critical"})


def _required_text(value: object, field_name: str) -> str:
    """Valida e normaliza um campo textual obrigatório."""

    if not isinstance(value, str):
        raise TypeError(f"{field_name} deve ser uma string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} não pode ser vazio")
    return normalized


def _text_tuple(
    values: Iterable[str],
    field_name: str,
    *,
    reject_duplicates: bool = False,
) -> tuple[str, ...]:
    """Copia um iterável textual para uma tupla validada."""

    if isinstance(values, (str, bytes)):
        raise TypeError(f"{field_name} deve ser um iterável de strings")

    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _required_text(value, field_name)
        if item in seen:
            if reject_duplicates:
                raise ValueError(f"{field_name} contém o item duplicado {item!r}")
            continue
        seen.add(item)
        normalized.append(item)
    return tuple(normalized)


def _canonical_text(value: str) -> str:
    """Produz representação textual estável para geração de identificadores."""

    return " ".join(unicodedata.normalize("NFKC", value).strip().split())


def _canonical_value(value: Any) -> Any:
    """Converte um valor JSON-like em estrutura canônica e auditável."""

    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("valores numéricos do resultado devem ser finitos")
        return value
    if isinstance(value, bytes):
        return {"__bytes__": value.hex()}
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("chaves de mappings do resultado devem ser strings")
            normalized[key] = _canonical_value(item)
        return {key: normalized[key] for key in sorted(normalized)}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        items = [_canonical_value(item) for item in value]
        return sorted(items, key=_canonical_json)
    raise TypeError(
        "resultado deve conter somente valores JSON-like ou bytes; "
        f"recebido {type(value).__name__}"
    )


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _canonical_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


@dataclass(frozen=True, slots=True)
class AcceptanceCriterion:
    """Critério de aceitação com procedimento explícito de verificação."""

    criterion_id: str
    description: str
    verification: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "criterion_id",
            _required_text(self.criterion_id, "criterion_id"),
        )
        object.__setattr__(
            self,
            "description",
            _required_text(self.description, "description"),
        )
        object.__setattr__(
            self,
            "verification",
            _required_text(self.verification, "verification"),
        )


def _criteria_tuple(
    criteria: Iterable[AcceptanceCriterion],
) -> tuple[AcceptanceCriterion, ...]:
    if isinstance(criteria, (str, bytes)):
        raise TypeError("acceptance_criteria deve ser um iterável de critérios")

    result: list[AcceptanceCriterion] = []
    criterion_ids: set[str] = set()
    for criterion in criteria:
        if not isinstance(criterion, AcceptanceCriterion):
            raise TypeError(
                "acceptance_criteria deve conter apenas AcceptanceCriterion"
            )
        if criterion.criterion_id in criterion_ids:
            raise ValueError(
                "acceptance_criteria contém criterion_id duplicado: "
                f"{criterion.criterion_id!r}"
            )
        criterion_ids.add(criterion.criterion_id)
        result.append(criterion)
    return tuple(result)


def _immutable_budget(budget: Mapping[str, int | float]) -> Mapping[str, int | float]:
    if not isinstance(budget, Mapping):
        raise TypeError("budget deve ser um mapping")

    normalized: dict[str, int | float] = {}
    for key, value in budget.items():
        normalized_key = _required_text(key, "budget key")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"budget[{normalized_key!r}] deve ser numérico")
        if not math.isfinite(float(value)) or value <= 0:
            raise ValueError(f"budget[{normalized_key!r}] deve ser positivo e finito")
        normalized[normalized_key] = value
    return MappingProxyType(normalized)


@dataclass(frozen=True, slots=True)
class NanoTaskSpec:
    """Especificação imutável de uma tarefa atômica do DAG."""

    task_id: str
    description: str
    expected_artifact: str
    required_capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    acceptance_criteria: tuple[AcceptanceCriterion, ...] = ()
    risk: str = "low"
    budget: Mapping[str, int | float] = field(
        default_factory=dict,
        hash=False,
    )
    max_attempts: int = 3
    atomic: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "task_id", _required_text(self.task_id, "task_id"))
        object.__setattr__(
            self,
            "description",
            _required_text(self.description, "description"),
        )
        object.__setattr__(
            self,
            "expected_artifact",
            _required_text(self.expected_artifact, "expected_artifact"),
        )
        object.__setattr__(
            self,
            "required_capabilities",
            _text_tuple(self.required_capabilities, "required_capabilities"),
        )
        object.__setattr__(
            self,
            "dependencies",
            _text_tuple(
                self.dependencies,
                "dependencies",
                reject_duplicates=True,
            ),
        )
        object.__setattr__(
            self,
            "acceptance_criteria",
            _criteria_tuple(self.acceptance_criteria),
        )

        normalized_risk = _required_text(self.risk, "risk").lower()
        if normalized_risk not in _RISK_LEVELS:
            raise ValueError(
                f"risk deve ser um de {sorted(_RISK_LEVELS)}, "
                f"recebido {self.risk!r}"
            )
        object.__setattr__(self, "risk", normalized_risk)
        object.__setattr__(self, "budget", _immutable_budget(self.budget))

        if isinstance(self.max_attempts, bool) or not isinstance(self.max_attempts, int):
            raise TypeError("max_attempts deve ser inteiro")
        if self.max_attempts < 1:
            raise ValueError("max_attempts deve ser maior que zero")
        if self.atomic is not True:
            raise ValueError("NanoTaskSpec deve representar uma tarefa atômica")


@dataclass(frozen=True, slots=True)
class RuntimeLimits:
    """Limites inclusivos e fail-closed de uma instância do runtime."""

    max_depth: int = 3
    max_fan_out: int = 4
    max_nodes: int = 20
    max_attempts: int = 3
    max_reassignments: int = 1
    lease_seconds: float = 10.0
    wall_clock_seconds: float = 60.0

    def __post_init__(self) -> None:
        non_negative = ("max_depth", "max_fan_out", "max_reassignments")
        positive = ("max_nodes", "max_attempts")
        for field_name in (*non_negative, *positive):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{field_name} deve ser inteiro")
            minimum = 0 if field_name in non_negative else 1
            if value < minimum:
                raise ValueError(f"{field_name} deve ser >= {minimum}")

        for field_name in ("lease_seconds", "wall_clock_seconds"):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{field_name} deve ser numérico")
            normalized = float(value)
            if not math.isfinite(normalized) or normalized <= 0:
                raise ValueError(f"{field_name} deve ser positivo e finito")
            object.__setattr__(self, field_name, normalized)


@dataclass(frozen=True, slots=True)
class TaskGraph:
    """Coleção imutável de nós; a validação do DAG ocorre na submissão."""

    graph_id: str
    nodes: tuple[NanoTaskSpec, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "graph_id", _required_text(self.graph_id, "graph_id"))
        if isinstance(self.nodes, (str, bytes)):
            raise TypeError("nodes deve ser um iterável de NanoTaskSpec")
        nodes = tuple(self.nodes)
        if any(not isinstance(node, NanoTaskSpec) for node in nodes):
            raise TypeError("nodes deve conter apenas NanoTaskSpec")
        object.__setattr__(self, "nodes", nodes)


@dataclass(frozen=True, slots=True)
class TaskLease:
    """Autorização temporária e vinculada a um único agente/tentativa."""

    graph_id: str
    task_id: str
    agent_id: str
    token: str
    attempt: int
    issued_at: float
    expires_at: float


@dataclass(frozen=True, slots=True)
class CompletionReceipt:
    """Recibo auditável de uma conclusão aceita pelo runtime."""

    completion_id: str
    graph_id: str
    task_id: str
    agent_id: str
    status: str
    result: Any
    idempotency_key: str
    completed_at: float


@dataclass(frozen=True, slots=True)
class TaskState:
    """Snapshot somente leitura do estado corrente de uma tarefa."""

    graph_id: str
    task_id: str
    status: str
    attempts: int
    reassignments: int
    assigned_agent_id: str | None
    lease_token: str | None
    lease_expires_at: float | None
    last_agent_id: str | None
    last_error: str | None
    result: Any = None


@dataclass(slots=True)
class _MutableTaskState:
    status: str = "pending"
    attempts: int = 0
    reassignments: int = 0
    assigned_agent_id: str | None = None
    last_agent_id: str | None = None
    last_error: str | None = None
    lease: TaskLease | None = None
    result: Any = None


@dataclass(slots=True)
class _GraphRun:
    graph: TaskGraph
    submitted_at: float
    topological_order: tuple[str, ...]
    nodes_by_id: dict[str, NanoTaskSpec]
    states: dict[str, _MutableTaskState]


@dataclass(frozen=True, slots=True)
class _StoredCompletion:
    signature: str
    receipt: CompletionReceipt


class TaskRuntime:
    """Executa DAGs locais com leases, retries e idempotência explícitos."""

    def __init__(
        self,
        limits: RuntimeLimits | None = None,
        clock: Callable[[], float] = time.monotonic,
        outcome_recorder: Callable[[str, bool], Any] | None = None,
    ) -> None:
        if limits is not None and not isinstance(limits, RuntimeLimits):
            raise TypeError("limits deve ser RuntimeLimits")
        if not callable(clock):
            raise TypeError("clock deve ser chamável")
        if outcome_recorder is not None and not callable(outcome_recorder):
            raise TypeError("outcome_recorder deve ser chamável")

        self.limits = limits or RuntimeLimits()
        self._clock = clock
        self._outcome_recorder = outcome_recorder
        self._graphs: dict[str, _GraphRun] = {}
        self._completions: dict[tuple[str, str], _StoredCompletion] = {}
        self._lease_counter = 0
        self._lock = threading.RLock()

    def submit_graph(self, graph: TaskGraph) -> str:
        """Valida integralmente e registra um DAG sem deixar estado parcial."""

        if not isinstance(graph, TaskGraph):
            raise TypeError("graph deve ser TaskGraph")

        with self._lock:
            existing = self._graphs.get(graph.graph_id)
            if existing is not None:
                if existing.graph == graph:
                    return graph.graph_id
                raise RuntimeError(
                    f"graph_id {graph.graph_id!r} já foi submetido com outro conteúdo"
                )

            topological_order = self._validate_graph(graph)
            submitted_at = self._now()
            nodes_by_id = {node.task_id: node for node in graph.nodes}
            run = _GraphRun(
                graph=graph,
                submitted_at=submitted_at,
                topological_order=topological_order,
                nodes_by_id=nodes_by_id,
                states={node.task_id: _MutableTaskState() for node in graph.nodes},
            )
            self._refresh_frontier(run)
            self._graphs[graph.graph_id] = run
            return graph.graph_id

    def ready_tasks(self, graph_id: str) -> tuple[NanoTaskSpec, ...]:
        """Retorna a fronteira pronta na ordem declarada pelo grafo."""

        with self._lock:
            run = self._get_run(graph_id)
            now = self._now()
            if self._expire_graph_if_needed(run, now):
                return ()
            self._reap_expired_leases(run, now)
            self._refresh_frontier(run)
            return tuple(
                node
                for node in run.graph.nodes
                if run.states[node.task_id].status == "ready"
            )

    def lease_task(
        self,
        graph_id: str,
        task_id: str,
        agent_id: str,
    ) -> TaskLease:
        """Concede uma tentativa se a tarefa e os orçamentos estiverem válidos."""

        graph_id = _required_text(graph_id, "graph_id")
        task_id = _required_text(task_id, "task_id")
        agent_id = _required_text(agent_id, "agent_id")

        with self._lock:
            run = self._get_run(graph_id)
            state = self._get_mutable_state(run, task_id)
            now = self._now()
            self._require_live_graph(run, now)
            self._reap_expired_leases(run, now)
            self._refresh_frontier(run)

            if state.status == "leased" and state.lease is not None:
                if state.lease.agent_id == agent_id:
                    return state.lease
                raise RuntimeError(
                    f"tarefa {task_id!r} possui lease vigente para outro agente"
                )
            if state.status != "ready":
                raise RuntimeError(
                    f"tarefa {task_id!r} não está pronta; status={state.status!r}"
                )

            node = run.nodes_by_id[task_id]
            max_attempts = min(node.max_attempts, self.limits.max_attempts)
            if state.attempts >= max_attempts:
                state.status = "failed"
                state.last_error = "orçamento de tentativas esgotado"
                self._refresh_frontier(run)
                raise RuntimeError("orçamento de tentativas esgotado")

            is_reassignment = (
                state.last_agent_id is not None
                and state.last_agent_id != agent_id
            )
            proposed_reassignments = state.reassignments + int(is_reassignment)
            if proposed_reassignments > self.limits.max_reassignments:
                raise RuntimeError("orçamento de reatribuições esgotado")

            attempt = state.attempts + 1
            token = self._new_lease_token(
                graph_id=graph_id,
                task_id=task_id,
                agent_id=agent_id,
                attempt=attempt,
            )
            expires_at = min(
                now + self.limits.lease_seconds,
                run.submitted_at + self.limits.wall_clock_seconds,
            )
            if expires_at <= now:
                self._expire_graph_if_needed(run, now)
                raise RuntimeError("orçamento wall-clock esgotado")

            lease = TaskLease(
                graph_id=graph_id,
                task_id=task_id,
                agent_id=agent_id,
                token=token,
                attempt=attempt,
                issued_at=now,
                expires_at=expires_at,
            )
            state.status = "leased"
            state.attempts = attempt
            state.reassignments = proposed_reassignments
            state.assigned_agent_id = agent_id
            state.last_agent_id = agent_id
            state.lease = lease
            return lease

    def complete_task(
        self,
        graph_id: str,
        task_id: str,
        agent_id: str,
        lease_token: str,
        result: Any,
        idempotency_key: str,
    ) -> CompletionReceipt:
        """Conclui uma tarefa ou devolve o recibo da repetição idêntica."""

        graph_id = _required_text(graph_id, "graph_id")
        task_id = _required_text(task_id, "task_id")
        agent_id = _required_text(agent_id, "agent_id")
        lease_token = _required_text(lease_token, "lease_token")
        idempotency_key = _required_text(idempotency_key, "idempotency_key")
        canonical_result = _canonical_value(result)
        signature = self._completion_signature(
            graph_id,
            task_id,
            agent_id,
            lease_token,
            canonical_result,
        )

        with self._lock:
            completion_key = (graph_id, idempotency_key)
            stored = self._completions.get(completion_key)
            if stored is not None:
                if stored.signature != signature:
                    raise RuntimeError(
                        "chave de idempotência reutilizada com payload divergente"
                    )
                return stored.receipt

            run = self._get_run(graph_id)
            state = self._get_mutable_state(run, task_id)
            now = self._now()
            self._require_live_graph(run, now)
            self._reap_expired_leases(run, now)
            self._require_lease(state, agent_id, lease_token, now)

            result_snapshot = copy.deepcopy(result)
            completion_id = "completion-" + hashlib.sha256(
                f"{graph_id}\0{idempotency_key}\0{signature}".encode("utf-8")
            ).hexdigest()[:24]
            receipt = CompletionReceipt(
                completion_id=completion_id,
                graph_id=graph_id,
                task_id=task_id,
                agent_id=agent_id,
                status="completed",
                result=result_snapshot,
                idempotency_key=idempotency_key,
                completed_at=now,
            )

            state.status = "completed"
            state.assigned_agent_id = None
            state.lease = None
            state.last_error = None
            state.result = copy.deepcopy(result_snapshot)
            self._completions[completion_key] = _StoredCompletion(signature, receipt)
            self._refresh_frontier(run)
            self._record_outcome(agent_id, success=True)
            return receipt

    def fail_task(
        self,
        graph_id: str,
        task_id: str,
        agent_id: str,
        lease_token: str,
        *,
        error: str,
        retryable: bool,
    ) -> TaskState:
        """Registra falha e reabre somente tentativas transitórias permitidas."""

        graph_id = _required_text(graph_id, "graph_id")
        task_id = _required_text(task_id, "task_id")
        agent_id = _required_text(agent_id, "agent_id")
        lease_token = _required_text(lease_token, "lease_token")
        error = _required_text(error, "error")
        if not isinstance(retryable, bool):
            raise TypeError("retryable deve ser booleano")

        with self._lock:
            run = self._get_run(graph_id)
            state = self._get_mutable_state(run, task_id)
            now = self._now()
            self._require_live_graph(run, now)
            self._reap_expired_leases(run, now)
            self._require_lease(state, agent_id, lease_token, now)

            node = run.nodes_by_id[task_id]
            max_attempts = min(node.max_attempts, self.limits.max_attempts)
            state.assigned_agent_id = None
            state.lease = None
            state.last_error = error
            if retryable and state.attempts < max_attempts:
                state.status = "pending"
            else:
                state.status = "failed"

            self._refresh_frontier(run)
            self._record_outcome(agent_id, success=False)
            return self._snapshot(run, task_id)

    def block_task(self, graph_id: str, task_id: str, reason: str) -> TaskState:
        """Bloqueia explicitamente uma tarefa, sem fallback permissivo."""

        graph_id = _required_text(graph_id, "graph_id")
        task_id = _required_text(task_id, "task_id")
        reason = _required_text(reason, "reason")
        with self._lock:
            run = self._get_run(graph_id)
            state = self._get_mutable_state(run, task_id)
            if state.status == "completed":
                raise RuntimeError("uma tarefa concluída não pode ser bloqueada")
            state.status = "blocked"
            state.assigned_agent_id = None
            state.lease = None
            state.last_error = reason
            self._refresh_frontier(run)
            return self._snapshot(run, task_id)

    def task_state(self, graph_id: str, task_id: str) -> TaskState:
        """Obtém um snapshot consistente, incluindo expiração de lease/prazo."""

        graph_id = _required_text(graph_id, "graph_id")
        task_id = _required_text(task_id, "task_id")
        with self._lock:
            run = self._get_run(graph_id)
            self._get_mutable_state(run, task_id)
            now = self._now()
            self._expire_graph_if_needed(run, now)
            self._reap_expired_leases(run, now)
            self._refresh_frontier(run)
            return self._snapshot(run, task_id)

    def graph_states(self, graph_id: str) -> tuple[TaskState, ...]:
        """Retorna snapshots de todos os nós na ordem declarada."""

        with self._lock:
            run = self._get_run(graph_id)
            now = self._now()
            self._expire_graph_if_needed(run, now)
            self._reap_expired_leases(run, now)
            self._refresh_frontier(run)
            return tuple(self._snapshot(run, node.task_id) for node in run.graph.nodes)

    def nanogranulate(
        self,
        objective: str,
        required_capabilities: Iterable[str] = (),
        expected_artifact: str | None = None,
        acceptance_criteria: Iterable[AcceptanceCriterion] | None = None,
    ) -> TaskGraph:
        """Decompõe localmente um objetivo em uma cadeia atômica estável."""

        objective = _canonical_text(_required_text(objective, "objective"))
        capabilities = tuple(
            sorted(
                _text_tuple(
                    required_capabilities,
                    "required_capabilities",
                )
            )
        )
        supplied_criteria = _criteria_tuple(acceptance_criteria or ())
        if expected_artifact is not None:
            expected_artifact = _required_text(
                expected_artifact,
                "expected_artifact",
            )

        request_fingerprint = {
            "objective": objective,
            "required_capabilities": capabilities,
            "expected_artifact": expected_artifact,
            "acceptance_criteria": [
                {
                    "criterion_id": criterion.criterion_id,
                    "description": criterion.description,
                    "verification": criterion.verification,
                }
                for criterion in supplied_criteria
            ],
        }
        namespace = hashlib.sha256(
            _canonical_json(request_fingerprint).encode("utf-8")
        ).hexdigest()[:24]
        graph_id = f"nano-{namespace}"
        artifact = expected_artifact or f"artifacts/{graph_id}/result.json"

        if self.limits.max_nodes < 2 or self.limits.max_depth < 1:
            raise ValueError(
                "os limites atuais não comportam decomposição em múltiplos nós"
            )

        plan_id = f"{graph_id}-specify"
        implement_id = f"{graph_id}-implement"
        plan_artifact = f"{artifact}.plan.json"
        common_budget = {
            "wall_clock_seconds": min(30.0, self.limits.wall_clock_seconds),
            "token_limit": 512,
        }
        plan = NanoTaskSpec(
            task_id=plan_id,
            description=f"Especificar de forma verificável: {objective}",
            expected_artifact=plan_artifact,
            required_capabilities=capabilities,
            dependencies=(),
            acceptance_criteria=(
                AcceptanceCriterion(
                    criterion_id=f"criterion-{namespace}-specification",
                    description="A especificação atômica deve existir.",
                    verification=f"artifact:{plan_artifact}:exists",
                ),
            ),
            risk="low",
            budget=common_budget,
            max_attempts=self.limits.max_attempts,
            atomic=True,
        )
        implementation = NanoTaskSpec(
            task_id=implement_id,
            description=f"Produzir o artefato atômico para: {objective}",
            expected_artifact=artifact,
            required_capabilities=capabilities,
            dependencies=(plan_id,),
            acceptance_criteria=(
                AcceptanceCriterion(
                    criterion_id=f"criterion-{namespace}-artifact",
                    description="O artefato objetivo deve existir e ser inspecionável.",
                    verification=f"artifact:{artifact}:exists",
                ),
            ),
            risk="low",
            budget=common_budget,
            max_attempts=self.limits.max_attempts,
            atomic=True,
        )

        nodes: tuple[NanoTaskSpec, ...]
        if self.limits.max_nodes >= 3 and self.limits.max_depth >= 2:
            verify_id = f"{graph_id}-verify"
            verification_artifact = f"{artifact}.verification.json"
            verification_criteria = supplied_criteria or (
                AcceptanceCriterion(
                    criterion_id=f"criterion-{namespace}-verification",
                    description="A verificação do artefato deve ser registrada.",
                    verification=f"artifact:{verification_artifact}:exists",
                ),
            )
            verification = NanoTaskSpec(
                task_id=verify_id,
                description=f"Verificar os critérios de aceitação de: {objective}",
                expected_artifact=verification_artifact,
                required_capabilities=capabilities,
                dependencies=(implement_id,),
                acceptance_criteria=verification_criteria,
                risk="low",
                budget=common_budget,
                max_attempts=self.limits.max_attempts,
                atomic=True,
            )
            nodes = (plan, implementation, verification)
        else:
            if supplied_criteria:
                implementation = NanoTaskSpec(
                    task_id=implementation.task_id,
                    description=implementation.description,
                    expected_artifact=implementation.expected_artifact,
                    required_capabilities=implementation.required_capabilities,
                    dependencies=implementation.dependencies,
                    acceptance_criteria=supplied_criteria,
                    risk=implementation.risk,
                    budget=implementation.budget,
                    max_attempts=implementation.max_attempts,
                    atomic=True,
                )
            nodes = (plan, implementation)

        graph = TaskGraph(graph_id=graph_id, nodes=nodes)
        self._validate_graph(graph)
        return graph

    def _validate_graph(self, graph: TaskGraph) -> tuple[str, ...]:
        if not graph.nodes:
            raise ValueError("TaskGraph deve conter pelo menos um nó")
        if len(graph.nodes) > self.limits.max_nodes:
            raise ValueError(
                f"grafo possui {len(graph.nodes)} nós; limite={self.limits.max_nodes}"
            )

        nodes_by_id: dict[str, NanoTaskSpec] = {}
        criterion_ids: set[str] = set()
        for node in graph.nodes:
            if node.task_id in nodes_by_id:
                raise ValueError(f"task_id duplicado: {node.task_id!r}")
            nodes_by_id[node.task_id] = node
            if not node.acceptance_criteria:
                raise ValueError(
                    f"tarefa {node.task_id!r} não possui critérios de aceitação"
                )
            for criterion in node.acceptance_criteria:
                if criterion.criterion_id in criterion_ids:
                    raise ValueError(
                        f"criterion_id duplicado no grafo: {criterion.criterion_id!r}"
                    )
                criterion_ids.add(criterion.criterion_id)

        children: dict[str, list[str]] = {task_id: [] for task_id in nodes_by_id}
        indegrees: dict[str, int] = {}
        for node in graph.nodes:
            indegrees[node.task_id] = len(node.dependencies)
            for dependency in node.dependencies:
                if dependency not in nodes_by_id:
                    raise ValueError(
                        f"tarefa {node.task_id!r} depende de nó ausente "
                        f"{dependency!r}"
                    )
                children[dependency].append(node.task_id)

        excessive_fan_out = {
            task_id: len(task_children)
            for task_id, task_children in children.items()
            if len(task_children) > self.limits.max_fan_out
        }
        if excessive_fan_out:
            task_id, fan_out = next(iter(excessive_fan_out.items()))
            raise ValueError(
                f"fan-out de {task_id!r} é {fan_out}; "
                f"limite={self.limits.max_fan_out}"
            )

        depths = {task_id: 0 for task_id in nodes_by_id}
        ready = deque(
            node.task_id for node in graph.nodes if indegrees[node.task_id] == 0
        )
        topological_order: list[str] = []
        while ready:
            task_id = ready.popleft()
            topological_order.append(task_id)
            for child_id in children[task_id]:
                depths[child_id] = max(depths[child_id], depths[task_id] + 1)
                indegrees[child_id] -= 1
                if indegrees[child_id] == 0:
                    ready.append(child_id)

        if len(topological_order) != len(graph.nodes):
            raise ValueError("TaskGraph deve ser acíclico")
        graph_depth = max(depths.values(), default=0)
        if graph_depth > self.limits.max_depth:
            raise ValueError(
                f"profundidade do grafo é {graph_depth}; "
                f"limite={self.limits.max_depth}"
            )
        return tuple(topological_order)

    def _now(self) -> float:
        now = float(self._clock())
        if not math.isfinite(now):
            raise RuntimeError("clock retornou valor não finito")
        return now

    def _get_run(self, graph_id: str) -> _GraphRun:
        graph_id = _required_text(graph_id, "graph_id")
        try:
            return self._graphs[graph_id]
        except KeyError:
            raise KeyError(f"grafo desconhecido: {graph_id!r}") from None

    @staticmethod
    def _get_mutable_state(run: _GraphRun, task_id: str) -> _MutableTaskState:
        try:
            return run.states[task_id]
        except KeyError:
            raise KeyError(
                f"tarefa desconhecida no grafo {run.graph.graph_id!r}: {task_id!r}"
            ) from None

    def _expire_graph_if_needed(self, run: _GraphRun, now: float) -> bool:
        deadline = run.submitted_at + self.limits.wall_clock_seconds
        if now < deadline:
            return False
        for state in run.states.values():
            if state.status == "completed" or state.status in _TERMINAL_FAILURE_STATES:
                continue
            state.status = "blocked"
            state.assigned_agent_id = None
            state.lease = None
            state.last_error = "orçamento wall-clock esgotado"
        return True

    def _require_live_graph(self, run: _GraphRun, now: float) -> None:
        if self._expire_graph_if_needed(run, now):
            raise RuntimeError("orçamento wall-clock esgotado")

    def _reap_expired_leases(self, run: _GraphRun, now: float) -> None:
        for task_id, state in run.states.items():
            lease = state.lease
            if lease is None or now < lease.expires_at:
                continue
            state.lease = None
            state.assigned_agent_id = None
            state.last_error = "lease expirado"
            node = run.nodes_by_id[task_id]
            max_attempts = min(node.max_attempts, self.limits.max_attempts)
            state.status = "pending" if state.attempts < max_attempts else "failed"
        self._refresh_frontier(run)

    @staticmethod
    def _refresh_frontier(run: _GraphRun) -> None:
        for task_id in run.topological_order:
            state = run.states[task_id]
            if state.status in {"completed", "leased"} | _TERMINAL_FAILURE_STATES:
                continue
            dependencies = run.nodes_by_id[task_id].dependencies
            dependency_states = [run.states[item].status for item in dependencies]
            if any(status in _TERMINAL_FAILURE_STATES for status in dependency_states):
                state.status = "blocked"
                state.last_error = "dependência terminou sem sucesso"
            elif all(status == "completed" for status in dependency_states):
                state.status = "ready"
            else:
                state.status = "pending"

    @staticmethod
    def _require_lease(
        state: _MutableTaskState,
        agent_id: str,
        lease_token: str,
        now: float,
    ) -> TaskLease:
        lease = state.lease
        if state.status != "leased" or lease is None:
            raise RuntimeError("tarefa não possui lease vigente")
        if now >= lease.expires_at:
            raise RuntimeError("lease expirado")
        if lease.agent_id != agent_id:
            raise RuntimeError("lease pertence a outro agente")
        if not secrets.compare_digest(lease.token, lease_token):
            raise RuntimeError("lease_token inválido")
        return lease

    def _new_lease_token(
        self,
        *,
        graph_id: str,
        task_id: str,
        agent_id: str,
        attempt: int,
    ) -> str:
        self._lease_counter += 1
        material = (
            f"{graph_id}\0{task_id}\0{agent_id}\0{attempt}\0"
            f"{self._lease_counter}\0{secrets.token_hex(24)}"
        )
        return "lease-" + hashlib.sha256(material.encode("utf-8")).hexdigest()

    @staticmethod
    def _completion_signature(
        graph_id: str,
        task_id: str,
        agent_id: str,
        lease_token: str,
        canonical_result: Any,
    ) -> str:
        payload = {
            "graph_id": graph_id,
            "task_id": task_id,
            "agent_id": agent_id,
            "lease_token": lease_token,
            "result": canonical_result,
        }
        return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()

    def _record_outcome(self, agent_id: str, *, success: bool) -> None:
        if self._outcome_recorder is not None:
            self._outcome_recorder(f"delegate:{agent_id}", success)

    @staticmethod
    def _snapshot(run: _GraphRun, task_id: str) -> TaskState:
        state = run.states[task_id]
        lease = state.lease
        return TaskState(
            graph_id=run.graph.graph_id,
            task_id=task_id,
            status=state.status,
            attempts=state.attempts,
            reassignments=state.reassignments,
            assigned_agent_id=state.assigned_agent_id,
            lease_token=lease.token if lease is not None else None,
            lease_expires_at=lease.expires_at if lease is not None else None,
            last_agent_id=state.last_agent_id,
            last_error=state.last_error,
            result=copy.deepcopy(state.result),
        )


__all__ = [
    "AcceptanceCriterion",
    "CompletionReceipt",
    "NanoTaskSpec",
    "RuntimeLimits",
    "TaskGraph",
    "TaskLease",
    "TaskRuntime",
    "TaskState",
]
