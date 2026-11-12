# -*- coding: utf-8 -*-
"""Testes do MCP stdio local Tiangong — SPEC-935-R1089-MCP.

Cobertura hermética: sem rede, sem Pillow, sem arquivos externos. O PNG é
gerado no próprio teste com ``zlib`` e o transporte stdio é exercitado com o
mesmo interpretador do ``.venv``.
"""

from __future__ import annotations

import json
import math
import struct
import subprocess
import sys
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from integrations import tiangong_mcp  # noqa: E402


# ── helpers PNG (stdlib) ─────────────────────────────────────────────────────


def _chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def _png(width: int, height: int, color_type: int, rows: list[bytes]) -> bytes:
    raw = b"".join(rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw))
        + _chunk(b"IEND", b"")
    )


def _png_gray(width: int, height: int, pixels: list[list[int]]) -> bytes:
    rows = [b"\x00" + bytes(row) for row in pixels]
    return _png(width, height, 0, rows)


def _png_rgb(width: int, height: int, pixels: list[list[tuple[int, int, int]]]) -> bytes:
    rows = [b"\x00" + bytes(v for px in row for v in px) for row in pixels]
    return _png(width, height, 2, rows)


def _png_rgba(width: int, height: int, pixels: list[list[tuple[int, int, int, int]]]) -> bytes:
    rows = [b"\x00" + bytes(v for px in row for v in px) for row in pixels]
    return _png(width, height, 6, rows)


def _b64(data: bytes) -> str:
    import base64

    return base64.b64encode(data).decode("ascii")


# ── catálogo ────────────────────────────────────────────────────────────────


def test_catalog_lista_tres_apps_com_hashes_reais():
    out = tiangong_mcp.catalog()
    assert out["status"] == "success"
    apps = {a["app"]: a for a in out["result"]["apps"]}
    assert set(apps) == {"HDR", "RSIR", "VRP"}
    assert apps["HDR"]["source_bundle_sha256"] == (
        "7f6e3f71fa4fcc42cd6dafef79f881f0a32afe44db43f001eac9893e7d1f9eea"
    )
    assert apps["RSIR"]["source_bundle_sha256"] == (
        "76308919310a4b6235a21fe83a4e96d0b83949f486602ea774998a508ff8c418"
    )
    assert apps["VRP"]["source_bundle_sha256"] == (
        "38acd57efc1fd70229a9fad67bfd0a4c3d2886bc4146d562675de9383397cfe6"
    )
    for app in apps.values():
        assert app["source_html_sha256"] == (
            "8040aca93fb0c658ff15108ecf2cbca9a5442fa2e395a579545a41cbeb73f342"
        )
        assert app["limitations"]


def test_catalog_declara_sem_rede_e_sem_credenciais():
    out = tiangong_mcp.catalog()
    assert out["result"]["network"] is False
    assert out["result"]["credentials_required"] is False
    assert out["evidence"]["method"] == "static_analysis_REA"


# ── HDR: falhas fechadas ────────────────────────────────────────────────────


def test_hdr_action_ausente_falha():
    out = tiangong_mcp.hdr_handler()
    assert out["status"] == "error"
    assert out["result"]["code"] == "missing_action"


def test_hdr_action_desconhecida_falha():
    out = tiangong_mcp.hdr_handler(action="treinar")
    assert out["status"] == "error"
    assert out["result"]["code"] == "invalid_action"


def test_hdr_recusa_image_path():
    out = tiangong_mcp.hdr_handler(action="preprocess", image_path="/etc/passwd")
    assert out["status"] == "error"
    assert out["result"]["code"] == "path_not_allowed"


def test_hdr_recusa_formato_nao_png():
    out = tiangong_mcp.hdr_handler(
        action="preprocess", image_base64=_b64(b"\xff\xd8\xff\xe0JFIF")
    )
    assert out["status"] == "error"
    assert out["result"]["code"] == "unsupported_image_format"


def test_hdr_recusa_payload_acima_do_limite():
    payload = _b64(b"x" * (tiangong_mcp.MAX_IMAGE_BYTES + 1))
    out = tiangong_mcp.hdr_handler(action="preprocess", image_base64=payload)
    assert out["status"] == "error"
    assert out["result"]["code"] == "payload_too_large"


