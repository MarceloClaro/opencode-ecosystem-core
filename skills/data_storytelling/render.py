# -*- coding: utf-8 -*-
"""Render SVG determinístico e acessível (SPEC-935-R1003).

Primitivas suportadas: barra (vertical/horizontal) e linha. Sem matplotlib,
sem relógio, sem aleatoriedade. O SVG carrega `<title>`, `<desc>` e o hash da
especificação em `<metadata>`.
"""

from __future__ import annotations

import html
import math
from collections.abc import Mapping
from typing import Any

from .util import (
    SCHEMA_VERSION,
    DataStoryError,
    as_number,
    canonical_json,
    format_value,
    is_blank,
    normalize_space,
    sha256_text,
)

PALETTE = (
    "#0072B2", "#D55E00", "#009E73", "#CC79A7",
    "#E69F00", "#56B4E9", "#8C8C8C", "#111111",
)

WIDTH = 760
HEIGHT = 460
MARGIN_LEFT = 88
MARGIN_RIGHT = 40
MARGIN_TOP = 104
MARGIN_BOTTOM = 104


def _esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _truncate(value: str, limit: int) -> str:
    text = normalize_space(value)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _nice_max(value: float) -> float:
    if value <= 0 or not math.isfinite(value):
        raise DataStoryError("non_positive_scale", "Escala exige valor positivo.")
    exponent = math.floor(math.log10(value))
    magnitude = 10 ** exponent
    for candidate in (1.0, 2.0, 2.5, 5.0, 10.0):
        if candidate * magnitude >= value:
            return candidate * magnitude
    return 10.0 * magnitude


def _decimals(values: list[float], explicit: Any) -> int:
    if isinstance(explicit, int) and not isinstance(explicit, bool):
        return max(0, min(explicit, 6))
    return 0 if all(float(v).is_integer() for v in values) else 1


def _unit(spec: Mapping[str, Any]) -> str | None:
    y = spec.get("y") if isinstance(spec.get("y"), Mapping) else {}
    unit = y.get("unit")
    return str(unit).strip() if unit else None


def _header(
    title: str, subtitle: str, alt_text: str, spec_sha: str, width: int, height: int
) -> tuple[str, str]:
    suffix = spec_sha[:8]
    title_id = f"ds-title-{suffix}"
    desc_id = f"ds-desc-{suffix}"
    description = alt_text or title
    header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" '
        f'aria-labelledby="{title_id} {desc_id}">'
        f'<title id="{title_id}">{_esc(title)}</title>'
        f'<desc id="{desc_id}">{_esc(description)}</desc>'
        f'<metadata id="ds-metadata-{suffix}">'
        f'{{"schema_version":"{SCHEMA_VERSION}","spec_sha256":"{spec_sha}"}}'
        "</metadata>"
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#FFFFFF"/>'
        f'<text x="32" y="44" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="20" font-weight="700" fill="#111111">'
        f"{_esc(_truncate(title, 84))}</text>"
    )
    if subtitle:
        header += (
            f'<text x="32" y="70" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="13" fill="#555555">{_esc(_truncate(subtitle, 110))}</text>'
        )
    return header, suffix


def _footer(
    spec: Mapping[str, Any], *, x: int, y: int, max_width: int
) -> str:
    source = normalize_space(spec.get("source"))
    sample_n = spec.get("sample_n")
    parts = []
    if source:
        parts.append(f"Fonte: {source}")
    if sample_n is not None:
        parts.append(f"n = {sample_n}")
    if not parts:
        return ""
    text = _truncate(" · ".join(parts), max_width)
    return (
        f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="11" fill="#666666">{_esc(text)}</text>'
    )


def _legend(spec: Mapping[str, Any], *, x: int, y: int, max_width: int) -> str:
    legend = normalize_space(spec.get("legend"))
    if not legend:
        return ""
    return (
        f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="11" fill="#444444">'
        f"{_esc(_truncate('Legenda: ' + legend, max_width))}</text>"
    )


