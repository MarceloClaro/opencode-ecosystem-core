"""R1051 — pesquisador científico ponta a ponta, file-first e anti-overclaim.

O pipeline recebe um tema, monta um contrato de recuperação inspirado na skill
MIT ``database-lookup`` (sem copiar código), executa a busca nativa quando
autorizado, deduplica registros, cria evidências literais em nível de resumo,
aplica o gate metacognitivo, audita o pacote e gera um manuscrito IMRaD para
validação humana. Nenhuma lacuna é preenchida com conteúdo inventado.
"""
from __future__ import annotations

import hashlib
import json
import re
import signal
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterable

from mci.metacognitive_gate import aggregate
from scientific_lab import fulltext, integrity, screening
from scientific_lab.native import evidence as native_evidence
from scientific_lab.native import research as native_research
from scientific_lab.native import review as native_review
from scientific_lab.native.common import dump, load, now, sha256_file, slug, uid

PIPELINE_VERSION = "R1051"
PIPELINE_REVISION = "R1052"
SCHEMA_VERSION = "1.0"

DEFAULT_SOURCES = (
    "openalex",
    "crossref",
    "europepmc",
    "arxiv",
    "semantic_scholar",
)

DATABASE_CATALOG: dict[str, dict[str, str]] = {
    "openalex": {
        "endpoint": "https://api.openalex.org/works",
        "access": "public",
        "role": "primary_bibliographic",
    },
    "crossref": {
        "endpoint": "https://api.crossref.org/works",
        "access": "public",
        "role": "metadata_crosscheck",
    },
    "europepmc": {
        "endpoint": "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        "access": "public",
        "role": "biomedical_literature",
    },
    "arxiv": {
        "endpoint": "https://export.arxiv.org/api/query",
        "access": "public",
        "role": "preprint",
    },
    "semantic_scholar": {
        "endpoint": "https://api.semanticscholar.org/graph/v1/paper/search",
        "access": "public_rate_limited",
        "role": "discovery",
    },
    "core": {
        "endpoint": "https://api.core.ac.uk/v3/search/works",
        "access": "optional_api_key",
        "role": "repository",
    },
    "scielo": {
        "endpoint": "https://api.crossref.org/members/530/works",
        "access": "public",
        "role": "regional_literature",
    },
    "pubmed": {
        "endpoint": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        "access": "public_rate_limited",
        "role": "biomedical_literature",
    },
    "biorxiv": {
        "endpoint": "https://api.crossref.org/works?filter=prefix:10.1101",
        "access": "public",
        "role": "preprint",
    },
}

STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da",
    "dos", "das", "em", "no", "na", "nos", "nas", "por", "para", "com",
    "sem", "sobre", "entre", "e", "ou", "que", "se", "não", "nao", "é",
    "eh", "são", "sao", "foi", "foram", "ser", "estar", "como", "mais",
    "menos", "muito", "pouco", "também", "tambem", "seu", "sua", "seus",
    "suas", "este", "esta", "esse", "essa", "aquele", "aquela", "isso",
    "isto", "aquilo", "the", "and", "for", "with", "from", "this", "that",
    "study", "studies", "results", "result", "analysis", "research",
    "tema", "temas", "estudo", "estudos", "resultado", "resultados",
    "dados", "pesquisa", "artigo", "trabalho", "forma", "partir", "pode",
    "podem", "onde", "quando", "qual", "quais", "descreve", "apresenta",
    "indica", "observa", "mostra", "revisão", "revisao", "narrativa",
    "experimento", "controlado", "associação", "associacao", "descritiva",
}

OVERCLAIM_PATTERNS = (
    r"\bprova(m)?\b",
    r"\bcomprova(m)?\b",
    r"\bdemonstra(m)?\s+causalidade\b",
    r"\bverdade\s+absoluta\b",
    r"\bqualis\s*a1\b",
    r"\baceito\b",
    r"\bpublicado\b",
    r"\bpronta?\s+para\s+publica",
    r"\bsubmetido\b",
    r"\baprovado\s+pelo\s+conselho\b",
    r"\b100\s*%\b",
    r"\bgarante\b",
    r"\bdefinitivo\b",
    r"\bcausalidade\b",
)

NEGATION = re.compile(
    r"(?i)(não|nao|sem|nunca|jamais|nenhum|nenhuma|isento|dispensa|"
    r"tampouco|exceto)\s+(?:\w+\s+){0,6}$"
)

PLACEHOLDER_MARKERS = (
    "[[",
    "]]",
    "TODO",
    "TBD",
    "XXX",
    "lorem ipsum",
    "{{",
    "}}",
    "PREENCHER",
    "INSERIR AQUI",
)

PROJECT_DIRS = (
    "00_contract",
    "01_sources",
    "02_screening",
    "03_evidence",
    "04_analysis",
    "05_audit",
    "06_manuscript",
    "07_validation",
    "07_artifacts",
    "08_manifest",
    "09_provenance",
)

CONTRACT_REQUIRED = (
    "schema_version", "contract_id", "theme", "question", "question_status",
    "intent", "target_entity", "accepted_identifiers", "databases", "filters",
    "expected_fields", "pagination", "budget", "provenance",
    "untrusted_data_policy", "missing_constraints", "clarification_required",
    "status",
)


# ---------------------------------------------------------------------------
# validação e contrato
# ---------------------------------------------------------------------------


def _text(value: Any, name: str, minimum: int = 1, maximum: int = 500) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} deve ser texto")
    value = " ".join(value.split())
    if not minimum <= len(value) <= maximum:
        raise ValueError(f"{name} deve ter entre {minimum} e {maximum} caracteres")
    return value


def _positive_int(value: Any, name: str, low: int = 1, high: int = 200) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f"{name} deve ser inteiro entre {low} e {high}")
    return value


def normalize_theme(theme: Any) -> str:
    return _text(theme, "theme", 3, 500)


def _strip_terminal(text: str) -> str:
    return text.rstrip("?.! ").strip()


def derive_question(theme: str) -> str:
    return (
        "Quais evidências disponíveis descrevem, explicam ou avaliam "
        f"{_strip_terminal(theme)}?"
    )


def normalize_sources(sources: Iterable[str] | str | None) -> list[str]:
    if sources is None:
        selected = list(DEFAULT_SOURCES)
    elif isinstance(sources, str):
        selected = [part.strip() for part in sources.split(",") if part.strip()]
    else:
        selected = [str(part).strip() for part in sources if str(part).strip()]
    if not selected:
        raise ValueError("selecione pelo menos uma fonte")
    ordered: list[str] = []
    for source in selected:
        if source not in native_research.ARTICLE_PLATFORMS:
            raise ValueError(f"fonte não permitida: {source}")
        if source not in ordered:
            ordered.append(source)
    return ordered


def normalize_budget(budget: dict | None, *, limit: int, per_platform: int,
                     timeout_seconds: int = 90, max_downloads: int = 0) -> dict:
    base = {
        "max_queries": 1,
        "max_records": _positive_int(limit, "limit", 1, 200),
        "per_platform": _positive_int(per_platform, "per_platform", 1, 50),
        "max_downloads": _positive_int(max_downloads, "max_downloads", 0, 20),
        "timeout_seconds": _positive_int(
            timeout_seconds, "timeout_seconds", 1, 600,
        ),
    }
    if budget is None:
        return base
    if not isinstance(budget, dict):
        raise ValueError("budget deve ser objeto")
    merged = {**base, **budget}
    merged["max_queries"] = _positive_int(merged["max_queries"], "max_queries", 1, 10)
    merged["max_records"] = _positive_int(merged["max_records"], "max_records", 1, 200)
    merged["per_platform"] = _positive_int(merged["per_platform"], "per_platform", 1, 50)
    merged["max_downloads"] = _positive_int(merged["max_downloads"], "max_downloads", 0, 0)
    timeout = merged["timeout_seconds"]
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) \
            or not 1 <= timeout <= 600:
        raise ValueError("timeout_seconds deve estar entre 1 e 600")
    merged["timeout_seconds"] = int(timeout)
    return merged


def _database_entries(sources: list[str], per_platform: int) -> list[dict]:
    entries = []
    for name in sources:
        catalog = DATABASE_CATALOG.get(name, {
            "endpoint": "não documentado",
            "access": "consultar provedor",
            "role": "discovery",
        })
        entries.append({
            "name": name,
            "endpoint": catalog["endpoint"],
            "access": catalog["access"],
            "role": catalog["role"],
            "rate_limit": (
                "consultar a documentação do provedor antes de uso em massa; "
                f"o pipeline limita {per_platform} registro(s) por plataforma"
            ),
            "auth_status_reported": False,
        })
    return entries


def build_retrieval_contract(
    theme: str,
    question: str,
    question_status: str,
    sources: list[str],
    budget: dict,
    *,
    constraints: dict | None = None,
) -> dict:
    theme = normalize_theme(theme)
    question = _text(question, "question", 5, 1000)
    if question_status not in {"explicit", "provisional_from_theme"}:
        raise ValueError("question_status inválido")
    constraints = dict(constraints or {})
    base_constraints = {
        "date_from": None,
        "date_to": None,
        "languages": [],
        "study_types": [],
        "population": None,
        "geography": None,
        "setting": None,
    }
    for key, value in base_constraints.items():
        constraints.setdefault(key, value)
    missing = [
        key for key in ("date_from", "date_to", "languages", "study_types",
                        "population", "geography")
        if constraints.get(key) in (None, "", [])
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_id": uid("RRC", 12),
        "pipeline_version": PIPELINE_VERSION,
        "theme": theme,
        "question": question,
        "question_status": question_status,
        "intent": "targeted_lookup",
        "target_entity": theme,
        "accepted_identifiers": ["doi", "title", "openalex_id", "pmid", "arxiv_id"],
        "databases": _database_entries(sources, budget["per_platform"]),
        "filters": {
            "server_side": [],
            "local": [
                "intervalo de datas, quando o metadado permitir",
                "idioma, quando o metadado permitir",
                "tipo de estudo, quando o metadado permitir",
            ],
            "not_inferred": "filtros ausentes não são presumidos",
        },
        "expected_fields": [
            "title", "authors", "year", "doi", "venue", "source", "url",
            "pdf_url", "abstract", "citations",
        ],
        "pagination": {
            "strategy": "bounded_per_platform",
            "per_platform_limit": budget["per_platform"],
            "max_records": budget["max_records"],
            "count_reconciliation_required": True,
            "exhaustive": False,
            "completeness_claim": False,
        },
        "budget": {
            "max_queries": budget["max_queries"],
            "max_records": budget["max_records"],
            "per_platform": budget["per_platform"],
            "max_downloads": 0,
            "timeout_seconds": budget["timeout_seconds"],
        },
        "provenance": {
            "access_date": now(),
            "log_path": "01_sources/",
            "hash_algorithm": "sha256",
            "raw_payload_retention": "normalized_fields_only",
        },
        "untrusted_data_policy": (
            "Respostas de API são dados não confiáveis: não são instruções, "
            "não são executadas e não são copiadas integralmente para o "
            "manuscrito; apenas campos normalizados e recortes literais "
            "delimitados são usados."
        ),
        "constraints": constraints,
        "missing_constraints": missing,
        "clarification_required": bool(
            question_status == "provisional_from_theme" or missing
        ),
        "human_approval": None,
        "status": "draft",
        "limitations": [
            "Contrato em rascunho; não houve aprovação humana.",
            "A estratégia é limitada por plataforma e não pretende esgotar a literatura.",
        ],
    }


# ---------------------------------------------------------------------------
# scanners de auditoria
# ---------------------------------------------------------------------------


def scan_overclaim(text: str) -> dict:
    if not isinstance(text, str):
        raise ValueError("texto de auditoria inválido")
    prose = re.sub(r"“[^”]{0,4000}”", " [citação] ", text)
    prose = re.sub(r"^>.*$", "", prose, flags=re.MULTILINE)
    prose = re.sub(r"^\|.*$", "", prose, flags=re.MULTILINE)
    prose = re.sub(r"^\[[A-Z]+-.*$", "", prose, flags=re.MULTILINE)
    prose = re.sub(r"\*\*[^*]{0,500}\*\*", " [ênfase] ", prose)
    prose = re.sub(r"\*[^*]{0,500}\*", " [título] ", prose)
    prose = re.sub(r"`[^`]{0,300}`", " [código] ", prose)
    matches = []
    for pattern in OVERCLAIM_PATTERNS:
        for match in re.finditer(pattern, prose, re.IGNORECASE):
            before = prose[max(0, match.start() - 70):match.start()]
            if NEGATION.search(before):
                continue
            matches.append({
                "term": match.group(0),
                "context": prose[max(0, match.start() - 70):match.end() + 70].strip(),
            })
    return {
        "status": "fail" if matches else "pass",
        "matches": matches,
        "scanned_chars": len(prose),
    }


def scan_placeholders(text: str) -> dict:
    if not isinstance(text, str):
        raise ValueError("texto de auditoria inválido")
    matches = []
    upper = text.upper()
    word_markers = {"TODO", "TBD", "XXX"}
    for marker in PLACEHOLDER_MARKERS:
        if marker in word_markers:
            for match in re.finditer(rf"\b{re.escape(marker)}\b", upper):
                matches.append({
                    "marker": marker,
                    "context": text[
                        max(0, match.start() - 40):match.end() + 40
                    ].strip(),
                })
            continue
        index = upper.find(marker.upper())
        if index >= 0:
            matches.append({
                "marker": marker,
                "context": text[max(0, index - 40):index + len(marker) + 40].strip(),
            })
    return {"status": "fail" if matches else "pass", "matches": matches}


# ---------------------------------------------------------------------------
# utilitários de conteúdo
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> list[str]:
    return [
        token for token in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{4,}", (text or "").lower())
        if token not in STOPWORDS
    ]


def _first_sentence(text: str, minimum: int = 40, maximum: int = 500) -> str:
    collapsed = " ".join((text or "").split())
    for part in re.split(r"(?<=[.!?])\s+", collapsed):
        if len(part) >= minimum:
            return part[:maximum]
    return collapsed[:maximum]


def _safe_error(exc: Exception) -> str:
    text = f"{type(exc).__name__}: {exc}"
    text = re.sub(
        r"(?i)(api[_-]?key|token|authorization|secret)\s*[=:]\s*\S+",
        r"\1=[redacted]",
        text,
    )
    return text[:300]


def _authors(record: dict) -> str:
    authors = [str(item) for item in (record.get("authors") or []) if str(item).strip()]
    if not authors:
        return "Autoria não informada"
    if len(authors) <= 3:
        return "; ".join(authors)
    return "; ".join(authors[:3]) + "; et al."


