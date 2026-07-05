#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EvolutionaryScannerPipeline v1.0 — Scanner de Trajetórias Evolutivas

Orquestra 5 módulos:
  M1: NoologicalScanner (SPEC-028) — "O que não existe?"
  M2: TeleologicalReverseScanner (SPEC-029) — "O que deveria existir?"
  M3: CrossValidationEngine — "O que sustenta o quê?"
  M4: PolymathicConvergence — "Quem já resolveu isso?"
  M5: TrajectoryMapper — "Qual o melhor caminho?"

Pipeline completo:
  scan(audit_trail, goals, domain) → EvolutionaryRoadmap
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SequencingStep:
    """Passo no sequenciamento lógico de construção de capacidades."""
    category: str
    domain: str
    phase: int
    predecessors: list[str]
    successors: list[str]
    can_run_in_parallel_with: list[str]
    cost: float = 0.0
    analogy_principle: str = ""
    analogy_domain: str = ""


@dataclass
class EvolutionarySequencing:
    """Resultado do sequenciamento evolutivo de capacidades."""
    total_phases: int
    logical_sequence: list[str]
    phases: dict[int, list[str]]
    steps: list[SequencingStep]
    timeline: list[str]


@dataclass
class PolymathicAnalogy:
    """Solução análoga encontrada em domínio externo."""
    gap_category: str         # categoria com gap
    external_domain: str      # "Neurociência", "Biologia Evolutiva", etc.
    analogous_problem: str    # descrição do problema análogo
    transferable_principle: str  # princípio transferível
    transferability_score: float  # 0-1


@dataclass
class EvolutionaryScenario:
    """Cenário de evolução para uma capacidade."""
    category: str
    domain: str
    scenario_type: str        # "quick_win" | "foundation" | "frontier" | "convergent"
    priority_score: float     # 0-1
    cascade_impact: float     # quantas capacidades desbloqueia
    prerequisites: list[str]  # capacidades necessárias antes
    analogies: list[PolymathicAnalogy] = field(default_factory=list)
    required_inputs: list[str] = field(default_factory=list)  # SPEC-033: input_ids necessários


@dataclass
class EvolutionaryRoute:
    """Rota de evolução: sequência ordenada de capacidades a adquirir."""
    name: str
    description: str
    steps: list[EvolutionaryScenario]
    total_priority: float
    estimated_impact: float


@dataclass
class EvolutionaryRoadmap:
    """Roadmap evolutivo completo."""
    noological_coverage: float       # 0-1
    teleological_score: float        # 0-1
    bottlenecks: list[str]           # top 5 bottlenecks
    analogies: list[PolymathicAnalogy]
    scenarios: list[EvolutionaryScenario]
    routes: list[EvolutionaryRoute]
    total_gaps: int
    quick_wins: int
    foundations: int
    frontiers: int
    convergents: int
    capability_units: list[Any] = field(default_factory=list)  # SPEC-033: CapabilityUnit[]
    total_construction_cost: float = 0.0  # SPEC-033
    sequencing: EvolutionarySequencing | None = None


# ═══════════════════════════════════════════════════════════════════════════
# MÓDULO 4 — CONVERGÊNCIA POLIMÁTICA
# ═══════════════════════════════════════════════════════════════════════════

