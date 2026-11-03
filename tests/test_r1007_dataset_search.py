# -*- coding: utf-8 -*-
"""SPEC-935-R1007 — buscador de datasets multi-provedor.

Testes offline: nenhuma rede. Os payloads reproduzem a forma documentada dos
seis provedores, verificada em 2026-11-01.
"""
from __future__ import annotations

import json

import pytest

from research import dataset_search as ds
from research import source_policy


# ── payloads sintéticos (forma real dos provedores) ──────────────────────────

ZENODO = {
    "hits": {
        "hits": [
            {
                "id": 5159133,
                "doi": "10.5281/zenodo.5159133",
                "metadata": {
                    "title": "Soil Survey of Scotland",
                    "description": "<p>Digital soil maps at 1:25 000 scale, digitised from the Soils of Scotland survey.</p>",
                    "publication_date": "2021-08-04",
                    "license": {"id": "cc-by-4.0"},
                    "creators": [{"name": "Scotland, Soil Survey"}],
                },
                "files": [{"key": "soil.csv", "size": 1024}],
                "links": {"self_html": "https://zenodo.org/records/5159133"},
                "updated": "2025-05-19T15:23:11Z",
            }
        ]
    }
}

DATACITE = {
    "data": [
        {
            "id": "10.5281/zenodo.5159133",
            "attributes": {
                "doi": "10.5281/zenodo.5159133",
                "titles": [{"title": "Soil Survey of Scotland"}],
                "creators": [{"name": "Scotland, Soil Survey"}],
                "publisher": "Zenodo",
                "publicationYear": 2021,
                "types": {"resourceTypeGeneral": "Dataset"},
                "url": "https://zenodo.org/records/5159133",
                # sem license => unknown
            },
        }
    ]
}

FIGSHARE = [
    {
        "id": 34876254,
        "title": "<b>Alpine Meadow Degradation</b>",
        "doi": "10.6084/m9.figshare.34876254.v1",
        "url": "https://api.figshare.com/v2/articles/34876254",
        "published_date": "2026-11-01T10:23:14Z",
        "defined_type_name": "dataset",
        "license": {"name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/"},
    }
]

OPENALEX = {
    "meta": {"count": 1},
    "results": [
        {
            "id": "https://openalex.org/W123",
            "doi": "https://doi.org/10.5061/dryad.abc",
            "title": "Global soil moisture dataset",
            "publication_year": 2020,
            "open_access": {"is_oa": True, "oa_status": "gold"},
            "best_oa_location": {"pdf_url": "https://example.org/soil.pdf", "license": "cc-by"},
            "primary_location": {"landing_page_url": "https://example.org/soil"},
            "cited_by_count": 42,
        }
    ],
}

HUGGINGFACE = [
    {
        "id": "soille/denis",
        "author": "soille",
        "gated": False,
        "private": False,
        "downloads": 10,
        "likes": 2,
        "lastModified": "2024-02-04T02:18:34.000Z",
        "tags": ["task_categories:image-segmentation", "format:parquet", "license:mit"],
    },
    {
        "id": "acme/gated",
        "author": "acme",
        "gated": True,
        "private": False,
        "downloads": 0,
        "likes": 0,
        "lastModified": "2024-02-04T02:18:34.000Z",
        "tags": ["license:unknown"],
    },
]

GBIF = {
    "results": [
        {
            "key": "d27fe7f2",
            "title": "Cyanobacteria of Algal Collection",
            "doi": "10.15468/nt9emp",
            "description": "Algal Collection of Soil Science Institute, established in 2016.",
            "license": "CC0 1.0",
            "publisher": "Soil Science Institute",
            "type": "OCCURRENCE",
        }
    ]
}

PAYLOADS = {
    "zenodo": ZENODO,
    "datacite": DATACITE,
    "figshare": FIGSHARE,
    "openalex": OPENALEX,
    "huggingface": HUGGINGFACE,
    "gbif": GBIF,
}


def fake_runner(provider, request):
    return PAYLOADS[provider]


# ── CA1: requisições ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "provider,method,fragment",
    [
        ("zenodo", "GET", "zenodo.org/api/records"),
        ("datacite", "GET", "api.datacite.org/dois"),
        ("figshare", "POST", "api.figshare.com/v2/articles/search"),
        ("openalex", "GET", "api.openalex.org/works"),
        ("huggingface", "GET", "huggingface.co/api/datasets"),
        ("gbif", "GET", "api.gbif.org/v1/dataset/search"),
    ],
)
def test_build_request_por_provedor(provider: str, method: str, fragment: str) -> None:
    req = ds.build_request(provider, "soil moisture", 5)
    assert req["method"] == method
    assert fragment in req["url"]
    if method == "GET":
        assert "soil" in req["url"] and "5" in req["url"]
    else:
        assert json.loads(req["body"])["search_for"] == "soil moisture"
        assert json.loads(req["body"])["page_size"] == 5


def test_build_request_recusa_provedor_desconhecido() -> None:
    with pytest.raises(ValueError):
        ds.build_request("scihub", "x", 1)


# ── CA2: parsers ────────────────────────────────────────────────────────────


def test_parse_zenodo_normaliza() -> None:
    recs = ds.parse("zenodo", ZENODO, endpoint="e", retrieved_at="2026-11-01T00:00:00Z")
    assert len(recs) == 1
    r = recs[0]
    assert r.doi == "10.5281/zenodo.5159133"
    assert r.year == 2021
    assert r.authors == ("Scotland, Soil Survey",)
    assert r.license_class == "open"
    assert r.access == "open"
    assert "csv" in r.formats
    assert len(r.provenance) == 1 and r.provenance[0]["raw_sha256"]


