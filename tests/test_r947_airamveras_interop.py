"""R947: formato canônico AiramVeras para consumidores/frameworks externos."""

import asyncio
import csv
import io
import json
from pathlib import Path

import pytest

from agents.lifecycle import AgentLifecycleService, _metadata


ROOT = Path(__file__).resolve().parents[1]


class FakeMatrixCorpus:
    def __init__(self, *, source_scope="public matrix metadata only"):
        self.source_scope = source_scope

    def get_matrix(self, matrix_id, *, system, limit=100, offset=0):
        return {
            "status": "ok",
            "system": system,
            "matrix_id": matrix_id,
            "source_scope": self.source_scope,
            "matrix": {
                "matriz_id": matrix_id,
                "edition_year": 2026,
                "stage": "EF",
                "year_serie": 2,
                "component": "Língua Portuguesa",
                "instrument_type": "formativa",
            },
            "descriptors": [
                {
                    "matriz_id": matrix_id,
                    "ano_edicao": 2026,
                    "etapa": "EF",
                    "ano_serie": 2,
                    "componente": "Língua Portuguesa",
                    "tipo_instrumento": "formativa",
                    "codigo": "H01",
                    "descricao": "Localizar informação explícita.",
                    "fonte_arquivo": "matriz.pdf",
                    "fonte_url": "https://official.example/matriz.pdf",
                    "pagina_pdf": 1,
                    "fonte_sha256": "a" * 64,
                    # Campo não permitido: o adaptador deve projetar a lista fechada.
                    "student_name": "DADO-SINTETICO-NAO-EXPORTAR",
                }
            ],
        }


def test_adapter_builds_canonical_bundle_with_row_level_provenance():
    from integrations.airamveras_adapter import AiramVerasAdapter

    adapter = AiramVerasAdapter(FakeMatrixCorpus())
    bundle = adapter.load_matrix("AvalieCE_2026_2_LP_2EF", system="CAEd")
    payload = bundle.to_payload("records")

    assert payload["schema_id"] == "airamveras.education-matrix"
    assert payload["schema_version"] == "1.0.0"
    assert payload["manifest"]["data_classification"] == "public_assessment_matrix"
    assert payload["manifest"]["rows"] == 1
    row = payload["records"][0]
    assert row["source_system"] == "CAEd"
    assert row["matrix_id"] == "AvalieCE_2026_2_LP_2EF"
    assert row["descriptor_code"] == "H01"
    assert row["source_sha256"] == "a" * 64
    assert "student_name" not in row
    assert "DADO-SINTETICO-NAO-EXPORTAR" not in json.dumps(payload, ensure_ascii=False)


def test_bundle_exports_records_json_and_csv_without_disk_writes(tmp_path):
    from integrations.airamveras_adapter import AiramVerasAdapter

    adapter = AiramVerasAdapter(FakeMatrixCorpus())
    bundle = adapter.load_matrix("AvalieCE_2026_2_LP_2EF", system="CAEd")
    before = list(tmp_path.iterdir())

    records = bundle.to_payload("records")
    parsed_json = json.loads(bundle.to_payload("json")["content"])
    csv_payload = bundle.to_payload("csv")
    rows = list(csv.DictReader(io.StringIO(csv_payload["content"])))

    assert parsed_json["schema_id"] == records["schema_id"]
    assert parsed_json["records"] == records["records"]
    assert rows[0]["descriptor_code"] == "H01"
    assert rows[0]["source_url"] == "https://official.example/matriz.pdf"
    assert list(tmp_path.iterdir()) == before

    with pytest.raises(ValueError):
        bundle.to_payload("parquet")


def test_bundle_includes_machine_readable_record_schema():
    from jsonschema import Draft202012Validator
    from integrations.airamveras_adapter import AiramVerasAdapter

    bundle = AiramVerasAdapter(FakeMatrixCorpus()).load_matrix(
        "AvalieCE_2026_2_LP_2EF", system="CAEd"
    )
    payload = bundle.to_payload("records")
    schema = payload["schema"]
    Draft202012Validator.check_schema(schema)
    assert schema["type"] == "object"
    assert set(schema["required"]) == set(payload["records"][0])
    assert schema["additionalProperties"] is False
    Draft202012Validator(schema).validate(payload["records"][0])


def test_adapter_rejects_restricted_sources_and_never_reads_student_tables():
    from integrations.airamveras_adapter import AiramVerasAdapter

    adapter = AiramVerasAdapter(FakeMatrixCorpus(source_scope="student_results"))
    with pytest.raises(ValueError):
        adapter.load_matrix("unapproved", system="CAEd")


def test_caed_spaece_mcp_exposes_framework_neutral_export():
    from integrations.caed_spaece_mcp import MatrixCorpus, create_server
    from integrations.airamveras_adapter import AiramVerasAdapter

    server = create_server(MatrixCorpus(), adapter=AiramVerasAdapter(MatrixCorpus()))
    tools = asyncio.run(server.list_tools())
    assert "export_matrix_bundle" in {tool.name for tool in tools}


def test_matrix_specialist_advertises_canonical_exports():
    report = AgentLifecycleService(ROOT).validate("caed-spaece-matrix-specialist")
    _, prompt = _metadata((ROOT / report["source_file"]).read_bytes())
    lowered = prompt.casefold()
    assert "airamveras.education-matrix" in lowered
    assert "json" in lowered and "jsonl" in lowered and "csv" in lowered and "records" in lowered
    assert "framework" in lowered
