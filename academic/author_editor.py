# -*- coding: utf-8 -*-
"""Autor/Editor de alto rigor (R991): estrutura IMRaD, estilo anti-plágio e raciocínio.

Nenhuma saída contém trecho verbatim: o "estilo" é descrito por características
estruturais e lexicais, nunca reproduzido. Pontuação interna não é aceite
editorial nem Qualis A1. Busca externa e LLM ficam nos conectores autorizados.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from typing import Any, Dict, List, Optional

MANUSCRIPT_SECTIONS: List[Dict[str, Any]] = [
    {"key": "titulo", "role": "identificar o estudo de forma específica e informativa",
     "moves": ["delimitar o objeto", "antecipar o recorte"]},
    {"key": "resumo", "role": "sintetizar objetivo, método, resultado e conclusão",
     "moves": ["estrutura IMRaD condensada", "palavras-chave"]},
    {"key": "introducao", "role": "contextualizar o problema, a lacuna e a justificativa",
     "moves": ["problema", "lacuna", "justificativa", "objetivo anunciado"]},
    {"key": "objetivos", "role": "declarar objetivo geral e objetivos específicos mensuráveis",
     "moves": ["objetivo geral", "objetivos específicos", "hipóteses quando aplicável"]},
    {"key": "fundamentacao_teorica", "role": "ancorar construtos em teorias e conceitos citados",
     "moves": ["definição de construtos", "diálogo com a literatura", "marco teórico"]},
    {"key": "metodologia", "role": "descrever desenho, amostra, instrumentos e análise de forma reproduzível",
     "moves": ["desenho", "participantes/amostra", "instrumentos", "procedimentos", "análise"]},
    {"key": "resultados", "role": "reportar achados com precisão e neutralidade interpretativa",
     "moves": ["descrição dos dados", "medidas observadas", "ausência de interpretação indevida"]},
    {"key": "discussao", "role": "interpretar achados em diálogo com a literatura, limites e contribuição",
     "moves": ["confronto com a teoria", "limites", "contribuição", "implicações"]},
    {"key": "conclusao", "role": "responder à pergunta central e aos objetivos sem introduzir novidade",
     "moves": ["síntese", "resposta ao objetivo", "trabalhos futuros"]},
    {"key": "referencias", "role": "listar fontes citadas com identificadores persistentes auditáveis",
     "moves": ["norma citacional", "DOI/identificador", "correspondência citação↔referência"]},
]

_HEADINGS = {
    "titulo": (r"^(?:#\s*)?titulo\b|^title\b",),
    "resumo": (r"^resumo\b|^abstract\b",),
    "introducao": (r"^introdu[çc][aã]o\b|^introduction\b",),
    "objetivos": (r"^objetivos?\b|^objectives?\b|^objetivo geral\b",),
    "fundamentacao_teorica": (r"^fundamenta[çc][aã]o te[oó]rica\b|^theoretical (?:framework|background)\b",),
    "metodologia": (r"^metodologia\b|^materiais? e m[ée]todos\b|^materials? and methods\b|^methods?\b",),
    "resultados": (r"^resultados?\b|^results?\b",),
    "discussao": (r"^discuss[aã]o\b|^discussion\b",),
    "conclusao": (r"^conclus[aã]o\b|^conclus[oõ]es\b|^conclusion\b|^conclusions?\b",),
    "referencias": (r"^refer[eê]ncias?\b|^bibliografia\b|^references?\b",),
}

_HEDGING = ("talvez", "possivelmente", "provavelmente", "sugere", "pode indicar", "em parte",
            "aparentemente", "tende a", "may", "might", "suggest", "likely", "possibly", "appears")
_CONNECTIVES = ("portanto", "assim", "ademais", "contudo", "entretanto", "no entanto", "por conseguinte",
                "dessa forma", "por outro lado", "therefore", "however", "moreover", "furthermore",
                "nevertheless", "thus", "consequently")
_FIRST_PERSON = ("nós", "nosso", "nossa", "nossos", "nossas", "we", "our", "eu", "i ")
_CIT_PATTERNS = (r"\([A-ZÀ-Ý][A-Za-zÀ-ÿ' -]+,?\s*\d{4}\)", r"\[[\d,\- ]+\]", r"\\cite\{", r"\b\d{4}\b")


def _normalize(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text.casefold())
    return "".join(c for c in folded if not unicodedata.combining(c))


def _text(value, maximum=200_000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or "\x00" in value:
        raise ValueError("Texto ausente, inválido ou excessivo")
    return value.strip()


def extract_structure(text: str) -> Dict[str, Any]:
    text = _text(text)
    keys = [s["key"] for s in MANUSCRIPT_SECTIONS]
    present: List[str] = []
    order: List[str] = []
    for line in text.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if not stripped:
            continue
        normalized = _normalize(stripped)
        for key in keys:
            if key in present:
                continue
            for pattern in _HEADINGS[key]:
                if re.match(pattern, normalized, re.IGNORECASE):
                    present.append(key)
                    order.append(key)
                    break
    # `order` preserva a ordem de aparecimento; seções ausentes ficam em missing.
    missing = [k for k in keys if k not in present]
    return {"present": present, "missing": missing, "order": order,
            "fabricated": [], "verbatim": [], "detection": "heading_heuristic",
            "human_review_required": True}


def style_fingerprint(text: str) -> Dict[str, Any]:
    text = _text(text)
    normalized = _normalize(text)
    words = re.findall(r"[a-zà-ÿ0-9]+", normalized)
    n_words = max(1, len(words))
    sentences = [s for s in re.split(r"[.!?]+", normalized) if s.strip()]
    first_person = sum(normalized.count(w) for w in _FIRST_PERSON)
    hedging = sum(normalized.count(w) for w in _HEDGING)
    connectives = sum(normalized.count(w) for w in _CONNECTIVES)
    citations = sum(len(re.findall(p, text, re.IGNORECASE)) for p in _CIT_PATTERNS)
    unique = len(set(words))
    register = "formal" if not first_person else "mixed_or_personal"
    return {
        "register": register,
        "person": "impersonal" if first_person == 0 else "first_person_present",
        "hedging": {"count": hedging, "density": round(hedging / n_words, 5)},
        "connectives": {"count": connectives, "density": round(connectives / n_words, 5)},
        "citation_density": {"count": citations, "density": round(citations / n_words, 5)},
        "sentence_count": len(sentences),
        "type_token_ratio": round(unique / n_words, 4),
        "verbatim_spans": [],  # anti-plágio por construção
        "anti_plagiarism": True,
        "style_scope": "structural_and_lexical_features_only",
        "human_review_required": True,
    }


def reasoning_registry() -> Dict[str, Any]:
    return {
        "axiomatico": {"name": "Raciocínio axiomático", "engine": "z3/sympy",
                       "axioms": ["sistema de axiomas consistente", "regras de inferência declaradas"],
                       "theorems": ["dedução de teoremas a partir de axiomas"],
                       "lemmas": ["lemas auxiliares prováveis", "corolários derivados"],
                       "laws": [], "scope": "formal_deduction_not_empirical_truth",
                       "proves_empirical_truth": False},
        "aristotelico": {"name": "Lógica aristotélica", "engine": "critical/z3",
                         "axioms": ["princípio da identidade", "princípio da não-contradição", "terceiro excluído"],
                         "laws": ["silogismo: premissa maior, premissa menor, conclusão", "modus ponens", "modus tollens"],
                         "lemmas": [], "scope": "deductive_validity",
                         "proves_empirical_truth": False},
        "cartesiano": {"name": "Método cartesiano", "engine": "critical/chain_of_thought",
                       "axioms": ["dúvida metódica", "evidência clara e distinta"],
                       "laws": ["dividir em partes", "ordenar do simples ao complexo", "enumeração completa"],
                       "lemmas": [], "scope": "methodological_clarity",
                       "proves_empirical_truth": False},
        "peirceano": {"name": "Lógica de Peirce", "engine": "arche_rlt/critical",
                      "axioms": ["abdução gera hipótese", "dedução deriva consequência", "indução testa"],
                      "laws": ["inferência à melhor explicação"], "lemmas": [],
                      "scope": "abductive_plausibility", "proves_empirical_truth": False},
        "popperiano": {"name": "Falsificacionismo", "engine": "critical",
                       "axioms": ["uma teoria científica é falsificável"],
                       "laws": ["conjecturas e refutações"], "lemmas": [],
                       "scope": "testability_not_confirmation", "proves_empirical_truth": False},
        "game_theory": {"name": "Teoria dos jogos", "engine": "game_theory_local/simulated_reviews_v2",
                        "axioms": ["utilidades declaradas", "jogadores e estratégias explícitos"],
                        "laws": ["equilíbrio de Nash", "ótimo de Pareto", "minimax regret"],
                        "lemmas": [], "scope": "strategic_priority_not_truth",
                        "proves_empirical_truth": False},
        "bayesiano": {"name": "Inferência bayesiana", "engine": "bayesian",
                      "axioms": ["priors explícitos"], "laws": ["teorema de Bayes"],
                      "lemmas": [], "scope": "belief_updating_given_prior",
                      "proves_empirical_truth": False},
        "causal": {"name": "Inferência causal", "engine": "causal",
                   "axioms": ["associação não implica causalidade"],
                   "laws": ["critérios de Bradford Hill", "contrafactual de Pearl"],
                   "lemmas": [], "scope": "causal_design_dependent",
                   "proves_empirical_truth": False},
        "dialetico": {"name": "Dialética", "engine": "dialectical/critical",
                      "axioms": ["toda tese admite antítese"],
                      "laws": ["tese-antítese-síntese"], "lemmas": [],
                      "scope": "argumentative_scrutiny", "proves_empirical_truth": False},
        "fuzzy": {"name": "Lógica difusa", "engine": "fuzzy",
                  "axioms": ["graus de pertinência em [0,1]"],
                  "laws": ["composição de conjuntos difusos"], "lemmas": [],
                  "scope": "approximate_reasoning", "proves_empirical_truth": False},
    }


def build_references_from_oa(oa_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Aplana resultados de busca OA e remove duplicatas por DOI ou título."""
    if not isinstance(oa_results, dict) or not isinstance(oa_results.get("searches"), list):
        raise ValueError("Resultado OA inválido")
    seen_doi = set()
    seen_title = set()
    refs: List[Dict[str, Any]] = []
    for search in oa_results["searches"]:
        if not isinstance(search, dict) or not isinstance(search.get("sources"), dict):
            raise ValueError("Busca OA inválida")
        for source_name, source in search["sources"].items():
            if not isinstance(source, dict) or source.get("status") != "ok":
                continue
            for record in source.get("results", []):
                if not isinstance(record, dict):
                    continue
                doi = record.get("doi")
                title = (record.get("title") or "").strip()
                if not title:
                    continue
                key = doi if doi else title.casefold()
                if key in (seen_doi if doi else seen_title):
                    continue
                (seen_doi if doi else seen_title).add(key)
                refs.append({"doi": doi, "title": title, "year": record.get("year"),
                             "source": source_name, "verified": False})
                if len(refs) >= 200:
                    return refs
    return refs