def test_hdr_recusa_png_corrompido():
    good = _png_gray(2, 1, [[0, 255]])
    out = tiangong_mcp.hdr_handler(
        action="preprocess", image_base64=_b64(good[:-12])
    )
    assert out["status"] == "error"
    assert out["result"]["code"] == "invalid_image"


# ── HDR: pré-processamento determinístico ──────────────────────────────────


def test_hdr_preprocess_cinza_28x28():
    pixels = [[(x + y) % 256 for x in range(28)] for y in range(28)]
    png = _png_gray(28, 28, pixels)
    out = tiangong_mcp.hdr_handler(action="preprocess", image_base64=_b64(png))
    assert out["status"] == "success"
    assert out["result"]["feature_dim"] == 784
    vec = out["result"]["feature_vector"]
    assert len(vec) == 784
    assert vec[0] == 0.0
    assert vec[-1] == pytest.approx((27 + 27) % 256 / 255.0, abs=1e-6)
    assert out["result"]["input_sha256"] == tiangong_mcp.sha256_hex(png)
    assert all(0.0 <= v <= 1.0 for v in vec)


def test_hdr_preprocess_rgb_converte_para_cinza():
    pixels = [
        [(255, 0, 0), (0, 255, 0)],
        [(0, 0, 255), (255, 255, 255)],
    ]
    out = tiangong_mcp.hdr_handler(
        action="preprocess", image_base64=_b64(_png_rgb(2, 2, pixels))
    )
    assert out["status"] == "success"
    vec = out["result"]["feature_vector"]
    # 2x2 ampliado para 28x28: cantos preservam a ordem dos pixels.
    assert vec[0] == pytest.approx(0.299, abs=1e-3)
    assert vec[27] == pytest.approx(0.587, abs=1e-3)
    assert vec[28 * 27] == pytest.approx(0.114, abs=1e-3)
    assert vec[-1] == pytest.approx(1.0, abs=1e-6)


def test_hdr_preprocess_rgba_ignora_alfa():
    pixels = [[(255, 0, 0, 10), (0, 255, 0, 200)]]
    out = tiangong_mcp.hdr_handler(
        action="preprocess", image_base64=_b64(_png_rgba(2, 1, pixels))
    )
    assert out["status"] == "success"
    vec = out["result"]["feature_vector"]
    assert vec[0] == pytest.approx(0.299, abs=1e-3)
    assert vec[27] == pytest.approx(0.587, abs=1e-3)


def test_hdr_preprocess_filtro_sub():
    # 2x1 cinza: valores 10 e 20, com filtro Sub (20-10=10).
    raw = b"\x01" + bytes([10, 10])
    png = _png(2, 1, 0, [raw])
    out = tiangong_mcp.hdr_handler(action="preprocess", image_base64=_b64(png))
    assert out["status"] == "success"
    vec = out["result"]["feature_vector"]
    assert vec[0] == pytest.approx(10 / 255.0, abs=1e-6)
    assert vec[27] == pytest.approx(20 / 255.0, abs=1e-6)


def test_hdr_preprocess_pixels_e_downscale():
    pixels = [[0, 255, 0, 255], [255, 0, 255, 0], [0, 255, 0, 255], [255, 0, 255, 0]]
    out = tiangong_mcp.hdr_handler(action="preprocess", pixels=pixels)
    assert out["status"] == "success"
    vec = out["result"]["feature_vector"]
    assert len(vec) == 784
    assert 0.0 <= min(vec) <= max(vec) <= 1.0
    # média global de uma matriz equilibrada tende a 0,5
    assert sum(vec) / len(vec) == pytest.approx(0.5, abs=0.05)


@pytest.mark.parametrize(
    "pixels, code",
    [
        ([], "invalid_pixels"),
        ([[0, 1], [0]], "invalid_pixels"),
        ([[0, 300]], "invalid_pixels"),
        ([[0, float("nan")]], "invalid_pixels"),
        ("nao-e-matriz", "invalid_pixels"),
    ],
)
def test_hdr_preprocess_pixels_invalidos(pixels, code):
    out = tiangong_mcp.hdr_handler(action="preprocess", pixels=pixels)
    assert out["status"] == "error"
    assert out["result"]["code"] == code


