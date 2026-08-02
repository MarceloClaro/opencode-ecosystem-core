# -*- coding: utf-8 -*-
"""Valida páginas impressas das rotas trilíngues contra labels do arquivo AUX.

Usa ``pdftotext -layout`` para preservar os blocos ``Rotas/Routes/路线`` e
detecta regressões de escopo em ``\trilangref``. Valida as 540 ocorrências reais
(180 por língua) e também informa a métrica legada de 462 IDs com prefixo de
três letras e sufixo numérico.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


FRAGMENT_ID_PATTERN = r"[A-Z]{3,4}-(?:\d+|[A-Za-z][A-Za-z-]*)"
LABEL_RE = re.compile(
    rf"\\newlabel\{{((?:frag|fragen|fragzh):({FRAGMENT_ID_PATTERN}))\}}"
    r"\{\{([^}]*)\}\{([^}]*)\}"
)
ROUTE_RE = re.compile(
    rf"(?<![A-Z])({FRAGMENT_ID_PATTERN})\s*\(p\.\s*(\d+)\)"
)
LEGACY_NUMERIC_ID_RE = re.compile(r"^[A-Z]{3}-\d+$")
MARKERS = (("Routes:", "fragen:"), ("Rotas:", "frag:"), ("路线:", "fragzh:"))


def parse_aux_labels(aux_text: str) -> dict[str, int]:
    return {
        match.group(1): int(match.group(4))
        for match in LABEL_RE.finditer(aux_text)
    }


def duplicate_aux_labels(aux_text: str) -> list[str]:
    counts = Counter(match.group(1) for match in LABEL_RE.finditer(aux_text))
    return sorted(label for label, count in counts.items() if count > 1)


def _marker(line: str) -> tuple[str, str] | None:
    normalized = re.sub(r"路\s+线\s*:", "路线:", line)
    for marker, prefix in MARKERS:
        if re.search(rf"(?:^|→)\s*{re.escape(marker)}", normalized):
            return marker, prefix
    return None


def extract_printed_routes(layout_text: str, lookahead: int = 7) -> list[dict[str, Any]]:
    lines = layout_text.splitlines()
    routes: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        selected = _marker(line)
        if selected is None:
            continue
        marker, prefix = selected
        block: list[str] = []
        for cursor in range(index, min(index + lookahead, len(lines))):
            if cursor > index and _marker(lines[cursor]) is not None:
                break
            block.append(lines[cursor])
        joined = " ".join(block)
        joined = re.sub(r"\b([A-Z]{3,4})-\s+([A-Za-z0-9])", r"\1-\2", joined)
        for fragment_id, page in ROUTE_RE.findall(joined):
            routes.append(
                {
                    "prefix": prefix,
                    "fragment_id": fragment_id,
                    "printed_page": int(page),
                    "source_line": index + 1,
                    "marker": marker,
                }
            )
    return routes


def validate_layout_text(
    layout_text: str,
    aux_text: str,
    *,
    expected_count: int = 540,
) -> dict[str, Any]:
    labels = parse_aux_labels(aux_text)
    duplicate_labels = duplicate_aux_labels(aux_text)
    routes = extract_printed_routes(layout_text)
    missing: list[dict[str, Any]] = []
    divergences: list[dict[str, Any]] = []
    for route in routes:
        label = route["prefix"] + route["fragment_id"]
        if label not in labels:
            missing.append(
                {
                    "label": label,
                    "printed_page": route["printed_page"],
                    "source_line": route["source_line"],
                }
            )
            continue
        if labels[label] != route["printed_page"]:
            divergences.append(
                {
                    "label": label,
                    "printed_page": route["printed_page"],
                    "aux_page": labels[label],
                }
            )
    counts = Counter(route["prefix"] for route in routes)
    by_prefix = {prefix: counts.get(prefix, 0) for prefix in ("frag:", "fragen:", "fragzh:")}
    legacy_routes = [
        route
        for route in routes
        if LEGACY_NUMERIC_ID_RE.fullmatch(route["fragment_id"])
    ]
    legacy_counts = Counter(route["prefix"] for route in legacy_routes)
    result = {
        "expected_count": expected_count,
        "route_count": len(routes),
        "by_prefix": by_prefix,
        "legacy_numeric_route_count": len(legacy_routes),
        "legacy_numeric_by_prefix": {
            prefix: legacy_counts.get(prefix, 0)
            for prefix in ("frag:", "fragen:", "fragzh:")
        },
        "label_count": len(labels),
        "duplicate_labels": duplicate_labels,
        "missing_labels": missing,
        "divergences": divergences,
    }
    result["passed"] = (
        result["route_count"] == expected_count
        and not duplicate_labels
        and not missing
        and not divergences
    )
    return result


def validate_pdf_routes(
    pdf_path: Path,
    aux_path: Path,
    *,
    expected_count: int = 540,
) -> dict[str, Any]:
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return validate_layout_text(
        completed.stdout,
        aux_path.read_text(encoding="utf-8"),
        expected_count=expected_count,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("aux", type=Path)
    parser.add_argument("--expected", type=int, default=540)
    args = parser.parse_args()
    result = validate_pdf_routes(
        args.pdf.resolve(),
        args.aux.resolve(),
        expected_count=args.expected,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
