"""SPEC-935-R874: completude das rotas admin/validação + persistência (SQLite).

Exercita as 11 rotas administrativas que o front (/review, /validacao) chama de
fato, e a persistência (sessões/feedback/imagens) via `RX_ADMIN_DB`. Dados são de
DEMONSTRAÇÃO sintética — este teste NÃO afirma equivalência clínica.
"""

from __future__ import annotations

import importlib
import io
import os
import sys
import zipfile
from importlib import util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

R853 = Path(__file__).resolve().parents[1] / "outputs" / "core-r853-rx"
BACKEND = R853 / "repro" / "backend"

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def _png(w=400, h=240) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (12, 20, 32)).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture(scope="module")
def store(tmp_path_factory):
    db = tmp_path_factory.mktemp("rx-admin") / "admin.db"
    os.environ["RX_ADMIN_DB"] = str(db)
    if str(BACKEND) not in sys.path:
        sys.path.insert(0, str(BACKEND))
    import store as store_mod  # noqa: PLC0415
    importlib.reload(store_mod)
    store_mod.reset()
    return store_mod


@pytest.fixture(scope="module")
def client(store):
    spec = util.spec_from_file_location("rx_app_r874", BACKEND / "app.py")
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    client = TestClient(mod.app)
    login = client.post("/admin/api/login", json={"username": "admin", "password": "senha"})
    assert login.status_code == 200
    return client


# --- autenticação ------------------------------------------------------------

def test_login_session_contract(client):
    session = client.get("/admin/api/session").json()
    assert session["authenticated"] is True
    for field in ("csrf", "role", "is_admin", "username", "user"):
        assert field in session, field


def test_unauth_returns_401():
    spec = util.spec_from_file_location("rx_app_r874_anon", BACKEND / "app.py")
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    anon = TestClient(mod.app)
    for path, method in [
        ("/admin/api/reviews", "get"),
        ("/admin/api/statistics", "get"),
        ("/admin/api/batch", "get"),
        ("/validacao/api/modelos", "get"),
        ("/validacao/api/modelos/teeth", "get"),
        ("/admin/api/export?group=all&task=detect", "get"),
    ]:
        assert getattr(anon, method)(path).status_code == 401, path


# --- estatísticas e revisões -------------------------------------------------

def test_statistics_contract(client):
    stats = client.get("/admin/api/statistics").json()
    for field in ("images", "reviewed_images", "classes_increased",
                  "classes", "average_review_seconds", "measured_reviews"):
        assert field in stats, field
    assert stats["images"] >= 1
    assert stats["classes"], "classes não pode ser vazio"
    row = stats["classes"][0]
    for field in ("group", "label", "images", "annotations", "segmented",
                  "pending_delta", "review_delta"):
        assert field in row, field


def test_reviews_contract_and_pagination(client):
    result = client.get("/admin/api/reviews", params={"page": 1, "status": "all"}).json()
    for field in ("page", "pages", "total", "items", "active_jobs", "edit_locks"):
        assert field in result, field
    assert result["pages"] >= 2, "esperado paginar (>10 imagens de demonstração)"
    assert result["total"] >= 12
    assert len(result["items"]) <= 10
    item = result["items"][0]
    for field in ("image_id", "reviewed", "reviewer", "revision", "created_at",
                  "source_database", "width", "height", "annotation_count",
                  "segmented_count", "complete_groups", "group_counts",
                  "age_classification"):
        assert field in item, field
    assert isinstance(item["complete_groups"], list)
    assert isinstance(item["group_counts"], dict)


def test_reviews_filter_by_status(client):
    reviewed = client.get("/admin/api/reviews", params={"status": "reviewed"}).json()
    pending = client.get("/admin/api/reviews", params={"status": "pending"}).json()
    assert all(row["reviewed"] for row in reviewed["items"])
    assert all(not row["reviewed"] for row in pending["items"])


# --- imagens -----------------------------------------------------------------

def _first_image_id(client) -> str:
    return client.get("/admin/api/reviews", params={"page": 1}).json()["items"][0]["image_id"]


def test_thumbnail_and_image_are_png(client):
    image_id = _first_image_id(client)
    for suffix in ("thumbnail", "image"):
        resp = client.get(f"/admin/api/images/{image_id}/{suffix}")
        assert resp.status_code == 200, suffix
        assert resp.headers["content-type"] == "image/png"
        assert resp.content.startswith(PNG_SIG)


