"""Métricas descritivas inspiradas em IIT — R1104/P0.

LIMITES EXPLÍCITOS
------------------
Este módulo NÃO calcula Φ (phi) da IIT 3.0/4.0. NÃO mede consciência.
NÃO demonstra causalidade. Entropia de Shannon, informação mútua e um grafo
de transição sequencial são métricas descritivas para monitoramento interno.

As saídas usam ``causal_status='sequence_association_only_not_causal'`` e
``score_semantics='descriptive_monitoring_only_not_consciousness_or_phi'``.
Nenhum score promove trust, stake ou classificação científica.

Referências de delimitação:
- Oizumi, Albantakis & Tononi (2014), IIT 3.0, DOI 10.1371/journal.pcbi.1003588.
- Albantakis et al. (2023), IIT 4.0, DOI 10.1371/journal.pcbi.1011465.
- Shinn et al. (2023), Reflexion, arXiv:2303.11366.
"""

from __future__ import annotations

import hashlib
import logging
import math
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from evolution import evolution_registry
from mci.metabus import metabus

logger = logging.getLogger("mci.iiit_metrics")
logger.setLevel(logging.INFO)

DEFAULT_N_STATES = 10
EPS = 1e-12

OUTCOME_VALUES = ("success", "failure", "abstained", "missing")
OUTCOME_INDEX = {value: index for index, value in enumerate(OUTCOME_VALUES)}
_OUTCOME_ALIASES = {
    "success": "success",
    "succeeded": "success",
    "ok": "success",
    "failure": "failure",
    "failed": "failure",
    "error": "failure",
    "abstained": "abstained",
    "abstain": "abstained",
    "abstention": "abstained",
    "missing": "missing",
    "unknown": "missing",
    "none": "missing",
}


@dataclass(frozen=True)
class IITMetricsResult:
    """Resultado descritivo; ``score`` é None quando não há dados."""

    score: Optional[float]
    entropy: float
    mutual_info: float
    causal_efficacy: float  # mantido por compatibilidade; significa influência sequencial
    strategy_diversity: float
    abstention_rate: float
    trace_count: int
    available: bool = True
    status: str = "ok"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def sequence_efficacy(self) -> float:
        """Nome honesto para o antigo ``causal_efficacy``."""
        return self.causal_efficacy


@dataclass
class CausalGraphResult:
    """Grafo de transição sequencial; não é um grafo causal demonstrado."""

    graph: Dict[str, List[str]]
    causal_power: Dict[str, int]
    total_links: int
    unique_nodes: int
    density: float


def _validate_n_states(n_states: int) -> int:
    if isinstance(n_states, bool) or not isinstance(n_states, int) or n_states < 2:
        raise ValueError("n_states deve ser inteiro >= 2")
    return n_states