POLYMATHIC_MAPPINGS: dict[str, list[tuple[str, str, str, float]]] = {
    # gap_category → [(external_domain, analogous_problem, transferable_principle, score)]
    "raciocinio.Probabilístico": [
        ("Neurociência", "Inferência bayesiana no córtex",
         "Redes neurais biológicas implementam inferência probabilística naturalmente", 0.9),
        ("Economia Comportamental", "Teoria da decisão sob incerteza",
         "Modelos formais de escolha sob risco (Kahneman & Tversky)", 0.85),
        ("Física", "Mecânica estatística",
         "Distribuições de probabilidade sobre ensembles de partículas", 0.7),
    ],
    "raciocinio.Contrafactual": [
        ("Filosofia", "Mundos possíveis (Lewis, Kripke)",
         "Semântica de mundos possíveis para raciocínio contrafactual", 0.8),
        ("Linguística", "Condicionais contrafactuais",
         "Gramática de condicionais irreais em línguas naturais", 0.7),
    ],
    "raciocinio.Sistêmico": [
        ("Biologia", "Teoria de sistemas vivos (Maturana, Varela)",
         "Autopoiese e acoplamento estrutural", 0.9),
        ("Ecologia", "Ecossistemas e redes tróficas",
         "Interdependência e equilíbrio dinâmico em ecossistemas", 0.85),
    ],
    "raciocinio.Metacognitivo": [
        ("Ciência Cognitiva", "Monitoramento metacognitivo",
         "Capacidade humana de avaliar a própria incerteza", 0.9),
        ("Inteligência Artificial", "Agentes reflexivos",
         "Arquiteturas de agentes com auto-monitoramento", 0.85),
    ],
    "teoria_jogos.Equilíbrio de Nash": [
        ("Economia", "Teoria dos jogos não-cooperativos",
         "Equilíbrio como solução de jogos estratégicos", 1.0),
        ("Biologia Evolutiva", "Estratégias evolutivamente estáveis (ESS)",
         "Maynard Smith — seleção natural como jogo", 0.9),
    ],
    "teoria_jogos.Evolutivo": [
        ("Biologia Evolutiva", "Dinâmica de replicadores",
         "Equações de replicador-mutador para populações", 0.95),
        ("Ecologia", "Coevolução predador-presa",
         "Ciclos de adaptação mútua em ecossistemas", 0.8),
    ],
    "teoria_jogos.Cooperativo": [
        ("Sociologia", "Ação coletiva e bens públicos",
         "Ostrom — governança de recursos comuns", 0.9),
        ("Biologia", "Altruísmo e seleção de parentesco",
         "Hamilton — cooperação emerge de parentesco genético", 0.8),
    ],
    "paradigmas.Complexo/Sistêmico": [
        ("Física", "Sistemas complexos e criticalidade auto-organizada",
         "Bak — emergência de ordem em sistemas longe do equilíbrio", 0.9),
        ("Biologia", "Biologia de sistemas",
         "Redes de regulação gênica como sistemas complexos", 0.85),
    ],
    "paradigmas.Fenomenológico": [
        ("Filosofia", "Fenomenologia (Husserl, Merleau-Ponty)",
         "Redução fenomenológica e intencionalidade da consciência", 1.0),
        ("Artes", "Estética da experiência",
         "A arte como modo de acesso à experiência vivida", 0.7),
    ],
    "metodos.Qualitativo fenomenológico": [
        ("Antropologia", "Etnografia e observação participante",
         "Malinowski, Geertz — descrição densa da experiência cultural", 0.9),
        ("Ciências da Saúde", "Fenomenologia clínica",
         "Jaspers — método fenomenológico em psicopatologia", 0.8),
    ],
    "dados.Dados longitudinais": [
        ("Epidemiologia", "Estudos de coorte",
         "Framingham Heart Study — acompanhamento populacional de décadas", 0.95),
        ("Economia", "Dados em painel",
         "Panel data econometrics — efeitos fixos e aleatórios", 0.8),
    ],
    "temporalidade.Longitudinal (longo prazo)": [
        ("Psicologia do Desenvolvimento", "Estudos longitudinais de ciclo de vida",
         "Baltes — lifespan developmental psychology", 0.9),
        ("Astronomia", "Observações de ciclo longo",
         "Registros astronômicos milenares para detecção de padrões", 0.6),
    ],
    # ─── v2.0: novos dominios (10 adicionais) ───────────────────────────
    "paradigmas.Pós-estruturalista": [
        ("Literatura", "Desconstrução textual (Derrida)",
         "Estratégias de leitura que expõem hierarquias implícitas", 0.85),
        ("Arquitetura", "Desconstrução arquitetônica (Eisenman)",
         "Formas que desafiam a estabilidade estrutural", 0.7),
    ],
    "raciocinio.Dedutivo": [
        ("Matemática", "Prova formal e sistemas axiomáticos",
         "Dedução como método de construção de conhecimento certo", 1.0),
        ("Ciência da Computação", "Verificação formal de programas",
         "Provas de correção usando lógica formal", 0.9),
    ],
    "raciocinio.Indutivo": [
        ("Ciência de Dados", "Aprendizado de máquina supervisionado",
         "Indução de padrões a partir de exemplos rotulados", 0.9),
        ("Genética", "Estudos de associação genômica (GWAS)",
         "Indução de variantes genéticas associadas a fenótipos", 0.8),
    ],
    "metodos.Revisão sistemática": [
        ("Medicina", "Medicina baseada em evidências (Cochrane)",
         "Protocolos PRISMA para síntese rigorosa de evidências", 1.0),
        ("Engenharia de Software", "Systematic Literature Reviews (SLR)",
         "Protocolos Kitchenham para revisões em engenharia de software", 0.85),
    ],
    "metodos.Meta-análise": [
        ("Epidemiologia", "Meta-análise de ensaios clínicos",
         "Modelos de efeitos fixos e aleatórios para síntese quantitativa", 1.0),
        ("Economia", "Meta-regressão em economia",
         "Síntese de elasticidades e efeitos de tratamento", 0.8),
    ],
    "niveis_analise.Sistêmico/político": [
        ("Ciência Política", "Análise de políticas públicas",
         "Modelos de ciclo de políticas e advocacy coalitions", 0.85),
        ("Ecologia", "Ecologia de paisagens e governança ambiental",
         "Sistemas socioecológicos e resiliência (Ostrom)", 0.8),
    ],
    "temporalidade.Transversal (momento único)": [
        ("Epidemiologia", "Estudos transversais de prevalência",
         "Inquéritos populacionais para estimar prevalência pontual", 0.9),
        ("Sociologia", "Surveys sociais transversais",
         "General Social Survey — retratos instantâneos da sociedade", 0.8),
    ],
    "populacao.Adultos": [
        ("Medicina", "Ensaios clínicos em população adulta",
         "Triagens de fase III com critérios de inclusão por idade", 0.9),
        ("Economia", "Economia do trabalho",
         "Estudos sobre participação na força de trabalho adulta", 0.7),
    ],
    "populacao.Infância": [
        ("Psicologia do Desenvolvimento", "Marcos do desenvolvimento infantil",
         "Piaget, Vygotsky — estágios de desenvolvimento cognitivo", 0.95),
        ("Pediatria", "Crescimento e desenvolvimento pediátrico",
         "Curvas de crescimento da OMS e marcos motores", 0.9),
    ],
    "dados.Dados epidemiológicos": [
        ("Saúde Pública", "Vigilância epidemiológica",
         "Sistemas de notificação compulsória e análise de surtos", 1.0),
        ("Climatologia", "Modelagem de propagação de doenças vetoriais",
         "Mapas de risco climático para dengue, malária, zika", 0.7),
    ],
}