def _render_bar(spec: Mapping[str, Any], *, width: int, height: int, footer: bool) -> str:
    y_config = spec.get("y") if isinstance(spec.get("y"), Mapping) else {}
    if y_config.get("zero") is False:
        raise DataStoryError(
            "bar_requires_zero_baseline",
            "Barra exige base zero; use linha ou ponto para recorte de eixo.",
        )
    data = spec.get("data")
    if not isinstance(data, list) or not data:
        raise DataStoryError("invalid_data", "Barra exige lista não vazia em 'data'.")
    if len(data) > 60:
        raise DataStoryError("too_many_bars", "Máximo de 60 barras por figura.")

    entries: list[tuple[str, float]] = []
    for item in data:
        if not isinstance(item, Mapping):
            raise DataStoryError("invalid_data", "Cada barra deve ser um mapeamento.")
        label = normalize_space(item.get("label") or item.get("x") or "")
        value = as_number(item.get("value", item.get("y")), field="bar.value")
        if value < 0:
            raise DataStoryError(
                "negative_value_unsupported",
                "Barra negativa exige diverging_bar, ainda não renderizado.",
            )
        entries.append((label, value))

    values = [value for _, value in entries]
    decimals = _decimals(values, spec.get("decimals"))
    unit = _unit(spec)
    top = _nice_max(max(values) if max(values) > 0 else 1.0)
    spec_sha = sha256_text(canonical_json(dict(spec)))
    header, _ = _header(
        normalize_space(spec.get("title")),
        normalize_space(spec.get("subtitle")),
        normalize_space(spec.get("alt_text")),
        spec_sha,
        width,
        height,
    )

    plot_x0, plot_x1 = MARGIN_LEFT, width - MARGIN_RIGHT
    plot_y0, plot_y1 = MARGIN_TOP, height - MARGIN_BOTTOM
    orientation = "horizontal" if spec.get("orientation") == "horizontal" else "vertical"
    body = [
        f'<line x1="{plot_x0}" y1="{plot_y1}" x2="{plot_x1}" y2="{plot_y1}" '
        'stroke="#333333" stroke-width="1"/>'
    ]

    if orientation == "vertical":
        for tick in range(5):
            fraction = tick / 4
            axis_y = plot_y1 - fraction * (plot_y1 - plot_y0)
            body.append(
                f'<line x1="{plot_x0}" y1="{axis_y:.1f}" x2="{plot_x1}" y2="{axis_y:.1f}" '
                'stroke="#E6E6E6" stroke-width="1"/>'
            )
            body.append(
                f'<text x="{plot_x0 - 10}" y="{axis_y + 4:.1f}" '
                'font-family="Arial, Helvetica, sans-serif" font-size="11" '
                'fill="#555555" text-anchor="end">'
                f"{_esc(format_value(top * fraction, unit, decimals))}</text>"
            )
        band = (plot_x1 - plot_x0) / len(entries)
        bar_width = min(64.0, band * 0.58)
        for index, (label, value) in enumerate(entries):
            center = plot_x0 + band * (index + 0.5)
            bar_height = (value / top) * (plot_y1 - plot_y0)
            bar_y = plot_y1 - bar_height
            body.append(
                f'<rect x="{center - bar_width / 2:.1f}" y="{bar_y:.1f}" '
                f'width="{bar_width:.1f}" height="{max(bar_height, 0):.1f}" '
                f'fill="{PALETTE[0]}" rx="2"/>'
            )
            body.append(
                f'<text x="{center:.1f}" y="{bar_y - 8:.1f}" '
                'font-family="Arial, Helvetica, sans-serif" font-size="12" '
                'font-weight="700" fill="#111111" text-anchor="middle">'
                f"{_esc(format_value(value, unit, decimals))}</text>"
            )
            body.append(
                f'<text x="{center:.1f}" y="{plot_y1 + 22:.1f}" '
                'font-family="Arial, Helvetica, sans-serif" font-size="11" '
                'fill="#444444" text-anchor="middle">'
                f"{_esc(_truncate(label, 18))}</text>"
            )
    else:
        for tick in range(5):
            fraction = tick / 4
            axis_x = plot_x0 + fraction * (plot_x1 - plot_x0)
            body.append(
                f'<line x1="{axis_x:.1f}" y1="{plot_y0}" x2="{axis_x:.1f}" y2="{plot_y1}" '
                'stroke="#E6E6E6" stroke-width="1"/>'
            )
            body.append(
                f'<text x="{axis_x:.1f}" y="{plot_y1 + 18}" '
                'font-family="Arial, Helvetica, sans-serif" font-size="11" '
                'fill="#555555" text-anchor="middle">'
                f"{_esc(format_value(top * fraction, unit, decimals))}</text>"
            )
        band = (plot_y1 - plot_y0) / len(entries)
        bar_height = min(42.0, band * 0.6)
        for index, (label, value) in enumerate(entries):
            center = plot_y0 + band * (index + 0.5)
            bar_width = (value / top) * (plot_x1 - plot_x0)
            body.append(
                f'<rect x="{plot_x0}" y="{center - bar_height / 2:.1f}" '
                f'width="{max(bar_width, 0):.1f}" height="{bar_height:.1f}" '
                f'fill="{PALETTE[0]}" rx="2"/>'
            )
            body.append(
                f'<text x="{plot_x0 + bar_width + 8:.1f}" y="{center + 4:.1f}" '
                'font-family="Arial, Helvetica, sans-serif" font-size="12" '
                'font-weight="700" fill="#111111">'
                f"{_esc(format_value(value, unit, decimals))}</text>"
            )
            body.append(
                f'<text x="{plot_x0 - 12}" y="{center + 4:.1f}" '
                'font-family="Arial, Helvetica, sans-serif" font-size="11" '
                'fill="#444444" text-anchor="end">'
                f"{_esc(_truncate(label, 20))}</text>"
            )

    extras = _legend(
        spec, x=plot_x0, y=plot_y1 + 44, max_width=width - plot_x0 - MARGIN_RIGHT
    )
    if footer:
        extras += _footer(
            spec, x=plot_x0, y=height - 26,
            max_width=width - plot_x0 - MARGIN_RIGHT,
        )
    return header + "".join(body) + extras + "</svg>"


