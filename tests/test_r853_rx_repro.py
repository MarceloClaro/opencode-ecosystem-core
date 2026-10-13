"""SPEC-935-R853: reprodução do contrato do site Panoramica AI.

Verifica que o backend reproduzido (outputs/core-r853-rx/repro/backend/app.py)
cumpre o contrato observado em /openapi.json e as invariantes que o front-end
real exige: ZIP_STORED com 4 entradas, layout com cards válidos, PNG da prancha
com dimensões iguais ao layout, e cabeçalhos X-*.

Nada aqui afirma equivalência clínica ao alvo: os modelos de IA não existem na
reprodução, apenas o contrato e o fluxo de I/O.
"""

from __future__ import annotations

import io
import json
import struct
import zipfile
from importlib import util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

R853 = Path(__file__).resolve().parents[1] / "outputs" / "core-r853-rx"

REFACT = {
    "index.html": "9638d56ae8aa3ef620abe98e755c316b1f121cccf7acedf2d197b6cd041a61f8",
    "editor.js": "6c8cce034d66fdaccc5e98b66628272f515a1c82183d95e84e753bda7df331ea",
    "review.html": "00e6f639ba44e52dacc22d262e9eb5aaa382b72be206b24e496cfc25c5887ece",
    "validacao.html": "8e0c89949140aa624404c1af0f939fb3df75910493a7b9c0b3cb3d40c2d664a7",
    "docs.html": "ed858cea6baef521fa5e62522a00dc000f54b9a1b9fd0f6bf4db8f68672cdb70",
}


@pytest.fixture(scope="module")
def client():
    spec = util.spec_from_file_location("rx_app", R853 / "repro" / "backend" / "app.py")
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return TestClient(mod.app)


def _png(w=800, h=500) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (12, 20, 32)).save(buf, format="PNG")
    return buf.getvalue()


# --- documentação/artefatos -------------------------------------------------

def test_artifacts_preserved_with_expected_hashes():
    import hashlib
    pages = R853 / "api" / "pages"
    for name, digest in REFACT.items():
        data = (pages / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == digest, name


def test_rea_evidence_records_two_analysis_passes():
    ev = json.loads((R853 / "rea-evidence.json").read_text())
    passes = ev["rea"]["passes"]
    assert len(passes) == 2
    assert all(p["evidence_id"].startswith("ev_") for p in passes)
    assert ev["flags"] == {"externally_validated": False, "confidence_promoted": False}


def test_openapi_contract_covers_reproduced_routes(client):
    paths = client.get("/openapi.json").json()["paths"]
    for p in ["/health", "/predict", "/predict/image", "/predict/images",
              "/segment/sam", "/feedback", "/admin/api/login", "/validacao/api/modelos"]:
        assert p in paths, p


# --- I/O do visualizador -----------------------------------------------------

def test_health_shape(client):
    h = client.get("/health").json()
    assert h["status"] == "ready"
    assert len(h["additional_model"]["classes"]) == 31
    assert "maxillary_sinus" in h["additional_model"]["classes"]


def test_predict_images_returns_frontend_compatible_bundle(client):
    r = client.post("/predict/images", files={"file": ("rx.png", _png(), "image/png")},
                    params={"include_additional": "true"})
    assert r.status_code == 200
    assert r.headers["X-Model-Scope"] == "combined"
    assert r.headers["X-Additional-Status"] == "completed"

    # Replica readImageBundle: ZIP_STORED, entradas exatas.
    data = r.content
    assert struct.unpack_from("<I", data, 0)[0] == 0x04034B50  # local file header
    zf = zipfile.ZipFile(io.BytesIO(data))
    names = set(zf.namelist())
    assert {"panoramica-anotada.png", "panoramica-anatomia.png",
            "panoramica-dentes.png", "panoramica-impressao.json"} <= names
    for info in zf.infolist():
        assert info.compress_type == zipfile.ZIP_STORED

    layout = json.loads(zf.read("panoramica-impressao.json"))
    assert isinstance(layout["cards"], list) and layout["cards"]
    for card in layout["cards"]:
        assert {"title", "x", "y", "width", "height"} <= set(card)
        assert card["x"] + card["width"] <= layout["width"]
        assert card["y"] + card["height"] <= layout["height"]

    # Dimensões da prancha == layout (invariante do front-end).
    plate = Image.open(io.BytesIO(zf.read("panoramica-dentes.png")))
    assert plate.size == (layout["width"], layout["height"])


def test_dental31_scope_marks_scope_and_skips_teeth(client):
    r = client.post("/predict/images", files={"file": ("rx.png", _png(), "image/png")},
                    params={"model_scope": "dental31"})
    assert r.headers["X-Model-Scope"] == "dental31"
    layout = json.loads(zipfile.ZipFile(io.BytesIO(r.content)).read("panoramica-impressao.json"))
    assert layout["cards"] == []


# --- SAM, feedback e admin ---------------------------------------------------

def test_sam_returns_contour(client):
    r = client.post("/segment/sam", files={"file": ("rx.png", _png(), "image/png")},
                    data={"box": "[10, 20, 110, 120]"})
    assert r.status_code == 200
    assert len(r.json()["contour"]) == 4


def test_feedback_roundtrip(client):
    doc = json.dumps({"groups": {"teeth": []}})
    saved = client.post("/feedback", files={"file": ("rx.png", _png(), "image/png")},
                        data={"document": doc, "revision": "0"}).json()
    img_id = saved["image_id"]
    assert client.get(f"/feedback/{img_id}").json()["revision"] == 0
    export = client.get("/feedback/export", params={"group": "teeth", "task": "segment"})
    assert export.status_code == 200


def test_admin_endpoints_require_session(client):
    assert client.get("/admin/api/reviews").status_code == 401
    assert client.get("/validacao/api/modelos").status_code == 401
    assert client.post("/admin/api/login", json={"user": "admin"}).status_code == 200
    assert client.get("/admin/api/session").json()["authenticated"] is True
    assert client.get("/validacao/api/modelos").json()["modelos"]
