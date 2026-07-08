# -*- coding: utf-8 -*-
"""
LegalKnowledgeBase — Base de Conhecimento Jurídico com RAG por Keywords (SPEC-923)
===================================================================================
Implementa o sistema de conhecimento jurídico inspirado no AUXJURIS:
documentos indexados por keywords + conteúdo textual, busca contextual,
e integração com dados do Datajud para enriquecimento automático.

Funciona como fonte de grounding para os agentes jurídicos e para
o módulo de raciocínio legal (SPEC-921).
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("legal.knowledge_base")


@dataclass
class LegalDocument:
    """Documento jurídico na base de conhecimento.

    Inspirado no KnowledgeDocument do AUXJURIS, com suporte a
    metadados expandidos e proveniência.
    """
    id: str
    title: str
    content: str
    keywords: List[str] = field(default_factory=list)
    category: str = "geral"          # doutrina, jurisprudencia, legislacao, contrato
    source: str = "knowledge_base"    # knowledge_base, datajud, usuario
    tribunal: Optional[str] = None    # Se veio do Datajud
    precedente_id: Optional[str] = None  # Ligação com PrecedentAnalyzer

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "source": self.source,
            "tribunal": self.tribunal,
            "keywords": self.keywords,
            "content_preview": self.content[:100] + "..." if len(self.content) > 100 else self.content,
        }


# ── Base de conhecimento padrão (inspirada no AUXJURIS + expansão OpenCode) ────

DEFAULT_LEGAL_DOCUMENTS: List[LegalDocument] = [
    LegalDocument(
        id="doc_contrato_validade",
        title="Princípios Básicos do Contrato (CC/2002)",
        content=(
            "O contrato é um acordo de vontades que cria, modifica ou extingue "
            "direitos e obrigações (CC, art. 421-480). Para ser válido, requer "
            "agentes capazes, objeto lícito, possível, determinado ou determinável, "
            "e forma prescrita ou não defesa em lei (CC, art. 104). A boa-fé objetiva "
            "deve permear todas as fases do contrato (CC, art. 422). A função social "
            "do contrato é princípio fundamental (CC, art. 421)."
        ),
        keywords=["contrato", "validade", "boa-fé", "obrigação", "acordo",
                   "cc", "código civil", "objeto lícito", "agente capaz"],
        category="doutrina",
    ),
    LegalDocument(
        id="doc_responsabilidade_civil",
        title="Responsabilidade Civil Objetiva e Subjetiva (CC/2002)",
        content=(
            "A responsabilidade civil subjetiva baseia-se na culpa (negligência, "
            "imprudência ou imperícia) do agente causador do dano (CC, art. 186). "
            "Já a responsabilidade civil objetiva independe de culpa, bastando a "
            "relação de causalidade entre a conduta e o dano (CC, art. 927, parágrafo único). "
            "É aplicável nos casos especificados em lei ou quando a atividade "
            "normalmente desenvolvida pelo autor do dano implicar risco para "
            "direitos de outrem. O dano moral é devido em caso de violação "
            "aos direitos da personalidade (CF, art. 5º, V e X)."
        ),
        keywords=["responsabilidade civil", "dano", "culpa", "objetiva",
                   "subjetiva", "risco", "indenização", "reparação"],
        category="doutrina",
    ),
    LegalDocument(
        id="doc_consumidor_vicio",
        title="Direitos do Consumidor — Vício do Produto (CDC)",
        content=(
            "O consumidor tem direito à substituição do produto, à restituição "
            "imediata da quantia paga ou ao abatimento proporcional do preço "
            "quando o produto apresentar vício de qualidade ou quantidade que "
            "o torne impróprio ou inadequado ao consumo (CDC, art. 18). "
            "O fornecedor tem prazo de 30 dias para sanar o vício. "
            "Tratando-se de vício oculto, o prazo para reclamar inicia-se "
            "no momento em que ficar evidenciado o defeito (CDC, art. 26, §3º). "
            "A garantia legal é independente de garantia contratual."
        ),
        keywords=["consumidor", "vício", "produto", "defeito", "garantia",
                   "troca", "restituição", "cdc", "fornecedor"],
        category="legislacao",
    ),
    LegalDocument(
        id="doc_habeas_corpus",
        title="Habeas Corpus — Conceito e Aplicação (CF/88)",
        content=(
            "O Habeas Corpus é uma garantia constitucional que visa proteger "
            "o direito de ir e vir (liberdade de locomoção) contra ilegalidade "
            "ou abuso de poder (CF, art. 5º, LXVIII). Pode ser impetrado por "
            "qualquer pessoa, em seu favor ou de outrem, bem como pelo Ministério "
            "Público (CPP, art. 654). O STF tem jurisprudência consolidada de "
            "que HC não é cabível quando o ato ilegal já cessou (Súmula 695 STF). "
            "O HC preventivo (salvo-conduto) é cabível quando há ameaça de "
            "violação à liberdade."
        ),
        keywords=["habeas corpus", "liberdade", "prisão", "ilegalidade",
                   "constitucional", "stf", "salvo-conduto", "locomoção"],
        category="jurisprudencia",
    ),
    LegalDocument(
        id="doc_precedentes_cpc",
        title="Precedentes Vinculantes no CPC/2015",
        content=(
            "O CPC/2015 estabelece um sistema de precedentes vinculantes "
            "(arts. 926-928). Os tribunais devem uniformizar sua jurisprudência "
            "e mantê-la estável, íntegra e coerente (art. 926). A ratio decidendi "
            "dos julgamentos de recursos repetitivos e repercussão geral "
            "vincula todos os órgãos do Poder Judiciário (art. 927). "
            "O distinguishing é admitido quando o caso concreto possuir "
            "particularidades que afastem a aplicação do precedente (art. 489, §1º, VI). "
            "O overruling exige fundamentação específica e observância do "
            "princípio da segurança jurídica."
        ),
        keywords=["precedente", "cpc", "vinculante", "ratio decidendi",
                   "distinguishing", "overruling", "stf", "stj",
                   "repercussão geral", "recurso repetitivo"],
        category="legislacao",
    ),
    LegalDocument(
        id="doc_principios_constitucionais",
        title="Princípios Constitucionais Fundamentais (CF/88)",
        content=(
            "A Constituição Federal de 1988 estabelece como fundamentos da "
            "República: a soberania, a cidadania, a dignidade da pessoa humana, "
            "os valores sociais do trabalho e da livre iniciativa, e o "
            "pluralismo político (CF, art. 1º). São objetivos fundamentais: "
            "construir uma sociedade livre, justa e solidária; garantir o "
            "desenvolvimento nacional; erradicar a pobreza e reduzir as "
            "desigualdades; promover o bem de todos (CF, art. 3º). "
            "A aplicação dos princípios constitucionais exige ponderação "
            "(Alexy) e proporcionalidade quando colidirem entre si."
        ),
        keywords=["constituição", "cf/88", "princípios", "dignidade",
                   "cidadania", "soberania", "fundamentos", "objetivos"],
        category="doutrina",
    ),
]


class LegalKnowledgeBase:
    """Base de conhecimento jurídico com busca por keywords e RAG contextual.

    Inspirada no sistema de KnowledgeDocuments do AUXJURIS.
    Suporta:
      - Documentos com keywords para busca textual
      - RAG com limite de contexto
      - Integração com Datajud para documentos processuais
      - Registro de fontes (doutrina, jurisprudência, legislação)
    """

    def __init__(self):
        self._documents: Dict[str, LegalDocument] = {}
        # Carregar documentos padrão
        for doc in DEFAULT_LEGAL_DOCUMENTS:
            self._documents[doc.id] = doc

    def add_document(self, doc: LegalDocument) -> None:
        """Adiciona um documento à base de conhecimento."""
        self._documents[doc.id] = doc
        logger.info(f"Documento adicionado: {doc.id} — {doc.title}")

    def get_document(self, doc_id: str) -> Optional[LegalDocument]:
        """Retorna um documento pelo ID."""
        return self._documents.get(doc_id)

    def remove_document(self, doc_id: str) -> bool:
        """Remove um documento da base."""
        if doc_id in self._documents:
            del self._documents[doc_id]
            return True
        return False

    def list_documents(self, category: Optional[str] = None) -> List[LegalDocument]:
        """Lista documentos, opcionalmente filtrados por categoria."""
        if category:
            return [d for d in self._documents.values() if d.category == category]
        return list(self._documents.values())

    def search(self, query: str, max_results: int = 3) -> List[Tuple[LegalDocument, float]]:
        """Busca documentos por correspondência de keywords e conteúdo textual.

        Algoritmo (inspirado no AUXJURIS):
          1. Extrai palavras-chave da query (len > 2)
          2. Para cada documento, calcula score:
             - +2 por keyword do documento correspondida
             - +1 por ocorrência no conteúdo
          3. Ordena por score decrescente
          4. Retorna top max_results

        Returns:
            Lista de (documento, score).
        """
        query_keywords = set(
            kw.lower() for kw in query.split()
            if len(kw) > 2
        )

        scored: List[Tuple[LegalDocument, float]] = []
        for doc in self._documents.values():
            score = 0.0
            content_lower = doc.content.lower()

            # Score por keywords do documento
            for kw in doc.keywords:
                kw_lower = kw.lower()
                for qkw in query_keywords:
                    if kw_lower in qkw or qkw in kw_lower:
                        score += 2.0
                        break

            # Score por conteúdo
            for qkw in query_keywords:
                if qkw in content_lower:
                    score += 1.0

            if score > 0:
                scored.append((doc, score))

        # Ordenar por score decrescente
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:max_results]

    def rag_context(self, query: str, max_chars: int = 1500) -> str:
        """Monta contexto RAG com documentos relevantes para a query.

        Args:
            query: Consulta do usuário.
            max_chars: Limite máximo de caracteres do contexto.

        Returns:
            String formatada com o contexto para usar em prompts.
        """
        results = self.search(query)

        if not results:
            return ""

        prefix = "Contexto de Documentos de Referência Relevantes:\n---\n"
        suffix = "---\n"
        body_budget = max(max_chars - len(prefix) - len(suffix), 0)

        parts: List[str] = []
        current_len = 0

        for doc, score in results:
            header = f"[{doc.category.upper()}] {doc.title}"
            content = doc.content
            entry = f"{header}\n{content}\n"

            if current_len + len(entry) > body_budget:
                # Truncar se necessário
                remaining = body_budget - current_len
                if remaining > 50:
                    entry = entry[:remaining] + "...\n"
                    parts.append(entry)
                break

            parts.append(entry)
            current_len += len(entry)

        if not parts:
            return ""

        return f"{prefix}{''.join(parts)}{suffix}"

    def load_from_datajud(self, processos: List[Any],
                          datajud_client: Optional[Any] = None) -> int:
        """Carrega processos do Datajud como documentos na base.

        Args:
            processos: Lista de DatajudProcess.
            datajud_client: Instância do DatajudClient (opcional).

        Returns:
            Número de documentos adicionados.
        """
        count = 0
        for proc in processos:
            # Extrair tribunal
            tribunal = getattr(proc, 'tribunal', '')
            tribunal_nome = getattr(proc, 'tribunal_nome', tribunal.upper())

            # Construir conteúdo a partir dos dados do processo
            partes = [f"Processo: {getattr(proc, 'numero_processo', '')}"]
            if proc.classe_nome:
                partes.append(f"Classe: {proc.classe_nome}")
            for assunto in getattr(proc, 'assuntos', []):
                partes.append(f"Assunto: {assunto.get('nome', '')}")
            if proc.resultado:
                partes.append(f"Resultado: {proc.resultado}")

            conteudo = "\n".join(partes)

            # Extrair keywords dos assuntos
            keywords = []
            for assunto in getattr(proc, 'assuntos', []):
                nome = assunto.get('nome', '')
                keywords.extend(nome.lower().split())

            doc = LegalDocument(
                id=f"datajud_{proc.tribunal}_{proc.id}",
                title=f"Processo {proc.numero_processo} — {tribunal_nome}",
                content=conteudo,
                keywords=keywords,
                category="jurisprudencia",
                source="datajud",
                tribunal=tribunal,
            )
            self.add_document(doc)
            count += 1

        return count

    def count(self) -> int:
        """Número total de documentos na base."""
        return len(self._documents)

    def get_categories(self) -> List[str]:
        """Lista categorias disponíveis."""
        return list({d.category for d in self._documents.values()})