def stable_bucket(value: str, buckets: int) -> int:
    """Bucket determinístico entre processos; não usa ``hash()`` randomizado."""
    buckets = _validate_n_states(buckets)
    digest = hashlib.sha256(str(value).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % buckets


def shannon_entropy(distribution: np.ndarray, base: int = 2) -> float:
    """Entropia de Shannon, ignorando zeros em vez de suavizá-los."""
    if base <= 0 or base == 1:
        raise ValueError("base deve ser positiva e diferente de 1")
    dist = np.asarray(distribution, dtype=float).ravel()
    dist = dist[np.isfinite(dist) & (dist > 0)]
    if dist.size == 0:
        return 0.0
    dist = dist / dist.sum()
    entropy = -np.sum(dist * np.log(dist) / np.log(base))
    return float(round(max(0.0, entropy), 6))


def mutual_information(
    p_xy: np.ndarray,
    p_x: Optional[np.ndarray] = None,
    p_y: Optional[np.ndarray] = None,
    base: int = 2,
) -> float:
    """Informação mútua exata de uma tabela conjunta, sem suavização de zeros."""
    if base <= 0 or base == 1:
        raise ValueError("base deve ser positiva e diferente de 1")
    joint = np.asarray(p_xy, dtype=float)
    if joint.ndim != 2:
        raise ValueError("p_xy deve ser uma matriz bidimensional")
    total = joint.sum()
    if total <= 0 or not np.isfinite(total):
        return 0.0
    joint = joint / total

    px = joint.sum(axis=1) if p_x is None else np.asarray(p_x, dtype=float).ravel()
    py = joint.sum(axis=0) if p_y is None else np.asarray(p_y, dtype=float).ravel()
    if px.shape[0] != joint.shape[0] or py.shape[0] != joint.shape[1]:
        raise ValueError("marginais incompatíveis com a tabela conjunta")
    if px.sum() <= 0 or py.sum() <= 0:
        return 0.0
    px = px / px.sum()
    py = py / py.sum()

    mi = 0.0
    for i in range(joint.shape[0]):
        for j in range(joint.shape[1]):
            p = joint[i, j]
            if p > 0 and px[i] > 0 and py[j] > 0:
                mi += p * math.log(p / (px[i] * py[j]), base)
    return float(round(max(0.0, mi), 6))


def discretize_state(value: float, n_states: int = DEFAULT_N_STATES) -> int:
    """Discretiza um valor em [0, 1] de forma determinística."""
    n_states = _validate_n_states(n_states)
    normalized = float(np.clip(value, 0.0, 1.0))
    return min(int(normalized * (n_states - 1)), n_states - 1)


def _normalized_categorical_entropy(counts: Dict[str, int]) -> float:
    values = [count for count in counts.values() if count > 0]
    if len(values) <= 1:
        return 0.0
    entropy = shannon_entropy(np.asarray(values, dtype=float), base=2)
    maximum = math.log2(len(values))
    return float(min(1.0, entropy / maximum)) if maximum > 0 else 0.0


def _payload_of(trace: Dict[str, Any]) -> Dict[str, Any]:
    payload = trace.get("payload")
    return payload if isinstance(payload, dict) else trace


def _first_value(payload: Dict[str, Any], trace: Dict[str, Any], keys) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
        if payload is not trace and key in trace and trace[key] is not None:
            return trace[key]
    return None


def _normalize_outcome(value: Any) -> str:
    if not isinstance(value, str):
        return "missing"
    normalized = value.strip().lower()
    return _OUTCOME_ALIASES.get(normalized, "missing")


def _parse_confidence(payload: Dict[str, Any], trace: Dict[str, Any]) -> Optional[float]:
    value = _first_value(payload, trace, ("confidence_after", "confidence"))
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed) or not 0.0 <= parsed <= 1.0:
        return None
    return parsed


def _parse_strategy(payload: Dict[str, Any], trace: Dict[str, Any]) -> Optional[str]:
    value = _first_value(payload, trace, ("strategy",))
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def _parse_action_id(payload: Dict[str, Any], trace: Dict[str, Any], index: int) -> str:
    value = _first_value(payload, trace, ("action_id",))
    if value is None and payload is not trace:
        value = trace.get("event_id")
    if value is None:
        return f"unidentified_{index}"
    cleaned = str(value).strip()
    return cleaned or f"unidentified_{index}"


def _empty_features(n_states: int, status: str, error: Optional[str], agent_id: Optional[str]) -> Dict[str, Any]:
    return {
        "total_traces": 0,
        "action_ids": [],
        "outcomes": [],
        "confidences": [],
        "strategies": [],
        "abstained_count": 0,
        "success_count": 0,
        "failure_count": 0,
        "missing_outcome_count": 0,
        "unique_strategies": [],
        "strategy_counts": {},
        "strategy_missing_count": 0,
        "confidence_distribution": [0.0] * n_states,
        "confidence_distribution_length": n_states,
        "avg_confidence": None,
        "confidence_variance": None,
        "confidence_missing_count": 0,
        "collection_status": status,
        "collection_error": error,
        "agent_id": agent_id,
    }


