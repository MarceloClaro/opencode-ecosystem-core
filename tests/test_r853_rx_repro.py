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


# --- Opções de motor (1/2/3) -------------------------------------------------

def test_options_page_lists_three_options(client):
    client.post("/opcoes", data={"engine": "stub"})
    html = client.get("/opcoes").text
    for opt in ("Opção 0", "Opção 1", "Opção 2", "Opção 3"):
        assert opt in html
    data = client.get("/opcoes.json").json()
    ids = {e["id"] for e in data["engines"]}
    assert ids == {"stub", "weights", "training", "open_base"}
    assert data["active"] == "stub"


def test_health_reports_engine_block(client):
    client.post("/opcoes", data={"engine": "stub"})
    eng = client.get("/health").json()["engine"]
    assert eng["active"] == "stub"
    assert {e["id"] for e in eng["options"]} == {"stub", "weights", "training", "open_base"}
    assert isinstance(eng["environment"], dict)


def test_stub_engine_is_available_and_works(client):
    # volta ao stub (estado de módulo pode ter sido alterado)
    client.post("/opcoes", data={"engine": "stub"})
    r = client.post("/predict/images", files={"file": ("rx.png", _png(), "image/png")})
    assert r.status_code == 200


def test_unavailable_engine_fails_closed(client):
    """Motor ativo indisponível NÃO finge inferência (SPEC-935-R876).

    Com `weights` selecionado mas indisponível (sem `ultralytics` + `.pt`), a
    detecção é servida pelo melhor motor DISPONÍVEL (stub) — HTTP 200, com o
    cabeçalho `X-Engine` diferente do motor indisponível. O fail-closed (409)
    agora só ocorre quando NENHUM motor disponível cobre a capacidade
    (ver `tests/test_r876_rx_capability.py`).
    """
    import importlib.util as u
    import os
    from pathlib import Path as _P
    has_pt = False
    wdir = os.environ.get("RX_WEIGHTS_DIR", "")
    if wdir and _P(wdir).expanduser().exists():
        has_pt = any(_P(wdir).expanduser().rglob("*.pt"))
    weights_ok = (u.find_spec("ultralytics") is not None) and has_pt
    client.post("/opcoes", data={"engine": "weights"})
    r = client.post("/predict/images", files={"file": ("rx.png", _png(), "image/png")})
    assert r.status_code == 200, r.text
    if weights_ok:
        assert r.headers.get("X-Engine") == "weights"  # Opção 1 realmente armada
    else:
        assert r.headers.get("X-Engine") == "stub"     # fallback honesto
    client.post("/opcoes", data={"engine": "stub"})  # restaura


def test_option1_real_inference_when_available(client):
    """Opção 1 ponta a ponta: com ultralytics + .pt, /predict faz inferência REAL.

    Só roda quando o ambiente tem as duas coisas (ex.: rodar sob .venv com
    RX_WEIGHTS_DIR apontando para um .pt). Caso contrário, é PULADO — nunca
    simulamos inferência real.
    """
    import importlib.util as u
    import os
    from pathlib import Path as _P
    wdir = os.environ.get("RX_WEIGHTS_DIR", "")
    if u.find_spec("ultralytics") is None or not wdir:
        pytest.skip("Opção 1 indisponível: falta ultralytics ou RX_WEIGHTS_DIR")
    pts = sorted(_P(wdir).expanduser().rglob("*.pt")) if _P(wdir).expanduser().exists() else []
    if not pts:
        pytest.skip(f"nenhum .pt em {wdir}")

    client.post("/opcoes", data={"engine": "weights"})
    # imagem com objeto real (COCO) -> deve produzir detecções
    sample = R853 / "op1-verificacao" / "sample-bus.jpg"
    if not sample.exists():
        r = client.post("/predict/images", files={"file": ("rx.png", _png(), "image/png")})
        assert r.status_code == 200
    else:
        r = client.post("/predict", files={"file": ("bus.jpg", sample.read_bytes(), "image/jpeg")})
        assert r.status_code == 200
        data = r.json()
        assert data["engine"] == "weights"
        assert len(data["additional"]) >= 1, "inferência real deveria detectar ≥1 objeto"
    client.post("/opcoes", data={"engine": "stub"})  # restaura



def test_unknown_engine_rejected(client):
    assert client.post("/opcoes", data={"engine": "nao_existe"}).status_code == 422


def test_option3_real_sam_when_available(client):
    """Opção 3 ponta a ponta: com segment_anything + checkpoint, /segment/sam é REAL.

    Só roda quando o ambiente tem as duas coisas (rodar sob .venv com RX_MEDSAM_CKPT
    válido). Caso contrário, PULA — nunca simulamos segmentação real.
    """
    import importlib.util as u
    import os
    from pathlib import Path as _P
    ckpt = os.environ.get("RX_MEDSAM_CKPT", "")
    if u.find_spec("segment_anything") is None or not ckpt or not _P(ckpt).expanduser().exists():
        pytest.skip("Opção 3 indisponível: falta segment_anything ou RX_MEDSAM_CKPT")

    client.post("/opcoes", data={"engine": "open_base"})
    r = client.post("/segment/sam", data={"box": "[10,10,100,100]", "target": "generic"},
                    files={"file": ("rx.png", _png(160, 160), "image/png")})
    assert r.status_code == 200
    data = r.json()
    assert data["engine"] == "open_base"
    assert len(data["contour"]) >= 3  # contorno real fechado
    client.post("/opcoes", data={"engine": "stub"})  # restaura



def test_training_scaffold_files_exist():
    tr = R853 / "repro" / "training"
    for name in ("README.md", "datasets.md", "download_datasets.sh",
                 "requirements-train.txt", "train_teeth.sh", "train_teeth_mmdet.py",
                 "configs/teeth-yolo.yaml"):
        assert (tr / name).exists(), name


def test_engines_registry_contract():
    """O registro de motores declara capabilities e availability honestas."""
    import importlib.util as u
    import sys
    spec = util.spec_from_file_location("rx_engines", R853 / "repro" / "backend" / "engines.py")
    mod = util.module_from_spec(spec)
    sys.modules["rx_engines"] = mod  # necessário p/ resolução de dataclass (Py3.14)
    spec.loader.exec_module(mod)
    statuses = {e.id: e for e in mod.engine_statuses()}
    assert statuses["stub"].available is True
    assert statuses["stub"].capabilities and "detection" in statuses["stub"].capabilities
    # weights só fica disponível com ultralytics + .pt; aqui não há
    if u.find_spec("ultralytics") is None:
        assert statuses["weights"].available is False
    assert statuses["training"].kind == "training"
    # require_available é fail-closed
    import pytest as _pytest
    with _pytest.raises(ValueError):
        mod.require_available("stub", "train")      # stub não treina
    with _pytest.raises(ValueError):
        mod.require_available("open_base", "detection")  # open_base só faz sam

