#!/usr/bin/env python3
"""reembed_figure.py — substitui um desenho do DOCX e preserva a proporção.

Por que existe: o DOCX guarda cada figura duas vezes — o PNG em
`word/media/` e a caixa de exibição em `wp:extent`/`a:ext`. Trocar só os bytes
do PNG deixa a caixa com a proporção antiga e o Word distorce a imagem. E
trocar a caixa sem os bytes não troca a figura. As duas coisas andam juntas.

O redimensionamento é sempre proporcional a partir da largura já presente no
documento (não de um valor fixo em polegadas), para não deslocar a figura na
coluna do manuscrito. Rejeita upscale: ampliar um PNG pequeno para "atingir"
600 dpi só produz uma imagem grande e borrada, e a falha reaparece no pre-check
do periódico. Uma figura que já entrava abaixo de 600 dpi tem de ser
re-renderizada na fonte, não extrapolada aqui.

Uso:
    python3 manuscript_assets/reembed_figure.py DOCX FIGURA_PNG NUMERO [--apply]
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path

from PIL import Image

EMU_PER_INCH = 914400


def drawings(doc_xml: str, rels_xml: str) -> list[tuple[str, str]]:
    """Desenhos na ordem do documento: [(media_path, r:embed_id), ...]."""
    rels = dict(re.findall(r'Id="([^"]+)"[^>]*Target="(media/[^"]+)"',
                           rels_xml))
    return [(rels[rid], rid)
            for rid in re.findall(r'r:embed="([^"]+)"', doc_xml)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("png")
    ap.add_argument("number", type=int, help="1-based drawing position")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    docx, png = Path(a.docx), Path(a.png)
    if not docx.exists() or not png.exists():
        print("input ausente", file=sys.stderr)
        return 2

    new = Image.open(png)
    nw, nh = new.size

    with zipfile.ZipFile(docx) as z:
        names = z.namelist()
        doc = z.read("word/document.xml").decode("utf-8", "ignore")
        rels_xml = z.read("word/_rels/document.xml.rels").decode("utf-8", "ignore")
        payload = {n: z.read(n) for n in names}

    order = drawings(doc, rels_xml)
    if not 1 <= a.number <= len(order):
        print(f"ERRO: o documento tem {len(order)} desenhos", file=sys.stderr)
        return 2
    media_rel, rid = order[a.number - 1]
    media_part = "word/" + media_rel
    old_bytes = payload.get(media_part, b"")
    old = Image.open(__import__("io").BytesIO(old_bytes)) if old_bytes else None

    # Aparições do extent/a:ext por desenho, na ordem em que r:embed aparece.
    ext_cx = re.findall(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', doc)
    aext = re.findall(r'<a:ext cx="(\d+)" cy="(\d+)"/>', doc)
    if len(ext_cx) < a.number:
        print("ERRO: wp:extent ausente", file=sys.stderr)
        return 2
    cx, _ = ext_cx[a.number - 1]
    cy_new = round(int(cx) * nh / nw)

    print(f"desenho {a.number}: {media_rel}")
    if old is not None:
        print(f"  antes: {old.size[0]}x{old.size[1]} px  "
              f"cx={cx} cy={ext_cx[a.number-1][1]}")
    print(f"  depois:{nw}x{nh} px  cx={cx} cy={cy_new}  "
          f"({int(cx)/EMU_PER_INCH:.2f} in, {nw/(int(cx)/EMU_PER_INCH):.0f} dpi)")

    if not a.apply:
        print("dry-run; use --apply")
        return 0

    payload[media_part] = png.read_bytes()
    doc_new = doc
    # substitui apenas a N-ª ocorrência, preservando as demais
    idx = [m.start() for m in re.finditer(r'<wp:extent cx="\d+" cy="\d+"/>', doc_new)]
    m_span = re.match(r'<wp:extent cx="(\d+)" cy="(\d+)"/>',
                      doc_new[idx[a.number - 1]:])
    doc_new = (doc_new[:idx[a.number - 1]]
               + f'<wp:extent cx="{m_span.group(1)}" cy="{cy_new}"/>'
               + doc_new[idx[a.number - 1] + m_span.end():])
    if len(aext) >= a.number:
        aidx = [m.start() for m in re.finditer(r'<a:ext cx="\d+" cy="\d+"/>', doc_new)]
        am = re.match(r'<a:ext cx="(\d+)" cy="(\d+)"/>', doc_new[aidx[a.number - 1]:])
        doc_new = (doc_new[:aidx[a.number - 1]]
                   + f'<a:ext cx="{am.group(1)}" cy="{cy_new}"/>'
                   + doc_new[aidx[a.number - 1] + am.end():])
    payload["word/document.xml"] = doc_new.encode("utf-8")

    bak = docx.with_suffix(".prereembed.docx")
    if not bak.exists():
        shutil.copy2(docx, bak)
    tmp = docx.with_suffix(".tmp.docx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for n in names:
            out.writestr(n, payload[n])
    tmp.replace(docx)
    print(f"  gravado; backup em {bak.name}")
    print(f"  sha256 media: {hashlib.sha256(payload[media_part]).hexdigest()[:32]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())