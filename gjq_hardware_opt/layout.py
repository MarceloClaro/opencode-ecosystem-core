#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Layout noise-aware para hardware com acoplamentos e erros declarados (R1109).

O layout não é um passe do Qiskit: ele usa o grafo de interação do circuito e
os erros do perfil para escolher uma região física. O resultado é passado ao
transpilador como ``initial_layout``.
"""
from __future__ import annotations

import heapq
import itertools
import math
from collections import Counter
from dataclasses import dataclass

from qiskit import QuantumCircuit

from .profile import HardwareProfile

EXACT_MAX_PERMUTATIONS = 200_000
TWO_OPT_MAX_ITER = 100


@dataclass
class LayoutResult:
    layout: list[int]
    physical_region: list[int]
    cost: float
    trivial_cost: float
    method: str
    used_logical: list[int]

    def to_dict(self) -> dict:
        return {
            "layout": list(self.layout),
            "physical_region": list(self.physical_region),
            "cost": self.cost,
            "trivial_cost": self.trivial_cost,
            "method": self.method,
            "used_logical": list(self.used_logical),
        }


def circuit_interactions(
    circuit: QuantumCircuit,
) -> tuple[Counter[int], Counter[int], Counter[tuple[int, int]]]:
    """Conta operações 1q, medições e arestas 2q por qubit lógico."""
    oneq: Counter[int] = Counter()
    measure: Counter[int] = Counter()
    edges: Counter[tuple[int, int]] = Counter()
    for instruction in circuit.data:
        name = instruction.operation.name
        if name in {"barrier", "delay", "reset"}:
            continue
        qubits = [circuit.find_bit(q).index for q in instruction.qubits]
        if name == "measure":
            for q in qubits:
                measure[q] += 1
            continue
        if len(qubits) == 1:
            oneq[qubits[0]] += 1
        elif len(qubits) == 2:
            a, b = sorted(qubits)
            edges[(a, b)] += 1
        elif len(qubits) > 2:
            for a, b in itertools.combinations(sorted(qubits), 2):
                edges[(a, b)] += 1
    return oneq, measure, edges


def _adjacency(profile: HardwareProfile) -> dict[int, set[int]]:
    adjacency: dict[int, set[int]] = {q: set() for q in range(profile.num_qubits)}
    for a, b in profile.coupling_map:
        adjacency[a].add(b)
        adjacency[b].add(a)
    return adjacency


def _pair_costs(profile: HardwareProfile) -> dict[tuple[int, int], float]:
    costs: dict[tuple[int, int], float] = {}
    for a, b in profile.coupling_map:
        costs[(a, b)] = profile.pair_error(a, b)
        costs.setdefault((b, a), profile.pair_error(b, a))
    return costs


def _dijkstra(
    start: int,
    adjacency: dict[int, set[int]],
    pair_costs: dict[tuple[int, int], float],
) -> dict[int, float]:
    distances = {start: 0.0}
    heap: list[tuple[float, int]] = [(0.0, start)]
    while heap:
        distance, node = heapq.heappop(heap)
        if distance > distances.get(node, math.inf):
            continue
        for neighbor in adjacency[node]:
            weight = pair_costs.get(
                (node, neighbor),
                pair_costs.get((neighbor, node), 1.0),
            )
            candidate = distance + weight
            if candidate < distances.get(neighbor, math.inf):
                distances[neighbor] = candidate
                heapq.heappush(heap, (candidate, neighbor))
    return distances


def _all_pairs(
    profile: HardwareProfile,
    adjacency: dict[int, set[int]],
    pair_costs: dict[tuple[int, int], float],
) -> dict[int, dict[int, float]]:
    return {
        q: _dijkstra(q, adjacency, pair_costs)
        for q in range(profile.num_qubits)
    }


def _mapping_cost(
    assign: dict[int, int],
    oneq: Counter[int],
    measure: Counter[int],
    edges: Counter[tuple[int, int]],
    qubit_cost: dict[int, float],
    readout_cost: dict[int, float],
    path_cost: dict[int, dict[int, float]],
) -> float:
    total = 0.0
    for logical, physical in assign.items():
        total += oneq.get(logical, 0) * qubit_cost[physical]
        total += measure.get(logical, 0) * readout_cost[physical]
    for (u, v), weight in edges.items():
        pu, pv = assign[u], assign[v]
        distance = path_cost.get(pu, {}).get(pv, math.inf)
        if math.isinf(distance):
            return math.inf
        total += weight * distance
    return total


def _degrees(edges: Counter[tuple[int, int]]) -> dict[int, float]:
    degree: dict[int, float] = {}
    for (a, b), weight in edges.items():
        degree[a] = degree.get(a, 0.0) + weight
        degree[b] = degree.get(b, 0.0) + weight
    return degree


def _exact_assign(
    used: list[int],
    degree: dict[int, float],
    physical_qubits: list[int],
    oneq: Counter[int],
    measure: Counter[int],
    edges: Counter[tuple[int, int]],
    qubit_cost: dict[int, float],
    readout_cost: dict[int, float],
    path_cost: dict[int, dict[int, float]],
) -> dict[int, int] | None:
    if math.perm(len(physical_qubits), len(used)) > EXACT_MAX_PERMUTATIONS:
        return None
    ordered = sorted(used, key=lambda q: (-degree.get(q, 0.0), q))
    best_cost = math.inf
    best: dict[int, int] | None = None
    for permutation in itertools.permutations(physical_qubits, len(ordered)):
        assign = dict(zip(ordered, permutation))
        cost = _mapping_cost(
            assign, oneq, measure, edges, qubit_cost, readout_cost, path_cost
        )
        if cost < best_cost:
            best_cost = cost
            best = assign
    return best


def _greedy_assign(
    used: list[int],
    degree: dict[int, float],
    physical_qubits: list[int],
    oneq: Counter[int],
    measure: Counter[int],
    edges: Counter[tuple[int, int]],
    qubit_cost: dict[int, float],
    readout_cost: dict[int, float],
    path_cost: dict[int, dict[int, float]],
) -> dict[int, int]:
    order = sorted(used, key=lambda q: (-degree.get(q, 0.0), q))
    assign: dict[int, int] = {}
    available = set(physical_qubits)
    assigned_neighbors: dict[int, list[tuple[int, int]]] = {q: [] for q in used}
    for a, b in edges:
        assigned_neighbors[a].append((b, edges[(a, b)]))
        assigned_neighbors[b].append((a, edges[(a, b)]))
    for logical in order:
        best_physical = None
        best_cost = math.inf
        for physical in sorted(available):
            cost = (
                oneq.get(logical, 0) * qubit_cost[physical]
                + measure.get(logical, 0) * readout_cost[physical]
            )
            for neighbor, weight in assigned_neighbors[logical]:
                if neighbor in assign:
                    distance = path_cost.get(physical, {}).get(assign[neighbor], math.inf)
                    cost += weight * distance
            if cost < best_cost:
                best_cost = cost
                best_physical = physical
        if best_physical is None:
            raise ValueError("não foi possível atribuir um qubit físico")
        assign[logical] = best_physical
        available.remove(best_physical)
    return assign


def _two_opt(
    assign: dict[int, int],
    oneq: Counter[int],
    measure: Counter[int],
    edges: Counter[tuple[int, int]],
    qubit_cost: dict[int, float],
    readout_cost: dict[int, float],
    path_cost: dict[int, dict[int, float]],
) -> dict[int, int]:
    current = dict(assign)
    current_cost = _mapping_cost(
        current, oneq, measure, edges, qubit_cost, readout_cost, path_cost
    )
    keys = sorted(current)
    for _ in range(TWO_OPT_MAX_ITER):
        improved = False
        for i, a in enumerate(keys):
            for b in keys[i + 1 :]:
                candidate = dict(current)
                candidate[a], candidate[b] = candidate[b], candidate[a]
                cost = _mapping_cost(
                    candidate, oneq, measure, edges, qubit_cost, readout_cost, path_cost
                )
                if cost + 1e-15 < current_cost:
                    current = candidate
                    current_cost = cost
                    improved = True
        if not improved:
            break
    return current


def _components(region: set[int], adjacency: dict[int, set[int]]) -> list[set[int]]:
    remaining = set(region)
    components: list[set[int]] = []
    while remaining:
        start = next(iter(remaining))
        component = {start}
        stack = [start]
        remaining.remove(start)
        while stack:
            node = stack.pop()
            for neighbor in adjacency[node]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)
        components.append(component)
    return components


def _bfs_path(
    start: int,
    targets: set[int],
    adjacency: dict[int, set[int]],
) -> list[int] | None:
    queue = [start]
    previous: dict[int, int | None] = {start: None}
    index = 0
    while index < len(queue):
        node = queue[index]
        index += 1
        if node in targets:
            path = []
            current: int | None = node
            while current is not None:
                path.append(current)
                current = previous[current]
            return list(reversed(path))
        for neighbor in adjacency[node]:
            if neighbor not in previous:
                previous[neighbor] = node
                queue.append(neighbor)
    return None


def _connect_region(region: set[int], adjacency: dict[int, set[int]]) -> set[int]:
    connected = set(region)
    while True:
        components = _components(connected, adjacency)
        if len(components) <= 1:
            return connected
        first, second = components[0], components[1]
        best_path: list[int] | None = None
        for start in sorted(first):
            path = _bfs_path(start, second, adjacency)
            if path is not None and (best_path is None or len(path) < len(best_path)):
                best_path = path
        if best_path is None:
            return connected
        connected.update(best_path)


def noise_aware_layout(
    circuit: QuantumCircuit,
    profile: HardwareProfile,
    seed: int = 42,
) -> LayoutResult:
    """Escolhe um layout lógico -> físico e uma região física conectada."""
    del seed  # determinístico; mantido para assinatura e reprodutibilidade futura
    physical_qubits = list(profile.operational_qubits) or list(range(profile.num_qubits))
    if circuit.num_qubits > len(physical_qubits):
        raise ValueError(
            f"circuito usa {circuit.num_qubits} qubits, mas o perfil tem "
            f"{len(physical_qubits)} qubits operacionais"
        )
    oneq, measure, edges = circuit_interactions(circuit)
    used = sorted(set(oneq) | set(measure) | {q for edge in edges for q in edge})
    if not used:
        layout = list(range(circuit.num_qubits))
        return LayoutResult(
            layout=layout,
            physical_region=layout,
            cost=0.0,
            trivial_cost=0.0,
            method="identity",
            used_logical=[],
        )

    adjacency = _adjacency(profile)
    pair_costs = _pair_costs(profile)
    path_cost = _all_pairs(profile, adjacency, pair_costs)
    qubit_cost = {q: profile.qubit_error(q) for q in physical_qubits}
    readout_cost = {q: profile.readout_error[q] for q in physical_qubits}
    degree = _degrees(edges)
    trivial_layout = physical_qubits[: circuit.num_qubits]
    trivial_assign = {q: trivial_layout[q] for q in used}
    trivial_cost = _mapping_cost(
        trivial_assign, oneq, measure, edges, qubit_cost, readout_cost, path_cost
    )
    if not math.isfinite(trivial_cost):
        raise ValueError(
            "não há região operacional conectada suficiente para o circuito"
        )

    assign = _exact_assign(
        used,
        degree,
        physical_qubits,
        oneq,
        measure,
        edges,
        qubit_cost,
        readout_cost,
        path_cost,
    )
    method = "exact"
    if assign is None:
        method = "greedy"
        assign = _greedy_assign(
            used,
            degree,
            physical_qubits,
            oneq,
            measure,
            edges,
            qubit_cost,
            readout_cost,
            path_cost,
        )
        assign = _two_opt(
            assign, oneq, measure, edges, qubit_cost, readout_cost, path_cost
        )

    cost = _mapping_cost(
        assign, oneq, measure, edges, qubit_cost, readout_cost, path_cost
    )
    if not math.isfinite(cost) or cost > trivial_cost:
        assign = trivial_assign
        cost = trivial_cost
        method = "trivial_fallback"

    region = _connect_region(set(assign.values()), adjacency)
    layout: list[int | None] = [None] * circuit.num_qubits
    for logical, physical in assign.items():
        layout[logical] = physical
    remaining = sorted(
        (p for p in physical_qubits if p not in set(assign.values())),
        key=lambda p: (qubit_cost[p], p),
    )
    for logical in range(circuit.num_qubits):
        if layout[logical] is None:
            layout[logical] = remaining.pop(0)
    final_layout = [int(p) for p in layout]
    region.update(final_layout)
    return LayoutResult(
        layout=final_layout,
        physical_region=sorted(region),
        cost=float(cost),
        trivial_cost=float(trivial_cost),
        method=method,
        used_logical=used,
    )
