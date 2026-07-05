"""
SPEC-044: Social Impact Scanner
================================
Avaliação de Impacto Social, Ambiental e Econômico
Integra 6 metodologias internacionais padronizadas:
  - SROI + ISO 26000
  - Social Value International (deadweight/attribution/displacement)
  - Theory of Change (input→activities→outputs→outcomes→impact)
  - IRIS+ / GIIN (4 indicadores padronizados)
  - B Impact Assessment (5 dimensões B Lab)
  - SDG Tracker (UN Agenda 2030)

Uso:
    from skills.system.academic_audit.social_impact_scanner import SocialImpactScanner
    scanner = SocialImpactScanner()
    report = scanner.analyze_research_paper(titulo, resumo, metodologia, ...)
    print(report.as_json())
"""

import json
import math
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime


# =====================================================================
# DATA STRUCTURES
# =====================================================================

@dataclass
class SocialValueAdjustments:
    """Ajustes de valor social conforme Social Value International"""
    deadweight: float = 0.0       # % que teria ocorrido sem intervenção (0-1)
    attribution: float = 1.0      # % atribuível à intervenção (0-1)
    displacement: float = 0.0     # % deslocado para outros contextos (0-1)
    drop_off: float = 0.0         # % de declínio anual do impacto (0-1)
    duration_years: int = 1       # Duração esperada do impacto em anos

    @property
    def net_multiplier(self) -> float:
        """Fator líquido = attribution * (1 - displacement) * (1 - deadweight)"""
        gross = 1.0
        gross *= self.attribution
        gross *= (1.0 - self.displacement)
        gross *= (1.0 - self.deadweight)
        return max(0.0, gross)


@dataclass
class Stakeholder:
    name: str
    weight: float = 1.0           # Importância relativa (0-1)
    outcomes: List[str] = field(default_factory=list)
    monetized_value: float = 0.0  # Valor social gerado (R$ estimado)


@dataclass
class SROIResult:
    """Resultado do cálculo SROI"""
    total_investment: float = 0.0
    gross_social_value: float = 0.0
    deadweight_value: float = 0.0
    attribution_value: float = 0.0
    displacement_value: float = 0.0
    net_present_value: float = 0.0
    sroi_ratio: float = 0.0       # NPV / Investment
    stakeholders: List[Stakeholder] = field(default_factory=list)
    iso_26000_themes: Dict[str, float] = field(default_factory=dict)


@dataclass
class ToCElement:
    input_desc: str = ""
    activities: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    outcomes: List[str] = field(default_factory=list)
    impact: str = ""
    indicators: Dict[str, str] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)


@dataclass
class IRISPlusIndicators:
    """IRIS+ GIIN - 4 indicadores padronizados"""
    od01_product_service_description: str = ""
    od02_social_objective: str = ""
    od03_direct_beneficiaries: int = 0
    od04_indirect_beneficiaries: int = 0
    additional_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class BImpactScore:
    governance: float = 0.0       # 20%
    workers: float = 0.0          # 20%
    community: float = 0.0        # 25%
    environment: float = 0.0      # 20%
    customers: float = 0.0        # 15%

    @property
    def total(self) -> float:
        """Score total ponderado (0-200)"""
        return (self.governance * 0.20 + self.workers * 0.20 +
                self.community * 0.25 + self.environment * 0.20 +
                self.customers * 0.15) * 2.0

    @property
    def rating(self) -> str:
        t = self.total
        if t >= 80: return "Certified B Corp (Excelente)"
        if t >= 60: return "Alto Impacto"
        if t >= 40: return "Impacto Moderado"
        if t >= 20: return "Impacto Inicial"
        return "Abaixo do Esperado"


@dataclass
class SDGAlignment:
    goal_number: int
    goal_name: str
    score: float = 0.0            # 0-100
    target_contributions: List[str] = field(default_factory=list)
    evidence: str = ""


