"""Aceitação física dos artefatos, independente da implementação do gerador."""
from pathlib import Path
import hashlib
import json

import pytest

fitz = pytest.importorskip("fitz")
Image = pytest.importorskip("PIL.Image")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "literatura/molambudos/capas/piranesi_pencz_2026-11-05"
SELECTED = ROOT / "literatura/molambudos/capas/molambudos_final"
MM = 72 / 25.4

if not OUT.is_dir() or not SELECTED.is_dir():
    pytest.skip("artefatos literários gitignored ausentes", allow_module_level=True)


@pytest.mark.parametrize("name,pages", [("422p_print",422),("436p_canonica",436)])
def test_pdf_physical_and_typographic_contract(name, pages):
    path = OUT / f"molambudos_capa_completa_{name}_300dpi.pdf"
    assert path.is_file(), "Capa PDF ainda não produzida"
    doc = fitz.open(path)
    assert len(doc) == 1 and not doc.is_encrypted
    p = doc[0]
    width = 326.35 + pages * .002347 * 25.4
    assert abs(p.rect.width / MM - width) < .02
    assert abs(p.rect.height / MM - 236.35) < .02
    assert abs(p.trimbox.x0 / MM - 3.175) < .02
    assert abs(p.trimbox.y0 / MM - 3.175) < .02
    assert p.bleedbox == p.mediabox
    text = p.get_text()
    for phrase in ["MOLAMBUDOS", "O Diário do Paciente 1.260", "Marcelo Dias de Carvalho Filho", "Marcelo Claro", "RECONSTITUIÇÕES FICCIONAIS"]:
        assert phrase in text
    assert "978-65-01-23456-7" not in text
    assert "ISBN" not in text
    images = p.get_image_info()
    assert len(images) == 4
    for im in images:
        box = fitz.Rect(im["bbox"])
        assert min(im["width"] / box.width * 72, im["height"] / box.height * 72) >= 600
    for font in p.get_fonts(full=True):
        assert doc.extract_font(font[0])[3], "Fonte não embutida"
    barcode = fitz.Rect(106.025*MM,196.345*MM,156.825*MM,226.825*MM)
    for block in p.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                assert span["size"] >= 6.99
                assert not fitz.Rect(span["bbox"]).intersects(barcode), "Texto na reserva de barras"


@pytest.mark.parametrize("name", ["422p_print","436p_canonica"])
def test_png_print_dimensions_and_master(name):
    for panel in ["capa_frontal_160x230mm","contracapa_160x230mm"]:
        im = Image.open(OUT/name/(panel+"_300dpi.png"))
        assert im.size == (1890,2717)
        assert abs(im.info["dpi"][0] - 300) < .1
        master = Image.open(OUT/name/(panel+"_600dpi.png"))
        assert master.size == (3780,5434)
        assert abs(master.info["dpi"][0] - 600) < .1


def test_provenance_and_preserved_reference_proofs():
    manifest = json.loads((OUT/"manifesto.json").read_text())
    assert manifest["ai_generated_artwork"] is True
    assert manifest["external_print_approval"] is False
    assert len(manifest["new_artworks"]) == 3
    for item in manifest["files"]:
        p = OUT/item["path"]
        assert p.is_file()
        assert hashlib.sha256(p.read_bytes()).hexdigest() == item["sha256"]
    old = json.loads((OUT/"provas_deterministicas/manifesto_original.json").read_text())
    for item in old["items"]:
        p = OUT/"provas_deterministicas"/item["output"]
        assert hashlib.sha256(p.read_bytes()).hexdigest() == item["output_sha256"]


@pytest.mark.parametrize("name,pages", [("422p_print",422),("436p_canonica",436)])
def test_author_selected_dark_cover(name,pages):
    selected = ROOT / "literatura/molambudos/capas/molambudos_final"
    doc = fitz.open(selected/f"molambudos_capa_completa_{name}_300dpi.pdf")
    assert len(doc) == 1 and not doc.is_encrypted
    p = doc[0]
    assert abs(p.rect.width/MM - (326.35+pages*.002347*25.4)) < .02
    assert abs(p.rect.height/MM - 236.35) < .02
    assert p.bleedbox == p.mediabox
    assert "Marcelo Dias de Carvalho Filho" in p.get_text()
    assert "Marcelo Claro" in p.get_text()
    assert "ISBN" not in p.get_text()
    assert len(p.get_image_info()) == 2
    for im in p.get_image_info():
        b = fitz.Rect(im["bbox"])
        assert min(im["width"]/b.width*72, im["height"]/b.height*72) >= 300
    for font in p.get_fonts(full=True):
        assert doc.extract_font(font[0])[3]
    for panel in ["capa_frontal_160x230mm", "contracapa_160x230mm"]:
        im = Image.open(selected/name/(panel+"_300dpi.png"))
        assert im.size == (1890,2717)
        assert abs(im.info["dpi"][0] - 300) < .1
