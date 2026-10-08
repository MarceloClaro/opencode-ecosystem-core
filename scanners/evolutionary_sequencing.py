"""Roadmap condicional de capacidades (R665), sem execução ou persistência.

Reutiliza a orientação de pré-requisitos de R483/R485. O grafo declarado é
um modelo de planejamento: evidência fornecida é preservada, não auditada aqui,
e não transforma uma hipótese causal em necessidade científica demonstrada.
"""

from __future__ import annotations

import math
import json
from typing import Any

_EXECUTED_STATES = frozenset({"executed", "external", "external_validated", "externally_validated"})


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError(f"{label} deve ser texto não vazio com até 256 caracteres")
    return value.strip()


def _estimate(value: Any, label: str, maximum: float | None = None) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} deve ser número finito não negativo")
    result = float(value)
    if not math.isfinite(result) or result < 0 or (maximum is not None and result > maximum):
        raise ValueError(f"{label} fora dos limites")
    return result


def _evidence(value: Any) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > 128:
        raise ValueError("evidence deve ser lista limitada de referências")
    if any(not ((isinstance(v, str) and v.strip()) or (isinstance(v, dict) and v)) for v in value):
        raise ValueError("referência de evidence vazia ou inválida")
    try:
        serialized = [json.dumps(v, ensure_ascii=False, sort_keys=True, allow_nan=False) for v in value]
    except (ValueError, TypeError, RecursionError) as exc:
        raise ValueError("evidence deve conter referências JSON finitas") from exc
    if any(len(v) > 16384 for v in serialized):
        raise ValueError("referência de evidence excede o limite de leitura")
    return [json.loads(v) for v in sorted(set(serialized))]


def _known_sum(values: list[float | None]) -> float | None:
    if any(v is None for v in values):
        return None
    try:
        result = math.fsum(values)
    except OverflowError as exc:
        raise ValueError("soma das estimativas excede o limite numérico") from exc
    if not math.isfinite(result):
        raise ValueError("soma das estimativas excede o limite numérico")
    return round(result, 8)