def test_parse_figshare_remove_html_do_titulo() -> None:
    recs = ds.parse("figshare", FIGSHARE, endpoint="e", retrieved_at="2026-11-01T00:00:00Z")
    assert recs[0].title == "Alpine Meadow Degradation"
    assert recs[0].license_class == "open"


def test_parse_huggingface_respeita_gated_e_licenca() -> None:
    recs = ds.parse("huggingface", HUGGINGFACE, endpoint="e", retrieved_at="2026-11-01T00:00:00Z")
    aberto, restrito = recs
    assert aberto.access == "open"
    assert aberto.license_class == "open"
    assert "parquet" in aberto.formats
    assert restrito.access == "restricted"
    assert restrito.license_class == "unknown"


# ── CA3/CA4/CA5: fail-closed, bloqueio e licença ────────────────────────────


def test_sem_runner_fail_closed() -> None:
    report = ds.search("soil", providers=["zenodo"], limit=3, runner=None, now="2026-11-01T00:00:00Z")
    assert report["results"] == []
    assert report["providers"]["zenodo"]["status"] == "unavailable"


def test_fonte_bloqueada_descartada() -> None:
    payload = {
        "data": [
            {
                "id": "10.1/x",
                "attributes": {
                    "doi": "10.1/x",
                    "titles": [{"title": "Pirated"}],
                    "url": "https://sci-hub.se/10.1/x",
                    "publicationYear": 2020,
                    "types": {"resourceTypeGeneral": "Dataset"},
                },
            }
        ]
    }
    report = ds.search(
        "x", providers=["datacite"], limit=1, runner=lambda p, r: payload, now="2026-11-01T00:00:00Z"
    )
    assert report["results"] == []
    assert report["rejected"][0]["reason"] == "unauthorized_source"


def test_licenca_ausente_nao_e_aberta() -> None:
    recs = ds.parse("datacite", DATACITE, endpoint="e", retrieved_at="2026-11-01T00:00:00Z")
    assert recs[0].license_class == "unknown"
    assert ds.fair_score(recs[0])["components"]["licensed"] == 0.0


# ── CA6/CA7/CA8/CA9/CA10 ────────────────────────────────────────────────────


def test_dedup_por_doi_preserva_proveniencia() -> None:
    zen = ds.parse("zenodo", ZENODO, endpoint="z", retrieved_at="2026-11-01T00:00:00Z")
    dc = ds.parse("datacite", DATACITE, endpoint="d", retrieved_at="2026-11-01T00:00:00Z")
    merged = ds.deduplicate(zen + dc)
    assert len(merged) == 1
    assert len(merged[0].provenance) == 2
    # preserva a licença observada (zenodo open) em vez de rebaixar para unknown
    assert merged[0].license_class == "open"


def test_ranking_deterministico_e_explicavel() -> None:
    a = ds.parse("zenodo", ZENODO, endpoint="z", retrieved_at="t")[0]
    b = ds.parse("datacite", DATACITE, endpoint="d", retrieved_at="t")[0]
    ranked1 = ds.rank("soil scotland", [a, b], now_year=2026)
    ranked2 = ds.rank("soil scotland", [b, a], now_year=2026)
    assert [r["doi"] for r in ranked1] == [r["doi"] for r in ranked2]
    assert "final" in ranked1[0]["scores"] and "components" in ranked1[0]["scores"]


def test_manifesto_detecta_adulteracao() -> None:
    report = ds.search("soil", providers=["zenodo"], limit=1, runner=fake_runner, now="2026-11-01T00:00:00Z")
    m1 = ds.manifest(report)
    tampered = json.loads(json.dumps(report))
    tampered["results"][0]["title"] = "alterado"
    m2 = ds.manifest(tampered)
    assert m1["sha256"] != m2["sha256"]


def test_campos_ausentes_sao_none() -> None:
    payload = {"results": [{"key": "k", "title": "Sem metadados"}]}
    recs = ds.parse("gbif", payload, endpoint="e", retrieved_at="t")
    r = recs[0]
    assert r.doi is None and r.year is None and r.downloads is None and r.citations is None
    assert r.license_class == "unknown"


def test_busca_completa_reprodutivel() -> None:
    a = ds.search("soil", providers=list(ds.PROVIDERS), limit=5, runner=fake_runner, now="2026-11-01T00:00:00Z")
    b = ds.search("soil", providers=list(ds.PROVIDERS), limit=5, runner=fake_runner, now="2026-11-01T00:00:00Z")
    assert ds.manifest(a)["sha256"] == ds.manifest(b)["sha256"]
    assert a["count"] >= 1
    assert set(a["providers"]) == set(ds.PROVIDERS)


def test_politica_de_fontes() -> None:
    assert source_policy.is_blocked_url("https://sci-hub.se/10.1/x")
    assert source_policy.is_blocked_url("HTTPS://SCI-HUB.RU/x")
    assert source_policy.is_blocked_url("scihub-mcp://archive/x")
    assert source_policy.is_blocked_url("https://example.org/?ref=sci-hub")
    assert not source_policy.is_blocked_url("https://doi.org/10.5281/zenodo.1")
    with pytest.raises(PermissionError):
        source_policy.assert_allowed_url("https://scihub.org/x")
