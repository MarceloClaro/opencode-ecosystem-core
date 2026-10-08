#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KnowledgeComposition — Composição Unitária do Conhecimento (R490/R664)

Proposta do usuário (camada Composição Unitária): assim como uma parede não é
apenas uma atividade — mas tijolos, cimento, areia, mão de obra, equipamentos e
tempo — uma capacidade futura não é um elemento indivisível: possui insumos
cognitivos que precisam existir para construí-la.

    Scanner Reverso (R483):  "O que precisará existir?"
    Trajectory Mapper (R485): "Em que ordem?"
    KnowledgeComposition:    "DO QUE isso é feito?"

Insights por capacidade (7 classes de insumo):
    conceitos    — elementos teóricos (ex.: efeito de tamanho, axioma, causalidade)
    metodos      — procedimentos (ex.: síntese quantitativa, dedução simbólica)
    bases        — conteúdo (ex.: artigos primários, manuais, normas)
    ferramentas  — mecanismos operacionais (ex.: solver simbólico, agentes)
    dominios     — especialistas/domínios de apoio (ex.: estatística, neurociência)
    validacoes   — critérios de verificação (ex.: I², prova formal, benchmark)
    recursos     — dados, equipamento e tempo necessários, quando declarados

Origem:
    "bank"    — composição CURADA em COMPOSITION_BANK (curadoria humana);
    "lexical" — fallback heurístico derivado dos tokens da capacidade
                (warning explícito; requer curadoria).

Algoritmo (documentação):
    compose(g): se g ∈ COMPOSITION_BANK → remover prefixo de domínio e retornar
                composição curada; senão derivar dos tokens do nome da
                capacidade (item em `conceitos` a partir do núcleo lexical).
    scan(scan, alvo): usa ReverseScanner (R483) para obter Δ e aplica compose
                por lacuna em ordem estável (por_capability = dict ordenado).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
from typing import Any

from scanners.reverse_scanner import ReverseScanner
from scanners.capability_dna import (
    CATEGORIES, MAX_CAPABILITIES, STATES, capability_map, reference_copy, text, texts,
)


# ─── Bank curado (origem "bank"; curadoria humana) ─────────────────────
COMPOSITION_BANK: dict[str, dict[str, list[str]]] = {
    "metodos.Meta-análise": {
        "conceitos": ["efeito de tamanho", "heterogeneidade", "forest plot", "viés de publicação"],
        "metodos": ["síntese quantitativa", "modelo de efeitos aleatórios", "ponderacao por inverso da variância"],
        "bases": ["artigos primários", "manuais Cochrane", "protocolos PRISMA"],
        "ferramentas": ["agentes de extração", "motores de busca bibliográfica", "calculadora de efeitos"],
        "dominios": ["estatística", "epidemiologia", "medicina baseada em evidências"],
        "validacoes": ["teste de heterogeneidade I²", "benchmark vs meta-análises publicadas", "análise de sensibilidade"],
    },
    "raciocinio.Prova geométrica": {
        "conceitos": ["axioma", "teorema", "dedução", "construção auxiliar"],
        "metodos": ["dedução simbólica (DDAR)", "busca orientada", "prova por contradição"],
        "bases": ["problemas olímpicos (IMO)", "corpus de geometria plana", "artigos AlphaGeometry"],
        "ferramentas": ["solver simbólico", "agente de prova", "motor de busca de construções"],
        "dominios": ["matemática", "geometria", "lógica formal"],
        "validacoes": ["verificação formal da prova", "benchmark IMO", "comparação com solução humana"],
    },
    "dados.Metadados (revisões)": {
        "conceitos": ["metadados", "curadoria", "proveniência", "vocabulário controlado"],
        "metodos": ["modelagem de metadados", "mapeamento de esquemas", "validação de completude"],
        "bases": ["esquemas de metadados (Dublin Core)", "normas de catalogação", "documentação de repositórios"],
        "ferramentas": ["validadores de esquema", "agentes de extração de metadados", "grafos de conhecimento"],
        "dominios": ["biblioteconomia", "ciência da informação", "engenharia de dados"],
        "validacoes": ["completude de campos", "aderência ao esquema", "amostra auditada"],
    },
}


@dataclass
class CompositionInsight:
    """Insumos cognitivos de uma capacidade futura."""
    capability: str
    conceitos: list[str]
    metodos: list[str]
    bases: list[str]
    ferramentas: list[str]
    dominios: list[str]
    validacoes: list[str]
    origem: str = "lexical"           # bank | lexical
    warning: str = ""
    fonte_conceitos: str = ""          # "bank:curada" | "lexical:tokens"
    recursos: list[str] = field(default_factory=list)
    inputs: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[dict[str, Any]] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    missing_capabilities: list[str] = field(default_factory=list)
    missing_categories: list[str] = field(default_factory=list)
    validation_criteria: list[dict[str, Any]] = field(default_factory=list)
    missing_validation_criteria: list[str] = field(default_factory=list)
    construction_map: dict[str, Any] = field(default_factory=dict)
    planning_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompositionReport:
    """Relatório de composição unitária por lacuna do gap."""
    target_state: list[str]
    evolution_gap: list[str]
    matches: list["CompositionInsight"]
    by_capability: dict[str, "CompositionInsight"]
    params: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"target_state": list(self.target_state), "evolution_gap": list(self.evolution_gap),
                "matches": [insight.to_dict() for insight in self.matches],
                "by_capability": {key: value.to_dict() for key, value in self.by_capability.items()},
                "params": reference_copy(self.params), "warnings": list(self.warnings),
                "planning_only": True}


