"""SPEC-977 — Pipeline de Acesso Aberto Legal por DOI (RED, sem implementação).

Contratos R-977.1 a R-977.9. Usa doubles injetáveis, sem rede real.
Estado inicial esperado: FAIL (módulo research/legal_oa_pipeline.py ausente).
Nenhuma fixture é promovida a evidência externa.
"""
import hashlib
import re


def _norm_doi(doi: str) -> str:
    doi = doi.strip().lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    return doi


def test_r977_doi_normalization_contract():
    # INV-977.4: normalização determinística
    assert _norm_doi("  https://doi.org/10.1038/NATURE12373 ") == "10.1038/nature12373"
    assert _norm_doi("10.1038/nature12373") == "10.1038/nature12373"


def test_r977_pipeline_module_exists():
    # R-977.1/R-977.8: contrato base stdlib-only deve existir (RED até implementar)
    import importlib.util
    assert importlib.util.find_spec("research.legal_oa_pipeline") is not None, \
        "research/legal_oa_pipeline.py ausente — implementar por SPEC-977 sem novas deps"


def test_r977_resolve_enrich_check_gating_contract():
    # R-977.1, R-977.2, R-977.3, R-977.4: resolve -> enrich -> check -> gate
    try:
        from research.legal_oa_pipeline import (
            resolve_doi,
            enrich_openalex,
            check_unpaywall,
            is_download_allowed,
        )
    except ImportError:
        assert False, "API R-977 ausente (RED): resolve_doi/enrich_openalex/check_unpaywall/is_download_allowed"

    # DOI inválido deve falhar tipado, sem fabricar metadados (R-977.1)
    try:
        resolve_doi("not-a-doi", runner=lambda *a, **k: (_ for _ in ()).throw(AssertionError("rede real proibida")))
        assert False, "DOI inválido deveria levantar ValueError"
    except ValueError:
        pass

    # Enriquecimento sem prova não presume OA (R-977.2 — INV-977.2)
    unk = enrich_openalex("10.0000/unknown", runner=lambda *a, **k: {"status": "unknown"})
    assert unk.get("status") == "unknown"
    assert unk.get("is_oa") in (False, None)

    # Sem chave/rede, Unpaywall abstém-se fail-closed (R-977.3)
    un = check_unpaywall("10.1038/nature12373", runner=None)
    assert un.get("status") in ("unavailable", "unknown", "closed")

    # Gate só permite com licença observada + URL (R-977.4, INV-977.1)
    assert is_download_allowed({"license": None, "pdf_url": None})["allowed"] is False
    assert is_download_allowed(
        {"license": "cc-by", "pdf_url": "https://exemplo.org/oa.pdf"}
    )["allowed"] is True


def test_r977_closed_access_route_and_provenance():
    # R-977.5, R-977.6: fechado indica rota institucional + proveniência
    try:
        from research.legal_oa_pipeline import handle_closed_access
    except ImportError:
        assert False, "handle_closed_access ausente (RED)"
        return
    r = handle_closed_access("10.1038/nature12373")
    assert r["allowed"] is False
    assert r["reason"] == "closed_access"
    assert any(k in str(r).lower() for k in ["institucional", "empréstimo", "autor"])
    for k in ("doi", "fonte", "licenca", "data_consulta", "hash_resposta"):
        assert k in r, f"proveniência ausente: {k}"
    h = hashlib.sha256(str(r).encode()).hexdigest()
    assert len(h) == 64


def test_r977_scihub_blocked():
    # R-977.7, INV-977.3: Sci-Hub e espelhos nunca contatados
    try:
        from research.legal_oa_pipeline import guarded_fetch
    except ImportError:
        assert False, "guarded_fetch ausente (RED)"
        return
    for bad in ("https://sci-hub.se/10.1038/x", "https://sci-hub.st/10.1/y", "scihub-mcp://doi/10.1/z"):
        try:
            guarded_fetch(bad, runner=lambda *a, **k: (_ for _ in ()).throw(AssertionError("rede proibida")))
            assert False, f"fonte não autorizada deveria bloquear: {bad}"
        except PermissionError as e:
            assert "unauthorized_source" in str(e) or "blocked" in str(e).lower()
        except ValueError as e:
            assert "unauthorized_source" in str(e) or "blocked" in str(e).lower()
