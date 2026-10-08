#!/usr/bin/env python3
"""Compact NCBI PMC article-dataset metadata helper for imported skills."""

from __future__ import annotations

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from urllib.parse import quote

_PLUGIN_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(_PLUGIN_SCRIPTS))

from literature_source_contract import apply_source_contract  # noqa: E402

_SKILL_NAME = Path(__file__).resolve().parents[1].name

try:
    import requests
except ImportError as exc:  # pragma: no cover
    requests = None
    REQUESTS_IMPORT_ERROR = exc
else:
    REQUESTS_IMPORT_ERROR = None

PMC_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PMC_S3_BASE_URL = "https://pmc-oa-opendata.s3.amazonaws.com"
PMCID_RE = re.compile(r"^PMC(?P<accession>[0-9]+)(?:[.](?P<version>[0-9]+))?$", re.IGNORECASE)
DOI_RE = re.compile(r"^10[.][0-9]{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)


def error(code: str, message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {"code": code, "message": message},
        "warnings": warnings or [],
    }


def _require_str(name: str, value: Any, required: bool = False) -> str | None:
    if value is None:
        if required:
            raise ValueError(f"`{name}` is required.")
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"`{name}` must be a non-empty string.")
    return value.strip()


def _require_int(name: str, value: Any, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"`{name}` must be a positive integer.")
    return value


def _require_bool(name: str, value: Any, default: bool) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ValueError(f"`{name}` must be a boolean.")
    return value


def _require_object(name: str, value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"`{name}` must be an object.")
    return value


def _raw_response_bytes(response: Any, data: Any) -> bytes:
    content = getattr(response, "content", None)
    if isinstance(content, bytes):
        return content
    text = getattr(response, "text", None)
    if isinstance(text, str) and text:
        return text.encode(getattr(response, "encoding", None) or "utf-8")
    return json.dumps(data).encode("utf-8")


