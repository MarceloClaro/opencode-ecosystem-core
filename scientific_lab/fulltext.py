"""R1052 — texto integral: indexação, casamento, citações e aprovação humana.

O módulo não decide verdade. Ele indexa arquivos locais autorizados, extrai
recortes literais com página/parágrafo, propõe candidatos e só marca uma
evidência como ``verified`` quando existe um arquivo de aprovação humana
explícito, com revisor, data e confirmação.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterable

from scientific_lab.native import evidence as native_evidence
from scientific_lab.native.common import dump, load, now, sha256_file, uid

SCHEMA_VERSION = "1.0"
FULLTEXT_SUFFIXES = {".pdf", ".md", ".markdown", ".txt"}
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>]+", re.IGNORECASE)
PARAGRAPH_RE = re.compile(r"\n\s*\n+")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _clean(text: str) -> str:
    text = str(text or "").replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalize(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^a-z0-9à-öø-ÿ]+", " ", text)
    return " ".join(text.split())


def _normalize_doi(value: object) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text)
    text = re.sub(r"^doi:\s*", "", text)
    return text.strip().rstrip(".,;)")


def _doi_in_text(text: str) -> str | None:
    match = DOI_RE.search(text or "")
    return _normalize_doi(match.group(0)) if match else None


def _keywords(text: str) -> list[str]:
    stop = {
        "para", "como", "sobre", "entre", "este", "esta", "esse", "essa",
        "dos", "das", "uma", "com", "sem", "por", "que", "não", "nao",
        "the", "and", "for", "with", "from", "this", "that", "study",
    }
    return [
        token for token in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{4,}", (text or "").lower())
        if token not in stop
    ]


def _pdf_pages(path: Path, *, max_pages: int = 300) -> list[dict]:
    try:
        from research.pdf_pipeline import extract_pages
        pages = extract_pages(path.read_bytes())
        if pages:
            return pages[:max_pages]
    except Exception:
        pass
    if shutil.which("pdftotext"):
        try:
            out = subprocess.run(
                ["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
                capture_output=True, text=True, timeout=120,
            )
            if out.returncode == 0 and out.stdout.strip():
                raw_pages = out.stdout.split("\f")
                pages = []
                for index, raw in enumerate(raw_pages[:max_pages], start=1):
                    text = _clean(raw)
                    if text:
                        pages.append({
                            "page": index,
                            "text": text,
                            "empty": False,
                        })
                if pages:
                    return pages
        except Exception:
            pass
    return []


def _text_pages(path: Path, *, max_pages: int = 500) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    paragraphs = [
        _clean(part) for part in PARAGRAPH_RE.split(text)
        if _clean(part)
    ]
    if not paragraphs:
        return []
    return [
        {"page": index, "text": paragraph, "empty": False}
        for index, paragraph in enumerate(paragraphs[:max_pages], start=1)
    ]


def _read_pages(path: Path) -> tuple[str, list[dict]]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdf", _pdf_pages(path)
    if suffix in {".md", ".markdown"}:
        return "markdown", _text_pages(path)
    if suffix == ".txt":
        return "text", _text_pages(path)
    return suffix.lstrip("."), []


def index_fulltexts(
    path: str | Path,
    *,
    max_files: int = 50,
    max_bytes: int = 30_000_000,
) -> dict:
    """Indexa PDFs/Markdown/texto locais, sem baixar ou executar conteúdo."""
    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise ValueError(f"diretório de texto integral não encontrado: {root}")
    if root.is_file():
        files = [root]
        base = root.parent
    else:
        files = sorted(
            item for item in root.rglob("*")
            if item.is_file() and item.suffix.lower() in FULLTEXT_SUFFIXES
        )[:max_files]
        base = root
    if not files:
        raise ValueError("nenhum PDF, Markdown ou TXT encontrado")
    entries = []
    for file_path in files:
        if file_path.stat().st_size > max_bytes:
            entries.append({
                "fulltext_id": "FT-REJECTED",
                "path": file_path.relative_to(base).as_posix(),
                "absolute_path": str(file_path),
                "sha256": None,
                "bytes": file_path.stat().st_size,
                "format": file_path.suffix.lstrip("."),
                "pages": [],
                "page_count": 0,
                "text_chars": 0,
                "empty_pages": 0,
                "limitations": ["arquivo excede o limite de bytes e foi ignorado"],
            })
            continue
        fmt, pages = _read_pages(file_path)
        digest = sha256_file(file_path)
        text_chars = sum(len(page["text"]) for page in pages)
        entries.append({
            "fulltext_id": "FT-" + digest[:12],
            "path": file_path.relative_to(base).as_posix(),
            "absolute_path": str(file_path),
            "sha256": digest,
            "bytes": file_path.stat().st_size,
            "format": fmt,
            "pages": pages,
            "page_count": len(pages),
            "text_chars": text_chars,
            "empty_pages": sum(page["empty"] for page in pages),
            "limitations": [] if pages else ["nenhum texto extraído"],
        })
    with_text = [entry for entry in entries if entry["text_chars"] >= 200]
    if not with_text:
        raise ValueError("nenhum arquivo produziu texto suficiente")
    return {
        "schema_version": SCHEMA_VERSION,
        "root": str(root),
        "entries": entries,
        "count": len(entries),
        "with_text": len(with_text),
        "limitations": [
            "A indexação lê apenas arquivos locais; não verifica licença ou origem.",
            "PDFs digitalizados sem camada de texto podem produzir pouco ou nenhum texto.",
        ],
    }


def write_index(out: str | Path, index: dict) -> Path:
    out = Path(out)
    sanitized = []
    for entry in index["entries"]:
        sanitized.append({
            "fulltext_id": entry["fulltext_id"],
            "path": entry["path"],
            "sha256": entry["sha256"],
            "bytes": entry["bytes"],
            "format": entry["format"],
            "page_count": entry["page_count"],
            "text_chars": entry["text_chars"],
            "empty_pages": entry["empty_pages"],
            "limitations": entry["limitations"],
        })
    path = out / "03_evidence/fulltext-index.json"
    dump(path, {
        "schema_version": SCHEMA_VERSION,
        "root": index["root"],
        "entries": sanitized,
        "count": index["count"],
        "with_text": index["with_text"],
        "limitations": index["limitations"],
        "full_text_retained": False,
        "human_review_required": True,
    })
    return path


def _entry_sample(entry: dict, max_chars: int = 12_000) -> str:
    return " ".join(page["text"] for page in entry["pages"][:4])[:max_chars]


def _record_for_study(study: dict, records: list[dict]) -> dict | None:
    article_ids = study.get("source_records") or []
    by_article = {item.get("article_id"): item for item in records}
    for article_id in article_ids:
        if article_id in by_article:
            return by_article[article_id]
    return None


def _match_score(entry: dict, study: dict, record: dict | None) -> tuple[float, str]:
    sample = _entry_sample(entry)
    sample_norm = _normalize(sample)
    doi = _normalize_doi(
        (study.get("identifiers") or {}).get("doi")
        or ((record or {}).get("doi"))
    )
    title = (
        study.get("canonical_title")
        or (record or {}).get("title")
        or ""
    )
    title_norm = _normalize(title)[:240]
    filename = _normalize(Path(entry["path"]).stem)
    if doi and doi in sample.lower():
        return 1.0, "doi_in_text"
    if doi and _normalize(doi) in filename:
        return 0.98, "doi_in_filename"
    if title_norm and title_norm in sample_norm:
        return 0.95, "title_in_text"
    if title_norm and title_norm[:80] and title_norm[:80] in sample_norm:
        return 0.9, "title_prefix_in_text"
    if title_norm and title_norm[:60] in filename:
        return 0.85, "title_in_filename"
    if title_norm:
        ratio = difflib.SequenceMatcher(
            None, title_norm[:300], sample_norm[:300],
        ).ratio()
        if ratio >= 0.82:
            return round(0.7 + ratio * 0.15, 3), "fuzzy_title"
    return 0.0, "no_match"


def match_entries(index: dict, studies: list[dict], records: list[dict]) -> dict:
    matches = []
    for entry in index["entries"]:
        if entry["text_chars"] < 200:
            continue
        scored = []
        for study in studies:
            record = _record_for_study(study, records)
            score, method = _match_score(entry, study, record)
            if score > 0:
                scored.append((score, method, study, record))
        scored.sort(key=lambda item: (-item[0], item[2].get("study_id", "")))
        if not scored:
            continue
        best_score, best_method, study, record = scored[0]
        ambiguous = (
            len(scored) > 1
            and best_score - scored[1][0] < 0.05
            and scored[1][0] >= 0.82
        )
        matches.append({
            "fulltext_id": entry["fulltext_id"],
            "path": entry["path"],
            "study_id": study["study_id"],
            "article_id": (study.get("source_records") or [None])[0],
            "title": study.get("canonical_title") or (record or {}).get("title"),
            "method": best_method,
            "confidence": round(best_score, 3),
            "ambiguous": ambiguous,
            "alternatives": [
                {
                    "study_id": item[2]["study_id"],
                    "confidence": round(item[0], 3),
                    "method": item[1],
                }
                for item in scored[1:4]
            ],
            "human_review_required": True,
        })
    # um estudo não deve receber dois arquivos completos sem decisão humana
    by_study: dict[str, list[dict]] = {}
    for match in matches:
        by_study.setdefault(match["study_id"], []).append(match)
    for study_id, items in by_study.items():
        items.sort(key=lambda item: (-item["confidence"], item["path"]))
        for duplicate in items[1:]:
            duplicate["ambiguous"] = True
            duplicate["duplicate_for_study"] = True
    return {
        "schema_version": SCHEMA_VERSION,
        "matches": matches,
        "count": len(matches),
        "ambiguous": sum(match["ambiguous"] for match in matches),
        "limitations": [
            "O casamento é textual e pode errar em PDFs sem DOI/título legível.",
            "Correspondência não prova que o arquivo é a versão publicada.",
        ],
        "human_review_required": True,
    }


def extract_candidates(
    index: dict,
    matches: dict,
    studies: list[dict],
    records: list[dict],
    *,
    max_excerpts: int = 5,
    keywords: Iterable[str] = (),
) -> dict:
    from research.pdf_pipeline import select_excerpts

    entries = {entry["fulltext_id"]: entry for entry in index["entries"]}
    studies_by_id = {study["study_id"]: study for study in studies}
    records_by_article = {item["article_id"]: item for item in records}
    candidates = []
    for match in matches["matches"]:
        if match.get("duplicate_for_study"):
            continue
        entry = entries.get(match["fulltext_id"])
        study = studies_by_id.get(match["study_id"])
        if entry is None or study is None or entry["text_chars"] < 200:
            continue
        excerpts = select_excerpts(
            entry["pages"],
            max_excerpts=max_excerpts,
            min_len=80,
            max_len=600,
            keywords=keywords,
        )
        article_id = (study.get("source_records") or [None])[0]
        record = records_by_article.get(article_id, {})
        for position, excerpt in enumerate(excerpts, start=1):
            page = int(excerpt["page"])
            locator = (
                f"p.{page}" if entry["format"] == "pdf"
                else f"par.{page}"
            )
            quote = excerpt["text"]
            candidates.append({
                "claim_id": f"CLAIM-{article_id}-FT-{position:02d}",
                "fulltext_id": entry["fulltext_id"],
                "study_id": study["study_id"],
                "article_id": article_id,
                "title": study.get("canonical_title") or record.get("title"),
                "year": study.get("year") or record.get("year"),
                "doi": (study.get("identifiers") or {}).get("doi"),
                "page": page,
                "locator": locator,
                "quote": quote,
                "quote_sha256": hashlib.sha256(quote.encode("utf-8")).hexdigest(),
                "source_file": entry["path"],
                "source_sha256": entry["sha256"],
                "match_method": match["method"],
                "match_confidence": match["confidence"],
                "verification_status": "candidate",
                "human_review_required": True,
            })
    return {
        "schema_version": SCHEMA_VERSION,
        "candidates": candidates,
        "count": len(candidates),
        "by_study": {
            study_id: sum(
                candidate["study_id"] == study_id for candidate in candidates
            )
            for study_id in studies_by_id
        },
        "limitations": [
            "Os recortes são candidatos; a aprovação humana é obrigatória.",
            "A página ou o parágrafo indicado deve ser conferido no arquivo original.",
        ],
        "human_review_required": True,
    }


def write_candidates(out: str | Path, result: dict) -> Path:
    path = Path(out) / "03_evidence/fulltext-candidates.json"
    dump(path, result)
    return path


def approval_template(project_id: str, candidates: list[dict]) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "reviewer": "",
        "reviewed_at": "",
        "decision": "pending",
        "human_confirmation": False,
        "approved_claim_ids": [],
        "rejected_claim_ids": [],
        "notes": "",
        "candidate_count": len(candidates),
        "instructions": (
            "Preencha reviewer, reviewed_at, decision (approved ou partial), "
            "approved_claim_ids e human_confirmation=true. Confira cada recorte "
            "no arquivo original antes de aprovar."
        ),
    }


def validate_approval(path: str | Path, candidate_ids: Iterable[str]) -> dict:
    approval_path = Path(path)
    if not approval_path.exists():
        raise ValueError(f"aprovação não encontrada: {approval_path}")
    try:
        approval = json.loads(approval_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"aprovação ilegível: {type(exc).__name__}") from exc
    if not isinstance(approval, dict):
        raise ValueError("aprovação deve ser objeto")
    if approval.get("human_confirmation") is not True:
        raise ValueError("aprovação exige human_confirmation=true")
    reviewer = approval.get("reviewer")
    if not isinstance(reviewer, str) or len(reviewer.strip()) < 2:
        raise ValueError("aprovação exige reviewer")
    reviewed_at = approval.get("reviewed_at")
    if not isinstance(reviewed_at, str) or len(reviewed_at.strip()) < 10:
        raise ValueError("aprovação exige reviewed_at")
    decision = approval.get("decision")
    if decision not in {"approved", "partial"}:
        raise ValueError("decision deve ser approved ou partial")
    known = set(candidate_ids)
    approved = approval.get("approved_claim_ids")
    rejected = approval.get("rejected_claim_ids")
    for name, values in (("approved_claim_ids", approved), ("rejected_claim_ids", rejected)):
        if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
            raise ValueError(f"{name} deve ser lista de textos")
        unknown = set(values) - known
        if unknown:
            raise ValueError(f"{name} contém IDs desconhecidos: {sorted(unknown)}")
    if set(approved) & set(rejected):
        raise ValueError("um claim não pode ser aprovado e rejeitado")
    if decision == "approved" and not approved:
        raise ValueError("decision=approved exige ao menos um claim aprovado")
    return approval


def write_approval_template(out: str | Path, template: dict) -> Path:
    path = Path(out) / "07_validation/fulltext-approval.template.json"
    dump(path, template)
    return path


def _remove_existing_fulltext_annotations(out: Path, claim_ids: set[str]) -> int:
    root = out / "09_provenance/evidence_annotations"
    removed = 0
    for path in root.glob("*.json") if root.exists() else []:
        try:
            annotation = load(path)
        except (OSError, ValueError):
            continue
        if (
            annotation.get("claim_id") in claim_ids
            and annotation.get("annotator") in {"R1052-fulltext", "R1052-fulltext-human"}
        ):
            path.unlink()
            removed += 1
    return removed


def apply_approval(
    out: str | Path,
    project_id: str,
    index: dict,
    candidates: list[dict],
    approval: dict,
    studies: list[dict],
) -> dict:
    out = Path(out)
    entries = {entry["fulltext_id"]: entry for entry in index["entries"]}
    study_ids = {study["study_id"] for study in studies}
    approved = set(approval["approved_claim_ids"])
    rejected = set(approval["rejected_claim_ids"])
    removed = _remove_existing_fulltext_annotations(
        out, {candidate["claim_id"] for candidate in candidates},
    )
    counts = {"verified": 0, "rejected": 0, "candidate": 0, "skipped": 0}
    for candidate in candidates:
        if candidate["study_id"] not in study_ids:
            counts["skipped"] += 1
            continue
        if candidate["claim_id"] in approved:
            status = "verified"
        elif candidate["claim_id"] in rejected:
            status = "rejected"
        else:
            status = "candidate"
        entry = entries.get(candidate["fulltext_id"])
        source_file = (
            Path(entry["absolute_path"])
            if status == "verified" and entry is not None
            else None
        )
        native_evidence.annotate(
            out,
            project_id,
            candidate["claim_id"],
            candidate["study_id"],
            "supports",
            candidate["locator"],
            candidate["quote"],
            "R1052-fulltext-human" if status == "verified" else "R1052-fulltext",
            claim_text=(
                f"No texto integral de {candidate.get('title')} "
                f"({candidate.get('year') or 'ano não informado'}), "
                f"{candidate['locator']}, consta: “{candidate['quote']}”"
            ),
            status=status,
            source_file=source_file,
            human=status == "verified",
            verbatim=True,
        )
        counts[status] += 1
    return {
        "schema_version": SCHEMA_VERSION,
        "approval_id": uid("FTAPP", 12),
        "project_id": project_id,
        "reviewer": approval["reviewer"],
        "reviewed_at": approval["reviewed_at"],
        "decision": approval["decision"],
        "approved_claim_ids": sorted(approved),
        "rejected_claim_ids": sorted(rejected),
        "annotations_replaced": removed,
        "counts": counts,
        "truth_claim": False,
        "external_validation": False,
        "human_review_required": True,
        "limitations": [
            "A aprovação confirma o recorte contra o arquivo fornecido, não a versão publicada.",
            "A aprovação humana não promove o claim a verdade; o gate continua separado.",
        ],
    }


def fulltext_claims(
    candidates: list[dict],
    approved_ids: Iterable[str],
    studies: list[dict],
) -> list[dict]:
    approved = set(approved_ids)
    claims = []
    studies_by_id = {study["study_id"]: study for study in studies}
    for candidate in candidates:
        if candidate["claim_id"] not in approved:
            continue
        study = studies_by_id.get(candidate["study_id"])
        if study is None:
            continue
        claims.append({
            "id": candidate["claim_id"],
            "text": (
                f"No texto integral de {candidate.get('title')} "
                f"({candidate.get('year') or 'ano não informado'}), "
                f"{candidate['locator']}, consta: “{candidate['quote']}”"
            ),
            "confidence": 0.7,
            "evidence": [{
                "source_id": candidate["article_id"],
                "quote": candidate["quote"],
                "source_sha256": candidate["source_sha256"],
                "literal_verified": True,
            }],
            "inference_level": "observation",
            "falsifier": (
                "Se o texto integral não contiver o trecho no local indicado "
                "ou se a versão publicada divergir do arquivo fornecido."
            ),
            "contradictions": [],
            "mechanism": (
                "Recorte extraído do texto integral e aprovado explicitamente "
                "por revisor humano; a aprovação não é validação externa."
            ),
        })
    return claims


def write_fulltext_summary(
    out: str | Path,
    index: dict,
    matches: dict,
    candidates: dict,
    approval_result: dict | None,
) -> Path:
    path = Path(out) / "03_evidence/fulltext-summary.json"
    dump(path, {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "files_indexed": index["count"],
        "files_with_text": index["with_text"],
        "matches": matches["count"],
        "ambiguous_matches": matches["ambiguous"],
        "candidates": candidates["count"],
        "approval": approval_result,
        "full_text_retained": False,
        "human_review_required": True,
        "truth_claim": False,
        "external_validation": False,
    })
    return path
