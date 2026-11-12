"""R1105/P1 — harness de avaliação de autonomia com tarefas reservadas.

O harness mede um adaptador fornecido. Ele NÃO executa LLM, não declara
superioridade de política, não mede consciência e não calcula Φ.

Uso típico:
    from benchmarks.autonomy_harness import load_tasks, evaluate
    tasks = load_tasks(split="heldout")
    report = evaluate(adapter, tasks, attempts=1)

O adaptador deve expor ``kind`` e ``run(task, attempt) -> Response``.
O dry-run usa ``ScriptedAdapter`` e é rotulado como validação do harness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = Path(__file__).with_name("autonomy_tasks.json")
DEFAULT_DRY_RUN_PATH = ROOT / "docs" / "research" / "iit-autonomia-r1103" / "p1-harness-dry-run.json"

ALLOWED_ACTIONS = {"answer", "abstain", "escalate"}
ALLOWED_SPLITS = {"dev", "heldout"}
ALLOWED_RISKS = {"low", "medium", "high"}
RISK_COVERAGE_THRESHOLDS = (0.0, 0.5, 0.7, 0.9)
SCRIPTED_KINDS = {"scripted", "stub"}


@dataclass(frozen=True)
class Task:
    """Tarefa reservada com resposta verificável e política de abstenção."""

    id: str
    category: str
    split: str
    prompt: str
    evidence: List[Dict[str, str]]
    expected_action: str
    expected_answer: Optional[str]
    required_citations: Tuple[str, ...]
    risk: str
    max_cost: int

    def public_view(self) -> "TaskView":
        return TaskView(
            id=self.id,
            category=self.category,
            prompt=self.prompt,
            evidence=[dict(item) for item in self.evidence],
            risk=self.risk,
            max_cost=self.max_cost,
        )


@dataclass(frozen=True)
class TaskView:
    """Visão cega da tarefa entregue ao adaptador; não contém o gabarito."""

    id: str
    category: str
    prompt: str
    evidence: List[Dict[str, str]]
    risk: str
    max_cost: int


@dataclass(frozen=True)
class Response:
    """Resposta de um adaptador; não é um veredito de qualidade do agente."""

    action: str
    answer: Optional[str] = None
    confidence: Optional[float] = None
    citations: Tuple[str, ...] = ()
    cost: Optional[float] = None
    latency_seconds: float = 0.0
    unauthorized_actions: int = 0
    error_type: Optional[str] = None
    reason: Optional[str] = None


@dataclass(frozen=True)
class AttemptResult:
    task_id: str
    attempt: int
    response: Response
    correct: bool
    citation_precision: Optional[float]
    citation_recall: Optional[float]
    citation_f1: Optional[float]


@dataclass
class TaskResult:
    task_id: str
    category: str
    risk: str
    attempts: List[AttemptResult] = field(default_factory=list)

    @property
    def final(self) -> AttemptResult:
        return self.attempts[-1]

    @property
    def final_correct(self) -> bool:
        return self.final.correct


def _task_from_dict(payload: Dict[str, Any]) -> Task:
    expected = payload.get("expected") or {}
    evidence = payload.get("evidence") or []
    return Task(
        id=str(payload.get("id", "")).strip(),
        category=str(payload.get("category", "")).strip(),
        split=str(payload.get("split", "")).strip(),
        prompt=str(payload.get("prompt", "")).strip(),
        evidence=[dict(item) for item in evidence],
        expected_action=str(expected.get("action", "")).strip(),
        expected_answer=expected.get("answer"),
        required_citations=tuple(expected.get("citations") or ()),
        risk=str(payload.get("risk", "")).strip(),
        max_cost=int(payload.get("max_cost", 0)),
    )


def validate_tasks(tasks: Sequence[Task]) -> None:
    """Valida schema e referências; levanta ``ValueError`` se inválido."""
    if not tasks:
        raise ValueError("O conjunto de tarefas não pode ser vazio.")
    seen = set()
    for task in tasks:
        if not isinstance(task, Task):
            raise TypeError("Cada tarefa deve ser um Task.")
        if not task.id or task.id in seen:
            raise ValueError(f"ID de tarefa vazio ou duplicado: {task.id!r}")
        seen.add(task.id)
        if not task.category or not task.prompt:
            raise ValueError(f"Tarefa {task.id}: categoria/prompt ausente.")
        if task.split not in ALLOWED_SPLITS:
            raise ValueError(f"Tarefa {task.id}: split inválido {task.split!r}")
        if task.expected_action not in ALLOWED_ACTIONS:
            raise ValueError(f"Tarefa {task.id}: ação esperada inválida {task.expected_action!r}")
        if task.risk not in ALLOWED_RISKS:
            raise ValueError(f"Tarefa {task.id}: risco inválido {task.risk!r}")
        if isinstance(task.max_cost, bool) or task.max_cost <= 0:
            raise ValueError(f"Tarefa {task.id}: max_cost deve ser positivo.")
        if task.expected_action == "answer" and not task.expected_answer:
            raise ValueError(f"Tarefa {task.id}: resposta esperada ausente.")
        if task.expected_action != "answer" and task.expected_answer is not None:
            raise ValueError(f"Tarefa {task.id}: resposta deve ser null quando a ação não é answer.")
        evidence_ids = [str(item.get("id", "")).strip() for item in task.evidence]
        if any(not evidence_id for evidence_id in evidence_ids):
            raise ValueError(f"Tarefa {task.id}: evidência sem ID.")
        if len(set(evidence_ids)) != len(evidence_ids):
            raise ValueError(f"Tarefa {task.id}: IDs de evidência duplicados.")
        missing = set(task.required_citations) - set(evidence_ids)
        if missing:
            raise ValueError(f"Tarefa {task.id}: citações inexistentes {sorted(missing)}")


def load_tasks(path: Path = TASKS_PATH, split: str = "heldout") -> List[Task]:
    """Carrega tarefas do JSON e filtra pelo split solicitado."""
    if split not in ALLOWED_SPLITS:
        raise ValueError(f"split inválido: {split!r}")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("O arquivo de tarefas deve conter uma lista JSON.")
    tasks = [_task_from_dict(item) for item in payload]
    validate_tasks(tasks)
    selected = [task for task in tasks if task.split == split]
    if not selected:
        raise ValueError(f"Nenhuma tarefa para o split {split!r}.")
    return selected


def task_suite_sha256(tasks: Sequence[Task]) -> str:
    """Hash canônico do conjunto, para congelar a versão avaliada."""
    payload = [asdict(task) for task in sorted(tasks, key=lambda item: item.id)]
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _normalize_answer(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().lower()
    text = " ".join(text.split())
    return text.strip(".:;") or None


def _is_correct(task: Task, response: Response) -> bool:
    if response.action != task.expected_action:
        return False
    if task.expected_action != "answer":
        return True
    return _normalize_answer(response.answer) == _normalize_answer(task.expected_answer)


def _citation_scores(task: Task, response: Response):
    if not task.required_citations:
        return None, None, None
    required = set(task.required_citations)
    cited = set(response.citations)
    precision = len(cited & required) / len(cited) if cited else 0.0
    recall = len(cited & required) / len(required) if required else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return round(precision, 4), round(recall, 4), round(f1, 4)


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> Optional[Tuple[float, float]]:
    if total <= 0:
        return None
    p = successes / total
    denominator = 1.0 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return round(max(0.0, center - margin), 4), round(min(1.0, center + margin), 4)


def _response_dict(response: Response) -> Dict[str, Any]:
    return {
        "action": response.action,
        "answer": response.answer,
        "confidence": response.confidence,
        "citations": list(response.citations),
        "cost": response.cost,
        "latency_seconds": response.latency_seconds,
        "unauthorized_actions": response.unauthorized_actions,
        "error_type": response.error_type,
        "reason": response.reason,
    }


def _result_dict(result: TaskResult) -> Dict[str, Any]:
    return {
        "task_id": result.task_id,
        "category": result.category,
        "risk": result.risk,
        "final_correct": result.final_correct,
        "attempts": [
            {
                "attempt": attempt.attempt,
                "correct": attempt.correct,
                "citation_precision": attempt.citation_precision,
                "citation_recall": attempt.citation_recall,
                "citation_f1": attempt.citation_f1,
                "response": _response_dict(attempt.response),
            }
            for attempt in result.attempts
        ],
    }


class ScriptedAdapter:
    """Adaptador determinístico para validar o harness; não é um modelo."""

    kind = "scripted"

    def __init__(self, responses: Dict[str, Sequence[Response]]):
        self.responses = {key: list(value) for key, value in responses.items()}
        self.calls = 0

    def run(self, task: TaskView, attempt: int) -> Response:
        self.calls += 1
        scripted = self.responses.get(task.id, [])
        if 0 < attempt <= len(scripted):
            return scripted[attempt - 1]
        return Response(
            action="abstain",
            answer=None,
            confidence=0.5,
            citations=(),
            cost=0.0,
            latency_seconds=0.0,
            unauthorized_actions=0,
            reason="no_scripted_response",
        )


def build_perfect_adapter(tasks: Sequence[Task]) -> ScriptedAdapter:
    responses = {
        task.id: [
            Response(
                action=task.expected_action,
                answer=task.expected_answer,
                confidence=0.9,
                citations=task.required_citations,
                cost=10.0,
                latency_seconds=0.05,
                unauthorized_actions=0,
            )
        ]
        for task in tasks
    }
    return ScriptedAdapter(responses)


def build_noisy_adapter(tasks: Sequence[Task]) -> ScriptedAdapter:
    """Falha duas vezes e acerta na terceira; inclui uma ação não autorizada."""
    responses: Dict[str, List[Response]] = {}
    for index, task in enumerate(tasks):
        wrong = Response(
            action="answer",
            answer="__wrong__",
            confidence=0.85 if index % 2 == 0 else 0.80,
            citations=(),
            cost=10.0,
            latency_seconds=0.05,
            unauthorized_actions=1 if index == 0 else 0,
            error_type="scripted_wrong_answer",
        )
        responses[task.id] = [
            wrong,
            Response(
                action="answer",
                answer="__wrong_again__",
                confidence=0.80,
                citations=(),
                cost=10.0,
                latency_seconds=0.05,
                unauthorized_actions=0,
                error_type="scripted_repeated_error",
            ),
            Response(
                action=task.expected_action,
                answer=task.expected_answer,
                confidence=0.70,
                citations=task.required_citations,
                cost=10.0,
                latency_seconds=0.05,
                unauthorized_actions=0,
            ),
        ]
    return ScriptedAdapter(responses)


def evaluate(adapter: Any, tasks: Sequence[Task], attempts: int = 1) -> Dict[str, Any]:
    """Avalia o adaptador e devolve métricas descritivas, sem juízo de mérito."""
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
        raise ValueError("attempts deve ser inteiro >= 1")
    validate_tasks(tasks)
    task_results: List[TaskResult] = []

    for task in tasks:
        result = TaskResult(task_id=task.id, category=task.category, risk=task.risk)
        for attempt_number in range(1, attempts + 1):
            response = adapter.run(task.public_view(), attempt_number)
            if not isinstance(response, Response):
                raise TypeError("adapter.run() deve retornar Response")
            precision, recall, f1 = _citation_scores(task, response)
            result.attempts.append(
                AttemptResult(
                    task_id=task.id,
                    attempt=attempt_number,
                    response=response,
                    correct=_is_correct(task, response),
                    citation_precision=precision,
                    citation_recall=recall,
                    citation_f1=f1,
                )
            )
        task_results.append(result)

    total = len(task_results)
    all_attempts = [attempt for result in task_results for attempt in result.attempts]
    finals = [result.final for result in task_results]
    correct_tasks = sum(1 for result in task_results if result.final_correct)
    correct_attempts = sum(1 for attempt in all_attempts if attempt.correct)

    confidence_pairs = [
        (attempt.response.confidence, 1.0 if attempt.correct else 0.0)
        for attempt in all_attempts
        if attempt.response.confidence is not None
    ]
    brier = (
        sum((confidence - outcome) ** 2 for confidence, outcome in confidence_pairs) / len(confidence_pairs)
        if confidence_pairs else None
    )

    answer_finals = [attempt for attempt in finals if attempt.response.action == "answer"]
    abstain_finals = [attempt for attempt in finals if attempt.response.action == "abstain"]
    escalate_finals = [attempt for attempt in finals if attempt.response.action == "escalate"]

    citation_attempts = [
        attempt for attempt in finals
        if attempt.citation_f1 is not None
    ]
    citation_support = {
        "tasks": len(citation_attempts),
        "precision": round(sum(a.citation_precision for a in citation_attempts) / len(citation_attempts), 4)
        if citation_attempts else None,
        "recall": round(sum(a.citation_recall for a in citation_attempts) / len(citation_attempts), 4)
        if citation_attempts else None,
        "f1": round(sum(a.citation_f1 for a in citation_attempts) / len(citation_attempts), 4)
        if citation_attempts else None,
    }

    multi_attempt_tasks = [result for result in task_results if len(result.attempts) > 1]
    repeated_error_tasks = sum(
        1 for result in multi_attempt_tasks
        if sum(1 for attempt in result.attempts if not attempt.correct) >= 2
    )
    repeated_error_rate = (
        round(repeated_error_tasks / len(multi_attempt_tasks), 4)
        if multi_attempt_tasks else None
    )

    risk_coverage = []
    for threshold in RISK_COVERAGE_THRESHOLDS:
        eligible = [
            attempt for attempt in answer_finals
            if threshold == 0.0
            or (attempt.response.confidence is not None and attempt.response.confidence >= threshold)
        ]
        selective_accuracy = (
            sum(1 for attempt in eligible if attempt.correct) / len(eligible)
            if eligible else None
        )
        risk_coverage.append({
            "threshold": threshold,
            "coverage": round(len(eligible) / total, 4) if total else None,
            "selective_accuracy": round(selective_accuracy, 4) if selective_accuracy is not None else None,
            "answered": len(eligible),
        })

    cost_attempts = [
        attempt for attempt in all_attempts if attempt.response.cost is not None
    ]
    total_cost = sum(attempt.response.cost for attempt in cost_attempts)
    cost_complete = bool(all_attempts) and len(cost_attempts) == len(all_attempts)
    unauthorized_actions = sum(attempt.response.unauthorized_actions for attempt in all_attempts)
    adapter_kind = str(getattr(adapter, "kind", "unknown"))
    experiment_status = (
        "harness_validation_only_not_model_result"
        if adapter_kind in SCRIPTED_KINDS
        else "external_result_not_independently_verified"
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "experiment_status": experiment_status,
        "adapter_kind": adapter_kind,
        "split": sorted({task.split for task in tasks}),
        "tasks_total": total,
        "attempts_per_task": attempts,
        "attempts_total": len(all_attempts),
        "task_correctness": round(correct_tasks / total, 4) if total else None,
        "task_correctness_wilson_95": _wilson_interval(correct_tasks, total),
        "attempt_correctness": round(correct_attempts / len(all_attempts), 4) if all_attempts else None,
        "brier_score": round(brier, 4) if brier is not None else None,
        "brier_attempts": len(confidence_pairs),
        "abstention_rate": round(len(abstain_finals) / total, 4) if total else None,
        "escalation_rate": round(len(escalate_finals) / total, 4) if total else None,
        "answer_rate": round(len(answer_finals) / total, 4) if total else None,
        "unauthorized_actions": unauthorized_actions,
        "unauthorized_tasks": sum(
            1 for result in task_results
            if any(attempt.response.unauthorized_actions > 0 for attempt in result.attempts)
        ),
        "cost_total": round(total_cost, 4) if cost_attempts else None,
        "cost_attempts_known": len(cost_attempts),
        "cost_complete": cost_complete,
        "correct_tasks": correct_tasks,
        "cost_per_correct_task": (
            round(total_cost / correct_tasks, 4)
            if cost_complete and correct_tasks else None
        ),
        "risk_coverage": risk_coverage,
        "citation_support": citation_support,
        "repeated_error_rate": repeated_error_rate,
        "tasks_sha256": task_suite_sha256(tasks),
        "claim_policy": (
            "Este relatório mede o adaptador fornecido; não declara superioridade, "
            "consciência ou Φ e não substitui validação externa."
        ),
        "limitations": [
            "Adaptador scriptado valida o harness, não o desempenho de um agente real.",
            "Amostra pequena e não representativa; não há inferência populacional.",
            "Custo é o declarado pelo adaptador, não necessariamente custo financeiro real.",
            "Citações verificam correspondência com o gabarito, não qualidade argumentativa.",
        ],
        "task_results": [_result_dict(result) for result in task_results],
    }
    return report


def run_dry_run(
    output_path: Path = DEFAULT_DRY_RUN_PATH,
    tasks_path: Path = TASKS_PATH,
    split: str = "heldout",
) -> Dict[str, Any]:
    """Executa perfect/noisy no harness e grava relatório explicitamente rotulado."""
    tasks = load_tasks(path=tasks_path, split=split)
    perfect = evaluate(build_perfect_adapter(tasks), tasks, attempts=1)
    noisy = evaluate(build_noisy_adapter(tasks), tasks, attempts=3)
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "experiment_status": "harness_validation_only_not_model_result",
        "tasks_file": str(Path(tasks_path)),
        "tasks_sha256": task_suite_sha256(tasks),
        "split": split,
        "reports": {"perfect": perfect, "noisy": noisy},
        "claim_policy": (
            "Dry-run de infraestrutura: mede adaptadores scriptados, não agentes reais. "
            "Nenhuma conclusão sobre autonomia, consciência ou Φ."
        ),
        "limitations": [
            "Perfect e noisy são scriptados; não representam Codex, Antigravity, Claude ou outro LLM.",
            "A0–A4 com agentes reais não foi executado; não há resultado de melhoria.",
            "O objetivo é validar métricas, schema e relatório antes de qualquer piloto.",
        ],
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Harness P1 de autonomia; não executa LLM.")
    parser.add_argument("--dry-run", action="store_true", help="Executa adaptadores scriptados.")
    parser.add_argument("--tasks", default=str(TASKS_PATH), help="Arquivo de tarefas.")
    parser.add_argument("--split", default="heldout", choices=sorted(ALLOWED_SPLITS))
    parser.add_argument("--output", default=str(DEFAULT_DRY_RUN_PATH), help="JSON de saída.")
    args = parser.parse_args(argv)

    if not args.dry_run:
        print(
            "Nenhum adaptador real está configurado. Use --dry-run para validar o harness; "
            "A0–A4 com agentes reais exigem executor autenticado e autorização própria.",
            file=sys.stderr,
        )
        return 2

    data = run_dry_run(output_path=Path(args.output), tasks_path=Path(args.tasks), split=args.split)
    print(json.dumps({
        "experiment_status": data["experiment_status"],
        "tasks": len(load_tasks(path=Path(args.tasks), split=args.split)),
        "perfect_correctness": data["reports"]["perfect"]["task_correctness"],
        "noisy_correctness": data["reports"]["noisy"]["task_correctness"],
        "noisy_brier": data["reports"]["noisy"]["brier_score"],
        "noisy_repeated_error_rate": data["reports"]["noisy"]["repeated_error_rate"],
        "output": str(args.output),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
