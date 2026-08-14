#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preflight PDF fail-closed da SPEC-935-R362.

Compila opcionalmente as cinco edições em duas passadas, analisa sinais
bloqueantes dos logs, paginação PDF, caixas de conteúdo e as 540 rotas. O
resultado é uma verificação técnica interna: nunca abre o release nem confere
validação histórica, cultural ou editorial externa.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
BASE = ROOT / "validacao_externa" / "cultural_episteme"
DEFAULT_OUTPUT = BASE / "molambudos_r362_preflight.json"
BUILD_RECEIPTS_PATH = BASE / "molambudos_r362_build_receipts.json"
PT_PER_MM = 72.0 / 25.4


@dataclass(frozen=True)
class Edition:
    key: str
    engine: str
    tex: str
    jobname: str
    paper_width_pt: float
    paper_height_pt: float
    inner_pt: float
    outer_pt: float
    top_pt: float
    bottom_pt: float
    cut_safe_inset_pt: float
    titlepage_source: str
    backpage_source: str
    caution_source: str
    master_source: str

    @property
    def pdf(self) -> Path:
        return BOOK / f"{self.jobname}.pdf"

    @property
    def log(self) -> Path:
        return BOOK / f"{self.jobname}.log"

    @property
    def aux(self) -> Path:
        return BOOK / f"{self.jobname}.aux"

    @property
    def fls(self) -> Path:
        return BOOK / f"{self.jobname}.fls"


SQUARE = 9.0 * 72.0
EDITIONS = {
    "pt": Edition(
        "pt", "pdflatex", "main.tex", "main", SQUARE, SQUARE,
        72.0, 72.0, 72.0, 72.0, 9.0,
        "frontmatter/titlepage.tex", "frontmatter/backpage.tex",
        "frontmatter/cuidado.tex", "main.tex::partopener",
    ),
    "en": Edition(
        "en", "pdflatex", "en/main_en.tex", "main_en", SQUARE, SQUARE,
        72.0, 72.0, 72.0, 72.0, 9.0,
        "en/frontmatter/titlepage.tex", "en/frontmatter/backpage.tex",
        "en/frontmatter/cuidado.tex", "en/main_en.tex::partopener",
    ),
    "zh": Edition(
        "zh", "xelatex", "zh/main_zh.tex", "main_zh", SQUARE, SQUARE,
        72.0, 72.0, 72.0, 72.0, 9.0,
        "zh/frontmatter/titlepage.tex", "zh/frontmatter/backpage.tex",
        "zh/frontmatter/cuidado.tex", "zh/main_zh.tex::partopener",
    ),
    "tri": Edition(
        "tri", "xelatex", "tri/main_tri.tex", "main_tri", SQUARE, SQUARE,
        72.0, 72.0, 72.0, 72.0, 9.0,
        "tri/frontmatter/titlepage.tex", "tri/frontmatter/backpage.tex",
        "tri/frontmatter/cuidado.tex", "tri/main_tri.tex::partopener",
    ),
    "kdp_tri": Edition(
        "kdp_tri", "xelatex", "main_kdp_tri_160x230mm.tex",
        "main_kdp_tri_160x230mm", 160.0 * PT_PER_MM, 230.0 * PT_PER_MM,
        20.0 * PT_PER_MM, 15.0 * PT_PER_MM, 18.0 * PT_PER_MM,
        18.0 * PT_PER_MM, 18.0,
        "tri/frontmatter/titlepage.tex", "tri/frontmatter/backpage.tex",
        "tri/frontmatter/cuidado.tex", "tri/main_tri.tex::partopener",
    ),
}

ROUTE_FILES = (
    "mem/MEM-02.tex", "mem/MEM-04.tex", "mem/MEM-06.tex",
    "doc/DOC-02.tex", "doc/DOC-05.tex", "doc/DOC-08.tex",
    "doc/DOC-15.tex", "doc/DOC-17.tex", "doc/DOC-18.tex", "luc/LUC-10.tex",
)
LANGUAGE_ROOTS = {"pt": "fragmentos", "en": "en/fragmentos", "zh": "zh/fragmentos"}
PART_MARKERS = {
    "pt": (
        ("sertao", "Sertão (1914"),
        ("colonia", "Colônia (1917"),
        ("diario", "Diário de Oliveira e Laudos"),
        ("investigacao", "Investigação Lúcia"),
        ("contaminacao", "Contaminação (Você)"),
    ),
    "en": (
        ("sertao", "The Sertão (1914"),
        ("colonia", "The Colony (1917"),
        ("diario", "Oliveira’s Diary and Reports"),
        ("investigacao", "Lúcia’s Investigation"),
        ("contaminacao", "Contamination (You)"),
    ),
    "zh": (
        ("sertao", "塞尔唐（1914"),
        ("colonia", "收容院（1917"),
        ("diario", "奥利维拉日记与鉴定报告"),
        ("investigacao", "卢西亚调查"),
        # R407: a obra trata o leitor por 您 (formal), não 你 — convenção de
        # 528 contra 1 nos fragmentos de Contaminação. O abre-parte acompanhou.
        ("contaminacao", "污染（您）"),
    ),
    "tri": (
        ("sertao", "A Vala (1914"),
        ("colonia", "O Colônia (1917"),
        ("diario", "Diário e Relatórios"),
        ("investigacao", "A Investigação de Lúcia"),
        ("contaminacao", "A Contaminação (Você)"),
    ),
    "kdp_tri": (
        ("sertao", "A Vala (1914"),
        ("colonia", "O Colônia (1917"),
        ("diario", "Diário e Relatórios"),
        ("investigacao", "A Investigação de Lúcia"),
        ("contaminacao", "A Contaminação (Você)"),
    ),
}


def _count_lines(text: str, pattern: str, flags: int = 0) -> int:
    return len(re.findall(pattern, text, flags))


