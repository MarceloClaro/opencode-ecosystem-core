"""Testes do servidor local MOCK da Panoramica AI (SPEC-935-R899).

Cobrem o contrato que o front-end exige: multipart, ZIP STORED sem data
descriptor (flags==0 / compression==0) e dimensões da prancha iguais a
``layout.width``/``layout.height``.

Executar:  python3 -m pytest odonto/rx-site-local/tests/test_serve.py -q
"""
from __future__ import annotations

import io
import json
import struct
import sys
import zipfile
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import serve  # noqa: E402


@pytest.fixture(scope="module")
def radiografia() -> bytes:
    buf = io.BytesIO()
    Image.new("L", (900, 400), 60).save(buf, format="PNG")
    return buf.getvalue()


def _cabecalhos_locais(bundle: bytes) -> list[tuple[str, int, int]]:
    """Lê (nome, flags, compressão) de cada cabeçalho local do ZIP."""
    out, pos = [], 0
    while True:
        pos = bundle.find(b"PK\x03\x04", pos)
        if pos < 0:
            return out
        flags, comp = struct.unpack("<HH", bundle[pos + 6:pos + 10])
        nlen, elen = struct.unpack("<HH", bundle[pos + 26:pos + 30])
        out.append((bundle[pos + 30:pos + 30 + nlen].decode(), flags, comp))
        pos += 30 + nlen + elen


def test_multipart_extrai_png(radiografia):
    body = (b'--XYZ\r\nContent-Disposition: form-data; name="file"; filename="rx.png"\r\n'
            b"Content-Type: image/png\r\n\r\n" + radiografia + b"\r\n--XYZ--\r\n")
    assert serve.first_file_bytes(body, "multipart/form-data; boundary=XYZ") == radiografia


def test_multipart_sem_boundary_retorna_none():
    assert serve.first_file_bytes(b"qualquer", "text/plain") is None


def test_padrao_nao_fabrica_deteccoes(radiografia):
    _, headers, layout = serve.build_mock_bundle(radiografia, simulate=0)
    assert headers["X-Teeth-Count"] == "0"
    assert layout["report"]["teeth"] == []
    assert layout["report"]["findings"] == []
    assert layout["cards"] == []


def test_simulacao_gera_caixas_demo(radiografia):
    _, headers, layout = serve.build_mock_bundle(radiografia, simulate=5)
    assert len(layout["report"]["teeth"]) == 5 == int(headers["X-Teeth-Count"])
    assert all(row["mock"] is True for row in layout["report"]["teeth"])
    assert all(card["title"].startswith("DEMO-") for card in layout["cards"])


def test_cards_cabem_no_layout(radiografia):
    _, _, layout = serve.build_mock_bundle(radiografia, simulate=12)
    for card in layout["cards"]:
        assert card["x"] + card["width"] <= layout["width"]
        assert card["y"] + card["height"] <= layout["height"]


def test_zip_stored_sem_data_descriptor(radiografia):
    bundle, _, _ = serve.build_mock_bundle(radiografia, simulate=5)
    entradas = _cabecalhos_locais(bundle)
    assert [nome for nome, _, _ in entradas] == [
        "panoramica-anotada.png", "panoramica-anatomia.png",
        "panoramica-dentes.png", "panoramica-impressao.json",
    ]
    assert all(flags == 0 for _, flags, _ in entradas), "flags!=0 quebra readImageBundle"
    assert all(comp == 0 for _, _, comp in entradas), "compressão!=0 quebra readImageBundle"


def test_prancha_tem_dimensoes_do_layout(radiografia):
    bundle, _, layout = serve.build_mock_bundle(radiografia, simulate=3)
    with zipfile.ZipFile(io.BytesIO(bundle)) as zf:
        prancha = Image.open(io.BytesIO(zf.read("panoramica-dentes.png")))
        assert prancha.size == (layout["width"], layout["height"])
        assert json.loads(zf.read("panoramica-impressao.json")) == layout


def test_classes_de_anotacao_para_o_editor(radiografia):
    _, _, layout = serve.build_mock_bundle(radiografia, simulate=0)
    classes = layout["annotation_classes"]
    assert "55" in classes["teeth"] and "48" in classes["teeth"]
    assert set(classes["additional"]) >= {"maxillary_sinus", "mandibular_canal"}


def test_upload_invalido_degrada_sem_quebrar():
    _, _, layout = serve.build_mock_bundle(b"isto-nao-e-imagem", simulate=0)
    assert layout["width"] > 0 and layout["height"] > 0


def test_aviso_mock_nao_bloqueia_cliques():
    assert 'id="mock-notice"' in serve.MOCK_BANNER
    assert "pointer-events:none" in serve.MOCK_BANNER
    assert "bottom:0" in serve.MOCK_BANNER, "aviso no rodapé não pode cobrir a barra de navegação"
