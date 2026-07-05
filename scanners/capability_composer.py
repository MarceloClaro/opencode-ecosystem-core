#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CapabilityComposer v1.0 — Composição Unitária do Conhecimento (SPEC-033)
========================================================================
Decompõe capacidades abstratas em insumos cognitivos construtíveis.

Arquitetura:
  1. CognitiveInput     — unidade atômica imutável (conceito, método, tool, etc.)
  2. CapabilityUnit     — decomposição completa de uma capacidade
  3. InputNode          — nó no grafo de insumos compartilhados
  4. CognitiveLibrary   — carrega/valida/pesquisa a biblioteca de insumos
  5. CapabilityComposer — orquestra decomposição (template → analogia → frontier)

Bootstrap:
  - cognitive_library.json (77 insumos seed)
  - Extração de evo-*.md e skills/*/SKILL.md
  - Templates de composição por categoria (10 dimensões NoologicalScanner)

Autor: Marcelo Claro Laranjeira (2026)
Integração: SPEC-028, SPEC-029, SPEC-030, SPEC-032
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════

VALID_INPUT_TYPES: frozenset[str] = frozenset({
    "concept", "method", "knowledge_base", "tool",
    "external_domain", "validation",
})

VALID_MATURITIES: frozenset[str] = frozenset({
    "established", "emerging", "speculative",
})

VALID_SOURCES: frozenset[str] = frozenset({
    "curated", "inferred", "template",
})

# Prefixo "extracted:" é válido com qualquer sufixo
EXTRACTED_SOURCE_RE = re.compile(r"^extracted:(evo-\d+|skill-.+)$")


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CognitiveInput:
    """Insumo cognitivo imutável — unidade atômica da composição.

    Attributes:
        input_id: Identificador único (ex.: "method.engenharia_reversa")
        name: Nome legível (ex.: "Engenharia Reversa")
        input_type: Tipo do insumo (concept|method|knowledge_base|tool|external_domain|validation)
        description: Descrição do insumo
        maturity: Nível de maturidade (established|emerging|speculative)
        references: DOIs, paths ou URLs
        source: Origem (curated|inferred|template|extracted:evo-N|extracted:skill-X)
        validation_cts: CT-IDs que validam este input
    """
    input_id: str
    name: str
    input_type: str
    description: str
    maturity: str = "established"
    references: list[str] = field(default_factory=list)
    source: str = "curated"
    validation_cts: list[str] = field(default_factory=list)

    def __post_init__(self):
        # Validate input_type
        if self.input_type not in VALID_INPUT_TYPES:
            raise ValueError(
                f"input_type '{self.input_type}' inválido. "
                f"Válidos: {sorted(VALID_INPUT_TYPES)}"
            )
        # Validate maturity
        if self.maturity not in VALID_MATURITIES:
            raise ValueError(
                f"maturity '{self.maturity}' inválida. "
                f"Válidas: {sorted(VALID_MATURITIES)}"
            )
        # Validate source
        if self.source not in VALID_SOURCES and not EXTRACTED_SOURCE_RE.match(self.source):
            raise ValueError(
                f"source '{self.source}' inválido. "
                f"Válidos: {sorted(VALID_SOURCES)} ou 'extracted:evo-N' / 'extracted:skill-X'"
            )
        # Validate input_id not empty
        if not self.input_id or "." not in self.input_id:
            raise ValueError(
                f"input_id '{self.input_id}' deve conter '<tipo>.<nome>' (ex.: 'method.engenharia_reversa')"
            )
        # Validate references are strings
        for i, ref in enumerate(self.references):
            if not isinstance(ref, str):
                raise ValueError(f"references[{i}] deve ser string, não {type(ref).__name__}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_id": self.input_id,
            "name": self.name,
            "input_type": self.input_type,
            "description": self.description,
            "maturity": self.maturity,
            "references": list(self.references),
            "source": self.source,
            "validation_cts": list(self.validation_cts),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CognitiveInput":
        return cls(
            input_id=data["input_id"],
            name=data["name"],
            input_type=data["input_type"],
            description=data["description"],
            maturity=data.get("maturity", "established"),
            references=data.get("references", []),
            source=data.get("source", "curated"),
            validation_cts=data.get("validation_cts", []),
        )


@dataclass(frozen=True)
class CapabilityUnit:
    """Decomposição completa de uma capacidade em insumos construtíveis.

    Attributes:
        capability_id: Identificador da capacidade (ex.: "metodos.Quantitativo experimental")
        capability_name: Nome legível
        concepts: input_ids do tipo "concept"
        methods: input_ids do tipo "method"
        knowledge_bases: input_ids do tipo "knowledge_base"
        tools: input_ids do tipo "tool" (podem referenciar capabilities)
        external_domains: input_ids do tipo "external_domain"
        validations: input_ids do tipo "validation"
        internal_deps: input_id → [input_ids que dependem dele]
        missing_inputs: input_ids que não existem na biblioteca
        construction_cost: 0-1, proporção de inputs faltantes
        frontier: True se sem composição conhecida
    """
    capability_id: str
    capability_name: str
    concepts: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    knowledge_bases: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    external_domains: list[str] = field(default_factory=list)
    validations: list[str] = field(default_factory=list)
    internal_deps: dict[str, list[str]] = field(default_factory=dict)
    missing_inputs: list[str] = field(default_factory=list)
    construction_cost: float = 0.0
    frontier: bool = False

    def __post_init__(self):
        total_inputs = (
            len(self.concepts) + len(self.methods) + len(self.knowledge_bases)
            + len(self.tools) + len(self.external_domains) + len(self.validations)
        )
        if total_inputs == 0:
            object.__setattr__(self, "frontier", True)
            object.__setattr__(self, "construction_cost", 1.0)
        elif self.construction_cost < 0.0 or self.construction_cost > 1.0:
            raise ValueError(
                f"construction_cost deve estar entre 0 e 1, recebido {self.construction_cost}"
            )

    @property
    def all_inputs(self) -> list[str]:
        """Todos os input_ids combinados."""
        return (
            self.concepts + self.methods + self.knowledge_bases
            + self.tools + self.external_domains + self.validations
        )

    @property
    def total_input_count(self) -> int:
        """Número total de inputs (todos os tipos)."""
        return len(self.all_inputs)

    @property
    def input_counts_by_type(self) -> dict[str, int]:
        """Contagem de inputs por tipo."""
        return {
            "concept": len(self.concepts),
            "method": len(self.methods),
            "knowledge_base": len(self.knowledge_bases),
            "tool": len(self.tools),
            "external_domain": len(self.external_domains),
            "validation": len(self.validations),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "concepts": list(self.concepts),
            "methods": list(self.methods),
            "knowledge_bases": list(self.knowledge_bases),
            "tools": list(self.tools),
            "external_domains": list(self.external_domains),
            "validations": list(self.validations),
            "internal_deps": {k: list(v) for k, v in self.internal_deps.items()},
            "missing_inputs": list(self.missing_inputs),
            "construction_cost": self.construction_cost,
            "frontier": self.frontier,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CapabilityUnit":
        return cls(
            capability_id=data["capability_id"],
            capability_name=data["capability_name"],
            concepts=data.get("concepts", []),
            methods=data.get("methods", []),
            knowledge_bases=data.get("knowledge_bases", []),
            tools=data.get("tools", []),
            external_domains=data.get("external_domains", []),
            validations=data.get("validations", []),
            internal_deps=data.get("internal_deps", {}),
            missing_inputs=data.get("missing_inputs", []),
            construction_cost=data.get("construction_cost", 0.0),
            frontier=data.get("frontier", False),
        )


@dataclass
class InputNode:
    """Nó no grafo de insumos compartilhados.

    Attributes:
        input_id: Identificador do input
        input_type: Tipo do input
        shared_by: capability_ids que usam este input
        build_cost: Custo de construir este input (0-1)
        exists: True se já existe no ecossistema
    """
    input_id: str
    input_type: str
    shared_by: set[str] = field(default_factory=set)
    build_cost: float = 0.5
    exists: bool = False


# ═══════════════════════════════════════════════════════════════════════════
# TEMPLATES DE COMPOSIÇÃO POR CATEGORIA (10 dimensões NoologicalScanner)
# ═══════════════════════════════════════════════════════════════════════════

COMPOSITION_TEMPLATES: dict[str, dict[str, list[str]]] = {
    "metodos": {
        "concepts": [
            "concept.causalidade",
            "concept.validacao_empirica",
            "concept.abstracao",
        ],
        "methods": [
            "method.design_fatorial",
            "method.randomizacao",
        ],
        "knowledge_bases": [
            "knowledge_base.artigos_cientificos",
            "knowledge_base.normas_tecnicas",
        ],
        "tools": [
            "tool.analise_estatistica_inferencial",
        ],
        "external_domains": [
            "domain.estatistica",
            "domain.filosofia_ciencia",
        ],
        "validations": [
            "valid.ct_passam",
            "valid.composicao_completa",
        ],
    },
    "raciocinio": {
        "concepts": [
            "concept.probabilidade",
            "concept.inferencia",
            "concept.abstracao",
        ],
        "methods": [
            "method.validacao_cruzada",
            "method.raciocinio_comparativo",
        ],
        "knowledge_bases": [
            "knowledge_base.livros_fundamentais",
            "knowledge_base.especificacoes_formais",
        ],
        "tools": [],
        "external_domains": [
            "domain.filosofia_ciencia",
            "domain.ciencia_computacao",
        ],
        "validations": [
            "valid.coerencia_identificada",
            "valid.ct_passam",
        ],
    },
    "paradigmas": {
        "concepts": [
            "concept.aderencia_estrutural",
            "concept.abstracao",
        ],
        "methods": [
            "method.analise_estrutural",
            "method.decomposicao_hierarquica",
        ],
        "knowledge_bases": [
            "knowledge_base.livros_fundamentais",
            "knowledge_base.artigos_cientificos",
        ],
        "tools": [],
        "external_domains": [
            "domain.filosofia_ciencia",
            "domain.sociologia",
        ],
        "validations": [
            "valid.coerencia_identificada",
            "valid.aderencia_estado_futuro",
        ],
    },
    "teoria_jogos": {
        "concepts": [
            "concept.causalidade",
            "concept.dependencia_estrutural",
            "concept.inferencia",
        ],
        "methods": [
            "method.raciocinio_comparativo",
            "method.analise_estrutural",
        ],
        "knowledge_bases": [
            "knowledge_base.artigos_cientificos",
            "knowledge_base.dados_empiricos",
        ],
        "tools": [
            "tool.raciocinio_probabilistico",
        ],
        "external_domains": [
            "domain.teoria_jogos",
            "domain.economia",
            "domain.biologia_evolutiva",
        ],
        "validations": [
            "valid.ct_passam",
            "valid.aderencia_estado_futuro",
        ],
    },
    "dados": {
        "concepts": [
            "concept.validacao_empirica",
            "concept.probabilidade",
        ],
        "methods": [
            "method.validacao_cruzada",
            "method.randomizacao",
        ],
        "knowledge_bases": [
            "knowledge_base.dados_empiricos",
            "knowledge_base.repositorios_codigo",
        ],
        "tools": [
            "tool.analise_estatistica_inferencial",
        ],
        "external_domains": [
            "domain.estatistica",
            "domain.ciencia_computacao",
        ],
        "validations": [
            "valid.composicao_completa",
            "valid.ct_passam",
        ],
    },
    "temporalidade": {
        "concepts": [
            "concept.causalidade",
            "concept.estado_futuro",
        ],
        "methods": [
            "method.engenharia_reversa",
            "method.analise_estrutural",
        ],
        "knowledge_bases": [
            "knowledge_base.conhecimento_historico",
        ],
        "tools": [],
        "external_domains": [
            "domain.engenharia",
            "domain.biologia_evolutiva",
        ],
        "validations": [
            "valid.aderencia_estado_futuro",
        ],
    },
    "niveis_analise": {
        "concepts": [
            "concept.aderencia_estrutural",
            "concept.abstracao",
        ],
        "methods": [
            "method.decomposicao_hierarquica",
            "method.analise_estrutural",
        ],
        "knowledge_bases": [
            "knowledge_base.especificacoes_formais",
        ],
        "tools": [],
        "external_domains": [
            "domain.sociologia",
            "domain.engenharia",
        ],
        "validations": [
            "valid.coerencia_identificada",
        ],
    },
    "populacao": {
        "concepts": [
            "concept.validacao_empirica",
            "concept.inferencia",
        ],
        "methods": [
            "method.randomizacao",
            "method.analise_poder_estatistico",
        ],
        "knowledge_bases": [
            "knowledge_base.dados_empiricos",
            "knowledge_base.artigos_cientificos",
        ],
        "tools": [],
        "external_domains": [
            "domain.estatistica",
            "domain.sociologia",
        ],
        "validations": [
            "valid.ct_passam",
            "valid.composicao_completa",
        ],
    },
    "teorias": {
        "concepts": [
            "concept.abstracao",
            "concept.transferencia_aprendizagem",
        ],
        "methods": [
            "method.raciocinio_comparativo",
            "method.analise_estrutural",
        ],
        "knowledge_bases": [
            "knowledge_base.livros_fundamentais",
            "knowledge_base.artigos_cientificos",
        ],
        "tools": [],
        "external_domains": [
            "domain.filosofia_ciencia",
            "domain.linguistica",
        ],
        "validations": [
            "valid.coerencia_identificada",
        ],
    },
    "dominios": {
        "concepts": [
            "concept.transferencia_aprendizagem",
            "concept.aderencia_estrutural",
        ],
        "methods": [
            "method.raciocinio_comparativo",
            "method.engenharia_reversa",
        ],
        "knowledge_bases": [
            "knowledge_base.documentacao_tecnica",
            "knowledge_base.repositorios_codigo",
        ],
        "tools": [],
        "external_domains": [
            "domain.biologia_evolutiva",
            "domain.neurociencia",
            "domain.engenharia",
        ],
        "validations": [
            "valid.ct_passam",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# COGNITIVE LIBRARY
# ═══════════════════════════════════════════════════════════════════════════

class CognitiveLibrary:
    """Biblioteca de insumos cognitivos — carrega, valida e pesquisa."""

    def __init__(self):
        self._inputs: dict[str, CognitiveInput] = {}

    # ─── CRUD ───────────────────────────────────────────────────────────

    @property
    def size(self) -> int:
        return len(self._inputs)

    @property
    def input_ids(self) -> list[str]:
        return sorted(self._inputs.keys())

    def get(self, input_id: str) -> CognitiveInput | None:
        return self._inputs.get(input_id)

    def has(self, input_id: str) -> bool:
        return input_id in self._inputs

    def add(self, inp: CognitiveInput) -> None:
        """Adiciona um input. Levanta ValueError se duplicado."""
        if inp.input_id in self._inputs:
            raise ValueError(f"Input duplicado: '{inp.input_id}' já existe na biblioteca")
        self._inputs[inp.input_id] = inp

    def remove(self, input_id: str) -> None:
        """Remove um input. Levanta KeyError se não existe."""
        if input_id not in self._inputs:
            raise KeyError(f"Input '{input_id}' não encontrado na biblioteca")
        del self._inputs[input_id]

    # ─── LOAD / SAVE ────────────────────────────────────────────────────

    def load_json(self, path: str | Path) -> int:
        """Carrega biblioteca de arquivo JSON. Retorna número de inputs carregados."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Biblioteca não encontrada: {path}")

        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"JSON deve ser uma lista, recebido {type(data).__name__}")

        loaded = 0
        for item in data:
            inp = CognitiveInput.from_dict(item)
            self.add(inp)
            loaded += 1

        return loaded

    def save_json(self, path: str | Path) -> int:
        """Salva biblioteca em arquivo JSON. Retorna número de inputs salvos."""
        path = Path(path)
        items = [inp.to_dict() for inp in self._inputs.values()]
        path.write_text(
            json.dumps(items, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return len(items)

    # ─── QUERIES ────────────────────────────────────────────────────────

    def by_type(self, input_type: str) -> list[CognitiveInput]:
        """Filtra inputs por tipo."""
        if input_type not in VALID_INPUT_TYPES:
            raise ValueError(f"input_type inválido: '{input_type}'")
        return [inp for inp in self._inputs.values() if inp.input_type == input_type]

    def by_source(self, source: str) -> list[CognitiveInput]:
        """Filtra inputs por origem."""
        return [inp for inp in self._inputs.values() if inp.source == source]

    def search(self, query: str) -> list[CognitiveInput]:
        """Busca textual em name e description (case-insensitive)."""
        q = query.lower()
        results = []
        for inp in self._inputs.values():
            if q in inp.name.lower() or q in inp.description.lower():
                results.append(inp)
        return results

    def stats(self) -> dict[str, int]:
        """Estatísticas: contagem por input_type."""
        stats: dict[str, int] = {}
        for inp in self._inputs.values():
            stats[inp.input_type] = stats.get(inp.input_type, 0) + 1
        return stats

    # ─── VALIDATION ─────────────────────────────────────────────────────

    def validate_all(self) -> list[str]:
        """Valida todos os inputs. Retorna lista de erros (vazia = OK)."""
        errors: list[str] = []
        ids_seen: set[str] = set()

        for inp in self._inputs.values():
            # Unicidade (já garantida por add(), mas verifica no dicionário)
            if inp.input_id in ids_seen:
                errors.append(f"input_id duplicado: '{inp.input_id}'")
            ids_seen.add(inp.input_id)

            # Validação de campos obrigatórios
            if not inp.name.strip():
                errors.append(f"'{inp.input_id}': name vazio")
            if not inp.description.strip():
                errors.append(f"'{inp.input_id}': description vazio")

        return errors

    # ─── BOOTSTRAP ──────────────────────────────────────────────────────

    @classmethod
    def bootstrap_from_evos(cls, evo_dir: str | Path) -> "CognitiveLibrary":
        """Extrai insumos de arquivos evolution/evo-*.md."""
        lib = cls()
        evo_dir = Path(evo_dir)
        if not evo_dir.exists():
            return lib

        for evo in sorted(evo_dir.glob("evo-*.md")):
            text = evo.read_text(encoding="utf-8")
            rm = re.search(r"round:\s*(\d+)", text)
            round_n = rm.group(1) if rm else "?"

            # Extrai ferramentas
            tools_section = re.search(r"## Acoes Executadas.*?(?=##|\Z)", text, re.DOTALL)
            if tools_section:
                for line in tools_section.group(0).split("\n"):
                    tm = re.match(r"-\s+([a-z_-]+):", line.strip())
                    if tm:
                        tool_name = tm.group(1)
                        tid = f"tool.{tool_name.replace('-', '_')}"
                        if not lib.has(tid):
                            lib.add(CognitiveInput(
                                input_id=tid,
                                name=tool_name.replace("-", " ").title(),
                                input_type="tool",
                                description=f"Ferramenta usada no ciclo evolutivo Round {round_n}",
                                references=[f"evolution/{evo.name}"],
                                source=f"extracted:evo-{round_n}",
                            ))

            # Extrai métodos
            practices = re.search(r"## Melhores Praticas Extraidas.*?(?=##|\Z)", text, re.DOTALL)
            if practices:
                for line in practices.group(0).split("\n"):
                    line = line.strip()
                    if line and line[0].isdigit():
                        for mp in re.findall(
                            r"(?:Pearson|cross.validation|validacao.cruzada|"
                            r"analise.\w+|decomposicao.\w+|engenharia.reversa)",
                            line, re.IGNORECASE,
                        ):
                            mid = f"method.{mp.lower().replace(' ', '_')}"
                            if not lib.has(mid):
                                lib.add(CognitiveInput(
                                    input_id=mid,
                                    name=mp.title(),
                                    input_type="method",
                                    description=line[:120],
                                    references=[f"evolution/{evo.name}"],
                                    source=f"extracted:evo-{round_n}",
                                ))

        return lib

    @classmethod
    def bootstrap_from_skills(cls, skills_dir: str | Path, max_skills: int = 30) -> "CognitiveLibrary":
        """Extrai insumos de skills/*/SKILL.md."""
        lib = cls()
        skills_dir = Path(skills_dir)

        skill_files = (
            list(skills_dir.glob("*/SKILL.md"))
            + list(skills_dir.glob("*/*/SKILL.md"))
        )[:max_skills]

        for sf in skill_files:
            if not sf.exists():
                continue
            skill_name = sf.parent.name
            tid = f"tool.{skill_name.replace('-', '_')}"
            if not lib.has(tid):
                text = sf.read_text(encoding="utf-8")
                desc_line = ""
                for line in text.split("\n")[:15]:
                    if "description" in line.lower() or "skill do ecossistema" in line.lower():
                        desc_line = line.strip()
                        break
                lib.add(CognitiveInput(
                    input_id=tid,
                    name=skill_name.replace("-", " ").title(),
                    input_type="tool",
                    description=desc_line[:200] if desc_line else f"Skill do ecossistema OpenCode: {skill_name}",
                    references=[str(sf)],
                    source=f"extracted:skill-{skill_name}",
                ))

        return lib


# ═══════════════════════════════════════════════════════════════════════════
# CAPABILITY COMPOSER
# ═══════════════════════════════════════════════════════════════════════════

class CapabilityComposer:
    """Orquestrador da decomposição de capacidades em insumos cognitivos.

    Pipeline:
      1. Template por categoria (COMPOSITION_TEMPLATES)
      2. [Futuro] Analogia Polimática (PolymathicConvergence)
      3. [Futuro] Decomposição Generativa (LLM)
      4. Fallback: frontier (construction_cost=1.0)

    Uso:
        composer = CapabilityComposer(library)
        unit = composer.decompose("metodos.Quantitativo experimental", "psicologia")
    """

    def __init__(self, library: CognitiveLibrary | None = None):
        self.library = library or CognitiveLibrary()

    def _extract_category(self, capability_id: str) -> str:
        """Extrai a categoria da capability_id (ex.: 'metodos.X' → 'metodos')."""
        return capability_id.split(".", 1)[0] if "." in capability_id else capability_id

    def _apply_template(self, category: str, capability_id: str) -> CapabilityUnit | None:
        """Aplica template de composição para a categoria. Retorna None se não houver template."""
        template = COMPOSITION_TEMPLATES.get(category)
        if not template:
            return None

        concepts = list(template.get("concepts", []))
        methods = list(template.get("methods", []))
        knowledge_bases = list(template.get("knowledge_bases", []))
        tools = list(template.get("tools", []))
        external_domains = list(template.get("external_domains", []))
        validations = list(template.get("validations", []))

        # Computa missing_inputs e construction_cost
        all_inputs = concepts + methods + knowledge_bases + tools + external_domains + validations
        missing = [iid for iid in all_inputs if not self.library.has(iid)]
        total = len(all_inputs) if all_inputs else 1
        cost = len(missing) / total

        return CapabilityUnit(
            capability_id=capability_id,
            capability_name=capability_id,
            concepts=concepts,
            methods=methods,
            knowledge_bases=knowledge_bases,
            tools=tools,
            external_domains=external_domains,
            validations=validations,
            missing_inputs=missing,
            construction_cost=round(cost, 4),
            frontier=False,
        )

    def decompose(self, capability_id: str, domain: str = "") -> CapabilityUnit:
        """Decompõe uma capacidade em insumos cognitivos.

        Args:
            capability_id: Identificador da capacidade (ex.: "metodos.Quantitativo experimental")
            domain: Domínio de conhecimento (ex.: "psicologia") — usado para refinar templates

        Returns:
            CapabilityUnit com a decomposição completa
        """
        category = self._extract_category(capability_id)

        # Estratégia 1: Template por categoria
        unit = self._apply_template(category, capability_id)
        if unit is not None:
            return unit

        # Estratégia 2: [Futuro] Analogia Polimática

        # Estratégia 3: [Futuro] Decomposição Generativa

        # Fallback: Frontier
        return CapabilityUnit(
            capability_id=capability_id,
            capability_name=capability_id,
            frontier=True,
            construction_cost=1.0,
        )

    def decompose_many(
        self, capability_ids: list[str], domain: str = ""
    ) -> dict[str, CapabilityUnit]:
        """Decompõe múltiplas capacidades. Retorna dicionário capability_id → CapabilityUnit."""
        return {cid: self.decompose(cid, domain) for cid in capability_ids}

    def compute_shared_inputs(
        self, units: dict[str, CapabilityUnit]
    ) -> dict[str, InputNode]:
        """Constrói grafo de insumos compartilhados entre múltiplas CapabilityUnits.

        Args:
            units: Dicionário capability_id → CapabilityUnit

        Returns:
            Dicionário input_id → InputNode com shared_by populado
        """
        input_nodes: dict[str, InputNode] = {}

        for cid, unit in units.items():
            for iid in unit.all_inputs:
                if iid not in input_nodes:
                    inp = self.library.get(iid)
                    input_nodes[iid] = InputNode(
                        input_id=iid,
                        input_type=inp.input_type if inp else "unknown",
                        exists=self.library.has(iid),
                    )
                input_nodes[iid].shared_by.add(cid)

        return input_nodes

    def compute_total_construction_cost(
        self, units: dict[str, CapabilityUnit]
    ) -> float:
        """Calcula custo total de construção considerando inputs compartilhados.

        Inputs usados por múltiplas capabilities são contados apenas uma vez.
        """
        input_nodes = self.compute_shared_inputs(units)
        missing_unique = sum(
            1 for node in input_nodes.values()
            if not node.exists and len(node.shared_by) > 0
        )
        total_unique = len(input_nodes)
        if total_unique == 0:
            return 0.0
        return round(missing_unique / total_unique, 4)


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════════════

def create_composer_with_seed_library(
    base_dir: str | Path | None = None,
) -> CapabilityComposer:
    """Factory: cria CapabilityComposer com biblioteca seed completa.

    Carrega cognitive_library.json + bootstrap de evo-*.md + bootstrap de skills.
    """
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent  # academic-audit dir

    base_dir = Path(base_dir)

    # Tenta localizar a raiz do ecossistema
    ecosystem_root = base_dir
    while ecosystem_root.parent != ecosystem_root:
        if (ecosystem_root / "skills").exists() and (ecosystem_root / "evolution").exists():
            break
        ecosystem_root = ecosystem_root.parent

    lib = CognitiveLibrary()

    # 1. Carrega biblioteca seed
    seed_path = base_dir / "cognitive_library.json"
    if seed_path.exists():
        try:
            lib.load_json(seed_path)
        except Exception:
            pass

    # 2. Bootstrap de evo-*.md
    evo_dir = ecosystem_root / "evolution"
    if evo_dir.exists():
        try:
            evo_lib = CognitiveLibrary.bootstrap_from_evos(evo_dir)
            for inp_id in evo_lib.input_ids:
                inp = evo_lib.get(inp_id)
                if inp and not lib.has(inp_id):
                    lib.add(inp)
        except Exception:
            pass

    # 3. Bootstrap de skills
    skills_dir = ecosystem_root / "skills"
    if skills_dir.exists():
        try:
            skill_lib = CognitiveLibrary.bootstrap_from_skills(skills_dir)
            for inp_id in skill_lib.input_ids:
                inp = skill_lib.get(inp_id)
                if inp and not lib.has(inp_id):
                    lib.add(inp)
        except Exception:
            pass

    return CapabilityComposer(lib)
