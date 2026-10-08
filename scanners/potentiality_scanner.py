#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PotentialityScanner — Scanner de Potenciais Latentes (R491/R664)

Proposta do usuário (camada Potentiality): responder **"o que está prestes a
nascer?"** — capacidades emergentes cujos componentes estruturais já estão
parcialmente presentes no ecossistema. Inspiração: o avião surgiu da
convergência de aerodinâmica, materiais e propulsão — nenhum componente novo,
a novidade foi a combinação.

    Noological/Teleological...: "o que não existe / deveria existir?"
    ReverseScanner (R483):      "o que é necessário?"
    KnowledgeComposition (R490): "do que isso é feito?"
    PotentialityScanner:        "o que pode emergir da estrutura atual?"

Módulos desta revisão:
    1. StructuralDNA — catálogo declarativo módulos → capabilities;
       expõe capabilities, redundant (cap em >1 módulo) e central.
    2. Emergence Scan — para cada candidata (hipótese de latentidade) computa:
       coverage(c)   = |requires(c) ∩ dna.capabilities| / |requires(c)|
       missing(c)    = requires(c) - dna.capabilities
       resistencia(c)= 1 - coverage(c)
       tier(c)       = 'latente-alto' se coverage ≥ 0.75
                       'emergente'    se coverage ≥ 0.34
                       'distante'     caso contrário

Candidatas são hipóteses; o relatório informa componentes, evidências e faltas.
R664 acrescenta combinações limitadas por relações/interfaces/metadados e
separa coverage declarativa de suporte operacional. O score é heurístico,
sem probabilidade calibrada. Referências são informadas, não executadas aqui.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from typing import Any

from scanners.capability_dna import (
    MAX_CAPABILITIES, STATES, bounded_int, evidence_records, normalize_modules, reference_copy, text, texts,
)

# Limiares de tiering documentados (não mágicos)
# latente-alto exige ≥ 3/4 dos componentes presentes; emergente ≥ 1/3
TIER_LATENTE_ALTO = 0.75
TIER_EMERGENTE = 0.34

# DNA declarativo padrão do ecossistema (compatibilidade com pipeline.py,
# que instancia PotentialityScanner() sem argumentos — SPEC-020)
DEFAULT_MODULES: dict[str, list[str]] = {
    "noological_scanner": ["gap_detection"],
    "teleological_scanner": ["target_definition"],
    "reverse_scanner": ["capacity_decomposition"],
    "trajectory_mapper": ["dependency_mapping", "trajectory_mapping"],
    "cross_validation_engine": ["cross_validation"],
    "polymathic_convergence": ["polymathic_reasoning", "cross_reference"],
    "knowledge_composition": ["input_decomposition"],
    "auto_evolve": ["self_evolution"],
    "mci_blackboard": ["multi_agent_coordination"],
    "trust_engine": ["evaluation"],
    "metabus": ["shared_memory"],
}

DEFAULT_RECIPES = (
    ("evidence-oriented-evolution", "Hipótese de evolução orientada a evidências",
     ["self_evolution", "evaluation", "shared_memory"]),
    ("goal-oriented-composition", "Hipótese de composição orientada a um estado futuro",
     ["target_definition", "capacity_decomposition", "input_decomposition", "dependency_mapping"]),
)


@dataclass
class StructuralDNA:
    """Mapa por declarações/evidências; nunca deriva capacidades de código."""
    modules: dict[str, list[Any]]
    records: dict[str, dict[str, Any]] = field(init=False, repr=False)

    def __post_init__(self):
        self.modules, self.records = normalize_modules(self.modules)

    @property
    def capabilities(self) -> set[str]:
        """Todas as capabilities declaradas nos módulos."""
        return set(self.records)

    @property
    def redundant(self) -> set[str]:
        """Capabilities declaradas em mais de um módulo."""
        seen: set[str] = set()
        dup: set[str] = set()
        for caps in self.modules.values():
            for c in set(caps):
                if c in seen:
                    dup.add(c)
                seen.add(c)
        return dup

    @property
    def central(self) -> set[str]:
        """Centrais: múltiplos provedores ou dependência de ≥2 capacidades."""
        consumers: dict[str, set[str]] = {}
        for capability, record in self.records.items():
            for required in record["requires"]:
                consumers.setdefault(required, set()).add(capability)
        return self.redundant | {capability for capability, users in consumers.items()
                                 if capability in self.records and len(users) >= 2}

    def to_dict(self) -> dict[str, Any]:
        dependencies = [{"source": capability, "target": requirement,
                         "relation": "requires", "origin": provider["origin"]}
                        for capability, record in self.records.items()
                        for provider in record["providers"]
                        for requirement in provider["requires"]]
        absent = sorted({edge["target"] for edge in dependencies} - self.capabilities)
        return {"capabilities": sorted(self.capabilities), "modules": list(self.modules),
                "capability_map": reference_copy(self.records),
                "redundant": sorted(self.redundant), "central": sorted(self.central),
                "absent": absent, "dependencies": dependencies,
                "evidence_scope": "provided_references", "code_tokenization": False}


