"""R935: inventário GDC metadata-only; os testes usam fixtures e nunca a rede."""
import json
import hashlib
import re
from pathlib import Path
from urllib.request import Request
from urllib.parse import parse_qs, urlparse

import pytest

from integrations.gdc_metadata_inventory import (
    GDC_API_BASE,
    GDCMetadataInventory,
    GDCInventoryError,
    NoRedirectHandler,
    MAX_CONTENT_BYTES,
    build_request_url,
)


def hit(
    file_id="file-1",
    *,
    patient="TCGA-AB-1234",
    sample_type="Primary Tumor",
    sample_id="sample-1",
    sample_barcode=None,
    aliquot_id="aliquot-1",
    aliquot_barcode=None,
    size=1000,
    access="open",
    state="released",
    workflow_version="wf-5",
    data_release="45.0 - 46.0",
    md5="0123456789abcdef0123456789abcdef",
):
    if sample_barcode is None:
        sample_code = "01A" if sample_type == "Primary Tumor" else "11A"
        sample_barcode = f"{patient}-{sample_code}"
    if aliquot_barcode is None:
        aliquot_barcode = f"{sample_barcode}-01R-0000-01"
    return {
        "file_id": file_id,
        "id": file_id,
        "file_name": f"{file_id}.rna_seq.augmented_star_gene_counts.tsv",
        "file_size": size,
        "md5sum": md5,
        "access": access,
        "state": state,
        "data_category": "Transcriptome Profiling",
        "data_type": "Gene Expression Quantification",
        "analysis": {"workflow_type": "STAR - Counts", "workflow_version": workflow_version},
        "version": "1",
        "data_release": data_release,
        "cases": [
            {
                "case_id": f"case-{patient}",
                "submitter_id": patient,
                "project": {"project_id": "TCGA-KIRC"},
                "samples": [
                    {
                        "sample_id": sample_id,
                        "submitter_id": sample_barcode,
                        "sample_type": sample_type,
                        "portions": [
                            {"analytes": [{"aliquots": [
                                {"aliquot_id": aliquot_id, "submitter_id": aliquot_barcode}
                            ]}]}
                        ],
                    }
                ],
            }
        ],
    }


def page(offset, size, rows, total=None, warnings=None):
    return {
        "data": {
            "hits": rows,
            "pagination": {
                "from": offset,
                "size": size,
                "sort": "None",
            "count": len(rows),
                "total": len(rows) if total is None else total,
            },
        },
        "warnings": warnings or {},
    }


def test_query_is_fixed_open_released_and_metadata_only():
    url = build_request_url(offset=0, size=100)
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    assert parsed.netloc == "api.gdc.cancer.gov"
    assert parsed.path == "/files"
    filters = json.loads(params["filters"][0])
    serialized = json.dumps(filters, sort_keys=True)
    for value in ("TCGA-KIRC", "Transcriptome Profiling", "Gene Expression Quantification", "STAR - Counts", "open", "released"):
        assert value in serialized
    fields = params["fields"][0].split(",")
    assert "files.file_id" in fields or "file_id" in fields
    assert "files.file_size" in fields or "file_size" in fields
    assert "cases.samples.portions.analytes.aliquots.submitter_id" in fields
    assert "version" not in fields and "data_release" not in fields
    assert params.get("sort") == ["file_id:asc"]
    assert GDC_API_BASE == "https://api.gdc.cancer.gov/files"
    assert MAX_CONTENT_BYTES == 6 * 1024**3
    assert "/data" not in parsed.path
    preflight_path = Path(__file__).resolve().parents[1] / "outputs/core-r934/gdc-query-preflight.json"
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    sample = preflight["response_corrected_query"]["sample_record"]
    assert sample["version"] and sample["data_release"]
    assert preflight["response_corrected_query"]["warnings"] == {}
    handler = NoRedirectHandler()
    try:
        handler.redirect_request(
            Request("https://api.gdc.cancer.gov/files"), None, 302,
            "Found", {}, "https://example.invalid/data",
        )
    except GDCInventoryError as exc:
        assert str(exc) == "redirect_blocked"
    else:
        raise AssertionError("redirect was not refused")