def _reference(record: dict) -> str:
    article_id = record.get("article_id") or "ART-?"
    authors = _authors(record)
    year = record.get("year") or "ano não informado"
    title = record.get("title") or "Título não informado"
    venue = record.get("venue") or "Veículo não informado"
    doi = record.get("doi") or "DOI não informado"
    url = record.get("url") or record.get("record_url") or "URL não informada"
    abstract = "sim" if (record.get("abstract") or "").strip() else "não"
    source = record.get("source") or "fonte não informada"
    return (
        f"[{article_id}] {authors} ({year}). **{title}**. {venue}. "
        f"DOI: {doi}. URL: {url}. "
        f"[Fonte: {source}; resumo indexado: {abstract}; acesso: "
        f"{record.get('retrieved_at') or 'não informado'}.]"
    )


def _corpus_reference(source: dict) -> str:
    return (
        f"[{source['id']}] {source.get('provenance') or 'proveniência não informada'}. "
        f"Texto fornecido pelo operador; SHA-256: `{source.get('text_sha256')}`."
    )


def _unique_records(ctx: dict) -> list[dict]:
    records = ctx["search"].get("records", [])
    studies = ctx["screening"].get("studies", [])
    if not studies:
        return records
    by_article = {item["article_id"]: item for item in records}
    unique = []
    seen = set()
    for study in studies:
        article_id = (study.get("source_records") or [None])[0]
        if article_id in by_article and article_id not in seen:
            unique.append(by_article[article_id])
            seen.add(article_id)
    return unique or records


# ---------------------------------------------------------------------------
# etapas
# ---------------------------------------------------------------------------


def _prepare_output(out: Path) -> None:
    if out.exists():
        manifest = out / "08_manifest/project-manifest.json"
        if manifest.exists():
            raise ValueError(
                "o diretório já contém um projeto; escolha outro --out para não "
                "misturar artefatos"
            )
        for name in PROJECT_DIRS:
            if (out / name).exists() and any((out / name).iterdir()):
                raise ValueError(
                    f"o diretório já contém {name}; escolha um --out vazio"
                )
    out.mkdir(parents=True, exist_ok=True)


def _write_intake(out: Path, data: dict) -> Path:
    path = out / "00_contract/intake.json"
    dump(path, data)
    return path


def _write_contract(out: Path, contract: dict) -> Path:
    path = out / "00_contract/retrieval-contract.json"
    dump(path, contract)
    return path


def _write_protocol(out: Path, project_id: str, theme: str, question: str,
                    sources: list[str]) -> tuple[Path, dict]:
    path = native_review.init_protocol(
        out,
        project_id,
        title=f"Evidências disponíveis sobre {_strip_terminal(theme)}",
        question=question,
        sources=sources,
        human=False,
    )
    return path, load(path)


def _write_search_plan(out: Path, query: str, sources: list[str],
                       budget: dict) -> Path:
    path = out / "01_sources/search-plan.json"
    dump(path, {
        "schema_version": SCHEMA_VERSION,
        "plan_id": uid("SPLAN", 12),
        "query": query,
        "sources": sources,
        "execution": "not_executed",
        "reason": "dry_run",
        "estimated_calls": len(sources),
        "per_platform_limit": budget["per_platform"],
        "max_records": budget["max_records"],
        "budget": budget,
        "count_reconciliation_required": True,
        "provenance": {"created_at": now(), "hash_algorithm": "sha256"},
        "limitations": [
            "Plano apenas; nenhuma chamada de rede foi feita.",
            "A busca real depende de disponibilidade e limites dos provedores.",
        ],
    })
    return path


def _normalize_records(records: list, manifest: dict) -> list[dict]:
    items = manifest.get("results", [])
    normalized = []
    for record, item in zip(records, items):
        abstract = " ".join((getattr(record, "abstract", "") or "").split())
        entry = dict(item)
        entry["abstract"] = abstract
        entry["abstract_sha256"] = (
            hashlib.sha256(abstract.encode("utf-8")).hexdigest() if abstract else None
        )
        entry["abstract_chars"] = len(abstract)
        entry["retrieved_at"] = manifest.get("created_at")
        entry["search_id"] = manifest.get("search_id")
        entry["query"] = manifest.get("query")
        entry["untrusted"] = True
        normalized.append(entry)
    return normalized


def _write_source_records(out: Path, normalized: list[dict], manifest: dict) -> Path:
    path = out / "01_sources/source-records.json"
    dump(path, {
        "schema_version": SCHEMA_VERSION,
        "search_id": manifest.get("search_id"),
        "query": manifest.get("query"),
        "created_at": manifest.get("created_at"),
        "records": normalized,
        "counts": {
            "retrieved": len(normalized),
            "with_abstract": sum(bool(item.get("abstract")) for item in normalized),
            "with_doi": sum(bool(item.get("doi")) for item in normalized),
            "oa_candidates": sum(bool(item.get("oa")) for item in normalized),
        },
        "policy": "normalized_fields_only",
        "untrusted_data": True,
        "limitations": [
            "Registros são candidatos; metadados podem estar incompletos ou desatualizados.",
            "Resumos indexados não substituem o texto integral.",
        ],
    })
    return path


class _SearchDeadlineExceeded(BaseException):
    """BaseException para não ser engolido pelo ``except Exception`` dos buscadores."""


@contextmanager
def _hard_deadline(seconds: int):
    """Limite de parede para a busca, quando SIGALRM está disponível.

    Os buscadores nativos capturam ``Exception`` e retornariam lista vazia;
    por isso o estouro usa ``BaseException``. Em plataformas sem SIGALRM, o
    limite não é aplicado e a limitação fica registrada no contrato.
    """
    if not hasattr(signal, "SIGALRM") or seconds <= 0:
        yield
        return
    previous = signal.getsignal(signal.SIGALRM)

    def _handler(signum, frame):
        raise _SearchDeadlineExceeded(
            f"busca excedeu o orçamento de {seconds}s"
        )

    signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def _execute_search(out: Path, query: str, sources: list[str], budget: dict,
                    searcher_factory: Callable | None) -> dict:
    manifest_path, records, manifest = native_research.search(
        query,
        out,
        limit=budget["max_records"],
        per_platform=budget["per_platform"],
        platforms=sources,
        searcher_factory=searcher_factory,
    )
    normalized = _normalize_records(records, manifest)
    source_records_path = _write_source_records(out, normalized, manifest)
    return {
        "status": "completed" if normalized else "completed_empty",
        "manifest_path": manifest_path,
        "manifest": manifest,
        "records": normalized,
        "source_records_path": source_records_path,
        "error": None,
    }


def _write_search_error(out: Path, exc: Exception, query: str,
                        sources: list[str]) -> dict:
    error = {
        "schema_version": SCHEMA_VERSION,
        "error_id": uid("SERR", 12),
        "query": query,
        "sources": sources,
        "error_type": type(exc).__name__,
        "message": _safe_error(exc),
        "created_at": now(),
        "execution_attempted": True,
        "records_fabricated": False,
        "limitations": [
            "A busca falhou; nenhum registro foi inventado ou inferido.",
            "A ausência de resultados não prova ausência de literatura.",
        ],
    }
    dump(out / "01_sources/search-error.json", error)
    return error


def _screening_payload(out: Path, project_id: str, protocol_id: str,
                       theme: str, question: str, records: list[dict],
                       studies: list[dict]) -> dict:
    by_article = {item["article_id"]: item for item in records}
    theme_terms = set(_tokenize(theme + " " + question))
    triage_studies = []
    for study in studies:
        article_id = (study.get("source_records") or [None])[0]
        record = by_article.get(article_id, {})
        text = f"{study.get('canonical_title', '')} {record.get('abstract', '')}"
        matched = sorted(theme_terms & set(_tokenize(text)))
        score = round(len(matched) / max(1, len(theme_terms)), 3)
        triage_studies.append({
            "study_id": study["study_id"],
            "article_id": article_id,
            "title": study.get("canonical_title"),
            "year": study.get("year"),
            "source": record.get("source"),
            "doi": (study.get("identifiers") or {}).get("doi"),
            "has_abstract": bool(record.get("abstract")),
            "matched_terms": matched,
            "lexical_score": score,
            "decision": (
                "candidate_for_human_screening" if score > 0
                else "uncertain_for_human_screening"
            ),
            "screening_status": study.get("screening_status", "pending"),
            "included_in_synthesis": bool(study.get("included_in_synthesis")),
            "human_review_required": True,
            "reasons": [
                "correspondência lexical exploratória; não é decisão de inclusão",
                "triagem final exige dois revisores humanos",
            ],
        })
    triage = {
        "schema_version": SCHEMA_VERSION,
        "triage_id": uid("TRIAGE", 12),
        "protocol_id": protocol_id,
        "project_id": project_id,
        "generated_at": now(),
        "studies": triage_studies,
        "summary": {
            "total": len(triage_studies),
            "candidate": sum(
                item["decision"] == "candidate_for_human_screening"
                for item in triage_studies
            ),
            "uncertain": sum(
                item["decision"] == "uncertain_for_human_screening"
                for item in triage_studies
            ),
            "human_included": 0,
        },
        "decision_scope": "assisted_candidate_only",
        "human_review_required": True,
        "limitations": [
            "A pontuação lexical é exploratória e não substitui leitura de título/resumo.",
            "Nenhuma decisão de inclusão ou exclusão foi tomada pelo pipeline.",
        ],
    }
    summary = screening.summarize(studies, screening.load_decisions(out))
    triage = screening.merge_into_triage(triage, summary)
    triage["summary"]["human_included"] = summary["summary"]["included"]
    triage["summary"]["human_pending"] = summary["summary"]["pending"]
    triage["human_verified"] = summary["human_verified"]
    dump(out / "02_screening/triage.json", triage)
    screening.write_summary(out, summary)
    prisma_path = native_review.prisma(
        out, protocol_id, human_verified=summary["human_verified"],
    )
    dump(out / "02_screening/prisma-audit.json", {
        "schema_version": SCHEMA_VERSION,
        "prisma_path": str(prisma_path),
        "screening_summary": summary["summary"],
        "screening_status": summary["status"],
        "human_verified": summary["human_verified"],
        "reviewers": summary["reviewers"],
        "pending": summary["summary"]["pending"],
        "conflicts": summary["summary"]["conflicts"],
        "policy": "pending_is_not_included",
        "truth_claim": False,
        "human_review_required": True,
    })
    return {
        "studies": studies,
        "triage": triage,
        "summary": summary,
        "prisma_path": prisma_path,
    }


def _screen(out: Path, manifest_path: Path, project_id: str, protocol_id: str,
            theme: str, question: str, records: list[dict]) -> dict:
    ingest = native_review.ingest(out, manifest_path)
    studies = [load(path) for path in
               sorted((out / "01_sources/systematic_review/studies").glob("*.json"))]
    payload = _screening_payload(
        out, project_id, protocol_id, theme, question, records, studies,
    )
    payload["ingest"] = ingest
    return payload


def _load_corpus(path: Path) -> dict:
    if not path.exists():
        raise ValueError(f"corpus não encontrado: {path}")
    if path.stat().st_size > 2_000_000:
        raise ValueError("corpus excede 2 MB")
    try:
        corpus = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"corpus ilegível: {type(exc).__name__}") from exc
    if not isinstance(corpus, dict) or set(corpus) != {"sources", "claims"}:
        raise ValueError("corpus deve conter apenas sources e claims")
    sources = corpus["sources"]
    claims = corpus["claims"]
    if not isinstance(sources, list) or not 1 <= len(sources) <= 10:
        raise ValueError("corpus deve ter entre uma e dez fontes")
    if not isinstance(claims, list) or not 1 <= len(claims) <= 20:
        raise ValueError("corpus deve ter entre um e vinte claims")
    from scientific_lab.council import validate_claims
    council = validate_claims(claims, sources)
    return {
        "sources": sources,
        "claims": claims,
        "council": council,
    }


def _corpus_to_gate(corpus: dict) -> tuple[list[dict], list[dict]]:
    original = {item["id"]: item for item in corpus["claims"]}
    gate_claims = []
    for checked in corpus["council"]["claims"]:
        source = original[checked["id"]]
        gate_claims.append({
            "id": checked["id"],
            "text": checked["text"],
            "confidence": checked["confidence"],
            "evidence": [
                {**item, "literal_verified": True}
                for item in checked["evidence"]
            ],
            "inference_level": checked["inference_level"],
            "falsifier": source["falsifier"],
            "contradictions": list(source["contradictions"]),
            "mechanism": source["mechanism"],
        })
    source_index = []
    for source in corpus["sources"]:
        text = source["text"]
        source_index.append({
            "id": source["id"],
            "provenance": source["provenance"],
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "chars": len(text),
            "role": "supplied_literal_evidence_only",
        })
    return gate_claims, source_index


