"""R935: bounded, metadata-only GDC file inventory for the R934 protocol."""

from __future__ import annotations

import json
import hashlib
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from tempfile import mkstemp
from typing import Callable
from urllib.parse import urlencode, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


GDC_API_BASE = "https://api.gdc.cancer.gov/files"
GDC_VERSION_BASE = "https://api.gdc.cancer.gov/files/versions"
AUTHORIZATION_PATH = Path(__file__).resolve().with_name("gdc_authorized_exclusions.json")
MAX_CONTENT_BYTES = 6 * 1024**3
PAGE_SIZE = 100
VERSION_BATCH_SIZE = 50
MAX_METADATA_HITS = 5000
MAX_PAGE_BYTES = 8 * 1024 * 1024
REQUEST_FIELDS = (
    "file_id,file_name,file_size,md5sum,access,state,data_category,data_type,"
    "analysis.workflow_type,analysis.workflow_version,cases.project.project_id,"
    "cases.case_id,cases.submitter_id,cases.samples.sample_type,"
    "cases.samples.sample_id,cases.samples.submitter_id,"
    "cases.samples.portions.analytes.aliquots.aliquot_id,"
    "cases.samples.portions.analytes.aliquots.submitter_id"
)
_MD5 = re.compile(r"[0-9a-f]{32}\Z")
_TCGA_CASE = re.compile(r"TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}\Z")
_TCGA_SAMPLE = re.compile(r"TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}-[0-9]{2}[A-Z]\Z")
_TCGA_ALIQUOT = re.compile(r"TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}-(?:01|11)[A-Z]-[0-9]{2}[A-Z]-[A-Z0-9]{4}-[0-9]{2}\Z")
_GDC_FILE_VERSION = re.compile(r"[1-9][0-9]*\Z")
_GDC_DATA_RELEASE = re.compile(r"[0-9]+\.[0-9]+(?:\s*-\s*[0-9]+\.[0-9]+)?\Z")
_GDC_RELEASE_VERSION = re.compile(r"[0-9]+\.[0-9]+\Z")
_GDC_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")


class GDCInventoryError(ValueError):
    """A fail-closed GDC response or metadata invariant violation."""

    def __init__(self, code, details=None):
        super().__init__(code)
        self.code = code
        self.details = dict(details or {})


class NoRedirectHandler(HTTPRedirectHandler):
    """Reject all redirects so the client remains on the fixed metadata endpoint."""

    def redirect_request(self, request, response, code, message, headers, new_url):
        raise GDCInventoryError("redirect_blocked")


def _query_filters():
    return {
        "op": "and",
        "content": [
            {"op": "in", "content": {"field": "cases.project.project_id", "value": ["TCGA-KIRC"]}},
            {"op": "in", "content": {"field": "files.data_category", "value": ["Transcriptome Profiling"]}},
            {"op": "in", "content": {"field": "files.data_type", "value": ["Gene Expression Quantification"]}},
            {"op": "in", "content": {"field": "files.analysis.workflow_type", "value": ["STAR - Counts"]}},
            {"op": "in", "content": {"field": "files.access", "value": ["open"]}},
            {"op": "in", "content": {"field": "files.state", "value": ["released"]}},
        ],
    }


def build_request_url(offset: int, size: int) -> str:
    """Build a fixed `/files` query. No caller-supplied URLs or file IDs."""
    if type(offset) is not int or offset < 0 or type(size) is not int or not 1 <= size <= PAGE_SIZE:
        raise ValueError("invalid_page_bounds")
    params = {
        "filters": json.dumps(_query_filters(), ensure_ascii=False, separators=(",", ":")),
        "fields": REQUEST_FIELDS,
        "format": "JSON",
        "from": str(offset),
        "size": str(size),
        "sort": "file_id:asc",
    }
    return GDC_API_BASE + "?" + urlencode(params)


def _fetch_page(offset: int, size: int, request_url: str) -> dict:
    parsed = urlparse(request_url)
    if parsed.scheme != "https" or parsed.netloc != "api.gdc.cancer.gov" or parsed.path != "/files":
        raise GDCInventoryError("fixed_gdc_endpoint_invariant_failed")
    request = Request(
        request_url,
        headers={"Accept": "application/json", "User-Agent": "MarceloClaro-R935-metadata-inventory/1"},
        method="GET",
    )
    opener = build_opener(NoRedirectHandler())
    with opener.open(request, timeout=45) as response:
        if response.geturl() != request.full_url:
            raise GDCInventoryError("redirect_destination_changed")
        body = response.read(MAX_PAGE_BYTES + 1)
    if len(body) > MAX_PAGE_BYTES:
        raise GDCInventoryError("metadata_page_exceeds_8MiB")
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GDCInventoryError("invalid_gdc_json") from exc
    return payload


