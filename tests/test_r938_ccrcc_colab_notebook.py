"""R938: contrato estático e guard local do notebook; nenhuma célula Colab é executada."""

import ast
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "artigos/bio/Pacote_Pesquisa_ccRCC_Genomic_Intelligence/Pesquisa_ccRCC_Genomic_Intelligence_Colab.ipynb"
AUTHORIZED_OUTLIER = "2b0106c5-7e32-423b-957f-06c9f2e7751b"
MAX_CONTENT_BYTES = 6 * 1024**3


def _notebook():
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))


def _sources(notebook):
    code = []
    markdown = []
    for cell in notebook.get("cells", []):
        source = "".join(cell.get("source", []))
        (code if cell.get("cell_type") == "code" else markdown).append(source)
    return code, markdown


def _guard_function():
    """Extract and test only the pure manifest validator, never a notebook cell."""
    code, _ = _sources(_notebook())
    tree = ast.parse("\n".join(code))
    function = next(
        (node for node in ast.walk(tree)
         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
         and node.name == "validate_gdc_manifest"),
        None,
    )
    assert function is not None, "notebook needs a pure validate_gdc_manifest guard"
    isolated = ast.Module(body=[function], type_ignores=[])
    namespace = {
        "re": re,
        "MAX_CONTENT_BYTES": MAX_CONTENT_BYTES,
        "AUTHORIZED_OUTLIER": AUTHORIZED_OUTLIER,
    }
    exec(compile(ast.fix_missing_locations(isolated), "<manifest-guard>", "exec"), namespace)
    return namespace["validate_gdc_manifest"]


def _execution_gate_function():
    code, _ = _sources(_notebook())
    tree = ast.parse("\n".join(code))
    function = next(
        (node for node in ast.walk(tree)
         if isinstance(node, ast.FunctionDef)
         and node.name == "validate_colab_execution_gate"),
        None,
    )
    assert function is not None, "notebook needs a separate P0/P1 execution gate"
    isolated = ast.Module(body=[function], type_ignores=[])
    namespace = {}
    exec(compile(ast.fix_missing_locations(isolated), "<execution-gate>", "exec"), namespace)
    return namespace["validate_colab_execution_gate"]


def _valid_manifest():
    selected = {
        "file_id": "selected-file-1",
        "selection_status": "selected_for_manifest",
        "access": "open",
        "state": "released",
        "file_size": 1000,
        "md5sum": "0123456789abcdef0123456789abcdef",
        "workflow_version": "workflow-primary",
        "condition": "tumor",
        "available_releases": ["36.0", "46.0"],
    }
    excluded = {
        "file_id": AUTHORIZED_OUTLIER,
        "selection_status": "excluded_workflow_version_incompatible",
        "exclusion_reason": "operator_authorized_workflow_version_incompatibility",
        "workflow_version": "5a02c12930eb23436322a7494047b907b97570c5",
        "data_release_normalized": "36.0-46.0",
        "exclusion_rationale": (
            "Workflow version distinta; releases comuns existem; a faixa textual de release "
            "não é motivo de exclusão e a decisão ocorreu antes de examinar expressão ou desfecho."
        ),
    }
    return {
        "cohort_query_sent": True,
        "status": "metadata_manifest_ready",
        "download_eligible": True,
        "max_content_bytes": MAX_CONTENT_BYTES,
        "selected_file_count": 1,
        "selected_bytes": 1000,
        "files": [selected, excluded],
        "workflow_versions": ["workflow-primary"],
        "common_data_releases": ["36.0", "46.0"],
        "selected_common_data_release": "46.0",
        "authorized_exclusions": [{
            "file_id": AUTHORIZED_OUTLIER,
            "decision_basis": "workflow_version",
            "authorized_on": "2026-10-21",
            "workflow_version": "5a02c12930eb23436322a7494047b907b97570c5",
            "rationale": excluded["exclusion_rationale"],
        }],
        "file_content_downloaded": False,
        "controlled_accessed": False,
        "analysis_executed": False,
    }


def test_notebook_is_valid_unexecuted_nbformat4():
    notebook = _notebook()
    assert notebook["nbformat"] == 4
    assert isinstance(notebook.get("cells"), list) and notebook["cells"]
    assert all(cell.get("execution_count") is None for cell in notebook["cells"] if cell.get("cell_type") == "code")
    assert all(not cell.get("outputs") for cell in notebook["cells"] if cell.get("cell_type") == "code")


def test_notebook_removes_hidden_r_and_unbounded_download_execution():
    code, _ = _sources(_notebook())
    source = "\n".join(code)
    for forbidden in (
        "R_SCRIPT_B64",
        "GDCdownload(",
        "GDCprepare(",
        "subprocess.run(",
        "INSTALAR_R_E_BIOCONDUCTOR",
        "ROOT.rglob('*')",
    ):
        assert forbidden not in source, f"unsafe or unbounded notebook operation remains: {forbidden}"
    assert "EXECUTAR_GI_REST = False" in source