def test_pagination_is_reconciled_by_unique_file_id(tmp_path):
    rows = [hit(file_id="file-1"), hit(file_id="file-2", patient="TCGA-CD-5678", sample_id="sample-2", aliquot_id="aliquot-2")]

    def fetch(offset, size, _url):
        return page(offset, size, rows[offset:offset + size], total=2)

    inventory = GDCMetadataInventory(root=tmp_path, page_size=1, page_fetcher=fetch)
    manifest = inventory.run()
    assert manifest.get("hits_total") == 2
    assert manifest["unique_file_ids"] == 2
    assert manifest["page_count"] == 2
    assert manifest.get("metadata_passes") == 2
    assert manifest["snapshot_reconciliation"]["stable"] is True
    assert len(manifest["files"]) == 2
    assert manifest["selected_bytes"] == 2000
    assert manifest["download_eligible"] is True

    def duplicate_page(offset, size, _url):
        return page(offset, size, [rows[0]], total=2)

    duplicate_manifest = GDCMetadataInventory(root=tmp_path, page_size=1, page_fetcher=duplicate_page).run()
    assert duplicate_manifest["status"] == "blocked_pagination_or_duplicate_file"
    assert duplicate_manifest["download_eligible"] is False

    def wrong_page_size(offset, size, _url):
        response = page(offset, size, [rows[0]], total=1)
        response["data"]["pagination"]["size"] = size + 1
        return response

    wrong_size_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=wrong_page_size).run()
    assert wrong_size_manifest["status"] == "blocked_pagination_or_duplicate_file"
    assert wrong_size_manifest["download_eligible"] is False

    request_count = 0

    def changing_metadata(offset, size, _url):
        nonlocal request_count
        current_pass = request_count // 2
        request_count += 1
        page_rows = rows[offset:offset + size]
        if current_pass == 1 and offset == 0:
            page_rows = [hit(file_id="file-1", size=9999)]
        return page(offset, size, page_rows, total=2)

    changed = GDCMetadataInventory(root=tmp_path, page_size=1, page_fetcher=changing_metadata).run()
    assert changed["status"] == "blocked_metadata_changed_between_passes"
    assert changed["download_eligible"] is False

    def bad_page_size(offset, size, _url):
        response = page(offset, size, [rows[0]], total=1)
        response["data"]["pagination"]["size"] = size + 1
        return response

    bad_page = GDCMetadataInventory(root=tmp_path, page_fetcher=bad_page_size).run()
    assert bad_page["status"] == "blocked_pagination_or_duplicate_file"
    assert bad_page["download_eligible"] is False

    unsorted_rows = [
        hit(file_id="z-file", patient="TCGA-ZZ-9999", sample_id="sample-z", aliquot_id="aliquot-z"),
        hit(file_id="a-file", patient="TCGA-AA-0001", sample_id="sample-a", aliquot_id="aliquot-a"),
    ]

    def unsorted_page(offset, size, _url):
        return page(offset, size, unsorted_rows[offset:offset + size], total=2)

    unsorted_manifest = GDCMetadataInventory(root=tmp_path, page_size=1, page_fetcher=unsorted_page).run()
    assert unsorted_manifest["status"] == "blocked_pagination_or_duplicate_file"
    assert unsorted_manifest["download_eligible"] is False


