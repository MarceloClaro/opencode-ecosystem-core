"""R1081: gate do pacote visual Piranesi/Pencz e das provas determinísticas."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "reports/r1081/illustration_style"
PACK = STYLE / "style_pack.json"
MANIFEST = STYLE / "samples_manifest.json"
SOURCE = ROOT / "literatura/molambudos/Molambudos_Revisada_R1075/figures/immersao"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_style_pack_schema_and_plate_types():
    data = json.loads(PACK.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert "Piranesi" in data["name"]
    assert "Pencz" in data["name"]
    assert len(data["plate_types"]) == 6
    ids = [plate["id"] for plate in data["plate_types"]]
    assert len(ids) == len(set(ids))
    for plate in data["plate_types"]:
        for key in ("id", "name", "use_when", "piranesi", "pencz",
                    "composition", "prompt", "negative", "caption"):
            assert plate[key].strip(), (plate["id"], key)


def test_style_pack_prompts_and_technical_specs():
    data = json.loads(PACK.read_text(encoding="utf-8"))
    prompts = data["prompts"]
    assert "Piranesi" in prompts["base_en"]
    assert "Pencz" in prompts["base_en"]
    assert "photorealistic" in prompts["negative_en"]
    assert "texto" in prompts["negative_pt"]
    technical = data["technical"]
    assert technical["min_dpi"] == 300
    assert technical["tac_limit"] <= 210
    assert "TIFF 16-bit" in technical["formats"]
    assert "domínio público" in data["ethics"]["public_domain"].lower()
    assert "não é prova histórica" in data["ethics"]["fiction"].lower()
    assert "IA" in data["ethics"]["ai_disclosure"]


def test_samples_manifest_and_hashes():
    if not SOURCE.is_dir():
        pytest.skip("pranchas de origem ausentes")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["status"] == "visual_reference_only"
    assert len(data["items"]) == 3
    for item in data["items"]:
        output = STYLE / "samples" / item["output"]
        assert output.is_file(), item["output"]
        assert sha256(output) == item["output_sha256"], item["output"]
        assert item["pixels"] == [
            ImageSize(SOURCE / item["source"])[0] + 52,
            ImageSize(SOURCE / item["source"])[1] + 52,
        ], item["output"]
    sheet = STYLE / "samples" / data["contact_sheet"]["path"]
    assert sheet.is_file()
    assert sha256(sheet) == data["contact_sheet"]["sha256"]


def ImageSize(path: Path) -> tuple[int, int]:
    from PIL import Image
    with Image.open(path) as image:
        return image.size


def test_readme_documents_limits_and_ethics():
    text = (STYLE / "README.md").read_text(encoding="utf-8").lower()
    for term in ("piranesi", "pencz", "300", "domínio público",
                 "não é arte final", "não é prova histórica", "aviso de conteúdo"):
        assert term in text, term


def test_demo_plate_contract():
    text = (STYLE / "demo_plate.md").read_text(encoding="utf-8")
    lower = text.lower()
    for section in ("## status", "## findings", "## evidence", "## limitations"):
        assert section in lower, section
    assert "Piranesi" in text and "Pencz" in text
    assert "não é prova histórica" in lower
    assert "prévia" in lower
