#!/usr/bin/env python3
"""Monta o caderno de provas das 6 pranchas e roda o preflight local."""
from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[2]
PROOF = Path(__file__).resolve().parent / "plate_proof"
PLATES = PROOF / "plates"
MANIFEST = PROOF / "plates_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_html(items: list[dict]) -> str:
    plates_html = []
    for index, item in enumerate(items, 1):
        image_rel = f"plates/{item['output']}"
        plates_html.append(f"""
<section class="plate">
  <p class="kicker">PRANCHA {index:02d} · {html.escape(item['title']).upper()}</p>
  <img src="{image_rel}" alt="{html.escape(item['title'])} — {html.escape(item['description'])}">
  <p class="caption">{html.escape(item['description'])}. Reconstituição ficcional.</p>
  <p class="meta">Fonte: {html.escape(item['source'])} · {item['effective_dpi']:.1f} DPI a {item['final_width_mm']:.0f} mm · {item['two_x_effective_dpi']:.1f} DPI a 2× · prova</p>
</section>""")
    rows = "".join(
        f"<tr><td>{html.escape(i['title'])}</td><td><code>{i['output_sha256'][:16]}…</code></td>"
        f"<td>{i['effective_dpi']:.1f}</td><td>{i['two_x_effective_dpi']:.1f}</td></tr>"
        for i in items
    )
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Molambudos — Caderno de Provas Piranesi/Pencz</title>
<style>
@page {{ size: 160mm 230mm; margin: 18mm 18mm 20mm 18mm;
        @bottom-center {{ content: counter(page); font-size: 8pt; color: #6E4E10; }} }}
body {{ font-family: "EB Garamond", "Liberation Serif", serif; color: #2B2117;
        font-size: 11pt; line-height: 1.45; }}
.cover {{ page-break-after: always; padding-top: 28mm; }}
.kicker {{ font-family: "DejaVu Sans", sans-serif; font-size: 8pt; letter-spacing: 1.6pt;
          text-transform: uppercase; color: #6E4E10; }}
h1 {{ font-size: 30pt; line-height: 1.05; margin: 0.25em 0 0.1em; font-weight: normal; }}
.sub {{ font-size: 15pt; font-style: italic; color: #552A7A; }}
.rule {{ width: 28mm; height: 1.2pt; background: #9B1B1B; margin: 8mm 0; }}
.warning {{ font-family: "DejaVu Sans", sans-serif; font-size: 9pt; color: #9B1B1B;
            border: 0.8pt solid #9B1B1B; padding: 5mm; margin-top: 10mm; }}
.small {{ font-size: 9pt; color: #6E4E10; margin-top: 8mm; }}
.plate {{ page-break-before: always; }}
.plate img {{ display: block; width: 86mm; height: auto; margin: 4mm auto 2mm; }}
.caption {{ text-align: center; font-style: italic; font-size: 10pt; }}
.meta {{ text-align: center; font-family: "DejaVu Sans", sans-serif; font-size: 7.2pt;
         color: #6E4E10; }}
.prov {{ page-break-before: always; }}
.prov h2 {{ font-size: 18pt; font-weight: normal; }}
table {{ width: 100%; border-collapse: collapse; font-family: "DejaVu Sans", sans-serif;
         font-size: 7.5pt; margin: 4mm 0; }}
th, td {{ border-bottom: 0.4pt solid #6E4E10; padding: 1.4mm 1mm; text-align: left; }}
code {{ font-size: 6.8pt; }}
</style></head><body>
<div class="cover">
  <p class="kicker">Molambudos · Caderno de Provas</p>
  <h1>Direção de Arte<br>Piranesi / Pencz</h1>
  <p class="sub">Seis pranchas de prova · 160 × 230 mm</p>
  <div class="rule"></div>
  <p class="warning">PROVA — NÃO É ARTE FINAL<br>
  Não é prova histórica, não é publicação e não é validação externa.<br>
  As imagens são ficcionais. A arte final exige re-layout, revisão humana e prova de impressão.</p>
  <p class="small">316–345 DPI no tamanho final de 86 mm. A 2× (172 mm), as fontes atuais caem
  para 158–173 DPI; não houve upscale. O caderno canônico do livro não foi alterado.</p>
</div>
{''.join(plates_html)}
<div class="prov">
  <h2>Proveniência e limites</h2>
  <p>As artes de <em>arte_confinamento</em>, <em>arte_sertao</em>, <em>arte_arquivo</em> e
  <em>arte_frontal_original</em> foram geradas/editadas por IA no pacote R1082 e são
  reconstituições ficcionais. <em>placa_00</em> é uma prancha existente do projeto.
  Nenhuma retrata vítima real identificável.</p>
  <table>
    <tr><th>Prancha</th><th>SHA-256</th><th>DPI 86 mm</th><th>DPI 2×</th></tr>
    {rows}
  </table>
  <p><strong>Lacuna 2×:</strong> seriam necessários 2032 px de largura para 172 mm a 300 DPI;
  as fontes têm 1024–1122 px. Não houve upscale artificial.</p>
  <p><strong>Limites:</strong> RGB, sem CMYK perfilado, sem PDF/X, sem prova física e sem
  aprovação da gráfica/KDP. Três artes têm arquitetura europeia; a adaptação brasileira
  está pendente. O perfil literário foi configurado para modelo local, mas a inferência
  local não foi comprovada nesta sessão.</p>
  <p><strong>Direção:</strong> Piranesi para arquitetura, escala e chiaroscuro; Pencz para
  figura, gesto e emblema; um acento carmim por prancha.</p>
</div>
</body></html>"""


def ink_coverage(pdf: Path) -> dict:
    output = subprocess.run(
        ["gs", "-q", "-o", "-", "-sDEVICE=inkcov", str(pdf)],
        capture_output=True, text=True, timeout=180,
    ).stdout
    values = []
    for line in output.splitlines():
        match = re.search(r"([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+CMYK OK", line)
        if match:
            channels = [float(value) for value in match.groups()]
            values.append(channels + [sum(channels)])
    if not values:
        return {"pages": 0, "avg_tac": None, "max_tac": None}
    array = np.array(values)
    return {
        "pages": len(values),
        "avg_cmyk": [round(float(value), 4) for value in array[:, :4].mean(axis=0)],
        "avg_tac": round(float(array[:, 4].mean()), 4),
        "max_tac": round(float(array[:, 4].max()), 4),
    }


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = manifest["items"]
    document = build_html(items)
    html_path = PROOF / "caderno_provas.html"
    html_path.write_text(document, encoding="utf-8")
    pdf_path = PROOF / "caderno_provas.pdf"
    HTML(string=document, base_url=str(PROOF)).write_pdf(str(pdf_path))

    info = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True).stdout
    fields = {}
    for line in info.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    fonts = subprocess.run(["pdffonts", str(pdf_path)], capture_output=True, text=True).stdout
    font_rows = [row for row in fonts.splitlines()[2:] if row.strip()]
    not_embedded = [row for row in font_rows if len(row.split()) >= 5 and row.split()[-5] != "yes"]
    images = subprocess.run(["pdfimages", "-list", str(pdf_path)], capture_output=True, text=True).stdout
    ppi = []
    for line in images.splitlines()[2:]:
        parts = line.split()
        if len(parts) >= 14 and parts[2] == "image":
            ppi.append(int(parts[-4]))
    page_size = fields.get("Page size", "")
    page_match = re.search(r"([0-9.]+) x ([0-9.]+) pts", page_size)
    page_ok = bool(page_match) and abs(float(page_match.group(1)) - 453.543) <= 0.05 and abs(float(page_match.group(2)) - 651.968) <= 0.05
    ink = ink_coverage(pdf_path)
    checks = {
        "page_size_160x230": {"status": "pass" if page_ok else "fail", "value": page_size},
        "pages": {"status": "pass" if fields.get("Pages") == "8" else "fail",
                  "value": fields.get("Pages")},
        "fonts_embedded": {"status": "pass" if not not_embedded else "fail",
                           "value": f"{len(font_rows)} fontes; {len(not_embedded)} não embutidas"},
        "images_min_300dpi": {"status": "pass" if ppi and min(ppi) >= 300 else "fail",
                              "value": f"{len(ppi)} imagens; mínimo {min(ppi) if ppi else 0} DPI"},
        "two_x_300dpi": {"status": "fail", "value": "fontes 1024–1122 px; 2× exige 2032 px"},
        "ink_coverage": {"status": "info", "value": ink},
    }
    preflight = {
        "schema_version": 1,
        "status": "proof_only",
        "pdf": {"path": str(pdf_path), "bytes": pdf_path.stat().st_size,
                "sha256": sha256(pdf_path)},
        "checks": checks,
        "limits": [
            "Prova de caderno; não é o caderno canônico do livro.",
            "RGB; sem CMYK perfilado, PDF/X ou prova física.",
            "2× a 300 DPI não é possível com as fontes atuais; não houve upscale.",
            "Três artes têm arquitetura europeia; adaptação brasileira pendente.",
            "Nenhuma publicação, KDP ou validação externa.",
        ],
    }
    (PROOF / "preflight.json").write_text(
        json.dumps(preflight, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for page in (1, 2):
        subprocess.run(
            ["pdftoppm", "-png", "-r", "100", "-f", str(page), "-l", str(page),
             "-singlefile", str(pdf_path), str(PROOF / f"preview_p{page}")],
            check=True, capture_output=True, text=True,
        )
    print(json.dumps(preflight, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
