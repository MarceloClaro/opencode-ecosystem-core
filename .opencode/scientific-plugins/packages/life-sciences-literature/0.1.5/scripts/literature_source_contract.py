"""Evidence-only provenance and safe, deterministic literature record links."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

REGISTRY_PATH = Path(__file__).resolve().parents[1] / "references" / "source-links.json"
REDACTED = "REDACTED"

_PRIVATE_TOKENS = frozenset(
    {
        "access",
        "apikey",
        "auth",
        "authorization",
        "bearer",
        "client",
        "code",
        "credential",
        "credentials",
        "criteria",
        "diagnosis",
        "email",
        "expr",
        "expression",
        "filter",
        "input",
        "jwt",
        "key",
        "keyword",
        "keywords",
        "password",
        "patient",
        "phpsessid",
        "private",
        "prompt",
        "q",
        "query",
        "refresh",
        "sas",
        "search",
        "secret",
        "sequence",
        "session",
        "sessionid",
        "sid",
        "sig",
        "signature",
        "subject",
        "term",
        "terms",
        "text",
        "token",
        "variables",
        "webenv",
        "where",
    }
)
_METADATA_KEYS = frozenset(
    {
        "available",
        "capabilities",
        "count",
        "cursor",
        "endpoint",
        "fields",
        "health",
        "limit",
        "message",
        "messages",
        "next",
        "offset",
        "ok",
        "page",
        "pages",
        "pagination",
        "reachable",
        "schema",
        "service",
        "status",
        "timestamp",
        "total",
        "totalcount",
        "updated",
        "uptime",
        "url",
        "version",
        "warnings",
    }
)
_ERROR_KEYS = frozenset({"error", "errors"})
_DIAGNOSTIC_KEYS = _ERROR_KEYS | frozenset({"message", "messages", "warning", "warnings"})
_STRUCTURAL_METADATA_KEYS = frozenset(
    {
        "cursor",
        "extensions",
        "meta",
        "metadata",
        "schema",
        "tracing",
        "type",
        "typename",
    }
)
_RECORD_FIELDS = (
    "records",
    "results",
    "items",
    "collection",
    "articles",
    "documents",
    "hits",
)
_NON_EVIDENCE_MODES = frozenset(
    {
        "check",
        "connectivity",
        "empty",
        "fields",
        "health",
        "info",
        "introspection",
        "metadata",
        "ping",
        "routing",
        "schema",
        "status",
    }
)
_DOI_RE = re.compile(r"^10[.][0-9]{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)
_PMCID_RE = re.compile(r"^PMC[0-9]+(?:[.][0-9]+)?$", re.IGNORECASE)
_GEO_RE = re.compile(r"^(?:GSE|GSM|GPL|GDS)[0-9]+$", re.IGNORECASE)


@lru_cache(maxsize=1)
def _registry() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["skills"]


def _normalized_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _sensitive_key(value: str) -> bool:
    separated = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", value)
    separated = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", separated)
    normalized = re.sub(r"[^a-z0-9]+", "_", separated.casefold()).strip("_")
    collapsed = normalized.replace("_", "")
    return (
        normalized in _PRIVATE_TOKENS
        or collapsed in _PRIVATE_TOKENS
        or bool(set(normalized.split("_")) & _PRIVATE_TOKENS)
        or bool(re.fullmatch(r"q[0-9]+", collapsed))
        or any(
            token in collapsed
            for token in (
                "apikey",
                "patient",
                "subject",
                "diagnosis",
                "expression",
                "webenv",
                "sessionid",
                "phpsessid",
            )
        )
    )


def sanitize_request_url(url: str | None) -> str | None:
    """Strip fragments/userinfo and redact secret or private query parameters."""
    if not isinstance(url, str) or not url.strip():
        return None
    try:
        parts = urlsplit(url)
    except ValueError:
        return None
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        return None
    sanitized = [
        (key, REDACTED if _sensitive_key(key) else value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
    ]
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc.rsplit("@", 1)[-1],
            parts.path,
            urlencode(sanitized),
            "",
        )
    )


def _find_value(record: Any, name: str, depth: int = 0) -> Any:
    if depth > 5:
        return None
    wanted = _normalized_key(name)
    if isinstance(record, dict):
        for key, value in record.items():
            normalized = _normalized_key(str(key))
            if normalized in _DIAGNOSTIC_KEYS:
                continue
            if normalized == wanted and value not in (None, ""):
                return value
        for key, value in record.items():
            if _normalized_key(str(key)) in _DIAGNOSTIC_KEYS:
                continue
            if isinstance(value, (dict, list)):
                found = _find_value(value, name, depth + 1)
                if found is not None:
                    return found
    elif isinstance(record, list):
        for item in record[:20]:
            found = _find_value(item, name, depth + 1)
            if found is not None:
                return found
    return None


def _normalized_identifier(kind: str, value: Any, database: str) -> str | None:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        return None
    identifier = str(value).strip()
    if not identifier or len(identifier) > 256:
        return None
    if kind == "DOI":
        if not _DOI_RE.fullmatch(identifier):
            return None
        return None if any(part in {".", ".."} for part in identifier.split("/")) else identifier
    if kind in {"PMID", "NCBI Gene ID"}:
        return identifier if identifier.isdigit() else None
    if kind == "PMCID":
        if database == "pmc" and identifier.isdigit():
            identifier = "PMC" + identifier
        return identifier.upper() if _PMCID_RE.fullmatch(identifier) else None
    if kind == "GEO accession":
        return identifier.upper() if _GEO_RE.fullmatch(identifier) else None
    return None


def _identifier_fields(skill_name: str, mapping: dict[str, Any], database: str) -> tuple[str, ...]:
    """Return explicit fields plus Entrez fallbacks only for an exact database."""
    fields = [field for field in mapping.get("identifier_fields", []) if isinstance(field, str)]
    expected = mapping.get("database")
    if (
        skill_name == "ncbi-entrez-skill"
        and isinstance(expected, str)
        and database
        and database == expected.casefold()
    ):
        fields.extend(("id", "uid"))
    return tuple(dict.fromkeys(fields))


def canonical_record_url(
    skill_name: str,
    record: dict[str, Any],
    *,
    database: str | None = None,
    identifier_type: str | None = None,
) -> str | None:
    """Link only explicitly supported identifiers in their correct database."""
    if not isinstance(record, dict):
        return None
    entry = _registry().get(skill_name)
    if not isinstance(entry, dict):
        return None
    db = str(database or record.get("database") or record.get("db") or "").casefold()
    for mapping in entry.get("record_url_templates", []):
        kind = mapping.get("identifier_type")
        if not isinstance(kind, str) or (identifier_type is not None and kind != identifier_type):
            continue
        allowed = mapping.get("databases", [])
        expected = mapping.get("database")
        if expected and db and db != expected:
            continue
        if allowed and db not in allowed:
            continue
        for field in _identifier_fields(skill_name, mapping, db):
            identifier = _normalized_identifier(kind, _find_value(record, field), db)
            if identifier is None:
                continue
            template = mapping.get("template")
            if (
                not isinstance(template, str)
                or not template.startswith("https://")
                or "{id}" not in template
            ):
                continue
            return template.replace("{id}", quote(identifier, safe="/" if kind == "DOI" else ""))
    return None


def _has_value(value: Any) -> bool:
    """Find a nonempty scalar without depth limits or cycle risk."""
    pending = [value]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if current is None or current is False or current == "":
            continue
        if isinstance(current, (dict, list)):
            if id(current) in seen:
                continue
            seen.add(id(current))
            pending.extend(current.values() if isinstance(current, dict) else current)
            continue
        return True
    return False


def _is_zero_count(value: Any) -> bool:
    """Recognize numeric zero counts without coercing arbitrary strings."""
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value == 0
    if not isinstance(value, str):
        return False
    return (
        re.fullmatch(
            r"[+-]?(?:0+(?:[.]0*)?|[.]0+)(?:[eE][+-]?[0-9]+)?",
            value.strip(),
        )
        is not None
    )


def _has_collection_value(value: Any) -> bool:
    """Find a record value while ignoring structural metadata wrappers."""
    if not isinstance(value, (dict, list)):
        return False
    pending = [value]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if isinstance(current, (dict, list)):
            if id(current) in seen:
                continue
            seen.add(id(current))
            if isinstance(current, dict):
                pending.extend(
                    child
                    for key, child in current.items()
                    if _normalized_key(str(key)) not in _DIAGNOSTIC_KEYS | _STRUCTURAL_METADATA_KEYS
                )
            else:
                pending.extend(current)
        elif not isinstance(current, bool) and current is not None and current != "":
            return True
    return False


def _has_identifier_collection_value(value: Any) -> bool:
    """Accept containers or a single positive numeric Entrez identifier."""
    if isinstance(value, (dict, list)):
        return _has_collection_value(value)
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value > 0
    return isinstance(value, str) and value.strip().isdigit() and int(value.strip()) > 0


def _summary_mode(summary: Any) -> str:
    """Classify nested response summaries with metadata-wrapper suppression."""
    if not _has_value(summary):
        return "empty"
    if not isinstance(summary, dict):
        return "evidence"
    normalized_collections = {_normalized_key(field) for field in _RECORD_FIELDS}
    identifier_collections = {"idlist", "ids", "uids"}
    normalized_counts = {
        "count",
        "hitcount",
        "recordcount",
        "recordcountreturned",
        "resultcount",
        "total",
        "totalcount",
    }
    saw_empty = False
    saw_evidence = False
    saw_failure = False
    pending: list[tuple[dict[str, Any] | list[Any], bool]] = [(summary, False)]
    seen: set[int] = set()
    while pending:
        current, suppress_leaves = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, list):
            for item in current:
                if isinstance(item, (dict, list)):
                    pending.append((item, suppress_leaves))
                elif not suppress_leaves and not isinstance(item, bool) and _has_value(item):
                    saw_evidence = True
            continue
        for key, value in current.items():
            normalized = _normalized_key(str(key))
            if normalized in _STRUCTURAL_METADATA_KEYS:
                continue
            if normalized in _DIAGNOSTIC_KEYS:
                if normalized in _ERROR_KEYS and _has_value(value):
                    saw_failure = True
                continue
            if normalized in normalized_collections:
                if _has_collection_value(value):
                    saw_evidence = True
                else:
                    saw_empty = True
            elif normalized in identifier_collections:
                if _has_identifier_collection_value(value):
                    saw_evidence = True
                else:
                    saw_empty = True
            elif normalized in normalized_counts:
                if _is_zero_count(value):
                    saw_empty = True
            elif normalized == "data" and not _has_value(value):
                saw_empty = True
            elif isinstance(value, (dict, list)):
                pending.append((value, suppress_leaves or normalized in _METADATA_KEYS))
            elif (
                not suppress_leaves
                and normalized not in _METADATA_KEYS
                and not isinstance(value, bool)
                and _has_value(value)
            ):
                saw_evidence = True
    if saw_evidence:
        return "evidence"
    if saw_failure:
        return "failure"
    return "empty" if saw_empty else "metadata"


def _evidence_mode(output: dict[str, Any], mode: str | None) -> str:
    requested = str(mode or output.get("mode") or "").casefold()
    if requested in _NON_EVIDENCE_MODES:
        return requested
    endpoint = str(output.get("endpoint") or "").removesuffix(".fcgi").casefold()
    if endpoint in {
        "einfo",
        "egquery",
        "espell",
        "health",
        "healthz",
        "schema",
        "status",
    }:
        return "metadata"
    path = str(output.get("path") or "").split("?", 1)[0].rstrip("/").casefold()
    if path.rsplit("/", 1)[-1] in {
        "capabilities",
        "fields",
        "health",
        "healthz",
        "metadata",
        "schema",
        "status",
        "ping",
        "info",
    }:
        return "metadata"
    summary = output.get("summary")
    summary_mode = _summary_mode(summary) if "summary" in output else None
    if summary_mode == "evidence":
        return "evidence"
    saw_record_collection = False
    for field in _RECORD_FIELDS:
        if field in output:
            saw_record_collection = True
            if _has_collection_value(output[field]):
                return "evidence"
    if summary_mode == "failure":
        return "failure"
    if saw_record_collection:
        return "empty"
    for name in ("record_count_returned", "result_count", "hit_count"):
        if name in output:
            value = output[name]
            if (
                isinstance(value, int) and not isinstance(value, bool) and value <= 0
            ) or _is_zero_count(value):
                return "empty"
    if summary_mode is not None:
        return summary_mode
    return "evidence" if output.get("text_head") or output.get("raw_output_path") else "metadata"


def _annotate(
    value: Any, skill_name: str, urls: list[str], database: str | None, depth: int = 0
) -> None:
    if depth > 5:
        return
    if isinstance(value, list):
        for item in value[:100]:
            _annotate(item, skill_name, urls, database, depth + 1)
        return
    if isinstance(value, (str, int)) and not isinstance(value, bool):
        canonical = canonical_record_url(skill_name, {"id": value}, database=database)
        if canonical and canonical not in urls:
            urls.append(canonical)
        return
    if not isinstance(value, dict):
        return
    canonical_for_record: list[str] = []
    entry = _registry().get(skill_name, {})
    db = str(database or "").casefold()
    for mapping in entry.get("record_url_templates", []):
        for field in _identifier_fields(skill_name, mapping, db):
            identifier = _find_value(value, field)
            if identifier is None:
                continue
            canonical = canonical_record_url(
                skill_name,
                {str(field): identifier},
                database=database,
                identifier_type=mapping.get("identifier_type"),
            )
            if canonical and canonical not in canonical_for_record:
                canonical_for_record.append(canonical)
    if canonical_for_record:
        value["canonical_url"] = canonical_for_record[0]
        if len(canonical_for_record) > 1:
            value["canonical_urls"] = canonical_for_record
        else:
            value.pop("canonical_urls", None)
        for canonical in canonical_for_record:
            if canonical not in urls:
                urls.append(canonical)
    else:
        value.pop("canonical_url", None)
        value.pop("canonical_urls", None)
    for key, child in list(value.items()):
        if (
            _normalized_key(str(key)) not in _DIAGNOSTIC_KEYS
            and key
            not in {
                "sources",
                "checked_sources",
                "canonical_url",
                "canonical_urls",
            }
            and isinstance(child, (dict, list))
        ):
            _annotate(child, skill_name, urls, database, depth + 1)


def _strip_reserved_canonical_fields(value: Any) -> None:
    """Remove untrusted upstream annotations before deciding whether evidence exists."""
    pending = [value]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if not isinstance(current, (dict, list)) or id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, list):
            pending.extend(current)
            continue
        current.pop("canonical_url", None)
        current.pop("canonical_urls", None)
        pending.extend(child for child in current.values() if isinstance(child, (dict, list)))


def evidence_sources(*outputs: Any) -> list[dict[str, Any]]:
    """Return only unique downstream sources that explicitly bear evidence."""
    selected: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for output in outputs:
        if not isinstance(output, dict) or output.get("ok") is not True:
            continue
        for item in output.get("sources", []):
            if (
                not isinstance(item, dict)
                or item.get("supports_claim") is not True
                or item.get("kind") != "evidence"
            ):
                continue
            key = (
                str(item.get("name")),
                str(item.get("canonical_url") or item.get("url")),
            )
            if key not in seen:
                selected.append(item)
                seen.add(key)
    return selected


def apply_source_contract(
    output: dict[str, Any],
    skill_name: str,
    request_url: str | None = None,
    *,
    mode: str | None = None,
) -> dict[str, Any]:
    """Attach evidence-only sources without changing scalar record shapes."""
    if not isinstance(output, dict) or output.get("ok") is not True:
        return output
    entry = _registry().get(skill_name)
    if not isinstance(entry, dict):
        return output
    _strip_reserved_canonical_fields(output)
    kind = _evidence_mode(output, mode)
    sanitized = sanitize_request_url(request_url)
    database = output.get("database") or output.get("db")
    canonical_urls: list[str] = []
    if kind == "evidence":
        for field in (*_RECORD_FIELDS, "summary"):
            if field in output:
                _annotate(
                    output[field],
                    skill_name,
                    canonical_urls,
                    str(database) if database else None,
                )
    source: dict[str, Any] = {
        "name": entry["source_name"],
        "url": (
            canonical_urls[0]
            if len(canonical_urls) == 1
            else sanitized or entry.get("homepage_url")
        ),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "supports_claim": kind == "evidence",
        "kind": "evidence" if kind == "evidence" else "checked",
    }
    if sanitized:
        source["request_url"] = sanitized
    if len(canonical_urls) == 1:
        source["canonical_url"] = canonical_urls[0]
    elif canonical_urls:
        source["canonical_urls"] = canonical_urls
    if kind == "evidence":
        output["sources"] = evidence_sources(output) + [source]
    else:
        output.pop("sources", None)
        source["reason"] = kind
        output.setdefault("checked_sources", []).append(source)
    return output