def test_age_update(client):
    image_id = _first_image_id(client)
    resp = client.put(f"/admin/api/images/{image_id}/age", json={"label": "child"})
    assert resp.status_code == 200
    item = client.get("/admin/api/reviews", params={"page": 1}).json()
    row = next(r for r in item["items"] if r["image_id"] == image_id)
    assert row["age_classification"]["label"] == "child"
    assert row["age_classification"]["reviewed"] is True


def test_edit_lock_lifecycle(client):
    image_id = _first_image_id(client)
    assert client.post(f"/admin/api/images/{image_id}/edit-lock").status_code == 200
    result = client.get("/admin/api/reviews", params={"page": 1}).json()
    assert image_id in result["edit_locks"]
    assert client.delete(f"/admin/api/images/{image_id}/edit-lock").status_code == 200
    result = client.get("/admin/api/reviews", params={"page": 1}).json()
    assert image_id not in result["edit_locks"]


# --- jobs / batch ------------------------------------------------------------

def test_segment_job_and_poll(client):
    image_id = _first_image_id(client)
    job = client.post(f"/admin/api/images/{image_id}/segment").json()
    assert "job_id" in job and "status" in job
    polled = client.get(f"/admin/api/jobs/{job['job_id']}").json()
    assert polled["job_id"] == job["job_id"]
    assert polled["status"] in ("queued", "processing", "completed")


def test_unknown_job_404(client):
    assert client.get("/admin/api/jobs/nao-existe").status_code == 404


def test_batch_lifecycle(client):
    idle = client.get("/admin/api/batch").json()
    assert "status" in idle
    started = client.post("/admin/api/batch").json()
    assert "batch_id" in started and "status" in started
    for field in ("current", "total", "succeeded", "skipped", "failed"):
        assert field in started, field
    stopped = client.delete(f"/admin/api/batch/{started['batch_id']}").json()
    assert stopped["status"] in ("cancelled", "cancelling")


def test_export_zip(client):
    resp = client.get("/admin/api/export", params={"group": "all", "task": "detect"})
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        names = zf.namelist()
        assert any(n.endswith(".json") for n in names)


# --- validação ---------------------------------------------------------------

def test_validacao_models_list_contract(client):
    data = client.get("/validacao/api/modelos").json()
    assert data["models"], "models não pode ser vazio"
    assert data["modelos"], "compat: chave 'modelos' preservada (R853)"
    model = data["models"][0]
    for field in ("slug", "name", "description", "eyebrow", "kind", "progress"):
        assert field in model, field
    for field in ("processed", "total", "status"):
        assert field in model["progress"], field


def test_validacao_detail_contract(client):
    model = client.get("/validacao/api/modelos/teeth", params={"page": 1, "page_size": 10}).json()
    for field in ("slug", "name", "eyebrow", "description", "kind", "progress",
                  "summary", "per_class", "plots", "examples", "pagination"):
        assert field in model, field
    assert isinstance(model["per_class"], list)
    assert isinstance(model["plots"], list)
    assert isinstance(model["examples"], list)
    assert "metrics" in model["summary"]
    pag = model["pagination"]
    assert {"page", "pages", "total"} <= set(pag)


def test_validacao_detail_unknown_slug_404(client):
    assert client.get("/validacao/api/modelos/inexistente").status_code == 404


def test_validacao_revisao_post(client):
    resp = client.post("/validacao/api/modelos/teeth/imagens/rx-0001/revisao")
    assert resp.status_code == 200
    assert "review_url" in resp.json()


def test_validacao_slug_serves_html(client):
    resp = client.get("/validacao/teeth")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


# --- persistência ------------------------------------------------------------

def test_feedback_persists_across_reopen(client, store):
    saved = client.post("/feedback", files={"file": ("rx.png", _png(), "image/png")},
                        data={"document": '{"a": 1}', "revision": "0"}).json()
    image_id = saved["image_id"]
    store.reset()  # força reabrir a conexão (mesmo arquivo em disco)
    again = client.get(f"/feedback/{image_id}")
    assert again.status_code == 200
    assert again.json()["image_id"] == image_id


def test_session_persists_across_reopen(client, store):
    store.reset()
    assert client.get("/admin/api/session").json()["authenticated"] is True