def author_brief(topic: str, sources: Optional[List[Dict[str, Any]]] = None,
                 bibliography: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    topic = _text(topic, 4000)
    references = []
    if sources is not None:
        if not isinstance(sources, list) or not 1 <= len(sources) <= 20:
            raise ValueError("Forneça entre uma e vinte fontes")
        ids = set()
        for source in sources:
            if not isinstance(source, dict) or set(source) != {"id", "text", "provenance"}:
                raise ValueError("Fonte deve conter id, text e provenance")
            sid = _text(source["id"], 100)
            if sid in ids:
                raise ValueError("ID de fonte duplicado")
            references.append({"source_id": sid,
                               "provenance": _text(source["provenance"], 300),
                               "text_sha256": __import__("hashlib").sha256(
                                   _text(source["text"], 8000).encode()).hexdigest(),
                               "role": "supplied_literal_evidence_only"})
            ids.add(sid)
    bib = []
    if bibliography is not None:
        if not isinstance(bibliography, list) or not 1 <= len(bibliography) <= 200:
            raise ValueError("Bibliografia deve ter entre uma e duzentas referências")
        seen = set()
        for ref in bibliography:
            if not isinstance(ref, dict) or set(ref) != {"doi", "title", "year", "source", "verified"}:
                raise ValueError("Referência deve conter doi, title, year, source e verified")
            if not isinstance(ref["title"], str) or not ref["title"].strip():
                raise ValueError("Referência sem título")
            if type(ref["verified"]) is not bool:
                raise ValueError("Campo verified deve ser booleano")
            key = ref["doi"] or ref["title"].casefold()
            if key in seen:
                raise ValueError("Referência duplicada")
            seen.add(key)
            bib.append({"doi": ref["doi"], "title": ref["title"].strip(),
                        "year": ref["year"], "source": ref["source"], "verified": ref["verified"]})
    verified_count = sum(1 for r in bib if r["verified"])
    section_references: Dict[str, List[int]] = {}
    if bib:
        idxs = list(range(len(bib)))
        section_references = {"introducao": idxs[:1], "fundamentacao_teorica": idxs, "referencias": idxs}
    frameworks = reasoning_registry()
    sections = [{"key": s["key"], "role": s["role"], "planned_moves": list(s["moves"])}
                for s in MANUSCRIPT_SECTIONS]
    return {
        "status": "planned", "topic": topic,
        "search": "supplied" if sources else "pending",
        "sections": sections,
        "reasoning_plan": [
            {"framework": name, "engine": fw["engine"],
             "why": "priorizar clareza e refutação, não validar conclusão por método."}
            for name, fw in frameworks.items()],
        "style_plan": {"register": "formal", "person": "impersonal_preferred",
                       "hedging": "proporcional à força da alegação",
                       "citations": "identificadores persistentes auditáveis",
                       "paragraph": "tópico frasal + evidência + análise + conexão"},
        "anti_plagiarism": {"verbatim_copy": False, "style_transfer": "structural_features_only",
                            "citation_of_sources": True, "paraphrase_with_citation": True},
        "references": references,
        "bibliography": bib,
        "references_verified_count": verified_count,
        "section_references": section_references,
        "scientific_acceptance": False, "human_review_required": True,
        "external_validation": False, "confidence_promoted": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Autor/Editor de alto rigor: estrutura, estilo e raciocínio.")
    parser.add_argument("operation", choices=("structure", "style", "brief"))
    parser.add_argument("--topic")
    parser.add_argument("--text", help="Manuscrito a analisar para structure/style.")
    parser.add_argument("--sources-json", help="Corpus não sensível para o plano.")
    args = parser.parse_args(argv)
    if args.operation == "structure":
        result = extract_structure(args.text or "")
    elif args.operation == "style":
        result = style_fingerprint(args.text or "")
    else:
        from scientific_lab.council import decode_json
        result = author_brief(args.topic or "", sources=decode_json(args.sources_json) if args.sources_json else None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result.get("status") == "blocked" else 0
