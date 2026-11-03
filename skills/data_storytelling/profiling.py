# -*- coding: utf-8 -*-
"""Perfil de dados e recomendação de codificação (SPEC-935-R1003)."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any

from .util import (
    SCHEMA_VERSION,
    LIMITS,
    DataStoryError,
    canonical_json,
    is_blank,
    normalize_space,
    sha256_text,
)

_TEMPORAL_HINTS = (
    "ano", "year", "periodo", "período", "data", "date", "mes", "mês",
    "trimestre", "semestre", "dia", "decada", "década",
)
_ID_HINTS = ("id", "codigo", "código", "code", "uuid", "chave", "key")
_DATE_PATTERNS = (
    re.compile(r"^\d{4}-\d{2}(-\d{2})?([T ].*)?$"),
    re.compile(r"^\d{2}/\d{2}/\d{4}$"),
    re.compile(r"^\d{4}$"),
)
_INTENTS = {
    "trend", "comparison", "ranking", "composition", "distribution",
    "relationship", "deviation",
}


def _is_temporal_name(name: str) -> bool:
    lowered = name.casefold()
    return any(hint in lowered for hint in _TEMPORAL_HINTS)


def _is_identifier_name(name: str) -> bool:
    lowered = name.casefold()
    return lowered in _ID_HINTS or any(
        lowered.endswith(f"_{hint}") or lowered.endswith(hint)
        for hint in _ID_HINTS
    )


def _looks_like_date(text: str) -> bool:
    return any(pattern.match(text) for pattern in _DATE_PATTERNS)


def _kind(name: str, values: list[Any], n_rows: int) -> str:
    if not values:
        return "unknown"

    if all(isinstance(v, bool) for v in values):
        return "categorical"

    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
        if (
            _is_temporal_name(name)
            and all(isinstance(v, int) for v in values)
            and all(1900 <= v <= 2100 for v in values)
        ):
            return "temporal"
        return "numeric"

    if all(isinstance(v, (date, datetime)) for v in values):
        return "temporal"

    if all(isinstance(v, str) for v in values):
        texts = [normalize_space(v) for v in values]
        distinct = len(set(texts))
        if _is_temporal_name(name) and all(_looks_like_date(v) for v in texts):
            return "temporal"
        if all(_looks_like_date(v) for v in texts) and all(
            re.match(r"^\d{4}-\d{2}", v) for v in texts
        ):
            return "temporal"
        if _is_identifier_name(name):
            return "identifier"
        average_length = sum(len(v) for v in texts) / len(texts)
        if average_length > 40:
            return "text"
        if distinct <= 20 or distinct / max(len(texts), 1) <= 0.2:
            return "categorical"
        if distinct / max(n_rows, 1) > 0.8 and any(" " in v for v in texts):
            return "text"
        return "categorical"

    return "mixed"


def _is_present(value: Any) -> bool:
    if is_blank(value):
        return False
    if isinstance(value, float) and not math.isfinite(value):
        return False
    return True


def _field_profile(name: str, values: list[Any], n_rows: int) -> dict[str, Any]:
    present = [v for v in values if _is_present(v)]
    kind = _kind(name, present, n_rows)
    distinct_values: list[Any] = []
    seen: set[str] = set()
    for value in present:
        key = canonical_json(value)
        if key not in seen:
            seen.add(key)
            distinct_values.append(value)

    profile: dict[str, Any] = {
        "name": name,
        "kind": kind,
        "non_null": len(present),
        "missing": n_rows - len(present),
        "distinct": len(distinct_values),
        "examples": [str(v) for v in distinct_values[:3]],
    }
    if kind == "numeric" and present:
        numbers = [float(v) for v in present]
        profile.update(
            {
                "min": min(numbers),
                "max": max(numbers),
                "mean": sum(numbers) / len(numbers),
            }
        )
    elif kind == "temporal" and present:
        orderable = sorted(str(v) for v in present)
        profile.update({"min": orderable[0], "max": orderable[-1]})
    return profile


def profile_dataset(
    rows: Sequence[Mapping[str, Any]], *, max_rows: int = 50_000
) -> dict[str, Any]:
    """Perfila tipos, ausências e cardinalidade de um conjunto de linhas."""
    if not isinstance(max_rows, int) or isinstance(max_rows, bool) or max_rows <= 0:
        raise DataStoryError("invalid_row_limit", "max_rows deve ser inteiro positivo.")
    if isinstance(rows, (str, bytes)) or not isinstance(rows, Sequence):
        raise DataStoryError("invalid_dataset", "rows deve ser uma sequência de linhas.")
    if len(rows) == 0:
        raise DataStoryError("empty_dataset", "Conjunto vazio não pode ser perfilado.")
    if len(rows) > max_rows:
        raise DataStoryError(
            "row_limit_exceeded",
            f"{len(rows)} linhas excedem o teto de {max_rows}.",
        )

    keysets: set[frozenset[str]] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise DataStoryError("invalid_row", f"Linha {index} não é mapeamento.")
        keysets.add(frozenset(str(k) for k in row.keys()))

    names = sorted({str(k) for row in rows for k in row.keys()})
    fields = []
    missing: dict[str, int] = {}
    for name in names:
        values = [row.get(name) for row in rows]
        field = _field_profile(name, values, len(rows))
        fields.append(field)
        missing[name] = field["missing"]

    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "dataset_profile",
        "n_rows": len(rows),
        "n_fields": len(fields),
        "fields": fields,
        "missing": missing,
        "missing_total": sum(missing.values()),
        "ragged_rows": len(keysets) > 1,
        "source_sha256": sha256_text(canonical_json(list(rows))),
        "limits": list(LIMITS),
    }


def _recommendation(chart: str, score: int, rationale: str, **extra: Any) -> dict[str, Any]:
    item = {"chart": chart, "score": score, "rationale": rationale}
    item.update(extra)
    return item


def _rejection(chart: str, reason: str) -> dict[str, str]:
    return {"chart": chart, "reason": reason}


def recommend_chart(
    profile: Mapping[str, Any], *, intent: str, emphasis: str | None = None
) -> dict[str, Any]:
    """Recomenda codificações compatíveis com a intenção narrativa."""
    if intent not in _INTENTS:
        raise DataStoryError("unsupported_intent", f"Intenção desconhecida: {intent!r}")
    if not isinstance(profile, Mapping) or not isinstance(profile.get("fields"), list):
        raise DataStoryError("invalid_profile", "Perfil inválido para recomendação.")

    fields = {str(f.get("name")): f for f in profile["fields"] if isinstance(f, Mapping)}
    numeric = [f for f in fields.values() if f.get("kind") == "numeric"]
    temporal = [f for f in fields.values() if f.get("kind") == "temporal"]
    categorical = [f for f in fields.values() if f.get("kind") == "categorical"]

    measure = fields.get(emphasis) if emphasis else None
    if measure is not None and measure.get("kind") != "numeric":
        measure = None
    if measure is None and numeric:
        measure = numeric[0]

    dimension = fields.get(emphasis) if emphasis else None
    if dimension is not None and dimension.get("kind") not in {"categorical", "temporal"}:
        dimension = None
    if dimension is None:
        dimension = (categorical or temporal or [None])[0]

    recommendations: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []

    def needs_measure() -> None:
        if measure is None:
            raise DataStoryError(
                "no_compatible_chart",
                f"Nenhum campo numérico compatível com a intenção {intent}.",
            )

    if intent == "trend":
        needs_measure()
        if temporal:
            recommendations.append(
                _recommendation(
                    "line", 95,
                    "Série temporal contínua: a linha preserva a ordem e a inclinação.",
                    encoding={"x": temporal[0]["name"], "y": measure["name"]},
                    guardrails=["não truncar o eixo sem sinalizar", "declarar n e período"],
                )
            )
            recommendations.append(
                _recommendation(
                    "area", 72,
                    "Área só é aceitável com base zero e uma única série.",
                    encoding={"x": temporal[0]["name"], "y": measure["name"]},
                    guardrails=["y.zero=true", "uma série"],
                )
            )
        else:
            rejected.append(
                _rejection("line", "sem campo temporal: a ordem do eixo X seria arbitrária")
            )
        rejected.append(
            _rejection("pie", "pizza não representa tendência nem ordem temporal")
        )

    elif intent in {"comparison", "ranking"}:
        needs_measure()
        if dimension is not None:
            orientation = "horizontal" if intent == "ranking" else "vertical"
            recommendations.append(
                _recommendation(
                    "bar", 95,
                    "Barras comparam magnitudes com base comum e leitura direta.",
                    orientation=orientation,
                    encoding={"x": dimension["name"], "y": measure["name"]},
                    sorting="descending" if intent == "ranking" else "none",
                    guardrails=["y.zero=true", "ordenar no ranking", "rótulos diretos"],
                )
            )
            recommendations.append(
                _recommendation(
                    "dot", 78,
                    "Pontos reduzem tinta e evitam competição de área.",
                    encoding={"x": measure["name"], "y": dimension["name"]},
                    guardrails=["eixo zero não é obrigatório para pontos", "declarar unidade"],
                )
            )
        rejected.append(
            _rejection("pie", "pizza não ordena nem compara diferenças pequenas")
        )

    elif intent == "composition":
        needs_measure()
        if dimension is None:
            raise DataStoryError(
                "no_compatible_chart", "Composição exige campo categórico."
            )
        categories = int(dimension.get("distinct") or 0)
        if categories >= 5:
            recommendations.append(
                _recommendation(
                    "stacked_bar", 90,
                    "Muitas categorias: barra empilhada preserva a ordem e o total.",
                    encoding={"x": dimension["name"], "y": measure["name"]},
                    guardrails=["y.zero=true", "limitar a 5–7 categorias visuais"],
                )
            )
        else:
            recommendations.append(
                _recommendation(
                    "stacked_bar", 82,
                    "Barra empilhada mantém a soma visível e evita ângulos.",
                    encoding={"x": dimension["name"], "y": measure["name"]},
                    guardrails=["y.zero=true"],
                )
            )
        if 0 < categories <= 4:
            recommendations.append(
                _recommendation(
                    "pie", 70,
                    "Pizza só com até 4 fatias e soma exata de 100%.",
                    encoding={"color": dimension["name"], "size": measure["name"]},
                    guardrails=["part_to_whole=true", "soma=100%", "rótulos diretos"],
                )
            )
        else:
            rejected.append(
                _rejection(
                    "pie",
                    f"{categories} categorias excedem o limite de 4 fatias legíveis",
                )
            )
        recommendations.append(
            _recommendation(
                "treemap", 55,
                "Alternativa para hierarquia, mas exige área proporcional exata.",
                guardrails=["não usar para valores negativos"],
            )
        )

    elif intent == "distribution":
        needs_measure()
        n_rows = int(profile.get("n_rows") or 0)
        if n_rows >= 30:
            recommendations.append(
                _recommendation(
                    "histogram", 95,
                    "Distribuição com n >= 30: bins declaram o agrupamento.",
                    encoding={"x": measure["name"]},
                    guardrails=["declarar bins", "y.zero=true", "n no rodapé"],
                )
            )
        else:
            recommendations.append(
                _recommendation(
                    "dot", 80,
                    "Amostra pequena: pontos preservam cada observação.",
                    encoding={"x": measure["name"]},
                    guardrails=["n < 30: evitar suavização", "mostrar todos os pontos"],
                )
            )
        rejected.append(_rejection("pie", "pizza não representa distribuição"))

    elif intent == "relationship":
        if len(numeric) < 2:
            raise DataStoryError(
                "no_compatible_chart", "Relação exige ao menos dois campos numéricos."
            )
        recommendations.append(
            _recommendation(
                "scatter", 95,
                "Dispersão expõe forma, outliers e sobreposição.",
                encoding={"x": numeric[0]["name"], "y": numeric[1]["name"]},
                guardrails=[
                    "controlar sobreposição acima de 500 pontos",
                    "não inferir causalidade",
                ],
            )
        )
        if categorical:
            recommendations.append(
                _recommendation(
                    "heatmap", 55,
                    "Calor só com células discretas e escala declarada.",
                    guardrails=["não usar cor como único canal"],
                )
            )
        rejected.append(_rejection("pie", "pizza não representa relação entre variáveis"))

    elif intent == "deviation":
        needs_measure()
        recommendations.append(
            _recommendation(
                "diverging_bar", 95,
                "Desvio pede barras divergentes com zero explícito no centro.",
                encoding={"x": (dimension or {}).get("name"), "y": measure["name"]},
                guardrails=["y.zero=true", "ordenar por magnitude", "sinal visível"],
            )
        )
        recommendations.append(
            _recommendation(
                "line", 60,
                "Linha mostra desvio ao longo do tempo, mas dilui o sinal.",
                guardrails=["marcar a referência zero"],
            )
        )
        rejected.append(_rejection("pie", "pizza não representa desvio em torno de zero"))

    if not recommendations:
        raise DataStoryError(
            "no_compatible_chart",
            f"Nenhuma codificação compatível com a intenção {intent}.",
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "chart_recommendation",
        "intent": intent,
        "emphasis": emphasis,
        "recommendations": recommendations,
        "rejected": rejected,
        "profile_sha256": sha256_text(canonical_json(dict(profile))),
        "limits": list(LIMITS),
    }