def test_file_case_sample_aliquot_links_fail_closed(tmp_path):
    malformed = hit()
    malformed["cases"][0]["samples"][0]["portions"] = []

    def fetch(offset, size, _url):
        return page(offset, size, [malformed], total=1)

    manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch).run()
    assert manifest["status"] == "blocked_ambiguous_association"
    assert manifest["download_eligible"] is False
    assert manifest["file_content_downloaded"] is False
    assert "aliquot" in json.dumps(manifest["blockers"]).casefold()
    assert manifest["blockers"][0].get("file_id") == "file-1"

    conflicting = hit()
    second_case = json.loads(json.dumps(conflicting["cases"][0]))
    second_case["submitter_id"] = "TCGA-ZZ-9999"
    conflicting["cases"].append(second_case)

    def fetch_conflicting(offset, size, _url):
        return page(offset, size, [conflicting], total=1)

    conflict_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_conflicting).run()
    assert conflict_manifest["status"] == "blocked_ambiguous_association"
    assert conflict_manifest["download_eligible"] is False

    mismatched_sample_barcode = hit(file_id="file-sample-barcode", sample_barcode="TCGA-ZZ-9999-01A")

    def fetch_mismatched_sample_barcode(offset, size, _url):
        return page(offset, size, [mismatched_sample_barcode], total=1)

    mismatched_sample_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_mismatched_sample_barcode).run()
    assert mismatched_sample_manifest["status"] == "blocked_ambiguous_association"
    assert mismatched_sample_manifest["download_eligible"] is False

    mismatched_aliquot_barcode = hit(file_id="file-aliquot-barcode", aliquot_barcode="TCGA-ZZ-9999-01A-01R-0000-01")

    def fetch_mismatched_aliquot_barcode(offset, size, _url):
        return page(offset, size, [mismatched_aliquot_barcode], total=1)

    mismatched_aliquot_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_mismatched_aliquot_barcode).run()
    assert mismatched_aliquot_manifest["status"] == "blocked_ambiguous_association"
    assert mismatched_aliquot_manifest["download_eligible"] is False

    malformed_sample_barcode = hit(file_id="file-malformed-sample", sample_barcode="TCGA-AB-1234-01AA")

    def fetch_malformed_sample_barcode(offset, size, _url):
        return page(offset, size, [malformed_sample_barcode], total=1)

    malformed_sample_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_malformed_sample_barcode).run()
    assert malformed_sample_manifest["status"] == "blocked_ambiguous_association"
    assert malformed_sample_manifest["download_eligible"] is False

    malformed_aliquot_barcode = hit(file_id="file-malformed-aliquot", aliquot_barcode="TCGA-AB-1234-01A-xx")

    def fetch_malformed_aliquot_barcode(offset, size, _url):
        return page(offset, size, [malformed_aliquot_barcode], total=1)

    malformed_aliquot_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_malformed_aliquot_barcode).run()
    assert malformed_aliquot_manifest["status"] == "blocked_ambiguous_association"
    assert malformed_aliquot_manifest["download_eligible"] is False

    out_of_scope = hit(
        file_id="file-out-of-scope",
        patient="TCGA-EF-9012",
        sample_id="sample-out-of-scope",
        sample_type="Metastatic",
        sample_barcode="TCGA-EF-9012-06A",
        aliquot_id="aliquot-out-of-scope",
    )
    in_scope = hit()

    def fetch_out_of_scope(offset, size, _url):
        return page(offset, size, [in_scope, out_of_scope], total=2)

    out_of_scope_manifest = GDCMetadataInventory(root=tmp_path, page_size=2, page_fetcher=fetch_out_of_scope).run()
    assert out_of_scope_manifest["status"] == "metadata_manifest_ready"
    assert out_of_scope_manifest["selected_file_count"] == 1
    excluded = next(row for row in out_of_scope_manifest["files"] if row["file_id"] == "file-out-of-scope")
    assert excluded["selection_status"] == "excluded_sample_type_out_of_scope"

    alphanumeric_plate = hit(
        file_id="file-plate-alpha",
        patient="TCGA-IJ-7890",
        sample_id="sample-plate-alpha",
        sample_barcode="TCGA-IJ-7890-01A",
        aliquot_id="aliquot-plate-alpha",
        aliquot_barcode="TCGA-IJ-7890-01A-01R-A32O-07",
    )

    def fetch_alphanumeric_plate(offset, size, _url):
        return page(offset, size, [alphanumeric_plate], total=1)

    plate_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_alphanumeric_plate).run()
    assert plate_manifest["status"] == "metadata_manifest_ready"

    mismatched_file_ids = hit(file_id="file-id")
    mismatched_file_ids["id"] = "other-id"

    def fetch_mismatched_file_ids(offset, size, _url):
        return page(offset, size, [mismatched_file_ids], total=1)

    mismatch_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_mismatched_file_ids).run()
    assert mismatch_manifest["status"] == "blocked_file_identity"
    assert mismatch_manifest["download_eligible"] is False

    conflicting_sample = hit()
    duplicate_sample = json.loads(json.dumps(conflicting_sample["cases"][0]["samples"][0]))
    duplicate_sample["sample_type"] = "Solid Tissue Normal"
    conflicting_sample["cases"][0]["samples"].append(duplicate_sample)

    def fetch_conflicting_sample(offset, size, _url):
        return page(offset, size, [conflicting_sample], total=1)

    sample_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_conflicting_sample).run()
    assert sample_manifest["status"] == "blocked_ambiguous_association"
    assert sample_manifest["download_eligible"] is False

    conflicting_aliquot = hit()
    duplicate_aliquot = json.loads(json.dumps(conflicting_aliquot["cases"][0]["samples"][0]["portions"][0]["analytes"][0]["aliquots"][0]))
    duplicate_aliquot["submitter_id"] = "TCGA-DIFFERENT-BARCODE"
    conflicting_aliquot["cases"][0]["samples"][0]["portions"][0]["analytes"][0]["aliquots"].append(duplicate_aliquot)

    def fetch_conflicting_aliquot(offset, size, _url):
        return page(offset, size, [conflicting_aliquot], total=1)

    aliquot_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_conflicting_aliquot).run()
    assert aliquot_manifest["status"] == "blocked_ambiguous_association"
    assert aliquot_manifest["download_eligible"] is False


def test_file_metadata_and_checksums_are_validated(tmp_path):
    bad = hit(access="controlled")

    def fetch(offset, size, _url):
        return page(offset, size, [bad], total=1)

    manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch).run()
    assert manifest["status"] == "blocked_file_access_or_state"
    assert manifest["download_eligible"] is False
    assert manifest["file_content_downloaded"] is False

    invalid_md5 = hit(file_id="file-md5", md5="not-a-checksum")

    def fetch_invalid(offset, size, _url):
        return page(offset, size, [invalid_md5], total=1)

    invalid_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_invalid).run()
    assert invalid_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"
    assert invalid_manifest["download_eligible"] is False

    bad_release = hit(file_id="file-release")
    bad_release["data_release"] = ["45.0"]

    def fetch_bad_release(offset, size, _url):
        return page(offset, size, [bad_release], total=1)

    bad_release_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_bad_release).run()
    assert bad_release_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"
    bad_release_blockers = json.dumps(bad_release_manifest["blockers"])
    assert "file-release" in bad_release_blockers
    assert "data_release" in bad_release_blockers