def parse_latex_log(text: str) -> dict[str, Any]:
    """Extrai todos os sinais bloqueantes do log sem suavizar falhas."""

    result = {
        "overfull_hbox_count": _count_lines(text, r"Overfull \\hbox"),
        "overfull_vbox_count": _count_lines(text, r"Overfull \\vbox"),
        "infinite_glue_count": _count_lines(text, r"Infinite glue", re.IGNORECASE),
        "duplicate_page_destination_count": _count_lines(
            text, r"destination with the same identifier", re.IGNORECASE
        ),
        "undefined_reference_count": _count_lines(
            text,
            r"^(?:LaTeX|Package .*?) Warning: .*undefined reference|"
            r"^LaTeX Warning: There were undefined references",
            re.IGNORECASE | re.MULTILINE,
        ),
        "missing_character_count": _count_lines(
            text, r"^Missing character:", re.IGNORECASE | re.MULTILINE
        ),
        "rerun_required_count": _count_lines(
            text,
            r"^(?:LaTeX Warning: Label\(s\) may have changed\..*|"
            r"\(rerunfilecheck\).*Rerun to get.*)$",
            re.IGNORECASE | re.MULTILINE,
        ),
        "fatal_error_count": _count_lines(
            text,
            r"^! (?:LaTeX|Package|Class|Font).*Error|Emergency stop|"
            r"Fatal error occurred|No pages of output",
            re.IGNORECASE | re.MULTILINE,
        ),
    }
    result["passed"] = all(value == 0 for value in result.values())
    return result


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _engine_version(engine: str) -> str:
    completed = subprocess.run(
        [engine, "--version"], capture_output=True, text=True, errors="replace"
    )
    if completed.returncode != 0:
        raise RuntimeError(f"não foi possível obter versão de {engine}")
    first_line = (completed.stdout or completed.stderr).splitlines()
    if not first_line:
        raise RuntimeError(f"{engine} --version não retornou identificação")
    return first_line[0].strip()


def _stored_path(path: Path) -> tuple[str, str]:
    resolved = path.resolve()
    try:
        return "workspace", str(resolved.relative_to(ROOT.resolve()))
    except ValueError:
        return "absolute", str(resolved)


def _path_from_record(record: dict[str, Any]) -> Path:
    return (
        ROOT / record["path"]
        if record.get("scope") == "workspace"
        else Path(record["path"])
    )


def _dependency_snapshot(fls_path: Path) -> dict[str, Any]:
    if not fls_path.is_file():
        raise FileNotFoundError(fls_path)
    lines = fls_path.read_text(encoding="utf-8", errors="replace").splitlines()
    pwd_line = next((line[4:] for line in lines if line.startswith("PWD ")), str(BOOK))
    pwd = Path(pwd_line)
    resolved_inputs: dict[str, Path] = {}
    missing: list[str] = []
    for line in lines:
        if not line.startswith("INPUT "):
            continue
        raw = line[6:].strip()
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = pwd / candidate
        candidate = candidate.resolve()
        if not candidate.is_file():
            if str(candidate) not in missing:
                missing.append(str(candidate))
            continue
        resolved_inputs[str(candidate)] = candidate

    records = []
    for key, path in sorted(resolved_inputs.items()):
        scope, stored = _stored_path(path)
        records.append({"scope": scope, "path": stored, "sha256": _sha256(path)})
    # Ordenação canônica (scope, path) — DEVE espelhar _dependency_snapshot_is_current;
    # ordenar por path absoluto (resolved_inputs) intercala absolute/workspace e
    # produz Merkle diferente do validado, invalidando todo receipt (R362 bugfix).
    records.sort(key=lambda item: (item["scope"], item["path"]))
    merkle_material = "".join(
        f"{item['scope']}\0{item['path']}\0{item['sha256']}\n" for item in records
    ).encode("utf-8")
    return {
        "input_count": len(records),
        "inputs": records,
        "missing_inputs": sorted(missing),
        "merkle_sha256": hashlib.sha256(merkle_material).hexdigest(),
    }


def _dependency_snapshot_is_current(snapshot: dict[str, Any]) -> bool:
    inputs = snapshot.get("inputs", [])
    if not inputs or snapshot.get("missing_inputs"):
        return False
    current_records = []
    for record in inputs:
        path = _path_from_record(record)
        if not path.is_file() or _sha256(path) != record.get("sha256"):
            return False
        current_records.append(record)
    material = "".join(
        f"{item['scope']}\0{item['path']}\0{item['sha256']}\n"
        for item in sorted(current_records, key=lambda item: (item["scope"], item["path"]))
    ).encode("utf-8")
    return (
        len(current_records) == snapshot.get("input_count")
        and hashlib.sha256(material).hexdigest() == snapshot.get("merkle_sha256")
    )


def _rect_list(rect: Any) -> list[float]:
    return [round(float(value), 3) for value in (rect.x0, rect.y0, rect.x1, rect.y1)]


def _contains(outer: Any, inner: Any, tolerance: float) -> bool:
    return (
        inner.x0 >= outer.x0 - tolerance
        and inner.y0 >= outer.y0 - tolerance
        and inner.x1 <= outer.x1 + tolerance
        and inner.y1 <= outer.y1 + tolerance
    )


def _is_sepia_background(drawing: dict[str, Any], page_area: float) -> bool:
    fill = drawing.get("fill")
    return bool(
        fill
        and drawing["rect"].get_area() >= page_area * 0.90
        and min(fill) >= 0.70
    )


def _is_black_full_page(drawing: dict[str, Any], page_area: float) -> bool:
    fill = drawing.get("fill")
    return bool(
        fill
        and drawing["rect"].get_area() >= page_area * 0.90
        and max(fill) <= 0.15
    )


def _full_bleed_source(
    edition: Edition,
    page_index: int,
    last_page_index: int,
    text: str,
    image_count: int,
) -> dict[str, str] | None:
    role: str | None = None
    source: str | None = None
    justification: str | None = None
    if page_index == 0:
        role, source, justification = (
            "titlepage",
            edition.titlepage_source,
            "Capa integral declarada no fonte TeX.",
        )
    elif page_index == last_page_index:
        role, source, justification = (
            "backpage",
            edition.backpage_source,
            "Contracapa integral declarada no fonte TeX.",
        )
    else:
        normalized = text.casefold()
        if "cuidado" in normalized or "beware" in normalized or "当心" in text:
            role, source, justification = (
                "caution",
                edition.caution_source,
                "Página de advertência com fundo preto integral.",
            )
        else:
            for marker_id, marker in PART_MARKERS[edition.key]:
                if marker in text:
                    role, source, justification = (
                        f"partopener:{marker_id}",
                        edition.master_source.split("::", 1)[0],
                        "Abertura de parte explicitamente gerada pela macro partopener.",
                    )
                    break
    if role is None or source is None or justification is None:
        return None
    if role.startswith("partopener") and (not image_count or not text.strip()):
        return None
    source_path = BOOK / source
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    return {
        "allowlist_id": f"{edition.key}:{role}",
        "source": source,
        "source_sha256": _sha256(source_path),
        "justification": justification,
    }


