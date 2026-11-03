"""R951: formatos neutros e registry explícito de adaptadores consumidores."""

import asyncio
import csv
import io
import json

import pytest


class FakeMatrixProvider:
    def get_matrix(self, matrix_id, *, system, limit=100, offset=0):
        return {
            "status": "ok",
            "system": system,
            "matrix_id": matrix_id,
            "source_scope": "public matrix metadata only",
            "matrix": {"matriz_id": matrix_id, "edition_year": 2026, "stage": "EF",
                       "year_serie": 2, "component": "Língua Portuguesa",
                       "instrument_type": "formativa"},
            "descriptors": [{"codigo": "H01", "descricao": "Localizar informação explícita.",
                             "fonte_arquivo": "matriz.pdf", "fonte_url": "https://official.example/m.pdf",
                             "pagina_pdf": 1, "fonte_sha256": "a" * 64}],
        }


def test_jsonl_export_is_stable_and_provenance_complete():
    from integrations.airamveras_adapter import AiramVerasAdapter

    adapter = AiramVerasAdapter(FakeMatrixProvider())
    payload = adapter.export_matrix_bundle("M1", system="CAEd", format="jsonl")
    lines = payload["content"].splitlines()
    assert payload["schema_id"] == "airamveras.education-matrix"
    assert payload["format"] == "jsonl"
    assert len(lines) == payload["manifest"]["rows"] == 1
    row = json.loads(lines[0])
    assert row["record_id"] == "CAEd:M1:H01"
    assert row["source_url"] == "https://official.example/m.pdf"
    assert row["source_sha256"] == "a" * 64


def test_existing_builtin_formats_remain_compatible():
    from integrations.airamveras_adapter import AiramVerasAdapter

    adapter = AiramVerasAdapter(FakeMatrixProvider())
    records = adapter.export_matrix_bundle("M1", system="CAEd", format="records")
    json_payload = adapter.export_matrix_bundle("M1", system="CAEd", format="json")
    csv_payload = adapter.export_matrix_bundle("M1", system="CAEd", format="csv")

    assert records["format"] == "records"
    assert json.loads(json_payload["content"])["records"] == records["records"]
    csv_rows = list(csv.DictReader(io.StringIO(csv_payload["content"])))
    assert len(csv_rows) == records["manifest"]["rows"] == 1
    assert csv_rows[0]["record_id"] == records["records"][0]["record_id"]


def test_framework_exporter_registry_is_explicit_and_bounded():
    from integrations.airamveras_adapter import (
        MAX_EXPORT_BYTES, AiramVerasAdapter, FrameworkExportRegistry,
    )

    registry = FrameworkExportRegistry(max_payload_bytes=256)
    with pytest.raises(ValueError):
        FrameworkExportRegistry(max_payload_bytes=MAX_EXPORT_BYTES + 1)
    registry.register("demo-framework", lambda bundle: {
        "format": "demo-framework", "rows": len(bundle.records),
        "schema_id": bundle.schema_id,
    })
    adapter = AiramVerasAdapter(FakeMatrixProvider(), export_registry=registry)
    output = adapter.export_matrix_bundle("M1", system="CAEd", format="demo-framework")
    assert output == {"format": "demo-framework", "rows": 1, "schema_id": "airamveras.education-matrix"}
    with pytest.raises(ValueError):
        registry.register("demo-framework", lambda bundle: {})
    with pytest.raises(ValueError):
        registry.register("../module", lambda bundle: {})
    with pytest.raises(ValueError):
        registry.register("not-callable", None)
    registry.register("bad-output", lambda bundle: {"value": float("nan")})
    with pytest.raises(ValueError):
        adapter.export_matrix_bundle("M1", system="CAEd", format="bad-output")
    registry.register("oversized", lambda bundle: {"payload": "x" * 256})
    with pytest.raises(ValueError, match="max_payload_bytes"):
        adapter.export_matrix_bundle("M1", system="CAEd", format="oversized")


def test_caed_spaece_mcp_advertises_jsonl():
    from integrations.caed_spaece_mcp import MatrixCorpus, create_server
    from integrations.airamveras_adapter import AiramVerasAdapter

    server = create_server(MatrixCorpus(), adapter=AiramVerasAdapter(FakeMatrixProvider()))
    tools = asyncio.run(server.list_tools())
    tool = next(item for item in tools if item.name == "export_matrix_bundle")
    properties = tool.inputSchema["properties"]
    assert set(properties) == {"matrix_id", "system", "format", "limit", "offset"}
    assert set(properties["format"]["enum"]) == {"records", "json", "jsonl", "csv"}
    assert tool.annotations.readOnlyHint is True
    assert tool.annotations.destructiveHint is False
    assert tool.annotations.openWorldHint is False