def _collect_evidence(out: Path, project_id: str, studies: list[dict],
                      records: list[dict], corpus: dict | None,
                      *, base_claims: list[dict] | None = None,
                      base_cards: list[dict] | None = None,
                      base_gaps: list[dict] | None = None,
                      extra_claims: list[dict] | None = None) -> dict:
    by_article = {item["article_id"]: item for item in records}
    metadata_claims = [] if base_claims is None else []
    cards = list(base_cards or [])
    gaps = list(base_gaps or [])
    gap_keys = {
        (gap.get("study_id"), gap.get("reason"))
        for gap in gaps
    }
    for study in studies:
        if study.get("integrity_status") in {"retracted", "retracted_notice"}:
            key = (study.get("study_id"), "retracted_study")
            if key not in gap_keys:
                gaps.append({
                    "study_id": study.get("study_id"),
                    "article_id": (study.get("source_records") or [None])[0],
                    "reason": "retracted_study",
                    "detail": "Estudo retratado; excluído da síntese e dos claims.",
                })
                gap_keys.add(key)
    iter_studies = studies if base_claims is None else []
    for study in iter_studies:
        article_id = (study.get("source_records") or [None])[0]
        if study.get("integrity_status") in {"retracted", "retracted_notice"}:
            continue
        record = by_article.get(article_id)
        if record is None:
            gaps.append({
                "study_id": study.get("study_id"),
                "article_id": article_id,
                "reason": "record_missing",
                "detail": "Registro de origem não encontrado no manifesto normalizado.",
            })
            continue
        abstract = record.get("abstract") or ""
        if len(abstract) < 80:
            gaps.append({
                "study_id": study.get("study_id"),
                "article_id": article_id,
                "reason": "abstract_missing_or_short",
                "detail": "Sem resumo indexado suficiente para uma citação literal.",
            })
            continue
        quote = _first_sentence(abstract)
        if not quote or quote not in abstract:
            gaps.append({
                "study_id": study.get("study_id"),
                "article_id": article_id,
                "reason": "quote_not_literal",
                "detail": "Não foi possível extrair um recorte literal do resumo.",
            })
            continue
        claim_id = f"CLAIM-{article_id}"
        claim_text = (
            f"O resumo indexado de {record.get('title')} "
            f"({record.get('year') or 'ano não informado'}) contém: “{quote}”"
        )
        claim = {
            "id": claim_id,
            "text": claim_text,
            "confidence": 0.6,
            "evidence": [{
                "source_id": article_id,
                "quote": quote,
                "source_sha256": hashlib.sha256(abstract.encode("utf-8")).hexdigest(),
                "literal_verified": True,
            }],
            "inference_level": "observation",
            "falsifier": (
                "Se o texto integral ou uma versão revisada do registro não "
                "contiver o trecho citado."
            ),
            "contradictions": [],
            "mechanism": (
                "Trecho extraído literalmente do campo abstract do registro "
                "recuperado; não houve leitura do texto integral."
            ),
        }
        metadata_claims.append(claim)
        native_evidence.annotate(
            out,
            project_id,
            claim_id,
            study["study_id"],
            "supports",
            f"abstract:{article_id}",
            quote,
            "R1051-pipeline",
            claim_text=claim_text,
            status="candidate",
            verbatim=True,
        )
        cards.append({
            "claim_id": claim_id,
            "study_id": study["study_id"],
            "article_id": article_id,
            "title": record.get("title"),
            "year": record.get("year"),
            "source": record.get("source"),
            "doi": record.get("doi"),
            "quote": quote,
            "source_sha256": claim["evidence"][0]["source_sha256"],
            "locator": f"abstract:{article_id}",
            "scope": "indexed_abstract_only",
            "verification_status": "candidate",
            "integrity_status": study.get("integrity_status", "unchecked"),
            "full_text_read": False,
            "human_review_required": True,
        })

    corpus_gate_claims: list[dict] = []
    corpus_index: list[dict] = []
    council = None
    if base_claims is None and corpus is not None:
        corpus_gate_claims, corpus_index = _corpus_to_gate(corpus)
        council = corpus["council"]
        dump(out / "03_evidence/council-claims.json", council)
        dump(out / "03_evidence/corpus-sources.json", {
            "schema_version": SCHEMA_VERSION,
            "sources": corpus_index,
            "full_text_retained": False,
            "policy": "hashes_and_quotes_only",
            "truth_claim": False,
            "human_review_required": True,
        })

    if base_claims is None:
        claims = metadata_claims + corpus_gate_claims
    else:
        claims = list(base_claims)
    extra_claims = list(extra_claims or [])
    merged = {item["id"]: item for item in claims}
    for item in extra_claims:
        merged[item["id"]] = item
    claims = list(merged.values())
    ids = [item["id"] for item in claims]
    if len(ids) != len(set(ids)):
        raise ValueError("identificadores de claim duplicados")
    if len(claims) > 50:
        raise ValueError("o gate aceita no máximo 50 claims por execução")
    dump(out / "03_evidence/claims.json", {
        "schema_version": SCHEMA_VERSION,
        "claims": claims,
        "counts": {
            "metadata_claims": len(metadata_claims),
            "corpus_claims": len(corpus_gate_claims),
            "fulltext_claims": len(extra_claims),
            "total": len(claims),
        },
        "policy": "literal_evidence_only",
        "truth_claim": False,
        "human_review_required": True,
    })
    if claims:
        gate = aggregate(claims)
    else:
        gate = {
            "status": "blocked",
            "truth_claim": False,
            "claims": [],
            "counts": {},
            "policy": "vote_score_payoff_never_truth",
            "confidence_promoted": False,
            "human_review_required": True,
            "reason": "no_literal_evidence",
            "limitation": (
                "Nenhum claim com evidência literal foi produzido; "
                "não há base para conclusão."
            ),
        }
    dump(out / "03_evidence/claim-gate.json", gate)
    dump(out / "03_evidence/evidence-cards.json", {
        "schema_version": SCHEMA_VERSION,
        "cards": cards,
        "count": len(cards),
        "scope": "metadata_and_indexed_abstracts_only",
        "full_text_read": False,
        "human_review_required": True,
    })
    dump(out / "03_evidence/gaps.json", {
        "schema_version": SCHEMA_VERSION,
        "gaps": gaps,
        "count": len(gaps),
        "policy": "gap_is_reported_not_filled",
        "human_review_required": True,
    })
    native_evidence.build(out, project_id)
    return {
        "claims": claims,
        "gate": gate,
        "cards": cards,
        "gaps": gaps,
        "corpus_gate_claims": corpus_gate_claims,
        "corpus_index": corpus_index,
        "council": council,
        "metadata_claims": metadata_claims,
        "fulltext_claims": [
            claim for claim in claims if "-FT-" in claim.get("id", "")
        ],
    }


def _run_downloads(out: Path, records: list[dict], *, enabled: bool,
                   max_downloads: int, downloader_factory: Callable | None) -> dict:
    if not enabled:
        result = {
            "schema_version": SCHEMA_VERSION,
            "status": "not_requested",
            "downloaded": 0,
            "receipts": [],
            "paths": [],
            "limitations": ["Download de PDF não solicitado."],
        }
        dump(out / "01_sources/downloads.json", result)
        return result
    if not records:
        result = {
            "schema_version": SCHEMA_VERSION,
            "status": "not_applicable",
            "downloaded": 0,
            "receipts": [],
            "paths": [],
            "limitations": ["Sem registros para download."],
        }
        dump(out / "01_sources/downloads.json", result)
        return result
    from research.downloader import PaperDownloader
    from research.searchers import PaperRecord

    objects = [
        PaperRecord(
            title=record.get("title") or "",
            authors=record.get("authors") or [],
            year=record.get("year"),
            doi=record.get("doi"),
            arxiv_id=record.get("arxiv_id"),
            url=record.get("record_url") or record.get("url"),
            pdf_url=record.get("pdf_url"),
            abstract=record.get("abstract") or "",
            venue=record.get("venue") or "",
            source=record.get("source") or "",
            citations=record.get("cited_by_count"),
            extra={},
        )
        for record in records[:max_downloads]
    ]
    try:
        downloader = (
            downloader_factory(str(out / "01_sources/pdfs"))
            if downloader_factory is not None
            else PaperDownloader(str(out / "01_sources/pdfs"))
        )
        results = downloader.download(objects)
    except Exception as exc:
        result = {
            "schema_version": SCHEMA_VERSION,
            "status": "blocked",
            "downloaded": 0,
            "receipts": [],
            "paths": [],
            "error_type": type(exc).__name__,
            "error": _safe_error(exc),
            "limitations": ["O download falhou; nenhum PDF foi inventado."],
        }
        dump(out / "01_sources/downloads.json", result)
        return result
    receipts = []
    for record, download in zip(records, results):
        extra = dict(getattr(download, "extra", {}) or {})
        ok = bool(getattr(download, "ok", False))
        receipts.append({
            "article_id": record.get("article_id"),
            "title": record.get("title"),
            "doi": record.get("doi"),
            "ok": ok,
            "path": getattr(download, "pdf_path", None),
            "sha256": extra.get("sha256"),
            "rights_basis": extra.get("rights_basis", "not_verified_open"),
            "license": extra.get("license"),
            "content_type": extra.get("content_type"),
            "error": getattr(download, "error", None),
            "status": (
                "downloaded" if ok
                else "not_open" if extra.get("rights_basis") == "not_verified_open"
                else "failed"
            ),
            "limitations": list(extra.get("limitations", [])),
        })
    result = {
        "schema_version": SCHEMA_VERSION,
        "status": "completed",
        "requested": len(objects),
        "downloaded": sum(item["ok"] for item in receipts),
        "receipts": receipts,
        "paths": [item["path"] for item in receipts if item["ok"] and item["path"]],
        "policy": "open_science_only_no_paywall_bypass",
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "Somente rotas abertas verificáveis são aceitas; o downloader não contorna paywall.",
            "Um download bem-sucedido não prova licença, versão publicada ou qualidade.",
        ],
    }
    dump(out / "01_sources/downloads.json", result)
    return result


def _merge_fulltext_indices(indices: list[dict]) -> dict:
    entries_by_key: dict[str, dict] = {}
    for index in indices:
        for entry in index["entries"]:
            key = entry.get("sha256") or entry.get("path")
            entries_by_key[key] = entry
    entries = list(entries_by_key.values())
    return {
        "schema_version": SCHEMA_VERSION,
        "root": "; ".join(index["root"] for index in indices),
        "entries": entries,
        "count": len(entries),
        "with_text": sum(entry["text_chars"] >= 200 for entry in entries),
        "limitations": [
            limitation
            for index in indices
            for limitation in index.get("limitations", [])
        ],
    }


def _run_integrity(out: Path, studies: list[dict], *, enabled: bool,
                   checker: Callable | None, max_checks: int) -> dict:
    if not enabled:
        result = {
            "schema_version": SCHEMA_VERSION,
            "mode": "not_requested",
            "checks": [],
            "summary": {"not_requested": len(studies)},
            "checked": 0,
            "policy": "absence_of_update_is_not_proof_of_integrity",
            "truth_claim": False,
            "external_validation": False,
            "human_review_required": True,
            "limitations": ["Verificação de integridade não solicitada."],
        }
        integrity.write_checks(out, result)
        return result
    if not studies:
        result = {
            "schema_version": SCHEMA_VERSION,
            "mode": "not_applicable",
            "checks": [],
            "summary": {"not_applicable": 0},
            "checked": 0,
            "policy": "absence_of_update_is_not_proof_of_integrity",
            "truth_claim": False,
            "external_validation": False,
            "human_review_required": True,
            "limitations": ["Sem estudos para verificar."],
        }
        integrity.write_checks(out, result)
        return result
    result = integrity.check_many(
        studies, checker=checker, max_checks=max_checks,
    )
    result["mode"] = "executed"
    integrity.write_checks(out, result)
    integrity.apply_to_studies(out, result)
    return result


def _run_fulltext(out: Path, project_id: str, studies: list[dict],
                  records: list[dict], *, directories: list[Path] | None,
                  approval_path: str | Path | None,
                  theme: str, question: str) -> dict:
    if approval_path is not None and not directories:
        raise ValueError("--fulltext-approval exige --fulltext-dir")
    if not directories:
        result = {
            "status": "not_requested",
            "index": None,
            "matches": None,
            "candidates": {"candidates": [], "count": 0},
            "approval": None,
            "claims": [],
        }
        dump(out / "03_evidence/fulltext-summary.json", {
            "schema_version": SCHEMA_VERSION,
            "status": "not_requested",
            "files_indexed": 0,
            "candidates": 0,
            "approved": 0,
            "full_text_retained": False,
            "truth_claim": False,
            "external_validation": False,
            "human_review_required": True,
            "limitations": ["Nenhum diretório de texto integral foi fornecido."],
        })
        return result
    indices = []
    limitations = []
    for directory in directories:
        try:
            indices.append(fulltext.index_fulltexts(directory))
        except ValueError as exc:
            limitations.append(f"{directory}: {exc}")
    if not indices:
        raise ValueError(
            "nenhum diretório de texto integral produziu índice: "
            + "; ".join(limitations)
        )
    index = _merge_fulltext_indices(indices)
    index["limitations"] = list(index.get("limitations", [])) + limitations
    fulltext.write_index(out, index)
    matches = fulltext.match_entries(index, studies, records)
    candidates = fulltext.extract_candidates(
        index, matches, studies, records,
        max_excerpts=5,
        keywords=_tokenize(theme + " " + question),
    )
    fulltext.write_candidates(out, candidates)
    template = fulltext.approval_template(project_id, candidates["candidates"])
    fulltext.write_approval_template(out, template)
    approval_result = None
    claims: list[dict] = []
    if approval_path is not None:
        approval = fulltext.validate_approval(
            approval_path,
            [candidate["claim_id"] for candidate in candidates["candidates"]],
        )
        dump(out / "07_validation/fulltext-approval.json", {
            **approval,
            "source_path": str(approval_path),
            "applied_at": now(),
        })
        approval_result = fulltext.apply_approval(
            out, project_id, index, candidates["candidates"], approval, studies,
        )
        claims = fulltext.fulltext_claims(
            candidates["candidates"], approval["approved_claim_ids"], studies,
        )
    fulltext.write_fulltext_summary(
        out, index, matches, candidates, approval_result,
    )
    return {
        "status": "completed",
        "index": index,
        "matches": matches,
        "candidates": candidates,
        "approval": approval_result,
        "claims": claims,
    }


def _descriptive_analysis(out: Path, project_id: str, records: list[dict],
                          studies: list[dict], evidence: dict) -> dict:
    with_abstract = [item for item in records if item.get("abstract")]
    terms = Counter()
    for item in with_abstract:
        terms.update(_tokenize(item.get("abstract", "")))
    years = Counter(str(item.get("year") or "não informado") for item in records)
    sources = Counter(item.get("source") or "não informado" for item in records)
    venues = Counter(item.get("venue") or "não informado" for item in records)
    claims = evidence["claims"]
    gate = evidence["gate"]
    status_counts = Counter(item.get("status", "blocked") for item in gate.get("claims", []))
    analysis = {
        "schema_version": SCHEMA_VERSION,
        "analysis_id": uid("ANALYSIS", 12),
        "project_id": project_id,
        "generated_at": now(),
        "status": "completed_descriptive" if records or claims else "not_applicable",
        "records": len(records),
        "unique_studies": len(studies),
        "with_abstract": len(with_abstract),
        "with_doi": sum(bool(item.get("doi")) for item in records),
        "oa_candidates": sum(bool(item.get("oa")) for item in records),
        "year_counts": dict(sorted(years.items())),
        "source_counts": dict(sources),
        "top_venues": [
            {"venue": name, "count": count}
            for name, count in venues.most_common(5) if name != "não informado"
        ],
        "top_terms": [
            {"term": term, "count": count}
            for term, count in terms.most_common(12)
        ],
        "claims": {
            "total": len(claims),
            "metadata": len(evidence["metadata_claims"]),
            "corpus": len(evidence["corpus_gate_claims"]),
            "status_counts": dict(status_counts),
        },
        "inference_scope": "metadata_and_indexed_abstracts_only",
        "statistical_testing": "not_performed",
        "causal_claim": False,
        "meta_analysis": "not_performed",
        "truth_claim": False,
        "human_review_required": True,
        "limitations": [
            "Contagens descritivas de metadados não medem qualidade ou efeito.",
            "Termos frequentes são padrão lexical exploratório, não síntese temática validada.",
            "Nenhum teste estatístico, meta-análise ou inferência causal foi executado.",
        ],
    }
    dump(out / "04_analysis/descriptive.json", analysis)
    return analysis


