# -*- coding: utf-8 -*-
"""SPEC-935-R1010 — MCP oa-resolver: contrato, confinamento e anti-fabricação."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / ".opencode" / "mcp" / "oa_resolver_server.py"

fitz = pytest.importorskip("fitz", reason="PyMuPDF necessário para o PDF de teste")


def _load_server():
    spec = importlib.util.spec_from_file_location("oa_resolver_server", SERVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


server = _load_server()


def _make_pdf() -> bytes:
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text(
        (72, 90),
        "We propose a reproducible method for soil moisture estimation that combines satellite retrievals with ground stations. "
        "Results show a 23% reduction in error across 12 stations and three climate regions.",
        fontsize=11,
    )
    p2 = doc.new_page()
    p2.insert_text(
        (72, 90),
        "Limitations include the small sample of 12 stations and the short observation window used in the experiments. "
        "Future work should validate the approach on independent datasets before operational deployment.",
        fontsize=11,
    )
    data = doc.tobytes()
    doc.close()
    return data


PDF = _make_pdf()
DOI = "10.1234/example"


def fake_runner(doi):
    return {
        "pdf_url": "https://example.org/paper.pdf",
        "license": "cc-by-4.0",
        "is_oa": True,
        "host_type": "repository",
    }


def fake_work(doi):
    return {
        "title": "A reproducible method",
        "authorships": [{"author": {"display_name": "João Silva"}}],
        "publication_year": 2020,
        "primary_location": {"source": {"display_name": "Journal of Tests"}},
    }


def fake_fetcher(url):
    return 200, {"content-type": "application/pdf"}, PDF


@pytest.fixture()
def base(tmp_path, monkeypatch):
    monkeypatch.setenv("OA_AUDIT_BASE", str(tmp_path))
    monkeypatch.setattr(server, "openalex_runner", fake_runner)
    monkeypatch.setattr(server, "openalex_work", fake_work)
    monkeypatch.setattr(server, "http_fetcher", fake_fetcher)
    return tmp_path


def test_catalogo_de_ferramentas() -> None:
    names = {tool.name for tool in server.TOOLS}
    assert names == {"oa_resolve", "oa_download", "oa_query_rag", "oa_audit_status", "oa_list_folders"}


def test_resolve_recusa_fonte_bloqueada(base) -> None:
    server.openalex_runner = lambda doi: {
        "pdf_url": "https://sci-hub.se/x",
        "license": "cc-by",
        "is_oa": True,
    }
    out = server.resolve_payload(DOI)
    assert out["status"] == "no_legal_pdf"
    assert out["rejected"][0]["reason"] == "unauthorized_source"


def test_download_exige_confirmacao(base) -> None:
    out = server.download_payload(DOI, confirm=False)
    assert out["status"] == "confirmation_required"
    assert out["requires_confirmation"] is True
    assert list(base.iterdir()) == []


def test_download_confirmado_cria_pacote(base) -> None:
    out = server.download_payload(DOI, confirm=True, max_excerpts=2, keywords=["results"])
    assert out["status"] == "ok", out
    pasta = Path(out["pasta"])
    assert pasta.parent == base
    for nome in ("artigo.pdf", "metadados.json", "paginas.json", "trechos.json", "fichamento.md", "resenha.md", "recibo.json"):
        assert (pasta / nome).is_file(), nome
    fich = (pasta / "fichamento.md").read_text(encoding="utf-8")
    assert "(SILVA, 2020, p." in fich
    assert "Pendente" in fich  # sem LLM, nada é inventado
    assert out["translations_ok"] == 0


def test_query_rag_retorna_pagina(base) -> None:
    out = server.download_payload(DOI, confirm=True, max_excerpts=2, keywords=["results"])
    pasta = Path(out["pasta"]).name
    hits = server.query_payload(pasta, "limitations small sample stations", k=3)
    assert hits["count"] >= 1
    assert hits["hits"][0]["page"] == 2
    assert hits["hits"][0]["citation"].startswith("(SILVA, 2020, p. 2")


def test_confinamento_rejeita_traversal(base) -> None:
    with pytest.raises(ValueError):
        server._confine("../fora")
    with pytest.raises(ValueError):
        server.query_payload("../fora", "x")


def test_status_e_listagem(base) -> None:
    server.download_payload(DOI, confirm=True, max_excerpts=1, keywords=["results"])
    status = server.status_payload("10-1234-example")
    assert status["doi"] == DOI
    assert "rag" in status and status["rag"]["chunks"] >= 1
    listing = server.list_payload()
    assert listing["count"] == 1
    assert listing["pastas"][0]["pasta"] == "10-1234-example"