class PolymathicConvergence:
    """Módulo 4: Descobre soluções em domínios externos que resolveram problemas análogos."""

    def find_analogies(self, gaps: list[Any]) -> list[PolymathicAnalogy]:
        """Para cada gap teleológico, busca analogias em domínios externos.

        Args:
            gaps: lista de TeleologicalGap do TeleologicalReverseScanner
        """
        analogies: list[PolymathicAnalogy] = []
        seen: set[tuple[str, str]] = set()

        for gap in gaps:
            gap_key = f"{gap.dim_key}.{gap.category}"
            if gap_key in POLYMATHIC_MAPPINGS:
                for ext_domain, problem, principle, score in POLYMATHIC_MAPPINGS[gap_key]:
                    key = (gap_key, ext_domain)
                    if key not in seen:
                        seen.add(key)
                        analogies.append(PolymathicAnalogy(
                            gap_category=gap_key,
                            external_domain=ext_domain,
                            analogous_problem=problem,
                            transferable_principle=principle,
                            transferability_score=score,
                        ))

        analogies.sort(key=lambda a: a.transferability_score, reverse=True)
        return analogies


# ═══════════════════════════════════════════════════════════════════════════
# MÓDULO 5 — MAPA DE TRAJETÓRIAS EVOLUTIVAS
# ═══════════════════════════════════════════════════════════════════════════

