# -*- coding: utf-8 -*-
"""
Literary Research Scanners — rigor internacional para pesquisa literária
========================================================================

Scanners determinísticos para avaliar a robustez de pesquisa, busca,
fundamentação teórica, comparação de corpus e padrões internacionais em
projetos literários. São auxiliares críticos: não substituem revisão humana,
peer review, busca bibliográfica real ou validação externa.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Type


def _normalize(text: str) -> str:
    return (text or "").strip()


def _lower(text: str) -> str:
    return _normalize(text).lower()


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return round(max(lo, min(hi, value)), 2)


def _grade(score: float) -> str:
    if score >= 85:
        return "excelente"
    if score >= 70:
        return "forte"
    if score >= 50:
        return "consistente"
    if score >= 25:
        return "emergente"
    return "insuficiente"


def _count_keywords(text_lower: str, keywords: Iterable[str]) -> int:
    return sum(1 for kw in keywords if kw.lower() in text_lower)


def _hits(text_lower: str, keywords: Iterable[str], limit: int = 12) -> List[str]:
    return [kw for kw in keywords if kw.lower() in text_lower][:limit]


def _presence(count: int, target: int) -> float:
    if target <= 0:
        return 0.0
    return _clamp((count / target) * 100.0)


def _regex_count(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE | re.UNICODE))


@dataclass(frozen=True)
class ResearchDimension:
    name: str
    score: float
    evidence: List[str]
    rationale: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "score": _clamp(self.score),
            "evidence": list(self.evidence),
            "rationale": self.rationale,
        }


def _empty_result(scanner_id: str, name: str, dimension_names: Sequence[str]) -> Dict[str, Any]:
    return {
        "scanner_id": scanner_id,
        "name": name,
        "score": 0.0,
        "grade": "insuficiente",
        "dimensions": {
            dim: {"score": 0.0, "evidence": [], "rationale": "Texto ausente ou insuficiente."}
            for dim in dimension_names
        },
        "evidence": [],
        "warnings": ["Texto vazio ou insuficiente para avaliação de pesquisa literária."],
        "recommendations": ["Forneça pergunta de pesquisa, corpus, bibliografia, teoria, fontes e limites de escopo."],
    }


class LiteraryResearchScannerBase:
    scanner_id: ClassVar[str] = "literary_research_base"
    name: ClassVar[str] = "Scanner de Pesquisa Literária Base"
    dimension_names: ClassVar[Tuple[str, ...]] = ()

    def scan(self, text: str, metadata: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        clean = _normalize(text)
        if not clean:
            return _empty_result(self.scanner_id, self.name, self.dimension_names)
        dims = self._evaluate(clean, metadata or {})
        score = _clamp(sum(d.score for d in dims) / max(1, len(dims)))
        dimensions = {d.name: d.as_dict() for d in dims}
        evidence: List[str] = []
        for dim in dims:
            for item in dim.evidence:
                if item not in evidence:
                    evidence.append(item)
        warnings = self._warnings(score, dimensions)
        recommendations = self._recommendations(score, dimensions)
        return {
            "scanner_id": self.scanner_id,
            "name": self.name,
            "score": score,
            "grade": _grade(score),
            "dimensions": dimensions,
            "evidence": evidence[:16],
            "warnings": warnings,
            "recommendations": recommendations,
        }

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[ResearchDimension]:
        raise NotImplementedError

    def _warnings(self, score: float, dimensions: Mapping[str, Any]) -> List[str]:
        warnings = []
        weak = [name for name, payload in dimensions.items() if payload["score"] < 40]
        if weak:
            warnings.append("Dimensões de pesquisa frágeis: " + ", ".join(weak[:5]) + ".")
        if score < 35:
            warnings.append("Pesquisa ainda insuficiente para reivindicação de rigor internacional.")
        return warnings

    def _recommendations(self, score: float, dimensions: Mapping[str, Any]) -> List[str]:
        recs = []
        for name, payload in dimensions.items():
            if payload["score"] < 55:
                recs.append(f"Fortaleça '{name}' com fontes, método ou evidências explícitas.")
        if not recs:
            recs.append("Manter protocolo de evidências e submeter bibliografia a revisão especializada.")
        return recs[:7]


class LiteraryBibliographyScanner(LiteraryResearchScannerBase):
    scanner_id = "literary_bibliography"
    name = "Scanner de Bibliografia Literária"
    dimension_names = ("fontes_primarias", "fontes_secundarias", "bases_e_indices", "identificadores_e_edicoes")

    PRIMARY = ["corpus primário", "obra", "edição", "romance", "conto", "poema", "texto-base", "original", "tradução"]
    SECONDARY = ["artigo", "livro acadêmico", "crítica", "revisado por pares", "peer-reviewed", "ensaio", "capítulo", "dissertação", "tese"]
    DATABASES = ["mla", "jstor", "project muse", "scielo", "google scholar", "worldcat", "periódicos capes", "catálogo", "library of congress"]
    IDS = ["doi", "isbn", "issn", "página", "edição", "editora", "ano", "url", "data de acesso"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[ResearchDimension]:
        low = _lower(text)
        doi_like = _regex_count(text, r"10\.\d{4,9}/[-._;()/:A-Z0-9]+")
        isbn_like = _regex_count(text, r"\b97[89][\d\- ]{9,17}\b")
        return [
            ResearchDimension("fontes_primarias", _presence(_count_keywords(low, self.PRIMARY), 4), _hits(low, self.PRIMARY), "Delimitação de obras e edições primárias."),
            ResearchDimension("fontes_secundarias", _presence(_count_keywords(low, self.SECONDARY), 5), _hits(low, self.SECONDARY), "Presença de crítica, artigos, livros e estudos especializados."),
            ResearchDimension("bases_e_indices", _presence(_count_keywords(low, self.DATABASES), 4), _hits(low, self.DATABASES), "Uso de bases reconhecidas internacionalmente."),
            ResearchDimension("identificadores_e_edicoes", _clamp((_presence(_count_keywords(low, self.IDS), 5) * 0.75) + (_presence(doi_like + isbn_like, 2) * 0.25)), _hits(low, self.IDS) + ([f"{doi_like} DOI(s)"] if doi_like else []) + ([f"{isbn_like} ISBN(s)"] if isbn_like else []), "Rastreabilidade bibliográfica por edição, página e identificadores."),
        ]


class ComparativeCorpusScanner(LiteraryResearchScannerBase):
    scanner_id = "comparative_corpus"
    name = "Scanner de Corpus Comparativo"
    dimension_names = ("delimitacao_corpus", "tradicoes_e_generos", "eixos_comparativos", "diferenciacao")

    CORPUS = ["corpus", "corpus primário", "corpus secundário", "obras análogas", "critérios de inclusão", "critérios de exclusão", "amostra"]
    TRADITIONS = ["tradição", "gênero", "romance", "horror", "fantástico", "arquivo", "documental", "ergódica", "metaficção", "comparada"]
    AXES = ["motivo", "tema", "forma", "período", "recepção", "materialidade", "narrador", "paratexto", "estrutura", "estilo"]
    DIFFERENCE = ["diferenciação", "distinção", "lacuna", "inovação", "contribuição", "posicionamento", "singularidade", "limite"]
    AUTHORS = ["machado", "shelley", "borges", "poe", "cortázar", "calvino", "danielewski", "aleksiévitch", "joyce", "lispector"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[ResearchDimension]:
        low = _lower(text)
        author_hits = _hits(low, self.AUTHORS)
        return [
            ResearchDimension("delimitacao_corpus", _presence(_count_keywords(low, self.CORPUS), 4), _hits(low, self.CORPUS), "Clareza sobre corpus e critérios de seleção."),
            ResearchDimension("tradicoes_e_generos", _presence(_count_keywords(low, self.TRADITIONS), 5), _hits(low, self.TRADITIONS), "Mapeamento de gênero, tradição e família formal."),
            ResearchDimension("eixos_comparativos", _presence(_count_keywords(low, self.AXES), 5), _hits(low, self.AXES), "Definição de eixos comparáveis entre obras."),
            ResearchDimension("diferenciacao", _clamp((_presence(_count_keywords(low, self.DIFFERENCE), 4) * 0.65) + (_presence(len(author_hits), 4) * 0.35)), _hits(low, self.DIFFERENCE) + author_hits, "Diferenciação da obra frente a autores, obras e lacunas."),
        ]


class TheoreticalFrameworkScanner(LiteraryResearchScannerBase):
    scanner_id = "theoretical_framework"
    name = "Scanner de Fundamentação Teórica"
    dimension_names = ("autores_teoricos", "conceitos_operacionais", "adequacao_metodologica", "interdisciplinaridade")

    THEORISTS = ["genette", "foucault", "ricoeur", "lacapra", "hutcheon", "aarseth", "eco", "barthes", "todorov", "goffman", "freud", "bakhtin"]
    CONCEPTS = ["paratexto", "arquivo", "memória", "trauma", "metaficção", "ergódica", "obra aberta", "fantástico", "focalização", "intertextualidade"]
    METHOD = ["metodologia", "método", "operacionalização", "matriz", "critério", "categoria", "eixo", "hipótese", "pergunta de pesquisa"]
    INTER = ["história", "psicanálise", "sociologia", "filosofia", "humanidades médicas", "estudos culturais", "antropologia", "teoria literária"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[ResearchDimension]:
        low = _lower(text)
        return [
            ResearchDimension("autores_teoricos", _presence(_count_keywords(low, self.THEORISTS), 5), _hits(low, self.THEORISTS), "Presença de autores teóricos reconhecíveis e pertinentes."),
            ResearchDimension("conceitos_operacionais", _presence(_count_keywords(low, self.CONCEPTS), 5), _hits(low, self.CONCEPTS), "Conceitos críticos que podem orientar análise textual."),
            ResearchDimension("adequacao_metodologica", _presence(_count_keywords(low, self.METHOD), 5), _hits(low, self.METHOD), "Indícios de método e operacionalização, não apenas nomes teóricos."),
            ResearchDimension("interdisciplinaridade", _presence(_count_keywords(low, self.INTER), 3), _hits(low, self.INTER), "Diálogo controlado com áreas auxiliares relevantes."),
        ]


class InternationalRigorScanner(LiteraryResearchScannerBase):
    scanner_id = "international_rigor"
    name = "Scanner de Rigor Internacional em Pesquisa Literária"
    dimension_names = ("transparencia_escopo", "verificabilidade_fontes", "anti_overclaim", "etica_e_limites")

    SCOPE = ["escopo", "limitação", "limitações", "critério", "inclusão", "exclusão", "pergunta", "hipótese", "lacuna"]
    VERIFY = ["citação", "página", "doi", "isbn", "edição", "fonte", "referência", "data de acesso", "evidência", "verificável"]
    OVERCLAIM = ["anti-overclaim", "não substitui", "hipótese interpretativa", "não validação", "revisão externa", "cautela", "não canônica", "corpus comparativo"]
    ETHICS = ["ética", "trauma", "representação", "alteridade", "apropriação", "romantização", "testemunho", "reparação", "responsabilidade"]

    def _evaluate(self, text: str, metadata: Mapping[str, Any]) -> List[ResearchDimension]:
        low = _lower(text)
        return [
            ResearchDimension("transparencia_escopo", _presence(_count_keywords(low, self.SCOPE), 5), _hits(low, self.SCOPE), "Clareza de escopo, hipótese, lacunas e critérios."),
            ResearchDimension("verificabilidade_fontes", _presence(_count_keywords(low, self.VERIFY), 6), _hits(low, self.VERIFY), "Rastreabilidade por citação, edição, páginas e identificadores."),
            ResearchDimension("anti_overclaim", _presence(_count_keywords(low, self.OVERCLAIM), 4), _hits(low, self.OVERCLAIM), "Formulações que impedem claims de originalidade/validação sem prova."),
            ResearchDimension("etica_e_limites", _presence(_count_keywords(low, self.ETHICS), 4), _hits(low, self.ETHICS), "Atenção a ética, trauma, representação e responsabilidade."),
        ]

    def _warnings(self, score: float, dimensions: Mapping[str, Any]) -> List[str]:
        warnings = super()._warnings(score, dimensions)
        if dimensions.get("anti_overclaim", {}).get("score", 0) < 40:
            warnings.append("Risco de reivindicação internacional sem revisão externa ou corpus comparativo suficiente.")
        return warnings


LITERARY_RESEARCH_SCANNER_CLASSES: Tuple[Type[LiteraryResearchScannerBase], ...] = (
    LiteraryBibliographyScanner,
    ComparativeCorpusScanner,
    TheoreticalFrameworkScanner,
    InternationalRigorScanner,
)


def run_literary_research_scanner_suite(text: str, metadata: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    meta = dict(metadata or {})
    results: Dict[str, Dict[str, Any]] = {}
    for scanner_cls in LITERARY_RESEARCH_SCANNER_CLASSES:
        scanner = scanner_cls()
        results[scanner.scanner_id] = scanner.scan(text, meta)
    scores = [payload["score"] for payload in results.values()]
    aggregate = _clamp(sum(scores) / max(1, len(scores))) if _normalize(text) else 0.0
    recommendations: List[str] = []
    warnings: List[str] = []
    for payload in results.values():
        for rec in payload.get("recommendations", []):
            if rec not in recommendations:
                recommendations.append(rec)
        for warn in payload.get("warnings", []):
            if warn not in warnings:
                warnings.append(warn)
    return {
        "domain": "literary_research",
        "scanner_count": len(results),
        "international_research_rigor_score": aggregate,
        "grade": _grade(aggregate),
        "results": results,
        "metadata": meta,
        "recommendations": recommendations[:12],
        "warnings": warnings[:12],
        "overclaim_guard": (
            "Este índice não substitui busca bibliográfica real, crítica literária humana, "
            "peer review, comparação de corpus por especialista ou validação acadêmica externa."
        ),
    }


literary_research_scanner_suite = run_literary_research_scanner_suite
