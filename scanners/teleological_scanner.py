#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TeleologicalReverseScanner v1.0 — Scanner Teleologico Reverso
==============================================================

Complementa o NoologicalScanner com inferencia prescritiva:
  - Dados os OBJETIVOS da pesquisa, infere QUAIS dimensoes epistemologicas
    sao necessarias (principio teleologico)
  - Compara o requerido com o existente (scan noologico)
  - Identifica GAPS TELEOLOGICOS: dimensoes que DEVERIAM estar cobertas
    mas NAO ESTAO

Pipeline:
  1. set_goals(goals) → infer_requirements() → lista de requisitos
  2. compare_with_scan(noological_results) → lista de gaps
  3. generate_report() → markdown

Autor: Marcelo Claro Laranjeira (2026)
Integrado com: NoologicalScanner v3.0 (SPEC-028)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

BRAZIL_TZ = timezone.utc


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TeleologicalGoal:
    """Objetivo de pesquisa com tipo teleologico."""
    description: str
    goal_type: str
    weight: float = 1.0

    def __post_init__(self):
        valid_types = list(TELEOLOGICAL_MAPPINGS.keys())
        if self.goal_type not in valid_types:
            import warnings
            warnings.warn(
                f"Goal type '{self.goal_type}' nao reconhecido. "
                f"Tipos validos: {valid_types}. Nenhum requisito sera inferido."
            )


@dataclass
class DimensionRequirement:
    """Requisito teleologico: uma categoria que DEVE estar presente."""
    dim_key: str
    category: str
    weight: float          # 0.0–1.0 (quao essencial)
    rationale: str
    goal_description: str  # qual objetivo gerou este requisito


@dataclass
class TeleologicalGap:
    """Gap teleologico: categoria requerida mas ausente no scan."""
    goal: str
    dim_key: str
    category: str
    required_weight: float
    severity: str          # "critical" | "high" | "moderate" | "low"
    rationale: str
    actual_density: float = 0.0  # densidade real da dimensao (do scan)


# ═══════════════════════════════════════════════════════════════════════════
# MAPEAMENTOS TELEOLÓGICOS (Goal Type → Required Categories)
# ═══════════════════════════════════════════════════════════════════════════

# Cada entrada: (dim_key, category, weight, rationale)
# weight: 1.0 = essencial, 0.5 = desejavel