def collect_trace_features(
    traces: Optional[List[Dict[str, Any]]] = None,
    agent_id: Optional[str] = None,
    limit: int = 100,
    n_states: int = DEFAULT_N_STATES,
) -> Dict[str, Any]:
    """Extrai features de traces/eventos, lendo ``payload`` quando presente.

    ``missing`` é uma categoria própria. Nenhum outcome, confiança ou
    estratégia ausente é preenchido por default.
    """
    n_states = _validate_n_states(n_states)
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("limit deve ser inteiro >= 1")

    if traces is None:
        try:
            traces = metabus.get_recent_events(limit=limit)
        except Exception as exc:  # noqa: BLE001 - a falha precisa ser reportada
            logger.warning("MetaBus indisponível: %s", exc)
            return _empty_features(n_states, "unavailable", str(exc), agent_id)
    if not isinstance(traces, list):
        raise TypeError("traces deve ser uma lista de objetos")

    if not traces:
        return _empty_features(n_states, "empty", None, agent_id)

    action_ids: List[str] = []
    outcomes: List[str] = []
    confidences: List[Optional[float]] = []
    strategies: List[Optional[str]] = []

    for index, trace in enumerate(traces):
        if not isinstance(trace, dict):
            raise TypeError("cada trace deve ser um objeto")
        payload = _payload_of(trace)
        action_ids.append(_parse_action_id(payload, trace, index))
        outcomes.append(_normalize_outcome(_first_value(payload, trace, ("outcome",))))
        confidences.append(_parse_confidence(payload, trace))
        strategies.append(_parse_strategy(payload, trace))

    outcome_counts = Counter(outcomes)
    strategy_counts = Counter(strategy for strategy in strategies if strategy is not None)
    valid_confidences = [value for value in confidences if value is not None]

    if valid_confidences:
        histogram, _ = np.histogram(valid_confidences, bins=n_states, range=(0.0, 1.0))
        distribution = histogram / len(valid_confidences)
        average = float(np.mean(valid_confidences))
        variance = float(np.var(valid_confidences)) if len(valid_confidences) > 1 else 0.0
    else:
        distribution = np.zeros(n_states, dtype=float)
        average = None
        variance = None

    return {
        "total_traces": len(traces),
        "action_ids": action_ids,
        "outcomes": outcomes,
        "confidences": confidences,
        "strategies": strategies,
        "abstained_count": outcome_counts.get("abstained", 0),
        "success_count": outcome_counts.get("success", 0),
        "failure_count": outcome_counts.get("failure", 0),
        "missing_outcome_count": outcome_counts.get("missing", 0),
        "unique_strategies": sorted(strategy_counts),
        "strategy_counts": dict(strategy_counts),
        "strategy_missing_count": sum(1 for strategy in strategies if strategy is None),
        "confidence_distribution": distribution.tolist(),
        "confidence_distribution_length": len(distribution),
        "avg_confidence": average,
        "confidence_variance": variance,
        "confidence_missing_count": len(confidences) - len(valid_confidences),
        "collection_status": "ok",
        "collection_error": None,
        "agent_id": agent_id,
    }