@dataclass
class PotentialityCandidate:
    """Hipótese de capacidade latente (a avaliar pelo scanner)."""
    id: str
    description: str
    requires: list[str]
    origin: str = "declared_hypothesis"
    explanation: str = ""
    interfaces: list[dict[str, str]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Potentiality:
    """Resultado da avaliação de uma candidata."""
    id: str
    description: str
    requires: list[str]
    coverage: float
    missing: list[str]
    resistencia: float
    tier: str
    present: list[str] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    explanation: str = ""
    origin: str = "declared_hypothesis"
    operational_coverage: float = 0.0
    executed_coverage: float = 0.0
    external_coverage: float = 0.0
    heuristic_score: float = 0.0
    heuristic_resistance: float = 1.0
    resistance_factors: dict[str, Any] = field(default_factory=dict)
    score_kind: str = "heuristic"
    probability_calibrated: bool = False
    hypothesis_only: bool = True
    interfaces: list[dict[str, str]] = field(default_factory=list)
    hypothesis_references: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PotentialityReport:
    """Relatório de potencialidades latentes."""
    candidates: list["Potentiality"]
    by_id: dict[str, "Potentiality"]
    params: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        candidates = [candidate.to_dict() for candidate in self.candidates]
        return {"n_candidates": len(candidates), "candidates": candidates,
                "latent_potentials": candidates,
                "by_id": {key: value.to_dict() for key, value in self.by_id.items()},
                "params": reference_copy(self.params), "warnings": list(self.warnings),
                "score_kind": "heuristic", "probability_calibrated": False,
                "hypothesis_only": True}

    def items(self):
        return self.to_dict().items()

    def get(self, key: str, default=None):
        return self.to_dict().get(key, default)


class PotentialityScanner:
    """Avalia candidatas a capacidade latente contra o DNA estrutural.

    Compatibilidade (SPEC-020/pipeline.py): sem argumentos, usa
    DEFAULT_MODULES e expõe extract_dna() para o SuccessorGenerator legado.
    """

    def __init__(self, modules: dict[str, list[Any]] | None = None,
                 relations: list[dict[str, str]] | None = None):
        self.dna = StructuralDNA(modules=modules if modules is not None
                                 else DEFAULT_MODULES)
        self.relations = []
        if relations is not None:
            if not isinstance(relations, list) or len(relations) > 512:
                raise ValueError("relations deve conter até 512 relações declaradas.")
            for relation in relations:
                if not isinstance(relation, dict) or relation.get("relation") not in ("requires", "enables"):
                    raise ValueError("Relação deve ser requires ou enables.")
                self.relations.append({"source": text(relation.get("source"), "source"),
                                       "target": text(relation.get("target"), "target"),
                                       "relation": relation["relation"],
                                       "origin": text(relation.get("origin", "provided_relation"), "origin")})
        self.relations.sort(key=lambda edge: (edge["source"], edge["target"], edge["relation"]))
        self._last_discovery: dict[str, Any] = {}

    def extract_dna(self) -> dict[str, Any]:
        """Retorna o DNA estrutural no formato legado (SPEC-020).

        Formato aceito por SuccessorGenerator.generate():
            {'capabilities': [...], 'modules': [...]}
        """
        result = self.dna.to_dict()
        result["dependencies"].extend(reference_copy(self.relations))
        result["absent"] = sorted(set(result["absent"]) |
                                 {edge["target"] for edge in self.relations
                                  if edge["relation"] == "requires"
                                  and edge["target"] not in self.dna.capabilities})
        return result

    def discover(self, max_candidates: int = 32,
                 max_pair_checks: int = 256) -> list[PotentialityCandidate]:
        """Gera hipóteses limitadas; interfaces e metadados não provam execução."""
        bounded_int(max_candidates, "max_candidates", 128)
        bounded_int(max_pair_checks, "max_pair_checks", 8192)
        candidates: list[PotentialityCandidate] = []
        ids = set()
        pair_checks = 0
        truncated = False

        def add(origin: str, description: str, requires: list[str], explanation: str,
                interfaces: list[dict[str, str]] | None = None, identifier: str | None = None):
            nonlocal truncated
            required = list(dict.fromkeys(requires))
            if identifier is None:
                digest = hashlib.sha256((origin + "\0" + "\0".join(required)).encode()).hexdigest()[:16]
                identifier = f"hypothesis:{origin}:{digest}"
            if identifier in ids:
                return
            if len(candidates) >= max_candidates:
                truncated = True
                return
            ids.add(identifier)
            if len(explanation) > 2000:
                explanation = explanation[:1900] + " ... Resumo limitado; metadados completos permanecem no DNA."
            candidates.append(PotentialityCandidate(identifier, description, required,
                                                     origin, explanation, interfaces or []))

        for identifier, description, requires in DEFAULT_RECIPES:
            add("curated_recipe", description, requires,
                "Receita declarativa de composição; componentes ainda precisam de critérios e evidências.",
                identifier=identifier)
        records = self.dna.records
        for edge in self.relations:
            add("relations", f"Hipótese de colaboração entre {edge['source']} e {edge['target']}",
                [edge["source"], edge["target"]] + records.get(edge["source"], {}).get("requires", [])
                + records.get(edge["target"], {}).get("requires", []),
                f"Relação {edge['relation']} informada em {edge['origin']}.")
        for capability, record in records.items():
            for requirement in record["requires"]:
                add("dependencies", f"Hipótese de construção de {capability} com {requirement}",
                    [capability, requirement] + record["requires"],
                    f"{capability} declara requires={requirement}; a presença e execução são avaliadas separadamente.")
        names = list(records)
        for index, left_name in enumerate(names):
            if truncated:
                break
            for right_name in names[index + 1:]:
                if pair_checks >= max_pair_checks or len(candidates) >= max_candidates:
                    truncated = True
                    break
                pair_checks += 1
                left, right = records[left_name], records[right_name]
                interfaces = ([{"source": left_name, "target": right_name, "type": item}
                               for item in sorted(set(left["outputs"]) & set(right["inputs"]))] +
                              [{"source": right_name, "target": left_name, "type": item}
                               for item in sorted(set(right["outputs"]) & set(left["inputs"]))])
                shared = sorted(set(left["tags"]) & set(right["tags"]))
                requires = [left_name, right_name] + left["requires"] + right["requires"]
                if interfaces:
                    add("interfaces", f"Hipótese de integração de {left_name} e {right_name}", requires,
                        "Interfaces declaradas de saída/entrada compartilham " + ", ".join(sorted({i['type'] for i in interfaces}))
                        + "; compatibilidade operacional ainda exige teste.", interfaces)
                elif shared:
                    add("metadata", f"Hipótese de composição de {left_name} e {right_name}", requires,
                        "Metadados compartilhados: " + ", ".join(shared) + "; relação semântica proposta, sem execução.")
            if truncated:
                break
        total_pairs = len(names) * (len(names) - 1) // 2
        self._last_discovery = {"pair_checks": pair_checks, "possible_pairs": total_pairs,
                                "max_candidates": max_candidates, "max_pair_checks": max_pair_checks,
                                "truncated": truncated, "generated": len(candidates)}
        return candidates

    @staticmethod
    def _resolve(candidate: PotentialityCandidate, dna_caps: set[str],
                 records: dict[str, dict[str, Any]] | None = None) -> Potentiality:
        records = records or {}
        requires = list(dict.fromkeys(candidate.requires))
        n = len(requires)
        if n == 0:
            coverage, missing, present = 0.0, [], []
        else:
            present = [r for r in requires if r in dna_caps]
            coverage = len(present) / n
            missing = [r for r in requires if r not in dna_caps]
        if coverage >= TIER_LATENTE_ALTO:
            tier = "latente-alto"
        elif coverage >= TIER_EMERGENTE:
            tier = "emergente"
        else:
            tier = "distante"
        available = [r for r in present if STATES.index(records.get(r, {}).get("state", "declared")) >= 1]
        executed = [r for r in present if STATES.index(records.get(r, {}).get("state", "declared")) >= 2]
        external = [r for r in present if records.get(r, {}).get("state") == "externally_validated"]
        operational = len(available) / n if n else 0.0
        execution = len(executed) / n if n else 0.0
        validation = len(external) / n if n else 0.0
        score = 0.4 * coverage + 0.35 * operational + 0.2 * execution + 0.05 * validation
        evidence = [{"capability": requirement, "state": records.get(requirement, {}).get("state", "declared"),
                     "providers": reference_copy(records.get(requirement, {}).get("providers", [])),
                     "references": reference_copy(records.get(requirement, {}).get("evidence", []))}
                    for requirement in present]
        explanation = (candidate.explanation + " " if candidate.explanation else "") + (
            f"Hipótese com {len(present)}/{n} componentes declarados, {len(available)}/{n} disponíveis "
            f"e {len(executed)}/{n} com registros de execução. Faltantes: {', '.join(missing) or 'nenhum declarado'}. "
            "Cobertura declarativa não implica capacidade integrada em execução.")
        return Potentiality(
            id=candidate.id,
            description=candidate.description,
            requires=requires,
            coverage=round(coverage, 4),
            missing=missing,
            resistencia=round(1 - coverage, 4),
            tier=tier,
            present=present, evidence=evidence, explanation=explanation, origin=candidate.origin,
            operational_coverage=round(operational, 4), executed_coverage=round(execution, 4),
            external_coverage=round(validation, 4), heuristic_score=round(score, 4),
            heuristic_resistance=round(1 - score, 4),
            resistance_factors={"missing": missing,
                                "not_available": [r for r in present if r not in available],
                                "no_execution_reference": [r for r in present if r not in executed]},
            interfaces=reference_copy(candidate.interfaces),
            hypothesis_references=reference_copy(candidate.evidence),
        )

    def scan(self, candidates: list[PotentialityCandidate | dict[str, Any]] | None = None,
             *, strict_ids: bool = False) -> PotentialityReport:
        """Avalia todas as candidatas em ordem estável."""
        if candidates is None:
            candidates = self.discover()
        if not isinstance(candidates, list) or len(candidates) > 128:
            raise ValueError("candidates deve conter até 128 hipóteses.")
        if type(strict_ids) is not bool:
            raise ValueError("strict_ids deve ser booleano.")
        id_counts: dict[str, int] = {}
        for candidate in candidates:
            if not isinstance(candidate, (PotentialityCandidate, dict)):
                raise ValueError("Cada candidata deve ser objeto ou descritor.")
            identifier = text(candidate.get("id") if isinstance(candidate, dict) else candidate.id,
                              "candidate.id")
            id_counts[identifier] = id_counts.get(identifier, 0) + 1
        if strict_ids and any(count > 1 for count in id_counts.values()):
            raise ValueError("IDs de hipótese repetidos; forneça identificadores distintos.")
        aliases: dict[str, list[str]] = {}
        warnings = ["Hipóteses e scores heurísticos; referências informadas não são execução pelo scanner."]
        results: list[Potentiality] = []
        by_id: dict[str, Potentiality] = {}
        dna_caps = self.dna.capabilities
        for cand in candidates:
            if isinstance(cand, dict):
                try:
                    cand = PotentialityCandidate(**cand)
                except TypeError as exc:
                    raise ValueError("Descritor de hipótese incompleto ou com campos desconhecidos.") from exc
            if not isinstance(cand, PotentialityCandidate):
                raise ValueError("Cada candidata deve ser PotentialityCandidate ou descritor.")
            identifier = text(cand.id, "candidate.id")
            text(cand.description, "candidate.description", 2000)
            required = texts(cand.requires, "candidate.requires", MAX_CAPABILITIES)
            origin = text(cand.origin, "candidate.origin")
            if not isinstance(cand.explanation, str) or len(cand.explanation) > 2000:
                raise ValueError("candidate.explanation deve ser texto de até 2000 caracteres.")
            if not isinstance(cand.interfaces, list) or len(cand.interfaces) > 128:
                raise ValueError("candidate.interfaces deve conter até 128 interfaces.")
            interfaces = []
            for interface in cand.interfaces:
                if not isinstance(interface, dict):
                    raise ValueError("Cada interface deve declarar source, target e type.")
                interfaces.append({key: text(interface.get(key), f"interface.{key}")
                                   for key in ("source", "target", "type")})
            references = evidence_records(cand.evidence)
            if id_counts[identifier] > 1:
                original = identifier
                canonical = json.dumps({"requires": sorted(required), "description": cand.description,
                                        "origin": origin, "explanation": cand.explanation,
                                        "interfaces": interfaces, "evidence": references},
                                       sort_keys=True, ensure_ascii=False)
                digest = hashlib.sha256(canonical.encode()).hexdigest()[:16]
                identifier = f"{original[:470]}:{digest}"
                aliases.setdefault(original, [])
                if identifier not in aliases[original]:
                    aliases[original].append(identifier)
                if identifier in by_id:
                    warnings.append(f"Hipótese equivalente com ID {original} repetida; mantida uma representação.")
                    continue
            normalized = PotentialityCandidate(identifier, cand.description, required, origin,
                                                cand.explanation, interfaces, references)
            p = self._resolve(normalized, dna_caps, self.dna.records)
            results.append(p)
            by_id[p.id] = p
        return PotentialityReport(
            candidates=results,
            by_id=by_id,
            params={
                "n_candidates": len(candidates),
                "dna_capabilities": len(dna_caps),
                "coverage_scope": "declared_components",
                "score_weights": {"declared": 0.4, "available": 0.35,
                                  "executed": 0.2, "externally_validated": 0.05},
                "evidence_scope": "provided_references",
                "discovery": dict(self._last_discovery),
                "id_aliases": {key: sorted(value) for key, value in aliases.items()},
            },
            warnings=warnings + (["IDs de exibição legados desambiguados por componentes/metadados."] if aliases else []),
        )
