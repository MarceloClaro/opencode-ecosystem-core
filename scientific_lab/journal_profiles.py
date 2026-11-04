"""R1054 — perfis de periódicos reais e checagem objetiva de submissão.

O perfil PLOS ONE foi transcrito das diretrizes públicas em 2026-11-04. Ele não
é exaustivo e não certifica conformidade. A checagem separa falhas objetivas
(idioma, limite de resumo, seções, estilo de citação) de itens que exigem
decisão humana (declarações, ORCID, carta, ética).
"""
from __future__ import annotations

import datetime
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"

PROFILES: dict[str, dict[str, Any]] = {
    "plos-one": {
        "schema_version": SCHEMA_VERSION,
        "journal_id": "plos-one",
        "name": "PLOS ONE",
        "publisher": "PLOS",
        "language": "en",
        "article_types": [
            "Research Article", "Systematic Review", "Meta-Analysis",
            "Clinical Trial", "Registered Report",
        ],
        "file_formats": ["DOC", "DOCX", "RTF", "PDF (LaTeX)"],
        "word_limit": None,
        "abstract_max_words": 300,
        "title_max_chars": 250,
        "short_title_max_chars": 100,
        "reference_style": "Vancouver/ICMJE",
        "heading_levels": 3,
        "double_spaced": True,
        "page_line_numbers": True,
        "footnotes": False,
        "figures_separate": True,
        "tables_in_manuscript": True,
        "supporting_info_max_mb": 20,
        "cover_letter_max_pages": 1,
        "required_sections": [
            "Title page", "Abstract", "Introduction", "Materials and Methods",
            "Results", "Discussion", "Acknowledgments", "References",
        ],
        "required_declarations": [
            "financial_disclosure", "competing_interests", "data_availability",
            "author_contributions", "orcid", "ethics",
        ],
        "submission_url": "https://journals.plos.org/plosone/s/submission-guidelines",
        "source_url": "https://journals.plos.org/plosone/s/submission-guidelines",
        "verified_at": "2026-11-04",
        "notes": [
            "Resumo com no máximo 300 palavras e sem citações.",
            "Título completo com até 250 caracteres; título curto com até 100.",
            "Referências em Vancouver/ICMJE, numeradas na ordem de aparição.",
            "Figuras em arquivos separados; tabelas no manuscrito.",
            "Declarações financeiras e de conflito ficam no sistema, não no manuscrito.",
            "A fonte é pública; o perfil não é exaustivo nem certifica aceite.",
        ],
    },
    "generic-abnt": {
        "schema_version": SCHEMA_VERSION,
        "journal_id": "generic-abnt",
        "name": "Template ABNT genérico",
        "publisher": "não informado",
        "language": "pt-BR",
        "article_types": ["artigo"],
        "file_formats": ["DOCX", "PDF"],
        "word_limit": None,
        "abstract_max_words": 250,
        "title_max_chars": None,
        "short_title_max_chars": None,
        "reference_style": "ABNT",
        "heading_levels": 5,
        "double_spaced": False,
        "page_line_numbers": False,
        "footnotes": True,
        "figures_separate": False,
        "tables_in_manuscript": True,
        "supporting_info_max_mb": None,
        "cover_letter_max_pages": None,
        "required_sections": [
            "Resumo", "Introdução", "Métodos", "Resultados", "Discussão",
            "Conclusão", "Referências",
        ],
        "required_declarations": [],
        "submission_url": None,
        "source_url": None,
        "verified_at": None,
        "notes": [
            "Template genérico; não é um periódico real.",
            "Não certifica conformidade ABNT.",
        ],
    },
}


def load_profile(profile_id: str) -> dict:
    if profile_id not in PROFILES:
        raise ValueError(f"perfil de periódico desconhecido: {profile_id}")
    return dict(PROFILES[profile_id])