@dataclass
class SocialImpactReport:
    title: str = ""
    date: str = ""
    sroi: SROIResult = field(default_factory=SROIResult)
    theory_of_change: ToCElement = field(default_factory=ToCElement)
    iris_plus: IRISPlusIndicators = field(default_factory=IRISPlusIndicators)
    b_impact: BImpactScore = field(default_factory=BImpactScore)
    sdg_alignments: List[SDGAlignment] = field(default_factory=list)
    parecer: str = ""
    consolidated_score: float = 0.0  # 0-100
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)

    def as_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2, default=str)

    def as_dict(self) -> Dict:
        return asdict(self)


# =====================================================================
# SROI ANALYZER (ISO 26000)
# =====================================================================

class SROIAnalyzer:
    """
    Análise de Social Return on Investment conforme ISO 26000.
    Calcula o ratio de retorno social, mapeia stakeholders e
    avalia os 7 temas centrais de responsabilidade social.
    """

    ISO_26000_THEMES = [
        "governanca_organizacional",
        "direitos_humanos",
        "praticas_trabalhistas",
        "meio_ambiente",
        "praticas_justas",
        "consumidores",
        "comunidade"
    ]

    def __init__(self):
        self.adjustments = SocialValueAdjustments()

    def set_adjustments(self, deadweight: float = 0.0, attribution: float = 1.0,
                        displacement: float = 0.0, drop_off: float = 0.0,
                        duration_years: int = 1):
        """Configura ajustes de valor social"""
        self.adjustments = SocialValueAdjustments(
            deadweight=deadweight, attribution=attribution,
            displacement=displacement, drop_off=drop_off,
            duration_years=duration_years
        )

    def add_stakeholder(self, name: str, weight: float = 1.0,
                        outcomes: Optional[List[str]] = None,
                        monetized_value: float = 0.0) -> Stakeholder:
        return Stakeholder(
            name=name, weight=min(1.0, max(0.0, weight)),
            outcomes=outcomes or [],
            monetized_value=monetized_value
        )

    def calculate_sroi(self, total_investment: float,
                       stakeholders: List[Stakeholder],
                       iso_26000_scores: Optional[Dict[str, float]] = None
                       ) -> SROIResult:
        """
        Calcula o SROI ratio.
        Fórmula: SROI = (NPV of Benefits) / (Total Investment)

        NPV = sum(monetized_value * net_multiplier * duration_factor)
        """
        duration_factor = 0.0
        for y in range(self.adjustments.duration_years):
            duration_factor += (1 - self.adjustments.drop_off) ** y

        gross_value = sum(s.monetized_value for s in stakeholders)
        net_mult = self.adjustments.net_multiplier
        npv = gross_value * net_mult * duration_factor

        result = SROIResult(
            total_investment=total_investment,
            gross_social_value=gross_value,
            deadweight_value=gross_value * self.adjustments.deadweight,
            attribution_value=gross_value * self.adjustments.attribution,
            displacement_value=gross_value * self.adjustments.displacement,
            net_present_value=npv,
            sroi_ratio=npv / total_investment if total_investment > 0 else 0.0,
            stakeholders=stakeholders,
            iso_26000_themes=iso_26000_scores or {}
        )

        if result.iso_26000_themes.get("governanca_organizacional") is None:
            result.iso_26000_themes = {t: 50.0 for t in self.ISO_26000_THEMES}

        return result

    def analyze_iso_26000(self, research_themes: List[str]) -> Dict[str, float]:
        """Avalia alinhamento com os 7 temas centrais da ISO 26000"""
        theme_keywords = {
            "governanca_organizacional": ["governança", "transparência", "accountability", "prestação", "conta", "responsabilidade"],
            "direitos_humanos": ["direitos humanos", "dignidade", "liberdade", "igualdade", "discriminação"],
            "praticas_trabalhistas": ["trabalhista", "emprego", "remuneração", "saúde ocupacional", "segurança trabalho"],
            "meio_ambiente": ["ambiental", "sustentável", "ecossistema", "poluição", "biodiversidade", "carbono"],
            "praticas_justas": ["justa", "corrupção", "concorrência", "propriedade intelectual", "ética"],
            "consumidores": ["consumidor", "privacidade", "dados pessoais", "qualidade", "transparência informação"],
            "comunidade": ["comunidade", "desenvolvimento local", "engajamento", "filantropia", "voluntariado"]
        }

        scores = {}
        research_text = " ".join(research_themes).lower()

        for theme, keywords in theme_keywords.items():
            matches = sum(1 for kw in keywords if kw in research_text)
            max_match = len(keywords)
            scores[theme] = round((matches / max_match) * 100, 1) if max_match > 0 else 0.0

        return scores


