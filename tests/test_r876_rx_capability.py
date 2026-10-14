"""SPEC-935-R876: composição por capacidade (motor por rota) na reprodução RX.

Cobre a correção do 409 indevido: com o motor `open_base` (Opção 3, só `sam`)
ativo, `/predict` (capability `detection`) NÃO deve falhar se outro motor
disponível cobre `detection`; e `/segment/sam` continua servido pelo MedSAM.

Fail-closed é preservado: só há 409 quando NENHUM motor disponível cobre a
capacidade. Nada aqui afirma equivalência clínica ao alvo.
"""

from __future__ import annotations

import importlib.util as u
import io
import sys
from importlib import util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

R853 = Path(__file__).resolve().parents[1] / "outputs" / "core-r853-rx"
BACKEND = R853 / "repro" / "backend"


def _engines():
    spec = util.spec_from_file_location("rx_engines_r876", BACKEND / "engines.py")
    mod = util.module_from_spec(spec)
    sys.modules["rx_engines_r876"] = mod  # dataclass em Py3.14
    spec.loader.exec_module(mod)
    return mod


def _app(active: str):
    """Carrega app.py e fixa o motor ativo (sem depender do env)."""
    for name in ("rx_engines",):
        sys.modules.pop(name, None)
    spec = util.spec_from_file_location("rx_app_r876", BACKEND / "app.py")
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod._ACTIVE_ENGINE = active
    return mod


def _png(w=800, h=500) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (12, 20, 32)).save(buf, format="PNG")
    return buf.getvalue()


# --- unidade: engines.resolve_capability ------------------------------------

def test_providers_order_real_before_stub():
    e = _engines()
    assert e.providers_for("detection") == ["weights", "stub"]
    assert e.providers_for("sam") == ["open_base", "stub"]


def test_resolve_capability_active_wins_when_it_covers(monkeypatch):
    e = _engines()

    def fake_statuses():
        E = e.EngineInfo
        return [
            E(id="stub", option=0, title="stub", kind="inference",
              capabilities=["detection", "sam", "bundle"], available=True,
              requires=[], env_vars={}, detail="", how_to_enable=""),
            E(id="weights", option=1, title="w", kind="inference",
              capabilities=["detection", "bundle"], available=True,
              requires=[], env_vars={}, detail="", how_to_enable=""),
            E(id="open_base", option=3, title="o", kind="inference",
              capabilities=["sam"], available=True,
              requires=[], env_vars={}, detail="", how_to_enable=""),
        ]

    monkeypatch.setattr(e, "engine_statuses", fake_statuses)
    # ativo cobre -> usa o ativo
    assert e.resolve_capability("sam", "open_base") == "open_base"
    assert e.resolve_capability("detection", "weights") == "weights"
    # ativo não cobre -> melhor disponível
    assert e.resolve_capability("detection", "open_base") == "weights"
    assert e.resolve_capability("sam", "weights") == "open_base"
    # nenhum preferido -> ordem de preferência
    assert e.resolve_capability("detection", None) == "weights"


def test_resolve_capability_fail_closed_returns_none(monkeypatch):
    e = _engines()

    def fake_statuses():
        E = e.EngineInfo
        return [
            E(id="stub", option=0, title="stub", kind="inference",
              capabilities=["detection"], available=False,
              requires=[], env_vars={}, detail="", how_to_enable=""),
            E(id="open_base", option=3, title="o", kind="inference",
              capabilities=["sam"], available=True,
              requires=[], env_vars={}, detail="", how_to_enable=""),
        ]

    monkeypatch.setattr(e, "engine_statuses", fake_statuses)
    assert e.resolve_capability("detection", "open_base") is None  # ninguém cobre
    assert e.resolve_capability("sam", None) == "open_base"


def test_serving_map_shape():
    e = _engines()
    m = e.serving_map("stub")
    assert set(m) == {"detection", "sam", "bundle"}


# --- integração: app com open_base ativo ------------------------------------

def test_predict_falls_back_when_active_engine_lacks_detection(monkeypatch):
    monkeypatch.delenv("RX_WEIGHTS_DIR", raising=False)
    mod = _app("open_base")
    c = TestClient(mod.app)
    r = c.post("/predict", files={"file": ("p.png", _png(), "image/png")})
    assert r.status_code == 200, r.text
    body = r.json()
    # open_base não detecta -> cai para o melhor disponível (stub, sem pesos)
    assert body["engine"] in ("stub", "weights")
    assert body["engine"] != "open_base"
    assert isinstance(body["teeth"], list)


def test_segment_sam_served_by_active_open_base(monkeypatch):
    monkeypatch.setenv("RX_MEDSAM_CKPT", "/tmp/opencode/nao-existe.pth")
    mod = _app("open_base")
    c = TestClient(mod.app)
    r = c.post("/segment/sam", data={"box": "[10,10,60,60]", "target": "generic"},
               files={"file": ("p.png", _png(), "image/png")})
    assert r.status_code == 200, r.text
    # com MedSAM/torch presentes -> open_base; sem eles -> fail no resolve -> stub
    assert r.json()["engine"] in ("open_base", "stub")


def test_health_exposes_serving_map():
    mod = _app("open_base")
    c = TestClient(mod.app)
    health = c.get("/health").json()
    assert "serving" in health["engine"]
    assert set(health["engine"]["serving"]) == {"detection", "sam", "bundle"}


def test_fail_closed_409_when_no_engine_covers(monkeypatch):
    """409 real: nenhum motor disponível cobre 'detection'."""
    mod = _app("open_base")
    c = TestClient(mod.app)

    def _no_detection(cap, preferred=None):
        return None if cap == "detection" else "stub"

    monkeypatch.setattr(mod.engines_mod, "resolve_capability", _no_detection)
    r = c.post("/predict", files={"file": ("p.png", _png(), "image/png")})
    assert r.status_code == 409
    assert "detection" in r.json()["detail"]


def test_opcoes_json_has_serving():
    mod = _app("stub")
    c = TestClient(mod.app)
    j = c.get("/opcoes.json").json()
    assert "serving" in j and set(j["serving"]) == {"detection", "sam", "bundle"}
