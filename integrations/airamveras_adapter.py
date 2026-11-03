"""Adaptador independente para interoperabilidade dos descritores AiramVeras.

O bundle canônico é neutro em framework: consumidores podem usar records Python,
JSON, JSONL ou CSV sem importar código AiramVeras, pandas, Polars, Spark ou HuggingFace.
Somente matrizes públicas retornadas pelo MatrixCorpus são aceitas.
"""
from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Protocol

SCHEMA_ID = "airamveras.education-matrix"
SCHEMA_VERSION = "1.0.0"
RECORD_FIELDS = (
    "record_id", "source_system", "matrix_id", "edition_year", "stage", "grade",
    "component", "instrument_type", "descriptor_code", "descriptor_text",
    "source_file", "source_url", "source_page", "source_sha256",
)
DEFAULT_MAX_EXPORT_BYTES = 2 * 1024 * 1024
MAX_EXPORT_BYTES = 16 * 1024 * 1024
CANONICAL_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:airamveras:education-matrix:record:1.0.0",
    "title": "AiramVeras public assessment-matrix descriptor record",
    "type": "object",
    "required": list(RECORD_FIELDS),
    "properties": {
        "record_id": {"type": "string", "minLength": 1},
        "source_system": {"enum": ["CAEd", "SPAECE"]},
        "matrix_id": {"type": "string", "minLength": 1},
        "edition_year": {"type": ["integer", "null"], "minimum": 1900, "maximum": 2200},
        "stage": {"type": ["string", "null"]},
        "grade": {"type": ["integer", "null"], "minimum": 1, "maximum": 20},
        "component": {"type": ["string", "null"]},
        "instrument_type": {"type": ["string", "null"]},
        "descriptor_code": {"type": "string", "minLength": 1},
        "descriptor_text": {"type": "string", "minLength": 1},
        "source_file": {"type": ["string", "null"]},
        "source_url": {"type": ["string", "null"]},
        "source_page": {"type": ["integer", "null"], "minimum": 1},
        "source_sha256": {"type": ["string", "null"], "pattern": "^[a-f0-9]{64}$"},
    },
    "additionalProperties": False,
}


class MatrixProvider(Protocol):
    def get_matrix(self, matrix_id: str, *, system: str, limit: int = 100,
                   offset: int = 0) -> dict[str, Any]: ...


@dataclass(frozen=True)
class CanonicalMatrixBundle:
    manifest: dict[str, Any]
    records: tuple[dict[str, Any], ...]

    @property
    def schema_id(self) -> str:
        return SCHEMA_ID

    @property
    def schema_version(self) -> str:
        return SCHEMA_VERSION

    def to_payload(self, format: str = "records", *, registry: "FrameworkExportRegistry | None" = None) -> dict[str, Any]:
        return (registry or DEFAULT_EXPORT_REGISTRY).export(self, format)


def _base_payload(bundle: CanonicalMatrixBundle) -> dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "schema": CANONICAL_SCHEMA,
        "manifest": dict(bundle.manifest),
    }


def _export_records(bundle: CanonicalMatrixBundle) -> dict[str, Any]:
    return {**_base_payload(bundle), "format": "records",
            "records": [dict(record) for record in bundle.records]}


def _export_json(bundle: CanonicalMatrixBundle) -> dict[str, Any]:
    document = _export_records(bundle)
    return {**_base_payload(bundle), "format": "json",
            "content": json.dumps(document, ensure_ascii=False, sort_keys=True, allow_nan=False)}


def _export_jsonl(bundle: CanonicalMatrixBundle) -> dict[str, Any]:
    content = "\n".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False)
        for record in bundle.records
    )
    return {**_base_payload(bundle), "format": "jsonl", "content": content}


def _export_csv(bundle: CanonicalMatrixBundle) -> dict[str, Any]:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=RECORD_FIELDS, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(bundle.records)
    return {**_base_payload(bundle), "format": "csv", "content": stream.getvalue()}


class FrameworkExportRegistry:
    """Registro explícito de serializadores; não importa plugins dinamicamente."""

    def __init__(self, *, max_payload_bytes: int = DEFAULT_MAX_EXPORT_BYTES) -> None:
        if (isinstance(max_payload_bytes, bool) or not isinstance(max_payload_bytes, int)
                or not 1 <= max_payload_bytes <= MAX_EXPORT_BYTES):
            raise ValueError("max_payload_bytes deve estar entre 1 byte e 16 MiB.")
        self.max_payload_bytes = max_payload_bytes
        self._exporters: dict[str, Callable[[CanonicalMatrixBundle], dict[str, Any]]] = {
            "records": _export_records,
            "json": _export_json,
            "jsonl": _export_jsonl,
            "csv": _export_csv,
        }

    def formats(self) -> tuple[str, ...]:
        return tuple(sorted(self._exporters))

    def register(self, format_id: str, exporter: Callable[[CanonicalMatrixBundle], dict[str, Any]], *, replace: bool = False) -> None:
        if not isinstance(format_id, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", format_id):
            raise ValueError("Identificador de exportador inválido.")
        if not callable(exporter):
            raise ValueError("Exportador deve ser callable fornecido explicitamente pelo host.")
        if format_id in self._exporters and not replace:
            raise ValueError("Formato já registrado; substituição exige decisão explícita.")
        self._exporters[format_id] = exporter

    def export(self, bundle: CanonicalMatrixBundle, format_id: str) -> dict[str, Any]:
        exporter = self._exporters.get(format_id)
        if exporter is None:
            raise ValueError("Formato não registrado.")
        payload = exporter(bundle)
        if not isinstance(payload, dict):
            raise ValueError("Exportador deve retornar objeto JSON.")
        try:
            encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False,
                                 separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError):
            raise ValueError("Exportador retornou conteúdo não serializável como JSON.") from None
        if len(encoded) > self.max_payload_bytes:
            raise ValueError("Payload excede max_payload_bytes configurado.")
        return payload