# ── HDR: reconhecimento não fabricado ──────────────────────────────────────


def test_hdr_recognize_indisponivel_sem_fabricacao():
    out = tiangong_mcp.hdr_handler(action="recognize")
    assert out["status"] == "unavailable"
    assert out["result"]["code"] == "provider_not_implemented"
    assert out["result"]["digit"] is None
    assert out["result"]["confidence"] is None
    assert any("backend" in item.lower() for item in out["limitations"])


# ── HDR: comparação ────────────────────────────────────────────────────────


def test_hdr_compare_vetores():
    a = [0.0] * 784
    b = [0.0] * 783 + [1.0]
    out = tiangong_mcp.hdr_handler(action="compare", left=a, right=b)
    assert out["status"] == "success"
    r = out["result"]
    assert r["dimension"] == 784
    assert r["l1"] == pytest.approx(1.0, abs=1e-6)
    assert r["l2"] == pytest.approx(1.0, abs=1e-6)
    assert r["cosine"] == pytest.approx(0.0, abs=1e-6)


def test_hdr_compare_dimensoes_diferentes_falha():
    out = tiangong_mcp.hdr_handler(action="compare", left=[0.0] * 3, right=[0.0] * 4)
    assert out["status"] == "error"
    assert out["result"]["code"] == "dimension_mismatch"


def test_hdr_export_nao_grava_arquivo():
    out = tiangong_mcp.hdr_handler(action="export", pixels=[[0] * 28] * 28)
    assert out["status"] == "success"
    assert out["result"]["format"] == "json"
    assert "path" not in out["result"]


# ── RSIR ────────────────────────────────────────────────────────────────────


def test_rsir_analyze_indisponivel_sem_rotulo():
    out = tiangong_mcp.rsir_handler(action="analyze")
    assert out["status"] == "unavailable"
    assert out["result"]["code"] == "provider_not_implemented"
    assert out["result"]["class_label"] is None
    assert out["result"]["probabilities"] is None


def test_rsir_classify_indisponivel_sem_rotulo():
    out = tiangong_mcp.rsir_handler(action="classify")
    assert out["status"] == "unavailable"
    assert out["result"]["class_label"] is None


def test_rsir_features_validas():
    vec = [0.5] * 768
    out = tiangong_mcp.rsir_handler(action="features", features=vec)
    assert out["status"] == "success"
    assert out["result"]["dimension"] == 768
    assert out["result"]["mean"] == pytest.approx(0.5, abs=1e-6)
    assert out["result"]["l2_norm"] == pytest.approx(math.sqrt(768 * 0.25), abs=1e-6)


def test_rsir_features_dimensao_errada():
    out = tiangong_mcp.rsir_handler(action="features", features=[0.0] * 10)
    assert out["status"] == "error"
    assert out["result"]["code"] == "dimension_mismatch"


def test_rsir_features_nao_finitas():
    vec = [0.0] * 768
    vec[0] = float("inf")
    out = tiangong_mcp.rsir_handler(action="features", features=vec)
    assert out["status"] == "error"
    assert out["result"]["code"] == "invalid_vector"


# ── VRP ─────────────────────────────────────────────────────────────────────


def _vrp_instance():
    return {
        "nodes": [
            {"id": "0", "x": 0, "y": 0, "demand": 0},
            {"id": "1", "x": 1, "y": 0, "demand": 2},
            {"id": "2", "x": 0, "y": 1, "demand": 2},
            {"id": "3", "x": 1, "y": 1, "demand": 2},
        ],
        "vehicles": [
            {"id": "v1", "capacity": 4},
            {"id": "v2", "capacity": 4},
        ],
    }


def test_vrp_validate():
    out = tiangong_mcp.vrp_handler(action="validate", **_vrp_instance())
    assert out["status"] == "success"
    assert out["result"]["n_nodes"] == 4
    assert out["result"]["n_vehicles"] == 2
    assert out["result"]["total_demand"] == 6
    assert out["result"]["capacity"] == 8