def _empty_triage(out: Path, project_id: str, protocol_id: str, reason: str) -> dict:
    triage = {
        "schema_version": SCHEMA_VERSION,
        "triage_id": uid("TRIAGE", 12),
        "protocol_id": protocol_id,
        "project_id": project_id,
        "generated_at": now(),
        "studies": [],
        "summary": {"total": 0, "candidate": 0, "uncertain": 0, "human_included": 0},
        "decision_scope": "assisted_candidate_only",
        "human_review_required": True,
        "reason": reason,
        "limitations": [
            "Nenhum estudo foi triado nesta execução.",
            "A ausência de registros não prova ausência de literatura.",
        ],
    }
    dump(out / "02_screening/triage.json", triage)
    return triage


def _render_manuscript(ctx: dict) -> str:
    contract = ctx["contract"]
    protocol = ctx["protocol"]
    search = ctx["search"]
    screening = ctx["screening"]
    evidence = ctx["evidence"]
    analysis = ctx["analysis"]
    records = search.get("records", [])
    studies = screening.get("studies", [])
    triage = screening.get("triage", {})
    claims = evidence.get("claims", [])
    gate = evidence.get("gate", {})
    cards = evidence.get("cards", [])
    gaps = evidence.get("gaps", [])
    corpus_index = evidence.get("corpus_index", [])
    council = evidence.get("council")
    downloads = ctx.get("downloads") or {}
    download_count = downloads.get("downloaded", 0)
    fulltext = ctx.get("fulltext") or {}
    integrity = ctx.get("integrity") or {}
    fulltext_claims = evidence.get("fulltext_claims") or []
    fulltext_candidates = (fulltext.get("candidates") or {}).get("candidates", [])
    integrity_checks = integrity.get("checks") or []
    theme = contract["theme"]
    question = contract["question"]
    question_status = contract["question_status"]
    records_count = len(records)
    unique_count = len(studies)
    with_abstract = sum(bool(item.get("abstract")) for item in records)
    claim_count = len(claims)
    fulltext_claim_count = sum("-FT-" in claim.get("id", "") for claim in claims)
    metadata_claim_count = sum(
        claim.get("id", "").startswith("CLAIM-ART-")
        and "-FT-" not in claim.get("id", "")
        for claim in claims
    )
    corpus_claim_count = max(
        0, claim_count - fulltext_claim_count - metadata_claim_count,
    )

    lines: list[str] = []
    lines.append(
        f"# Evidências disponíveis sobre {_strip_terminal(theme)}: "
        "protocolo, recuperação e mapa de evidências"
    )
    lines.append("")
    lines.append(
        f"**Projeto:** `{ctx['project_id']}` · **Protocolo:** "
        f"`{protocol.get('protocol_id')}` · **Pipeline:** R1051/R1052 · "
        f"**Gerado em:** {ctx['generated_at']}"
    )
    lines.append("")
    if fulltext_claims:
        scope = (
            "Houve leitura de arquivos de texto integral fornecidos e aprovação "
            "humana explícita para os recortes marcados como `verified`; não "
            "houve validação externa."
        )
    else:
        scope = (
            "Não houve leitura do texto integral, triagem humana independente "
            "ou validação externa."
        )
    lines.append(
        "> **Status:** rascunho para validação humana. Não é artigo aceito, "
        "publicado ou avaliado por pares. As afirmações se limitam aos registros, "
        f"resumos indexados e recortes aprovados. {scope}"
    )
    lines.append("")
    lines.append("## Resumo")
    lines.append("")
    lines.append(
        f"**Objetivo.** Organizar a recuperação e o mapeamento de evidências "
        f"sobre {_strip_terminal(theme)}, com pergunta de pesquisa explícita ou "
        "provisória e trilha auditável de proveniência."
    )
    lines.append("")
    if search.get("status") == "blocked":
        methods_result = (
            "A execução da busca foi tentada e falhou antes de produzir "
            "registros. O erro foi registrado e nenhum resultado foi inventado."
        )
    elif search.get("status") == "planned":
        methods_result = (
            "O protocolo e o contrato de recuperação foram gerados, mas a busca "
            "não foi executada neste modo. O pacote contém apenas o plano e o "
            "rascunho metodológico."
        )
    else:
        methods_result = (
            f"A busca recuperou {records_count} registro(s); após deduplicação, "
            f"restaram {unique_count} estudo(s) único(s). "
            f"{with_abstract} registro(s) apresentaram resumo indexado. "
            f"{claim_count} claim(s) com evidência literal passaram pelo gate."
        )
    lines.append(f"**Métodos.** {methods_result}")
    lines.append("")
    if claim_count or corpus_claim_count or fulltext_claims:
        lines.append(
            f"**Resultados.** Foram produzidos {metadata_claim_count} claim(s) a "
            f"partir de resumos indexados, {corpus_claim_count} claim(s) a partir "
            f"de corpus fornecido e {len(fulltext_claims)} claim(s) a partir de "
            "texto integral aprovado por humano. O gate metacognitivo não "
            "promoveu nenhum claim a verdade e não houve validação externa."
        )
        if integrity_checks:
            lines.append("")
            lines.append(
                "**Integridade.** Foram consultados "
                f"{len(integrity_checks)} estudo(s) no Crossref; o resultado é "
                "observacional e não certifica integridade."
            )
    else:
        lines.append(
            "**Resultados.** Nenhum claim com evidência literal foi produzido. "
            "O relatório registra a lacuna em vez de preenchê-la."
        )
    lines.append("")
    lines.append(
        "**Conclusão.** O pacote entrega um protocolo reproduzível, contagens de "
        "recuperação, mapa de evidências e um rascunho para validação. A pergunta "
        "permanece aberta até que a triagem humana, a leitura do texto integral e "
        "a validação externa sejam concluídas."
    )
    lines.append("")
    keywords = [item["term"] for item in analysis.get("top_terms", [])[:5]]
    if not keywords:
        keywords = ["protocolo", "evidência", "recuperação", "validação"]
    lines.append("**Palavras-chave:** " + "; ".join(keywords) + ".")
    lines.append("")
    lines.append("## 1. Introdução")
    lines.append("")
    lines.append(
        f"Este documento descreve a preparação de uma pesquisa sobre "
        f"{_strip_terminal(theme)}. A pergunta registrada é: **{question}**"
    )
    lines.append("")
    if question_status == "provisional_from_theme":
        lines.append(
            "A pergunta é **provisória**, derivada do tema porque não foi "
            "fornecida uma pergunta explícita. Ela precisa ser confirmada por "
            "um pesquisador antes de orientar a triagem e a extração."
        )
        lines.append("")
    if fulltext_claims:
        analysis_unit = (
            "A unidade de análise inclui o registro bibliográfico, o resumo "
            "indexado e os recortes de texto integral aprovados por humano; "
            "os demais recortes permanecem candidatos."
        )
    else:
        analysis_unit = (
            "A unidade de análise é o registro bibliográfico e o resumo "
            "indexado, não o texto integral."
        )
    lines.append(
        "O objetivo não é responder à pergunta com dados primários, mas "
        "verificar o que os registros recuperados permitem afirmar com "
        f"proveniência. {analysis_unit}"
    )
    lines.append("")
    lines.append(
        "A revisão humana continua necessária porque a busca é limitada por "
        "cobertura das bases, idioma, disponibilidade de metadados e critérios "
        "de elegibilidade que ainda não foram aprovados."
    )
    lines.append("")
    lines.append("## 2. Métodos")
    lines.append("")
    lines.append("### 2.1 Delineamento")
    lines.append("")
    if fulltext_claims:
        design_note = (
            "não houve protocolo aprovado, triagem independente por dois "
            "revisores, avaliação de risco de viés ou síntese quantitativa; "
            "houve leitura de arquivos de texto integral aprovados por humano."
        )
    else:
        design_note = (
            "não houve protocolo aprovado, triagem independente, leitura de "
            "texto integral, avaliação de risco de viés ou síntese quantitativa."
        )
    lines.append(
        "Foi gerado um protocolo de escopo e um mapa de evidências. O desenho "
        f"não é uma revisão sistemática completa: {design_note}"
    )
    lines.append("")
    lines.append("### 2.2 Contrato de recuperação")
    lines.append("")
    lines.append(
        "O contrato de recuperação registra entidade-alvo, identificadores "
        "aceitos, bases, filtros, paginação, orçamento, proveniência e política "
        "para dados externos não confiáveis. A inspiração é a skill MIT "
        "`database-lookup`; nenhum código ou script da skill foi executado."
    )
    lines.append("")
    lines.append("| Base | Papel | Acesso | Limite declarado |")
    lines.append("|---|---|---|---|")
    for database in contract.get("databases", []):
        lines.append(
            f"| {database['name']} | {database['role']} | {database['access']} | "
            f"{database['rate_limit']} |"
        )
    lines.append("")
    lines.append(
        f"**Consulta:** `{search.get('query') or context_query(ctx)}`. "
        f"**Orçamento:** até {contract['budget']['max_records']} registro(s), "
        f"{contract['budget']['per_platform']} por plataforma, "
        f"{contract['budget']['max_queries']} consulta(s). "
        "**Downloads de PDF:** 0."
    )
    lines.append("")
    lines.append("### 2.3 Execução da busca")
    lines.append("")
    if search.get("status") == "blocked":
        lines.append(
            "A busca foi tentada e falhou. O erro está registrado em "
            "`01_sources/search-error.json`; nenhum registro foi fabricado."
        )
    elif search.get("status") == "planned":
        lines.append(
            "A busca não foi executada. O plano está em "
            "`01_sources/search-plan.json` e pode ser revisado antes da execução."
        )
    else:
        search_time = (search.get("manifest") or {}).get(
            "created_at", ctx["generated_at"]
        )
        lines.append(
            f"A busca foi executada em {search_time} e produziu "
            f"{records_count} registro(s). O manifesto normalizado está em "
            "`01_sources/source-records.json`; os campos originalmente "
            "retornados pelas APIs não são reproduzidos integralmente."
        )
        if download_count:
            lines.append(
                f"Foram baixados {download_count} PDF(s) por rotas abertas "
                "verificadas; nenhum paywall foi contornado."
            )
    lines.append("")
    lines.append("### 2.4 Elegibilidade e triagem")
    lines.append("")
    lines.append(
        "Os critérios de inclusão e exclusão permanecem em rascunho no "
        "protocolo. A triagem automática é apenas lexical e exploratória: ela "
        "marca candidatos para leitura humana, sem incluir ou excluir estudos. "
        "Nenhuma decisão de triagem foi gravada como humana."
    )
    lines.append("")
    lines.append("### 2.5 Evidência e gate")
    lines.append("")
    lines.append(
        "Para cada resumo indexado com extensão suficiente, foi extraído um "
        "recorte literal. O recorte foi vinculado ao SHA-256 do resumo e passou "
        "pelo gate metacognitivo, que verifica evidência, falseabilidade, "
        "mecanismo, contradições e calibração. O status máximo possível sem "
        "validação externa é `candidate`; nenhum claim é tratado como verdade."
    )
    lines.append("")
    lines.append("### 2.6 Texto integral e integridade")
    lines.append("")
    if fulltext_candidates:
        lines.append(
            f"Foram indexados arquivos locais de texto integral e propostos "
            f"{len(fulltext_candidates)} recorte(s). Apenas recortes aprovados "
            "explicitamente por um revisor humano recebem status `verified`; os "
            "demais permanecem `candidate` ou `rejected`. A aprovação é contra o "
            "arquivo fornecido, não contra a versão publicada."
        )
    else:
        lines.append(
            "Nenhum diretório de texto integral foi processado nesta execução. "
            "A evidência permanece em nível de resumo indexado."
        )
    lines.append("")
    if integrity_checks:
        lines.append(
            "A integridade foi consultada no Crossref para os estudos com DOI, "
            "dentro de um orçamento explícito. O resultado é observacional: "
            "`no_update_found` não é atestado de integridade."
        )
    else:
        lines.append(
            "A verificação de retratações/correções não foi executada nesta "
            "rodada; o checklist humano continua obrigatório."
        )
    lines.append("")
    lines.append("## 3. Resultados")
    lines.append("")
    lines.append("### 3.1 Fluxo de recuperação")
    lines.append("")
    lines.append("| Etapa | Resultado |")
    lines.append("|---|---|")
    lines.append(f"| Registros recuperados | {records_count} |")
    lines.append(
        f"| Duplicatas removidas | {screening.get('ingest', {}).get('duplicates_removed', 0)} |"
    )
    lines.append(f"| Estudos únicos | {unique_count} |")
    lines.append(f"| Registros com resumo indexado | {with_abstract} |")
    lines.append(f"| Claims com evidência literal | {claim_count} |")
    lines.append(f"| Claims de texto integral | {fulltext_claim_count} |")
    lines.append(f"| Claims do corpus fornecido | {corpus_claim_count} |")
    lines.append(f"| Lacunas registradas | {len(gaps)} |")
    lines.append("")
    if records:
        lines.append("### 3.2 Registros recuperados")
        lines.append("")
        lines.append("| ID | Ano | Título | Fonte | DOI | Resumo |")
        lines.append("|---|---|---|---|---|---|")
        for record in records:
            title = (record.get("title") or "Título não informado").replace("|", "/")
            lines.append(
                f"| {record.get('article_id')} | {record.get('year') or 'não informado'} | "
                f"{title} | {record.get('source') or 'não informado'} | "
                f"{record.get('doi') or 'não informado'} | "
                f"{'sim' if record.get('abstract') else 'não'} |"
            )
        lines.append("")
        lines.append("### 3.3 Panorama descritivo")
        lines.append("")
        lines.append(
            "As contagens abaixo descrevem os metadados recuperados. Elas não "
            "medem qualidade, efeito ou representatividade da literatura."
        )
        lines.append("")
        lines.append(
            f"- **Anos:** {_format_counts(analysis.get('year_counts', {}))}."
        )
        lines.append(
            f"- **Fontes:** {_format_counts(analysis.get('source_counts', {}))}."
        )
        if analysis.get("top_venues"):
            lines.append(
                "- **Veículos mais frequentes:** "
                + "; ".join(
                    f"{item['venue']} ({item['count']})"
                    for item in analysis["top_venues"]
                )
                + "."
            )
        if analysis.get("top_terms"):
            lines.append(
                "- **Termos mais frequentes nos resumos:** "
                + "; ".join(
                    f"{item['term']} ({item['count']})"
                    for item in analysis["top_terms"][:10]
                )
                + "."
            )
        lines.append(
            "- **Escopo inferencial:** metadados e resumos indexados; nenhum "
            "teste estatístico, meta-análise ou inferência causal."
        )
        lines.append("")
    lines.append("### 3.4 Evidências em nível de resumo")
    lines.append("")
    card_scope = (
        "escopo: resumo indexado; ver recortes de texto integral aprovados."
        if fulltext_claims else
        "escopo: resumo indexado; texto integral não lido."
    )
    if cards:
        for card in cards:
            lines.append(
                f"**{card['claim_id']}** — *{card['title']}* "
                f"({card.get('year') or 'ano não informado'}), "
                f"fonte `{card.get('source')}`. Status: `candidate`; "
                f"{card_scope}"
            )
            lines.append("")
            lines.append(f"> “{card['quote']}”")
            lines.append("")
    else:
        lines.append(
            "Nenhum recorte literal de resumo indexado foi produzido nesta "
            "execução."
        )
        if gaps:
            lines.append(
                f"As lacunas estão registradas em `03_evidence/gaps.json` "
                f"({len(gaps)} ocorrência(s))."
            )
        lines.append("")
    fulltext = ctx.get("fulltext") or {}
    integrity = ctx.get("integrity") or {}
    fulltext_candidates = (fulltext.get("candidates") or {}).get("candidates", [])
    fulltext_claims = evidence.get("fulltext_claims") or []
    fulltext_approval = fulltext.get("approval") or {}
    approved_ids = set(fulltext_approval.get("approved_claim_ids") or [])
    rejected_ids = set(fulltext_approval.get("rejected_claim_ids") or [])
    integrity_checks = integrity.get("checks") or []
    section = 5
    if fulltext_candidates:
        lines.append(f"### 3.{section} Evidências em texto integral")
        lines.append("")
        lines.append(
            "Os recortes abaixo foram extraídos de arquivos locais e só recebem "
            "status `verified` quando um revisor humano aprova explicitamente o "
            "claim no arquivo de aprovação. A aprovação confirma o recorte "
            "contra o arquivo fornecido, não contra a versão publicada."
        )
        lines.append("")
        lines.append("| Claim | Estudo | Local | Status | Recorte |")
        lines.append("|---|---|---|---|---|")
        for candidate in fulltext_candidates:
            claim_id = candidate["claim_id"]
            if claim_id in approved_ids:
                status = "verified"
            elif claim_id in rejected_ids:
                status = "rejected"
            else:
                status = "candidate"
            quote = (candidate.get("quote") or "").replace("|", "/")
            if len(quote) > 140:
                quote = quote[:137] + "..."
            title = (candidate.get("title") or "não informado").replace("|", "/")
            lines.append(
                f"| {claim_id} | {title} | {candidate.get('locator')} | "
                f"`{status}` | {quote} |"
            )
        lines.append("")
        if fulltext_approval:
            lines.append(
                f"Aprovação humana: revisor `{fulltext_approval.get('reviewer')}`, "
                f"decisão `{fulltext_approval.get('decision')}`, "
                f"{fulltext_approval.get('counts', {}).get('verified', 0)} "
                "recorte(s) verificado(s)."
            )
            lines.append("")
        else:
            lines.append(
                "Nenhuma aprovação humana foi anexada; todos os recortes "
                "permanecem `candidate`."
            )
            lines.append("")
        section += 1
    if council is not None:
        lines.append(f"### 3.{section} Claims do corpus fornecido")
        lines.append("")
        lines.append(
            "Os claims abaixo foram validados literalmente contra o corpus "
            "fornecido pelo operador. A validação é contra o corpus, não contra "
            "a versão publicada."
        )
        lines.append("")
        lines.append("| Claim | Texto | Status | Confiança | Evidências |")
        lines.append("|---|---|---|---|---|")
        for claim in council.get("claims", []):
            text = (claim.get("text") or "").replace("|", "/")
            if len(text) > 160:
                text = text[:157] + "..."
            lines.append(
                f"| {claim['id']} | {text} | {claim['status']} | "
                f"{claim['confidence']:.2f} | {len(claim.get('evidence', []))} |"
            )
        lines.append("")
        lines.append(
            "O status `partial` do conselho indica que a afirmação não atingiu "
            "os critérios para `supported`; ele não é uma aprovação."
        )
        lines.append("")
        section += 1
    if integrity_checks:
        lines.append(f"### 3.{section} Integridade de literatura")
        lines.append("")
        lines.append(
            "A consulta ao Crossref é observacional: `no_update_found` não é "
            "atestado de integridade e `unchecked` não é ausência de risco."
        )
        lines.append("")
        lines.append("| Estudo | DOI | Status | Atualizações |")
        lines.append("|---|---|---|---|")
        for check in integrity_checks:
            updates = "; ".join(
                str(item.get("relation") or item.get("id") or "")
                for item in (check.get("updates") or [])[:3]
            ) or "não informado"
            lines.append(
                f"| {check.get('study_id')} | {check.get('doi') or 'não informado'} | "
                f"`{check.get('status')}` | {updates.replace('|', '/')} |"
            )
        lines.append("")
        section += 1
    lines.append(f"### 3.{section} Lacunas")
    lines.append("")
    if gaps:
        for gap in gaps:
            lines.append(
                f"- `{gap.get('study_id') or gap.get('article_id')}`: "
                f"{gap.get('reason')} — {gap.get('detail')}"
            )
    else:
        lines.append(
            "Nenhuma lacuna de resumo foi registrada para os estudos triados; "
            "isso não significa que o texto integral esteja disponível."
        )
    lines.append("")
    lines.append("## 4. Discussão")
    lines.append("")
    lines.append(
        "Os dados permitem descrever a cobertura da busca, a distribuição dos "
        "registros por ano e fonte e o conteúdo literal dos resumos indexados. "
        "Eles não permitem estimar efeitos, testar hipóteses causais, comparar "
        "intervenções ou concluir eficácia."
    )
    lines.append("")
    if analysis.get("top_terms"):
        lines.append(
            "Os termos mais frequentes nos resumos — "
            + ", ".join(item["term"] for item in analysis["top_terms"][:8])
            + " — formam um padrão lexical exploratório. Esse padrão não foi "
            "submetido a análise temática, codificação independente ou teste de "
            "saturação."
        )
        lines.append("")
    if fulltext_claims:
        interpretation_note = (
            "A interpretação substantiva exige triagem por dois revisores, "
            "conferência dos recortes aprovados, verificação de retratações e "
            "correções e avaliação do risco de viés."
        )
    else:
        interpretation_note = (
            "A interpretação substantiva exige triagem por dois revisores, "
            "leitura do texto integral, verificação de retratações e correções "
            "e avaliação do risco de viés."
        )
    lines.append(
        f"{interpretation_note} Até lá, o manuscrito é um mapa de evidências, "
        "não uma resposta conclusiva."
    )
    lines.append("")
    lines.append("## 5. Limitações")
    lines.append("")
    limitations = [
        "A busca depende de rede, disponibilidade e limites dos provedores; a ausência de resultados não prova ausência de literatura.",
        (
            "Os claims de texto integral foram verificados contra o arquivo "
            "fornecido, não contra a versão publicada; os claims de metadados "
            "permanecem em nível de resumo indexado."
            if fulltext_claims else
            "Os claims de metadados são em nível de resumo indexado; não houve "
            "leitura do texto integral."
        ),
        "A triagem é lexical e assistida; não substitui dois revisores humanos independentes.",
        "A verificação de retratações/correções depende do Crossref e pode ser incompleta; ausência de atualização não é atestado de integridade.",
        "Não houve validação externa, avaliação por pares, aceite editorial ou publicação.",
        "Não houve teste estatístico, meta-análise, modelagem causal ou análise de risco de viés.",
        "Metadados podem estar incompletos, desatualizados ou conter erros de indexação.",
        "A cobertura é limitada pelas bases escolhidas, pelo idioma e pelo limite por plataforma.",
        "Trechos de resumos e de texto integral são mantidos no idioma original; tradução e interpretação exigem revisão humana.",
        "O corpus fornecido, quando usado, é validado contra si mesmo, não contra a versão publicada.",
        (
            f"{download_count} PDF(s) foram baixados apenas por rotas abertas "
            "verificadas; nenhum paywall foi contornado."
            if download_count else
            "Nenhum PDF foi baixado pelo pipeline e nenhuma credencial foi usada."
        ),
    ]
    if search.get("status") == "blocked":
        limitations.insert(0, "A busca falhou nesta execução; o pacote não contém resultados externos.")
    for limitation in limitations:
        lines.append(f"- {limitation}")
    lines.append("")
    lines.append("## 6. Conclusão")
    lines.append("")
    lines.append(
        "O pacote entrega um protocolo reproduzível, um contrato de recuperação, "
        "contagens de busca, um mapa de evidências e um rascunho de manuscrito. "
        "A pergunta permanece aberta. A próxima etapa é a validação humana do "
        "escopo, da triagem, das citações e das conclusões."
    )
    lines.append("")
    lines.append("## Referências")
    lines.append("")
    reference_records = _unique_records(ctx)
    if reference_records or corpus_index:
        for record in reference_records:
            lines.append(_reference(record))
            lines.append("")
        for source in corpus_index:
            lines.append(_corpus_reference(source))
            lines.append("")
    else:
        lines.append("Nenhuma referência foi recuperada nesta execução.")
        lines.append("")
    lines.append("## Apêndice A — Consulta, fontes e contagens")
    lines.append("")
    lines.append(f"- **Tema:** {theme}")
    lines.append(f"- **Pergunta:** {question}")
    lines.append(f"- **Status da pergunta:** `{question_status}`")
    lines.append(f"- **Consulta executada:** `{search.get('query') or context_query(ctx)}`")
    source_names = ", ".join(
        item.get("name", "não informado") for item in contract.get("databases", [])
    )
    lines.append(f"- **Fontes:** {source_names or 'não informado'}")
    lines.append(f"- **Registros recuperados:** {records_count}")
    lines.append(f"- **Estudos únicos:** {unique_count}")
    lines.append(f"- **Duplicatas removidas:** {screening.get('ingest', {}).get('duplicates_removed', 0)}")
    lines.append(f"- **Claims:** {claim_count}")
    lines.append(f"- **Lacunas:** {len(gaps)}")
    lines.append("")
    lines.append("## Apêndice B — Auditoria")
    lines.append("")
    lines.append(
        "O relatório de auditoria está em `05_audit/audit-report.json`. O gate "
        f"metacognitivo terminou com status `{gate.get('status', 'blocked')}`. "
        "`truth_claim` é sempre `false`; `external_validation` é sempre `false`; "
        "`human_review_required` é sempre `true`."
    )
    lines.append("")
    lines.append("## Apêndice C — Validação humana")
    lines.append("")
    lines.append(
        "O checklist está em `07_validation/VALIDATION.md`. Ele lista o que "
        "ainda precisa ser feito por um humano e não declara que a validação "
        "foi concluída."
    )
    lines.append("")
    return "\n".join(lines)