DEFAULT_EXPORT_REGISTRY = FrameworkExportRegistry()


class AiramVerasAdapter:
    """Projeta uma matriz local CAEd/SPAECE em contrato estável e rastreável."""

    def __init__(self, provider: MatrixProvider | None = None,
                 export_registry: FrameworkExportRegistry | None = None) -> None:
        if provider is None:
            from integrations.caed_spaece_mcp import MatrixCorpus
            provider = MatrixCorpus()
        self.provider = provider
        self.export_registry = export_registry or DEFAULT_EXPORT_REGISTRY

    def export_matrix_bundle(self, matrix_id: str, *, system: str, format: str = "records",
                             limit: int = 100, offset: int = 0) -> dict[str, Any]:
        bundle = self.load_matrix(matrix_id, system=system, limit=limit, offset=offset)
        return bundle.to_payload(format, registry=self.export_registry)

    def load_matrix(self, matrix_id: str, *, system: str, limit: int = 100,
                    offset: int = 0) -> CanonicalMatrixBundle:
        result = self.provider.get_matrix(matrix_id, system=system, limit=limit, offset=offset)
        if result.get("status") != "ok":
            raise ValueError("Matriz ausente ou indisponível no corpus allowlisted.")
        if result.get("source_scope") != "public matrix metadata only":
            raise ValueError("Fonte fora do escopo público de matrizes.")
        matrix = result.get("matrix")
        descriptors = result.get("descriptors")
        if not isinstance(matrix, dict) or not isinstance(descriptors, list):
            raise ValueError("Resposta da fonte de matriz não satisfaz o contrato.")
        system_value = result.get("system")
        if system_value not in {"CAEd", "SPAECE"} or matrix.get("matriz_id") != matrix_id:
            raise ValueError("Identidade da matriz divergente.")

        records: list[dict[str, Any]] = []
        for item in descriptors:
            if not isinstance(item, dict):
                raise ValueError("Registro de descritor inválido.")
            code = item.get("codigo")
            text = item.get("descricao") or item.get("descricao_extraida")
            if not isinstance(code, str) or not code.strip() or not isinstance(text, str) or not text.strip():
                raise ValueError("Descritor sem código ou descrição.")
            edition_year = item.get("ano_edicao", matrix.get("edition_year"))
            record = {
                "record_id": f"{system_value}:{matrix_id}:{code}",
                "source_system": system_value,
                "matrix_id": matrix_id,
                "edition_year": edition_year if isinstance(edition_year, int) and not isinstance(edition_year, bool) else None,
                "stage": item.get("etapa", matrix.get("stage")),
                "grade": item.get("ano_serie", matrix.get("year_serie")),
                "component": item.get("componente", matrix.get("component")),
                "instrument_type": item.get("tipo_instrumento", matrix.get("instrument_type")),
                "descriptor_code": code.strip(),
                "descriptor_text": text.strip(),
                "source_file": item.get("fonte_arquivo", matrix.get("source_file")),
                "source_url": item.get("fonte_url", matrix.get("source_url")),
                "source_page": item.get("pagina_pdf"),
                "source_sha256": item.get("fonte_sha256"),
            }
            # Projeção por allowlist: campos extras, inclusive identificadores e
            # valores inesperados do fornecedor, nunca atravessam a fronteira.
            records.append({field: record.get(field) for field in RECORD_FIELDS})

        manifest = {
            "dataset_id": f"{system_value}:{matrix_id}",
            "source_system": system_value,
            "matrix_id": matrix_id,
            "edition_year": matrix.get("edition_year"),
            "stage": matrix.get("stage"),
            "grade": matrix.get("year_serie"),
            "component": matrix.get("component"),
            "instrument_type": matrix.get("instrument_type"),
            "rows": len(records),
            "data_classification": "public_assessment_matrix",
            "license_status": "not_asserted_by_adapter",
            "source_scope": "public matrix metadata only",
            "synthetic": False,
            "training_executed": False,
            "upload_executed": False,
            "externally_validated": False,
            "limitations": [
                "O bundle não valida pedagogicamente a matriz nem a equivalência com BNCC.",
                "Licença e vigência precisam ser verificadas na fonte correspondente.",
                "O adaptador não representa resultados individuais ou microdados.",
            ],
        }
        return CanonicalMatrixBundle(manifest=manifest, records=tuple(records))
