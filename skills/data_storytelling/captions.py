# -*- coding: utf-8 -*-
"""Legenda, fonte e nota metodológica (SPEC-935-R1003).

Quatro camadas: rótulo, título-mensagem, chave visual e fonte+nota.
"""

from __future__ import annotations

import html
import re
from collections.abc import Mapping
from typing import Any

from .util import (
    SCHEMA_VERSION,
    LIMITS,
    PLACEHOLDER_RE,
    DataStoryError,
    canonical_json,
    is_blank,
    is_traceable_source,
    normalize_space,
    sha256_text,
)

_KINDS = {
    "figura": "Figura",
    "gráfico": "Gráfico",
    "grafico": "Gráfico",
    "tabela": "Tabela",
    "quadro": "Quadro",
    "mapa": "Mapa",
}
_NUMBER_RE = re.compile(r"^\d+[A-Za-z]?$")
_MAX_TITLE = 140
_METHOD_RE = re.compile(
    r"(m[eé]todo|metodologia|calculad|imputa|m[eé]dia|mediana|percentual|"
    r"raz[aã]o|s[eé]rie|amostra|crit[eé]rio|sem\s+imputa|n\s*=)",
    re.IGNORECASE,
)


def _format_n(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _clean_title(value: Any) -> str:
    title = normalize_space(value).rstrip(". ")
    if not title:
        raise DataStoryError("missing_title", "Título é obrigatório.")
    if len(title) > _MAX_TITLE:
        raise DataStoryError(
            "title_too_long",
            f"Título com {len(title)} caracteres excede {_MAX_TITLE}.",
        )
    return title


def _clean_number(value: Any) -> str:
    if isinstance(value, bool):
        raise DataStoryError("invalid_number", "Número da figura inválido.")
    if isinstance(value, int) and value >= 1:
        return str(value)
    if isinstance(value, str) and _NUMBER_RE.match(value.strip()):
        return value.strip()
    raise DataStoryError("invalid_number", f"Número da figura inválido: {value!r}")


def build_caption(
    *,
    number: Any,
    title: Any,
    source: Any,
    note: Any,
    kind: str = "Figura",
    legend: Any = "",
    unit: str | None = None,
    n: Any = None,
    period: Any = None,
    method: Any = None,
    filters: Any = None,
    definitions: Any = None,
    elaboration: Any = None,
    spec_sha256: str | None = None,
) -> dict[str, Any]:
    """Monta a legenda completa com rótulo, chave, fonte e nota."""
    canonical_kind = _KINDS.get(str(kind).strip().casefold())
    if canonical_kind is None:
        raise DataStoryError("invalid_kind", f"Tipo de legenda inválido: {kind!r}")
    label_number = _clean_number(number)
    clean_title = _clean_title(title)

    clean_source = normalize_space(source).rstrip(".")
    if not clean_source:
        raise DataStoryError("missing_source", "Fonte é obrigatória.")
    clean_note = normalize_space(note).rstrip(".")
    if not clean_note:
        raise DataStoryError("missing_note", "Nota metodológica é obrigatória.")

    clean_legend = normalize_space(legend).rstrip(".")
    clauses = [clean_note]
    if n is not None and not re.search(r"\bn\s*=", clean_note, re.IGNORECASE):
        clauses.append(f"n = {_format_n(n)}")
    if period and "período" not in clean_note.casefold() and "periodo" not in clean_note.casefold():
        clauses.append(f"Período: {normalize_space(period)}")
    if method and "método" not in clean_note.casefold() and "metodo" not in clean_note.casefold():
        clauses.append(f"Método: {normalize_space(method)}")
    if filters and "filtro" not in clean_note.casefold():
        clauses.append(f"Filtros: {normalize_space(filters)}")
    if definitions and "defini" not in clean_note.casefold():
        clauses.append(f"Definições: {normalize_space(definitions)}")
    if unit and not clean_legend:
        clauses.append(f"Unidade: {str(unit).strip()}")
    nota = "Nota: " + ". ".join(clause.rstrip(". ") for clause in clauses) + "."

    base_source = clean_source
    clean_elaboration = normalize_space(elaboration).rstrip(".")
    if clean_elaboration and clean_elaboration.casefold() not in base_source.casefold():
        base_source = f"{clean_elaboration} {base_source}"
    fonte = f"Fonte: {base_source}."

    legenda = f"Legenda: {clean_legend}." if clean_legend else ""
    if unit and clean_legend and str(unit).strip() not in clean_legend:
        legenda = f"{legenda[:-1]}; unidade: {str(unit).strip()}."

    label = f"{canonical_kind} {label_number} – {clean_title}"
    plain_parts = [label]
    if legenda:
        plain_parts.append(legenda)
    plain_parts.extend([fonte, nota])
    plain = "\n".join(plain_parts)

    markdown = f"**{label}**"
    if legenda:
        markdown += f"\n\n{legenda}"
    markdown += f"\n\n{fonte}\n\n{nota}"

    html_block = (
        '<div class="data-caption">'
        f'<p class="caption-label"><strong>{html.escape(label)}</strong></p>'
    )
    if legenda:
        html_block += f'<p class="caption-legend">{html.escape(legenda)}</p>'
    html_block += (
        f'<p class="caption-source">{html.escape(fonte)}</p>'
        f'<p class="caption-note">{html.escape(nota)}</p>'
        "</div>"
    )

    warnings: list[dict[str, str]] = []
    if not is_traceable_source(fonte):
        warnings.append({
            "code": "SOURCE_NOT_TRACEABLE",
            "message": "A fonte não contém ano, DOI ou URL verificável.",
        })

    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "caption_bundle",
        "label": label,
        "title": clean_title,
        "legend": legenda,
        "fonte": fonte,
        "nota": nota,
        "markdown": markdown,
        "html": html_block,
        "plain": plain,
        "parts": {
            "label": True,
            "title": True,
            "legend": bool(legenda),
            "source": True,
            "note": True,
        },
        "warnings": warnings,
        "spec_sha256": spec_sha256,
        "sha256": sha256_text(plain),
        "limits": list(LIMITS),
    }