def test_missing_default_version_fields_use_bounded_versions_metadata(tmp_path):
    file_id = "000d81dd-9ba4-4852-9090-2bf22f6483f0"
    incomplete = hit(file_id=file_id)
    incomplete["version"] = None
    incomplete["data_release"] = None

    def fetch_page(offset, size, _url):
        return page(offset, size, [incomplete], total=1)

    def fetch_versions(file_ids):
        assert file_ids == [file_id]
        return {
            file_id: {
                "id": file_id,
                "latest_id": file_id,
                "version": "1",
                "latest_version": "1",
                "md5": incomplete["md5sum"],
                "size": incomplete["file_size"],
                "latest_md5": incomplete["md5sum"],
                "latest_size": incomplete["file_size"],
                "latest_release": ["45.0", "46.0"],
            }
        }

    manifest = GDCMetadataInventory(
        root=tmp_path,
        page_fetcher=fetch_page,
        version_detail_fetcher=fetch_versions,
    ).run()
    assert manifest["status"] == "metadata_manifest_ready"
    selected = next(row for row in manifest["files"] if row["file_id"] == file_id)
    assert selected["version"] == "1"
    assert selected["data_release"] == "45.0 - 46.0"
    assert selected["version_metadata_source"] == "files_versions_api"
    assert manifest["download_eligible"] is True

    def run_with_version_details(record, details):
        def fetch_record(offset, size, _url):
            return page(offset, size, [record], total=1)

        return GDCMetadataInventory(
            root=tmp_path,
            page_fetcher=fetch_record,
            version_detail_fetcher=lambda ids: {ids[0]: details},
        ).run()

    wrong_latest_id = dict(fetch_versions([file_id])[file_id])
    wrong_latest_id["latest_id"] = "00000000-0000-0000-0000-000000000000"
    wrong_id_manifest = run_with_version_details(incomplete, wrong_latest_id)
    assert wrong_id_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"

    changed_checksum = dict(fetch_versions([file_id])[file_id])
    changed_checksum["latest_md5"] = "f" * 32
    checksum_manifest = run_with_version_details(incomplete, changed_checksum)
    assert checksum_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"

    malformed_releases = dict(fetch_versions([file_id])[file_id])
    malformed_releases["latest_release"] = ["not-a-release"]
    release_manifest = run_with_version_details(incomplete, malformed_releases)
    assert release_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"

    version_conflict_record = hit(file_id=file_id)
    version_conflict_record["data_release"] = None
    stale_latest_version = dict(fetch_versions([file_id])[file_id])
    stale_latest_version["latest_version"] = "2"
    stale_latest_version["version"] = "2"
    conflict_manifest = run_with_version_details(version_conflict_record, stale_latest_version)
    assert conflict_manifest["status"] == "paused_workflow_or_release_compatibility"

    malformed_release = hit(file_id="file-bad-release-format", data_release="unknown")

    def fetch_malformed_release(offset, size, _url):
        return page(offset, size, [malformed_release], total=1)

    malformed_release_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_malformed_release).run()
    assert malformed_release_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"

    integer_release = hit(file_id="file-release-integer", data_release="45")

    def fetch_integer_release(offset, size, _url):
        return page(offset, size, [integer_release], total=1)

    integer_release_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_integer_release).run()
    assert integer_release_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"

    malformed_release = hit(file_id="file-release-format", data_release="unknown")

    def fetch_malformed_release(offset, size, _url):
        return page(offset, size, [malformed_release], total=1)

    malformed_release_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_malformed_release).run()
    assert malformed_release_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"

    blank_version = hit(file_id="file-version", data_release="45.0")
    blank_version["version"] = "  "

    def fetch_blank_version(offset, size, _url):
        return page(offset, size, [blank_version], total=1)

    blank_version_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_blank_version).run()
    assert blank_version_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"

    malformed_version = hit(file_id="file-version-format", data_release="45.0")
    malformed_version["version"] = "v1"

    def fetch_malformed_version(offset, size, _url):
        return page(offset, size, [malformed_version], total=1)

    malformed_version_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_malformed_version).run()
    assert malformed_version_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"

    mismatched_ids = hit(file_id="file-a")
    mismatched_ids["id"] = "file-b"

    def fetch_mismatched_ids(offset, size, _url):
        return page(offset, size, [mismatched_ids], total=1)

    mismatched_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_mismatched_ids).run()
    assert mismatched_manifest["status"] == "blocked_file_identity"

    malformed_analysis = hit(file_id="file-analysis")
    malformed_analysis["analysis"] = []

    def fetch_malformed_analysis(offset, size, _url):
        return page(offset, size, [malformed_analysis], total=1)

    malformed_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_malformed_analysis).run()
    assert malformed_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"

    out_of_scope = hit(
        file_id="file-out-of-scope-no-release",
        patient="TCGA-GH-3456",
        sample_id="sample-out-of-scope-no-release",
        sample_type="Metastatic",
        sample_barcode="TCGA-GH-3456-06A",
        aliquot_id="aliquot-out-of-scope-no-release",
    )
    out_of_scope["version"] = None
    out_of_scope["data_release"] = None
    out_of_scope["analysis"]["workflow_version"] = None
    out_of_scope["file_size"] = None
    out_of_scope["md5sum"] = None

    def fetch_out_of_scope_without_download_metadata(offset, size, _url):
        return page(offset, size, [hit(), out_of_scope], total=2)

    out_of_scope_manifest = GDCMetadataInventory(root=tmp_path, page_size=2, page_fetcher=fetch_out_of_scope_without_download_metadata).run()
    assert out_of_scope_manifest["status"] == "metadata_manifest_ready"
    assert out_of_scope_manifest["selected_file_count"] == 1

    def fetch_warning(offset, size, _url):
        return page(offset, size, [hit()], total=1, warnings={"fields": "unrecognized"})

    warning_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_warning).run()
    assert warning_manifest["status"] == "blocked_api_warning"

    def missing_warning_field(offset, size, _url):
        response = page(offset, size, [hit()], total=1)
        response.pop("warnings")
        return response

    missing_warning_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=missing_warning_field).run()
    assert missing_warning_manifest["status"] == "blocked_api_warning"

    def malformed_warning(offset, size, _url):
        response = page(offset, size, [hit()], total=1)
        response["warnings"] = []
        return response

    malformed_warning_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=malformed_warning).run()
    assert malformed_warning_manifest["status"] == "blocked_api_warning"

    malformed_analysis = hit(file_id="file-analysis")
    malformed_analysis["analysis"] = []

    def malformed_analysis_page(offset, size, _url):
        return page(offset, size, [malformed_analysis], total=1)

    malformed_analysis_manifest = GDCMetadataInventory(root=tmp_path, page_fetcher=malformed_analysis_page).run()
    assert malformed_analysis_manifest["status"] == "blocked_missing_or_invalid_integrity_metadata"