def _calculate_from_features(features: Dict[str, Any], n_states: int) -> IITMetricsResult:
    n_states = _validate_n_states(n_states)
    total = int(features.get("total_traces", 0))
    if total == 0:
        status = features.get("collection_status", "empty")
        return IITMetricsResult(
            score=None,
            entropy=0.0,
            mutual_info=0.0,
            causal_efficacy=0.0,
            strategy_diversity=0.0,
            abstention_rate=0.0,
            trace_count=0,
            available=False,
            status="insufficient_data",
            metadata={
                "reason": status,
                "collection_error": features.get("collection_error"),
                "score_semantics": "descriptive_monitoring_only_not_consciousness_or_phi",
                "causal_status": "sequence_association_only_not_causal",
            },
        )

    success = int(features.get("success_count", 0))
    failure = int(features.get("failure_count", 0))
    abstained = int(features.get("abstained_count", 0))
    missing = int(features.get("missing_outcome_count", 0))

    # Sem outcome utilizável não há métrica de resultado; não transformar
    # ausência de dados em score baixo.
    if success + failure + abstained == 0:
        return IITMetricsResult(
            score=None,
            entropy=0.0,
            mutual_info=0.0,
            causal_efficacy=0.0,
            strategy_diversity=0.0,
            abstention_rate=0.0,
            trace_count=total,
            available=False,
            status="insufficient_data",
            metadata={
                "reason": "no_outcomes",
                "total_traces_analyzed": total,
                "missing_outcome_rate": 1.0,
                "score_semantics": "descriptive_monitoring_only_not_consciousness_or_phi",
                "causal_status": "sequence_association_only_not_causal",
            },
        )

    distribution = np.asarray(features["confidence_distribution"], dtype=float)
    entropy = shannon_entropy(distribution, base=2)
    maximum_entropy = math.log2(n_states)
    entropy_normalized = min(1.0, entropy / maximum_entropy) if maximum_entropy > 0 else 0.0

    # MI condicionada à estratégia, não ao action_id único de cada episódio.
    # action_id único produziria MI artificialmente alta por sobreajuste.
    condition_values = [
        strategy if strategy is not None else "__missing_strategy__"
        for strategy in features["strategies"]
    ]
    unique_conditions = sorted(set(condition_values))
    condition_index = {value: index for index, value in enumerate(unique_conditions)}
    outcome_indices = [
        OUTCOME_INDEX.get(outcome, OUTCOME_INDEX["missing"])
        for outcome in features["outcomes"]
    ]
    joint = np.zeros((len(unique_conditions), len(OUTCOME_VALUES)), dtype=float)
    for condition, outcome_index in zip(condition_values, outcome_indices):
        joint[condition_index[condition], outcome_index] += 1.0

    mi = mutual_information(joint, base=2)
    h_conditions = shannon_entropy(joint.sum(axis=1), base=2)
    h_outcomes = shannon_entropy(joint.sum(axis=0), base=2)
    denominator = min(h_conditions, h_outcomes)
    mi_normalized = min(1.0, mi / denominator) if denominator > 0 else 0.0

    graph = build_causal_graph_from_traces(features)
    sequence_efficacy = calculate_causal_efficacy(graph)
    strategy_diversity = _normalized_categorical_entropy(features.get("strategy_counts", {}))

    decided = success + failure
    abstention_rate = abstained / total
    missing_rate = missing / total
    coverage = decided / total
    selective_risk = (failure / decided) if decided > 0 else None

    score = (
        0.30 * entropy_normalized
        + 0.30 * mi_normalized
        + 0.20 * sequence_efficacy
        + 0.20 * strategy_diversity
    )
    score = round(max(0.0, min(1.0, score)), 4)

    metadata = {
        "n_states_used": n_states,
        "confidence_distribution_length": len(distribution),
        "total_traces_analyzed": total,
        "outcome_counts": dict(Counter(features["outcomes"])),
        "mi_conditioning_variable": "strategy_or_missing",
        "success_rate": round(success / total, 4),
        "failure_rate": round(failure / total, 4),
        "abstention_rate": round(abstention_rate, 4),
        "missing_outcome_rate": round(missing_rate, 4),
        "coverage": round(coverage, 4),
        "selective_risk": round(selective_risk, 4) if selective_risk is not None else None,
        "avg_confidence": features.get("avg_confidence"),
        "confidence_variance": features.get("confidence_variance"),
        "confidence_missing_count": features.get("confidence_missing_count", 0),
        "confidence_missing_rate": round(
            features.get("confidence_missing_count", 0) / total, 4
        ),
        "strategies_detected": features.get("unique_strategies", []),
        "strategy_counts": features.get("strategy_counts", {}),
        "strategy_missing_count": features.get("strategy_missing_count", 0),
        "strategy_missing_rate": round(
            features.get("strategy_missing_count", 0) / total, 4
        ),
        "causal_status": "sequence_association_only_not_causal",
        "score_semantics": "descriptive_monitoring_only_not_consciousness_or_phi",
        "collection_status": features.get("collection_status", "ok"),
        "collection_error": features.get("collection_error"),
        "agent_id": features.get("agent_id"),
    }

    return IITMetricsResult(
        score=score,
        entropy=round(entropy_normalized, 4),
        mutual_info=round(mi_normalized, 4),
        causal_efficacy=sequence_efficacy,
        strategy_diversity=round(strategy_diversity, 4),
        abstention_rate=round(abstention_rate, 4),
        trace_count=total,
        available=True,
        status="ok",
        metadata=metadata,
    )


def calculate_simplified_ii(
    traces: Optional[List[Dict[str, Any]]] = None,
    agent_id: Optional[str] = None,
    n_states: int = DEFAULT_N_STATES,
) -> IITMetricsResult:
    """Calcula métricas descritivas; não é Φ e não mede consciência."""
    features = collect_trace_features(
        traces, agent_id=agent_id, limit=200, n_states=n_states
    )
    return _calculate_from_features(features, n_states)