# =====================================================================
# THEORY OF CHANGE BUILDER
# =====================================================================

class TheoryOfChangeBuilder:
    """
    Theory of Change: input → activities → outputs → outcomes → impact
    Com indicadores verificáveis, preconditions e assumptions.
    """

    def build(self, input_desc: str, activities: List[str],
              outputs: List[str], outcomes: List[str], impact: str,
              indicators: Optional[Dict[str, str]] = None,
              assumptions: Optional[List[str]] = None) -> ToCElement:
        return ToCElement(
            input_desc=input_desc,
            activities=activities,
            outputs=outputs,
            outcomes=outcomes,
            impact=impact,
            indicators=indicators or {},
            assumptions=assumptions or []
        )

    def generate_narrative(self, toc: ToCElement) -> str:
        """Gera narrativa de mudança a partir da ToC"""
        narrative = f"Dado o investimento em '{toc.input_desc}', "
        narrative += f"foram realizadas {len(toc.activities)} atividades principais. "
        narrative += f"Isso produziu {len(toc.outputs)} resultados diretos, "
        narrative += f"gerando {len(toc.outcomes)} mudanças de curto/médio prazo "
        narrative += f"e contribuindo para o impacto de longo prazo: '{toc.impact}'."
        return narrative

    def validate_chain(self, toc: ToCElement) -> List[str]:
        """Valida a integridade da cadeia lógica"""
        issues = []
        if not toc.input_desc:
            issues.append("Input não definido")
        if not toc.activities:
            issues.append("Nenhuma atividade definida")
        if not toc.outputs:
            issues.append("Nenhum output definido")
        if not toc.outcomes:
            issues.append("Nenhum outcome definido")
        if not toc.impact:
            issues.append("Impacto não definido")
        if len(toc.activities) > len(toc.outputs) * 3:
            issues.append("Proporção atividades/outputs desbalanceada (>3:1)")
        if not toc.indicators:
            issues.append("Nenhum indicador verificável definido")
        return issues


# =====================================================================
# IRIS+ / GIIN REPORT
# =====================================================================

class IRISPlusReport:
    """
    IRIS+ Catalog — Sistema de indicadores padronizados do GIIN
    (Global Impact Investing Network).
    Núcleo mínimo: 4 indicadores obrigatórios (OD01-OD04).
    """

    OD01_LABEL = "OD01: Descrição do Produto/Serviço Social"
    OD02_LABEL = "OD02: Objetivo Social Declarado"
    OD03_LABEL = "OD03: Beneficiários Diretos"
    OD04_LABEL = "OD04: Beneficiários Indiretos"

    def generate(self, product_desc: str, social_objective: str,
                 direct_beneficiaries: int = 0,
                 indirect_beneficiaries: int = 0,
                 additional_metrics: Optional[Dict[str, float]] = None
                 ) -> IRISPlusIndicators:
        return IRISPlusIndicators(
            od01_product_service_description=product_desc,
            od02_social_objective=social_objective,
            od03_direct_beneficiaries=direct_beneficiaries,
            od04_indirect_beneficiaries=indirect_beneficiaries,
            additional_metrics=additional_metrics or {}
        )

    def validate(self, indicators: IRISPlusIndicators) -> List[str]:
        errors = []
        if not indicators.od01_product_service_description:
            errors.append("OD01 obrigatório: descrição do produto/serviço social")
        if not indicators.od02_social_objective:
            errors.append("OD02 obrigatório: objetivo social declarado")
        if indicators.od03_direct_beneficiaries <= 0:
            errors.append("OD03 deve ser > 0: beneficiários diretos")
        if indicators.od04_indirect_beneficiaries < 0:
            errors.append("OD04 não pode ser negativo")
        return errors