def test_budget_and_version_compatibility_gate_content(tmp_path):
    exactly_at_budget = hit(file_id="file-at-6gib", size=MAX_CONTENT_BYTES)

    def fetch_at_budget(offset, size, _url):
        return page(offset, size, [exactly_at_budget], total=1)

    at_budget = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_at_budget).run()
    assert at_budget["selected_bytes"] == 6 * 1024**3
    assert at_budget["status"] == "metadata_manifest_ready"
    assert at_budget["download_eligible"] is True

    too_large = hit(size=MAX_CONTENT_BYTES + 1)

    def fetch_large(offset, size, _url):
        return page(offset, size, [too_large], total=1)

    over_budget = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch_large).run()
    assert over_budget["status"] == "paused_over_6gib"
    assert over_budget["download_eligible"] is False
    assert "selected_content_exceeds_6gib" in over_budget["blockers"]

    other_workflow = hit(file_id="file-wf", patient="TCGA-CD-5678", sample_id="sample-wf", aliquot_id="aliquot-wf", workflow_version="wf-other")
    rows = [hit(), other_workflow]

    def fetch_mixed(offset, size, _url):
        return page(offset, size, rows[offset:offset + size], total=2)

    mixed = GDCMetadataInventory(root=tmp_path, page_size=2, page_fetcher=fetch_mixed).run()
    assert mixed["status"] == "paused_workflow_or_release_compatibility"
    assert mixed["download_eligible"] is False

    other_release = hit(file_id="file-release-2", patient="TCGA-EF-9012", sample_id="sample-release-2", aliquot_id="aliquot-release-2", data_release="44.0")
    release_rows = [hit(), other_release]

    def fetch_mixed_release(offset, size, _url):
        return page(offset, size, release_rows[offset:offset + size], total=2)

    mixed_release = GDCMetadataInventory(root=tmp_path, page_size=2, page_fetcher=fetch_mixed_release).run()
    assert mixed_release["status"] == "paused_workflow_or_release_compatibility"
    assert mixed_release["download_eligible"] is False

    equivalent_release_spacing = [
        hit(file_id="file-release-compact", patient="TCGA-MN-5678", sample_id="sample-release-compact", aliquot_id="aliquot-release-compact", data_release="45.0-46.0"),
        hit(file_id="file-release-spaced", patient="TCGA-KL-1234", sample_id="sample-release-spaced", aliquot_id="aliquot-release-spaced", data_release="45.0 - 46.0"),
    ]

    def fetch_equivalent_releases(offset, size, _url):
        return page(offset, size, equivalent_release_spacing[offset:offset + size], total=2)

    equivalent_manifest = GDCMetadataInventory(root=tmp_path, page_size=2, page_fetcher=fetch_equivalent_releases).run()
    assert equivalent_manifest["status"] == "metadata_manifest_ready"

    valid_different_file_versions = [hit(), hit(file_id="file-v2", patient="TCGA-CD-5678", sample_id="sample-v2", aliquot_id="aliquot-v2")]
    valid_different_file_versions[1]["version"] = "2"

    def fetch_versions(offset, size, _url):
        return page(offset, size, valid_different_file_versions[offset:offset + size], total=2)

    versions = GDCMetadataInventory(root=tmp_path, page_size=2, page_fetcher=fetch_versions).run()
    assert versions["status"] == "metadata_manifest_ready"
    assert versions["download_eligible"] is True