def build_causal_graph_from_traces(features: Dict[str, Any]) -> CausalGraphResult:
    """Constrói grafo de transição por adjacência temporal.

    O nome é mantido por compatibilidade. As arestas representam apenas
    ``action_i -> action_{i+1}`` na ordem da lista; não há intervenção,
    controle ou TPM e, portanto, não há causalidade demonstrada.
    """
    action_ids = features.get("action_ids", [])
    if not action_ids or len(action_ids) < 2:
        return CausalGraphResult(graph={}, causal_power={}, total_links=0, unique_nodes=0, density=0.0)

    graph: Dict[str, List[str]] = {}
    all_nodes = set()
    for index in range(len(action_ids) - 1):
        source = action_ids[index] or f"unidentified_{index}"
        target = action_ids[index + 1] or f"unidentified_{index + 1}"
        all_nodes.add(source)
        all_nodes.add(target)
        graph.setdefault(source, [])
        if target not in graph[source]:
            graph[source].append(target)

    causal_power: Dict[str, int] = {
        source: len(set(targets)) for source, targets in graph.items()
    }
    for node in all_nodes:
        causal_power.setdefault(node, 0)

    total_links = sum(len(targets) for targets in graph.values())
    nodes = len(all_nodes)
    maximum_links = nodes * (nodes - 1) if nodes > 1 else 1
    density = total_links / maximum_links if maximum_links > 0 else 0.0
    return CausalGraphResult(
        graph=graph,
        causal_power=causal_power,
        total_links=total_links,
        unique_nodes=nodes,
        density=round(density, 4),
    )


def calculate_causal_efficacy(
    graph_result: CausalGraphResult,
    n_interventions: int = 3,
) -> float:
    """Influência sequencial descritiva; não é eficácia causal demonstrada."""
    if isinstance(n_interventions, bool) or not isinstance(n_interventions, int) or n_interventions < 1:
        raise ValueError("n_interventions deve ser inteiro >= 1")
    causal_power = graph_result.causal_power
    total_power = sum(causal_power.values())
    nodes = len(causal_power)
    if nodes == 0:
        return 0.0
    average_power = total_power / nodes
    normalized = min(average_power / n_interventions, 1.0)
    density_bonus = graph_result.density * 0.1
    return round(min(normalized + density_bonus, 1.0), 4)


def classify_iit_maturity_level(score: Optional[float]) -> str:
    """Classificação descritiva; não declara publicação, consciência ou Φ."""
    if score is None:
        return "insufficient_data - Sem score descritivo; não classificar."
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return "invalid_score - Score não numérico; não classificar."
    value = float(score)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        return "invalid_score - Fora do intervalo 0-1; não classificar."
    if value >= 0.80:
        return "high_structural_signal - Sinal descritivo alto; não é validação científica"
    if value >= 0.65:
        return "moderate_structural_signal - Sinal descritivo moderado; monitoramento"
    if value >= 0.50:
        return "mixed_structural_signal - Sinal descritivo misto; investigar componentes"
    if value >= 0.30:
        return "low_structural_signal - Sinal descritivo baixo; otimização recomendada"
    return "minimal_structural_signal - Sinal descritivo mínimo; não usar como evidência"


def _format_result(result: IITMetricsResult) -> str:
    lines = ["=== Métricas IIT-Simplified ==="]
    if not result.available:
        lines.append(f"Status: {result.status}")
        reason = result.metadata.get("reason")
        if reason:
            lines.append(f"Motivo: {reason}")
        error = result.metadata.get("collection_error")
        if error:
            lines.append(f"Erro de coleta: {error}")
        lines.append("Nenhum score foi calculado; nenhum dado sintético foi gerado.")
        lines.append("Limite: métrica descritiva; não é Φ da IIT 4.0 e não mede consciência.")
        return "\n".join(lines) + "\n"

    average = result.metadata.get("avg_confidence")
    risk = result.metadata.get("selective_risk")
    average_text = f"{average:.4f}" if isinstance(average, (int, float)) else "n/d"
    risk_text = f"{risk:.4f}" if isinstance(risk, (int, float)) else "n/d"
    strategies = result.metadata.get("strategies_detected") or []
    lines.extend([
        f"Score descritivo (0-1): {result.score}",
        f"  - Entropia Normalizada: {result.entropy}",
        f"  - Mutual Information: {result.mutual_info}",
        f"  - Influência Sequencial (não causal): {result.causal_efficacy}",
        f"  - Diversidade de Estratégias: {result.strategy_diversity}",
        f"  - Abstenção: {result.abstention_rate}",
        f"  - Cobertura: {result.metadata.get('coverage')}",
        f"  - Risco seletivo: {risk_text}",
        f"  - Missing outcome: {result.metadata.get('missing_outcome_rate')}",
        f"  - Traces Analisadas: {result.trace_count}",
        "",
        "Detalhes:",
        f"  - Confiança Média: {average_text}",
        f"  - Estratégias: {', '.join(strategies) if strategies else 'nenhuma'}",
        f"  - Semântica: {result.metadata.get('score_semantics')}",
        f"  - Causalidade: {result.metadata.get('causal_status')}",
        "",
        "Limite: métrica descritiva; não é Φ da IIT 4.0, não mede consciência e não demonstra causalidade.",
    ])
    return "\n".join(lines) + "\n"