def _render_line(spec: Mapping[str, Any], *, width: int, height: int, footer: bool) -> str:
    data = spec.get("data")
    if not isinstance(data, list) or len(data) < 2:
        raise DataStoryError("invalid_data", "Linha exige ao menos dois pontos.")
    if len(data) > 2000:
        raise DataStoryError("too_many_points", "Máximo de 2.000 pontos por linha.")

    points: list[tuple[Any, float]] = []
    for item in data:
        if not isinstance(item, Mapping):
            raise DataStoryError("invalid_data", "Cada ponto deve ser um mapeamento.")
        points.append((item.get("x"), as_number(item.get("y"), field="line.y")))

    values = [value for _, value in points]
    decimals = _decimals(values, spec.get("decimals"))
    unit = _unit(spec)
    low, high = min(values), max(values)
    if low == high:
        pad = abs(low) * 0.1 or 1.0
        low, high = low - pad, high + pad
    else:
        pad = (high - low) * 0.08
        low, high = low - pad, high + pad

    numeric_x = all(
        isinstance(x, (int, float)) and not isinstance(x, bool) for x, _ in points
    )
    if numeric_x:
        x_low = min(float(x) for x, _ in points)
        x_high = max(float(x) for x, _ in points)
        if x_low == x_high:
            x_low, x_high = x_low - 1.0, x_high + 1.0
    else:
        x_low, x_high = 0.0, float(len(points) - 1)

    spec_sha = sha256_text(canonical_json(dict(spec)))
    header, _ = _header(
        normalize_space(spec.get("title")),
        normalize_space(spec.get("subtitle")),
        normalize_space(spec.get("alt_text")),
        spec_sha,
        width,
        height,
    )

    plot_x0, plot_x1 = MARGIN_LEFT, width - MARGIN_RIGHT
    plot_y0, plot_y1 = MARGIN_TOP, height - MARGIN_BOTTOM
    body: list[str] = []

    def x_position(index: int, x_value: Any) -> float:
        if numeric_x:
            return plot_x0 + ((float(x_value) - x_low) / (x_high - x_low)) * (plot_x1 - plot_x0)
        return plot_x0 + (index / max(len(points) - 1, 1)) * (plot_x1 - plot_x0)

    def y_position(value: float) -> float:
        return plot_y1 - ((value - low) / (high - low)) * (plot_y1 - plot_y0)

    for tick in range(5):
        fraction = tick / 4
        axis_y = plot_y1 - fraction * (plot_y1 - plot_y0)
        tick_value = low + fraction * (high - low)
        body.append(
            f'<line x1="{plot_x0}" y1="{axis_y:.1f}" x2="{plot_x1}" y2="{axis_y:.1f}" '
            'stroke="#E6E6E6" stroke-width="1"/>'
        )
        body.append(
            f'<text x="{plot_x0 - 10}" y="{axis_y + 4:.1f}" '
            'font-family="Arial, Helvetica, sans-serif" font-size="11" '
            'fill="#555555" text-anchor="end">'
            f"{_esc(format_value(tick_value, unit, decimals))}</text>"
        )

    coordinates = [
        (x_position(index, x_value), y_position(y_value))
        for index, (x_value, y_value) in enumerate(points)
    ]
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in coordinates)
    body.append(
        f'<polyline points="{path}" fill="none" stroke="{PALETTE[0]}" '
        'stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>'
    )
    for x, y in coordinates:
        body.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{PALETTE[0]}" '
            'stroke="#FFFFFF" stroke-width="1.5"/>'
        )

    for index, (x_value, y_value) in enumerate(points):
        if len(points) <= 8 or index in {0, len(points) - 1}:
            x, _ = coordinates[index]
            label = (
                format_value(x_value, None, decimals)
                if numeric_x
                else _truncate(str(x_value), 12)
            )
            body.append(
                f'<text x="{x:.1f}" y="{plot_y1 + 22}" '
                'font-family="Arial, Helvetica, sans-serif" font-size="11" '
                'fill="#444444" text-anchor="middle">'
                f"{_esc(label)}</text>"
            )

    last_x, last_y = coordinates[-1]
    body.append(
        f'<text x="{last_x + 10:.1f}" y="{last_y - 10:.1f}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="12" '
        'font-weight="700" fill="#111111">'
        f"{_esc(format_value(points[-1][1], unit, decimals))}</text>"
    )

    extras = _legend(
        spec, x=plot_x0, y=plot_y1 + 44, max_width=width - plot_x0 - MARGIN_RIGHT
    )
    if footer:
        extras += _footer(
            spec, x=plot_x0, y=height - 26,
            max_width=width - plot_x0 - MARGIN_RIGHT,
        )
    return header + "".join(body) + extras + "</svg>"


def render_svg(
    spec: Mapping[str, Any], *, width: int = WIDTH, height: int = HEIGHT, footer: bool = True
) -> str:
    """Renderiza barra ou linha em SVG determinístico."""
    if not isinstance(spec, Mapping):
        raise DataStoryError("invalid_spec", "Especificação deve ser um mapeamento.")
    if not isinstance(width, int) or not isinstance(height, int) or width < 320 or height < 240:
        raise DataStoryError("invalid_canvas", "Canvas mínimo de 320×240.")
    if is_blank(spec.get("title")):
        raise DataStoryError("missing_title", "SVG exige título-mensagem.")
    chart = str(spec.get("chart") or "")
    if chart == "bar":
        return _render_bar(spec, width=width, height=height, footer=footer)
    if chart == "line":
        return _render_line(spec, width=width, height=height, footer=footer)
    raise DataStoryError(
        "unsupported_render",
        f"Render suporta 'bar' e 'line'; recebido {chart!r}. "
        "Use a auditoria e um renderizador externo para os demais tipos.",
    )