def test_operator_authorized_outlier_is_excluded_with_provenance_rationale(tmp_path):
    outlier_id = "2b0106c5-7e32-423b-957f-06c9f2e7751b"
    primary_workflow = "5d8c131bbff59fb0c969217fc1d44e6d1503cd1f"
    outlier_workflow = "5a02c12930eb23436322a7494047b907b97570c5"
    primary_releases = [
        "32.0", "33.0", "33.1", "34.0", "35.0", "36.0", "37.0", "38.0",
        "39.0", "40.0", "41.0", "42.0", "43.0", "44.0", "45.0", "46.0",
    ]
    outlier_releases = primary_releases[5:]
    primary = hit(
        file_id="canonical-file",
        patient="TCGA-AB-1234",
        sample_id="sample-primary",
        aliquot_id="aliquot-primary",
        workflow_version=primary_workflow,
        data_release="32.0 - 46.0",
    )
    outlier = hit(
        file_id=outlier_id,
        patient="TCGA-CD-5678",
        sample_id="sample-authorized-outlier",
        aliquot_id="aliquot-authorized-outlier",
        workflow_version=outlier_workflow,
        data_release="36.0 - 46.0",
        size=4_265_635,
    )
    rows = sorted([primary, outlier], key=lambda row: row["file_id"])
    rows_by_id = {row["file_id"]: row for row in rows}
    release_lists = {"canonical-file": primary_releases, outlier_id: outlier_releases}

    def fetch_page(offset, size, _url):
        return page(offset, size, rows[offset:offset + size], total=2)

    def fetch_versions(file_ids):
        return {
            file_id: {
                "id": file_id,
                "latest_id": file_id,
                "version": "1",
                "latest_version": "1",
                "md5": rows_by_id[file_id]["md5sum"],
                "size": rows_by_id[file_id]["file_size"],
                "latest_md5": rows_by_id[file_id]["md5sum"],
                "latest_size": rows_by_id[file_id]["file_size"],
                "latest_release": release_lists[file_id],
            }
            for file_id in file_ids
        }

    manifest = GDCMetadataInventory(
        root=tmp_path,
        page_fetcher=fetch_page,
        version_detail_fetcher=fetch_versions,
    ).run()
    assert manifest["status"] == "metadata_manifest_ready"
    assert manifest["download_eligible"] is True
    assert manifest["selected_file_count"] == 1
    assert manifest["selected_bytes"] == primary["file_size"]
    assert manifest["workflow_versions"] == [primary_workflow]
    assert manifest["data_release_values"] == ["32.0-46.0"]
    assert manifest["common_data_releases"] == primary_releases
    assert manifest["selected_common_data_release"] == "46.0"
    excluded = next(row for row in manifest["files"] if row["file_id"] == outlier_id)
    assert excluded["selection_status"] == "excluded_workflow_version_incompatible"
    assert excluded["exclusion_reason"] == "operator_authorized_workflow_version_incompatibility"
    assert excluded["workflow_version"] == outlier_workflow
    assert excluded["data_release_normalized"] == "36.0-46.0"
    assert excluded["available_releases"] == outlier_releases
    assert excluded["file_size"] == 4_265_635
    rationale = excluded["exclusion_rationale"].casefold()
    assert "5a02c12930eb23436322a7494047b907b97570c5" in rationale
    assert "36.0-46.0" in rationale
    assert "processamento" in rationale and "variação biológica" in rationale
    assert "antes de examinar expressão ou desfecho" in rationale
    assert "não afirma que o arquivo seja inválido" in rationale
    assert "não é motivo de exclusão" in rationale
    assert manifest["authorized_exclusions"] == [{
        "file_id": outlier_id,
        "workflow_version": outlier_workflow,
        "data_release": "36.0-46.0",
        "latest_release": outlier_releases,
        "authorized_on": "2026-10-21",
        "decision_basis": "workflow_version",
        "rationale": excluded["exclusion_rationale"],
    }]
    assert manifest["file_content_downloaded"] is False
    assert manifest["analysis_executed"] is False

    changed_outlier = dict(outlier)
    changed_outlier["analysis"] = dict(outlier["analysis"], workflow_version="unexpected-workflow")
    changed_rows = sorted([primary, changed_outlier], key=lambda row: row["file_id"])
    changed_by_id = {row["file_id"]: row for row in changed_rows}

    def fetch_changed_metadata(offset, size, _url):
        return page(offset, size, changed_rows[offset:offset + size], total=2)

    def fetch_changed_versions(file_ids):
        return {
            file_id: {
                "id": file_id,
                "latest_id": file_id,
                "version": "1",
                "latest_version": "1",
                "md5": changed_by_id[file_id]["md5sum"],
                "size": changed_by_id[file_id]["file_size"],
                "latest_md5": changed_by_id[file_id]["md5sum"],
                "latest_size": changed_by_id[file_id]["file_size"],
                "latest_release": release_lists[file_id],
            }
            for file_id in file_ids
        }

    changed_manifest = GDCMetadataInventory(
        root=tmp_path,
        page_fetcher=fetch_changed_metadata,
        version_detail_fetcher=fetch_changed_versions,
    ).run()
    assert changed_manifest["status"] == "blocked_metadata_exclusion_policy"
    assert changed_manifest["download_eligible"] is False
    assert changed_manifest["blockers"][0]["code"] == "authorized_exclusion_metadata_mismatch"

    alternate = hit(
        file_id="alternate-file",
        patient="TCGA-CD-5678",
        sample_id="sample-alternate",
        aliquot_id="aliquot-alternate",
        aliquot_barcode="TCGA-CD-5678-01A-02R-0000-01",
        workflow_version=primary_workflow,
        data_release="32.0 - 46.0",
    )
    rows_with_alternate = sorted([primary, outlier, alternate], key=lambda row: row["file_id"])
    alternate_by_id = {row["file_id"]: row for row in rows_with_alternate}
    alternate_release_lists = {**release_lists, "alternate-file": primary_releases}

    def fetch_alternate(offset, size, _url):
        return page(offset, size, rows_with_alternate[offset:offset + size], total=3)

    def fetch_alternate_versions(file_ids):
        return {
            file_id: {
                "id": file_id,
                "latest_id": file_id,
                "version": "1",
                "latest_version": "1",
                "md5": alternate_by_id[file_id]["md5sum"],
                "size": alternate_by_id[file_id]["file_size"],
                "latest_md5": alternate_by_id[file_id]["md5sum"],
                "latest_size": alternate_by_id[file_id]["file_size"],
                "latest_release": alternate_release_lists[file_id],
            }
            for file_id in file_ids
        }

    alternate_manifest = GDCMetadataInventory(
        root=tmp_path,
        page_fetcher=fetch_alternate,
        version_detail_fetcher=fetch_alternate_versions,
    ).run()
    assert alternate_manifest["status"] == "blocked_metadata_exclusion_policy"
    assert alternate_manifest["download_eligible"] is False
    assert alternate_manifest["blockers"][0]["code"] == "authorized_exclusion_alternative_candidate_present"