def _save_raw_json(data: bytes, raw_output_path: str | None) -> str:
    path = Path(raw_output_path or "/tmp/ncbi-pmc.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return str(path)


def _safe_request_error(label: str, exc: Exception) -> str:
    response = getattr(exc, "response", None)
    status_code = getattr(response, "status_code", None)
    if isinstance(status_code, int):
        return f"{label} returned HTTP {status_code}."
    return f"{label} failed ({type(exc).__name__})."


def parse_input(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Input must be one JSON object.")
    params = _require_object("params", payload.get("params"))
    identifier = _require_str("params.id", params.get("id"), required=True)
    max_items = _require_int("max_items", payload.get("max_items"), 10)
    retmax = _require_int("params.retmax", params.get("retmax"), max_items)
    return {
        "identifier": identifier,
        "retmax": retmax,
        "max_items": max_items,
        "timeout_sec": _require_int("timeout_sec", payload.get("timeout_sec"), 30),
        "save_raw": _require_bool("save_raw", payload.get("save_raw"), False),
        "raw_output_path": _require_str("raw_output_path", payload.get("raw_output_path")),
    }


def _ncbi_common_params(params: dict[str, Any]) -> dict[str, Any]:
    merged = dict(params)
    api_key = os.environ.get("NCBI_API_KEY") or os.environ.get("NCBI_EUTILS_API_KEY")
    tool = os.environ.get("NCBI_TOOL")
    email = os.environ.get("NCBI_EMAIL")
    if api_key and "api_key" not in merged:
        merged["api_key"] = api_key
    if tool and "tool" not in merged:
        merged["tool"] = tool
    if email and "email" not in merged:
        merged["email"] = email
    return merged


def _direct_pmcid(identifier: str) -> tuple[str, int | None] | None:
    match = PMCID_RE.fullmatch(identifier)
    if not match:
        return None
    pmcid = f"PMC{match.group('accession')}"
    version = match.group("version")
    return pmcid, int(version) if version is not None else None


def _search_term(identifier: str) -> str:
    if DOI_RE.fullmatch(identifier):
        return f'"{identifier}"[doi]'
    if identifier.isdigit():
        return f"{identifier}[pmid]"
    return f'"{identifier}"[all fields]'


def _resolve_pmcids(
    session: requests.Session, identifier: str, retmax: int, timeout_sec: int
) -> tuple[list[str], int]:
    params = _ncbi_common_params(
        {
            "db": "pmc",
            "term": _search_term(identifier),
            "retmode": "json",
            "retmax": retmax,
        }
    )
    response = session.get(PMC_ESEARCH_URL, params=params, timeout=timeout_sec)
    response.raise_for_status()
    data = response.json()
    result = data.get("esearchresult") if isinstance(data, dict) else None
    if not isinstance(result, dict):
        raise ValueError("PMC ESearch response did not contain `esearchresult`.")
    ids = result.get("idlist")
    if not isinstance(ids, list):
        raise ValueError("PMC ESearch response did not contain an ID list.")
    pmcids = [f"PMC{value}" for value in ids if str(value).isdigit()]
    count_value = result.get("count")
    try:
        total = int(count_value)
    except (TypeError, ValueError):
        total = len(pmcids)
    return pmcids, total


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _version_sort_key(version_key: str) -> tuple[int, int]:
    match = PMCID_RE.fullmatch(version_key)
    if not match:
        return (0, 0)
    return int(match.group("accession")), int(match.group("version") or 0)


def _list_versions(session: requests.Session, pmcid: str, timeout_sec: int) -> list[str]:
    response = session.get(
        PMC_S3_BASE_URL,
        params={"list-type": "2", "prefix": f"{pmcid}.", "delimiter": "/"},
        timeout=timeout_sec,
    )
    response.raise_for_status()
    root = ET.fromstring(response.text)
    versions: set[str] = set()
    for element in root.iter():
        if _local_name(element.tag) != "Prefix" or not element.text:
            continue
        candidate = element.text.strip().rstrip("/")
        if PMCID_RE.fullmatch(candidate):
            versions.add(candidate.upper())
    return sorted(versions, key=_version_sort_key)


def _fetch_metadata(
    session: requests.Session, version_key: str, timeout_sec: int
) -> tuple[dict[str, Any], bytes] | None:
    url = f"{PMC_S3_BASE_URL}/metadata/{quote(version_key, safe='')}.json"
    response = session.get(url, timeout=timeout_sec)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError(f"PMC metadata for {version_key} was not a JSON object.")
    return data, _raw_response_bytes(response, data)


def _https_download_url(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    prefix = "s3://pmc-oa-opendata/"
    if value.startswith(prefix):
        return f"{PMC_S3_BASE_URL}/{value[len(prefix) :]}"
    return value


def _compact_metadata(data: dict[str, Any], max_files: int) -> dict[str, Any]:
    media_values = data.get("media_urls")
    media = media_values if isinstance(media_values, list) else []
    normalized_media = [
        url for value in media[:max_files] if (url := _https_download_url(value)) is not None
    ]
    return {
        "pmcid": data.get("pmcid"),
        "version": data.get("version"),
        "pmid": data.get("pmid"),
        "doi": data.get("doi"),
        "title": data.get("title"),
        "citation": data.get("citation"),
        "is_pmc_openaccess": data.get("is_pmc_openaccess"),
        "is_manuscript": data.get("is_manuscript"),
        "is_historical_ocr": data.get("is_historical_ocr"),
        "is_retracted": data.get("is_retracted"),
        "license_code": data.get("license_code"),
        "pdf_url": _https_download_url(data.get("pdf_url")),
        "xml_url": _https_download_url(data.get("xml_url")),
        "text_url": _https_download_url(data.get("text_url")),
        "media_url_count": len(media),
        "media_urls_truncated": len(media) > len(normalized_media),
        "media_urls": normalized_media,
    }


def execute(payload: Any) -> dict[str, Any]:
    if requests is None:
        return error("missing_dependency", f"`requests` is required: {REQUESTS_IMPORT_ERROR}")
    config = parse_input(payload)
    warnings: list[str] = []
    request_stage = "PMC identifier lookup"
    session = requests.Session()
    try:
        direct = _direct_pmcid(config["identifier"])
        requested_version: int | None = None
        if direct is not None:
            pmcids = [direct[0]]
            requested_version = direct[1]
            pmcid_count_available = 1
        else:
            pmcids, pmcid_count_available = _resolve_pmcids(
                session, config["identifier"], config["retmax"], config["timeout_sec"]
            )

        version_keys: list[str] = []
        request_stage = "PMC Cloud version lookup"
        for pmcid in pmcids:
            if requested_version is not None:
                version_keys.append(f"{pmcid}.{requested_version}")
            else:
                version_keys.extend(_list_versions(session, pmcid, config["timeout_sec"]))

        request_stage = "PMC Cloud metadata lookup"
        raw_records: list[dict[str, Any]] = []
        upstream_payloads: list[bytes] = []
        for version_key in version_keys[: config["max_items"]]:
            fetched = _fetch_metadata(session, version_key, config["timeout_sec"])
            if fetched is None:
                warnings.append(f"No PMC Cloud metadata was found for {version_key}.")
                continue
            metadata, upstream = fetched
            raw_records.append(metadata)
            upstream_payloads.append(upstream)

        if not version_keys and pmcids:
            warnings.append(
                "No current PMC Article Dataset versions were found for the resolved PMCID."
            )

        raw_output_path = None
        raw_page_paths: list[str] = []
        if config["save_raw"] and upstream_payloads:
            raw_output_path = _save_raw_json(upstream_payloads[0], config["raw_output_path"])
            raw_page_paths.append(raw_output_path)
            base = Path(raw_output_path)
            for index, page in enumerate(upstream_payloads[1:], start=2):
                sidecar = base.with_name(f"{base.stem}.page-{index}{base.suffix}")
                raw_page_paths.append(_save_raw_json(page, str(sidecar)))
        records = [_compact_metadata(record, config["max_items"]) for record in raw_records]
        output = {
            "ok": True,
            "source": "ncbi-pmc-cloud",
            "identifier": config["identifier"],
            "pmcids": pmcids,
            "pmcid_count_returned": len(pmcids),
            "pmcid_count_available": pmcid_count_available,
            "record_count_returned": len(records),
            "record_count_available": len(version_keys),
            "truncated": (
                pmcid_count_available > len(pmcids) or len(version_keys) > config["max_items"]
            ),
            "records": records,
            "raw_output_path": raw_output_path,
            "warnings": warnings,
        }
        if len(raw_page_paths) > 1:
            output["raw_page_paths"] = raw_page_paths
        request_url = (
            f"{PMC_S3_BASE_URL}/metadata/{quote(version_keys[0], safe='')}.json"
            if version_keys and records
            else PMC_S3_BASE_URL
        )
        return apply_source_contract(output, _SKILL_NAME, request_url)
    except ET.ParseError as exc:
        return error("invalid_response", f"Could not parse PMC Cloud response: {exc}", warnings)
    except ValueError as exc:
        return error("invalid_response", str(exc), warnings)
    except requests.RequestException as exc:
        return error("network_error", _safe_request_error(request_stage, exc), warnings)
    finally:
        session.close()


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write(json.dumps(error("invalid_json", f"Could not parse JSON input: {exc}")))
        return 2
    try:
        output = execute(payload)
    except ValueError as exc:
        output = error("invalid_input", str(exc))
        code = 2
    else:
        code = 0 if output.get("ok") else 1
    sys.stdout.write(json.dumps(output))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