def _expected_full_bleed_ids(edition: Edition) -> set[str]:
    return {
        f"{edition.key}:titlepage",
        f"{edition.key}:caution",
        *(f"{edition.key}:partopener:{marker_id}" for marker_id, _ in PART_MARKERS[edition.key]),
        f"{edition.key}:backpage",
    }


def _geometry_boxes(edition: Edition, page_index: int, page_rect: Any) -> dict[str, list[float]]:
    recto = page_index % 2 == 0
    left = edition.inner_pt if recto else edition.outer_pt
    right = edition.outer_pt if recto else edition.inner_pt
    body = type(page_rect)(left, edition.top_pt, page_rect.x1 - right, page_rect.y1 - edition.bottom_pt)
    safe = type(page_rect)(
        page_rect.x0 + edition.cut_safe_inset_pt,
        page_rect.y0 + edition.cut_safe_inset_pt,
        page_rect.x1 - edition.cut_safe_inset_pt,
        page_rect.y1 - edition.cut_safe_inset_pt,
    )
    header = type(page_rect)(body.x0, safe.y0, body.x1, body.y0)
    footer = type(page_rect)(body.x0, body.y1, body.x1, safe.y1)
    if recto:
        margin_note = type(page_rect)(body.x1, body.y0, safe.x1, body.y1)
    else:
        margin_note = type(page_rect)(safe.x0, body.y0, body.x0, body.y1)
    body_ink = type(page_rect)(
        max(safe.x0, body.x0 - 12.0),
        max(safe.y0, body.y0 - 3.0),
        min(safe.x1, body.x1 + 12.0),
        min(safe.y1, body.y1 + 12.0),
    )
    return {
        "body_box": _rect_list(body),
        "body_ink_box": _rect_list(body_ink),
        "header_box": _rect_list(header),
        "footer_box": _rect_list(footer),
        "margin_note_box": _rect_list(margin_note),
        "allowed_editorial_box": _rect_list(safe),
    }


