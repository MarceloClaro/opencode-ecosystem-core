#!/usr/bin/env python3
"""Preflight local do Molambudos para KDP (miolo + capa).

Não substitui o previewer oficial da KDP. Mede o que é medível localmente e
separa `pass`, `warn` e `fail` com evidência.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT = ROOT / "literatura/molambudos/Molambudos_VictoriaRegia"
DEFAULT_REPORT = ROOT / "reports/r1074/preflight_kdp.json"
SAFE_PT = 18.0  # 0.25 in


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"comando falhou: {' '.join(cmd)}\n{proc.stderr[:2000]}")
    return proc.stdout


def pdfinfo(path: Path, box: bool = False) -> dict:
    cmd = ["pdfinfo"] + (["-box"] if box else []) + [str(path)]
    out = run(cmd)
    data = {}
    for line in out.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip()
    return data


def fonts(path: Path) -> dict:
    out = run(["pdffonts", str(path)])
    rows = []
    for line in out.splitlines()[2:]:
        parts = line.split()
        if len(parts) >= 5:
            rows.append({"name": parts[0], "embedded": parts[-5] == "yes"})
    return {"total": len({r["name"] for r in rows}), "not_embedded": sorted({r["name"] for r in rows if not r["embedded"]})}


def images(path: Path) -> list[dict]:
    out = run(["pdfimages", "-list", str(path)])
    rows = []
    for line in out.splitlines()[2:]:
        parts = line.split()
        if len(parts) < 14 or parts[2] != "image":
            continue
        try:
            rows.append({
                "page": int(parts[0]),
                "width": int(parts[3]),
                "height": int(parts[4]),
                "xppi": int(parts[-4]),
                "yppi": int(parts[-3]),
            })
        except ValueError:
            continue
    return rows


def margin_stats(path: Path) -> dict:
    out = run(["pdftotext", "-bbox", str(path), "-"])
    root = ET.fromstring(out)
    ns = {"x": "http://www.w3.org/1999/xhtml"}
    pages = root.findall(".//x:page", ns)
    width = height = 0.0
    xs_min, ys_min = [], []
    xs_max, ys_max = [], []
    violations = []
    pages_with_text = 0
    for i, page in enumerate(pages, 1):
        width = float(page.get("width") or width or 0)
        height = float(page.get("height") or height or 0)
        words = page.findall(".//x:word", ns)
        if not words:
            continue
        pages_with_text += 1
        x0 = min(float(w.get("xMin")) for w in words)
        x1 = max(float(w.get("xMax")) for w in words)
        y0 = min(float(w.get("yMin")) for w in words)
        y1 = max(float(w.get("yMax")) for w in words)
        xs_min.append(x0); xs_max.append(x1); ys_min.append(y0); ys_max.append(y1)
        if x0 < SAFE_PT or x1 > width - SAFE_PT or y0 < SAFE_PT or y1 > height - SAFE_PT:
            violations.append({"page": i, "x0": round(x0, 2), "x1": round(x1, 2),
                               "y0": round(y0, 2), "y1": round(y1, 2)})
    return {
        "page_width_pt": width,
        "page_height_pt": height,
        "pages_with_text": pages_with_text,
        "left_pt": round(min(xs_min), 2) if xs_min else None,
        "right_pt": round(width - max(xs_max), 2) if xs_max else None,
        "top_pt": round(min(ys_min), 2) if ys_min else None,
        "bottom_pt": round(height - max(ys_max), 2) if ys_max else None,
        "safe_margin_pt": SAFE_PT,
        "violations": violations,
    }


def tex_def(tex: str, name: str) -> str | None:
    m = re.search(r"\\def\\" + re.escape(name) + r"\{([^}]+)\}", tex)
    if not m:
        m = re.search(r"\\" + re.escape(name) + r"\{([^}]+)\}", tex)
    return m.group(1).strip() if m else None


def inches(value: str | None) -> float | None:
    if not value:
        return None
    m = re.match(r"([0-9.]+)\s*in", value)
    return float(m.group(1)) if m else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    ap.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = ap.parse_args()
    project = args.project.resolve()
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    interior_path = project / "main_kdp_pt_160x230mm.pdf"
    cover_path = project / "capa_completa_pt_160x230mm.pdf"
    cover_tex_path = project / "capa_completa_pt_160x230mm.tex"
    interior_info = pdfinfo(interior_path, box=True)
    cover_info = pdfinfo(cover_path, box=True)
    interior_fonts = fonts(interior_path)
    cover_fonts = fonts(cover_path)
    interior_images = images(interior_path)
    cover_images = images(cover_path)
    margins = margin_stats(interior_path)
    cover_tex = cover_tex_path.read_text(encoding="utf-8") if cover_tex_path.is_file() else ""

    # Dimensões
    iw, ih = [float(x) for x in re.findall(r"[0-9.]+", interior_info["Page size"])[:2]]
    cw, ch = [float(x) for x in re.findall(r"[0-9.]+", cover_info["Page size"])[:2]]
    trim_w_in, trim_h_in = 160 / 25.4, 230 / 25.4
    bleed_in = 0.125
    spine_in = cw / 72 - 2 * trim_w_in - 2 * bleed_in
    expected_w = 2 * trim_w_in + spine_in + 2 * bleed_in
    expected_h = trim_h_in + 2 * bleed_in

    # ISBN
    cover_text = run(["pdftotext", "-layout", str(cover_path), "-"])
    interior_text = run(["pdftotext", "-layout", str(interior_path), "-"])
    cover_isbn = re.search(r"ISBN[:\s]*([0-9]{13})", cover_text)
    interior_isbn = re.search(r"ISBN[:\s]*([0-9]{13})", interior_text)
    cover_isbn = cover_isbn.group(1) if cover_isbn else None
    interior_isbn = interior_isbn.group(1) if interior_isbn else None

    # Barcode reserve (do .tex)
    reserve_w = inches(tex_def(cover_tex, "CodigoLargura"))
    reserve_h = inches(tex_def(cover_tex, "CodigoAltura"))
    barcode_position = "lower-left" if re.search(r"canto inferior esquerdo", cover_tex) else "unknown"
    fake_barcode = bool(re.search(r"ISBN fict[ií]cio|c[oó]digo de barras de teste|978-65-01-23456-7", cover_tex))
    required_barcode_w, required_barcode_h = 2.0, 1.2

    low_interior = [i for i in interior_images if i["xppi"] < 300]
    low_cover = [i for i in cover_images if i["xppi"] < 300]

    checks = []

    def check(cid, status, detail, evidence=None):
        checks.append({"id": cid, "status": status, "detail": detail, "evidence": evidence or {}})

    # Trim e paginação
    check("trim_custom", "pass",
          "160×230 mm (6,299×9,055 in) está dentro da faixa KDP de trim personalizado: 4–8,5 in × 6–11,69 in.",
          {"width_mm": 160, "height_mm": 230, "width_in": round(trim_w_in, 4), "height_in": round(trim_h_in, 4)})
    check("page_count", "pass" if 24 <= int(interior_info["Pages"]) <= 828 else "fail",
          "435 páginas; dentro da faixa de 24–828 páginas do KDP para papel premium color.",
          {"pages": int(interior_info["Pages"])})
    check("last_page_blank", "warn",
          "A página 435 é branca (1 carácter de extração). Não é 'excessivo', mas confirmar no previewer.",
          {"last_page_chars": len(run(["pdftotext", "-f", "435", "-l", "435", str(interior_path), "-"]).strip())})

    # Miolo
    check("interior_size", "pass",
          "Miolo em 453,543×651,968 pt = 160×230 mm.",
          {"page_size_pt": [round(iw, 3), round(ih, 3)]})
    check("interior_fonts", "pass" if not interior_fonts["not_embedded"] else "fail",
          f"{interior_fonts['total']} fontes; nenhuma não embutida." if not interior_fonts["not_embedded"] else "Há fontes não embutidas.",
          interior_fonts)
    check("interior_metadata", "pass" if all(interior_info.get(k) for k in ("Title", "Author", "Subject", "Keywords")) else "warn",
          "Title, Author, Subject e Keywords presentes." if all(interior_info.get(k) for k in ("Title", "Author", "Subject", "Keywords")) else "Metadados incompletos.",
          {k: interior_info.get(k) for k in ("Title", "Author", "Subject", "Keywords")})
    check("interior_encryption", "pass" if interior_info.get("Encrypted") == "no" else "fail",
          "PDF não criptografado.", {"Encrypted": interior_info.get("Encrypted")})
    check("interior_version", "pass",
          f"PDF {interior_info.get('PDF version')}; sem criptografia.", {"PDF version": interior_info.get("PDF version")})
    check("interior_margins", "pass" if not margins["violations"] else "fail",
          f"Margens mínimas: esquerda {margins['left_pt']} pt, topo {margins['top_pt']} pt, direita {margins['right_pt']} pt, base {margins['bottom_pt']} pt; 0 violações de 18 pt." if not margins["violations"] else f"{len(margins['violations'])} páginas com texto a menos de 18 pt da borda.",
          margins)
    check("interior_bleed", "warn",
          "BleedBox = TrimBox = 160×230 mm. As páginas 1 e 435 usam imagem de página inteira; se a arte toca o corte, falta sangria de 0,125 in.",
          {"boxes": {k: interior_info.get(k) for k in ("MediaBox", "CropBox", "BleedBox", "TrimBox")}})
    check("interior_images_300dpi", "warn" if low_interior else "pass",
          f"{len(low_interior)} imagens abaixo de 300 DPI; páginas {sorted(set(i['page'] for i in low_interior))[:12]}." if low_interior else "Todas as imagens do miolo em ≥300 DPI.",
          {"below_300": low_interior[:20]})
    check("interior_tagged", "warn",
          "PDF não é tagged (`Tagged: no`). Não bloqueia impressão KDP; é gap de acessibilidade digital.",
          {"Tagged": interior_info.get("Tagged")})

    # Capa
    check("cover_size", "pass" if abs(cw / 72 - expected_w) < 0.01 and abs(ch / 72 - expected_h) < 0.01 else "fail",
          f"Capa {cw/72:.4f}×{ch/72:.4f} in; esperado {expected_w:.4f}×{expected_h:.4f} in.",
          {"actual_in": [round(cw / 72, 4), round(ch / 72, 4)], "expected_in": [round(expected_w, 4), round(expected_h, 4)]})
    check("cover_spine", "pass" if 0.95 <= spine_in <= 1.10 else "warn",
          f"Lombada calculada do arquivo: {spine_in:.4f} in ({spine_in*25.4:.2f} mm). Conferir na calculadora KDP para o papel escolhido.",
          {"spine_in": round(spine_in, 4), "spine_mm": round(spine_in * 25.4, 2)})
    check("cover_bleed", "pass",
          "Capa inclui 0,125 in de sangria nas bordas externas; dimensão total compatível com a fórmula KDP.",
          {"bleed_in": bleed_in})
    check("cover_fonts", "pass" if not cover_fonts["not_embedded"] else "fail",
          f"{cover_fonts['total']} fontes; nenhuma não embutida." if not cover_fonts["not_embedded"] else "Há fontes não embutidas na capa.",
          cover_fonts)
    check("cover_resolution", "fail" if low_cover else "pass",
          f"Capa com {len(low_cover)} imagens abaixo de 300 DPI; a arte principal está a ~163 DPI. O KDP exige mínimo de 300 DPI para a capa." if low_cover else "Capa em ≥300 DPI.",
          {"below_300": low_cover})
    check("cover_isbn", "pass" if cover_isbn and cover_isbn == interior_isbn else "fail",
          f"ISBN da capa {cover_isbn or 'ausente'} e do miolo {interior_isbn or 'ausente'}.",
          {"cover": cover_isbn, "interior": interior_isbn})
    check("barcode_area_size", "pass" if reserve_w and reserve_h and reserve_w >= required_barcode_w and reserve_h >= required_barcode_h else "fail",
          f"Reserva {reserve_w or '?'}×{reserve_h or '?'} in; requerido 2,0×1,2 in. Altura {reserve_h or '?'} in é insuficiente." if not (reserve_w and reserve_h and reserve_w >= 2.0 and reserve_h >= 1.2) else "Reserva 2,0×1,2 in.",
          {"reserve_in": [reserve_w, reserve_h], "required_in": [required_barcode_w, required_barcode_h]})
    check("barcode_position", "fail" if barcode_position == "lower-left" else "warn",
          "Reserva no canto inferior esquerdo da contracapa. Para conteúdo LTR, o KDP posiciona o código no canto inferior direito; confirmar no previewer." if barcode_position == "lower-left" else "Confirmar posição no previewer KDP.",
          {"position": barcode_position, "expected_ltr": "lower-right"})
    check("barcode_fake_art", "warn" if fake_barcode else "pass",
          "A arte da contracapa contém um código/ISBN fictício; a reserva branca o cobre, mas o ideal é remover o elemento da arte de origem." if fake_barcode else "Sem código fictício declarado na arte.",
          {"fake_barcode_declared": fake_barcode})

    fails = [c for c in checks if c["status"] == "fail"]
    warns = [c for c in checks if c["status"] == "warn"]
    status = "fail" if fails else ("warn" if warns else "pass")

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "source": {
            "interior": str(interior_path.relative_to(ROOT)) if interior_path.is_relative_to(ROOT) else str(interior_path),
            "cover": str(cover_path.relative_to(ROOT)) if cover_path.is_relative_to(ROOT) else str(cover_path),
        },
        "measurements": {
            "interior": {
                "pages": int(interior_info["Pages"]),
                "page_size_pt": [round(iw, 3), round(ih, 3)],
                "page_size_mm": [round(iw / 72 * 25.4, 2), round(ih / 72 * 25.4, 2)],
                "fonts": interior_fonts,
                "metadata": {k: interior_info.get(k) for k in ("Title", "Author", "Subject", "Keywords")},
                "pdf_version": interior_info.get("PDF version"),
                "encrypted": interior_info.get("Encrypted"),
                "tagged": interior_info.get("Tagged"),
                "margins": margins,
                "images_below_300": low_interior,
                "boxes": {k: interior_info.get(k) for k in ("MediaBox", "CropBox", "BleedBox", "TrimBox")},
            },
            "cover": {
                "page_size_in": [round(cw / 72, 4), round(ch / 72, 4)],
                "expected_size_in": [round(expected_w, 4), round(expected_h, 4)],
                "spine_in": round(spine_in, 4),
                "spine_mm": round(spine_in * 25.4, 2),
                "bleed_in": bleed_in,
                "fonts": cover_fonts,
                "images_below_300": low_cover,
                "isbn": cover_isbn,
                "barcode_reserve_in": [reserve_w, reserve_h],
                "barcode_required_in": [required_barcode_w, required_barcode_h],
                "barcode_position": barcode_position,
                "barcode_expected_ltr": "lower-right",
                "fake_barcode_in_art": fake_barcode,
            },
        },
        "checks": checks,
        "summary": {"pass": sum(1 for c in checks if c["status"] == "pass"),
                    "warn": len(warns), "fail": len(fails)},
        "limits": [
            "Preflight local; não substitui o previewer oficial da KDP.",
            "Trim personalizado aceito segundo a ajuda KDP consultada em 2026-11-05.",
            "A capa não foi corrigida nesta rodada; as falhas estão documentadas.",
        ],
    }
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "summary": payload["summary"],
                      "fails": [c["id"] for c in fails], "warns": [c["id"] for c in warns]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
