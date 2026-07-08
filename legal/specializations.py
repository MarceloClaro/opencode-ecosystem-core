# -*- coding: utf-8 -*-
"""
SPEC-927: Especialização Jurídica por Domínio
=============================================
Perfis jurídicos por ramo, roteamento de consultas e construção de agentes
especialistas, aproximando o ecossistema de comportamento "nível PhD por área"
com honestidade epistêmica e escopo explícito.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from legal.agents import LegalAgentCard


@dataclass(frozen=True)
class LegalDomainProfile:
    domain_id: str
    name: str
    description: str
    core_statutes: List[str] = field(default_factory=list)
    principles: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    common_issues: List[str] = field(default_factory=list)
    risk_vectors: List[str] = field(default_factory=list)

    def specialist_prompt(self) -> str:
        return (
            f"Você é um especialista jurídico em {self.name}. "
            f"Atue com foco principal em {self.description}. "
            f"Base normativa central: {', '.join(self.core_statutes)}. "
            f"Princípios estruturantes: {', '.join(self.principles)}. "
            f"Questões frequentes: {', '.join(self.common_issues)}. "
            f"Vetores de risco: {', '.join(self.risk_vectors)}. "
            "Se houver incerteza relevante, explicite limitações, peça contexto adicional "
            "e recomende revisão humana especializada."
        )


LEGAL_DOMAIN_PROFILES: Dict[str, LegalDomainProfile] = {
    "penal": LegalDomainProfile(
        domain_id="penal",
        name="Direito Penal",
        description="crime, pena, processo penal defensivo e garantias fundamentais penais",
        core_statutes=["Código Penal", "Código de Processo Penal", "Constituição Federal de 1988"],
        principles=["legalidade", "presunção de inocência", "individualização da pena"],
        keywords=["prisão", "pena", "crime", "habeas corpus", "dosimetria", "flagrante", "denúncia", "acusação", "defesa"],
        common_issues=["prisão preventiva", "tipicidade", "culpabilidade", "dosimetria", "nulidades processuais"],
        risk_vectors=["restrição indevida de liberdade", "nulidade", "prova ilícita"],
    ),
    "trabalhista": LegalDomainProfile(
        domain_id="trabalhista",
        name="Direito do Trabalho",
        description="relações de trabalho, verbas, vínculos, jornada e rescisão",
        core_statutes=["CLT", "Constituição Federal de 1988", "Legislação esparsa trabalhista"],
        principles=["proteção", "primazia da realidade", "continuidade da relação de emprego"],
        keywords=["rescisão", "justa causa", "horas extras", "verbas rescisórias", "vínculo", "fgts", "salário", "insalubridade"],
        common_issues=["vínculo empregatício", "horas extras", "adicionais", "justa causa", "terceirização"],
        risk_vectors=["passivo trabalhista", "fraude contratual", "descumprimento de jornada"],
    ),
    "tributario": LegalDomainProfile(
        domain_id="tributario",
        name="Direito Tributário",
        description="tributos, lançamento, execução fiscal, imunidade e planejamento tributário",
        core_statutes=["CTN", "Constituição Federal de 1988", "Lei de Execução Fiscal"],
        principles=["legalidade tributária", "anterioridade", "capacidade contributiva"],
        keywords=["tributo", "icms", "iss", "ipi", "execução fiscal", "crédito tributário", "auto de infração", "imunidade", "isenção"],
        common_issues=["lançamento", "prescrição", "decadência", "execução fiscal", "compensação"],
        risk_vectors=["autuação", "bitributação", "contencioso fiscal"],
    ),
    "empresarial": LegalDomainProfile(
        domain_id="empresarial",
        name="Direito Empresarial",
        description="sociedades, governança, contratos empresariais e recuperação judicial",
        core_statutes=["Código Civil", "Lei das S.A.", "Lei de Recuperação e Falências"],
        principles=["função social da empresa", "autonomia privada", "preservação da empresa"],
        keywords=["sociedade", "holding", "quotas", "acionista", "recuperação judicial", "falência", "governança", "contrato social"],
        common_issues=["governança societária", "responsabilidade de sócios", "acordos de quotistas", "recuperação judicial"],
        risk_vectors=["desconsideração da personalidade jurídica", "conflito societário", "insolvência"],
    ),
    "administrativo": LegalDomainProfile(
        domain_id="administrativo",
        name="Direito Administrativo",
        description="atos administrativos, licitações, improbidade e controle da administração pública",
        core_statutes=["Constituição Federal de 1988", "Lei de Licitações", "Lei de Improbidade Administrativa"],
        principles=["legalidade", "impessoalidade", "moralidade", "publicidade", "eficiência"],
        keywords=["licitação", "ato administrativo", "improbidade", "servidor", "processo administrativo", "sanção", "edital", "contrato administrativo"],
        common_issues=["nulidade do ato", "responsabilização de agente público", "dispensa de licitação", "controle externo"],
        risk_vectors=["nulidade administrativa", "responsabilização pessoal", "irregularidade contratual"],
    ),
    "ambiental": LegalDomainProfile(
        domain_id="ambiental",
        name="Direito Ambiental",
        description="licenciamento, dano ambiental, prevenção, reparação e sustentabilidade regulada",
        core_statutes=["Política Nacional do Meio Ambiente", "Lei de Crimes Ambientais", "Constituição Federal de 1988"],
        principles=["prevenção", "precaução", "poluidor-pagador", "desenvolvimento sustentável"],
        keywords=["licenciamento ambiental", "eia/rima", "dano ambiental", "poluição", "resíduo", "ibama", "supressão vegetal", "crime ambiental"],
        common_issues=["licença ambiental", "responsabilidade objetiva ambiental", "compensação ambiental", "passivo ambiental"],
        risk_vectors=["embargo", "multa ambiental", "responsabilidade civil objetiva"],
    ),
    "digital_lgpd": LegalDomainProfile(
        domain_id="digital_lgpd",
        name="Direito Digital e LGPD",
        description="proteção de dados, responsabilidade em tecnologia, governança digital e compliance informacional",
        core_statutes=["LGPD", "Marco Civil da Internet", "Constituição Federal de 1988"],
        principles=["finalidade", "necessidade", "transparência", "segurança", "accountability"],
        keywords=["lgpd", "dados pessoais", "consentimento", "controlador", "operador", "anonimização", "base legal", "privacidade", "incidente de segurança"],
        common_issues=["base legal", "incidente de segurança", "transferência internacional", "governança de dados", "uso de IA"],
        risk_vectors=["vazamento", "reidentificação", "sanção regulatória", "uso indevido de dados"],
    ),
}


def list_legal_domains() -> List[LegalDomainProfile]:
    return list(LEGAL_DOMAIN_PROFILES.values())


def get_legal_domain_profile(domain_id: str) -> Optional[LegalDomainProfile]:
    return LEGAL_DOMAIN_PROFILES.get(domain_id)


def _keyword_hits(text: str, keywords: List[str]) -> int:
    lowered = text.lower()
    return sum(1 for kw in keywords if kw.lower() in lowered)


def assess_domain_coverage(text: str, domain_id: str) -> float:
    profile = get_legal_domain_profile(domain_id)
    if not profile:
        return 0.0
    hits = _keyword_hits(text, profile.keywords)
    score = min(100.0, hits * 14.0 + (10.0 if hits else 0.0))
    return round(score, 2)


def route_legal_domain(query: str) -> LegalDomainProfile:
    query = query or ""
    best: Optional[Tuple[LegalDomainProfile, int]] = None
    for profile in LEGAL_DOMAIN_PROFILES.values():
        hits = _keyword_hits(query, profile.keywords)
        if best is None or hits > best[1]:
            best = (profile, hits)
    if best and best[1] > 0:
        return best[0]
    return LEGAL_DOMAIN_PROFILES["digital_lgpd"] if "dados" in query.lower() else LEGAL_DOMAIN_PROFILES["empresarial"] if "empresa" in query.lower() else LEGAL_DOMAIN_PROFILES["administrativo"] if "administra" in query.lower() else LEGAL_DOMAIN_PROFILES["penal"]


def build_domain_specialist_agent(domain_id: str) -> LegalAgentCard:
    profile = get_legal_domain_profile(domain_id)
    if not profile:
        raise ValueError(f"Domínio jurídico desconhecido: {domain_id}")
    return LegalAgentCard(
        id=f"auxjuris_{domain_id}_specialist",
        name=f"Especialista em {profile.name}",
        description=(
            f"Agente especialista em {profile.name}. Atua com foco em {profile.description}, "
            f"com atenção a {', '.join(profile.common_issues[:3])}."
        ),
        system_prompt=profile.specialist_prompt(),
        tools=["read", "write", "reason", "legal", domain_id],
        trust_threshold=0.65,
        category="legal",
    )


def route_specialist_agent(query: str) -> LegalAgentCard:
    profile = route_legal_domain(query)
    return build_domain_specialist_agent(profile.domain_id)


__all__ = [
    "LegalDomainProfile",
    "LEGAL_DOMAIN_PROFILES",
    "list_legal_domains",
    "get_legal_domain_profile",
    "route_legal_domain",
    "assess_domain_coverage",
    "build_domain_specialist_agent",
    "route_specialist_agent",
]