def _roman(number: int) -> str:
    values = (
        (1000, "m"), (900, "cm"), (500, "d"), (400, "cd"),
        (100, "c"), (90, "xc"), (50, "l"), (40, "xl"),
        (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"),
    )
    result = []
    remaining = number
    for value, token in values:
        while remaining >= value:
            result.append(token)
            remaining -= value
    return "".join(result)


def _aux_first_fragment_label(aux_path: Path) -> str | None:
    if not aux_path.is_file():
        return None
    match = re.search(
        r"\\newlabel\{frag:MEM-01\}\{\{[^}]*\}\{([^}]*)\}",
        aux_path.read_text(encoding="utf-8", errors="replace"),
    )
    return match.group(1) if match else None


def _classify_zone(bbox: Any, zones: dict[str, Any], tolerance_pt: float) -> str | None:
    center = (bbox.x0 + bbox.x1) / 2.0, (bbox.y0 + bbox.y1) / 2.0
    for role in ("body", "header", "footer", "margin_note"):
        zone = zones["body_ink"] if role == "body" else zones[role]
        expanded = type(zone)(
            zone.x0 - tolerance_pt,
            zone.y0 - tolerance_pt,
            zone.x1 + tolerance_pt,
            zone.y1 + tolerance_pt,
        )
        if expanded.contains(center):
            return role
    return None


def _audit_pdf(edition: Edition, tolerance_pt: float) -> dict[str, Any]:
    import math

    if not math.isfinite(tolerance_pt) or not 0.0 <= tolerance_pt <= 1.0:
        raise ValueError("tolerância deve ser finita e estar entre 0 e 1 pt")
    try:
        import fitz  # type: ignore
    except ImportError as exc:  # pragma: no cover - depende do ambiente
        raise RuntimeError("PyMuPDF é obrigatório para o preflight R362") from exc

    if not edition.pdf.is_file():
        raise FileNotFoundError(edition.pdf)
    pdf_sha256_before = _sha256(edition.pdf)
    document = fitz.open(edition.pdf)
    if document.page_count == 0:
        raise RuntimeError(f"PDF sem páginas: {edition.pdf}")

    labels = document.get_page_labels()
    page_labels = [document[index].get_label() for index in range(document.page_count)]
    duplicate_labels = sorted(label for label, count in Counter(page_labels).items() if label and count > 1)
    roman_start = next(
        (rule for rule in labels if rule.get("startpage") == 0 and rule.get("style") == "r"),
        None,
    )
    decimal_rules = [
        rule for rule in labels
        if rule.get("style") == "D" and rule.get("firstpagenum", 1) == 1
    ]
    decimal_start = decimal_rules[0]["startpage"] if len(decimal_rules) == 1 else None
    first_fragment_label = (
        document[decimal_start].get_label()
        if isinstance(decimal_start, int) and 0 <= decimal_start < document.page_count
        else None
    )
    named_destinations = document.resolve_names()
    first_fragment_destination = named_destinations.get("MEM-01", {})
    first_fragment_destination_page = first_fragment_destination.get("page")
    aux_first_fragment_label = _aux_first_fragment_label(edition.aux)
    foliation_sequence_passed = bool(
        isinstance(decimal_start, int)
        and page_labels[:decimal_start] == [_roman(index + 1) for index in range(decimal_start)]
        and page_labels[decimal_start:]
        == [str(index + 1) for index in range(document.page_count - decimal_start)]
    )
    first_fragment_destination_matches = bool(
        isinstance(decimal_start, int)
        and first_fragment_destination_page == decimal_start
        and first_fragment_label == "1"
        and aux_first_fragment_label == "1"
    )

    violations: list[dict[str, Any]] = []
    page_reports: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []
    audited_object_count = 0
    min_text_size: float | None = None
    table_text_sizes: list[float] = []
    observed_full_bleed_ids: set[str] = set()
    all_dimensions_match = True

    for page_index, page in enumerate(document):
        page_rect = page.rect
        page_area = page_rect.get_area()
        page_dimensions_match = (
            abs(page_rect.width - edition.paper_width_pt) <= 0.25
            and abs(page_rect.height - edition.paper_height_pt) <= 0.25
        )
        all_dimensions_match = all_dimensions_match and page_dimensions_match
        geometry = _geometry_boxes(edition, page_index, page_rect)
        zones = {
            "body": fitz.Rect(geometry["body_box"]),
            "body_ink": fitz.Rect(geometry["body_ink_box"]),
            "header": fitz.Rect(geometry["header_box"]),
            "footer": fitz.Rect(geometry["footer_box"]),
            "margin_note": fitz.Rect(geometry["margin_note_box"]),
            "safe": fitz.Rect(geometry["allowed_editorial_box"]),
        }
        text_dict = page.get_text("dict")
        drawings = page.get_drawings()
        text = page.get_text("text")
        text_boxes: list[dict[str, Any]] = []
        image_boxes: list[dict[str, Any]] = []
        drawing_boxes: list[dict[str, Any]] = []
        page_violations: list[dict[str, Any]] = []
        image_blocks = [
            block for block in text_dict.get("blocks", [])
            if block.get("type") == 1 and not fitz.Rect(block["bbox"]).is_empty
        ]

        has_black_full_page = any(_is_black_full_page(item, page_area) for item in drawings)
        full_bleed = (
            _full_bleed_source(
                edition, page_index, document.page_count - 1, text, len(image_blocks)
            )
            if has_black_full_page
            else None
        )
        if full_bleed:
            observed_full_bleed_ids.add(full_bleed["allowlist_id"])
            exceptions.append({"page_index": page_index, "page_label": page.get_label(), **full_bleed})

        def add_violation(kind: str, bbox: Any, reason: str) -> None:
            violation = {
                "edition": edition.key,
                "page_index": page_index,
                "page_label": page.get_label(),
                "kind": kind,
                "bbox": _rect_list(bbox),
                "reason": reason,
            }
            page_violations.append(violation)
            violations.append(violation)

        for block in text_dict.get("blocks", []):
            if block.get("type") == 0:
                for line in block.get("lines", []):
                    line_spans = line.get("spans", [])
                    line_max_size = max(
                        (float(item.get("size", 0.0)) for item in line_spans),
                        default=0.0,
                    )
                    for span in line_spans:
                        bbox = fitz.Rect(span["bbox"])
                        size = float(span.get("size", 0.0))
                        if bbox.is_empty or size <= 0:
                            continue
                        min_text_size = size if min_text_size is None else min(min_text_size, size)
                        role = "full_bleed_art" if full_bleed else _classify_zone(bbox, zones, 3.0)
                        text_boxes.append(
                            {
                                "bbox": _rect_list(bbox),
                                "role": role or "unassigned",
                                "size_pt": round(size, 3),
                                "text": str(span.get("text", ""))[:120],
                                "is_superscript": bool(
                                    len(str(span.get("text", "")).strip()) <= 3
                                    and line_max_size > 0
                                    and size < line_max_size * 0.8
                                ),
                            }
                        )
                        if not _contains(page_rect, bbox, tolerance_pt):
                            add_violation("text", bbox, "fora do MediaBox/CropBox")
                        elif not full_bleed and not _contains(zones["safe"], bbox, tolerance_pt):
                            add_violation("text", bbox, "fora da área de corte segura")
                        elif role is None:
                            add_violation("text", bbox, "não pertence a body/header/footer/margin_note")
            elif block.get("type") == 1:
                bbox = fitz.Rect(block["bbox"])
                if bbox.is_empty:
                    continue
                assigned = _classify_zone(bbox, zones, 1.0)
                role = "full_bleed_art" if full_bleed else (
                    "body" if assigned == "body" else None
                )
                image_boxes.append({"bbox": _rect_list(bbox), "role": role or "unassigned"})
                if not _contains(page_rect, bbox, tolerance_pt):
                    add_violation("image", bbox, "fora do MediaBox/CropBox")
                elif not full_bleed and not _contains(zones["safe"], bbox, tolerance_pt):
                    add_violation("image", bbox, "fora da área de corte segura")
                elif role is None:
                    add_violation("image", bbox, "imagem não decorativa fora da caixa body")

        table_drawing_rects = []
        for drawing in drawings:
            bbox = drawing["rect"]
            role = "page_background" if _is_sepia_background(drawing, page_area) else "drawing"
            if _is_black_full_page(drawing, page_area):
                role = "full_bleed_background" if full_bleed else "unassigned_full_bleed"
            elif role != "page_background":
                assigned = _classify_zone(bbox, zones, 1.0)
                role = "full_bleed_art" if full_bleed else (
                    "body" if assigned == "body" else "unassigned"
                )
                if role == "body":
                    table_drawing_rects.append(bbox)
            drawing_boxes.append({"bbox": _rect_list(bbox), "role": role})
            if not _contains(page_rect, bbox, tolerance_pt):
                add_violation("drawing", bbox, "fora do MediaBox/CropBox")
            elif role != "page_background" and not full_bleed and not _contains(
                zones["safe"], bbox, tolerance_pt
            ):
                add_violation("drawing", bbox, "fora da área de corte segura")
            elif role.startswith("unassigned"):
                add_violation("drawing", bbox, "desenho não decorativo fora da caixa body")

        audited_object_count += len(text_boxes) + len(image_boxes) + len(
            [item for item in drawing_boxes if item["role"] != "page_background"]
        )
        if len(table_drawing_rects) >= 8:
            table_union = fitz.Rect(
                min(rect.x0 for rect in table_drawing_rects),
                min(rect.y0 for rect in table_drawing_rects),
                max(rect.x1 for rect in table_drawing_rects),
                max(rect.y1 for rect in table_drawing_rects),
            )
            if table_union.width >= zones["body"].width * 0.65 and table_union.height >= 20:
                table_text_sizes.extend(
                    item["size_pt"]
                    for item in text_boxes
                    if item["role"] == "body"
                    and item["is_superscript"] is False
                    and table_union.intersects(fitz.Rect(item["bbox"]))
                )

        page_reports.append(
            {
                "page_index": page_index,
                "page_label": page.get_label(),
                "dimensions_match_source_geometry": page_dimensions_match,
                "media_box": _rect_list(page.mediabox),
                "crop_box": _rect_list(page.cropbox),
                **geometry,
                "text_boxes": text_boxes,
                "image_boxes": image_boxes,
                "drawing_boxes": drawing_boxes,
                "violations": page_violations,
            }
        )

    first_page = document[0]
    dimensions_match = all_dimensions_match
    expected_full_bleed_ids = _expected_full_bleed_ids(edition)
    full_bleed_allowlist_passed = observed_full_bleed_ids == expected_full_bleed_ids
    table_minimum_text_size = min(table_text_sizes) if table_text_sizes else None
    links = sum(len(page.get_links()) for page in document)
    report = {
        "page_count": document.page_count,
        "pdf_sha256": pdf_sha256_before,
        "page_dimensions_pt": [round(first_page.rect.width, 3), round(first_page.rect.height, 3)],
        "expected_page_dimensions_pt": [
            round(edition.paper_width_pt, 3), round(edition.paper_height_pt, 3)
        ],
        "dimensions_match_source_geometry": dimensions_match,
        "all_page_dimensions_match_source_geometry": all_dimensions_match,
        "pagination": {
            "page_label_rules": labels,
            "frontmatter_style": "roman" if roman_start and len(decimal_rules) == 1 else "invalid",
            "first_fragment_page_index": decimal_start,
            "first_fragment_label": first_fragment_label,
            "first_fragment_named_destination_page": first_fragment_destination_page,
            "first_fragment_aux_label": aux_first_fragment_label,
            "first_fragment_destination_matches": first_fragment_destination_matches,
            "foliation_sequence_passed": foliation_sequence_passed,
            "duplicate_page_labels": duplicate_labels,
            "passed": bool(
                roman_start
                and len(labels) == 2
                and len(decimal_rules) == 1
                and first_fragment_label == "1"
                and first_fragment_destination_matches
                and foliation_sequence_passed
                and not duplicate_labels
            ),
        },
        "layout": {
            "tolerance_pt": tolerance_pt,
            "zone_assignment_tolerance_pt": 3.0,
            "cut_safe_inset_pt": edition.cut_safe_inset_pt,
            "audited_object_count": audited_object_count,
            "minimum_text_size_pt": round(min_text_size, 3) if min_text_size else None,
            "table_minimum_text_size_pt": (
                round(table_minimum_text_size, 3) if table_minimum_text_size else None
            ),
            "violation_count": len(violations),
            "zone_violation_count": len(
                [item for item in violations if "body/header/footer/margin_note" in item["reason"] or "caixa body" in item["reason"]]
            ),
            "violations": violations,
            "page_reports": page_reports,
            "full_bleed_exceptions": exceptions,
            "expected_full_bleed_allowlist_ids": sorted(expected_full_bleed_ids),
            "observed_full_bleed_allowlist_ids": sorted(observed_full_bleed_ids),
            "full_bleed_allowlist_passed": full_bleed_allowlist_passed,
            "passed": dimensions_match
            and not violations
            and full_bleed_allowlist_passed
            and (table_minimum_text_size is None or table_minimum_text_size >= 9.0),
        },
        "pdf_features": {
            "link_annotation_count": links,
            "outline_entry_count": len(document.get_toc(simple=True)),
        },
    }
    document.close()
    pdf_sha256_after = _sha256(edition.pdf)
    if pdf_sha256_before != pdf_sha256_after:
        raise RuntimeError(f"PDF mudou durante a auditoria: {edition.pdf}")
    return report


def _run_build(edition: Edition, passes: int = 2) -> dict[str, Any]:
    command = [
        edition.engine,
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        "-recorder",
        edition.tex,
    ]
    returncodes: list[int] = []
    durations: list[float] = []
    output_tails: list[str] = []
    for _ in range(passes):
        started = time.monotonic()
        completed = subprocess.run(
            command,
            cwd=BOOK,
            capture_output=True,
            text=True,
            errors="replace",
        )
        durations.append(round(time.monotonic() - started, 3))
        returncodes.append(completed.returncode)
        combined = completed.stdout + "\n" + completed.stderr
        output_tails.append("\n".join(combined.splitlines()[-20:]))
        if completed.returncode != 0:
            break
    report = {
        "engine": edition.engine,
        "engine_version": _engine_version(edition.engine),
        "tex_path": _rel(BOOK / edition.tex),
        "command": command,
        "passes": len(returncodes),
        "required_passes": passes,
        "returncodes": returncodes,
        "durations_seconds": durations,
        "output_tails": output_tails,
        "passed": len(returncodes) == passes and all(code == 0 for code in returncodes),
    }
    if edition.pdf.is_file():
        report["pdf_sha256"] = _sha256(edition.pdf)
    if edition.log.is_file():
        report["log_sha256"] = _sha256(edition.log)
    if edition.aux.is_file():
        report["aux_sha256"] = _sha256(edition.aux)
    if edition.fls.is_file():
        report["fls_sha256"] = _sha256(edition.fls)
        report["dependency_snapshot"] = _dependency_snapshot(edition.fls)
        if report["dependency_snapshot"]["missing_inputs"]:
            report["passed"] = False
    report["completed_at"] = datetime.now(timezone.utc).isoformat()
    return report


def _receipt_is_current(edition: Edition, receipt: dict[str, Any]) -> bool:
    return bool(
        receipt.get("passed") is True
        and receipt.get("passes") == 2
        and receipt.get("returncodes") == [0, 0]
        and receipt.get("engine") == edition.engine
        and receipt.get("engine_version") == _engine_version(edition.engine)
        and receipt.get("tex_path") == _rel(BOOK / edition.tex)
        and edition.pdf.is_file()
        and edition.log.is_file()
        and edition.aux.is_file()
        and edition.fls.is_file()
        and receipt.get("pdf_sha256") == _sha256(edition.pdf)
        and receipt.get("log_sha256") == _sha256(edition.log)
        and receipt.get("aux_sha256") == _sha256(edition.aux)
        and receipt.get("fls_sha256") == _sha256(edition.fls)
        and _dependency_snapshot_is_current(receipt.get("dependency_snapshot", {}))
    )


def _load_build_receipts() -> dict[str, Any]:
    if not BUILD_RECEIPTS_PATH.is_file():
        return {}
    try:
        payload = json.loads(BUILD_RECEIPTS_PATH.read_text(encoding="utf-8"))
        return payload.get("editions", {}) if payload.get("spec_id") == "SPEC-935-R362" else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_build_receipts(receipts: dict[str, Any]) -> None:
    _atomic_write(
        BUILD_RECEIPTS_PATH,
        {
            "spec_id": "SPEC-935-R362",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "editions": receipts,
        },
    )


def _run_builds(jobs: int) -> dict[str, Any]:
    receipts = _load_build_receipts()
    if jobs <= 1:
        for key, edition in EDITIONS.items():
            receipts[key] = _run_build(edition)
            _save_build_receipts(receipts)
        return receipts

    with ThreadPoolExecutor(max_workers=min(jobs, len(EDITIONS))) as executor:
        futures = {executor.submit(_run_build, edition): key for key, edition in EDITIONS.items()}
        for future in as_completed(futures):
            key = futures[future]
            try:
                receipts[key] = future.result()
            except Exception as exc:  # fail-closed; preserva diagnóstico dos demais
                receipts[key] = {
                    "engine": EDITIONS[key].engine,
                    "tex_path": _rel(BOOK / EDITIONS[key].tex),
                    "passes": 0,
                    "returncodes": [],
                    "passed": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            _save_build_receipts(receipts)
    return receipts


def _source_checks() -> tuple[dict[str, Any], dict[str, Any]]:
    forbidden_counts = re.compile(
        r"(?:8[\.,]240|7[\.,]912|4[\.,]712|3[\.,]200|80\\?%|"
        r"dois terços|two thirds|三分之二)", re.IGNORECASE
    )
    disclaimers = {"pt": "Reconstituição ficcional", "en": "Fictional reconstruction", "zh": "虚构重构"}
    route_markers = {
        "pt": ("de Senador Pompeu a Fortaleza", "Campo do Alagadiço"),
        "en": ("from Senador Pompeu to Fortaleza", "Alagadiço"),
        "zh": ("塞纳多尔", "Alagadiço"),
    }
    forbidden_route_phrases = (
        "Curral do Governo em Senador Pompeu", "Curral do Governo de Senador Pompeu",
        "Campo de Concentração de Senador Pompeu", "Government Pen in Senador Pompeu",
        "Government Pen of Senador Pompeu", "Senador Pompeu Concentration Camp",
        "塞纳多尔·蓬佩乌的政府牲畜圈", "塞纳多尔·蓬佩乌集中营",
        "1915-1917", "1915--1917", "1915—1917",
    )
    details: dict[str, Any] = {}
    all_passed = True
    for language, language_root in LANGUAGE_ROOTS.items():
        corpus = "\n".join((BOOK / language_root / relative).read_text(encoding="utf-8") for relative in ROUTE_FILES)
        mem02 = (BOOK / language_root / "mem/MEM-02.tex").read_text(encoding="utf-8")
        mem04 = (BOOK / language_root / "mem/MEM-04.tex").read_text(encoding="utf-8")
        mem06 = (BOOK / language_root / "mem/MEM-06.tex").read_text(encoding="utf-8")
        route_marker, camp_marker = route_markers[language]
        pseudoarchives_ok = all(
            disclaimers[language] in (BOOK / language_root / relative).read_text(encoding="utf-8")
            for relative in ("doc/DOC-02.tex", "doc/DOC-17.tex", "doc/DOC-18.tex")
        )
        language_result = {
            "route_origin_and_destination": route_marker in mem02,
            "fortaleza_present": "Fortaleza" in mem02 + mem04 + mem06 or "福塔莱萨" in mem02 + mem04 + mem06,
            "alagadico_confinement": camp_marker in mem04 and camp_marker in mem06,
            "forbidden_route_phrases": [item for item in forbidden_route_phrases if item in corpus],
            "unsupported_exact_counts": forbidden_counts.findall(corpus),
            "pseudoarchives_marked_fictional": pseudoarchives_ok,
        }
        language_result["passed"] = bool(
            language_result["route_origin_and_destination"]
            and language_result["fortaleza_present"]
            and language_result["alagadico_confinement"]
            and not language_result["forbidden_route_phrases"]
            and not language_result["unsupported_exact_counts"]
            and pseudoarchives_ok
        )
        details[language] = language_result
        all_passed = all_passed and language_result["passed"]

    active_tex_paths: set[Path] = set()
    for edition in EDITIONS.values():
        if not edition.fls.is_file():
            continue
        for record in _dependency_snapshot(edition.fls)["inputs"]:
            path = _path_from_record(record)
            try:
                relative = path.resolve().relative_to(BOOK.resolve())
            except ValueError:
                continue
            if path.suffix == ".tex" and "_archive" not in relative.parts:
                active_tex_paths.add(path.resolve())
    active_forbidden = []
    active_counts = []
    for path in sorted(active_tex_paths):
        text = path.read_text(encoding="utf-8", errors="replace")
        for phrase in forbidden_route_phrases:
            if phrase in text:
                active_forbidden.append(
                    {"path": str(path.relative_to(ROOT)), "match": phrase}
                )
        for match in forbidden_counts.finditer(text):
            active_counts.append(
                {"path": str(path.relative_to(ROOT)), "match": match.group(0)}
            )
    active_dependency_corpus = {
        "basis": "workspace INPUT *.tex dos cinco arquivos FLS canônicos",
        "tex_file_count": len(active_tex_paths),
        "forbidden_route_occurrences": active_forbidden,
        "unsupported_exact_count_occurrences": active_counts,
        "passed": bool(active_tex_paths and not active_forbidden and not active_counts),
    }
    all_passed = all_passed and active_dependency_corpus["passed"]

    masters = ["main.tex", "en/main_en.tex", "zh/main_zh.tex", "tri/main_tri.tex"]
    class_checks = {}
    for relative in masters:
        text = (BOOK / relative).read_text(encoding="utf-8")
        class_checks[relative] = bool(re.search(r"\\documentclass\[14pt(?:,|\])", text))
    option_checks = {}
    for relative in ("misc/options.sty", "misc/options_zh.sty"):
        text = (BOOK / relative).read_text(encoding="utf-8")
        table_definitions = re.findall(
            r"\\newenvironment\{moltable(?:three|four|five|six)\}.*?"
            r"\\end\{supertabular\}\\endgroup\}",
            text,
            re.DOTALL,
        )
        option_checks[relative] = {
            "baseline_1_25": r"\renewcommand{\baselinestretch}{1.25}" in text,
            "document_table_definition_count": len(table_definitions),
            "all_document_tables_use_footnotesize": len(table_definitions) == 4
            and all(r"\begingroup\footnotesize" in match for match in table_definitions),
        }
    typography_passed = all(class_checks.values()) and all(
        item["baseline_1_25"] and item["all_document_tables_use_footnotesize"]
        for item in option_checks.values()
    )
    typography = {
        "global_narrative_class": "14pt",
        "global_narrative_size_preserved": typography_passed,
        "baseline_stretch": "1.25",
        "table_minimum": r"\footnotesize",
        "master_checks": class_checks,
        "option_checks": option_checks,
        "passed": typography_passed,
    }
    return {
        "historical_route_a": details,
        "active_dependency_corpus": active_dependency_corpus,
        "passed": all_passed,
    }, typography


def _source_route_multisets() -> dict[str, Counter[str]]:
    pattern = re.compile(r"\\rota\{([A-Z]{3,4}-(?:\d+|[A-Za-z][A-Za-z-]*))\}")
    result: dict[str, Counter[str]] = {}
    for language, relative_root in LANGUAGE_ROOTS.items():
        counter: Counter[str] = Counter()
        for path in sorted((BOOK / relative_root).rglob("*.tex")):
            if "_archive" in path.parts:
                continue
            counter.update(pattern.findall(path.read_text(encoding="utf-8", errors="replace")))
        result[language] = counter
    return result


def _validate_edition_routes(
    edition: Edition, source_routes: dict[str, Counter[str]]
) -> dict[str, Any]:
    from scripts.validate_molambudos_routes import (
        LEGACY_NUMERIC_ID_RE,
        duplicate_aux_labels,
        extract_printed_routes,
        parse_aux_labels,
    )

    completed = subprocess.run(
        ["pdftotext", "-layout", str(edition.pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    aux_text = edition.aux.read_text(encoding="utf-8")
    labels = parse_aux_labels(aux_text)
    duplicates = duplicate_aux_labels(aux_text)
    printed = extract_printed_routes(completed.stdout)
    single_language = edition.key if edition.key in {"pt", "en", "zh"} else None
    prefix_language = {"frag:": "pt", "fragen:": "en", "fragzh:": "zh"}
    expected_languages = [single_language] if single_language else ["pt", "en", "zh"]
    printed_by_language: dict[str, Counter[str]] = {
        language: Counter() for language in expected_languages if language
    }
    missing = []
    divergences = []
    for route in printed:
        language = single_language or prefix_language[route["prefix"]]
        printed_by_language[language].update([route["fragment_id"]])
        label = ("frag:" if single_language else route["prefix"]) + route["fragment_id"]
        if label not in labels:
            missing.append(
                {
                    "label": label,
                    "printed_page": route["printed_page"],
                    "source_line": route["source_line"],
                }
            )
        elif labels[label] != route["printed_page"]:
            divergences.append(
                {
                    "label": label,
                    "printed_page": route["printed_page"],
                    "aux_page": labels[label],
                }
            )
    source_multiset_match = all(
        printed_by_language.get(language, Counter()) == source_routes[language]
        for language in expected_languages
        if language
    )
    expected_total = sum(sum(source_routes[language].values()) for language in expected_languages if language)
    by_language = {
        language: sum(printed_by_language.get(language, Counter()).values())
        for language in ("pt", "en", "zh")
        if language in expected_languages
    }
    canonical_multiset = {
        language: sorted(counter.items()) for language, counter in printed_by_language.items()
    }
    passed = bool(
        len(printed) == expected_total
        and not duplicates
        and not missing
        and not divergences
        and source_multiset_match
    )
    return {
        "expected": expected_total,
        "total": len(printed),
        "valid": len(printed) - len(missing) - len(divergences),
        "by_language": by_language,
        "missing": missing,
        "divergences": divergences,
        "duplicate_labels": duplicates,
        "source_multiset_match": source_multiset_match,
        "printed_multiset_sha256": hashlib.sha256(
            json.dumps(canonical_multiset, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "legacy_numeric_routes": sum(
            1 for route in printed if LEGACY_NUMERIC_ID_RE.fullmatch(route["fragment_id"])
        ),
        "passed": passed,
    }


def _route_report() -> dict[str, Any]:
    try:
        source_routes = _source_route_multisets()
        editions = {
            key: _validate_edition_routes(edition, source_routes)
            for key, edition in EDITIONS.items()
        }
        tri = editions["tri"]
        by_language = {language: tri["by_language"].get(language, 0) for language in ("pt", "en", "zh")}
        missing = len(tri["missing"])
        divergent = len(tri["divergences"])
        # O corpus cresce entre ciclos (novos fragmentos, novos \rota{} restaurados
        # em rotas antes só em texto puro) — fixar 180/540 como número mágico
        # reproduziria o mesmo problema já corrigido no R358 para a contagem de
        # fragmentos. A invariante real e estável é: PT/EN/ZH devem ter sempre a
        # mesma contagem de rotas entre si (paridade trilíngue), e o total deve
        # bater com essa contagem × 3.
        language_counts = set(by_language.values())
        languages_match = len(language_counts) == 1 and next(iter(language_counts)) > 0
        expected_total = by_language["pt"] * 3
        passed = bool(
            all(item["passed"] for item in editions.values())
            and languages_match
            and tri["total"] == expected_total
        )
        return {
            "expected": expected_total,
            "total": tri["total"],
            "valid": tri["valid"],
            "by_language": by_language,
            "missing": missing,
            "divergent": divergent,
            "legacy_numeric_routes": tri["legacy_numeric_routes"],
            "source_route_counts": {
                language: sum(counter.values()) for language, counter in source_routes.items()
            },
            "editions": editions,
            "passed": passed,
        }
    except Exception as exc:  # fail-closed e artefato diagnóstico
        return {
            "expected": 540,
            "total": 0,
            "valid": 0,
            "by_language": {"pt": 0, "en": 0, "zh": 0},
            "missing": 540,
            "divergent": 0,
            "editions": {},
            "passed": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
        directory_fd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary = Path(temporary_name)
        if temporary.exists():
            temporary.unlink()


def generate_preflight(
    *, build: bool, jobs: int, tolerance_pt: float, output: Path
) -> dict[str, Any]:
    build_receipts = _run_builds(jobs) if build else _load_build_receipts()
    source_checks, typography = _source_checks()
    reports: dict[str, Any] = {}
    for key, edition in EDITIONS.items():
        stored_receipt = build_receipts.get(key, {})
        build_report = dict(stored_receipt)
        build_report["receipt_current"] = _receipt_is_current(edition, stored_receipt)
        build_report["passed"] = build_report["receipt_current"]
        if not stored_receipt:
            build_report.update(
                {
                    "engine": edition.engine,
                    "passes": 0,
                    "required_passes": 2,
                    "returncodes": [],
                    "passed": False,
                    "reason": "recibo verificável de duas passadas ausente",
                }
            )
        report: dict[str, Any] = {
            "tex_path": _rel(BOOK / edition.tex),
            "pdf_path": _rel(edition.pdf),
            "log_path": _rel(edition.log),
            "aux_path": _rel(edition.aux),
            "fls_path": _rel(edition.fls),
            "build": build_report,
        }
        try:
            for required in (edition.log, edition.aux, edition.fls):
                if not required.is_file():
                    raise FileNotFoundError(required)
            log_sha256 = _sha256(edition.log)
            aux_sha256 = _sha256(edition.aux)
            fls_sha256 = _sha256(edition.fls)
            report["log"] = parse_latex_log(
                edition.log.read_text(encoding="utf-8", errors="replace")
            )
            report.update(_audit_pdf(edition, tolerance_pt))
            if (
                log_sha256 != _sha256(edition.log)
                or aux_sha256 != _sha256(edition.aux)
                or fls_sha256 != _sha256(edition.fls)
            ):
                raise RuntimeError(f"log/AUX/FLS mudou durante a auditoria: {edition.jobname}")
            report["log_sha256"] = log_sha256
            report["aux_sha256"] = aux_sha256
            report["fls_sha256"] = fls_sha256
        except Exception as exc:
            report.setdefault("log", {"passed": False})
            report.setdefault("pagination", {
                "frontmatter_style": "invalid",
                "first_fragment_label": None,
                "duplicate_page_labels": [],
                "passed": False,
            })
            report.setdefault("layout", {
                "violation_count": 1,
                "violations": [{"reason": f"{type(exc).__name__}: {exc}"}],
                "page_reports": [],
                "full_bleed_exceptions": [],
                "audited_object_count": 0,
                "passed": False,
            })
            report["audit_error"] = f"{type(exc).__name__}: {exc}"
        reports[key] = report

    routes = _route_report()
    kdp_pages = reports.get("kdp_tri", {}).get("page_count")
    kdp_limit = 828
    internal_passed = bool(
        source_checks["passed"]
        and typography["passed"]
        and routes["passed"]
        and all(
            report.get("build", {}).get("passed") is True
            and report.get("log", {}).get("passed") is True
            and report.get("pagination", {}).get("passed") is True
            and report.get("layout", {}).get("passed") is True
            for report in reports.values()
        )
    )
    payload = {
        "spec_id": "SPEC-935-R362",
        "generated_at": "2026-08-01",
        "external_validation": False,
        "human_review_required": True,
        "release_gate": "blocked",
        "quality_verdict_allowed": False,
        "overall_internal_spec_passed": internal_passed,
        "build_receipts_path": _rel(BUILD_RECEIPTS_PATH),
        "build_receipts_sha256": (
            _sha256(BUILD_RECEIPTS_PATH) if BUILD_RECEIPTS_PATH.is_file() else None
        ),
        "source_checks": source_checks,
        "source_typography": typography,
        "editions": reports,
        "routes": routes,
        "publication_constraints": {
            "release_allowed": False,
            "kdp_tri_page_count": kdp_pages,
            "kdp_assumed_max_page_count": kdp_limit,
            "kdp_page_limit_passed": bool(isinstance(kdp_pages, int) and kdp_pages <= kdp_limit),
            "kdp_pages_over_assumed_limit": (
                max(0, kdp_pages - kdp_limit) if isinstance(kdp_pages, int) else None
            ),
            "note": "O limite depende da configuração comercial final e não foi validado externamente nesta rodada; o release permanece bloqueado.",
        },
        "safe_claim": (
            "O preflight mede conformidade técnica interna da SPEC-935-R362. "
            "Não confere validação histórica/cultural externa, qualidade literária "
            "nem autorização de publicação."
        ),
    }
    _atomic_write(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--build",
        action="store_true",
        help="compila cada edição exatamente duas vezes antes da auditoria",
    )
    parser.add_argument("--tolerance-pt", type=float, default=1.0)
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="número de edições compiladas em paralelo quando --build é usado",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = generate_preflight(
        build=args.build,
        jobs=max(1, args.jobs),
        tolerance_pt=args.tolerance_pt,
        output=args.output.resolve(),
    )
    print(
        json.dumps(
            {
                "spec_id": payload["spec_id"],
                "overall_internal_spec_passed": payload["overall_internal_spec_passed"],
                "release_gate": payload["release_gate"],
                "output": str(args.output.resolve()),
            },
            ensure_ascii=False,
        )
    )
    return 0 if payload["overall_internal_spec_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