def context_query(ctx: dict) -> str:
    return ctx["contract"].get("question") or ctx["contract"].get("theme") or ""


def _format_counts(counts: dict) -> str:
    if not counts:
        return "não informado"
    return "; ".join(f"{key}: {value}" for key, value in counts.items())


def _render_validation(ctx: dict) -> str:
    protocol_id = ctx["protocol"].get("protocol_id")
    project_id = ctx["project_id"]
    theme = ctx["contract"]["theme"]
    lines = [
        f"# Validação humana — {theme}",
        "",
        f"**Projeto:** `{project_id}` · **Protocolo:** `{protocol_id}` · "
        f"**Pipeline:** R1051/R1052",
        "",
        "> **Estado:** `pending_human`. Nenhum item abaixo foi executado pelo "
        "pipeline. O manuscrito é um rascunho e não deve ser submetido, "
        "publicado ou tratado como conclusão científica antes desta checklist.",
        "",
        "## O que o pipeline já fez",
        "",
        "- Gerou intake, contrato de recuperação e protocolo em rascunho.",
        "- Executou ou planejou a busca, com contagens e erros registrados.",
        "- Deduplicou registros e produziu triagem lexical assistida.",
        "- Extraiu recortes literais de resumos indexados e/ou corpus fornecido.",
        "- Aplicou o gate metacognitivo e a auditoria determinística.",
        "- Gerou o manuscrito e este checklist.",
        "",
        "## O que ainda precisa ser feito por humanos",
        "",
        "| Item | Estado | Responsável | Evidência esperada |",
        "|---|---|---|---|",
        "| Confirmar a pergunta e o escopo | pending_human | pesquisador responsável | pergunta aprovada e registrada |",
        "| Aprovar o protocolo | pending_human | pesquisador responsável | `status=approved` com nome e data |",
        "| Verificar cobertura e datas das bases | pending_human | bibliotecário ou pesquisador | consulta e data de acesso conferidas |",
        "| Triagem por dois revisores independentes | pending_human | dois revisores | decisões `include`/`exclude` com justificativa |",
        "| Obter textos integrais por via legal | pending_human | pesquisador | arquivos com licença e hash |",
        "| Conferir licença dos PDFs baixados | pending_human | bibliotecário | `rights_basis` e licença conferidos |",
        "| Conferir cada citação no texto integral | pending_human | revisor | recorte literal e localizador |",
        "| Aprovar recortes de texto integral | pending_human | revisor | `fulltext-approval` com revisor, data e confirmação |",
        "| Verificar retratações e correções | pending_human | revisor | consulta a Retraction Watch/Crossref |",
        "| Confirmar que só há `verified` com aprovação humana | pending_human | auditor | confronto entre annotations e approval |",
        "| Avaliar risco de viés | pending_human | revisor metodológico | instrumento e julgamento registrados |",
        "| Revisar análise e limites inferenciais | pending_human | estatístico ou metodólogo | parecer com pressupostos e incerteza |",
        "| Verificar ética, consentimento e conflitos | pending_human | comitê ou pesquisador | declaração e aprovação aplicável |",
        "| Adequar ao periódico-alvo | pending_human | autor | norma, extensão e referências conferidas |",
        "| Confirmar ausência de overclaim | pending_human | revisor independente | leitura crítica do manuscrito |",
        "| Autorizar submissão ou publicação | pending_human | autor responsável | decisão explícita e datada |",
        "",
        "## Comandos de continuidade",
        "",
        "```bash",
        f"python -m marceloclaro.scientific_lab review init --project-id {project_id} "
        f"--title \"Evidências sobre {theme}\" --question \"{ctx['contract']['question']}\" "
        "--human --approved-by \"NOME\"",
        f"python -m marceloclaro.scientific_lab review screen --protocol-id {protocol_id} "
        "--study STUDY-XXXXXXXX --stage title_abstract --reviewer \"NOME\" "
        "--decision include --reason \"JUSTIFICATIVA\" --human",
        "python -m marceloclaro.scientific_lab evidence annotate --project-id "
        f"{project_id} --claim-id CLAIM-... --study-id STUDY-XXXXXXXX "
        "--relation supports --locator \"p. X\" --text \"TRECHO\" "
        "--annotator \"NOME\" --status verified --source-file CAMINHO.pdf --human",
        "```",
        "",
        "## Critério de conclusão",
        "",
        "Todos os itens da tabela precisam estar concluídos, com nome, data e "
        "evidência. A conclusão científica continua sendo responsabilidade "
        "humana; o pipeline não a declara.",
        "",
        "## Limites",
        "",
        "- A triagem automática é lexical e não substitui dois revisores.",
        "- Os claims de metadados são em nível de resumo indexado.",
        "- O corpus fornecido é validado contra si mesmo, não contra a versão publicada.",
        "- Não houve validação externa, aceite editorial ou publicação.",
        "",
    ]
    return "\n".join(lines)


