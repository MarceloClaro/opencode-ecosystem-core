"""R1147 — correlações de erro, arranjos e contraprovas.

Três ideias auditáveis:

1. **Correlação de leitura**: além das marginais `p_i`, mede a co-ocorrência
   `p_ij` e o coeficiente `phi`. O modelo independente pode subestimar ou
   superestimar a métrica dependendo do estatístico (fidelidade vs. erro
   múltiplo vs. união).
2. **Arranjo sensível à correlação**: custo de layout combina caminho de portas,
   leitura, crosstalk e `phi` positivo entre qubits medidos juntos.
3. **Contraprovas**: marginais iguais não determinam a junta; greedy pode ser
   subótimo; o arranjo ótimo depende do regime de ruído; layout cego à
   correlação pode ser pior.

Nada aqui executa hardware. Os custos são proxies declarados, não previsões de
fidelidade.
"""
from __future__ import annotations

import itertools
import math
from typing import Iterable

import numpy as np
from scipy.stats import norm

LIMITS = (
    "Modelo offline. Correlação estimada de counts de calibração; não identifica "
    "mecanismo, crosstalk físico ou drift. O custo de layout é um proxy "
    "declarado, não uma previsão de fidelidade. Nenhum hardware é executado e "
    "nenhum resultado autoriza submissão."
)
LAYOUT_LIMITS = (
    "Otimização combinatória sobre um modelo de ruído declarado. O ótimo é "
    "condicional ao modelo; não prova superioridade em hardware real. "
    "Contraexemplos mostram que arranjo ótimo não é universal."
)
INF = float("inf")


# ---------------------------------------------------------------------------
# Correlação de leitura
# ---------------------------------------------------------------------------


def _normalize_key(key: str, n_qubits: int) -> str:
    cleaned = "".join(str(key).split())
    if len(cleaned) != n_qubits or set(cleaned) - {"0", "1"}:
        raise ValueError(f"bitstring inválida para {n_qubits} qubits: {key!r}")
    return cleaned


def _bit(key: str, index: int, n_qubits: int) -> int:
    """Qiskit: o caractere mais à direita é o qubit 0."""
    return int(key[n_qubits - 1 - index])