class TrajectoryMapper:
    """Módulo 5: Transforma gaps + dependências + analogias em cenários e rotas."""

    def classify_scenario(self, category: str, domain: str,
                          cascade_impact: float,
                          prerequisites: list[str],
                          has_analogy: bool) -> EvolutionaryScenario:
        """Classifica uma capacidade em um tipo de cenário evolutivo.

        Tipos:
          - quick_win: cascade_impact > 0.5, <= 1 prerequisite
          - foundation: é bottleneck (prerequisite de >2)
          - convergent: tem analogia com transferability > 0.8
          - frontier: requer >2 prerequisites
        """
        priority = self._calc_priority(cascade_impact, len(prerequisites), has_analogy)
        
        if has_analogy and cascade_impact > 0.3:
            scenario_type = "convergent"
        elif cascade_impact > 0.5 and len(prerequisites) <= 1:
            scenario_type = "quick_win"
        elif len(prerequisites) > 2:
            scenario_type = "frontier"
        else:
            scenario_type = "foundation"

        return EvolutionaryScenario(
            category=category,
            domain=domain,
            scenario_type=scenario_type,
            priority_score=priority,
            cascade_impact=cascade_impact,
            prerequisites=prerequisites,
        )

    def _calc_priority(self, cascade_impact: float, n_prereqs: int,
                       has_analogy: bool) -> float:
        """priority_score = cascade*0.35 + transferability*0.25 + feasibility*0.40"""
        transferability = 0.8 if has_analogy else 0.1
        feasibility = 1.0 / (1.0 + n_prereqs)
        score = (cascade_impact * 0.35) + (transferability * 0.25) + (feasibility * 0.40)
        return round(min(1.0, score), 2)

    def generate_routes(self, scenarios: list[EvolutionaryScenario],
                        max_routes: int = 3) -> list[EvolutionaryRoute]:
        """Gera rotas de evolução a partir dos cenários.

        Estratégia: ordenar cenários por priority_score, agrupar por tipo,
        e gerar rotas que priorizem quick_wins e foundations antes de frontiers.
        """
        if not scenarios:
            return []

        sorted_scenarios = sorted(scenarios, key=lambda s: s.priority_score, reverse=True)
        
        routes: list[EvolutionaryRoute] = []
        
        # Rota A: Quick-wins → Foundations → Convergents → Frontiers
        qw = [s for s in sorted_scenarios if s.scenario_type == "quick_win"]
        fo = [s for s in sorted_scenarios if s.scenario_type == "foundation"]
        co = [s for s in sorted_scenarios if s.scenario_type == "convergent"]
        fr = [s for s in sorted_scenarios if s.scenario_type == "frontier"]
        
        route_a_steps = qw[:2] + fo[:2] + co[:1] + fr[:1]
        if route_a_steps:
            routes.append(EvolutionaryRoute(
                name="Rota Pragmática",
                description="Quick-wins primeiro, depois fundações, convergências, e fronteiras",
                steps=route_a_steps,
                total_priority=round(sum(s.priority_score for s in route_a_steps) / max(1, len(route_a_steps)), 2),
                estimated_impact=round(sum(s.cascade_impact for s in route_a_steps), 2),
            ))
        
        # Rota B: Convergents → Foundations → Quick-wins
        route_b_steps = co[:2] + fo[:2] + qw[:2]
        if route_b_steps and len(routes) < max_routes:
            routes.append(EvolutionaryRoute(
                name="Rota Polimática",
                description="Aproveitar soluções de outros domínios como alavanca inicial",
                steps=route_b_steps,
                total_priority=round(sum(s.priority_score for s in route_b_steps) / max(1, len(route_b_steps)), 2),
                estimated_impact=round(sum(s.cascade_impact for s in route_b_steps), 2),
            ))
        
        # Rota C: Foundations → Quick-wins → Frontiers
        route_c_steps = fo[:3] + qw[:2] + fr[:2]
        if route_c_steps and len(routes) < max_routes:
            routes.append(EvolutionaryRoute(
                name="Rota Estrutural",
                description="Construir fundações primeiro para maximizar efeito cascata",
                steps=route_c_steps,
                total_priority=round(sum(s.priority_score for s in route_c_steps) / max(1, len(route_c_steps)), 2),
                estimated_impact=round(sum(s.cascade_impact for s in route_c_steps), 2),
            ))
        
        return routes

    def generate(self, gaps: list[Any], bottlenecks: list[Any],
                 analogies: list[PolymathicAnalogy],
                 cascade: dict[str, float]) -> tuple[list[EvolutionaryScenario], list[EvolutionaryRoute]]:
        """Gera cenários e rotas completos a partir de todos os módulos."""
        scenarios: list[EvolutionaryScenario] = []
        
        # Criar lookup de analogias
        analogy_map: dict[str, list[PolymathicAnalogy]] = {}
        for a in analogies:
            analogy_map.setdefault(a.gap_category, []).append(a)
        
        # Criar lookup de prerequisites
        prereq_map: dict[str, list[str]] = {}
        for bn in bottlenecks:
            prereq_map.setdefault(f"{bn.domain}.{bn.category}", []).extend(bn.requires)
        
        for gap in gaps:
            gap_key = f"{gap.dim_key}.{gap.category}"
            impact = cascade.get(gap_key, 0.0)
            prereqs = prereq_map.get(gap_key, [])
            has_analogy = gap_key in analogy_map
            
            scenario = self.classify_scenario(
                category=gap.category,
                domain=gap.dim_key,
                cascade_impact=impact,
                prerequisites=prereqs,
                has_analogy=has_analogy,
            )
            
            if has_analogy:
                scenario.analogies = analogy_map[gap_key]
            
            scenarios.append(scenario)
        
        routes = self.generate_routes(scenarios)
        return scenarios, routes


# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE ORQUESTRADOR
# ═══════════════════════════════════════════════════════════════════════════

class EvolutionaryScannerPipeline:
    """Orquestrador do pipeline completo de 5 módulos."""

    def __init__(self):
        from noological_scanner import NoologicalScanner
        from teleological_scanner import TeleologicalReverseScanner
        from cross_validation_engine import CrossValidationEngine
        from capability_composer import CapabilityComposer, CognitiveLibrary
        from pathlib import Path as _Path

        self.noological = NoologicalScanner()
        self.teleological = TeleologicalReverseScanner()
        self.cross_validator = CrossValidationEngine()
        self.polymathic = PolymathicConvergence()
        self.trajectory_mapper = TrajectoryMapper()

        # SPEC-033: Inicializa compositor com biblioteca seed
        lib = CognitiveLibrary()
        lib_path = _Path(__file__).parent / "cognitive_library.json"
        if lib_path.exists():
            lib.load_json(lib_path)
        self.composer = CapabilityComposer(lib)
        from optimal_question_scanner import OptimalQuestionScanner
        self.oqs = OptimalQuestionScanner()  # SPEC-039

    def scan(self, audit_trail: Any, goals: list[Any],
             domain: str = "") -> EvolutionaryRoadmap:
        """Executa o pipeline completo e retorna roadmap evolutivo.

        Args:
            audit_trail: objeto compatível com NoologicalScanner.scan()
            goals: lista de TeleologicalGoal
            domain: domínio de pesquisa (opcional)
        """
        # M1: Scan noológico
        nool_scan = self.noological.scan(audit_trail, domain)

        # M2: Scan teleológico reverso
        self.teleological.set_goals(goals)
        self.teleological.infer_requirements()
        tel_gaps = self.teleological.compare_with_scan(nool_scan)

        # M3: Validação cruzada
        dep_graph = self.cross_validator.build_graph(nool_scan)
        bottlenecks = self.cross_validator.find_bottlenecks()
        cascade = self.cross_validator.cascade_impact(nool_scan)

        # M3.5: Composição Unitária do Conhecimento (SPEC-033) ← NOVO
        capability_ids = [f"{gap.dim_key}.{gap.category}" for gap in tel_gaps]
        capability_units = self.composer.decompose_many(capability_ids, domain)
        total_cost = self.composer.compute_total_construction_cost(capability_units)

        # Enriquecer CapabilityNode com composição
        for node_key, node in dep_graph.items():
            if node_key in capability_units:
                node.composition = capability_units[node_key]

        # M4: Convergência polimática
        analogies = self.polymathic.find_analogies(tel_gaps)

        # M5: Mapa de trajetórias
        scenarios, routes = self.trajectory_mapper.generate(
            gaps=tel_gaps,
            bottlenecks=bottlenecks,
            analogies=analogies,
            cascade=cascade,
        )

        # Enriquecer cenários com required_inputs da composição
        for scenario in scenarios:
            cap_id = f"{scenario.domain}.{scenario.category}"
            if cap_id in capability_units:
                unit = capability_units[cap_id]
                scenario.required_inputs = unit.all_inputs

        # Classificar cenários por tipo
        quick_wins = sum(1 for s in scenarios if s.scenario_type == "quick_win")
        foundations = sum(1 for s in scenarios if s.scenario_type == "foundation")
        frontiers = sum(1 for s in scenarios if s.scenario_type == "frontier")
        convergents = sum(1 for s in scenarios if s.scenario_type == "convergent")

        # M3.8: Sequenciamento Evolutivo (Camada 1 — Proposta de Melhoria)
        sequencer = EvolutionarySequencer()
        sequencing_res = sequencer.sequence(tel_gaps, dep_graph, capability_units, analogies)

        return EvolutionaryRoadmap(
            noological_coverage=nool_scan["overall_density"],
            teleological_score=self.teleological.teleological_score(),
            bottlenecks=[f"{b.domain}.{b.category}" for b in bottlenecks[:5]],
            analogies=analogies,
            scenarios=scenarios,
            routes=routes,
            total_gaps=len(tel_gaps),
            quick_wins=quick_wins,
            foundations=foundations,
            frontiers=frontiers,
            convergents=convergents,
            capability_units=list(capability_units.values()),  # SPEC-033
            total_construction_cost=total_cost,  # SPEC-033
            sequencing=sequencing_res,
        )

    def generate_report(self, roadmap: EvolutionaryRoadmap) -> str:
        """Gera relatório Markdown do roadmap evolutivo."""
        lines = [
            "# Roadmap Evolutivo — Scanner de Trajetórias",
            "",
            f"**Cobertura Noológica**: {roadmap.noological_coverage:.0%}",
            f"**Alinhamento Teleológico**: {roadmap.teleological_score:.0%}",
            f"**Total de Gaps**: {roadmap.total_gaps}",
            "",
            "---",
            "",
            "## Cenários de Evolução",
            "",
            f"| Tipo | Quantidade |",
            f"|------|-----------|",
            f"| ⚡ Quick-wins | {roadmap.quick_wins} |",
            f"| 🏗️ Foundations | {roadmap.foundations} |",
            f"| 🔮 Convergentes | {roadmap.convergents} |",
            f"| 🚀 Frontiers | {roadmap.frontiers} |",
            "",
            "---",
            "",
            "## Top 5 Bottlenecks",
            "",
        ]
        for i, bn in enumerate(roadmap.bottlenecks, 1):
            lines.append(f"{i}. `{bn}`")
        
        lines.extend([
            "",
            "---",
            "",
            f"## Analogias Polimáticas ({len(roadmap.analogies)})",
            "",
        ])
        for a in roadmap.analogies[:10]:
            lines.append(f"- **{a.gap_category}** → {a.external_domain}: {a.transferable_principle} "
                        f"(_score: {a.transferability_score}_)")
        
        lines.extend([
            "",
            "---",
            "",
            f"## Rotas de Evolução ({len(roadmap.routes)})",
            "",
        ])
        for route in roadmap.routes:
            lines.append(f"### {route.name}")
            lines.append(f"> {route.description}")
            lines.append(f"**Prioridade média**: {route.total_priority:.2f} | "
                        f"**Impacto estimado**: {route.estimated_impact:.2f}")
            lines.append("")
            for i, step in enumerate(route.steps, 1):
                tag = {"quick_win": "⚡", "foundation": "🏗️", "convergent": "🔮", "frontier": "🚀"}.get(step.scenario_type, "•")
                lines.append(f"{i}. {tag} **{step.category}** `[{step.domain}]` — "
                           f"prioridade: {step.priority_score}, impacto: {step.cascade_impact}")
            lines.append("")
        
        if roadmap.sequencing:
            lines.extend([
                "",
                "---",
                "",
                "## Sequenciamento Evolutivo (Camada 1 — Planejamento de Obra Epistêmica)",
                "",
                f"O sequenciamento evolutivo distribuiu as capacidades em **{roadmap.sequencing.total_phases} fases lógicas** de desenvolvimento contínuo e paralelizável:",
                "",
            ])
            
            # Agrupar steps por fase
            steps_by_phase: dict[int, list[SequencingStep]] = {}
            for step in roadmap.sequencing.steps:
                steps_by_phase.setdefault(step.phase, []).append(step)
                
            for phase in sorted(steps_by_phase.keys()):
                phase_title = f"### 📅 Fase {phase} — "
                if phase == 1:
                    phase_title += "Capacidades de Partida (Paralelizável)"
                else:
                    phase_title += f"Capacidades Dependentes (Requer Fase {phase - 1})"
                
                lines.extend([
                    phase_title,
                    "",
                ])
                for step in steps_by_phase[phase]:
                    cost_pct = f"{step.cost * 100:.0f}%"
                    info = f"- 🛠️ **{step.category}** `[{step.domain}]` — _Esforço Construtivo: {cost_pct}_"
                    if step.analogy_principle:
                        info += f" | 🔮 _Analogia Polimática ({step.analogy_domain})_: {step.analogy_principle}"
                    lines.append(info)
                    
                    if step.predecessors:
                        lines.append(f"  - _Predecessoras_: " + ", ".join([f"`{p}`" for p in step.predecessors]))
                    if step.successors:
                        lines.append(f"  - _Sucessoras_: " + ", ".join([f"`{s}`" for s in step.successors]))
                lines.append("")
        
        return "\n".join(lines)