def _render_references(ctx: dict) -> dict:
    records = _unique_records(ctx)
    corpus_index = ctx["evidence"].get("corpus_index", [])
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": ctx["project_id"],
        "generated_at": ctx["generated_at"],
        "records": [
            {
                "article_id": item.get("article_id"),
                "title": item.get("title"),
                "authors": item.get("authors") or [],
                "year": item.get("year"),
                "venue": item.get("venue"),
                "doi": item.get("doi"),
                "url": item.get("url") or item.get("record_url"),
                "source": item.get("source"),
                "abstract_level": bool(item.get("abstract")),
                "retrieved_at": item.get("retrieved_at"),
                "verified": False,
            }
            for item in records
        ],
        "corpus_sources": [
            {
                "id": item["id"],
                "provenance": item["provenance"],
                "text_sha256": item["text_sha256"],
                "verified_against_published_version": False,
            }
            for item in corpus_index
        ],
        "references_verified_count": 0,
        "truth_claim": False,
        "human_review_required": True,
        "limitations": [
            "Referências não foram conferidas contra o texto integral.",
            "Identificadores podem estar incompletos ou desatualizados.",
        ],
    }


def _render_readme(ctx: dict) -> str:
    lines = [
        f"# {ctx['contract']['theme']} — pacote de pesquisa R1051",
        "",
        f"**Projeto:** `{ctx['project_id']}` · **Status:** `{ctx['status']}` · "
        f"**Gerado em:** {ctx['generated_at']}",
        "",
        "> Rascunho para validação humana. Não é artigo aceito, publicado ou "
        "avaliado por pares. Nenhum PDF foi baixado e nenhuma publicação foi "
        "feita.",
        "",
        "## Etapas",
        "",
        "| Etapa | Estado |",
        "|---|---|",
    ]
    for stage, status in ctx["stages"].items():
        lines.append(f"| {stage} | `{status}` |")
    lines += [
        "",
        "## Artefatos principais",
        "",
        "| Caminho | Conteúdo |",
        "|---|---|",
        "| `00_contract/intake.json` | tema, pergunta e modo de execução |",
        "| `00_contract/retrieval-contract.json` | contrato de recuperação |",
        "| `00_contract/systematic-review-protocol.json` | protocolo em rascunho |",
        "| `01_sources/source-records.json` | registros normalizados |",
        "| `01_sources/downloads.json` | downloads OA e recusas |",
        "| `02_screening/triage.json` | triagem lexical assistida |",
        "| `03_evidence/claims.json` | claims e evidências literais |",
        "| `03_evidence/claim-gate.json` | gate metacognitivo |",
        "| `03_evidence/fulltext-candidates.json` | recortes de texto integral para aprovação |",
        "| `03_evidence/integrity-checks.json` | retratações/correções consultadas |",
        "| `04_analysis/descriptive.json` | análise descritiva |",
        "| `05_audit/audit-report.json` | auditoria determinística |",
        "| `06_manuscript/manuscript.md` | manuscrito IMRaD |",
        "| `07_validation/VALIDATION.md` | checklist humano |",
        "| `08_manifest/project-manifest.json` | hashes e estados |",
        "",
        "## Como continuar",
        "",
        "1. Leia `07_validation/VALIDATION.md`.",
        "2. Confirme a pergunta e aprove o protocolo com um revisor humano.",
        "3. Faça a triagem por dois revisores e obtenha os textos integrais.",
        "4. Confira cada citação e atualize as evidências para `verified`.",
        "5. Só então avalie a submissão ao periódico-alvo.",
        "",
        "## Limites",
        "",
        "- A busca é limitada por bases, idioma, metadados e limites por plataforma.",
        "- Claims de metadados são em nível de resumo indexado.",
        "- A triagem é assistida e não substitui revisão humana.",
        "- O manuscrito não foi validado externamente nem publicado.",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# auditoria e manifesto
# ---------------------------------------------------------------------------


def _maybe_load(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return load(path)
    except (OSError, json.JSONDecodeError):
        return None


def _check(check_id: str, status: str, detail: str) -> dict:
    return {"id": check_id, "status": status, "detail": detail}


def audit_project(out: str | Path) -> dict:
    out = Path(out).resolve()
    contract = _maybe_load(out / "00_contract/retrieval-contract.json") or {}
    intake = _maybe_load(out / "00_contract/intake.json") or {}
    protocol_exists = (out / "00_contract/systematic-review-protocol.json").exists()
    intake_exists = bool(intake)
    source_records = _maybe_load(out / "01_sources/source-records.json") or {}
    triage = _maybe_load(out / "02_screening/triage.json") or {}
    claims_doc = _maybe_load(out / "03_evidence/claims.json") or {}
    gate = _maybe_load(out / "03_evidence/claim-gate.json") or {}
    descriptive = _maybe_load(out / "04_analysis/descriptive.json") or {}
    manuscript_path = out / "06_manuscript/manuscript.md"
    manuscript = manuscript_path.read_text(encoding="utf-8") if manuscript_path.exists() else ""
    validation_path = out / "07_validation/VALIDATION.md"
    validation = validation_path.read_text(encoding="utf-8") if validation_path.exists() else ""
    manifest = _maybe_load(out / "08_manifest/project-manifest.json") or {}
    corpus_doc = _maybe_load(out / "03_evidence/corpus-sources.json") or {}
    corpus_sources = corpus_doc.get("sources") or []
    downloads = _maybe_load(out / "01_sources/downloads.json") or {}
    fulltext_candidates_doc = _maybe_load(
        out / "03_evidence/fulltext-candidates.json"
    ) or {}
    fulltext_candidates = fulltext_candidates_doc.get("candidates") or []
    approval_doc = _maybe_load(
        out / "07_validation/fulltext-approval.json"
    ) or {}
    screening_summary = _maybe_load(
        out / "02_screening/screening-summary.json"
    ) or {}
    integrity_doc = _maybe_load(
        out / "03_evidence/integrity-checks.json"
    ) or {}
    search_error = (out / "01_sources/search-error.json").exists()
    search_plan = (out / "01_sources/search-plan.json").exists()
    search_manifests = list((out / "01_sources/metadata").glob("search-*.json"))
    ingest_summary = _maybe_load(
        out / "09_provenance/systematic_review/ingest-summary.json"
    ) or {}
    study_paths = list((out / "01_sources/systematic_review/studies").glob("*.json"))
    claims = claims_doc.get("claims") or []

    checks = []
    checks.append(_check(
        "intake_present", "pass" if intake_exists else "fail",
        "intake.json presente" if intake_exists else "intake.json ausente",
    ))
    checks.append(_check(
        "protocol_present", "pass" if protocol_exists else "fail",
        "protocolo presente" if protocol_exists else "protocolo ausente",
    ))
    missing_contract = [field for field in CONTRACT_REQUIRED if field not in contract]
    checks.append(_check(
        "contract_complete", "pass" if not missing_contract else "fail",
        "contrato completo" if not missing_contract
        else "campos ausentes: " + ", ".join(missing_contract),
    ))
    question_status = contract.get("question_status")
    question_ok = question_status == "explicit" or (
        question_status == "provisional_from_theme"
        and contract.get("clarification_required") is True
    )
    checks.append(_check(
        "question_explicit_or_flagged", "pass" if question_ok else "fail",
        f"question_status={question_status}",
    ))
    if search_error:
        has_alternative = bool(corpus_sources) or bool(
            approval_doc.get("approved_claim_ids")
        )
        search_status = "partial" if has_alternative else "fail"
        search_detail = (
            "busca falhou, mas há corpus/texto integral aprovado"
            if has_alternative else "busca falhou sem fonte alternativa"
        )
    elif search_manifests:
        search_status = "pass"
        search_detail = f"{len(search_manifests)} manifesto(s) de busca"
    elif search_plan:
        search_status = "not_applicable"
        search_detail = "dry-run: busca planejada e não executada"
    else:
        search_status = "fail"
        search_detail = "sem plano, manifesto ou erro de busca"
    checks.append(_check("search_executed", search_status, search_detail))

    if source_records:
        recorded = source_records.get("counts", {}).get("retrieved")
        actual = len(source_records.get("records", []))
        counts_status = "pass" if recorded == actual else "fail"
        counts_detail = f"contagem registrada={recorded}; registros={actual}"
    else:
        counts_status = "not_applicable"
        counts_detail = "sem registros normalizados"
    checks.append(_check("counts_reconciled", counts_status, counts_detail))

    if ingest_summary:
        unique = ingest_summary.get("unique_studies")
        studies_status = "pass" if unique == len(study_paths) else "fail"
        studies_detail = f"estudos únicos={unique}; arquivos={len(study_paths)}"
    else:
        studies_status = "not_applicable"
        studies_detail = "sem ingestão de estudos"
    checks.append(_check("no_duplicate_studies", studies_status, studies_detail))

    if triage:
        triaged = triage.get("studies") or []
        pending = all(item.get("screening_status") == "pending" for item in triaged)
        human_flag = triage.get("human_review_required") is True
        screening_status = "pass" if pending and human_flag else "fail"
        screening_detail = (
            f"{len(triaged)} estudo(s); todos pendentes de humano"
            if screening_status == "pass"
            else "há decisão de triagem sem humano ou flag ausente"
        )
        if not triaged:
            screening_status = "not_applicable"
            screening_detail = "triagem sem estudos"
    else:
        screening_status = "not_applicable"
        screening_detail = "sem triagem"
    checks.append(_check("human_screening_pending", screening_status, screening_detail))

    if screening_summary:
        summary_counts = screening_summary.get("summary") or {}
        screening_policy_ok = (
            screening_summary.get("policy") == "decision_is_human_only"
            and screening_summary.get("truth_claim") is False
        )
        checks.append(_check(
            "screening_pending_not_included",
            "pass" if screening_policy_ok else "fail",
            (
                f"pending={summary_counts.get('pending', 0)}; "
                f"included={summary_counts.get('included', 0)}; "
                f"status={screening_summary.get('status')}"
            ),
        ))
    else:
        checks.append(_check(
            "screening_pending_not_included", "not_applicable",
            "sem resumo de triagem",
        ))

    if downloads:
        download_status = downloads.get("status")
        if download_status in {"not_requested", "not_applicable"}:
            checks.append(_check(
                "downloads_open_access", "not_applicable",
                f"downloads={download_status}",
            ))
        elif download_status == "blocked":
            checks.append(_check(
                "downloads_open_access", "fail",
                "download bloqueado",
            ))
        else:
            allowed_rights = {
                "open_access", "repository", "preprint",
                "public_domain", "user_authorized",
            }
            bad = [
                receipt for receipt in downloads.get("receipts", [])
                if receipt.get("ok") and (
                    receipt.get("rights_basis") not in allowed_rights
                    or not re.fullmatch(
                        r"[a-f0-9]{64}", receipt.get("sha256") or "",
                    )
                )
            ]
            checks.append(_check(
                "downloads_open_access",
                "pass" if not bad else "fail",
                f"{downloads.get('downloaded', 0)} download(s); {len(bad)} inválido(s)",
            ))
    else:
        checks.append(_check(
            "downloads_open_access", "not_applicable", "sem registro de download",
        ))

    if fulltext_candidates:
        bad_candidates = [
            candidate for candidate in fulltext_candidates
            if not re.fullmatch(r"[a-f0-9]{64}", candidate.get("source_sha256") or "")
            or not re.fullmatch(r"[a-f0-9]{64}", candidate.get("quote_sha256") or "")
            or not candidate.get("locator")
            or not candidate.get("source_file")
        ]
        checks.append(_check(
            "fulltext_candidates_hashed",
            "pass" if not bad_candidates else "fail",
            f"{len(fulltext_candidates)} candidato(s); {len(bad_candidates)} sem hash/local",
        ))
    else:
        checks.append(_check(
            "fulltext_candidates_hashed", "not_applicable",
            "sem candidatos de texto integral",
        ))

    fulltext_claims = [
        claim for claim in claims if "-FT-" in claim.get("id", "")
    ]
    if fulltext_claims:
        approval_ok = (
            approval_doc.get("human_confirmation") is True
            and bool(approval_doc.get("approved_claim_ids"))
            and len(approval_doc.get("approved_claim_ids", [])) == len(fulltext_claims)
        )
        checks.append(_check(
            "fulltext_verified_requires_human",
            "pass" if approval_ok else "fail",
            f"{len(fulltext_claims)} claim(s) de texto integral; aprovação={bool(approval_doc)}",
        ))
    else:
        checks.append(_check(
            "fulltext_verified_requires_human", "not_applicable",
            "sem claims de texto integral",
        ))

    if integrity_doc:
        integrity_ok = (
            integrity_doc.get("policy") == "absence_of_update_is_not_proof_of_integrity"
            and integrity_doc.get("truth_claim") is False
        )
        checks.append(_check(
            "integrity_observational",
            "pass" if integrity_ok else "fail",
            f"mode={integrity_doc.get('mode')}; checked={integrity_doc.get('checked', 0)}",
        ))
    else:
        checks.append(_check(
            "integrity_observational", "not_applicable",
            "sem verificação de integridade",
        ))

    if claims:
        evidence_status = "pass" if all(item.get("evidence") for item in claims) else "fail"
        evidence_detail = (
            f"{len(claims)} claim(s) com evidência"
            if evidence_status == "pass" else "claim sem evidência"
        )
    else:
        evidence_status = "not_applicable"
        evidence_detail = "sem claims"
    checks.append(_check("claims_have_evidence", evidence_status, evidence_detail))

    gate_status = "pass" if (
        gate.get("truth_claim") is False
        and gate.get("confidence_promoted") is not True
    ) else "fail"
    checks.append(_check(
        "gate_not_truth", gate_status,
        f"gate={gate.get('status', 'ausente')}; truth_claim={gate.get('truth_claim')}",
    ))

    references_count = (
        len(study_paths) if study_paths
        else len(source_records.get("records") or [])
    ) + len(corpus_sources)
    checks.append(_check(
        "references_present",
        "pass" if references_count else "not_applicable",
        f"{references_count} referência(s) potencial(is)",
    ))

    headings = (
        "## Resumo", "## 1. Introdução", "## 2. Métodos", "## 3. Resultados",
        "## 4. Discussão", "## 5. Limitações", "## 6. Conclusão",
        "## Referências", "## Apêndice A",
    )
    missing_headings = [heading for heading in headings if heading not in manuscript]
    checks.append(_check(
        "manuscript_sections",
        "pass" if not missing_headings else "fail",
        "seções completas" if not missing_headings
        else "seções ausentes: " + ", ".join(missing_headings),
    ))
    checks.append(_check(
        "validation_checklist",
        "pass" if validation and "pending_human" in validation else "fail",
        "checklist presente" if validation else "checklist ausente",
    ))

    placeholders = scan_placeholders(manuscript)
    checks.append(_check(
        "no_placeholders", placeholders["status"],
        f"{len(placeholders['matches'])} marcador(es) de preenchimento",
    ))
    overclaim = scan_overclaim(manuscript)
    checks.append(_check(
        "overclaim", overclaim["status"],
        f"{len(overclaim['matches'])} ocorrência(s) não negada(s)",
    ))
    policy = manifest.get("policy") or {}
    publication = policy.get("publication")
    checks.append(_check(
        "no_publication",
        "pass" if publication == "not_performed" else "not_applicable",
        f"publication={publication or 'manifesto ainda não escrito'}",
    ))

    status = "fail" if any(
        check["status"] == "fail" for check in checks
    ) else "pass_with_pending_human"
    result = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": uid("AUD", 12),
        "project_id": intake.get("project_id") or "RP-UNKNOWN",
        "generated_at": now(),
        "status": status,
        "checks": checks,
        "overclaim": overclaim,
        "placeholders": placeholders,
        "counts": {
            "checks": len(checks),
            "passed": sum(check["status"] == "pass" for check in checks),
            "not_applicable": sum(
                check["status"] == "not_applicable" for check in checks
            ),
            "failed": sum(check["status"] == "fail" for check in checks),
            "records": len(source_records.get("records") or []),
            "studies": len(study_paths),
            "claims": len(claims),
            "fulltext_candidates": len(fulltext_candidates),
            "fulltext_claims": len(fulltext_claims),
            "integrity_checks": len(integrity_doc.get("checks", [])),
            "retracted": sum(
                check.get("status") in {"retracted", "retracted_notice"}
                for check in integrity_doc.get("checks", [])
            ),
            "downloads": downloads.get("downloaded", 0),
            "gaps": len((_maybe_load(out / "03_evidence/gaps.json") or {}).get("gaps", [])),
        },
        "descriptive_status": descriptive.get("status"),
        "publication": "not_performed",
        "pdf_downloads": downloads.get("downloaded", 0),
        "credentials_used": False,
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "A auditoria verifica consistência interna; não valida ciência, ética ou aceite editorial.",
            "Um status `pass_with_pending_human` não é aprovação humana.",
            "A ausência de falha determinística não prova que o manuscrito seja publicável.",
        ],
    }
    return result