# =====================================================================
# B IMPACT ASSESSMENT (B LAB)
# =====================================================================

class BImpactAssessor:
    """
    B Impact Assessment — B Lab
    5 dimensões: Governance, Workers, Community, Environment, Customers
    Score total: 0-200 (80+ = eligibility for B Corp certification)
    """

    DIMENSION_WEIGHTS = {
        "governance": 0.20,
        "workers": 0.20,
        "community": 0.25,
        "environment": 0.20,
        "customers": 0.15
    }

    def assess(self, governance: float = 0.0, workers: float = 0.0,
               community: float = 0.0, environment: float = 0.0,
               customers: float = 0.0) -> BImpactScore:
        """Avalia as 5 dimensões (cada uma 0-100)"""
        return BImpactScore(
            governance=min(100, max(0, governance)),
            workers=min(100, max(0, workers)),
            community=min(100, max(0, community)),
            environment=min(100, max(0, environment)),
            customers=min(100, max(0, customers))
        )

    def diagnose(self, score: BImpactScore) -> Dict[str, List[str]]:
        """Diagnóstico por dimensão: forças e fraquezas"""
        result = {}
        dims = [
            ("governance", "Governança"),
            ("workers", "Trabalhadores"),
            ("community", "Comunidade"),
            ("environment", "Meio Ambiente"),
            ("customers", "Clientes")
        ]
        for key, label in dims:
            val = getattr(score, key)
            if val >= 70:
                result[key] = {"status": "forte", "label": label, "score": val}
            elif val >= 40:
                result[key] = {"status": "moderado", "label": label, "score": val}
            else:
                result[key] = {"status": "fraco", "label": label, "score": val}
        return result


# =====================================================================
# SDG TRACKER (UN AGENDA 2030)
# =====================================================================