def test_data_release_ranges_use_common_latest_release_intersection(tmp_path):
    primary_releases = [
        "32.0", "33.0", "33.1", "34.0", "35.0", "36.0", "37.0", "38.0",
        "39.0", "40.0", "41.0", "42.0", "43.0", "44.0", "45.0", "46.0",
    ]
    overlapping_releases = primary_releases[5:]
    rows = [
        hit(file_id="file-range-1", patient="TCGA-AB-1234", sample_id="sample-range-1", aliquot_id="aliquot-range-1", data_release="32.0 - 46.0"),
        hit(file_id="file-range-2", patient="TCGA-CD-5678", sample_id="sample-range-2", aliquot_id="aliquot-range-2", data_release="36.0 - 46.0"),
    ]
    rows_by_id = {row["file_id"]: row for row in rows}
    releases_by_id = {"file-range-1": primary_releases, "file-range-2": overlapping_releases}

    def fetch_page(offset, size, _url):
        return page(offset, size, rows[offset:offset + size], total=2)

    version_calls = []

    def fetch_versions(file_ids):
        version_calls.extend(file_ids)
        return {
            file_id: {
                "id": file_id,
                "latest_id": file_id,
                "version": "1",
                "latest_version": "1",
                "md5": rows_by_id[file_id]["md5sum"],
                "size": rows_by_id[file_id]["file_size"],
                "latest_md5": rows_by_id[file_id]["md5sum"],
                "latest_size": rows_by_id[file_id]["file_size"],
                "latest_release": releases_by_id[file_id],
            }
            for file_id in file_ids
        }

    overlap_manifest = GDCMetadataInventory(
        root=tmp_path,
        page_size=2,
        page_fetcher=fetch_page,
        version_detail_fetcher=fetch_versions,
    ).run()
    assert version_calls == ["file-range-1", "file-range-2"]
    assert overlap_manifest["status"] == "metadata_manifest_ready"
    assert overlap_manifest["data_release_values"] == ["32.0-46.0", "36.0-46.0"]
    assert overlap_manifest["common_data_releases"] == overlapping_releases
    assert overlap_manifest["selected_common_data_release"] == "46.0"
    assert overlap_manifest["download_eligible"] is True

    disjoint_rows = [
        hit(file_id="file-disjoint-1", patient="TCGA-EF-9012", sample_id="sample-disjoint-1", aliquot_id="aliquot-disjoint-1", data_release="32.0 - 33.0"),
        hit(file_id="file-disjoint-2", patient="TCGA-GH-3456", sample_id="sample-disjoint-2", aliquot_id="aliquot-disjoint-2", data_release="34.0 - 35.0"),
    ]
    disjoint_by_id = {row["file_id"]: row for row in disjoint_rows}
    disjoint_releases = {"file-disjoint-1": ["32.0", "33.0"], "file-disjoint-2": ["34.0", "35.0"]}

    def fetch_disjoint(offset, size, _url):
        return page(offset, size, disjoint_rows[offset:offset + size], total=2)

    def fetch_disjoint_versions(file_ids):
        return {
            file_id: {
                "id": file_id,
                "latest_id": file_id,
                "version": "1",
                "latest_version": "1",
                "md5": disjoint_by_id[file_id]["md5sum"],
                "size": disjoint_by_id[file_id]["file_size"],
                "latest_md5": disjoint_by_id[file_id]["md5sum"],
                "latest_size": disjoint_by_id[file_id]["file_size"],
                "latest_release": disjoint_releases[file_id],
            }
            for file_id in file_ids
        }

    disjoint_manifest = GDCMetadataInventory(
        root=tmp_path,
        page_size=2,
        page_fetcher=fetch_disjoint,
        version_detail_fetcher=fetch_disjoint_versions,
    ).run()
    assert disjoint_manifest["status"] == "paused_workflow_or_release_compatibility"
    assert disjoint_manifest["common_data_releases"] == []
    assert "no_common_gdc_data_release" in disjoint_manifest["blockers"]
    assert disjoint_manifest["download_eligible"] is False