def verify_manifest(out: str | Path) -> dict:
    out = Path(out).resolve()
    manifest_path = out / "08_manifest/project-manifest.json"
    if not manifest_path.exists():
        return {
            "status": "fail",
            "checked": 0,
            "failures": ["08_manifest/project-manifest.json ausente"],
        }
    try:
        manifest = load(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "fail",
            "checked": 0,
            "failures": [f"manifesto ilegível: {type(exc).__name__}"],
        }
    failures = []
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        return {"status": "fail", "checked": 0, "failures": ["artifacts inválido"]}
    for item in artifacts:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            failures.append("artefato sem caminho")
            continue
        candidate = (out / item["path"]).resolve()
        try:
            candidate.relative_to(out)
        except ValueError:
            failures.append(f"caminho fora do projeto: {item['path']}")
            continue
        if not candidate.exists():
            failures.append(f"ausente: {item['path']}")
            continue
        expected = item.get("sha256")
        actual = sha256_file(candidate)
        if expected != actual:
            failures.append(f"hash divergente: {item['path']}")
    return {
        "status": "pass" if not failures else "fail",
        "checked": len(artifacts),
        "failures": failures,
    }


def _collect_artifacts(out: Path) -> list[dict]:
    paths: list[Path] = []
    for name in PROJECT_DIRS:
        root = out / name
        if root.exists():
            paths.extend(path for path in root.rglob("*") if path.is_file())
    readme = out / "README.md"
    if readme.exists():
        paths.append(readme)
    manifest_path = out / "08_manifest/project-manifest.json"
    artifacts = []
    for path in sorted(set(paths)):
        if path.resolve() == manifest_path.resolve():
            continue
        artifacts.append({
            "path": path.relative_to(out).as_posix(),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        })
    return artifacts


def _build_manifest(out: Path, ctx: dict, audit: dict) -> dict:
    artifacts = _collect_artifacts(out)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "project_id": ctx["project_id"],
        "pipeline_version": PIPELINE_VERSION,
        "pipeline_revision": PIPELINE_REVISION,
        "theme": ctx["contract"]["theme"],
        "question": ctx["contract"]["question"],
        "question_status": ctx["contract"]["question_status"],
        "created_at": ctx["generated_at"],
        "updated_at": now(),
        "mode": ctx["mode"],
        "status": ctx["status"],
        "corpus_used": bool(ctx["evidence"].get("corpus_index")),
        "budget": ctx["contract"]["budget"],
        "stages": [
            {"id": stage, "status": status}
            for stage, status in ctx["stages"].items()
        ],
        "counts": ctx["counts"],
        "audit": {
            "status": audit["status"],
            "path": "05_audit/audit-report.json",
        },
        "artifacts": artifacts,
        "integrity": {
            "status": "pass",
            "checked": len(artifacts),
            "algorithm": "sha256",
        },
        "policy": {
            "truth_claim": False,
            "external_validation": False,
            "human_review_required": True,
            "no_fabrication": True,
            "untrusted_api_data": True,
            "publication": "not_performed",
            "pdf_downloads": (ctx.get("downloads") or {}).get("downloaded", 0),
            "credentials_used": False,
        },
        "limitations": [
            "O manifesto prova integridade local dos artefatos, não validade científica.",
            "Nenhuma validação externa, aceite editorial ou publicação foi realizada.",
            "A busca pode ser incompleta e os metadados podem conter erros.",
        ],
    }
    dump(out / "08_manifest/project-manifest.json", manifest)
    return manifest


# ---------------------------------------------------------------------------
# execução
# ---------------------------------------------------------------------------


def run(
    theme: str,
    out: str | Path,
    *,
    question: str | None = None,
    sources: Iterable[str] | str | None = None,
    dry_run: bool = False,
    limit: int = 30,
    per_platform: int = 5,
    timeout_seconds: int = 90,
    searcher_factory: Callable | None = None,
    corpus_path: str | Path | None = None,
    fulltext_dir: str | Path | None = None,
    fulltext_approval: str | Path | None = None,
    allow_open_access: bool = False,
    max_downloads: int = 5,
    downloader_factory: Callable | None = None,
    check_integrity: bool = False,
    integrity_checker: Callable | None = None,
    max_integrity_checks: int = 20,
    budget: dict | None = None,
) -> dict:
    theme = normalize_theme(theme)
    out = Path(out).expanduser().resolve()
    corpus = _load_corpus(Path(corpus_path)) if corpus_path is not None else None
    if fulltext_approval is not None and fulltext_dir is None:
        raise ValueError("fulltext_approval exige fulltext_dir")
    if fulltext_dir is not None and not Path(fulltext_dir).expanduser().exists():
        raise ValueError(f"diretório de texto integral não encontrado: {fulltext_dir}")
    if fulltext_approval is not None and not Path(fulltext_approval).expanduser().exists():
        raise ValueError(f"aprovação de texto integral não encontrada: {fulltext_approval}")
    _prepare_output(out)
    if question is None or not str(question).strip():
        question = derive_question(theme)
        question_status = "provisional_from_theme"
    else:
        question = _text(question, "question", 5, 1000)
        question_status = "explicit"
    selected_sources = normalize_sources(sources)
    normalized_budget = normalize_budget(
        budget, limit=limit, per_platform=per_platform,
        timeout_seconds=timeout_seconds,
        max_downloads=max_downloads if allow_open_access else 0,
    )
    project_id = uid("RP", 8)
    generated_at = now()
    query = question if question_status == "explicit" else theme

    intake = {
        "schema_version": SCHEMA_VERSION,
        "intake_id": uid("INTAKE", 12),
        "project_id": project_id,
        "theme": theme,
        "question": question,
        "question_status": question_status,
        "sources": selected_sources,
        "mode": "dry_run" if dry_run else "executed",
        "corpus_requested": corpus_path is not None,
        "fulltext_requested": fulltext_dir is not None,
        "open_access_requested": bool(allow_open_access),
        "integrity_requested": bool(check_integrity),
        "created_at": generated_at,
        "budget": normalized_budget,
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "Pergunta provisória derivada do tema." if question_status == "provisional_from_theme"
            else "Pergunta fornecida pelo operador; ainda não aprovada por protocolo humano.",
        ],
    }
    _write_intake(out, intake)

    contract = build_retrieval_contract(
        theme, question, question_status, selected_sources, normalized_budget,
    )
    _write_contract(out, contract)
    _, protocol = _write_protocol(
        out, project_id, theme, question, selected_sources,
    )
    protocol_id = protocol["protocol_id"]

    stages: dict[str, str] = {
        "intake": "completed",
        "protocol": "completed",
    }

    if dry_run:
        _write_search_plan(out, query, selected_sources, normalized_budget)
        search = {
            "status": "planned",
            "query": query,
            "records": [],
            "manifest": None,
            "manifest_path": None,
            "error": None,
        }
    else:
        try:
            with _hard_deadline(normalized_budget["timeout_seconds"]):
                search = _execute_search(
                    out, query, selected_sources, normalized_budget, searcher_factory,
                )
            search["query"] = query
        except _SearchDeadlineExceeded as exc:
            error = _write_search_error(out, exc, query, selected_sources)
            search = {
                "status": "blocked",
                "query": query,
                "records": [],
                "manifest": None,
                "manifest_path": None,
                "error": error,
            }
        except Exception as exc:  # boundary: falha externa vira estado explícito
            error = _write_search_error(out, exc, query, selected_sources)
            search = {
                "status": "blocked",
                "query": query,
                "records": [],
                "manifest": None,
                "manifest_path": None,
                "error": error,
            }

    download_result = _run_downloads(
        out,
        search["records"],
        enabled=bool(allow_open_access),
        max_downloads=normalized_budget["max_downloads"],
        downloader_factory=downloader_factory,
    )
    fulltext_dirs: list[Path] = []
    if fulltext_dir is not None:
        fulltext_dirs.append(Path(fulltext_dir).expanduser())
    if download_result.get("downloaded"):
        fulltext_dirs.append(out / "01_sources/pdfs")
    deduped_dirs = []
    for directory in fulltext_dirs:
        if directory not in deduped_dirs and directory.exists():
            deduped_dirs.append(directory)

    if search["status"] in {"completed", "completed_empty"}:
        try:
            screening = _screen(
                out,
                search["manifest_path"],
                project_id,
                protocol_id,
                theme,
                question,
                search["records"],
            )
            summary = screening.get("summary") or {}
            if screening["studies"]:
                if summary.get("status") == "human_verified":
                    screening_status = "completed_human_verified"
                elif summary.get("status") == "human_partial":
                    screening_status = "completed_with_pending_human"
                else:
                    screening_status = "completed_assisted"
            else:
                screening_status = "completed_empty"
        except Exception as exc:
            screening = {
                "studies": [],
                "triage": _empty_triage(
                    out, project_id, protocol_id,
                    f"screening_error:{type(exc).__name__}",
                ),
                "ingest": {},
                "prisma_path": None,
                "error": _safe_error(exc),
            }
            screening_status = "blocked"
    else:
        screening = {
            "studies": [],
            "triage": _empty_triage(
                out, project_id, protocol_id,
                "dry_run" if dry_run else "search_blocked",
            ),
            "ingest": {},
            "prisma_path": None,
        }
        screening_status = "planned" if dry_run else "blocked"

    integrity_result = _run_integrity(
        out,
        screening["studies"],
        enabled=bool(check_integrity),
        checker=integrity_checker,
        max_checks=max_integrity_checks,
    )
    if check_integrity and screening["studies"]:
        screening["studies"] = [
            load(path) for path in sorted(
                (out / "01_sources/systematic_review/studies").glob("*.json")
            )
        ]
    fulltext_result = _run_fulltext(
        out,
        project_id,
        screening["studies"],
        search["records"],
        directories=deduped_dirs,
        approval_path=fulltext_approval,
        theme=theme,
        question=question,
    )
    evidence = _collect_evidence(
        out,
        project_id,
        screening["studies"],
        search["records"],
        corpus,
        extra_claims=fulltext_result["claims"],
    )
    analysis = _descriptive_analysis(
        out, project_id, search["records"], screening["studies"], evidence,
    )

    counts = {
        "records_retrieved": len(search["records"]),
        "unique_studies": len(screening["studies"]),
        "duplicates_removed": int(
            screening.get("ingest", {}).get("duplicates_removed", 0)
        ),
        "with_abstract": sum(
            bool(item.get("abstract")) for item in search["records"]
        ),
        "claims": len(evidence["claims"]),
        "blocked_claims": sum(
            claim.get("status") == "blocked"
            for claim in evidence["gate"].get("claims", [])
        ),
        "corpus_claims": len(evidence["corpus_gate_claims"]),
        "downloads": download_result.get("downloaded", 0),
        "fulltext_candidates": fulltext_result["candidates"].get("count", 0),
        "fulltext_verified": (fulltext_result.get("approval") or {}).get(
            "counts", {}
        ).get("verified", 0),
        "integrity_checked": integrity_result.get("checked", 0),
        "retracted_studies": sum(
            study.get("integrity_status") in {"retracted", "retracted_notice"}
            for study in screening["studies"]
        ),
        "references": len(_unique_records({
            "search": search, "screening": screening,
        })) + len(evidence["corpus_index"]),
        "gaps": len(evidence["gaps"]),
    }

    ctx = {
        "project_id": project_id,
        "generated_at": generated_at,
        "mode": "dry_run" if dry_run else "executed",
        "contract": contract,
        "protocol": protocol,
        "search": search,
        "screening": screening,
        "evidence": evidence,
        "downloads": download_result,
        "integrity": integrity_result,
        "fulltext": fulltext_result,
        "analysis": analysis,
        "stages": stages,
        "counts": counts,
        "status": "in_progress",
    }

    manuscript_path = out / "06_manuscript/manuscript.md"
    manuscript_path.parent.mkdir(parents=True, exist_ok=True)
    manuscript_path.write_text(_render_manuscript(ctx), encoding="utf-8")
    dump(out / "06_manuscript/references.json", _render_references(ctx))
    validation_path = out / "07_validation/VALIDATION.md"
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_text(_render_validation(ctx), encoding="utf-8")

    audit = audit_project(out)
    dump(out / "05_audit/audit-report.json", audit)

    if evidence["claims"]:
        evidence_status = (
            "completed_with_fulltext"
            if counts["fulltext_verified"] else "completed_candidate"
        )
    elif dry_run and not evidence["corpus_gate_claims"]:
        evidence_status = "not_applicable"
    else:
        evidence_status = "blocked"
    if fulltext_result["status"] == "not_requested":
        fulltext_stage = "not_requested"
    elif fulltext_result.get("approval"):
        fulltext_stage = "completed_human_approved"
    else:
        fulltext_stage = "completed_pending_human"
    integrity_stage = (
        "completed" if integrity_result.get("mode") == "executed"
        else integrity_result.get("mode", "not_requested")
    )
    stages.update({
        "search": search["status"],
        "downloads": download_result.get("status", "not_requested"),
        "screening": screening_status,
        "integrity": integrity_stage,
        "fulltext": fulltext_stage,
        "evidence": evidence_status,
        "analysis": analysis["status"],
        "audit": audit["status"],
        "manuscript": "completed_draft",
        "validation": "pending_human",
    })
    if dry_run and not evidence["claims"]:
        overall = "planned"
    elif (
        search["status"] == "blocked"
        and not evidence["corpus_gate_claims"]
        and not counts["fulltext_verified"]
    ):
        overall = "blocked"
    elif audit["status"] == "fail":
        overall = "blocked"
    elif not evidence["claims"]:
        overall = "partial"
    else:
        overall = "completed_pending_external_validation"
    ctx["status"] = overall

    (out / "README.md").write_text(_render_readme(ctx), encoding="utf-8")
    manifest = _build_manifest(out, ctx, audit)
    integrity = verify_manifest(out)
    if integrity["status"] != "pass":
        overall = "blocked"
        stages["manifest"] = "blocked"
        manifest["status"] = overall
        manifest["integrity"] = integrity
        dump(out / "08_manifest/project-manifest.json", manifest)
    else:
        stages["manifest"] = "pass"

    return {
        "project_id": project_id,
        "out": str(out),
        "status": overall,
        "stages": stages,
        "counts": counts,
        "audit_status": audit["status"],
        "manifest": str(out / "08_manifest/project-manifest.json"),
        "manifest_integrity": integrity["status"],
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "Pacote para validação humana; não é artigo aceito ou publicado.",
            "Claims de metadados são em nível de resumo indexado.",
            "A triagem automática é assistida e não substitui revisão humana.",
            "A busca pode ser incompleta e depende de rede e limites dos provedores.",
        ],
    }