def validate_caption(caption: Mapping[str, Any]) -> dict[str, Any]:
    """Valida a legenda contra placeholders, fonte e nota."""
    if not isinstance(caption, Mapping):
        raise DataStoryError("invalid_caption", "Legenda deve ser um mapeamento.")
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    title = normalize_space(caption.get("title"))
    label = normalize_space(caption.get("label"))
    fonte = normalize_space(caption.get("fonte"))
    nota = normalize_space(caption.get("nota"))
    legend = normalize_space(caption.get("legend"))

    if not label:
        errors.append({"code": "MISSING_LABEL", "message": "Rótulo ausente."})
    if not title:
        errors.append({"code": "MISSING_TITLE", "message": "Título ausente."})
    else:
        if len(title) > _MAX_TITLE:
            errors.append({
                "code": "TITLE_TOO_LONG",
                "message": f"Título com {len(title)} caracteres.",
            })
        if title.endswith("."):
            warnings.append({
                "code": "TITLE_ENDS_WITH_PERIOD",
                "message": "Título de figura não deve terminar em ponto.",
            })

    for field_name, value in (
        ("title", title), ("legend", legend), ("fonte", fonte), ("nota", nota),
    ):
        if value and PLACEHOLDER_RE.search(value):
            errors.append({
                "code": "PLACEHOLDER_TEXT",
                "message": f"Texto não finalizado em {field_name}.",
            })

    if not fonte:
        errors.append({"code": "MISSING_SOURCE", "message": "Fonte ausente."})
    elif not is_traceable_source(fonte):
        errors.append({
            "code": "UNTRACEABLE_SOURCE",
            "message": "Fonte sem ano, DOI ou URL verificável.",
        })

    if not nota:
        errors.append({"code": "MISSING_NOTE", "message": "Nota metodológica ausente."})
    elif not re.search(r"\d", nota):
        errors.append({
            "code": "NOTE_WITHOUT_NUMBER",
            "message": "Nota sem n, período ou medida numérica.",
        })
    elif not _METHOD_RE.search(nota):
        warnings.append({
            "code": "NOTE_WITHOUT_METHOD",
            "message": "A nota não declara método, cálculo ou tratamento de ausentes.",
        })

    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "caption_validation",
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def caption_from_spec(
    spec: Mapping[str, Any], *, number: Any, kind: str = "Gráfico", **overrides: Any
) -> dict[str, Any]:
    """Deriva a legenda de uma especificação de gráfico já auditada."""
    if not isinstance(spec, Mapping):
        raise DataStoryError("invalid_spec", "Especificação deve ser um mapeamento.")
    for field, code in (
        ("title", "missing_title"),
        ("source", "missing_source"),
        ("note", "missing_note"),
    ):
        if is_blank(spec.get(field)):
            raise DataStoryError(code, f"Campo obrigatório ausente: {field}.")
    payload = {
        "number": number,
        "title": spec.get("title"),
        "kind": kind,
        "source": spec.get("source"),
        "note": spec.get("note"),
        "legend": spec.get("legend", ""),
        "n": spec.get("sample_n"),
        "period": spec.get("period"),
        "method": spec.get("method"),
        "filters": spec.get("filters"),
        "definitions": spec.get("definitions"),
        "elaboration": spec.get("elaboration"),
        "spec_sha256": sha256_text(canonical_json(dict(spec))),
    }
    payload.update(overrides)
    return build_caption(**payload)
