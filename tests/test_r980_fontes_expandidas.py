"""SPEC-980 — Fontes expandidas (hermético, sem rede)."""
import json


def test_r980_modulo():
    import importlib.util
    assert importlib.util.find_spec("research.fontes_expandidas") is not None


def test_r980_pubmed_arxiv_doubles():
    from research.fontes_expandidas import buscar_pubmed, buscar_arxiv
    fake_pub = lambda url: json.dumps({"esearchresult": {"idlist": ["123", "456"]}}).encode()
    r = buscar_pubmed("dengue", 2, fake_pub)
    assert len(r) == 2 and r[0]["fonte"] == "pubmed" and "hash_resposta" in r[0]
    atom = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>T</title>"""
    atom += b"""<id>http://arxiv.org/abs/2301.00001</id><author><name>A B</name></author></entry></feed>"""
    r2 = buscar_arxiv("dengue", 1, lambda u: atom)
    assert r2[0]["arxiv_id"] == "2301.00001" and r2[0]["fonte"] == "arxiv"


def test_r980_brasileiras_sucupira_capes_doubles():
    from research.fontes_expandidas import (buscar_scielo, buscar_lilacs, buscar_oasisbr_btdt,
                                            buscar_sucupira_observatorio, buscar_capes_dados_abertos,
                                            consultar_portal_capes, buscar_todas)
    assert buscar_scielo("dengue", 1, lambda u: b"ok")[0]["fonte"] == "scielo"
    assert buscar_lilacs("dengue", 1, lambda u: b"ok")[0]["fonte"] == "lilacs"
    assert len(buscar_oasisbr_btdt("dengue", 2, lambda u: b"ok")) == 2
    fake_s = lambda u: json.dumps({"content": [{"nome": "IES X"}]}).encode()
    assert buscar_sucupira_observatorio("sao", 1, fake_s)[0]["fonte"] == "sucupira"
    fake_c = lambda u: json.dumps({"result": {"results": [{"title": "DS", "name": "ds"}]}}).encode()
    assert buscar_capes_dados_abertos("bolsa", 1, fake_c)[0]["fonte"] == "capes_dados_abertos"
    pc = consultar_portal_capes("10.1/x")
    assert pc["status"] == "unavailable" and "periodicos.capes" in pc["rota_institucional"]
    runners = {"pubmed": lambda u: json.dumps({"esearchresult": {"idlist": ["1"]}}).encode(),
               "arxiv": lambda u: b"<feed xmlns='http://www.w3.org/2005/Atom'></feed>",
               "scielo": lambda u: b"ok", "lilacs": lambda u: b"ok",
               "oasisbr_bdtd": lambda u: b"ok",
               "sucupira": lambda u: json.dumps({"content": []}).encode(),
               "capes_abertos": lambda u: json.dumps({"result": {"results": []}}).encode()}
    agg = buscar_todas("dengue", 1, runners)
    assert len(agg) >= 5 and all("fonte" in r and "data_consulta" in r for r in agg)


def test_r980_bloqueio_scihub():
    from research.fontes_expandidas import buscar_todas
    bad = {"pubmed": lambda u: b"{}", "arxiv": lambda u: b"<feed xmlns='http://www.w3.org/2005/Atom'></feed>",
           "scielo": lambda u: (_ for _ in ()).throw(ValueError("x")),
           "lilacs": lambda u: b"ok", "oasisbr_bdtd": lambda u: b"ok",
           "sucupira": lambda u: json.dumps({"content": []}).encode(),
           "capes_abertos": lambda u: json.dumps({"result": {"results": []}}).encode()}
    # injeção direta de URL bloqueada deve levantar
    from research.fontes_expandidas import _check
    try:
        _check("https://sci-hub.se/10.1/x")
        assert False
    except PermissionError as e:
        assert "unauthorized_source" in str(e)