class EvolutionarySequencer:
    """Sequencia um modelo explícito de capacidades com limites determinísticos.

    `requires(source=X,target=T)` coloca T antes de X; `enables(source=S,
    target=X)` coloca S antes de X. Cada predecessora aceita é uma restrição
    conjunta do plano; caminhos individuais não substituem esse conjunto.
    """

    def plan(
        self,
        capabilities: list[dict[str, Any]],
        dependencies: list[dict[str, Any]],
        target_state: list[str],
        *,
        observed: list[str] | None = None,
        max_routes: int = 100,
        max_depth: int = 64,
        duration_unit: str = "unspecified",
        cost_unit: str = "unspecified",
    ) -> dict[str, Any]:
        if not isinstance(capabilities, list) or len(capabilities) > 512:
            raise ValueError("capabilities deve ser lista com até 512 capacidades")
        if not isinstance(dependencies, list) or len(dependencies) > 4096:
            raise ValueError("dependencies deve ser lista com até 4096 dependências")
        if not isinstance(target_state, list) or (observed is not None and not isinstance(observed, list)):
            raise ValueError("target_state e observed devem ser listas")
        for value, limit, label in [(max_routes, 1000, "max_routes"), (max_depth, 512, "max_depth")]:
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= limit:
                raise ValueError(f"{label} fora dos limites")
        duration_unit = _identifier(duration_unit, "duration_unit")
        cost_unit = _identifier(cost_unit, "cost_unit")
        targets = sorted({_identifier(t, "target_state") for t in target_state})
        requested_observed = {_identifier(t, "observed") for t in (observed or [])}
        nodes: dict[str, dict[str, Any]] = {}
        warnings: list[str] = []
        for raw in capabilities:
            if not isinstance(raw, dict):
                raise ValueError("cada capacidade deve ser objeto")
            key = _identifier(raw.get("id", raw.get("capability")), "capability.id")
            if key in nodes:
                raise ValueError("capability.id duplicado")
            state = _identifier(raw.get("state", "unspecified"), "capability.state")
            explicit_observed = raw.get("observed", False)
            if not isinstance(explicit_observed, bool):
                raise ValueError("capability.observed deve ser booleano")
            nodes[key] = {
                "id": key,
                "state": state,
                "evidence": _evidence(raw.get("evidence")),
                "observed": explicit_observed or key in requested_observed,
                "estimated_duration": _estimate(raw.get("estimated_duration"), "estimated_duration"),
                "estimated_cost": _estimate(raw.get("estimated_cost"), "estimated_cost"),
                "resistance": _estimate(raw.get("resistance"), "resistance", 1.0),
            }
        satisfied = {
            key for key, node in nodes.items()
            if node["observed"] and node["evidence"]
            and (node["state"] in _EXECUTED_STATES or node["state"] == "unspecified")
        }
        for key in sorted(requested_observed - nodes.keys()):
            warnings.append(f"observed desconhecida: {key}")
        for key, node in sorted(nodes.items()):
            if node["observed"] and key not in satisfied:
                warnings.append(f"observed não satisfeita por estado/evidência: {key}")

        prereqs: dict[str, set[str]] = {key: set() for key in nodes}
        succ: dict[str, set[str]] = {key: set() for key in nodes}
        edges: dict[tuple[str, str], dict[str, Any]] = {}
        affinities: list[dict[str, Any]] = []
        unassessed: list[dict[str, Any]] = []
        for raw in sorted(dependencies, key=lambda e: (str(e.get("relation", "requires")),
                                                       str(e.get("source", "")), str(e.get("target", "")))
                          if isinstance(e, dict) else ("", "", "")):
            if not isinstance(raw, dict):
                raise ValueError("cada dependência deve ser objeto")
            source = _identifier(raw.get("source"), "dependency.source")
            target = _identifier(raw.get("target"), "dependency.target")
            relation = raw.get("relation", "requires")
            if relation not in {"requires", "enables", "co_occurs"}:
                raise ValueError("relação de dependência desconhecida")
            necessity = raw.get("necessity", "declared")
            if necessity not in {"declared", "hypothesis"}:
                raise ValueError("necessity deve ser declared ou hypothesis")
            edge = {
                "source": source, "target": target, "relation": relation,
                "necessity": necessity, "evidence": _evidence(raw.get("evidence")),
                "estimated_cost": _estimate(raw.get("estimated_cost"), "edge.estimated_cost"),
                "resistance": _estimate(raw.get("resistance"), "edge.resistance", 1.0),
            }
            if relation == "co_occurs":
                affinities.append(edge)
                continue
            predecessor, dependant = (target, source) if relation == "requires" else (source, target)
            edge["predecessor"] = predecessor
            edge["dependant"] = dependant
            if not edge["evidence"]:
                unassessed.append(edge)
                continue
            pair = (predecessor, dependant)
            if pair in edges:
                # requires/enables can express the same constraint. Deduplicate
                # identical declarations; conflicting estimates need resolution.
                previous = edges[pair]
                if any(previous[k] != edge[k] for k in ("estimated_cost", "resistance", "necessity")):
                    raise ValueError("estimativas/políticas conflitantes para a mesma dependência")
                previous["evidence"] = _evidence(previous["evidence"] + edge["evidence"])
                continue
            edges[pair] = edge
            if dependant in prereqs:
                prereqs[dependant].add(predecessor)
            if predecessor in succ:
                succ[predecessor].add(dependant)

        closure: set[str] = set()
        stack = list(targets)
        while stack:
            key = stack.pop()
            if key in closure or key not in nodes:
                continue
            closure.add(key)
            if key not in satisfied:
                stack.extend(sorted(prereqs[key], reverse=True))
        missing_targets = sorted(set(targets) - nodes.keys())
        active = closure - satisfied
        missing = sorted(
            ({"capability": key, "dependency": p, "reason": "unknown_capability"}
             for key in active for p in prereqs[key] if p not in nodes),
            key=lambda item: (item["capability"], item["dependency"]),
        )
        missing_evidence = sorted(key for key in closure if not nodes[key]["evidence"])
        relevant_unassessed = sorted(
            (edge for edge in unassessed if edge["dependant"] in active),
            key=lambda edge: (edge["dependant"], edge["predecessor"]),
        )
        cycles = self._cycles(active, succ)
        blocked = set(missing_evidence)
        blocked.update(item["capability"] for item in missing)
        blocked.update(edge["dependant"] for edge in relevant_unassessed)
        blocked.update(key for component in cycles for key in component)
        queue = list(blocked)
        while queue:
            current = queue.pop()
            for child in sorted(succ.get(current, set()) & active):
                if child not in blocked:
                    blocked.add(child)
                    queue.append(child)

        phases: list[list[str]] = []
        completed = set(satisfied)
        pending = active - blocked
        while pending:
            phase = sorted(key for key in pending if prereqs[key] <= completed)
            if not phase:
                blocked.update(pending)
                break
            phases.append(phase)
            completed.update(phase)
            pending.difference_update(phase)
        scheduled = set().union(*map(set, phases)) if phases else set()
        schedule = self._schedule(phases, nodes, prereqs, satisfied)
        makespan = None if blocked or missing_targets else (
            max((v["finish"] for v in schedule.values()), default=0.0)
            if all(v["finish"] is not None for v in schedule.values()) else None
        )
        required_edges = [edges[pair] for pair in sorted(edges)
                          if pair[1] in active and pair[0] in closure]
        total_cost = _known_sum(
            [nodes[k]["estimated_cost"] for k in sorted(active)]
            + [edge["estimated_cost"] for edge in required_edges]
        ) if not blocked and not missing_targets else None
        paths, truncated = self._routes(
            closure, blocked, satisfied, prereqs, succ, targets, max_routes, max_depth,
        )
        routes = []
        for path in paths:
            route_edges = [edges[(a, b)] for a, b in zip(path, path[1:])]
            route_nodes = [nodes[k] for k in path if k not in satisfied]
            routes.append({
                "path": path,
                "kind": "precedence_chain",
                "estimated_cost": _known_sum([n["estimated_cost"] for n in route_nodes]
                                              + [e["estimated_cost"] for e in route_edges]),
                "resistance_index": _known_sum([n["resistance"] for n in route_nodes]
                                                + [e["resistance"] for e in route_edges]),
                "resistance_kind": "additive_uncalibrated_index",
            })
        convergences = [
            {"capability": key, "predecessors": sorted(prereqs[key]),
             "estimated_start": schedule.get(key, {}).get("start"),
             "blocked": key in blocked}
            for key in sorted(active) if len(prereqs[key]) > 1
        ]
        warnings.extend([
            "Dependências fornecidas são condicionais; necessidade científica não demonstrada.",
            "Fases paralelas expressam independência lógica; disponibilidade de recursos não avaliada.",
            "Rotas são cadeias; todas as predecessoras aceitas continuam exigidas pelo plano.",
            "Estimativas não representam tempo, custo ou resistência observados em execução.",
        ])
        return {
            "status": "blocked" if blocked or missing_targets else ("planned" if active else "already_satisfied"),
            "target_state": targets, "closure": sorted(closure),
            "observed_capabilities": sorted(satisfied & closure),
            "evolution_gap": sorted(active),
            "capability_states": {key: nodes[key]["state"] for key in sorted(closure)},
            "prerequisites": {key: sorted(prereqs[key]) for key in sorted(closure)},
            "successors": {key: sorted(succ[key] & closure) for key in sorted(closure)},
            "dependencies": required_edges, "affinities": sorted(affinities, key=repr),
            "missing_dependencies": missing, "missing_targets": missing_targets,
            "missing_evidence": missing_evidence,
            "unassessed_dependencies": relevant_unassessed,
            "cycle_components": cycles, "blocked_nodes": sorted(blocked),
            "phases": phases, "scheduled_nodes": sorted(scheduled),
            "estimated_schedule": {"kind": "conditional_estimate", "unit": duration_unit,
                                   "nodes": schedule, "makespan": makespan},
            "estimated_total_cost": total_cost, "cost_unit": cost_unit,
            "routes": routes, "routes_truncated": truncated, "convergences": convergences,
            "params": {"max_routes": max_routes, "max_depth": max_depth},
            "execution_verified": False, "necessity_proven": False,
            "evidence_status": "provided_not_independently_validated",
            "warnings": sorted(warnings),
        }

    @staticmethod
    def _cycles(active: set[str], successors: dict[str, set[str]]) -> list[list[str]]:
        """Tarjan: separate actual cyclic components from their descendants."""
        indices: dict[str, int] = {}
        low: dict[str, int] = {}
        stack: list[str] = []
        on_stack: set[str] = set()
        result: list[list[str]] = []

        def visit(key: str) -> None:
            indices[key] = low[key] = len(indices)
            stack.append(key)
            on_stack.add(key)
            for child in sorted(successors.get(key, set()) & active):
                if child not in indices:
                    visit(child)
                    low[key] = min(low[key], low[child])
                elif child in on_stack:
                    low[key] = min(low[key], indices[child])
            if low[key] == indices[key]:
                component = []
                while True:
                    child = stack.pop()
                    on_stack.remove(child)
                    component.append(child)
                    if child == key:
                        break
                if len(component) > 1 or key in successors.get(key, set()):
                    result.append(sorted(component))

        for key in sorted(active):
            if key not in indices:
                visit(key)
        return sorted(result)

    @staticmethod
    def _schedule(phases, nodes, prerequisites, satisfied):
        result = {}
        finish = {key: 0.0 for key in satisfied}
        for phase in phases:
            for key in phase:
                previous = [finish[p] for p in prerequisites[key]]
                start = None if any(v is None for v in previous) else max(previous, default=0.0)
                duration = nodes[key]["estimated_duration"]
                end = None if start is None or duration is None else _known_sum([start, duration])
                finish[key] = end
                result[key] = {"start": start, "finish": end, "duration": duration}
        return result

    @staticmethod
    def _routes(closure, blocked, satisfied, prerequisites, successors, targets, limit, depth):
        usable = closure - blocked
        roots = sorted(key for key in usable if key in satisfied or not (prerequisites[key] & usable))
        target_set = set(targets)
        paths: list[list[str]] = []
        truncated = False

        def walk(key, path):
            nonlocal truncated
            if key in target_set:
                if len(paths) < limit:
                    paths.append(list(path))
                else:
                    truncated = True
                    return
            children = sorted(successors.get(key, set()) & usable - satisfied)
            if len(path) >= depth:
                if children:
                    truncated = True
                return
            for child in children:
                if len(paths) >= limit:
                    truncated = True
                    return
                if child not in path:
                    walk(child, path + [child])

        for key in roots:
            if len(paths) >= limit:
                truncated = True
                break
            walk(key, [key])
        return sorted(paths), truncated