def _fetch_version_batch(file_ids: list[str]) -> dict:
    """Retrieve version/release metadata for fixed GDC UUIDs, never file bodies."""
    if not file_ids or len(file_ids) > VERSION_BATCH_SIZE or any(not _GDC_UUID.fullmatch(value) for value in file_ids):
        raise GDCInventoryError("invalid_version_lookup_ids")
    request_url = GDC_VERSION_BASE + "/" + ",".join(file_ids)
    parsed = urlparse(request_url)
    if (parsed.scheme != "https" or parsed.netloc != "api.gdc.cancer.gov"
            or parsed.path != "/files/versions/" + ",".join(file_ids) or parsed.query):
        raise GDCInventoryError("fixed_gdc_versions_endpoint_invariant_failed")
    request = Request(
        request_url,
        headers={"Accept": "application/json", "User-Agent": "MarceloClaro-R935-metadata-inventory/1"},
        method="GET",
    )
    opener = build_opener(NoRedirectHandler())
    with opener.open(request, timeout=45) as response:
        if response.geturl() != request.full_url:
            raise GDCInventoryError("version_lookup_redirect_blocked")
        body = response.read(MAX_PAGE_BYTES + 1)
    if len(body) > MAX_PAGE_BYTES:
        raise GDCInventoryError("version_metadata_exceeds_8MiB")
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GDCInventoryError("invalid_version_metadata_json") from exc
    if not isinstance(payload, list):
        raise GDCInventoryError("invalid_version_metadata_shape")
    results = {}
    for row in payload:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise GDCInventoryError("version_metadata_id_missing")
        if row["id"] not in file_ids or row["id"] in results:
            raise GDCInventoryError("version_metadata_id_unexpected_or_duplicate")
        results[row["id"]] = row
    if set(results) != set(file_ids):
        raise GDCInventoryError("version_metadata_ids_incomplete")
    return results


def _require_list(value, reason, *, allow_none=False):
    if value is None and allow_none:
        return []
    if not isinstance(value, list):
        raise GDCInventoryError(reason)
    return value


