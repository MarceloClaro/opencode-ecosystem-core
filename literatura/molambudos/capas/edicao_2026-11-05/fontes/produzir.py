"""Produção e preflight local das capas; não altera os miolos ou as artes originais."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import fitz
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
MM = 72 / 25.4
BLEED = 3.175
VARIANTS = {"422p_print": 422, "436p_canonica": 436}


def create(variant, pages):
    spine = pages * 0.002347 * 25.4
    width, height = 326.35 + spine, 236.35
    (HERE / "variante.tex").write_text(
        f"\\def\\Pages{{{pages}}}\n\\def\\Spine{{{spine:.8f}}}\n"
        f"\\def\\CoverWidth{{{width:.8f}}}\n", encoding="utf-8"
    )
    # PGF remember-picture resolve a âncora absoluta na segunda passagem.
    for _ in range(2):
        proc = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "layout.tex"],
            cwd=HERE, capture_output=True, text=True
        )
        if proc.returncode:
            raise RuntimeError(proc.stdout[-5000:])
    (HERE / f"compilacao_{variant}.log").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    if proc.returncode:
        raise RuntimeError(proc.stdout[-5000:])
    assert "Overfull" not in proc.stdout, proc.stdout
    raw = fitz.open(HERE / "layout.pdf")
    assert len(raw) == 1
    page = raw[0]
    page.set_trimbox(fitz.Rect(BLEED*MM, BLEED*MM, (width-BLEED)*MM, (height-BLEED)*MM))
    page.set_bleedbox(page.mediabox)
    final = OUT / f"molambudos_capa_completa_{variant}_300dpi.pdf"
    raw.save(final, garbage=4, deflate=True)
    raw.close()
    doc = fitz.open(final)
    page = doc[0]
    assert abs(page.rect.width / MM - width) < .02
    assert abs(page.rect.height / MM - height) < .02
    text = page.get_text()
    for expected in ["MOLAMBUDOS", "O Diário do Paciente 1.260", "Marcelo Dias de Carvalho Filho", "Marcelo Claro", "Joaquim Antônio Correia", "Lúcia Mendes"]:
        assert expected in text, expected
    assert "978-65-01-23456-7" not in text
    assert "ISBN" not in text
    assert not doc.is_encrypted
    raster = []
    for entry in page.get_image_info(xrefs=True):
        bbox = fitz.Rect(entry["bbox"])
        dpi = [entry["width"] / bbox.width * 72, entry["height"] / bbox.height * 72]
        assert min(dpi) >= 300, dpi
        raster.append({"pixels": [entry["width"], entry["height"]], "effective_dpi": dpi})
    assert len(raster) == 2
    fonts = page.get_fonts(full=True)
    assert len(fonts) >= 3
    for font in fonts:
        assert len(doc.extract_font(font[0])[3]) > 0, font
    assert not page.get_drawings() or all(d["rect"].is_valid for d in page.get_drawings())
    pngdir = OUT / variant
    pngdir.mkdir(exist_ok=True)
    # Cada painel tem página própria antes da rasterização: dimensões físicas sem arredondar a origem do recorte.
    fx = BLEED + 160 + spine
    panels = {
        "capa_frontal_160x230mm": (fx, BLEED, 160, 230),
        "contracapa_160x230mm": (BLEED, BLEED, 160, 230),
        "lombada": (BLEED + 160, BLEED, spine, 230),
        "capa_aberta_com_sangria": (0, 0, width, height),
    }
    outputs = []
    for name, (x,y,w,h) in panels.items():
        panel = fitz.open()
        pp = panel.new_page(width=w*MM, height=h*MM)
        pp.show_pdf_page(pp.rect, doc, 0, clip=fitz.Rect(x*MM,y*MM,(x+w)*MM,(y+h)*MM))
        pix = pp.get_pixmap(dpi=300, alpha=False)
        pix.set_dpi(300, 300)
        target = pngdir / (name + "_300dpi.png")
        pix.save(target)
        im = Image.open(target)
        assert abs(im.info["dpi"][0] - 300) < .1
        outputs.append({"file": str(target.relative_to(OUT)), "pixels": list(im.size), "size_mm": [w,h]})
        panel.close()
    # Prévia leve, sempre sem guias de impressão.
    preview = page.get_pixmap(dpi=110, alpha=False)
    preview.save(OUT / f"previa_{variant}.png")
    doc.close()
    return {"variant": variant, "pages_for_spine": pages, "paper": "premium color / white", "spine_mm": spine,
            "cover_size_mm": [width,height], "trim_mm": [160,230], "bleed_mm": BLEED,
            "barcode_mm": [50.8,30.48], "barcode_clearance_mm": 6.35,
            "artwork": raster, "fonts_embedded": True, "text_checks": "pass",
            "pdf": final.name, "outputs": outputs, "status": "PASS_LOCAL", "external_approval": False}


if __name__ == "__main__":
    records = [create(name,pages) for name,pages in VARIANTS.items()]
    (OUT / "preflight_local.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(records, ensure_ascii=False, indent=2))