def _screening_stage(summary: dict, studies: list[dict]) -> str:
    if not studies:
        return "completed_empty"
    status = summary.get("status")
    if status == "human_verified":
        return "completed_human_verified"
    if status == "human_partial":
        return "completed_with_pending_human"
    return "completed_assisted"


def refresh_project(
    out: str | Path,
    *,
    fulltext_dir: str | Path | None = None,
    fulltext_approval: str | Path | None = None,
    allow_open_access: bool = False,
    max_downloads: int = 5,
    downloader_factory: Callable | None = None,
    check_integrity: bool = False,
    integrity_checker: Callable | None = None,
    max_integrity_checks: int = 20,
) -> dict:
    """Reaplica triagem humana, texto integral e integridade a um projeto existente.

    Não repete a busca e não recria estudos. Preserva decisões humanas,
    claims e cartões existentes; adiciona ou substitui apenas as evidências
    de texto integral aprovadas nesta rodada.
    """
    out = Path(out).expanduser().resolve()
    manifest = _maybe_load(out / "08_manifest/project-manifest.json") or {}
    if not manifest:
        raise ValueError("projeto não encontrado: manifesto ausente")
    intake = _maybe_load(out / "00_contract/intake.json") or {}
    contract = _maybe_load(out / "00_contract/retrieval-contract.json") or {}
    protocol = _maybe_load(out / "00_contract/systematic-review-protocol.json") or {}
    source_records = _maybe_load(out / "01_sources/source-records.json") or {}
    if not intake or not contract or not protocol:
        raise ValueError("projeto sem intake, contrato ou protocolo")
    if fulltext_approval is not None and fulltext_dir is None:
        raise ValueError("fulltext_approval exige fulltext_dir")
    if fulltext_dir is not None and not Path(fulltext_dir).expanduser().exists():
        raise ValueError(f"diretório de texto integral não encontrado: {fulltext_dir}")
    if fulltext_approval is not None and not Path(fulltext_approval).expanduser().exists():
        raise ValueError(f"aprovação de texto integral não encontrada: {fulltext_approval}")

    project_id = intake.get("project_id") or manifest.get("project_id")
    protocol_id = protocol.get("protocol_id")
    theme = contract.get("theme") or manifest.get("theme")
    question = contract.get("question") or manifest.get("question")
    records = source_records.get("records") or []
    studies = [
        load(path) for path in sorted(
            (out / "01_sources/systematic_review/studies").glob("*.json")
        )
    ]
    search = {
        "status": "completed" if records else "completed_empty",
        "query": source_records.get("query") or question,
        "records": records,
        "manifest": (
            {"created_at": source_records.get("created_at")}
            if source_records.get("created_at") else None
        ),
        "manifest_path": None,
        "error": None,
    }
    screening_payload = _screening_payload(
        out, project_id, protocol_id, theme, question, records, studies,
    )
    screening_payload["ingest"] = _maybe_load(
        out / "09_provenance/systematic_review/ingest-summary.json"
    ) or {}
    screening_status = _screening_stage(
        screening_payload.get("summary") or {}, screening_payload["studies"],
    )

    existing_downloads = _maybe_load(out / "01_sources/downloads.json") or {}
    if allow_open_access:
        download_result = _run_downloads(
            out,
            records,
            enabled=True,
            max_downloads=max_downloads,
            downloader_factory=downloader_factory,
        )
    else:
        download_result = existing_downloads or {
            "status": "not_requested",
            "downloaded": 0,
            "receipts": [],
            "paths": [],
            "limitations": ["Download não solicitado nesta atualização."],
        }

    if check_integrity:
        integrity_result = _run_integrity(
            out,
            screening_payload["studies"],
            enabled=True,
            checker=integrity_checker,
            max_checks=max_integrity_checks,
        )
        screening_payload["studies"] = [
            load(path) for path in sorted(
                (out / "01_sources/systematic_review/studies").glob("*.json")
            )
        ]
    else:
        integrity_result = _maybe_load(
            out / "03_evidence/integrity-checks.json"
        ) or {
            "schema_version": SCHEMA_VERSION,
            "mode": "not_requested",
            "checks": [],
            "summary": {"not_requested": len(screening_payload["studies"])},
            "checked": 0,
            "policy": "absence_of_update_is_not_proof_of_integrity",
            "truth_claim": False,
            "external_validation": False,
            "human_review_required": True,
            "limitations": ["Verificação de integridade não solicitada."],
        }

    fulltext_dirs: list[Path] = []
    if fulltext_dir is not None:
        fulltext_dirs.append(Path(fulltext_dir).expanduser())
    pdf_dir = out / "01_sources/pdfs"
    if pdf_dir.exists() and any(pdf_dir.glob("*.pdf")):
        fulltext_dirs.append(pdf_dir)
    deduped_dirs = []
    for directory in fulltext_dirs:
        if directory not in deduped_dirs and directory.exists():
            deduped_dirs.append(directory)

    existing_summary = _maybe_load(out / "03_evidence/fulltext-summary.json") or {}
    if deduped_dirs:
        fulltext_result = _run_fulltext(
            out,
            project_id,
            screening_payload["studies"],
            records,
            directories=deduped_dirs,
            approval_path=fulltext_approval,
            theme=theme,
            question=question,
        )
    else:
        fulltext_result = {
            "status": existing_summary.get("status", "not_requested"),
            "index": _maybe_load(out / "03_evidence/fulltext-index.json"),
            "matches": {
                "matches": [],
                "count": existing_summary.get("matches", 0),
                "ambiguous": existing_summary.get("ambiguous_matches", 0),
            },
            "candidates": _maybe_load(
                out / "03_evidence/fulltext-candidates.json"
            ) or {"candidates": [], "count": 0},
            "approval": existing_summary.get("approval"),
            "claims": [],
        }

    existing_claims_doc = _maybe_load(out / "03_evidence/claims.json") or {}
    existing_claims = existing_claims_doc.get("claims") or []
    existing_cards_doc = _maybe_load(out / "03_evidence/evidence-cards.json") or {}
    existing_cards = existing_cards_doc.get("cards") or []
    existing_gaps_doc = _maybe_load(out / "03_evidence/gaps.json") or {}
    existing_gaps = existing_gaps_doc.get("gaps") or []
    retracted_ids = {
        (study.get("source_records") or [None])[0]
        for study in screening_payload["studies"]
        if study.get("integrity_status") in {"retracted", "retracted_notice"}
    }
    filtered_claims = [
        claim for claim in existing_claims
        if not any(
            evidence.get("source_id") in retracted_ids
            for evidence in claim.get("evidence", [])
        )
    ]
    filtered_cards = [
        card for card in existing_cards
        if card.get("article_id") not in retracted_ids
    ]
    if existing_claims:
        base_claims = filtered_claims
        base_cards = filtered_cards
        base_gaps = existing_gaps
    else:
        base_claims = None
        base_cards = None
        base_gaps = None

    evidence = _collect_evidence(
        out,
        project_id,
        screening_payload["studies"],
        records,
        None,
        base_claims=base_claims,
        base_cards=base_cards,
        base_gaps=base_gaps,
        extra_claims=fulltext_result["claims"],
    )
    analysis = _descriptive_analysis(
        out, project_id, records, screening_payload["studies"], evidence,
    )
    counts = {
        "records_retrieved": len(records),
        "unique_studies": len(screening_payload["studies"]),
        "duplicates_removed": int(
            screening_payload.get("ingest", {}).get("duplicates_removed", 0)
        ),
        "with_abstract": sum(bool(item.get("abstract")) for item in records),
        "claims": len(evidence["claims"]),
        "blocked_claims": sum(
            claim.get("status") == "blocked"
            for claim in evidence["gate"].get("claims", [])
        ),
        "corpus_claims": len(evidence["corpus_gate_claims"]),
        "downloads": download_result.get("downloaded", 0),
        "fulltext_candidates": fulltext_result["candidates"].get("count", 0),
        "fulltext_verified": (fulltext_result.get("approval") or {}).get(
            "counts", {}
        ).get("verified", 0),
        "integrity_checked": integrity_result.get("checked", 0),
        "retracted_studies": sum(
            study.get("integrity_status") in {"retracted", "retracted_notice"}
            for study in screening_payload["studies"]
        ),
        "references": len(_unique_records({
            "search": search, "screening": screening_payload,
        })) + len(evidence["corpus_index"]),
        "gaps": len(evidence["gaps"]),
    }
    stages: dict[str, str] = {
        "intake": "completed",
        "protocol": "completed",
        "search": search["status"],
        "downloads": download_result.get("status", "not_requested"),
        "screening": screening_status,
        "integrity": (
            "completed" if integrity_result.get("mode") == "executed"
            else integrity_result.get("mode", "not_requested")
        ),
        "fulltext": (
            "not_requested" if fulltext_result["status"] == "not_requested"
            else "completed_human_approved" if fulltext_result.get("approval")
            else "completed_pending_human"
        ),
        "refresh": "completed",
    }
    ctx = {
        "project_id": project_id,
        "generated_at": now(),
        "mode": "refresh",
        "contract": contract,
        "protocol": protocol,
        "search": search,
        "screening": screening_payload,
        "evidence": evidence,
        "downloads": download_result,
        "integrity": integrity_result,
        "fulltext": fulltext_result,
        "analysis": analysis,
        "stages": stages,
        "counts": counts,
        "status": "in_progress",
    }
    manuscript_path = out / "06_manuscript/manuscript.md"
    manuscript_path.parent.mkdir(parents=True, exist_ok=True)
    manuscript_path.write_text(_render_manuscript(ctx), encoding="utf-8")
    dump(out / "06_manuscript/references.json", _render_references(ctx))
    validation_path = out / "07_validation/VALIDATION.md"
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_text(_render_validation(ctx), encoding="utf-8")
    audit = audit_project(out)
    dump(out / "05_audit/audit-report.json", audit)
    if evidence["claims"]:
        evidence_status = (
            "completed_with_fulltext"
            if counts["fulltext_verified"] else "completed_candidate"
        )
    else:
        evidence_status = "blocked"
    stages.update({
        "evidence": evidence_status,
        "analysis": analysis["status"],
        "audit": audit["status"],
        "manuscript": "completed_draft",
        "validation": "pending_human",
    })
    if audit["status"] == "fail":
        overall = "blocked"
    elif not evidence["claims"]:
        overall = "partial"
    else:
        overall = "completed_pending_external_validation"
    ctx["status"] = overall
    (out / "README.md").write_text(_render_readme(ctx), encoding="utf-8")
    _build_manifest(out, ctx, audit)
    integrity_report = verify_manifest(out)
    if integrity_report["status"] != "pass":
        overall = "blocked"
        stages["manifest"] = "blocked"
    else:
        stages["manifest"] = "pass"
    return {
        "project_id": project_id,
        "out": str(out),
        "status": overall,
        "stages": stages,
        "counts": counts,
        "audit_status": audit["status"],
        "manifest": str(out / "08_manifest/project-manifest.json"),
        "manifest_integrity": integrity_report["status"],
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "Atualização sem nova busca: o conjunto recuperado permanece o original.",
            "A triagem humana só é reconhecida se estiver registrada por review.screen.",
            "Texto integral aprovado não é validação externa nem prova de verdade.",
        ],
    }