class KnowledgeComposition:
    """Decompõe cada capacidade futura em insumos cognitivos construíveis."""

    def _TOKEN_SPLIT(self, s):
        return [t for t in s.lower().replace("-", " ").split() if t]

    def compose(self, capability: str, dna: Any = None,
                candidate: Any = None) -> CompositionInsight:
        """Insumos de `capability`: curados (bank) ou derivados (lexical)."""
        capability = text(capability, "capability")
        records = capability_map(dna)
        record = records.get(capability, {})
        if candidate is not None:
            if hasattr(candidate, "to_dict"):
                candidate = candidate.to_dict()
            if not isinstance(candidate, dict) or candidate.get("id") != capability:
                raise ValueError("candidate deve descrever a capacidade solicitada.")
            required = texts(candidate.get("requires", []), "candidate.requires", MAX_CAPABILITIES)
            record = {**record, "requires": required,
                      "composition": {"ferramentas": required}, "state": "declared",
                      "evidence": [], "origin": "hypothesis:" + text(candidate.get("origin", "provided"), "origin")}
        metadata = record.get("composition", {})
        if any(metadata.get(category) for category in CATEGORIES) or record.get("validation_criteria"):
            entry = {category: list(metadata.get(category, [])) for category in CATEGORIES}
            entry["validacoes"] = list(dict.fromkeys(entry["validacoes"] + record.get("validation_criteria", [])))
            insight = CompositionInsight(capability=capability,
                                         **entry, origem="metadata",
                                         fonte_conceitos="metadata:capability",
                                         warning="Composição declarada por metadados; insumos e critérios ainda exigem execução.")
            return self._enrich(insight, records, record)
        if capability in COMPOSITION_BANK:
            entry = COMPOSITION_BANK[capability]
            insight = CompositionInsight(
                capability=capability,
                conceitos=list(entry.get("conceitos", [])),
                metodos=list(entry.get("metodos", [])),
                bases=list(entry.get("bases", [])),
                ferramentas=list(entry.get("ferramentas", [])),
                dominios=list(entry.get("dominios", [])),
                validacoes=list(entry.get("validacoes", [])),
                origem="bank",
                fonte_conceitos="bank:curada",
                recursos=list(entry.get("recursos", ["corpus de referência", "tempo de revisão humana"])),
            )
            return self._enrich(insight, records, record)
        return self._enrich(self._lexical(capability), records, record)

    @staticmethod
    def _enrich(insight: CompositionInsight, records: dict[str, dict[str, Any]],
                record: dict[str, Any]) -> CompositionInsight:
        """Constrói um mapa de insumos; faltas não são preenchidas por invenção."""
        origin = record.get("origin") or "|".join(record.get("origins", [])) or f"{insight.origem}:{insight.capability}"
        requirements = list(record.get("requires", []))
        insight.missing_capabilities = sorted(set(requirements) - set(records))
        insight.missing_categories = [category for category in CATEGORIES if not getattr(insight, category)]
        for category in CATEGORIES:
            values = list(dict.fromkeys(getattr(insight, category)))
            setattr(insight, category, values)
            for label in values:
                digest = hashlib.sha256((insight.capability + "\0" + category + "\0" + label).encode()).hexdigest()[:16]
                identifier = f"input:{category}:{digest}"
                available = records.get(label, {})
                state = available.get("state", "absent")
                node = {"id": identifier, "kind": category, "name": label, "state": state,
                        "evidence": reference_copy(available.get("evidence", [])), "origin": origin}
                insight.inputs.append(node)
                if state not in STATES[1:]:
                    insight.missing.append(identifier)
                insight.dependencies.append({"source": insight.capability, "target": identifier,
                                             "relation": "requires", "origin": origin,
                                             "scope": "composition_input"})
                if category == "validacoes":
                    insight.validation_criteria.append({"id": identifier, "description": label,
                                                        "state": state if state in STATES[2:] else "pending",
                                                        "evidence": reference_copy(available.get("evidence", [])),
                                                        "origin": origin})
        if len(insight.inputs) > 128:
            raise ValueError("Composição excede 128 insumos; decomponha a capacidade em unidades menores.")
        # Validação usa as fontes e ferramentas da composição. Estas arestas
        # são regras de planejamento explícitas, sem alegação de teste realizado.
        prerequisites = [item for item in insight.inputs if item["kind"] in ("bases", "ferramentas")]
        for criterion in insight.validation_criteria:
            if criterion["state"] not in STATES[2:]:
                insight.missing_validation_criteria.append(criterion["id"])
            for prerequisite in prerequisites:
                insight.dependencies.append({"source": criterion["id"], "target": prerequisite["id"],
                                             "relation": "requires", "origin": "planning_rule:validation_inputs",
                                             "scope": "internal_input", "heuristic": True})
        for required in requirements:
            insight.dependencies.append({"source": insight.capability, "target": required,
                                         "relation": "requires", "origin": origin,
                                         "scope": "capability_requirement"})
        if len(insight.dependencies) > 512:
            raise ValueError("Composição excede 512 dependências; decomponha a capacidade.")
        materials_complete = not (insight.missing or insight.missing_capabilities or insight.missing_categories)
        insight.construction_map = {"capability": insight.capability,
                                    "nodes": reference_copy(insight.inputs),
                                    "edges": reference_copy(insight.dependencies),
                                    "missing": list(insight.missing),
                                    "missing_capabilities": list(insight.missing_capabilities),
                                    "missing_categories": list(insight.missing_categories),
                                    "materials_complete": materials_complete,
                                    "validation_pending": list(insight.missing_validation_criteria),
                                    "complete": (materials_complete and not insight.missing_validation_criteria
                                                 and record.get("state") in STATES[2:]),
                                    "planning_only": True, "evidence_scope": "provided_references"}
        return insight

    def compose_many(self, capabilities: list[str], dna: Any = None,
                     candidates: list[Any] | None = None) -> CompositionReport:
        """API integrada: unidades construíveis para capacidades e hipóteses."""
        capabilities = texts(capabilities, "capabilities", 128)
        candidate_map = {}
        if candidates is not None:
            if not isinstance(candidates, list) or len(candidates) > 128:
                raise ValueError("candidates deve conter até 128 hipóteses.")
            for candidate in candidates:
                item = candidate.to_dict() if hasattr(candidate, "to_dict") else candidate
                if not isinstance(item, dict):
                    raise ValueError("Cada candidata deve ser objeto ou descritor.")
                identifier = text(item.get("id"), "candidate.id")
                if identifier in candidate_map:
                    raise ValueError(f"ID de hipótese repetido: {identifier}")
                candidate_map[identifier] = item
        matches = [self.compose(capability, dna=dna, candidate=candidate_map.get(capability))
                   for capability in capabilities]
        return CompositionReport(target_state=list(capabilities), evolution_gap=list(capabilities),
                                 matches=matches, by_capability={item.capability: item for item in matches},
                                 params={"bank_entries": len(COMPOSITION_BANK), "planning_only": True,
                                         "max_inputs_per_capability": 128, "max_dependencies": 512},
                                 warnings=[item.warning for item in matches if item.warning])

    # ─── Fallback heurístico (origem lexical) ────────────────────────────

    def _lexical(self, capability: str) -> CompositionInsight:
        tokens = self._TOKEN_SPLIT(capability)
        # núcleo lexical: último token não genérico (lista de domínio/classe)
        generic = {"revisões", "longo", "prazo", "dados", "metodos", "raciocinio",
                   "temporalidade", "musica", "dimensao", "capacidade"}
        core = [t for t in tokens if t not in generic]
        if not core:
            core = tokens
        conceitos = [core[0]] if core else []
        return CompositionInsight(
            capability=capability,
            conceitos=conceitos,
            metodos=[],
            bases=[],
            ferramentas=[],
            dominios=[],
            validacoes=[],
            origem="lexical",
            warning="composição derivada por heurística léxica — requer curadoria humana",
            fonte_conceitos="lexical:tokens",
        )

    # ─── Scan integrado (ReverseScanner R483) ─────────────────────────────

    def scan(
        self,
        noological_scan: dict[str, Any],
        target_state: list[str],
        observed: list[str] | None = None,
        corpus_terms: list[str] | None = None,
        exemplars: list[list[str]] | None = None,
    ) -> CompositionReport:
        """Composição unitária por lacuna do gap (Δ do ReverseScanner)."""
        rs = ReverseScanner()
        base = rs.scan(
            noological_scan,
            target_state=target_state,
            observed=observed,
            corpus_terms=corpus_terms,
            exemplars=exemplars,
        )
        matches: list[CompositionInsight] = []
        by_capability: dict[str, CompositionInsight] = {}
        for gap in base.evolution_gap:
            ins = self.compose(gap)
            by_capability[gap] = ins
            matches.append(ins)
        warnings = [ins.warning for ins in matches if ins.warning]
        return CompositionReport(
            target_state=list(base.target_state),
            evolution_gap=list(base.evolution_gap),
            matches=matches,
            by_capability=by_capability,
            params={"bank_entries": len(COMPOSITION_BANK)},
            warnings=list(base.warnings) + warnings,
        )