def _section(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##+\s+(?:\d+\.\s*)?{re.escape(heading)}\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##+\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\wÀ-ÖØ-öø-ÿ'-]+\b", text))


def _title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _has_portuguese_headings(text: str) -> bool:
    portuguese = ("Resumo", "Introdução", "Métodos", "Resultados", "Discussão", "Conclusão")
    return any(re.search(rf"^##+\s+{heading}\b", text, re.MULTILINE | re.IGNORECASE)
               for heading in portuguese)


def _numeric_citations(text: str) -> bool:
    return bool(re.search(r"\[\d+(?:[-,]\d+)*\]", text))


def validate_manuscript(manuscript_path: str | Path, profile: dict) -> dict:
    path = Path(manuscript_path)
    if not path.exists():
        raise ValueError("manuscrito ausente")
    text = path.read_text(encoding="utf-8")
    title = _title(text)
    abstract = _section(text, "Abstract") or _section(text, "Resumo")
    checks = []

    def add(check_id, status, detail, evidence=None):
        checks.append({
            "id": check_id,
            "status": status,
            "detail": detail,
            "evidence": evidence,
        })

    if profile.get("title_max_chars"):
        ok = 0 < len(title) <= profile["title_max_chars"]
        add("title_length", "pass" if ok else "fail",
            f"{len(title)} caractere(s); máximo {profile['title_max_chars']}")
    else:
        add("title_length", "not_applicable", "perfil sem limite de título")

    if profile.get("abstract_max_words"):
        words = _word_count(abstract)
        ok = 0 < words <= profile["abstract_max_words"]
        add("abstract_length", "pass" if ok else "fail",
            f"{words} palavra(s); máximo {profile['abstract_max_words']}")
        citations = bool(re.search(r"\[\d+\]|\([A-Z][^)]{0,80},\s*\d{4}\)", abstract))
        add("abstract_citations", "fail" if citations else "pass",
            "citação encontrada no resumo" if citations else "sem citação no resumo")
    else:
        add("abstract_length", "not_applicable", "perfil sem limite de resumo")

    language = profile.get("language")
    if language == "en":
        portuguese = _has_portuguese_headings(text)
        add("language", "fail" if portuguese else "pass",
            "cabeçalhos em português" if portuguese else "cabeçalhos em inglês")
    else:
        add("language", "pass", f"idioma declarado: {language}")

    missing = []
    for section in profile.get("required_sections", []):
        if section == "Title page":
            if not title:
                missing.append(section)
            continue
        if not re.search(
            rf"^##+\s+(?:\d+\.\s*)?{re.escape(section)}\b",
            text, re.MULTILINE | re.IGNORECASE,
        ):
            missing.append(section)
    add("required_sections", "pass" if not missing else "fail",
        "seções completas" if not missing else "ausentes: " + ", ".join(missing))

    style = profile.get("reference_style")
    if style == "Vancouver/ICMJE":
        add("reference_style", "pass" if _numeric_citations(text) else "fail",
            "citações numéricas encontradas" if _numeric_citations(text)
            else "sem citação numérica Vancouver")
    else:
        add("reference_style", "not_applicable", f"estilo {style}")

    for item in (
        "financial_disclosure", "competing_interests", "data_availability",
        "author_contributions", "orcid", "ethics",
    ):
        if item in profile.get("required_declarations", []):
            add(f"declaration_{item}", "pending_human",
                "declaração exige preenchimento/decisão humana")

    add("cover_letter", "pending_human", "carta deve ser revisada por humano")
    add("figures_separate", "pending_human",
        "conferir se cada figura está em arquivo separado")
    add("tables_in_manuscript", "pending_human",
        "conferir posição e legendas das tabelas")
    add(
        "word_count",
        "not_applicable" if profile.get("word_limit") is None else "pending_human",
        "perfil sem limite de palavras" if profile.get("word_limit") is None
        else f"limite de {profile['word_limit']} palavras",
    )
    add("formatting", "pending_human",
        "conferir espaçamento, paginação, linhas e níveis de título")
    add("supplementary", "pending_human",
        "conferir material suplementar e limites de tamanho")
    add("submission_system", "pending_human",
        "preencher o sistema de submissão do periódico")

    hard_fail = any(
        check["status"] == "fail" and not check["id"].startswith("declaration_")
        for check in checks
    )
    pending = any(check["status"] == "pending_human" for check in checks)
    status = "blocked" if hard_fail else "pending_human" if pending else "pass"
    return {
        "schema_version": SCHEMA_VERSION,
        "journal_id": profile.get("journal_id"),
        "journal": profile.get("name"),
        "checked_at": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(),
        "status": status,
        "hard_fail": hard_fail,
        "pending_human": pending,
        "checks": checks,
        "title": title,
        "abstract_words": _word_count(abstract),
        "source_url": profile.get("source_url"),
        "verified_at": profile.get("verified_at"),
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "O perfil transcreve regras públicas e não é exaustivo.",
            "A checagem não certifica conformidade nem aceite editorial.",
            "Itens subjetivos permanecem pending_human.",
        ],
    }


def checklist(profile: dict, validation: dict) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "journal_id": profile.get("journal_id"),
        "journal": profile.get("name"),
        "status": validation["status"],
        "items": validation["checks"],
        "source_url": profile.get("source_url"),
        "verified_at": profile.get("verified_at"),
        "policy": "journal_rules_not_inferred",
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
    }
