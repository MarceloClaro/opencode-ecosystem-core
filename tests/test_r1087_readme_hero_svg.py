"""R1087: hero portátil, com semântica, sem números desatualizáveis."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import pytest


SVG = Path(__file__).resolve().parents[1] / "docs/images/readme-hero.svg"
README = SVG.parents[2] / "README.md"
S = "{http://www.w3.org/2000/svg}"


def test_svg_has_accessible_name_description_and_scaling():
    root = ET.parse(SVG).getroot()
    assert root.tag == f"{S}svg"
    assert root.attrib.get("viewBox") == "0 0 1200 420"
    assert root.attrib.get("role") == "img"
    ids = root.attrib.get("aria-labelledby", "").split()
    assert len(ids) == 2
    children = {node.get("id"): node for node in root}
    assert children[ids[0]].tag == f"{S}title"
    assert children[ids[1]].tag == f"{S}desc"
    assert all("".join(children[id_].itertext()).strip() for id_ in ids)


def test_no_stale_statistics_or_unverifiable_promise():
    text = SVG.read_text(encoding="utf-8")
    assert not re.search(r"\b(?:333|27|410)\s+(?:agentes|MCPs|testes)\b", text)
    assert not re.search(r"doctor\s*\d+/\d+", text, re.IGNORECASE)
    assert "sem inventar" not in text.lower()
    assert "revisão humana" in text.lower()
    assert "evidência" in text.lower()


def test_svg_is_self_contained_no_active_content():
    root = ET.parse(SVG).getroot()
    assert not any(node.tag in (f"{S}script", f"{S}image", f"{S}foreignObject", f"{S}animate")
                   for node in root.iter())
    data = SVG.read_text(encoding="utf-8")
    assert not re.search(r"(?:https?://|data:)(?!www\.w3\.org/2000/svg)", data)
    assert "@import" not in data and "<style" not in data


def test_readable_text_sizes_and_no_baked_in_counts():
    root = ET.parse(SVG).getroot()
    nodes = root.findall(f".//{S}text")
    assert len(nodes) >= 5
    assert all(int(node.attrib["font-size"]) >= 16 for node in nodes)


def test_human_gate_fits_inside_visual_panel():
    pillow = pytest.importorskip("PIL.ImageFont")
    try:
        font = pillow.truetype("DejaVuSans-Bold.ttf", 16)
    except OSError:
        pytest.skip("DejaVu Sans não disponível para teste tipográfico")
    root = ET.parse(SVG).getroot()
    gate = next(node for node in root.findall(f".//{S}text")
                if "AUTOMÁTIC" in (node.text or ""))
    assert float(gate.attrib["x"]) + font.getlength(gate.text) <= 1118


def test_embedded_image_alt_matches_visual_message():
    readme = README.read_text(encoding="utf-8")
    image = re.search(r'<img\s+src="docs/images/readme-hero\.svg"\s+alt="([^"]+)"', readme)
    assert image is not None
    alt = image.group(1).lower()
    assert all(term in alt for term in ("evidência antes da narrativa", "agentes", "revisão humana"))