def test_manifest_is_atomic_local_metadata_only_artifact(tmp_path, monkeypatch):
    def fetch(offset, size, _url):
        return page(offset, size, [hit()], total=1)

    inventory = GDCMetadataInventory(root=tmp_path, page_fetcher=fetch)
    manifest = inventory.run()
    output = tmp_path / "outputs/core-r934/gdc-manifest.json"
    assert output.is_file()
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved == manifest
    assert re.fullmatch(r"[0-9a-f]{64}", saved.get("query_sha256", ""))
    sidecar = output.with_suffix(output.suffix + ".sha256")
    assert sidecar.is_file()
    assert sidecar.read_text(encoding="utf-8").strip() == hashlib.sha256(output.read_bytes()).hexdigest()
    assert saved["cohort_query_sent"] is True
    assert saved["file_content_downloaded"] is False
    assert saved["analysis_executed"] is False
    assert "read_counts" not in json.dumps(saved).casefold()
    assert "counts_mat" not in json.dumps(saved).casefold()

    unsafe_root = tmp_path / "unsafe-root"
    unsafe_root.mkdir()
    external_outputs = tmp_path / "external-outputs"
    external_outputs.mkdir()
    (external_outputs / "gdc-manifest.json").write_text("do-not-touch", encoding="utf-8")
    (unsafe_root / "outputs").symlink_to(external_outputs, target_is_directory=True)
    unsafe_inventory = GDCMetadataInventory(root=unsafe_root, page_fetcher=fetch)
    blocked = False
    try:
        unsafe_inventory.run()
    except (OSError, GDCInventoryError):
        blocked = True
    assert blocked
    assert (external_outputs / "gdc-manifest.json").read_text(encoding="utf-8") == "do-not-touch"
    assert not (external_outputs / "core-r934/gdc-manifest.json").exists()

    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")
    monkeypatch.setattr("integrations.gdc_metadata_inventory.secrets.token_hex", lambda _length: "fixed")
    malicious_temp = output.with_name(".gdc-manifest-fixed.tmp")
    malicious_temp.symlink_to(sentinel)
    blocked_temp = False
    try:
        GDCMetadataInventory(root=tmp_path, page_fetcher=fetch).run()
    except FileExistsError:
        blocked_temp = True
    assert blocked_temp
    assert sentinel.read_text(encoding="utf-8") == "preserve"
    assert not output.is_symlink()