def _extract_one_relationship(hit):
    """Return one case/sample/aliquot relationship; ambiguous links are errors."""
    cases = _require_list(hit.get("cases"), "case_relationship_missing")
    case_map = {}
    case_signatures = {}
    for case in cases:
        if not isinstance(case, dict):
            raise GDCInventoryError("case_relationship_malformed")
        case_id = case.get("case_id")
        project = case.get("project")
        if not isinstance(project, dict):
            raise GDCInventoryError("case_project_malformed")
        signature = json.dumps(case, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if not isinstance(case_id, str) or not case_id:
            raise GDCInventoryError("case_id_missing")
        if case_id in case_signatures and case_signatures[case_id] != signature:
            raise GDCInventoryError("case_id_relationship_conflict")
        case_map[case_id] = case_map.get(case_id, case)
        case_signatures[case_id] = signature
    case_ids = sorted(case_map)
    if len(case_ids) != 1:
        raise GDCInventoryError("file_case_relationship_ambiguous")
    case = case_map[case_ids[0]]
    case_submitter = case.get("submitter_id")
    project = case.get("project")
    if (project.get("project_id") != "TCGA-KIRC" or not isinstance(case_submitter, str)
            or not _TCGA_CASE.fullmatch(case_submitter)):
        raise GDCInventoryError("case_identity_or_project_missing")
    samples = _require_list(case.get("samples"), "sample_relationship_missing")
    sample_map = {}
    for sample in samples:
        if not isinstance(sample, dict):
            raise GDCInventoryError("sample_relationship_malformed")
        sample_id = sample.get("sample_id")
        if not isinstance(sample_id, str) or not sample_id:
            raise GDCInventoryError("sample_id_missing")
        signature = json.dumps(sample, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if sample_id in sample_map and sample_map[sample_id]["signature"] != signature:
            raise GDCInventoryError("sample_id_relationship_conflict")
        sample_map[sample_id] = {"record": sample, "signature": signature}
    if len(sample_map) != 1:
        raise GDCInventoryError("file_sample_relationship_ambiguous")
    sample = next(iter(sample_map.values()))["record"]
    sample_type = sample.get("sample_type")
    sample_submitter = sample.get("submitter_id")
    if not isinstance(sample_type, str) or not sample_type or not isinstance(sample_submitter, str) or not sample_submitter:
        raise GDCInventoryError("sample_type_or_barcode_missing")
    if not _TCGA_SAMPLE.fullmatch(sample_submitter) or not sample_submitter.startswith(case_submitter + "-"):
        raise GDCInventoryError("sample_barcode_patient_mismatch")
    sample_code_parts = sample_submitter.split("-")
    sample_code = sample_code_parts[3][:2] if len(sample_code_parts) > 3 else ""
    expected_sample_code = {"Primary Tumor": "01", "Solid Tissue Normal": "11"}.get(sample_type)
    if sample_type in {"Primary Tumor", "Solid Tissue Normal"} and sample_code != expected_sample_code:
        raise GDCInventoryError("sample_type_barcode_code_mismatch")
    if sample_type not in {"Primary Tumor", "Solid Tissue Normal"}:
        return {
            "case_id": case_ids[0],
            "patient_submitter_id": case_submitter,
            "patient_id": case_submitter[:12],
            "sample_id": sample["sample_id"],
            "sample_submitter_id": sample_submitter,
            "sample_type": sample_type,
            "aliquot_id": None,
            "aliquot_submitter_id": None,
        }
    aliquots = []
    for portion in _require_list(sample.get("portions"), "sample_portions_malformed", allow_none=True):
        if not isinstance(portion, dict):
            raise GDCInventoryError("sample_portion_malformed")
        for analyte in _require_list(portion.get("analytes"), "sample_analytes_malformed", allow_none=True):
            if not isinstance(analyte, dict):
                raise GDCInventoryError("sample_analyte_malformed")
            aliquots.extend(_require_list(analyte.get("aliquots"), "sample_aliquots_malformed", allow_none=True))
    aliquot_map = {}
    for aliquot in aliquots:
        if not isinstance(aliquot, dict):
            raise GDCInventoryError("aliquot_relationship_malformed")
        identifier, barcode = aliquot.get("aliquot_id"), aliquot.get("submitter_id")
        if not isinstance(identifier, str) or not identifier or not isinstance(barcode, str) or not barcode:
            raise GDCInventoryError("aliquot_id_or_barcode_missing")
        if identifier in aliquot_map and aliquot_map[identifier] != barcode:
            raise GDCInventoryError("aliquot_id_barcode_conflict")
        aliquot_map[identifier] = barcode
    if len(aliquot_map) != 1:
        raise GDCInventoryError("file_aliquot_relationship_ambiguous")
    aliquot_id, aliquot_barcode = next(iter(aliquot_map.items()))
    if not isinstance(aliquot_barcode, str) or not _TCGA_ALIQUOT.fullmatch(aliquot_barcode):
        raise GDCInventoryError("aliquot_barcode_missing")
    if not aliquot_barcode.startswith(sample_submitter + "-"):
        raise GDCInventoryError("aliquot_barcode_sample_mismatch")
    return {
        "case_id": case_ids[0],
        "patient_submitter_id": case_submitter,
        "patient_id": case_submitter[:12],
        "sample_id": sample["sample_id"],
        "sample_submitter_id": sample_submitter,
        "sample_type": sample_type,
        "aliquot_id": aliquot_id,
        "aliquot_submitter_id": aliquot_barcode,
    }


def _load_authorizations():
    """Carrega as exclusões autorizadas declaradas pelo operador.

    A autorização é um artefato versionado no repositório: arquivo único,
    data, base da decisão e workflow esperado. A ausência do artefato não é
    exclusão automática — apenas não há autorização a aplicar.
    """
    try:
        with open(AUTHORIZATION_PATH, "r", encoding="utf-8") as fonte:
            data = json.load(fonte)
    except (OSError, ValueError):
        return []
    authorizations = data.get("authorizations") if isinstance(data, dict) else None
    if not isinstance(authorizations, list):
        return []
    validas = []
    for item in authorizations:
        if not isinstance(item, dict):
            continue
        file_id = item.get("file_id")
        if not isinstance(file_id, str) or not file_id:
            continue
        validas.append({
            "file_id": file_id,
            "authorized_on": str(item.get("authorized_on") or ""),
            "decision_basis": str(item.get("decision_basis") or ""),
            "expected_workflow_version": item.get("expected_workflow_version"),
        })
    return validas


def _release_key(value):
    return tuple(int(part) for part in str(value).split("."))


class GDCMetadataInventory:
    """Fetch only fixed GDC file metadata and persist a fail-closed manifest."""

    # ``root`` is dependency injection for isolated tests; the CLI entry point
    # calls the repository default and exposes no destination-path argument.
    def __init__(self, root=None, page_size=PAGE_SIZE, page_fetcher: Callable | None = None, version_detail_fetcher: Callable | None = None, clock=None):
        if type(page_size) is not int or not 1 <= page_size <= PAGE_SIZE:
            raise ValueError("page_size_out_of_range")
        self.root = Path(root or Path(__file__).resolve().parents[1]).resolve()
        self.output_path = self.root / "outputs" / "core-r934" / "gdc-manifest.json"
        self.page_size = page_size
        network_mode = page_fetcher is None
        self.page_fetcher = page_fetcher or _fetch_page
        self.version_detail_fetcher = version_detail_fetcher or (_fetch_version_batch if network_mode else None)
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())

    def _collect_pages(self):
        records = []
        total = None
        pages = []
        offset = 0
        while total is None or offset < total:
            size = self.page_size if total is None else min(self.page_size, total - offset)
            request_url = build_request_url(offset, size)
            response = self.page_fetcher(offset, size, request_url)
            if not isinstance(response, dict):
                raise GDCInventoryError("invalid_gdc_response")
            if "warnings" not in response:
                raise GDCInventoryError("gdc_warnings_missing")
            warnings = response["warnings"]
            if not isinstance(warnings, dict):
                raise GDCInventoryError("gdc_warnings_malformed")
            if warnings:
                raise GDCInventoryError("gdc_schema_or_query_warning")
            data = response.get("data")
            pagination = data.get("pagination") if isinstance(data, dict) else None
            hits = data.get("hits") if isinstance(data, dict) else None
            if not isinstance(pagination, dict) or not isinstance(hits, list):
                raise GDCInventoryError("pagination_or_hits_missing")
            page_total = pagination.get("total")
            page_from = pagination.get("from")
            page_size = pagination.get("size")
            page_count = pagination.get("count")
            if type(page_total) is not int or page_total <= 0:
                raise GDCInventoryError("invalid_or_empty_pagination_total")
            if page_total > MAX_METADATA_HITS:
                raise GDCInventoryError("metadata_hit_limit_exceeded")
            if total is None:
                total = page_total
            elif page_total != total:
                raise GDCInventoryError("pagination_total_changed_between_pages")
            if (type(page_from) is not int or type(page_size) is not int
                    or type(page_count) is not int
                    or page_from != offset or page_size != size
                    or page_count != len(hits) or not hits):
                raise GDCInventoryError("page_offset_or_count_mismatch")
            expected = min(size, total - offset)
            if len(hits) != expected:
                raise GDCInventoryError("incomplete_page")
            pages.append({"from": offset, "size": size, "count": len(hits), "reported_sort": pagination.get("sort")})
            records.extend(hits)
            offset += len(hits)
        file_ids = []
        for hit in records:
            if not isinstance(hit, dict):
                raise GDCInventoryError("file_metadata_malformed")
            file_id = hit.get("file_id")
            if not isinstance(file_id, str) or not file_id:
                raise GDCInventoryError("file_id_missing")
            if hit.get("id") is not None and hit.get("id") != file_id:
                raise GDCInventoryError("file_id_id_mismatch")
            file_ids.append(file_id)
        if len(file_ids) != len(set(file_ids)):
            raise GDCInventoryError("duplicate_file_id_across_pages")
        if len(file_ids) != total:
            raise GDCInventoryError("pagination_total_not_reconciled_to_unique_file_ids")
        if file_ids != sorted(file_ids):
            raise GDCInventoryError("file_id_sort_order_mismatch")
        return records, total, pages

    def _normalize_record(self, hit):
        if not isinstance(hit, dict):
            raise GDCInventoryError("file_metadata_malformed")
        file_id = hit.get("file_id")
        if not isinstance(file_id, str) or not file_id:
            raise GDCInventoryError("file_id_missing", {"fields": ["file_id"]})
        if hit.get("id") is not None and hit.get("id") != file_id:
            raise GDCInventoryError("file_id_id_mismatch", {"file_id": file_id, "fields": ["id", "file_id"]})
        analysis = hit.get("analysis")
        if not isinstance(analysis, dict):
            raise GDCInventoryError("analysis_metadata_malformed", {"file_id": file_id, "fields": ["analysis"]})
        if hit.get("access") != "open" or hit.get("state") != "released":
            raise GDCInventoryError("file_not_open_and_released", {"file_id": file_id, "fields": ["access", "state"]})
        if hit.get("data_category") != "Transcriptome Profiling" or hit.get("data_type") != "Gene Expression Quantification":
            raise GDCInventoryError("file_category_or_type_mismatch")
        if analysis.get("workflow_type") != "STAR - Counts":
            raise GDCInventoryError("workflow_type_mismatch")
        workflow_version = analysis.get("workflow_version")
        # The documented/live /files response returned these as default metadata
        # in outputs/core-r934/gdc-query-preflight.json; requesting them in
        # `fields` produced an unrecognized-field warning, so keep them out of
        # REQUEST_FIELDS and validate the default response values here.
        version = hit.get("version")
        data_release = hit.get("data_release")
        file_version = str(version).strip() if type(version) in (str, int) else ""
        try:
            relation = _extract_one_relationship(hit)
        except GDCInventoryError as exc:
            details = {"file_id": file_id, "fields": ["case/sample/aliquot relationship"]}
            details.update(exc.details)
            raise GDCInventoryError(exc.code, details) from exc
        sample_type = relation["sample_type"]
        condition_map = {"Primary Tumor": "tumor", "Solid Tissue Normal": "normal"}
        condition = condition_map.get(sample_type)
        workflow_version_valid = isinstance(workflow_version, str) and bool(workflow_version.strip())
        file_version_valid = bool(_GDC_FILE_VERSION.fullmatch(file_version))
        data_release_valid = isinstance(data_release, str) and bool(_GDC_DATA_RELEASE.fullmatch(data_release.strip()))
        normalized_data_release = re.sub(r"\s*-\s*", "-", data_release.strip()) if data_release_valid else None
        file_size = hit.get("file_size")
        md5sum = hit.get("md5sum")
        file_name = hit.get("file_name")
        if condition:
            if type(file_size) is not int or file_size <= 0:
                raise GDCInventoryError("file_size_missing_or_invalid", {"file_id": file_id, "fields": ["file_size"]})
            if not isinstance(md5sum, str) or not _MD5.fullmatch(md5sum):
                raise GDCInventoryError("md5sum_missing_or_invalid", {"file_id": file_id, "fields": ["md5sum"]})
            if not isinstance(file_name, str) or not file_name:
                raise GDCInventoryError("file_name_missing", {"file_id": file_id, "fields": ["file_name"]})
            if not workflow_version_valid:
                raise GDCInventoryError("workflow_or_release_metadata_missing", {"file_id": file_id, "fields": ["analysis.workflow_version"]})
        else:
            if type(file_size) is not int or file_size <= 0:
                file_size = None
            if not isinstance(md5sum, str) or not _MD5.fullmatch(md5sum):
                md5sum = None
            if not isinstance(file_name, str) or not file_name:
                file_name = None
        return {
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "md5sum": md5sum,
            "access": hit["access"],
            "state": hit["state"],
            "data_category": hit["data_category"],
            "data_type": hit["data_type"],
            "workflow_type": analysis["workflow_type"],
            "workflow_version": workflow_version if workflow_version_valid else None,
            "version": file_version if file_version_valid else None,
            "data_release": data_release if data_release_valid else None,
            "data_release_normalized": normalized_data_release,
            "version_metadata_missing_fields": [
                field for field, valid in (("version", file_version_valid), ("data_release", data_release_valid))
                if not valid
            ] if condition else [],
            "version_metadata_source": "files_endpoint_default" if condition and file_version_valid and data_release_valid else None,
            "relationship": relation,
            "condition": condition,
            "selection_status": "candidate" if condition else "excluded_sample_type_out_of_scope",
            "exclusion_reason": None if condition else "sample_type_out_of_scope",
        }

    @staticmethod
    def _select_one_per_patient_condition(records):
        groups = {}
        for record in records:
            if record["condition"]:
                relationship = record["relationship"]
                key = (relationship["patient_id"], record["condition"])
                groups.setdefault(key, []).append(record)
        for candidates in groups.values():
            candidates.sort(key=lambda row: (row["relationship"]["aliquot_submitter_id"], row["file_id"]))
            candidates[0]["selection_status"] = "selected_for_manifest"
            for row in candidates[1:]:
                row["selection_status"] = "excluded_duplicate_patient_condition"
                row["exclusion_reason"] = "alternative_aliquot_sensitivity_candidate"
        return [row for row in records if row["selection_status"] == "selected_for_manifest"]

    def _resolve_missing_version_metadata(self, selected):
        """Resolve metadados de versão/ release dos arquivos selecionados.

        Quando o detalhe de versões está disponível, **todos** os arquivos
        selecionados são reconciliados com ``/files/versions`` — não apenas os
        que vieram sem ``version``/``data_release``. A lista ``latest_release``
        de cada arquivo é a entrada da regra de compatibilidade por interseção
        exata (SPEC-935-R935); sem ela, faixas textuais diferentes não podem
        ser comparadas. Quando o detalhe não está disponível, apenas os
        arquivos com campos ausentes são exigidos — e a ausência do
        descobridor é bloqueadora, nunca uma suposição.
        """
        missing = [row for row in selected if row.get("version_metadata_missing_fields")]
        if not missing and self.version_detail_fetcher is None:
            return
        if self.version_detail_fetcher is None:
            raise GDCInventoryError(
                "version_detail_fetcher_unavailable",
                {"file_ids": [row["file_id"] for row in missing], "fields": sorted({field for row in missing for field in row["version_metadata_missing_fields"]})},
            )
        file_ids = [row["file_id"] for row in selected]
        details_by_id = {}
        for start in range(0, len(file_ids), VERSION_BATCH_SIZE):
            batch = file_ids[start:start + VERSION_BATCH_SIZE]
            details = self.version_detail_fetcher(batch)
            if not isinstance(details, dict) or set(details) != set(batch):
                raise GDCInventoryError("version_metadata_ids_incomplete", {"file_ids": batch})
            details_by_id.update(details)

        for row in selected:
            file_id = row["file_id"]
            details = details_by_id[file_id]
            if not isinstance(details, dict):
                raise GDCInventoryError("version_metadata_shape_invalid", {"file_id": file_id, "fields": ["version metadata"]})
            if details.get("id") != file_id or details.get("latest_id") != file_id:
                raise GDCInventoryError("version_metadata_latest_id_mismatch", {"file_id": file_id, "fields": ["id", "latest_id"]})
            latest_version = str(details.get("latest_version") or details.get("version") or "").strip()
            if not _GDC_FILE_VERSION.fullmatch(latest_version):
                raise GDCInventoryError("version_metadata_latest_version_invalid", {"file_id": file_id, "fields": ["latest_version"]})
            if row.get("version") and row["version"] != latest_version:
                raise GDCInventoryError("file_version_not_latest", {"file_id": file_id, "fields": ["version", "latest_version"]})

            latest_md5 = details.get("latest_md5") or details.get("md5")
            latest_size = details.get("latest_size") or details.get("size")
            if latest_md5 != row["md5sum"] or latest_size != row["file_size"]:
                raise GDCInventoryError("version_metadata_content_metadata_mismatch", {"file_id": file_id, "fields": ["md5sum", "file_size"]})

            releases = details.get("latest_release")
            if (not isinstance(releases, list) or not releases
                    or any(not isinstance(item, str) or not _GDC_RELEASE_VERSION.fullmatch(item) for item in releases)):
                raise GDCInventoryError("version_metadata_release_list_invalid", {"file_id": file_id, "fields": ["latest_release"]})
            ordered_releases = sorted(set(releases), key=_release_key)
            release_range = ordered_releases[0] if len(ordered_releases) == 1 else f"{ordered_releases[0]} - {ordered_releases[-1]}"
            existing_release = row.get("data_release")
            if (not existing_release or row.get("version_metadata_missing_fields")):
                if existing_release and re.sub(r"\s*-\s*", "-", existing_release.strip()) != re.sub(r"\s*-\s*", "-", release_range):
                    raise GDCInventoryError("file_release_metadata_mismatch", {"file_id": file_id, "fields": ["data_release", "latest_release"]})
                row["data_release"] = existing_release or release_range
                row["data_release_normalized"] = re.sub(r"\s*-\s*", "-", row["data_release"].strip())
            row["version"] = latest_version
            row["version_metadata_source"] = "files_versions_api"
            row["available_releases"] = ordered_releases
            row["version_metadata_missing_fields"] = []

    def _apply_authorized_exclusion(self, selected, records):
        """Aplica a exclusão autorizada do operador, se houver divergência real.

        Retorna ``(selected_sem_excluido, exclusoes, blocker)``. O blocker
        interrompe o manifesto com ``blocked_metadata_exclusion_policy``:
        metadado observado diferente do declarado, ou candidato alternativo do
        mesmo paciente/condição, não podem ser absorvidos em silêncio.
        """
        authorizations = {item["file_id"]: item for item in _load_authorizations()}
        if not authorizations:
            return selected, [], None
        divergentes = {}
        for row in selected:
            divergentes.setdefault(row.get("workflow_version"), []).append(row)
        if len(divergentes) < 2:
            return selected, [], None
        for authorization in authorizations.values():
            alvo = next((row for row in selected if row["file_id"] == authorization["file_id"]), None)
            if alvo is None:
                continue
            esperado = authorization.get("expected_workflow_version")
            if esperado and alvo.get("workflow_version") != esperado:
                return selected, [], {
                    "code": "authorized_exclusion_metadata_mismatch",
                    "file_id": alvo["file_id"],
                    "fields": ["analysis.workflow_version"],
                }
            alternativa = next(
                (
                    row for row in records
                    if row["file_id"] != alvo["file_id"]
                    and row.get("condition")
                    and row["condition"] == alvo.get("condition")
                    and row["relationship"]["patient_id"] == alvo["relationship"]["patient_id"]
                ),
                None,
            )
            if alternativa is not None:
                return selected, [], {
                    "code": "authorized_exclusion_alternative_candidate_present",
                    "file_id": alvo["file_id"],
                    "fields": ["cases.submitter_id", "cases.samples.sample_type"],
                }
            canonicais = [row for row in selected if row["file_id"] != alvo["file_id"]]
            workflows_canonicos = sorted({row.get("workflow_version") for row in canonicais})
            if len(workflows_canonicos) != 1 or workflows_canonicos[0] == alvo.get("workflow_version"):
                return selected, [], {
                    "code": "authorized_exclusion_workflow_divergence_not_observed",
                    "file_id": alvo["file_id"],
                    "fields": ["analysis.workflow_version"],
                }
            release_normalizado = alvo.get("data_release_normalized")
            rationale = (
                f"Exclusão autorizada pelo operador em {authorization['authorized_on']} para o file_id "
                f"{alvo['file_id']}: o arquivo foi processado com workflow_version "
                f"{alvo.get('workflow_version')}, distinto do workflow_version canônico "
                f"{workflows_canonicos[0]}. O data_release observado ({release_normalizado}) não é motivo "
                f"de exclusão. A justificativa é preservar workflow homogêneo: sem demonstração de "
                f"equivalência entre versões STAR - Counts, misturá-las poderia confundir processamento "
                f"com variação biológica. A decisão é metadata-only, antes de examinar expressão ou "
                f"desfecho, e não afirma que o arquivo seja inválido."
            )
            alvo["selection_status"] = "excluded_workflow_version_incompatible"
            alvo["exclusion_reason"] = "operator_authorized_workflow_version_incompatibility"
            alvo["exclusion_rationale"] = rationale
            exclusao = {
                "file_id": alvo["file_id"],
                "workflow_version": alvo.get("workflow_version"),
                "data_release": release_normalizado,
                "latest_release": list(alvo.get("available_releases") or []),
                "authorized_on": authorization["authorized_on"],
                "decision_basis": authorization["decision_basis"],
                "rationale": rationale,
            }
            restantes = [row for row in selected if row["file_id"] != alvo["file_id"]]
            return restantes, [exclusao], None
        return selected, [], None

    def _metadata_fingerprint(self, records):
        normalized = [self._normalize_record(row) for row in records]
        normalized.sort(key=lambda row: row["file_id"])
        canonical = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _build_manifest(self, records, total, pages):
        normalized = [self._normalize_record(hit) for hit in records]
        selected = self._select_one_per_patient_condition(normalized)
        selected_ids = [row["file_id"] for row in selected]
        if not selected or len(selected_ids) != len(set(selected_ids)):
            raise GDCInventoryError("empty_or_duplicate_selected_files")
        self._resolve_missing_version_metadata(selected)
        selected, authorized_exclusions, exclusion_blocker = self._apply_authorized_exclusion(
            selected, normalized
        )
        selected_bytes = sum(row["file_size"] for row in selected)
        workflow_versions = sorted({row["workflow_version"] for row in selected})
        release_values = sorted({row["data_release_normalized"] for row in selected})
        release_values_raw = sorted({row["data_release"] for row in selected})
        query_fingerprint = {
            "endpoint": GDC_API_BASE,
            "filters": _query_filters(),
            "fields": REQUEST_FIELDS.split(","),
            "format": "JSON",
            "sort": "file_id:asc",
            "page_size": self.page_size,
        }
        canonical_query = json.dumps(query_fingerprint, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        blockers = []
        status = "metadata_manifest_ready"
        common_data_releases = []
        selected_common_data_release = None
        if exclusion_blocker is not None:
            blockers.append(exclusion_blocker)
            status = "blocked_metadata_exclusion_policy"
        else:
            if len(workflow_versions) != 1:
                blockers.append("workflow_version_heterogeneous")
            available = [row.get("available_releases") for row in selected]
            if available and all(isinstance(item, list) and item for item in available):
                intersection = set(available[0])
                for item in available[1:]:
                    intersection &= set(item)
                common_data_releases = sorted(intersection, key=_release_key)
                if not common_data_releases:
                    blockers.append("no_common_gdc_data_release")
                else:
                    selected_common_data_release = common_data_releases[-1]
            elif len(release_values) != 1:
                blockers.append("data_release_compatibility_requires_human_review")
            if blockers:
                status = "paused_workflow_or_release_compatibility"
        if selected_bytes > MAX_CONTENT_BYTES:
            blockers.append("selected_content_exceeds_6gib")
            status = "paused_over_6gib"
        return {
            "schema_version": 1,
            "protocol": "SPEC-935-R934",
            "scope": "gdc_files_metadata_only",
            "generated_at": self.clock(),
            "query": {
                "endpoint": GDC_API_BASE,
                "filters": _query_filters(),
                "fields": REQUEST_FIELDS.split(","),
                "sort": "file_id:asc",
                "query_sha256": hashlib.sha256(canonical_query.encode("utf-8")).hexdigest(),
                "pagination_total_field": "data.pagination.total",
                "page_count": len(pages),
                "pages": pages,
                "hits_total": total,
                "unique_file_ids": len(records),
            },
            "query_fingerprint": query_fingerprint,
            "query_sha256": hashlib.sha256(canonical_query.encode("utf-8")).hexdigest(),
            "hits_total": total,
            "unique_file_ids": len(records),
            "page_count": len(pages),
            "sample_type_counts": {
                "Primary Tumor": sum(1 for row in normalized if row["relationship"]["sample_type"] == "Primary Tumor"),
                "Solid Tissue Normal": sum(1 for row in normalized if row["relationship"]["sample_type"] == "Solid Tissue Normal"),
            },
            "selected_file_count": len(selected),
            "selected_bytes": selected_bytes,
            "max_content_bytes": MAX_CONTENT_BYTES,
            "workflow_versions": workflow_versions,
            "data_release_values": release_values,
            "data_release_values_raw": release_values_raw,
            "common_data_releases": common_data_releases,
            "selected_common_data_release": selected_common_data_release,
            "authorized_exclusions": authorized_exclusions,
            "status": status,
            "blockers": blockers,
            "download_eligible": status == "metadata_manifest_ready",
            "cohort_query_sent": True,
            "file_content_downloaded": False,
            "controlled_accessed": False,
            "analysis_executed": False,
            "files": sorted(normalized, key=lambda row: row["file_id"]),
        }

    def _write_manifest(self, manifest):
        payload = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()
        sidecar_payload = f"{digest}\n".encode("ascii")
        directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        if not getattr(os, "O_DIRECTORY", 0) or not getattr(os, "O_NOFOLLOW", 0):
            raise GDCInventoryError("safe_directory_open_unavailable")
        root_fd = os.open(self.root, directory_flags)
        outputs_fd = None
        manifest_dir_fd = None
        temporary_names = []
        try:
            try:
                outputs_fd = os.open("outputs", directory_flags, dir_fd=root_fd)
            except FileNotFoundError:
                os.mkdir("outputs", 0o755, dir_fd=root_fd)
                outputs_fd = os.open("outputs", directory_flags, dir_fd=root_fd)
            try:
                manifest_dir_fd = os.open("core-r934", directory_flags, dir_fd=outputs_fd)
            except FileNotFoundError:
                os.mkdir("core-r934", 0o755, dir_fd=outputs_fd)
                manifest_dir_fd = os.open("core-r934", directory_flags, dir_fd=outputs_fd)

            def write_temporary(prefix, content):
                name = prefix + secrets.token_hex(16) + ".tmp"
                descriptor = os.open(
                    name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                    dir_fd=manifest_dir_fd,
                )
                temporary_names.append(name)
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                return name

            manifest_temporary = write_temporary(".gdc-manifest-", payload)
            sidecar_temporary = write_temporary(".gdc-manifest-sha256-", sidecar_payload)
            # Sidecar first: if interrupted before manifest replacement, the
            # previous manifest will not match the new digest and fails closed.
            os.replace(
                sidecar_temporary,
                "gdc-manifest.json.sha256",
                src_dir_fd=manifest_dir_fd,
                dst_dir_fd=manifest_dir_fd,
            )
            temporary_names.remove(sidecar_temporary)
            os.replace(
                manifest_temporary,
                "gdc-manifest.json",
                src_dir_fd=manifest_dir_fd,
                dst_dir_fd=manifest_dir_fd,
            )
            temporary_names.remove(manifest_temporary)
            os.fsync(manifest_dir_fd)
        finally:
            if manifest_dir_fd is not None:
                for name in temporary_names:
                    try:
                        os.unlink(name, dir_fd=manifest_dir_fd)
                    except FileNotFoundError:
                        pass
            if manifest_dir_fd is not None:
                os.close(manifest_dir_fd)
            if outputs_fd is not None:
                os.close(outputs_fd)
            os.close(root_fd)
        return self.output_path

    def run(self):
        """Fetch only fixed GDC metadata pages and persist a status manifest."""
        try:
            records, total, pages = self._collect_pages()
            first_fingerprint = self._metadata_fingerprint(records)
            verification_records, verification_total, verification_pages = self._collect_pages()
            verification_fingerprint = self._metadata_fingerprint(verification_records)
            if verification_total != total or verification_fingerprint != first_fingerprint:
                raise GDCInventoryError("metadata_changed_between_passes")
            manifest = self._build_manifest(records, total, pages)
            manifest["metadata_passes"] = 2
            manifest["snapshot_reconciliation"] = {
                "stable": True,
                "first_sha256": first_fingerprint,
                "second_sha256": verification_fingerprint,
                "verification_page_count": len(verification_pages),
                "sort": "file_id:asc",
            }
        except (GDCInventoryError, OSError, ValueError, TypeError, KeyError) as exc:
            reason = exc.code if isinstance(exc, GDCInventoryError) else (str(exc) or type(exc).__name__)
            blocker = {"code": reason}
            if isinstance(exc, GDCInventoryError) and exc.details:
                blocker.update(exc.details)
            if reason == "file_not_open_and_released":
                blocked_status = "blocked_file_access_or_state"
            elif reason in {"file_id_id_mismatch", "file_id_missing"}:
                blocked_status = "blocked_file_identity"
            elif reason in {
                "file_size_missing_or_invalid", "md5sum_missing_or_invalid", "file_name_missing",
                "workflow_or_release_metadata_missing", "analysis_metadata_malformed",
                "version_detail_fetcher_unavailable", "version_metadata_ids_incomplete",
                "version_metadata_id_missing", "version_metadata_id_unexpected_or_duplicate",
                "version_metadata_shape_invalid", "version_metadata_latest_id_mismatch",
                "version_metadata_latest_version_invalid", "version_metadata_latest_values_invalid",
                "version_metadata_content_metadata_mismatch", "version_metadata_release_list_invalid",
            }:
                blocked_status = "blocked_missing_or_invalid_integrity_metadata"
            elif "file_release_metadata" in reason or "file_version_not_latest" in reason:
                blocked_status = "paused_workflow_or_release_compatibility"
            elif any(token in reason for token in ("relationship", "case_", "sample_", "aliquot_")):
                blocked_status = "blocked_ambiguous_association"
            elif "pagination" in reason or "page_" in reason or "duplicate_file_id" in reason or "file_id_sort" in reason:
                blocked_status = "blocked_pagination_or_duplicate_file"
            elif "metadata_changed" in reason:
                blocked_status = "blocked_metadata_changed_between_passes"
            elif "warning" in reason:
                blocked_status = "blocked_api_warning"
            else:
                blocked_status = "blocked"
            manifest = {
                "schema_version": 1,
                "protocol": "SPEC-935-R934",
                "scope": "gdc_files_metadata_only",
                "generated_at": self.clock(),
                "status": blocked_status,
                "blockers": [blocker],
                "download_eligible": False,
                "cohort_query_sent": True,
                "file_content_downloaded": False,
                "controlled_accessed": False,
                "analysis_executed": False,
            }
        self._write_manifest(manifest)
        return manifest


def main() -> int:
    """Run the pre-authorized metadata-only inventory with the fixed repo target."""
    manifest = GDCMetadataInventory().run()
    public_result = {
        "status": manifest.get("status"),
        "hits_total": manifest.get("hits_total"),
        "unique_file_ids": manifest.get("unique_file_ids"),
        "selected_file_count": manifest.get("selected_file_count"),
        "selected_bytes": manifest.get("selected_bytes"),
        "download_eligible": manifest.get("download_eligible", False),
        "manifest_path": str(GDCMetadataInventory().output_path),
        "file_content_downloaded": False,
        "analysis_executed": False,
    }
    print(json.dumps(public_result, ensure_ascii=False, indent=2))
    return 0 if manifest.get("status") == "metadata_manifest_ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
