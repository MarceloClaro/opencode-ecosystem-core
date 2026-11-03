# -*- coding: utf-8 -*-
"""SPEC-935-R1008 — PDF legal → auditoria → fichamento → resenha → RAG.

Testes offline: o PDF é gerado localmente com PyMuPDF; resolução, download,
tradução e argumentação usam doubles determinísticos.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from research import oa_resolver, pdf_pipeline

fitz = pytest.importorskip("fitz", reason="PyMuPDF necessário para gerar o PDF de teste")

META = {
    "doi": "10.1234/example",
    "titulo": "A reproducible method for soil moisture",
    "autores": ["Silva, João"],
    "ano": 2020,
    "fonte": "Journal of Tests",
    "licenca": "cc-by-4.0",
    "pdf_url": "https://example.org/paper.pdf",
}

PDF_URL = "https://example.org/paper.pdf"


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


def resolver_runner(doi):
    return {
        "pdf_url": PDF_URL,
        "license": "cc-by-4.0",
        "is_oa": True,
        "host_type": "repository",
        "version": "published",
    }


def fetcher(url):
    return 200, {"content-type": "application/pdf"}, PDF


def translator_ok(text, lang):
    base = "Propomos um método reprodutível para estimativa de umidade do solo."
    if "23" in text and "12" in text:
        base += " Os resultados mostram redução de 23% no erro em 12 estações."
    return base


def argumenter_ok(payload):
    return {
        "justificativa": "O trecho sustenta a contribuição metodológica com evidência quantitativa observável.",
        "argumento": "Silva (2020) demonstra redução de erro em 12 estações, o que fundamenta a comparação proposta.",
    }


# ── CA1/CA2: resolução ──────────────────────────────────────────────────────


def test_resolver_recusa_fonte_bloqueada() -> None:
    out = oa_resolver.resolve(
        "10.1234/example",
        runners={"unpaywall": lambda doi: {"pdf_url": "https://sci-hub.se/x", "license": "cc-by", "is_oa": True}},
    )
    assert out["status"] == "no_legal_pdf"
    assert out["chosen"] is None
    assert out["rejected"][0]["reason"] == "unauthorized_source"


def test_sem_runner_nao_baixa(tmp_path: Path) -> None:
    receipt = pdf_pipeline.run("10.1234/example", META, base_dir=str(tmp_path), resolver_runners=None, fetcher=fetcher)
    assert receipt["status"] == "no_legal_pdf"
    assert list(tmp_path.iterdir()) == []


# ── CA3/CA4/CA5 ─────────────────────────────────────────────────────────────


def test_fetcher_rejeita_nao_pdf() -> None:
    with pytest.raises(ValueError):
        pdf_pipeline.fetch_pdf(PDF_URL, fetcher=lambda url: (200, {"content-type": "text/html"}, b"<html>"))


def test_extracao_por_pagina() -> None:
    pages = pdf_pipeline.extract_pages(PDF)
    assert len(pages) == 2
    assert "soil moisture" in pages[0]["text"].lower()
    assert "limitations" in pages[1]["text"].lower()
    assert pages[0]["page"] == 1 and pages[1]["page"] == 2


def test_recortes_deterministicos() -> None:
    pages = pdf_pipeline.extract_pages(PDF)
    a = pdf_pipeline.select_excerpts(pages, max_excerpts=3, keywords=("soil", "method", "limitations"))
    b = pdf_pipeline.select_excerpts(pages, max_excerpts=3, keywords=("soil", "method", "limitations"))
    assert a == b
    assert a and all(x["page"] in (1, 2) for x in a)
    assert all(x["text"] for x in a)


# ── CA6/CA7/CA8: anti-fabricação ────────────────────────────────────────────


def test_traducao_com_numero_inventado_rejeitada() -> None:
    pages = pdf_pipeline.extract_pages(PDF)
    excerpts = pdf_pipeline.select_excerpts(pages, max_excerpts=1, keywords=("results",))
    enriched = pdf_pipeline.enrich_excerpts(
        excerpts, META,
        translator=lambda text, lang: "Resultados mostram redução de 99% no erro.",
    )
    assert enriched[0]["translation"]["status"] == "rejected"
    assert enriched[0]["translation"]["text"] is None


def test_sem_tradutor_fica_pendente() -> None:
    pages = pdf_pipeline.extract_pages(PDF)
    excerpts = pdf_pipeline.select_excerpts(pages, max_excerpts=1, keywords=("results",))
    enriched = pdf_pipeline.enrich_excerpts(excerpts, META, translator=None)
    assert enriched[0]["translation"]["status"] == "pending"
    assert enriched[0]["translation"]["text"] is None


def test_argumentacao_sem_autor_rejeitada() -> None:
    pages = pdf_pipeline.extract_pages(PDF)
    excerpts = pdf_pipeline.select_excerpts(pages, max_excerpts=1, keywords=("results",))
    enriched = pdf_pipeline.enrich_excerpts(
        excerpts, META,
        argumenter=lambda payload: {"justificativa": "Trecho importante para o trabalho em desenvolvimento.", "argumento": "Mostra resultado relevante para a área estudada."},
    )
    assert enriched[0]["argumentation"]["status"] == "rejected"
    assert enriched[0]["argumentation"]["justificativa"] is None


# ── CA9/CA10/CA11: pacote e RAG ─────────────────────────────────────────────


def _run(tmp_path: Path):
    return pdf_pipeline.run(
        "10.1234/example",
        META,
        base_dir=str(tmp_path),
        resolver_runners={"unpaywall": resolver_runner},
        fetcher=fetcher,
        translator=translator_ok,
        argumenter=argumenter_ok,
        max_excerpts=3,
        keywords=("soil", "method", "limitations", "results"),
        now="2026-11-01T00:00:00Z",
    )


def test_fichamento_tem_citacao_abnt(tmp_path: Path) -> None:
    receipt = _run(tmp_path)
    assert receipt["status"] == "ok", receipt
    pasta = Path(receipt["pasta"])
    assert (pasta / "artigo.pdf").exists()
    assert (pasta / "metadados.json").exists()
    assert (pasta / "trechos.json").exists()
    assert (pasta / "resenha.md").exists()
    fich = (pasta / "fichamento.md").read_text(encoding="utf-8")
    assert "(SILVA, 2020, p." in fich
    assert "SILVA, J." in fich
    # tradução validada aparece
    assert "umidade do solo" in fich


def test_rag_recupera_pagina(tmp_path: Path) -> None:
    receipt = _run(tmp_path)
    pasta = Path(receipt["pasta"])
    hits = pdf_pipeline.query_rag(str(pasta), "limitations small sample stations", k=3)
    assert hits
    assert hits[0]["page"] == 2
    assert hits[0]["citation"].startswith("(SILVA, 2020, p. 2")


def test_manifesto_rag_detecta_adulteracao(tmp_path: Path) -> None:
    receipt = _run(tmp_path)
    pasta = Path(receipt["pasta"])
    m1 = json.loads((pasta / "rag" / "manifest.json").read_text(encoding="utf-8"))
    chunks = pasta / "rag" / "chunks.jsonl"
    chunks.write_text(chunks.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert pdf_pipeline.rag_manifest(str(pasta))["sha256"] != m1["sha256"]