def iiit_metrics_cli(
    traces: Optional[List[Dict[str, Any]]] = None,
    session_id: Optional[str] = None,
    limit: int = 100,
    n_states: int = DEFAULT_N_STATES,
) -> Dict[str, Any]:
    """Executa a coleta e o cálculo uma única vez, sem fallback sintético."""
    features = collect_trace_features(
        traces, agent_id=session_id, limit=limit, n_states=n_states
    )
    result = _calculate_from_features(features, n_states)
    return {
        "result": result,
        "formatted_output": _format_result(result),
        "raw_features": features,
    }


def record_to_evolution_registry(
    score_result: IITMetricsResult,
    cycle_id: str,
    objective: str,
    lessons: Optional[List[str]] = None,
    registry: Optional[Any] = None,
) -> Dict[str, Any]:
    """Registra um ciclo usando a assinatura real de ``EvolutionRegistry.record``.

    O registry de produção só é usado quando ``registry`` não é fornecido.
    Testes devem passar um ``EvolutionRegistry`` com ``state_path`` temporário.
    """
    if not isinstance(score_result, IITMetricsResult):
        raise TypeError("score_result deve ser IITMetricsResult")
    if not score_result.available or score_result.score is None:
        raise ValueError("Score indisponível; registro recusado.")
    if not isinstance(cycle_id, str) or not cycle_id.strip():
        raise ValueError("cycle_id deve ser texto não vazio")
    if not isinstance(objective, str) or not objective.strip():
        raise ValueError("objective deve ser texto não vazio")

    target = registry if registry is not None else evolution_registry
    classification = classify_iit_maturity_level(score_result.score)
    if lessons is None:
        lessons = [
            f"Score descritivo {score_result.score:.4f} ({classification}); "
            "não é evidência de consciência ou Phi."
        ]

    changes = [
        f"iiit_metrics.py: score descritivo = {score_result.score:.4f}",
        f"entropy={score_result.entropy:.4f}, mutual_info={score_result.mutual_info:.4f}",
        f"sequence_efficacy={score_result.causal_efficacy:.4f}, diversity={score_result.strategy_diversity:.4f}",
        f"abstention_rate={score_result.abstention_rate:.4f}, coverage={score_result.metadata.get('coverage')}",
        f"Classificação: {classification}",
        "Limite: métrica descritiva; não é Φ, não mede consciência e não demonstra causalidade.",
    ]

    cycle = target.record(
        objective=objective,
        changes=changes,
        score=round(score_result.score * 100, 2),
        lessons=lessons,
        round_id=cycle_id,
    )
    recorded = asdict(cycle)
    recorded["iit_simplified"] = {
        "score": score_result.score,
        "entropy": score_result.entropy,
        "mutual_info": score_result.mutual_info,
        "sequence_efficacy": score_result.causal_efficacy,
        "strategy_diversity": score_result.strategy_diversity,
        "abstention_rate": score_result.abstention_rate,
        "coverage": score_result.metadata.get("coverage"),
        "selective_risk": score_result.metadata.get("selective_risk"),
        "trace_count": score_result.trace_count,
        "available": score_result.available,
        "status": score_result.status,
        "classification": classification,
        "causal_status": "sequence_association_only_not_causal",
        "score_semantics": "descriptive_monitoring_only_not_consciousness_or_phi",
    }
    return recorded