class SDGTracker:
    """
    Rastreamento de alinhamento com os 17 ODS da ONU Agenda 2030.
    Mapeia temas de pesquisa para objetivos e metas específicas.
    """

    SDGS = {
        1: ("Erradicação da Pobreza", ["pobreza", "renda", "desigualdade", "vulnerabilidade", "assistência social"]),
        2: ("Fome Zero", ["fome", "agricultura", "alimentação", "nutrição", "segurança alimentar"]),
        3: ("Saúde e Bem-Estar", ["saúde", "bem-estar", "médico", "hospital", "doença", "tratamento", "clínico"]),
        4: ("Educação de Qualidade", ["educação", "ensino", "aprendizagem", "escola", "universidade", "formação"]),
        5: ("Igualdade de Gênero", ["gênero", "igualdade", "mulher", "feminino", "discriminação gênero"]),
        6: ("Água Potável e Saneamento", ["água", "saneamento", "higiene", "tratamento água", "recursos hídricos"]),
        7: ("Energia Limpa e Acessível", ["energia", "renovável", "solar", "eólica", "biomassa", "eficiência energética"]),
        8: ("Trabalho Decente e Crescimento Econômico", ["trabalho", "emprego", "econômico", "crescimento", "renda"]),
        9: ("Indústria, Inovação e Infraestrutura", ["inovação", "indústria", "infraestrutura", "tecnologia", "pesquisa"]),
        10: ("Redução das Desigualdades", ["desigualdade", "inclusão", "equidade", "exclusão", "marginalizado"]),
        11: ("Cidades e Comunidades Sustentáveis", ["cidades", "urbano", "comunidade", "habitação", "mobilidade"]),
        12: ("Consumo e Produção Responsáveis", ["consumo", "produção", "resíduo", "reciclagem", "sustentável"]),
        13: ("Ação contra a Mudança Global do Clima", ["clima", "mudança climática", "aquecimento", "carbono", "emissões"]),
        14: ("Vida na Água", ["oceano", "mar", "aquático", "pesca", "marinho"]),
        15: ("Vida Terrestre", ["biodiversidade", "floresta", "ecossistema", "fauna", "flora", "conservação"]),
        16: ("Paz, Justiça e Instituições Eficazes", ["paz", "justiça", "instituição", "governança", "direitos"]),
        17: ("Parcerias e Meios de Implementação", ["parceria", "cooperação", "internacional", "colaboração", "implementação"])
    }

    def track(self, research_text: str, keywords: Optional[List[str]] = None) -> List[SDGAlignment]:
        """
        Mapeia o texto da pesquisa para os 17 ODS.
        Retorna lista ordenada por score de relevância.
        """
        all_keywords = keywords or []
        text_lower = research_text.lower()
        for kw in all_keywords:
            text_lower += " " + kw.lower()

        alignments = []
        for goal_num, (goal_name, goal_keywords) in self.SDGS.items():
            matches = sum(1 for kw in goal_keywords if kw in text_lower)
            max_expected = len(goal_keywords)
            score = min(100, round((matches / max(1, max_expected * 0.3)) * 100, 1))
            score = min(100, max(0, score))

            if score > 0:
                matched_keywords = [kw for kw in goal_keywords if kw in text_lower]
                alignments.append(SDGAlignment(
                    goal_number=goal_num,
                    goal_name=goal_name,
                    score=score,
                    target_contributions=matched_keywords,
                    evidence=f"Keywords found: {', '.join(matched_keywords)}"
                ))

        alignments.sort(key=lambda x: x.score, reverse=True)
        return alignments

    def top_three(self, alignments: List[SDGAlignment]) -> List[SDGAlignment]:
        """Retorna os 3 ODS mais relevantes"""
        return alignments[:3]


# =====================================================================
# MAIN SCANNER ORCHESTRATOR
# =====================================================================

