# -*- coding: utf-8 -*-
"""Regressões Open Science do SPEC-017 v2 / Pesquisador Universal v4.2.

Todos os testes são offline. Eles verificam política de acesso e integridade do
artefato; não validam disponibilidade das APIs externas.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.downloader import PaperDownloader
from research.searchers import PaperRecord


class _Headers(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class _FakeResponse:
    def __init__(self, body: bytes, headers=None):
        self._body = body
        self._pos = 0
        self.headers = _Headers(headers or {})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, size=-1):
        if size is None or size < 0:
            size = len(self._body) - self._pos
        start = self._pos
        end = min(len(self._body), start + size)
        self._pos = end
        return self._body[start:end]


def _rec(**kwargs):
    base = {
        "title": "Open science test paper",
        "authors": ["Silva, Ana"],
        "year": 2026,
        "doi": "10.1234/open.1",
        "source": "openalex",
        "pdf_url": "https://repository.example/paper.pdf",
        "extra": {},
    }
    base.update(kwargs)
    return PaperRecord(**base)


def test_direct_open_access_pdf_is_hash_recorded(tmp_path, monkeypatch):
    payload = b"%PDF-1.7\nopen-science\n%%EOF\n"
    monkeypatch.setattr(
        "research.downloader.urllib.request.urlopen",
        lambda *a, **k: _FakeResponse(payload, {"Content-Length": str(len(payload))}),
    )
    dl = PaperDownloader(str(tmp_path))
    result = dl.download([_rec()])[0]
    assert result.ok is True
    assert result.method == "direct_oa"
    assert result.extra["validated_pdf_magic"] is True
    assert result.extra["sha256"] == hashlib.sha256(payload).hexdigest()
    assert Path(result.pdf_path).read_bytes() == payload
    receipt_path = Path(result.extra["receipt"])
    assert receipt_path.exists()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["sha256"] == hashlib.sha256(payload).hexdigest()
    assert receipt["access_basis"] == "open_access"
    assert receipt["validated_pdf_magic"] is True


def test_html_disfarçado_de_pdf_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "research.downloader.urllib.request.urlopen",
        lambda *a, **k: _FakeResponse(b"<html>paywall</html>", {}),
    )
    dl = PaperDownloader(str(tmp_path))
    result = dl.download([_rec()])[0]
    assert result.ok is False
    assert "magic bytes" in result.error
    assert not list(tmp_path.glob("*.pdf"))
    assert not list(tmp_path.glob("*.receipt.json"))


def test_crossref_pdf_url_is_not_presumed_open(tmp_path, monkeypatch):
    dl = PaperDownloader(str(tmp_path))
    monkeypatch.setattr(dl, "_resolve_openalex_oa", lambda doi: None)
    monkeypatch.setattr(dl, "_resolve_europepmc_oa", lambda doi: None)
    rec = _rec(source="crossref", pdf_url="https://publisher.example/article.pdf")
    result = dl.download([rec])[0]
    assert result.ok is False
    assert result.extra["attempted_routes"] == 0


def test_doi_resolver_stops_after_openalex_success(tmp_path, monkeypatch):
    calls = []
    dl = PaperDownloader(str(tmp_path), email="researcher@example.org")

    def openalex(doi):
        calls.append("openalex")
        return ("https://repo.example/openalex.pdf", {"resolver": "openalex", "access_basis": "open_access"})

    def unpaywall(doi):
        calls.append("unpaywall")
        return ("https://repo.example/unpaywall.pdf", {"resolver": "unpaywall", "access_basis": "open_access"})

    monkeypatch.setattr(dl, "_resolve_openalex_oa", openalex)
    monkeypatch.setattr(dl, "_resolve_unpaywall_oa", unpaywall)
    monkeypatch.setattr(dl, "_resolve_europepmc_oa", lambda doi: None)
    monkeypatch.setattr(
        dl,
        "_download_pdf",
        lambda rec, method, url, metadata: type("R", (), {
            "ok": method == "openalex_oa",
            "method": method,
            "error": "",
            "record": rec,
            "pdf_path": "/tmp/fake.pdf",
            "extra": metadata,
        })(),
    )

    result = dl.download([_rec(pdf_url=None, source="crossref")])[0]
    assert result.ok is True
    assert result.method == "openalex_oa"
    assert calls == ["openalex"]


def test_record_explicitly_marked_repository_may_use_direct_url(tmp_path, monkeypatch):
    payload = b"%PDF-1.4\nrepo\n%%EOF\n"
    monkeypatch.setattr(
        "research.downloader.urllib.request.urlopen",
        lambda *a, **k: _FakeResponse(payload, {}),
    )
    dl = PaperDownloader(str(tmp_path))
    rec = _rec(
        source="custom",
        extra={"access_basis": "repository"},
        pdf_url="https://institutional.example/accepted-manuscript.pdf",
    )
    result = dl.download([rec])[0]
    assert result.ok is True
    assert result.method == "direct_oa"
    assert result.extra["access_basis"] == "repository"


def test_receipt_strips_query_but_hashes_full_source_url(tmp_path, monkeypatch):
    payload = b"%PDF-1.7\nsigned-url\n%%EOF\n"
    signed = "https://repository.example/paper.pdf?token=secret-temporary&expires=123"
    monkeypatch.setattr(
        "research.downloader.urllib.request.urlopen",
        lambda *a, **k: _FakeResponse(payload, {}),
    )
    dl = PaperDownloader(str(tmp_path))
    result = dl.download([_rec(pdf_url=signed)])[0]
    receipt = json.loads(Path(result.extra["receipt"]).read_text(encoding="utf-8"))
    assert receipt["source_url"] == "https://repository.example/paper.pdf"
    assert "secret-temporary" not in json.dumps(receipt)
    assert receipt["source_url_sha256"] == hashlib.sha256(signed.encode("utf-8")).hexdigest()


def test_runtime_downloader_does_not_depend_on_external_bypass_cli():
    import inspect
    import research.downloader as downloader

    source = inspect.getsource(downloader)
    forbidden = "sci" + "hub-cli"
    assert forbidden not in source.lower()
    assert "subprocess" not in source
    assert "shutil.which" not in source


def test_doctor_does_not_register_external_paywall_bypass_cli():
    from marceloclaro import doctor

    forbidden = "sci" + "hub-cli"
    assert forbidden not in {name.lower() for name in doctor.EXTERNAL_CLIS}


def test_spec_017_declares_crossref_metadata_only():
    spec = Path(__file__).resolve().parents[1] / "specs" / "SPEC-017-research.md"
    text = spec.read_text(encoding="utf-8").lower()
    assert "crossref é usado para doi/metadados" in text
    assert "não comprovam acesso aberto" in text
