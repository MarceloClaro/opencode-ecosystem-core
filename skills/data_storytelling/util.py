# -*- coding: utf-8 -*-
"""Utilidades determinísticas do Data Storytelling Auditável (SPEC-935-R1003).

Sem rede, sem relógio, sem aleatoriedade. Tudo o que entra pode ser recomputado
a partir dos mesmos bytes.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from typing import Any

SCHEMA_VERSION = "r1003.v1"

#: Fonte rastreável: ano de 4 dígitos, DOI ou URL.
TRACEABLE_SOURCE_RE = re.compile(
    r"(\b(?:19|20)\d{2}\b|doi\.org|10\.\d{4,9}/|https?://|www\.)", re.IGNORECASE
)

#: Marcadores de texto não finalizado.
PLACEHOLDER_RE = re.compile(
    r"\b(TODO|TBD|XXX|lorem\s+ipsum|preencher|inserir)\b", re.IGNORECASE
)

LIMITS = [
    "Saída computacional determinística; não valida veracidade, "
    "representatividade ou causalidade dos dados.",
    "Revisão humana é obrigatória antes de publicação ou decisão.",
]


class DataStoryError(ValueError):
    """Erro de contrato com código estável para auditoria."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


def _json_safe(value: Any) -> Any:
    """Normaliza NaN/infinito e chaves para um JSON determinístico."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    """JSON canônico: chaves ordenadas, UTF-8, sem espaços supérfluos."""
    try:
        return json.dumps(
            _json_safe(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            default=str,
        )
    except (TypeError, ValueError) as exc:
        raise DataStoryError("non_serializable", "Objeto não serializável.") from exc


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def normalize_space(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def is_traceable_source(value: Any) -> bool:
    return bool(TRACEABLE_SOURCE_RE.search(normalize_space(value)))


def as_number(value: Any, *, field: str = "value") -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DataStoryError("non_numeric_value", f"{field} não é numérico: {value!r}")
    number = float(value)
    if not math.isfinite(number):
        raise DataStoryError("non_finite_value", f"{field} não é finito: {value!r}")
    return number


def format_number_ptbr(value: Any, decimals: int = 0) -> str:
    """Formata número no padrão brasileiro (milhar '.', decimal ',')."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(number):
        return str(value)
    decimals = max(0, min(int(decimals), 6))
    text = f"{number:,.{decimals}f}"
    return text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def format_value(value: Any, unit: str | None = None, decimals: int = 0) -> str:
    text = format_number_ptbr(value, decimals)
    if not unit:
        return text
    unit = str(unit).strip()
    if unit == "%":
        return f"{text}%"
    return f"{text} {unit}"