def test_drive_run_is_timestamped_and_non_overwriting():
    code, markdown = _sources(_notebook())
    source = "\n".join(code)
    text = "\n".join(markdown).casefold()
    assert "MONTAR_DRIVE = True" in source
    assert "drive.mount('/content/drive')" in source
    assert "datetime.now(timezone.utc)" in source
    assert "RUN_ID" in source and "runs" in source
    assert "RUN_DIR.mkdir(parents=True, exist_ok=False)" in source
    assert "stage_events.jsonl" in source
    assert "pilot_path = TABLES_DIR / 'GI_pilot_observed_predictions.tsv'" in source
    assert "pilot.to_csv(pilot_path" in source
    assert "shutil.copy2(MANIFEST_SOURCE, MANIFEST_PATH)" in source
    assert "/content/drive/MyDrive/ccRCC_Genomic_Intelligence" in source
    assert "artifact_index.json" in source
    assert "sha256" in source.casefold()
    assert "execução única" in text or "diretório de execução" in text


def test_manifest_guard_accepts_only_audited_metadata_only_manifest():
    validate = _guard_function()
    manifest = _valid_manifest()
    summary = validate(manifest, sidecar_matches=True)
    assert summary["selected_file_count"] == 1
    assert summary["selected_bytes"] == 1000
    assert summary["selected_common_data_release"] == "46.0"
    assert summary.get("authorized_outlier_basis") == "workflow_version"
    assert summary["file_content_downloaded"] is False


def test_manifest_guard_rejects_paused_or_hash_failure():
    validate = _guard_function()
    paused = _valid_manifest()
    paused["status"] = "paused_workflow_or_release_compatibility"
    paused["download_eligible"] = False
    try:
        validate(paused, sidecar_matches=True)
    except ValueError:
        pass
    else:
        raise AssertionError("paused manifest must fail closed")

    try:
        validate(_valid_manifest(), sidecar_matches=False)
    except ValueError:
        pass
    else:
        raise AssertionError("manifest with a mismatched SHA-256 sidecar must fail closed")

    over_budget = _valid_manifest()
    over_budget["selected_bytes"] = MAX_CONTENT_BYTES + 1
    try:
        validate(over_budget, sidecar_matches=True)
    except ValueError:
        pass
    else:
        raise AssertionError("manifest over 6 GiB must fail closed")

    wrong_exclusion = _valid_manifest()
    wrong_exclusion["files"][1]["workflow_version"] = "workflow-primary"
    wrong_exclusion["authorized_exclusions"][0]["workflow_version"] = "workflow-primary"
    try:
        validate(wrong_exclusion, sidecar_matches=True)
    except ValueError:
        pass
    else:
        raise AssertionError("workflow-version exception must not excuse a matching workflow")


def test_colab_p0_p1_gate_fails_closed_until_human_acceptance():
    gate = _execution_gate_function()
    assert gate("metadata_only", p0_method_accepted=False, p1_human_review_accepted=False, manifest_summary=None) is True
    ready = {
        "status": "metadata_manifest_ready",
        "download_eligible": True,
        "manifest_sha256_verified": True,
        "file_content_downloaded": False,
        "analysis_executed": False,
    }
    for p0, p1, summary in (
        (False, False, ready),
        (True, False, ready),
        (True, True, {"status": "paused_workflow_or_release_compatibility", "download_eligible": False}),
    ):
        try:
            gate("analysis", p0_method_accepted=p0, p1_human_review_accepted=p1, manifest_summary=summary)
        except ValueError:
            pass
        else:
            raise AssertionError("analysis must be blocked until P0/P1 acceptance")
    assert gate("analysis", p0_method_accepted=True, p1_human_review_accepted=True, manifest_summary=ready) is True
    unsealed = dict(ready, manifest_sha256_verified=False)
    try:
        gate("analysis", p0_method_accepted=True, p1_human_review_accepted=True, manifest_summary=unsealed)
    except ValueError:
        pass
    else:
        raise AssertionError("analysis gate must reject a manifest without verified sidecar SHA-256")


def test_notebook_states_primary_estimand_and_current_gates():
    _, markdown = _sources(_notebook())
    text = "\n".join(markdown).casefold()
    for marker in (
        "diferença da auc",
        "5 anos",
        "ic de 95%",
        "tripod+ai",
        "p0",
        "p1",
        "p2",
        "p3",
        "p4",
        "nenhum resultado tcga observado",
        "nenhum arquivo de conteúdo baixado",
    ):
        assert marker in text, f"missing notebook status/estimand statement: {marker}"


def test_genomic_intelligence_pilot_is_separate_from_tcga_measurements():
    _, markdown = _sources(_notebook())
    text = "\n".join(markdown).casefold()
    assert "in silico" in text
    assert "não são medições de rna-seq tcga" in text
    assert "não entram no modelo prognóstico primário" in text