TELEOLOGICAL_MAPPINGS: dict[str, list[tuple[str, str, float, str]]] = {
    "causal": [
        ("metodos", "Quantitativo experimental", 1.0,
         "Relações causais exigem controle experimental e randomização"),
        ("temporalidade", "Longitudinal (longo prazo)", 0.8,
         "Causalidade requer observação temporal para estabelecer precedência"),
        ("raciocinio", "Probabilístico", 0.7,
         "Inferência causal é intrinsecamente probabilística"),
        ("raciocinio", "Contrafactual", 0.6,
         "Contrafactuais são a base lógica da causalidade (Rubin, Pearl)"),
        ("dados", "Dados longitudinais", 0.7,
         "Dados de painel ou coorte são necessários para inferência causal"),
        ("metodos", "Quantitativo correlacional", 0.5,
         "Correlação é pré-condição (embora não suficiente) para causalidade"),
    ],
    "evaluative": [
        ("metodos", "Misto sequencial", 0.9,
         "Avaliação de intervenções requer triangulação quali+quanti"),
        ("metodos", "Misto convergente", 0.8,
         "Convergência de métodos fortalece validade da avaliação"),
        ("paradigmas", "Pragmatista", 0.8,
         "Paradigma pragmatista é o fundamento epistemológico da avaliação"),
        ("populacao", "Contexto clínico", 0.7,
         "Avaliação de intervenções tipicamente ocorre em contexto aplicado"),
        ("dados", "Dados clínicos (escalas, inventários)", 0.8,
         "Instrumentos padronizados são necessários para mensurar outcomes"),
        ("metodos", "Revisão sistemática", 0.6,
         "Revisões sistemáticas contextualizam a intervenção na literatura"),
        ("temporalidade", "Longitudinal (curto prazo)", 0.6,
         "Follow-up é necessário para avaliar manutenção de efeitos"),
    ],
    "exploratory": [
        ("paradigmas", "Fenomenológico", 1.0,
         "Exploração de experiências requer lente fenomenológica"),
        ("paradigmas", "Construtivista", 0.8,
         "Construção de significado é central na pesquisa exploratória"),
        ("metodos", "Qualitativo fenomenológico", 1.0,
         "Métodos qualitativos são essenciais para capturar experiência vivida"),
        ("metodos", "Qualitativo grounded theory", 0.7,
         "Grounded theory permite que categorias emerjam dos dados"),
        ("dados", "Dados qualitativos (entrevistas)", 1.0,
         "Entrevistas e grupos focais são a fonte primária na pesquisa exploratória"),
        ("raciocinio", "Abdutivo", 0.6,
         "Abdução gera hipóteses a partir de padrões observados"),
        ("raciocinio", "Indutivo", 0.5,
         "Indução permite generalização a partir de casos particulares"),
    ],
    "strategic": [
        ("teoria_jogos", "Equilíbrio de Nash", 1.0,
         "Nash é o conceito fundacional de interação estratégica"),
        ("teoria_jogos", "Bayesiano", 0.9,
         "Jogos bayesianos modelam decisão sob informação incompleta"),
        ("teoria_jogos", "Evolutivo", 0.7,
         "Jogos evolutivos modelam dinâmicas de adaptação estratégica"),
        ("raciocinio", "Contrafactual", 0.8,
         "Raciocínio contrafactual avalia cenários alternativos"),
        ("raciocinio", "Probabilístico", 0.7,
         "Decisão estratégica é intrinsecamente probabilística"),
        ("niveis_analise", "Sistêmico/político", 0.6,
         "Decisões estratégicas frequentemente envolvem análise sistêmica"),
        ("teoria_jogos", "Cooperativo", 0.6,
         "Coalizões e barganha são centrais em contextos cooperativos"),
    ],
    "comparative": [
        ("populacao", "Cross-cultural", 1.0,
         "Comparação entre culturas requer amostragem cross-cultural"),
        ("populacao", "Brasil/América Latina", 0.8,
         "Contexto LATAM é relevante para pesquisa comparativa na região"),
        ("dados", "Dados comparativos (cross-cultural)", 1.0,
         "Dados comparativos são a essência da pesquisa cross-cultural"),
        ("dominios", "Antropologia", 0.6,
         "Antropologia fornece framework para comparação cultural"),
        ("metodos", "Misto sequencial", 0.6,
         "Métodos mistos permitem comparação em múltiplos níveis"),
        ("temporalidade", "Transversal (momento único)", 0.5,
         "Comparações transversais são o design mais comum"),
    ],
    "predictive": [
        ("temporalidade", "Prospectivo/preditivo", 1.0,
         "Predição requer orientação temporal para o futuro"),
        ("dados", "Dados longitudinais", 1.0,
         "Modelos preditivos exigem dados de painel ou coorte"),
        ("raciocinio", "Probabilístico", 0.9,
         "Predição é fundamentalmente probabilística"),
        ("metodos", "Quantitativo correlacional", 0.7,
         "Modelos de regressão são a base da predição estatística"),
        ("dados", "Dados epidemiológicos", 0.6,
         "Dados populacionais alimentam modelos preditivos"),
        ("dados", "Metadados (revisões)", 0.5,
         "Meta-análises fornecem estimativas pooled para predição"),
    ],
    "integrative": [
        ("dominios", "Neurociências", 0.7,
         "Integração frequentemente requer ponte entre psicologia e neurociência"),
        ("dominios", "Sociologia", 0.6,
         "Fenômenos complexos exigem lente sociológica"),
        ("dominios", "Inteligência Artificial / Tecnologia", 0.6,
         "IA é domínio emergente para síntese de conhecimento"),
        ("paradigmas", "Complexo/Sistêmico", 0.8,
         "Paradigma da complexidade é o fundamento da integração"),
        ("raciocinio", "Sistêmico", 0.7,
         "Pensamento sistêmico conecta domínios dispares"),
        ("metodos", "Revisão sistemática", 0.7,
         "Revisões sistemáticas são o método padrão para síntese"),
        ("teoria_jogos", "Cooperativo", 0.5,
         "Coalizões interdisciplinares podem ser modeladas como jogos cooperativos"),
    ],
    "critical": [
        ("paradigmas", "Crítico/Transformador", 1.0,
         "Paradigma crítico é essencial para questionar estruturas de poder"),
        ("paradigmas", "Pós-estruturalista", 0.8,
         "Desconstrução de discursos requer lente pós-estruturalista"),
        ("niveis_analise", "Sistêmico/político", 0.7,
         "Análise crítica opera no nível sistêmico e político"),
        ("populacao", "Diversidade de gênero", 0.5,
         "Interseccionalidade requer atenção à diversidade"),
        ("dominios", "Sociologia", 0.6,
         "Sociologia fornece ferramentas para análise estrutural"),
        ("raciocinio", "Dialético", 0.7,
         "Dialética é o modo de raciocínio da transformação social"),
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# SCANNER TELEOLÓGICO REVERSO
# ═══════════════════════════════════════════════════════════════════════════

class TeleologicalReverseScanner:
    """Scanner que infere requisitos epistemologicos a partir dos objetivos.

    Principio teleologico:
      "Se o objetivo da pesquisa e X, entao por necessidade logica
       as dimensoes A, B, C devem estar cobertas."

    Pipeline:
      1. set_goals(goals) → define os objetivos da pesquisa
      2. infer_requirements() → mapeia goals → dimensoes requeridas
      3. compare_with_scan(noological_results) → identifica gaps
      4. generate_report() → relatorio teleologico
    """

    def __init__(self):
        self.goals: list[TeleologicalGoal] = []
        self.requirements: list[DimensionRequirement] = []
        self.gaps: list[TeleologicalGap] = []
        self._scan_results: dict[str, Any] = {}
        self._teleological_score: float = 0.0

    # ─── GOAL MANAGEMENT ─────────────────────────────────────────────────

    def set_goals(self, goals: list[TeleologicalGoal]) -> None:
        """Define os objetivos da pesquisa."""
        self.goals = goals
        self.requirements = []
        self.gaps = []
        self._scan_results = {}
        self._teleological_score = 0.0

    # ─── INFERENCE ENGINE ─────────────────────────────────────────────────

    def infer_requirements(self) -> list[DimensionRequirement]:
        """Infere requisitos teleologicos a partir dos objetivos.

        Para cada goal, consulta TELEOLOGICAL_MAPPINGS e gera
        DimensionRequirement com peso, racional e goal_description.
        Requisitos duplicados (mesmo dim_key + category) tem seus
        pesos somados e racionais concatenados.
        """
        self.requirements = []
        seen: dict[tuple[str, str], list[DimensionRequirement]] = {}

        for goal in self.goals:
            if goal.goal_type not in TELEOLOGICAL_MAPPINGS:
                continue
            mappings = TELEOLOGICAL_MAPPINGS[goal.goal_type]
            for dim_key, category, weight, rationale in mappings:
                effective_weight = weight * goal.weight
                req = DimensionRequirement(
                    dim_key=dim_key,
                    category=category,
                    weight=effective_weight,
                    rationale=rationale,
                    goal_description=goal.description,
                )
                key = (dim_key, category)
                if key not in seen:
                    seen[key] = []
                seen[key].append(req)

        # Consolidar duplicatas: soma pesos, concatena racionais
        for key, reqs in seen.items():
            if len(reqs) == 1:
                self.requirements.append(reqs[0])
            else:
                total_weight = min(1.0, sum(r.weight for r in reqs))
                combined_rationale = " | ".join(r.rationale for r in reqs)
                combined_goals = "; ".join(r.goal_description for r in reqs)
                self.requirements.append(DimensionRequirement(
                    dim_key=key[0],
                    category=key[1],
                    weight=total_weight,
                    rationale=combined_rationale,
                    goal_description=combined_goals,
                ))

        # Ordenar por peso decrescente
        self.requirements.sort(key=lambda r: r.weight, reverse=True)
        return self.requirements

    # ─── GAP DETECTION ────────────────────────────────────────────────────

    def compare_with_scan(self, noological_results: dict[str, Any]) -> list[TeleologicalGap]:
        """Compara requisitos teleologicos com scan noologico real.

        Para cada requisito inferido, verifica se a categoria esta
        presente no scan. Se nao estiver, gera um TeleologicalGap.

        Args:
            noological_results: saida de NoologicalScanner.scan()
        """
        self._scan_results = noological_results
        if not self.requirements:
            self.infer_requirements()

        self.gaps = []
        dims = noological_results.get("dimensions", {})

        for req in self.requirements:
            dim_data = dims.get(req.dim_key, {})
            covered = dim_data.get("covered", [])
            actual_density = dim_data.get("density", 0.0)

            if req.category not in covered:
                severity = self._severity(req.weight)
                self.gaps.append(TeleologicalGap(
                    goal=req.goal_description,
                    dim_key=req.dim_key,
                    category=req.category,
                    required_weight=round(req.weight, 2),
                    severity=severity,
                    rationale=req.rationale,
                    actual_density=actual_density,
                ))

        # Ordenar por severidade → peso
        severity_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3}
        self.gaps.sort(key=lambda g: (severity_order.get(g.severity, 4), -g.required_weight))

        # Calcular score teleologico
        self._calc_score()
        return self.gaps

    def _severity(self, weight: float) -> str:
        """Classifica severidade do gap baseado no peso do requisito."""
        if weight >= 0.9:
            return "critical"
        if weight >= 0.7:
            return "high"
        if weight >= 0.4:
            return "moderate"
        return "low"

    def _calc_score(self) -> None:
        """Calcula teleological_score: % de requisitos atendidos."""
        if not self.requirements:
            self._teleological_score = 1.0
            return

        total_weight = sum(r.weight for r in self.requirements)
        if total_weight == 0:
            self._teleological_score = 1.0
            return

        # Soma pesos dos requisitos atendidos
        dims = self._scan_results.get("dimensions", {})
        covered_weight = 0.0
        for req in self.requirements:
            dim_data = dims.get(req.dim_key, {})
            covered = dim_data.get("covered", [])
            if req.category in covered:
                covered_weight += req.weight

        self._teleological_score = round(covered_weight / total_weight, 3)

    def teleological_score(self) -> float:
        """Retorna o score teleologico (0.0–1.0)."""
        return self._teleological_score

    # ─── REPORTING ────────────────────────────────────────────────────────

    def generate_report(self) -> str:
        """Gera relatorio Markdown do scan teleologico reverso."""
        if not self.goals:
            return "Nenhum objetivo definido. Use set_goals() primeiro."

        lines = [
            "# Scanner Teleológico Reverso — Relatório de Alinhamento Epistemológico",
            "",
            f"**Data**: {datetime.now(BRAZIL_TZ).isoformat()[:19]}",
            f"**Score Teleológico**: {self._teleological_score:.0%} "
            f"({sum(1 for r in self.requirements if self._is_met(r))}/{len(self.requirements)} requisitos atendidos)",
            "",
            "---",
            "",
            "## Objetivos da Pesquisa",
            "",
        ]

        for i, goal in enumerate(self.goals, 1):
            lines.append(f"{i}. **[{goal.goal_type}]** {goal.description} "
                        f"(peso: {goal.weight})")

        lines.extend([
            "",
            "---",
            "",
            f"## Requisitos Teleológicos ({len(self.requirements)})",
            "",
            "| # | Dimensão | Categoria | Peso | Status |",
            "|:--:|----------|-----------|:----:|:------:|",
        ])

        for i, req in enumerate(self.requirements, 1):
            met = self._is_met(req)
            status = "✓ Coberto" if met else "✗ Gap"
            lines.append(f"| {i} | {req.dim_key} | {req.category} | "
                        f"{req.weight:.1f} | {status} |")

        lines.extend([
            "",
            "---",
            "",
            f"## Gaps Teleológicos ({len(self.gaps)})",
            "",
        ])

        if not self.gaps:
            lines.append("✅ **Nenhum gap teleológico detectado.** "
                         "A pesquisa cobre todas as dimensões necessárias para seus objetivos.")
        else:
            # Agrupar por severidade
            for severity in ["critical", "high", "moderate", "low"]:
                sev_gaps = [g for g in self.gaps if g.severity == severity]
                if not sev_gaps:
                    continue
                emoji = {"critical": "🔴", "high": "🟠", "moderate": "🟡", "low": "⚪"}
                lines.append(f"### {emoji.get(severity, '')} {severity.upper()} ({len(sev_gaps)})")
                lines.append("")
                for g in sev_gaps:
                    lines.append(f"- **{g.category}** `[{g.dim_key}]` — peso: {g.required_weight}")
                    lines.append(f"  > {g.rationale}")
                    lines.append(f"  > _Objetivo: {g.goal}_")
                    lines.append("")

        lines.extend([
            "---",
            "",
            "## Recomendações de Alinhamento Teleológico",
            "",
        ])

        if self.gaps:
            critical_gaps = [g for g in self.gaps if g.severity == "critical"]
            if critical_gaps:
                lines.append("### Ações Prioritárias (Gaps Críticos)")
                for g in critical_gaps[:5]:
                    lines.append(f"- **Incorporar {g.category}** na dimensão `{g.dim_key}`: {g.rationale}")
                lines.append("")

            high_gaps = [g for g in self.gaps if g.severity == "high"]
            if high_gaps:
                lines.append("### Ações Recomendadas (Gaps Altos)")
                for g in high_gaps[:5]:
                    lines.append(f"- Expandir cobertura de **{g.category}** `[{g.dim_key}]`")
                lines.append("")
        else:
            lines.append("A pesquisa está teleologicamente alinhada com seus objetivos. "
                         "Nenhuma ação corretiva necessária.")

        lines.extend([
            "",
            "---",
            "",
            f"*Relatório gerado pelo TeleologicalReverseScanner v1.0 — "
            f"{datetime.now(BRAZIL_TZ).isoformat()[:19]}*",
        ])

        return "\n".join(lines)

    def _is_met(self, req: DimensionRequirement) -> bool:
        """Verifica se um requisito foi atendido no scan."""
        if not self._scan_results:
            return False
        dims = self._scan_results.get("dimensions", {})
        dim_data = dims.get(req.dim_key, {})
        covered = dim_data.get("covered", [])
        return req.category in covered

    def save_report(self, output_path: str) -> None:
        """Salva relatorio em disco."""
        from pathlib import Path
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generate_report(), encoding="utf-8")
