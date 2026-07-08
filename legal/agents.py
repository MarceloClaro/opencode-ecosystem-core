# -*- coding: utf-8 -*-
"""
Legal Agents — Especialistas Jurídicos para OpenCode A2A (SPEC-923)
=====================================================================
Mapeia os 4 agentes do AUXJURIS para o formato Agent Card do OpenCode,
permitindo que o Blackboard A2A os descubra e delegue tarefas.

Agentes:
  1. auxjuris_legal_assistant    — Informações jurídicas gerais + subsunção
  2. auxjuris_document_summarizer — Sumarização de documentos legais
  3. auxjuris_email_drafter       — Redação de e-mails jurídicos
  4. auxjuris_legal_research      — Pesquisa em base de conhecimento + Datajud
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LegalAgentCard:
    """Agent Card compatível com o protocolo A2A do OpenCode.

    Mapeia diretamente para o formato usado pelo Blackboard no MCI.
    """
    id: str
    name: str
    description: str
    system_prompt: str
    tools: List[str] = field(default_factory=lambda: ["read", "write", "reason"])
    trust_threshold: float = 0.5
    category: str = "legal"

    def to_a2a_card(self) -> Dict[str, Any]:
        """Converte para formato de Agent Card do Blackboard A2A."""
        return {
            "agent_id": self.id,
            "name": self.name,
            "description": self.description,
            "capabilities": list(dict.fromkeys([self.category, *self.tools])),
            "schema": {
                "category": self.category,
                "trust_threshold": self.trust_threshold,
                "system_prompt": self.system_prompt,
            },
            "system_prompt": self.system_prompt,
        }


# ── 4 Agentes Jurídicos ────────────────────────────────────────────────

LEGAL_AGENTS: List[LegalAgentCard] = [
    LegalAgentCard(
        id="auxjuris_legal_assistant",
        name="Assistente Jurídico Geral",
        description=(
            "Fornece informações jurídicas gerais, analisa casos usando "
            "subsunção legal (LegalSyllogism), ponderação de princípios "
            "(PrincipleBalancing) e pesquisa de precedentes (PrecedentAnalyzer). "
            "Integra dados do Datajud para contexto processual real."
        ),
        system_prompt=(
            "Você é um assistente jurídico altamente competente e prestativo. "
            "Sua missão é fornecer informações claras, concisas e precisas "
            "com base na legislação brasileira (CF/88, CPC/2015, CC/2002, CP). "
            "Use os motores de raciocínio jurídico disponíveis: LegalSyllogism "
            "para subsunção, PrincipleBalancing para ponderação, "
            "PrecedentAnalyzer para análise de precedentes. "
            "Consulte a base de conhecimento jurídico e dados do Datajud "
            "quando relevante. Seja sempre profissional, objetivo e ético. "
            "Se a pergunta for ambígua, peça esclarecimentos. "
            "Se estiver fora do escopo jurídico, declare educadamente."
        ),
        tools=["read", "write", "reason", "legal"],
        trust_threshold=0.6,
    ),
    LegalAgentCard(
        id="auxjuris_document_summarizer",
        name="Sumarizador de Documentos Jurídicos",
        description=(
            "Resume petições, contratos, ementas, acórdãos e outros "
            "documentos legais de forma precisa. Extrai entidades jurídicas "
            "(leis, artigos, precedentes) e identifica a estrutura do documento. "
            "Integra com PrecedentAnalyzer para enriquecer o resumo com "
            "análise de precedentes relacionados."
        ),
        system_prompt=(
            "Você é um especialista em sumarização de documentos e textos legais. "
            "Analise o texto fornecido e produza um resumo conciso, preciso, "
            "que capture os pontos essenciais e as implicações legais. "
            "Identifique: (1) partes envolvidas, (2) objeto da demanda, "
            "(3) fundamentos jurídicos principais, (4) dispositivos legais citados, "
            "(5) conclusão/decisão. "
            "Se precedentes relevantes forem encontrados no PrecedentAnalyzer, "
            "inclua-os contextualmente. "
            "Evite introduzir opiniões ou informações externas não solicitadas."
        ),
        tools=["read", "write"],
        trust_threshold=0.5,
    ),
    LegalAgentCard(
        id="auxjuris_email_drafter",
        name="Redator de E-mail Jurídico",
        description=(
            "Ajuda a redigir e-mails com tom profissional e conteúdo "
            "jurídico adequado. Gera minutas de comunicação para "
            "advogados, clientes, tribunais e contrapartes."
        ),
        system_prompt=(
            "Você é um assistente especializado na redação de e-mails "
            "formais para o contexto jurídico brasileiro. "
            "O e-mail deve ser profissional, claro, cortês, "
            "gramaticalmente correto e juridicamente apropriado. "
            "Preste atenção ao público-alvo (juiz, advogado adverso, cliente) "
            "e ao objetivo do e-mail (cobrança, intimação, parecer, etc.). "
            "Use linguagem formal mas acessível. Inclua referências legais "
            "apenas quando relevante e solicitado."
        ),
        tools=["read", "write"],
        trust_threshold=0.4,
    ),
    LegalAgentCard(
        id="auxjuris_legal_research",
        name="Analista de Pesquisa Jurídica",
        description=(
            "Pesquisa na base de conhecimento jurídico e nos dados do "
            "Datajud (27 tribunais estaduais). Identifica doutrina, "
            "jurisprudência e legislação relevante para a consulta. "
            "Retorna trechos contextualizados com fontes."
        ),
        system_prompt=(
            "Você é um analista de pesquisa jurídica. "
            "Sua tarefa é analisar a consulta do usuário e identificar "
            "as informações mais pertinentes na base de conhecimento jurídico "
            "e nos dados processuais do Datajud. "
            "Apresente os trechos relevantes encontrados e explique "
            "brevemente sua conexão com a pergunta do usuário. "
            "Priorize fontes jurisprudenciais dos tribunais superiores (STF, STJ) "
            "e súmulas vinculantes. "
            "Se nenhum documento parecer relevante, indique isso claramente "
            "e sugira termos de busca alternativos."
        ),
        tools=["read", "write", "reason"],
        trust_threshold=0.6,
    ),
]


def get_legal_agent(agent_id: str) -> Optional[LegalAgentCard]:
    """Retorna um agente jurídico pelo ID."""
    for agent in LEGAL_AGENTS:
        if agent.id == agent_id:
            return agent
    return None


def resolve_legal_agent(query: str) -> LegalAgentCard:
    """Resolve o agente jurídico mais adequado para uma consulta.

    Usa heurística simples baseada em palavras-chave.
    """
    q = query.lower()
    if any(p in q for p in ["resum", "sumariz", "síntese", "compacto"]):
        return get_legal_agent("auxjuris_document_summarizer")
    elif any(p in q for p in ["email", "e-mail", "carta", "ofício", "comunica"]):
        return get_legal_agent("auxjuris_email_drafter")
    elif any(p in q for p in ["pesquis", "buscar", "encontrar", "doutrina",
                                "jurisprudência", "artigo", "lei"]):
        return get_legal_agent("auxjuris_legal_research")
    else:
        return get_legal_agent("auxjuris_legal_assistant")


def get_all_legal_agent_cards() -> List[Dict[str, Any]]:
    """Retorna todos os Agent Cards para registro no Blackboard A2A."""
    return [agent.to_a2a_card() for agent in LEGAL_AGENTS]


def register_legal_agents(metabus) -> int:
    """Registra os agentes jurídicos no Blackboard via MetaBus."""
    count = 0
    for agent in LEGAL_AGENTS:
        payload = agent.to_a2a_card()
        metabus.publish("agent.register", payload, source_agent="legal.agents")
        count += 1
    return count


__all__ = [
    "LegalAgentCard",
    "LEGAL_AGENTS",
    "get_legal_agent",
    "resolve_legal_agent",
    "get_all_legal_agent_cards",
    "register_legal_agents",
]
