"""R955: contrato de armazenamento testado em bancos sintéticos temporários."""
from __future__ import annotations

import hashlib
import importlib.util
import sqlite3
import stat
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "PROJETO 1" / "Airam veras" / "datamining" / "airam" / "banco.py"


def banco():
    assert MODULE_PATH.is_file(), "Módulo de armazenamento Airam ainda ausente"
    spec = importlib.util.spec_from_file_location("airam_storage_r955", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_original_sources_are_read_only_and_unchanged(tmp_path):
    module = banco()
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source = source_root / "public.sqlite"
    with sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE source_rows (code TEXT NOT NULL)")
        conn.execute("INSERT INTO source_rows VALUES ('D01')")
    before = sha(source)

    conn = module.open_source_readonly(source, allowed_root=source_root)
    try:
        assert conn.execute("SELECT code FROM source_rows").fetchone()["code"] == "D01"
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("INSERT INTO source_rows VALUES ('D02')")
    finally:
        conn.close()

    assert sha(source) == before
    rejected_relative = False
    try:
        module.open_source_readonly(Path("relative-source.sqlite"), allowed_root=source_root)
    except ValueError:
        rejected_relative = True
    assert rejected_relative, "fonte relativa deve ser recusada em vez de resolvida pelo cwd"


def test_each_scope_has_disjoint_schema(tmp_path):
    module = banco()
    source_root = tmp_path / "originals"
    source_root.mkdir()
    expected = {
        "public_matrix": {"store_meta", "source_asset", "matrix_descriptor"},
        "restricted_observations": {"store_meta", "restricted_source", "student_observation"},
        "aggregate_analytics": {"store_meta", "analysis_run", "aggregate_metric", "claim_evidence"},
    }
    paths = {}
    for scope, tables in expected.items():
        path = tmp_path / scope / "store.sqlite"
        module.initialize_store(path, scope, immutable_roots=[source_root])
        info = module.inspect_store(path, expected_scope=scope)
        assert info["schema_version"] == module.SCHEMA_VERSION
        assert info["scope"] == scope
        assert set(info["tables"]) == tables
        paths[scope] = path

    assert len(set(paths.values())) == 3
    assert "student_observation" not in module.inspect_store(
        paths["public_matrix"], expected_scope="public_matrix"
    )["tables"]
    assert "matrix_descriptor" not in module.inspect_store(
        paths["restricted_observations"], expected_scope="restricted_observations"
    )["tables"]
    assert "student_observation" not in module.inspect_store(
        paths["aggregate_analytics"], expected_scope="aggregate_analytics"
    )["tables"]


def test_store_creation_refuses_sources_and_existing_files(tmp_path):
    module = banco()
    source_root = tmp_path / "immutable"
    source_root.mkdir()
    with pytest.raises(ValueError, match="fonte|imutavel|source"):
        module.initialize_store(
            source_root / "new.sqlite", "public_matrix", immutable_roots=[source_root]
        )

    existing = tmp_path / "existing.sqlite"
    original = b"existing-user-file"
    existing.write_bytes(original)
    with pytest.raises(FileExistsError):
        module.initialize_store(existing, "public_matrix", immutable_roots=[source_root])
    assert existing.read_bytes() == original


@pytest.mark.skipif(__import__("os").name != "posix", reason="ACL do host não é POSIX")
def test_restricted_store_requires_private_posix_directory(tmp_path):
    module = banco()
    source_root = tmp_path / "originals"
    source_root.mkdir()
    path = tmp_path / "private" / "observations.sqlite"
    module.initialize_store(path, "restricted_observations", immutable_roots=[source_root])
    assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    info = module.inspect_store(path, expected_scope="restricted_observations")
    assert "student_observation" in info["tables"]
    assert not {"name", "name_raw", "student_name", "student_number"}.intersection(
        info["columns"]["student_observation"]
    )

    insecure_parent = tmp_path / "shared"
    insecure_parent.mkdir(mode=0o755)
    with pytest.raises(PermissionError, match="privad|permiss"):
        module.initialize_store(insecure_parent / "observations.sqlite", "restricted_observations",
                                immutable_roots=[source_root])
    assert not (insecure_parent / "observations.sqlite").exists()


def test_public_descriptors_have_composite_provenance_keys(tmp_path):
    module = banco()
    source_root = tmp_path / "originals"
    source_root.mkdir()
    path = tmp_path / "public" / "store.sqlite"
    module.initialize_store(path, "public_matrix", immutable_roots=[source_root])
    conn = module.connect_store(path, expected_scope="public_matrix", readonly=False)
    try:
        module.register_public_source(
            conn, source_id="src-1", relative_path="fontes/matriz.pdf",
            source_sha256="a" * 64, source_version="2026.1",
            license_status="not_asserted", source_system="CAEd",
        )
        module.register_matrix_descriptor(
            conn, source_id="src-1", matrix_id="M1", descriptor_code="D01_2EF",
            edition_year=2026, edition_label="Avalie.CE 2026.1", stage="EF", grade=2,
            component="Língua Portuguesa", instrument_type="padrão",
            descriptor_text="Texto de fixture", source_page=1,
        )
        with pytest.raises(sqlite3.IntegrityError):
            module.register_matrix_descriptor(
                conn, source_id="src-1", matrix_id="M1", descriptor_code="D01_2EF",
                edition_year=2026, edition_label="Avalie.CE 2026.1", stage="EF", grade=2,
                component="Língua Portuguesa", instrument_type="padrão",
                descriptor_text="Texto divergente", source_page=1,
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only|imutavel"):
            conn.execute("UPDATE matrix_descriptor SET descriptor_text='mudou'")
        with pytest.raises(sqlite3.IntegrityError, match="append-only|imutavel"):
            conn.execute("UPDATE store_meta SET schema_version=99")
        conn.commit()
    finally:
        conn.close()


def test_public_descriptor_allows_unknown_instrument_type(tmp_path):
    module = banco()
    source_root = tmp_path / "originals"
    source_root.mkdir()
    path = tmp_path / "public" / "store.sqlite"
    module.initialize_store(path, "public_matrix", immutable_roots=[source_root])
    conn = module.connect_store(path, expected_scope="public_matrix", readonly=False)
    try:
        module.register_public_source(
            conn, source_id="src-1", relative_path="fontes/spaece.pdf",
            source_sha256="a" * 64, source_version="legacy-unknown-year",
            license_status="not_asserted", source_system="SPAECE",
        )
        accepted = True
        try:
            module.register_matrix_descriptor(
                conn, source_id="src-1", matrix_id="SPAECE_LP_EF_2", descriptor_code="D01",
                edition_year=None, edition_label=None, stage="EF", grade=2,
                component="Língua Portuguesa", instrument_type=None,
                descriptor_text="Descritor público de fixture", source_page=1,
            )
        except (TypeError, ValueError, sqlite3.IntegrityError):
            accepted = False
        assert accepted, "tipo de instrumento/ano não informado não deve ser inventado"
    finally:
        conn.close()


def test_observations_preserve_missingness_and_block_raw_names(tmp_path):
    module = banco()
    source_root = tmp_path / "originals"
    source_root.mkdir()
    path = tmp_path / "restricted" / "observations.sqlite"
    module.initialize_store(path, "restricted_observations", immutable_roots=[source_root])
    conn = module.connect_store(path, expected_scope="restricted_observations", readonly=False)
    try:
        module.register_restricted_source(
            conn, source_id="rs-1", relative_path="exportacao/arquivo.csv",
            source_sha256="b" * 64, source_version="AV12026",
            lawful_basis="fixture de teste", custodian="fixture", purpose="contrato sintetico",
        )
        module.register_observation(
            conn, source_id="rs-1", source_row=12, local_student_id="a" * 64,
                assessment_id="AV12026", school_year=2, component="LEITURA",
                metric_id="H01", unit="acertos_itens", participation=True,
                availability=False, absence_reason="no_result", numerator=None, denominator=None,
        )
        with pytest.raises(TypeError, match="name_raw"):
            module.register_observation(
                conn, source_id="rs-1", source_row=13, local_student_id="b" * 64,
                assessment_id="AV12026", school_year=2, component="LEITURA",
                metric_id="H01", unit="acertos_itens", participation=True,
                availability=True, numerator=1, denominator=1, name_raw="NÃO ENVIAR",
            )
        with pytest.raises(ValueError, match="zero|ausente|missing|disponibilidade"):
            module.register_observation(
                conn, source_id="rs-1", source_row=14, local_student_id="c" * 64,
                assessment_id="AV12026", school_year=2, component="LEITURA",
                metric_id="H01", unit="acertos_itens", participation=True,
                availability=False, numerator=0, denominator=1,
            )
        rejected_raw_id = False
        try:
            module.register_observation(
                conn, source_id="rs-1", source_row=15, local_student_id="NOME ALUNO",
                assessment_id="AV12026", school_year=2, component="LEITURA",
                metric_id="H01", unit="acertos_itens", participation=True,
                availability=False, absence_reason="no_result",
            )
        except ValueError:
            rejected_raw_id = True
        assert rejected_raw_id, "identificador nominal não deve entrar no store restrito"
    finally:
        conn.close()


def test_aggregate_metrics_suppress_small_cells_and_require_review(tmp_path):
    module = banco()
    source_root = tmp_path / "originals"
    source_root.mkdir()
    path = tmp_path / "aggregate" / "analytics.sqlite"
    module.initialize_store(path, "aggregate_analytics", immutable_roots=[source_root])
    conn = module.connect_store(path, expected_scope="aggregate_analytics", readonly=False)
    try:
        with pytest.raises(ValueError, match="hash|SHA-256|SHA256"):
            module.register_analysis_run(
                conn, run_id="run-bad", input_manifest_sha256="not-a-hash",
                code_commit="abc", config_sha256="c" * 64,
                method="descriptive", min_cell_n=5,
            )
        module.register_analysis_run(
            conn, run_id="run-1", input_manifest_sha256="a" * 64,
            code_commit="b" * 40, config_sha256="c" * 64,
            method="descriptive", min_cell_n=5,
        )
        small = module.record_aggregate_metric(
            conn, run_id="run-1", metric_id="adequate_rate", dimensions={"grade": 2},
            n=4, numerator=3, denominator=4, value=0.75,
        )
        assert small["status"] == "suppressed"
        assert small["value"] is None
        enough = module.record_aggregate_metric(
            conn, run_id="run-1", metric_id="adequate_rate", dimensions={"grade": 3},
            n=5, numerator=4, denominator=5, value=0.8,
        )
        assert enough["status"] == "pending_human_review"
        assert enough["value"] == 0.8
        with pytest.raises(sqlite3.IntegrityError, match="append-only|imutavel"):
            conn.execute("UPDATE analysis_run SET method='other'")
        conn.commit()
    finally:
        conn.close()


def test_aggregate_dimensions_reject_identifiers(tmp_path):
    module = banco()
    source_root = tmp_path / "originals"
    source_root.mkdir()
    path = tmp_path / "aggregate" / "analytics.sqlite"
    module.initialize_store(path, "aggregate_analytics", immutable_roots=[source_root])
    conn = module.connect_store(path, expected_scope="aggregate_analytics", readonly=False)
    try:
        module.register_analysis_run(
            conn, run_id="run-1", input_manifest_sha256="a" * 64,
            code_commit="b" * 40, config_sha256="c" * 64,
            method="descriptive", min_cell_n=5,
        )
        rejected = False
        try:
            module.record_aggregate_metric(
                conn, run_id="run-1", metric_id="rate",
                dimensions={"school_year": 2, "student_local_id": "pseudonimo-1"},
                n=6, numerator=4, denominator=6,
            )
        except ValueError:
            rejected = True
        assert rejected, "dimensão individual não deve atravessar a fronteira agregada"
    finally:
        conn.close()


def test_claim_evidence_is_hash_and_locator_only(tmp_path):
    module = banco()
    source_root = tmp_path / "originals"
    source_root.mkdir()
    path = tmp_path / "aggregate" / "analytics.sqlite"
    module.initialize_store(path, "aggregate_analytics", immutable_roots=[source_root])
    conn = module.connect_store(path, expected_scope="aggregate_analytics", readonly=False)
    try:
        info = module.inspect_store(path, expected_scope="aggregate_analytics")
        columns = set(info["columns"]["claim_evidence"])
        assert {"claim_sha256", "source_sha256", "locator"}.issubset(columns)
        assert not {"statement", "student_name", "local_student_id"}.intersection(columns)
        module.register_analysis_run(
            conn, run_id="run-1", input_manifest_sha256="a" * 64,
            code_commit="b" * 40, config_sha256="c" * 64,
            method="descriptive", min_cell_n=5,
        )
        module.record_claim_evidence(
            conn, claim_id="claim-1", run_id="run-1", claim_type="observed",
            claim_sha256="d" * 64, source_sha256="e" * 64, locator="page:1",
        )
        rejected = False
        try:
            module.record_claim_evidence(
                conn, claim_id="claim-2", run_id="run-1", claim_type="observed",
                claim_sha256="f" * 64, source_sha256="e" * 64, locator="student name record",
            )
        except ValueError:
            rejected = True
        assert rejected, "localizador em texto livre não deve armazenar identificadores"
    finally:
        conn.close()
