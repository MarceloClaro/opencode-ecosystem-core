#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KnowledgeComposition v1.0 — Composição Unitária do Conhecimento (R490)

Proposta do usuário (camada Composição Unitária): assim como uma parede não é
apenas uma atividade — mas tijolos, cimento, areia, mão de obra, equipamentos e
tempo — uma capacidade futura não é um elemento indivisível: possui insumos
cognitivos que precisam existir para construí-la.

    Scanner Reverso (R483):  "O que precisará existir?"
    Trajectory Mapper (R485): "Em que ordem?"
    KnowledgeComposition:    "DO QUE isso é feito?"

Insights por capacidade (6 classes de insumo):
    conceitos    — elementos teóricos (ex.: efeito de tamanho, axioma, causalidade)
    metodos      — procedimentos (ex.: síntese quantitativa, dedução simbólica)
    bases        — conteúdo (ex.: artigos primários, manuais, normas)
    ferramentas  — mecanismos operacionais (ex.: solver simbólico, agentes)
    dominios     — especialistas/domínios de apoio (ex.: estatística, neurociência)
    validacoes   — critérios de verificação (ex.: I², prova formal, benchmark)

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

from dataclasses import dataclass, field
from typing import Any

from scanners.reverse_scanner import ReverseScanner


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


@dataclass
class CompositionReport:
    """Relatório de composição unitária por lacuna do gap."""
    target_state: list[str]
    evolution_gap: list[str]
    matches: list["CompositionInsight"]
    by_capability: dict[str, "CompositionInsight"]
    params: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class KnowledgeComposition:
    """Decompõe cada capacidade futura em insumos cognitivos construíveis."""

    _TOKEN_SPLIT = lambda self, s: [t for t in s.lower().replace("-", " ").split() if t]

    def compose(self, capability: str) -> CompositionInsight:
        """Insumos de `capability`: curados (bank) ou derivados (lexical)."""
        if capability in COMPOSITION_BANK:
            entry = COMPOSITION_BANK[capability]
            return CompositionInsight(
                capability=capability,
                conceitos=list(entry.get("conceitos", [])),
                metodos=list(entry.get("metodos", [])),
                bases=list(entry.get("bases", [])),
                ferramentas=list(entry.get("ferramentas", [])),
                dominios=list(entry.get("dominios", [])),
                validacoes=list(entry.get("validacoes", [])),
                origem="bank",
                fonte_conceitos="bank:curada",
            )
        return self._lexical(capability)

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