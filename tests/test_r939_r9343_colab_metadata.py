"""R939: contrato estático R934.3; não executa células, API, rede ou downloads."""

import hashlib
import ast
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "artigos/bio/TCGA_KIRC_R934_3_Metadata_Schema_Fix.ipynb"
R934_2 = ROOT / "artigos/bio/TCGA_KIRC_R934_2_Metadata_Only.ipynb"
R934_2_SHA256 = "32dc05cfb729bc7ed1d6a0f9513789e96b2a7551fe8fb7f3a4fbfa13c6668778"
OUTLIER = "2b0106c5-7e32-423b-957f-06c9f2e7751b"


def _notebook():
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))


def _source(notebook, cell_type):
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == cell_type
    )


def test_r9343_is_fresh_nbformat_and_has_no_user_execution_state():
    notebook = _notebook()
    assert notebook.get("nbformat") == 4
    cells = notebook.get("cells")
    assert isinstance(cells, list) and len(cells) >= 20
    assert all(cell.get("execution_count") is None for cell in cells if cell.get("cell_type") == "code")
    assert all(not cell.get("outputs") for cell in cells if cell.get("cell_type") == "code")
    metadata_text = json.dumps([cell.get("metadata", {}) for cell in cells])
    for marker in ('04472429858835237261', 'Prof. Marcelo Claro'):
        assert marker not in metadata_text
    assert R934_2.is_file()
    assert hashlib.sha256(R934_2.read_bytes()).hexdigest() == R934_2_SHA256


def test_all_r9343_python_cells_have_valid_syntax():
    code_cells = [cell for cell in _notebook().get("cells", []) if cell.get("cell_type") == "code"]
    assert code_cells
    for index, cell in enumerate(code_cells):
        ast.parse("".join(cell.get("source", [])), filename=f"R934.3 cell {index}")


def test_all_python_cells_parse_without_execution():
    notebook = _notebook()
    code_cells = [cell for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    assert code_cells
    for index, cell in enumerate(code_cells):
        source = "".join(cell.get("source", []))
        ast.parse(source, filename=f"R934.3-cell-{index}")


def test_files_mapping_and_related_cases_projection_are_separated():
    code = _source(_notebook(), "code")
    start = code.index("def verify_files_schema(")
    end = code.index("def metadata_pages(", start)
    schema_check = code[start:end]
    assert "files.access" in schema_check
    assert "files.file_id" in schema_check
    assert "files.file_name" in schema_check
    assert "files.analysis.workflow_version" in schema_check
    assert "cases." not in schema_check
    pages = code[end:code.index("def unique_one(", end)]
    assert "cases" in pages
    assert "cases deve ser uma lista" in pages
    assert "arquivo GDC não é objeto JSON" in pages


def test_query_is_open_released_sorted_and_metadata_only():
    code = _source(_notebook(), "code")
    fields = code.split("GDC_FIELDS=[", 1)[1].split("GDC_FILTER=", 1)[0]
    assert "'version'" not in fields
    assert "'data_release'" not in fields
    assert "files.access" in code and "'value':'open'" in code
    assert "files.state" in code and "'value':'released'" in code
    assert "sort" in code and "file_id:asc" in code
    assert "allow_redirects=False" in code
    assert "collect_two_stable_metadata_passes" in code
    assert "pass_label='gdc-pass-1'" in code and "pass_label='gdc-pass-2'" in code
    assert "records_sha256" in code and "snapshot_stable=True" in code
    assert "CONSULTAR_GDC_METADATA=True" in code


def test_common_latest_release_intersection_and_authorized_exclusion():
    code = _source(_notebook(), "code")
    synthetic_tests = code[code.index("def check_metadata_parser():"):code.index("assert check_metadata_parser()")]
    assert "files/versions/" in code
    assert "VERSION_BATCH_SIZE=50" in code or "VERSION_BATCH_SIZE = 50" in code
    assert "latest_release" in code
    assert "set.intersection" in code
    assert OUTLIER in code
    assert "excluded_workflow_version_incompatible" in code
    assert "'decision_basis':'workflow_version'" in code or '"decision_basis":"workflow_version"' in code
    assert "no_common_gdc_data_release" in code
    assert "disjoint_rows" in synthetic_tests and "expect_red(build_manifest" in synthetic_tests
    assert "data_release incompatible" not in code.casefold()


def test_drive_run_is_unique_and_public_bundle_excludes_private_metadata():
    notebook = _notebook()
    code = _source(notebook, "code")
    text = _source(notebook, "markdown").casefold()
    assert "MONTAR_DRIVE=True" in code or "MONTAR_DRIVE = True" in code
    assert "drive.mount('/content/drive')" in code
    assert "RUN_ID" in code and "datetime.now(timezone.utc)" in code
    assert "exist_ok=False" in code
    assert "stage_events.jsonl" in code
    assert "run_artifact_index.json" in code
    assert "artifact_index.json" in code
    assert "/content/drive/MyDrive" in code
    public_dirs = re.search(r"PUBLIC_DIRS\s*=\s*\[(.*?)\]", code, re.DOTALL)
    assert public_dirs is not None
    assert "private_metadata" not in public_dirs.group(1)
    assert "P1_metadata_summary_PUBLIC.json" in code
    assert "R934_auditoria_publica.zip" in code
    assert "R934_auditoria_publica.zip.sha256" in code
    assert "private_metadata não entra no zip público" in text


def test_content_download_is_disabled_and_gates_are_not_promoted():
    code = _source(_notebook(), "code")
    text = _source(_notebook(), "markdown").casefold()
    assert "EXECUTAR_DOWNLOADS=False" in code
    assert "download_open_manifest" not in code
    assert "REVISAO_REGISTRADA=False" in code
    assert "P2_DOWNLOADS_VERIFICADOS=False" in code
    assert "P3_PIPELINE_NESTED_VST_VERIFICADO=False" in code
    assert "P4_ANALISE_REVISADA=False" in code
    assert "p0" in text and "p1" in text and "p2" in text and "p3" in text and "p4" in text
    assert "GDC/data/" not in code


def test_public_reports_are_aggregate_only_and_downloads_disabled():
    code = _source(_notebook(), "code")
    start = code.index("P1_PRELIMINARY_AUDIT=")
    end = code.index("write_json(ROOT/'reports'/'P1_metadata_summary_PUBLIC.json'", start)
    public_summary = code[start:end]
    assert "file_id" not in public_summary
    assert "patient_id" not in public_summary
    assert "CONSULTAR_GDC_METADATA=True" in code
    assert "EXECUTAR_DOWNLOADS=False" in code
    assert "private_metadata" in code