def test_vrp_solve_deterministico_e_factivel():
    kwargs = _vrp_instance()
    a = tiangong_mcp.vrp_handler(action="solve", **kwargs)
    b = tiangong_mcp.vrp_handler(action="solve", **kwargs)
    assert a == b
    assert a["status"] == "success"
    r = a["result"]
    assert r["backend"] == "classical-heuristic"
    assert r["quantum"] is False
    assert r["optimality"] == "not_proven"
    assert r["feasible"] is True
    assert r["unserved"] == []
    served = [node for route in r["routes"] for node in route["node_ids"]]
    assert set(served) == {"0", "1", "2", "3"}
    assert sum(1 for node in served if node != "0") == 3
    assert r["total_distance"] > 0


def test_vrp_solve_inviavel_por_capacidade():
    nodes = [
        {"id": "0", "x": 0, "y": 0, "demand": 0},
        {"id": "1", "x": 1, "y": 0, "demand": 9},
    ]
    out = tiangong_mcp.vrp_handler(
        action="solve", nodes=nodes, vehicles=[{"id": "v1", "capacity": 5}]
    )
    assert out["status"] == "success"
    assert out["result"]["feasible"] is False
    assert out["result"]["unserved"] == ["1"]


def test_vrp_recusa_demanda_negativa():
    nodes = [
        {"id": "0", "x": 0, "y": 0, "demand": 0},
        {"id": "1", "x": 1, "y": 0, "demand": -1},
    ]
    out = tiangong_mcp.vrp_handler(
        action="solve", nodes=nodes, vehicles=[{"id": "v1", "capacity": 5}]
    )
    assert out["status"] == "error"
    assert out["result"]["code"] == "invalid_payload"


def test_vrp_recusa_limite_de_nos():
    nodes = [{"id": str(i), "x": i, "y": 0, "demand": 1} for i in range(201)]
    out = tiangong_mcp.vrp_handler(
        action="solve", nodes=nodes, vehicles=[{"id": "v1", "capacity": 500}]
    )
    assert out["status"] == "error"
    assert out["result"]["code"] == "limit_exceeded"


def test_vrp_upload_indisponivel():
    out = tiangong_mcp.vrp_handler(action="upload")
    assert out["status"] == "unavailable"
    assert out["result"]["code"] == "provider_not_implemented"


# ── segurança e transporte ──────────────────────────────────────────────────


def test_modulo_sem_rede_ou_shell():
    source = (ROOT / "integrations" / "tiangong_mcp.py").read_text(encoding="utf-8")
    for forbidden in (
        "import socket",
        "import subprocess",
        "import requests",
        "import urllib",
        "import http.client",
        "os.system(",
        "Popen(",
    ):
        assert forbidden not in source, f"proibido no servidor MCP: {forbidden}"


def _read_message(proc: subprocess.Popen) -> dict:
    while True:
        line = proc.stdout.readline()
        if not line:
            raise AssertionError(f"EOF inesperado do servidor MCP: {proc.stderr.read()[-1000:]}")
        line = line.strip()
        if line.startswith("{"):
            return json.loads(line)


def _send(proc: subprocess.Popen, message: dict) -> None:
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()


def test_transporte_stdio_real():
    proc = subprocess.Popen(
        [sys.executable, "-m", "integrations.tiangong_mcp"],
        cwd=str(ROOT),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        _send(proc, {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "pytest-r1089", "version": "1.0"},
            },
        })
        initialized = _read_message(proc)
        assert initialized["result"]["serverInfo"]["name"] == "tiangong-hdr"

        _send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        _send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        listed = _read_message(proc)
        names = {tool["name"] for tool in listed["result"]["tools"]}
        assert {"tiangong_catalog", "hdr_handler", "rsir_handler", "vrp_handler"} <= names

        _send(proc, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "tiangong_catalog", "arguments": {}},
        })
        called = _read_message(proc)
        body = json.loads(called["result"]["content"][0]["text"])
        assert body["status"] == "success"
        assert {a["app"] for a in body["result"]["apps"]} == {"HDR", "RSIR", "VRP"}
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    assert proc.returncode == 0