class SocialImpactScanner:
    """
    Scanner orquestrador completo de impacto social.
    Integra todas as 6 metodologias em um único pipeline de análise.
    Gera parecer consolidado com score e recomendações.
    """

    def __init__(self):
        self.sroi = SROIAnalyzer()
        self.toc = TheoryOfChangeBuilder()
        self.iris = IRISPlusReport()
        self.bia = BImpactAssessor()
        self.sdg = SDGTracker()

    def analyze_research_paper(
        self,
        titulo: str,
        resumo: str,
        metodologia: str,
        resultados: str,
        conclusoes: str,
        palavras_chave: Optional[List[str]] = None,
        area_conhecimento: str = "",
        orcamento_estimado: float = 100000.0,
        num_pesquisadores: int = 3,
        anos_projeto: int = 2
    ) -> SocialImpactReport:
        """
        Análise completa de impacto social de um paper/manuscrito.
        Retorna relatório consolidado com todas as metodologias.
        """
        full_text = f"{titulo} {resumo} {metodologia} {resultados} {conclusoes}"
        keywords = palavras_chave or []

        # 1. SROI + ISO 26000
        iso_scores = self.sroi.analyze_iso_26000(keywords + [area_conhecimento] + [resumo[:200]])
        stakeholders = [
            self.sroi.add_stakeholder("Academia/Pesquisadores", 0.8,
                                      ["Avanço científico", "Publicações", "Formação RH"],
                                      orcamento_estimado * 0.3),
            self.sroi.add_stakeholder("Sociedade/Beneficiários", 1.0,
                                      ["Aplicação prática", "Impacto social"],
                                      orcamento_estimado * 1.5),
            self.sroi.add_stakeholder("Governo/Políticas Públicas", 0.6,
                                      ["Evidências para políticas", "ODS"],
                                      orcamento_estimado * 0.5),
        ]
        total_investment = orcamento_estimado * anos_projeto
        self.sroi.set_adjustments(deadweight=0.15, attribution=0.8,
                                  displacement=0.05, drop_off=0.1,
                                  duration_years=min(10, anos_projeto * 2))
        sroi_result = self.sroi.calculate_sroi(total_investment, stakeholders, iso_scores)

        # 2. Theory of Change
        toc_element = self.toc.build(
            input_desc=f"Investimento de R${total_investment:,.0f} em pesquisa na área de {area_conhecimento or 'conhecimento'}",
            activities=[
                f"Pesquisa conduzida por {num_pesquisadores} pesquisadores",
                "Desenvolvimento de metodologia e experimentação",
                "Análise de dados e validação de resultados",
                "Publicação e divulgação científica",
            ],
            outputs=[
                "Artigos científicos publicados",
                "Dados e códigos disponibilizados",
                "Relatórios técnicos gerados",
                "Apresentações em conferências",
            ],
            outcomes=[
                "Avanço do estado da arte no tema",
                "Formação de recursos humanos qualificados",
                "Disseminação do conhecimento",
                "Potencial de aplicação prática",
            ],
            impact=conclusoes[:200],
            indicators={
                "Publicações": "Número de artigos em periódicos Qualis A",
                "Citações": "Impacto acadêmico mensurável",
                "Beneficiários": "Pessoas direta ou indiretamente impactadas",
                "ODS": "Número de ODS impactados"
            },
            assumptions=[
                "Resultados são reprodutíveis",
                "Conhecimento gerado é acessível",
                "Há demanda social pela aplicação"
            ]
        )

        # 3. IRIS+ indicators
        iris_indicators = self.iris.generate(
            product_desc=titulo[:200],
            social_objective=conclusoes[:200],
            direct_beneficiaries=int(sroi_result.gross_social_value / 10000),
            indirect_beneficiaries=int(sroi_result.gross_social_value / 5000),
            additional_metrics={
                "SROI_Ratio": sroi_result.sroi_ratio,
                "Total_Investment": total_investment,
                "Net_Present_Value": sroi_result.net_present_value
            }
        )

        # 4. B Impact Assessment
        b_score = self.bia.assess(
            governance=min(80, 40 + len(keywords) * 2),
            workers=min(80, 30 + num_pesquisadores * 5),
            community=min(100, 20 + sroi_result.sroi_ratio * 10),
            environment=min(60, 20 + (1 if "ambient" in full_text.lower() else 0) * 30),
            customers=min(70, 30 + len(iris_indicators.additional_metrics) * 5)
        )

        # 5. SDG Tracking
        sdg_alignments = self.sdg.track(full_text, keywords)

        # 6. Consolidated parecer and score
        score = self._calculate_consolidated_score(
            sroi_ratio=sroi_result.sroi_ratio,
            b_total=b_score.total,
            sdg_count=len(sdg_alignments),
            toc_issues=len(self.toc.validate_chain(toc_element)),
            iris_errors=len(self.iris.validate(iris_indicators))
        )

        parecer = self._generate_parecer(
            titulo, sroi_result, b_score, sdg_alignments, score
        )

        strengths, improvements = self._generate_recommendations(
            sroi_result, toc_element, b_score, sdg_alignments
        )

        return SocialImpactReport(
            title=titulo,
            date=datetime.now().strftime("%Y-%m-%d"),
            sroi=sroi_result,
            theory_of_change=toc_element,
            iris_plus=iris_indicators,
            b_impact=b_score,
            sdg_alignments=sdg_alignments,
            parecer=parecer,
            consolidated_score=score,
            strengths=strengths,
            improvements=improvements
        )

    def _calculate_consolidated_score(self, sroi_ratio: float,
                                       b_total: float,
                                       sdg_count: int,
                                       toc_issues: int,
                                       iris_errors: int) -> float:
        """Calcula score consolidado (0-100)"""
        sroi_score = min(100, sroi_ratio * 20)  # SROI 5+ = 100
        b_score = b_total / 2.0  # B total 0-200 -> 0-100
        sdg_score = min(100, sdg_count * 7)  # 14 ODS = 98
        toc_score = max(0, 100 - toc_issues * 20)
        iris_score = max(0, 100 - iris_errors * 25)

        weights = {"sroi": 0.25, "b": 0.20, "sdg": 0.20, "toc": 0.15, "iris": 0.20}
        score = (sroi_score * weights["sroi"] + b_score * weights["b"] +
                 sdg_score * weights["sdg"] + toc_score * weights["toc"] +
                 iris_score * weights["iris"])
        return round(min(100, max(0, score)), 1)

    def _generate_parecer(self, titulo: str, sroi: SROIResult,
                           b_score: BImpactScore,
                           sdgs: List[SDGAlignment],
                           score: float) -> str:
        """Gera parecer qualitativo de impacto social"""
        parecer = f"## Parecer de Impacto Social\n\n"
        parecer += f"**Título**: {titulo}\n\n"
        parecer += f"**Score Consolidado**: {score}/100\n\n"

        parecer += "### Análise SROI\n"
        parecer += f"O investimento total de R${sroi.total_investment:,.2f} "
        parecer += f"gera um Valor Presente Líquido Social de R${sroi.net_present_value:,.2f}, "
        parecer += f"resultando em um **ratio SROI de {sroi.sroi_ratio:.2f}:1**. "
        parecer += f"Isto significa que cada R$1,00 investido retorna R${sroi.sroi_ratio:.2f} em valor social.\n\n"

        parecer += "### B Impact Assessment\n"
        parecer += f"Score B total: {b_score.total:.1f}/200 — {b_score.rating}. "
        parecer += "Dimensões analisadas: Governança, Trabalhadores, Comunidade, Meio Ambiente e Clientes.\n\n"

        parecer += "### Alinhamento com ODS\n"
        if sdgs:
            top = sdgs[:3]
            parecer += f"Alinhado com {len(sdgs)} ODS. Principais: "
            parecer += ", ".join([f"ODS {s.goal_number} ({s.goal_name} - {s.score}%)" for s in top])
            parecer += ".\n\n"
        else:
            parecer += "Nenhum ODS identificado diretamente.\n\n"

        parecer += "### Conclusão\n"
        if score >= 80:
            parecer += "Esta pesquisa apresenta **alto impacto social potencial**. "
            parecer += "Recomenda-se prosseguir com o plano de disseminação e implementação."
        elif score >= 50:
            parecer += "Esta pesquisa apresenta **impacto social moderado**. "
            parecer += "Recomenda-se fortalecer a conexão com beneficiários diretos e ODS."
        else:
            parecer += "Esta pesquisa apresenta **impacto social limitado no curto prazo**. "
            parecer += "Recomenda-se revisar a estratégia de engajamento social e impacto."

        return parecer

    def _generate_recommendations(self, sroi: SROIResult,
                                    toc: ToCElement,
                                    b_score: BImpactScore,
                                    sdgs: List[SDGAlignment]) -> Tuple[List[str], List[str]]:
        """Gera recomendações de forças e melhorias"""
        strengths = []
        improvements = []

        if sroi.sroi_ratio >= 3:
            strengths.append("Alto retorno social sobre investimento (SROI)")
        else:
            improvements.append("Buscar ampliar o ratio SROI (>3:1 ideal)")

        if len(sdgs) >= 5:
            strengths.append(f"Forte alinhamento com {len(sdgs)} ODS da ONU")
        else:
            improvements.append("Fortalecer alinhamento com objetivos de desenvolvimento sustentável")

        if len(toc.activities) >= 3 and len(toc.outcomes) >= 2:
            strengths.append("Cadeia lógica Theory of Change bem estruturada")
        else:
            improvements.append("Estruturar melhor a teoria de mudança")

        if b_score.total >= 80:
            strengths.append(f"Score B Impact ({b_score.total:.0f}/200) compatível com padrões internacionais")
        elif b_score.total >= 40:
            improvements.append("Elevar score B Impact para >80 (elegibilidade B Corp)")

        return strengths, improvements