def _wilson(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total deve ser positivo")
    proportion = successes / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2.0 * total)) / denominator
    half = (
        z
        * math.sqrt(
            proportion * (1.0 - proportion) / total
            + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return max(0.0, centre - half), min(1.0, centre + half)


def calibration_correlations(counts: dict, qubits: Iterable[int]) -> dict:
    """Estima marginais, co-ocorrências e `phi` de counts preparados em |0>."""
    qubits = [int(qubit) for qubit in qubits]
    if len(qubits) < 2:
        raise ValueError("correlação exige ao menos dois qubits")
    if len(set(qubits)) != len(qubits):
        raise ValueError("qubits não podem repetir")
    n = len(qubits)
    parsed = []
    total = 0
    for key, value in counts.items():
        key = _normalize_key(key, n)
        value = int(value)
        if value < 0:
            raise ValueError("counts não podem ser negativos")
        if value == 0:
            continue
        parsed.append((key, value))
        total += value
    if total <= 0:
        raise ValueError("counts vazios")

    def probability(predicate) -> float:
        return sum(value for key, value in parsed if predicate(key)) / total

    marginals = [
        probability(lambda key, index=index: _bit(key, index, n) == 1)
        for index in range(n)
    ]
    all_zero_count = sum(
        value for key, value in parsed if set(key) == {"0"}
    )
    all_zero = all_zero_count / total
    any_error = 1.0 - all_zero
    independent_no_error = float(np.prod([1.0 - p for p in marginals]))
    independent_any_error = 1.0 - independent_no_error

    pairs = []
    for left in range(n):
        for right in range(left + 1, n):
            observed = probability(
                lambda key, a=left, b=right: (
                    _bit(key, a, n) == 1 and _bit(key, b, n) == 1
                )
            )
            expected = marginals[left] * marginals[right]
            covariance = observed - expected
            denominator = math.sqrt(
                marginals[left]
                * (1.0 - marginals[left])
                * marginals[right]
                * (1.0 - marginals[right])
            )
            phi = covariance / denominator if denominator > 1e-15 else 0.0
            pairs.append({
                "left": qubits[left],
                "right": qubits[right],
                "marginal_left": marginals[left],
                "marginal_right": marginals[right],
                "observed_joint": observed,
                "independent_joint": expected,
                "covariance": covariance,
                "phi": float(phi),
                "phi_defined": bool(denominator > 1e-15),
            })

    lower = max(marginals)
    for pair in pairs:
        lower = max(
            lower,
            pair["marginal_left"]
            + pair["marginal_right"]
            - pair["observed_joint"],
        )
    upper = min(1.0, float(sum(marginals)))
    ci_low, ci_high = _wilson(total - all_zero_count, total)
    phi_values = [pair["phi"] for pair in pairs if pair["phi_defined"]]
    max_abs_phi = max((abs(value) for value in phi_values), default=0.0)
    mean_phi = float(np.mean(phi_values)) if phi_values else 0.0
    if max_abs_phi < 0.01:
        correlation_class = "near_zero"
    elif mean_phi > 0:
        correlation_class = "positive"
    elif mean_phi < 0:
        correlation_class = "negative"
    else:
        correlation_class = "mixed"

    return {
        "schema_version": 1,
        "qubits": qubits,
        "n_qubits": n,
        "shots": total,
        "marginals": marginals,
        "pairs": pairs,
        "all_zero_probability": all_zero,
        "any_error_probability": any_error,
        "any_error_ci95": [ci_low, ci_high],
        "independent_no_error": independent_no_error,
        "independent_any_error": independent_any_error,
        "delta_any_error": any_error - independent_any_error,
        "delta_no_error": all_zero - independent_no_error,
        "bounds": {
            "lower": float(lower),
            "upper": float(upper),
            "contain_observed": bool(lower - 1e-12 <= any_error <= upper + 1e-12),
            "method": "primeira desigualdade de Bonferroni / union bound",
        },
        "max_abs_phi": float(max_abs_phi),
        "mean_phi": mean_phi,
        "correlation_class": correlation_class,
        "limits": LIMITS,
        "hardware_executed": False,
        "rates_measured": False,
    }


def simulate_correlated_readout(
    *,
    n_qubits: int = 4,
    marginals: Iterable[float] | None = None,
    rho: float = 0.5,
    shots: int = 20000,
    seed: int = 0,
) -> dict[str, int]:
    """Gera counts com fator latente comum; `rho=0` é independência."""
    n_qubits = int(n_qubits)
    if n_qubits < 2:
        raise ValueError("n_qubits deve ser >= 2")
    if int(shots) < 1:
        raise ValueError("shots deve ser >= 1")
    if not 0.0 <= float(rho) <= 1.0:
        raise ValueError("rho deve estar em [0,1]")
    if marginals is None:
        marginals = [0.08] * n_qubits
    marginals = [float(value) for value in marginals]
    if len(marginals) != n_qubits:
        raise ValueError("marginais devem ter n_qubits valores")
    if any(value < 0.0 or value > 1.0 for value in marginals):
        raise ValueError("marginais devem estar em [0,1]")
    rng = np.random.default_rng(int(seed))
    common = rng.normal(size=(int(shots), 1))
    independent = rng.normal(size=(int(shots), n_qubits))
    latent = math.sqrt(float(rho)) * common + math.sqrt(1.0 - float(rho)) * independent
    thresholds = np.array([norm.ppf(1.0 - value) for value in marginals])
    flips = latent > thresholds
    counts: dict[str, int] = {}
    for row in flips:
        key = "".join("1" if bit else "0" for bit in row[::-1])
        counts[key] = counts.get(key, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Dispositivo e custo de layout
# ---------------------------------------------------------------------------


def make_device(
    *,
    n: int,
    edges: Iterable,
    readout: Iterable[float],
    crosstalk: Iterable | None = None,
) -> dict:
    n = int(n)
    if n < 2:
        raise ValueError("n deve ser >= 2")
    readout = [float(value) for value in readout]
    if len(readout) != n:
        raise ValueError("readout deve ter n valores")
    if any(value < 0.0 or value > 1.0 for value in readout):
        raise ValueError("readout deve estar em [0,1]")
    edge_map: dict[tuple[int, int], float] = {}
    for edge in edges:
        values = list(edge)
        if len(values) == 2:
            left, right = values
            error = 0.0
        elif len(values) == 3:
            left, right, error = values
        else:
            raise ValueError("cada edge deve ter 2 ou 3 valores")
        left, right = int(left), int(right)
        error = float(error)
        if left == right or not (0 <= left < n and 0 <= right < n):
            raise ValueError("edge inválida")
        if error < 0.0:
            raise ValueError("erro de edge deve ser >= 0")
        edge_map[(min(left, right), max(left, right))] = min(
            error,
            edge_map.get((min(left, right), max(left, right)), INF),
        )
    crosstalk_list = []
    for pair in crosstalk or []:
        values = list(pair)
        if len(values) != 3:
            raise ValueError("crosstalk deve ter (i,j,penalidade)")
        left, right, penalty = int(values[0]), int(values[1]), float(values[2])
        if left == right or not (0 <= left < n and 0 <= right < n):
            raise ValueError("par de crosstalk inválido")
        if penalty < 0.0:
            raise ValueError("penalidade deve ser >= 0")
        crosstalk_list.append([min(left, right), max(left, right), penalty])
    return {
        "n": n,
        "edges": [
            [left, right, error]
            for (left, right), error in sorted(edge_map.items())
        ],
        "readout": readout,
        "crosstalk": crosstalk_list,
    }


def _edge_map(device: dict) -> dict[tuple[int, int], float]:
    return {
        (int(left), int(right)): float(error)
        for left, right, error in device["edges"]
    }


def _cross_map(device: dict) -> dict[tuple[int, int], float]:
    return {
        (int(left), int(right)): float(penalty)
        for left, right, penalty in device.get("crosstalk", [])
    }


def shortest_paths(device: dict) -> tuple[list[list[float]], list[list[int]]]:
    n = int(device["n"])
    distance = [[INF] * n for _ in range(n)]
    hops = [[10**9] * n for _ in range(n)]
    for index in range(n):
        distance[index][index] = 0.0
        hops[index][index] = 0
    for (left, right), error in _edge_map(device).items():
        distance[left][right] = min(distance[left][right], error)
        distance[right][left] = distance[left][right]
        hops[left][right] = 1
        hops[right][left] = 1
    for middle in range(n):
        for left in range(n):
            for right in range(n):
                candidate = distance[left][middle] + distance[middle][right]
                candidate_hops = hops[left][middle] + hops[middle][right]
                if candidate < distance[left][right] - 1e-15:
                    distance[left][right] = candidate
                    hops[left][right] = candidate_hops
                elif (
                    abs(candidate - distance[left][right]) <= 1e-15
                    and candidate_hops < hops[left][right]
                ):
                    hops[left][right] = candidate_hops
    return distance, hops


def _corr_value(correlation, left: int, right: int) -> float:
    if correlation is None:
        return 0.0
    if isinstance(correlation, dict):
        for key in ((left, right), (right, left), f"{left}-{right}", f"{right}-{left}"):
            if key in correlation:
                return float(correlation[key])
        return 0.0
    return float(correlation[left][right])


def layout_cost(
    layout: Iterable[int],
    device: dict,
    interactions: Iterable,
    *,
    measurement_weights: Iterable[float] | None = None,
    correlation=None,
    correlation_pairs: Iterable | None = None,
    correlation_weight: float = 1.0,
    swap_penalty: float = 1.0,
) -> dict:
    layout = tuple(int(value) for value in layout)
    n_logical = len(layout)
    if len(set(layout)) != n_logical:
        raise ValueError("layout deve ser injetivo")
    if any(value < 0 or value >= int(device["n"]) for value in layout):
        raise ValueError("layout fora do dispositivo")
    interactions = [
        (int(left), int(right), float(weight))
        for left, right, weight in interactions
    ]
    if any(
        left < 0 or right < 0 or left >= n_logical or right >= n_logical
        for left, right, _ in interactions
    ):
        raise ValueError("interação fora do circuito lógico")
    if measurement_weights is None:
        measurement_weights = [1.0] * n_logical
    measurement_weights = [float(value) for value in measurement_weights]
    if len(measurement_weights) != n_logical:
        raise ValueError("measurement_weights deve ter n_logical valores")
    distance, hops = shortest_paths(device)

    gate_cost = 0.0
    for left, right, weight in interactions:
        physical_left, physical_right = layout[left], layout[right]
        if distance[physical_left][physical_right] == INF:
            gate_cost = INF
            break
        gate_cost += weight * (
            distance[physical_left][physical_right]
            + swap_penalty * max(0, hops[physical_left][physical_right] - 1)
        )
    readout_cost = sum(
        measurement_weights[index] * device["readout"][layout[index]]
        for index in range(n_logical)
    )
    activity = [0.0] * int(device["n"])
    for left, right, weight in interactions:
        activity[layout[left]] += weight
        activity[layout[right]] += weight
    crosstalk_cost = sum(
        penalty * min(activity[left], activity[right])
        for (left, right), penalty in _cross_map(device).items()
    )
    if correlation_pairs is None:
        pair_set = {
            (min(left, right), max(left, right))
            for left, right, weight in interactions
            if weight > 0.0
        }
    else:
        pair_set = {
            (min(int(left), int(right)), max(int(left), int(right)))
            for left, right in correlation_pairs
        }
    correlation_cost = 0.0
    for left, right in sorted(pair_set):
        if left == right:
            continue
        if left < 0 or right >= n_logical:
            raise ValueError("par de correlação fora do circuito lógico")
        if measurement_weights[left] <= 0.0 or measurement_weights[right] <= 0.0:
            continue
        phi = _corr_value(correlation, layout[left], layout[right])
        if phi > 0.0:
            correlation_cost += (
                float(correlation_weight)
                * phi
                * measurement_weights[left]
                * measurement_weights[right]
            )
    total = gate_cost + readout_cost + crosstalk_cost + correlation_cost
    return {
        "total": float(total),
        "gate": float(gate_cost),
        "readout": float(readout_cost),
        "crosstalk": float(crosstalk_cost),
        "correlation": float(correlation_cost),
        "layout": list(layout),
    }


def _weighted_degree(interactions, n_logical: int) -> list[float]:
    degree = [0.0] * n_logical
    for left, right, weight in interactions:
        degree[left] += weight
        degree[right] += weight
    return degree


def greedy_layout(
    device: dict,
    interactions: Iterable,
    *,
    measurement_weights: Iterable[float] | None = None,
    correlation=None,
    correlation_pairs: Iterable | None = None,
    correlation_weight: float = 1.0,
    swap_penalty: float = 1.0,
) -> tuple[int, ...]:
    interactions = [
        (int(left), int(right), float(weight))
        for left, right, weight in interactions
    ]
    n_logical = max(
        [max(left, right) for left, right, _ in interactions] + [-1]
    ) + 1
    if measurement_weights is None:
        measurement_weights = [1.0] * n_logical
    measurement_weights = [float(value) for value in measurement_weights]
    distance, hops = shortest_paths(device)
    degree = _weighted_degree(interactions, n_logical)
    if correlation_pairs is None:
        pair_set = {
            (min(left, right), max(left, right))
            for left, right, weight in interactions
            if weight > 0.0
        }
    else:
        pair_set = {
            (min(int(left), int(right)), max(int(left), int(right)))
            for left, right in correlation_pairs
        }
    order = sorted(range(n_logical), key=lambda index: (-degree[index], index))
    assigned: dict[int, int] = {}
    layout = [None] * n_logical
    for logical in order:
        best_physical = None
        best_cost = INF
        for physical in range(int(device["n"])):
            if physical in assigned.values():
                continue
            cost = measurement_weights[logical] * device["readout"][physical]
            for other_logical, other_physical in assigned.items():
                weight = 0.0
                for left, right, value in interactions:
                    if {left, right} == {logical, other_logical}:
                        weight += value
                if weight > 0.0:
                    cost += weight * (
                        distance[physical][other_physical]
                        + swap_penalty
                        * max(0, hops[physical][other_physical] - 1)
                    )
                pair = (min(logical, other_logical), max(logical, other_logical))
                if pair in pair_set:
                    phi = _corr_value(correlation, physical, other_physical)
                    if phi > 0.0:
                        cost += (
                            float(correlation_weight)
                            * phi
                            * measurement_weights[logical]
                            * measurement_weights[other_logical]
                        )
            if cost < best_cost - 1e-15:
                best_cost = cost
                best_physical = physical
        if best_physical is None:
            raise ValueError("dispositivo pequeno para o circuito lógico")
        layout[logical] = best_physical
        assigned[logical] = best_physical
    return tuple(int(value) for value in layout)


def two_opt(
    layout: Iterable[int],
    device: dict,
    interactions: Iterable,
    *,
    measurement_weights: Iterable[float] | None = None,
    correlation=None,
    correlation_pairs: Iterable | None = None,
    correlation_weight: float = 1.0,
    swap_penalty: float = 1.0,
    max_passes: int = 20,
) -> tuple[int, ...]:
    current = tuple(int(value) for value in layout)
    cost = layout_cost(
        current,
        device,
        interactions,
        measurement_weights=measurement_weights,
        correlation=correlation,
        correlation_pairs=correlation_pairs,
        correlation_weight=correlation_weight,
        swap_penalty=swap_penalty,
    )["total"]
    for _ in range(int(max_passes)):
        improved = False
        for left in range(len(current)):
            for right in range(left + 1, len(current)):
                candidate = list(current)
                candidate[left], candidate[right] = candidate[right], candidate[left]
                candidate_cost = layout_cost(
                    candidate,
                    device,
                    interactions,
                    measurement_weights=measurement_weights,
                    correlation=correlation,
                    correlation_pairs=correlation_pairs,
                    correlation_weight=correlation_weight,
                    swap_penalty=swap_penalty,
                )["total"]
                if candidate_cost < cost - 1e-12:
                    current = tuple(candidate)
                    cost = candidate_cost
                    improved = True
        if not improved:
            break
    return current


def exhaustive_layout(
    device: dict,
    interactions: Iterable,
    *,
    measurement_weights: Iterable[float] | None = None,
    correlation=None,
    correlation_pairs: Iterable | None = None,
    correlation_weight: float = 1.0,
    swap_penalty: float = 1.0,
    max_qubits: int = 8,
) -> dict:
    interactions = [
        (int(left), int(right), float(weight))
        for left, right, weight in interactions
    ]
    n_logical = max(
        [max(left, right) for left, right, _ in interactions] + [-1]
    ) + 1
    if n_logical > int(max_qubits):
        raise ValueError(f"exaustão limitada a {max_qubits} qubits lógicos")
    best_layout = None
    best_cost = INF
    for permutation in itertools.permutations(range(int(device["n"])), n_logical):
        result = layout_cost(
            permutation,
            device,
            interactions,
            measurement_weights=measurement_weights,
            correlation=correlation,
            correlation_pairs=correlation_pairs,
            correlation_weight=correlation_weight,
            swap_penalty=swap_penalty,
        )
        if result["total"] < best_cost - 1e-15:
            best_cost = result["total"]
            best_layout = permutation
    return {"layout": list(best_layout), "cost": float(best_cost)}


def optimize_layout(
    device: dict,
    interactions: Iterable,
    *,
    measurement_weights: Iterable[float] | None = None,
    correlation=None,
    correlation_pairs: Iterable | None = None,
    correlation_weight: float = 1.0,
    swap_penalty: float = 1.0,
    exhaustive: bool = True,
) -> dict:
    shared = {
        "measurement_weights": measurement_weights,
        "correlation": correlation,
        "correlation_pairs": correlation_pairs,
        "correlation_weight": correlation_weight,
        "swap_penalty": swap_penalty,
    }
    greedy = greedy_layout(device, interactions, **shared)
    polished = two_opt(greedy, device, interactions, **shared)
    greedy_cost = layout_cost(greedy, device, interactions, **shared)
    polished_cost = layout_cost(polished, device, interactions, **shared)
    payload = {
        "greedy": {
            "layout": list(greedy),
            "cost": float(greedy_cost["total"]),
            "breakdown": greedy_cost,
        },
        "two_opt": {
            "layout": list(polished),
            "cost": float(polished_cost["total"]),
            "breakdown": polished_cost,
        },
    }
    if exhaustive:
        payload["exhaustive"] = exhaustive_layout(
            device, interactions, **shared
        )
    return payload


# ---------------------------------------------------------------------------
# Contraprovas
# ---------------------------------------------------------------------------


def _random_device(n: int, rng: np.random.Generator) -> dict:
    edges = []
    for node in range(1, n):
        parent = int(rng.integers(0, node))
        edges.append((parent, node, float(rng.uniform(0.001, 0.02))))
    for left in range(n):
        for right in range(left + 1, n):
            if (left, right) not in {
                (min(a, b), max(a, b)) for a, b, _ in edges
            } and rng.random() < 0.25:
                edges.append((left, right, float(rng.uniform(0.001, 0.02))))
    readout = [float(rng.uniform(0.01, 0.1)) for _ in range(n)]
    return make_device(n=n, edges=edges, readout=readout)


def _random_interactions(n: int, rng: np.random.Generator) -> list:
    interactions = []
    for left in range(n):
        for right in range(left + 1, n):
            if rng.random() < 0.6:
                interactions.append((left, right, float(rng.integers(1, 5))))
    if not interactions:
        interactions = [(0, 1, 1.0)]
    return interactions


def find_greedy_counterexample(
    *, n: int = 5, trials: int = 200, seed: int = 0
) -> dict:
    rng = np.random.default_rng(int(seed))
    for _ in range(int(trials)):
        device = _random_device(n, rng)
        interactions = _random_interactions(n, rng)
        greedy = greedy_layout(device, interactions)
        optimal = exhaustive_layout(device, interactions)
        greedy_cost = layout_cost(greedy, device, interactions)["total"]
        gap = greedy_cost - optimal["cost"]
        if gap > 1e-9:
            return {
                "found": True,
                "n": n,
                "device": device,
                "interactions": interactions,
                "greedy_layout": list(greedy),
                "optimal_layout": optimal["layout"],
                "greedy_cost": float(greedy_cost),
                "optimal_cost": float(optimal["cost"]),
                "gap": float(gap),
                "limits": LAYOUT_LIMITS,
                "hardware_executed": False,
            }
    return {
        "found": False,
        "trials": int(trials),
        "limits": LAYOUT_LIMITS,
        "hardware_executed": False,
    }


def find_regime_reversal(
    *, n: int = 5, trials: int = 100, seed: int = 0
) -> dict:
    """Arranjo ótimo em A pode ser ruim em B; inclui contraste determinístico."""
    n = int(n)
    if n < 4:
        raise ValueError("n deve ser >= 4")
    edges_a = [[0, 1, 0.001]]
    edges_a += [[index, index + 1, 0.05] for index in range(1, n - 1)]
    edges_a += [[0, n - 1, 0.05]]
    edges_b = [[index, index + 1, 0.05] for index in range(0, n - 2)]
    edges_b += [[n - 2, n - 1, 0.001]]
    edges_b += [[0, n - 1, 0.05]]
    device_a = make_device(n=n, edges=edges_a, readout=[0.01] * n)
    device_b = make_device(n=n, edges=edges_b, readout=[0.01] * n)
    interactions = [(0, 1, 10.0), (n - 2, n - 1, 1.0)]
    layout_a = exhaustive_layout(device_a, interactions)["layout"]
    layout_b = exhaustive_layout(device_b, interactions)["layout"]
    cost_a_on_b = layout_cost(layout_a, device_b, interactions)["total"]
    cost_b_on_b = layout_cost(layout_b, device_b, interactions)["total"]
    gap = cost_a_on_b - cost_b_on_b
    best = {
        "found": gap > 1e-9,
        "n": n,
        "device_a": device_a,
        "device_b": device_b,
        "interactions": interactions,
        "layout_optimal_on_a": layout_a,
        "layout_optimal_on_b": layout_b,
        "cost_optimal_on_a_on_b": float(cost_a_on_b),
        "cost_optimal_on_b_on_b": float(cost_b_on_b),
        "gap": float(gap),
        "gap_relative": float(gap / cost_b_on_b) if cost_b_on_b > 0 else None,
        "construction": "contraste determinístico de aresta boa",
        "limits": LAYOUT_LIMITS,
        "hardware_executed": False,
    }
    rng = np.random.default_rng(int(seed))
    for _ in range(int(trials)):
        topology = _random_device(n, rng)
        random_a = make_device(
            n=n,
            edges=topology["edges"],
            readout=topology["readout"],
            crosstalk=topology["crosstalk"],
        )
        random_b = make_device(
            n=n,
            edges=topology["edges"],
            readout=[float(rng.uniform(0.01, 0.1)) for _ in range(n)],
            crosstalk=topology["crosstalk"],
        )
        random_interactions = _random_interactions(n, rng)
        candidate_a = exhaustive_layout(random_a, random_interactions)["layout"]
        candidate_b = exhaustive_layout(random_b, random_interactions)["layout"]
        candidate_cost_a = layout_cost(
            candidate_a, random_b, random_interactions
        )["total"]
        candidate_cost_b = layout_cost(
            candidate_b, random_b, random_interactions
        )["total"]
        candidate_gap = candidate_cost_a - candidate_cost_b
        if candidate_gap > best["gap"]:
            best = {
                "found": True,
                "n": n,
                "device_a": random_a,
                "device_b": random_b,
                "interactions": random_interactions,
                "layout_optimal_on_a": candidate_a,
                "layout_optimal_on_b": candidate_b,
                "cost_optimal_on_a_on_b": float(candidate_cost_a),
                "cost_optimal_on_b_on_b": float(candidate_cost_b),
                "gap": float(candidate_gap),
                "gap_relative": (
                    float(candidate_gap / candidate_cost_b)
                    if candidate_cost_b > 0
                    else None
                ),
                "construction": "busca aleatória",
                "limits": LAYOUT_LIMITS,
                "hardware_executed": False,
            }
    return best


def correlation_blind_counterexample() -> dict:
    """Arranjo cego à correlação vs. arranjo que evita pares correlacionados."""
    n = 4
    edges = [
        (left, right, 0.001)
        for left in range(n)
        for right in range(left + 1, n)
    ]
    device = make_device(
        n=n, edges=edges, readout=[0.08] * n
    )
    interactions = [(0, 1, 1.0), (2, 3, 1.0)]
    correlation = {
        (0, 1): 0.6,
        (2, 3): 0.6,
    }
    blind = (0, 1, 2, 3)
    aware = (0, 2, 1, 3)
    pairs = [(0, 1), (2, 3)]
    blind_cost = layout_cost(
        blind,
        device,
        interactions,
        correlation=correlation,
        correlation_pairs=pairs,
    )
    aware_cost = layout_cost(
        aware,
        device,
        interactions,
        correlation=correlation,
        correlation_pairs=pairs,
    )
    return {
        "found": bool(blind_cost["total"] > aware_cost["total"] + 1e-9),
        "device": device,
        "interactions": interactions,
        "correlation": [[left, right, value] for (left, right), value in correlation.items()],
        "blind_layout": list(blind),
        "aware_layout": list(aware),
        "blind_cost": blind_cost,
        "aware_cost": aware_cost,
        "delta": float(blind_cost["total"] - aware_cost["total"]),
        "limits": LAYOUT_LIMITS,
        "hardware_executed": False,
    }