class EvolutionarySequencer:
    """Implementa a Camada 1: Sequenciamento Evolutivo.
    Analisa as dependências entre as capacidades futuras e gera um cronograma lógico
    baseado em níveis de ordenação topológica (BFS por camadas).
    """

    def sequence(self, gaps: list[Any], dep_graph: dict[str, Any],
                 capability_units: dict[str, Any] = None,
                 analogies: list[Any] = None) -> EvolutionarySequencing:
        
        # Build mappings for easy lookup
        unit_map = capability_units or {}
        analogy_map = {}
        if analogies:
            for a in analogies:
                analogy_map[a.gap_category] = a
                
        # 1. Mapear chaves de gap para verificação rápida
        gap_keys = {f"{g.dim_key}.{g.category}" for g in gaps}
        
        # 2. Construir subgrafo direcionado apenas com os gaps
        adj: dict[str, list[str]] = {} # u -> [v] (u habilita v)
        in_degree: dict[str, int] = {} # v -> num_prereqs
        predecessors_map: dict[str, list[str]] = {}
        successors_map: dict[str, list[str]] = {}

        for key in gap_keys:
            adj[key] = []
            in_degree[key] = 0
            predecessors_map[key] = []
            successors_map[key] = []

        # Usar as dependências do dep_graph (regras de requires e provides)
        for key in gap_keys:
            node = dep_graph.get(key)
            if node:
                # 1. requires: req deve vir antes de key (req -> key)
                for req in node.requires:
                    if req in gap_keys:
                        if key not in adj[req]:
                            adj[req].append(key)
                            in_degree[key] += 1
                            predecessors_map[key].append(req)
                            successors_map[req].append(key)
                # 2. provides: key deve vir antes de prov (key -> prov)
                for prov in node.provides:
                    if prov in gap_keys:
                        if prov not in adj[key]:
                            adj[key].append(prov)
                            in_degree[prov] += 1
                            predecessors_map[prov].append(key)
                            successors_map[key].append(prov)

        # 3. BFS por camadas (Level-order / Kahn's algorithm adaptado) para definir fases
        queue = [k for k, deg in in_degree.items() if deg == 0]
        phases: dict[int, list[str]] = {}
        logical_seq = []
        phase_num = 1
        
        temp_in_degree = dict(in_degree)
        
        while queue:
            current_phase_nodes = list(queue)
            phases[phase_num] = current_phase_nodes
            logical_seq.extend(current_phase_nodes)
            
            next_queue = []
            for u in current_phase_nodes:
                for v in adj[u]:
                    temp_in_degree[v] -= 1
                    if temp_in_degree[v] == 0:
                        next_queue.append(v)
            queue = next_queue
            phase_num += 1

        total_phases = phase_num - 1

        # Tratar ciclos ou nós não alcançados (colocar na última fase para segurança)
        unreached = gap_keys - set(logical_seq)
        if unreached:
            if total_phases == 0:
                total_phases = 1
                phases[total_phases] = []
            phases[total_phases].extend(list(unreached))
            logical_seq.extend(list(unreached))

        # 4. Criar passos detalhados (SequencingStep)
        steps = []
        for key in logical_seq:
            parts = key.split('.', 1)
            dim = parts[0]
            cat = parts[1] if len(parts) > 1 else key
            
            current_phase = 1
            for p, nodes in phases.items():
                if key in nodes:
                    current_phase = p
                    break
            parallel = [n for n in phases[current_phase] if n != key]
            
            # Obter custo e analogia
            cost = 0.0
            if key in unit_map:
                cost = unit_map[key].construction_cost
            
            analogy_principle = ""
            analogy_domain = ""
            if key in analogy_map:
                a = analogy_map[key]
                analogy_principle = a.transferable_principle
                analogy_domain = a.external_domain
            
            steps.append(SequencingStep(
                category=cat,
                domain=dim,
                phase=current_phase,
                predecessors=predecessors_map[key],
                successors=successors_map[key],
                can_run_in_parallel_with=parallel,
                cost=cost,
                analogy_principle=analogy_principle,
                analogy_domain=analogy_domain
            ))

        # 5. Gerar cronograma formatado como timeline
        timeline = []
        for phase, nodes in phases.items():
            nodes_str = ", ".join([f"`{n}`" for n in nodes])
            timeline.append(f"Fase {phase} (Paralelizável): Construir {nodes_str}")

        return EvolutionarySequencing(
            total_phases=total_phases,
            logical_sequence=logical_seq,
            phases=phases,
            steps=steps,
            timeline=timeline
        )
