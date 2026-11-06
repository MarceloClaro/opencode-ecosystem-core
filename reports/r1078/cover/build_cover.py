#!/usr/bin/env python3
"""Gera a capa print-safe do Molambudos com WeasyPrint + cairosvg.

Sem PyMuPDF, sem svglib e sem upscale. A frente é vetorial e é re-renderizada;
a contracapa é posicionada com ``contain`` e continua exigindo re-layout.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from marceloclaro.bookstudio import kdp_cover_spec  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_html(spec, front_uri: str, back_uri: str, title: str, author: str,
               guides: bool) -> str:
    bleed = spec.bleed_in
    tw, th = spec.trim_width_in, spec.trim_height_in
    spine = spec.spine_in
    front_left = bleed + tw + spine
    back_left = bleed
    spine_left = bleed + tw
    safe = spec.safe_margin_in
    bc_w, bc_h = spec.barcode_area_in
    bc_left = back_left + tw - bc_w - 0.25
    bc_top = bleed + th - bc_h - 0.25
    guide_css = ""
    if guides:
        guide_css = f"""
.guide {{ position:absolute; border:0.5pt dashed #FF4D4D; }}
.safe {{ position:absolute; border:0.4pt dotted #7FD1C8; }}
.label {{ position:absolute; left:0.18in; top:0.18in; background:#fff; color:#111;
          font-size:7pt; padding:3pt 5pt; border:0.5pt solid #FF4D4D; }}
.note {{ position:absolute; left:{back_left + 0.15:.4f}in; bottom:0.16in;
         width:{tw - 0.3:.4f}in; color:#f2e8cf; font-size:6.5pt; text-align:center; }}
"""
    guides_html = ""
    if guides:
        guides_html = f"""
<div class="guide" style="left:{back_left:.4f}in; top:{bleed:.4f}in; width:{tw:.4f}in; height:{th:.4f}in;"></div>
<div class="guide" style="left:{spine_left:.4f}in; top:{bleed:.4f}in; width:{spine:.4f}in; height:{th:.4f}in;"></div>
<div class="guide" style="left:{front_left:.4f}in; top:{bleed:.4f}in; width:{tw:.4f}in; height:{th:.4f}in;"></div>
<div class="safe" style="left:{back_left+safe:.4f}in; top:{bleed+safe:.4f}in; width:{tw-2*safe:.4f}in; height:{th-2*safe:.4f}in;"></div>
<div class="safe" style="left:{front_left+safe:.4f}in; top:{bleed+safe:.4f}in; width:{tw-2*safe:.4f}in; height:{th-2*safe:.4f}in;"></div>
<div class="label">TEMPLATE KDP · {spec.page_count} pp · {tw:.3f}×{th:.3f} in · lombada {spine:.4f} in · bleed {bleed:.3f} in · NÃO É ARTE FINAL</div>
<div class="note">Contracapa atual: 1050 × 1900 px (proporção 0,553) — re-layout necessário para {tw:.3f} × {th:.3f} in (0,696). Barcode antigo no canto inferior esquerdo precisa sair.</div>
"""
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<style>
@page {{ size: {spec.full_cover_width_in:.4f}in {spec.full_cover_height_in:.4f}in; margin: 0; }}
html, body {{ margin:0; padding:0; width:{spec.full_cover_width_in:.4f}in; height:{spec.full_cover_height_in:.4f}in; }}
body {{ background: radial-gradient(circle at 50% 36%, #241a10 0%, #140e08 55%, #060402 100%);
        font-family: "DejaVu Sans", sans-serif; }}
.panel {{ position:absolute; overflow:hidden; }}
.front {{ left:{front_left:.4f}in; top:{bleed:.4f}in; width:{tw:.4f}in; height:{th:.4f}in;
          background-image:url("{front_uri}"); background-size:100% 100%; background-repeat:no-repeat; }}
.back {{ left:{back_left:.4f}in; top:{bleed:.4f}in; width:{tw:.4f}in; height:{th:.4f}in;
         background-image:url("{back_uri}"); background-size:contain; background-position:center; background-repeat:no-repeat; }}
.spine {{ left:{spine_left:.4f}in; top:{bleed:.4f}in; width:{spine:.4f}in; height:{th:.4f}in;
          border-left:0.4pt solid #d8b876; border-right:0.4pt solid #d8b876; }}
.spine .rot {{ position:absolute; left:50%; top:50%;
               transform: translate(-50%,-50%) rotate(-90deg); white-space:nowrap;
               color:#d8b876; font-family: Georgia, "Liberation Serif", serif;
               font-weight:700; font-size:11pt; letter-spacing:1.5pt; }}
.barcode {{ position:absolute; left:{bc_left:.4f}in; top:{bc_top:.4f}in;
            width:{bc_w:.4f}in; height:{bc_h:.4f}in; background:#fff;
            border:0.6pt dashed #FF4D4D; color:#111; font-size:6.5pt;
            text-align:center; padding-top:0.45in; box-sizing:border-box; }}
{guide_css}
</style></head><body>
<div class="panel front"></div>
<div class="panel back"></div>
<div class="panel spine"><div class="rot">{html.escape(title)} · {html.escape(author)}</div></div>
<div class="barcode">ÁREA DO CÓDIGO DE BARRAS<br>2 × 1,2 in</div>
{guides_html}
</body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", type=int, default=422)
    parser.add_argument("--trim", default="160x230mm")
    parser.add_argument("--paper", choices=("white", "cream"), default="white")
    parser.add_argument("--ink", choices=("bw", "standard_color", "premium_color"),
                        default="premium_color")
    parser.add_argument("--front", type=Path, default=ROOT / "Molambudos_Capa_Frente_Corrigida.svg")
    parser.add_argument("--back", type=Path, default=ROOT / "Molambudos_Contracapa_Corrigida.svg")
    parser.add_argument("--title", default="MOLAMBUDOS")
    parser.add_argument("--author", default="MARCELO DIAS DE CARVALHO FILHO")
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--preview-dpi", type=int, default=150)
    args = parser.parse_args()

    try:
        import cairosvg
        from pypdf import PdfReader
        from weasyprint import HTML
    except ImportError as exc:
        print(f"ERRO: dependência ausente: {exc.name}", file=sys.stderr)
        return 2

    front = args.front.expanduser().resolve()
    back = args.back.expanduser().resolve()
    for label, path in (("frente", front), ("contracapa", back)):
        if not path.is_file():
            print(f"ERRO: {label} ausente: {path}", file=sys.stderr)
            return 2
    out = args.outdir.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    spec = kdp_cover_spec(args.trim, args.pages, paper=args.paper, ink=args.ink)

    front_png = out / "front_300dpi.png"
    cairosvg.svg2png(
        url=str(front), write_to=str(front_png),
        output_width=round(spec.trim_width_in * 300),
        output_height=round(spec.trim_height_in * 300),
    )

    clean_pdf = out / f"molambudos_cover_{args.pages}pp.pdf"
    guides_pdf = out / f"molambudos_cover_{args.pages}pp_guides.pdf"
    for target, guides in ((clean_pdf, False), (guides_pdf, True)):
        doc = build_html(spec, front.as_uri(), back.as_uri(), args.title, args.author, guides)
        (out / f"{target.stem}.html").write_text(doc, encoding="utf-8")
        HTML(string=doc, base_url=str(out)).write_pdf(str(target))

    preview = out / f"cover_preview_{args.preview_dpi}dpi"
    subprocess.run(
        ["pdftoppm", "-png", "-r", str(args.preview_dpi), "-singlefile",
         str(clean_pdf), str(preview)],
        check=True, capture_output=True, text=True,
    )
    preview_png = preview.with_suffix(".png")

    reader = PdfReader(str(clean_pdf))
    box = reader.pages[0].mediabox
    page_in = [float(box.width) / 72.0, float(box.height) / 72.0]
    fonts = subprocess.run(["pdffonts", str(clean_pdf)], capture_output=True, text=True)
    not_embedded = [
        line.split()[0] for line in fonts.stdout.splitlines()[2:]
        if line.strip() and len(line.split()) >= 5 and line.split()[-5] != "yes"
    ]

    manifest = {
        "schema_version": 1,
        "status": "generated",
        "spec": spec.to_dict(),
        "front_png": {
            "path": str(front_png), "sha256": sha256(front_png),
            "bytes": front_png.stat().st_size,
        },
        "pdf": {
            "path": str(clean_pdf), "sha256": sha256(clean_pdf),
            "bytes": clean_pdf.stat().st_size, "pages": len(reader.pages),
            "page_in": [round(value, 4) for value in page_in],
            "fonts_not_embedded": not_embedded,
        },
        "guides_pdf": {
            "path": str(guides_pdf), "sha256": sha256(guides_pdf),
            "bytes": guides_pdf.stat().st_size,
        },
        "preview": {
            "path": str(preview_png), "sha256": sha256(preview_png),
            "bytes": preview_png.stat().st_size,
        },
        "warnings": list(spec.warnings) + [
            "A contracapa atual tem proporção 0,553 e usa contain; precisa de re-layout.",
            "O barcode antigo da contracapa continua visível no canto inferior esquerdo.",
            "A frente é esticada de 0,707 para 0,696; revisar antes da arte final.",
        ],
        "limits": [
            "Não é arte final, não é prova física e não é upload KDP.",
            "Não há conversão CMYK/PDF-X nem certificação de preflight.",
            "O PDF sem guias ainda contém a reserva branca do barcode.",
        ],
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checks = [
        f"{sha256(path)}  {path.name}"
        for path in sorted(out.iterdir()) if path.is_file() and path.name != "SHA256SUMS.txt"
    ]
    (out / "SHA256SUMS.txt").write_text("\n".join(checks) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "generated",
        "pdf": manifest["pdf"],
        "guides_pdf": manifest["guides_pdf"],
        "front_png": manifest["front_png"],
        "warnings": manifest["warnings"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
