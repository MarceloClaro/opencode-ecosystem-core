"""R944: MCPs educacionais locais e agentes especialistas read-only."""

import json
import sqlite3
from pathlib import Path

import pytest

from agents.lifecycle import AgentLifecycleService, _metadata


ROOT = Path(__file__).resolve().parents[1]
AIRAM_ROOT = ROOT / "PROJETO 1" / "Airam veras"


def _make_fixture(root: Path) -> None:
    caed = root / "caed-dados" / "dados" / "caed.sqlite"
    caed.parent.mkdir(parents=True)
    with sqlite3.connect(caed) as db:
        db.executescript("""
            CREATE TABLE descritores (
                matriz_id TEXT, documento_id TEXT, ano_edicao INTEGER,
                componente TEXT, etapa TEXT, ano_serie INTEGER,
                tipo_instrumento TEXT, codigo TEXT, eixo_topico_extraido TEXT,
                pagina_pdf INTEGER, fonte_arquivo TEXT, fonte_url TEXT,
                fonte_sha256 TEXT, texto_linha_extraido TEXT, descricao TEXT,
                codigo_relacionado_publicado TEXT,
                descricao_relacionada_publicada TEXT
            );
            CREATE TABLE documentos (
                documento_id TEXT, arquivo TEXT, ano_edicao INTEGER,
                sha256 TEXT, url TEXT, origem TEXT, paginas INTEGER, membro_zip TEXT
            );
            CREATE TABLE paginas (documento_id TEXT, pagina INTEGER, texto TEXT);
            CREATE TABLE estudantes_restritos (nome TEXT, resultado TEXT);
            INSERT INTO descritores VALUES
              ('AvalieCE_2026_2_LP_2EF','doc-a',2026,'Língua Portuguesa','EF',2,
               'formativa','H01','Leitura',1,'matriz.pdf','https://official.example/matriz.pdf',
               'abc123','H01 localizar informação','Localizar informação explícita.',NULL,NULL),
              ('AvalieCE_2026_2_LP_2EF','doc-a',2026,'Língua Portuguesa','EF',2,
               'formativa','H02','Leitura',1,'matriz.pdf','https://official.example/matriz.pdf',
               'abc123','H02 inferir informação','Inferir informação no texto.',NULL,NULL);
            INSERT INTO documentos VALUES
              ('doc-a','matriz.pdf',2026,'abc123','https://official.example/matriz.pdf','fixture',1,NULL);
            INSERT INTO estudantes_restritos VALUES ('SINTÉTICO','não deve ser lido');
        """)

    spaece = root / "spaece-dados" / "dados" / "spaece.sqlite"
    spaece.parent.mkdir(parents=True)
    with sqlite3.connect(spaece) as db:
        db.executescript("""
            CREATE TABLE descritores (
                matriz_id TEXT, sistema TEXT, componente TEXT, etapa TEXT,
                ano_serie INTEGER, codigo TEXT, eixo_topico_extraido TEXT,
                subeixo TEXT, fonte_url TEXT, fonte_arquivo TEXT, pagina_pdf INTEGER,
                fonte_sha256 TEXT, vigencia_2026 TEXT, descricao_extraida TEXT,
                descricao TEXT
            );
            INSERT INTO descritores VALUES
              ('SPAECE_LP_EF_5','SPAECE','Língua Portuguesa','Ensino Fundamental',5,
               'D13','Leitura',NULL,'https://official.example/spaece.pdf','spaece.pdf',1,
               'def456','não confirmada','Localizar informação','Localizar informação explícita.');
        """)


def test_matrix_mcp_reads_only_allowlisted_databases(tmp_path):
    from integrations.caed_spaece_mcp import MatrixCorpus, MATRIX_DATABASES

    _make_fixture(tmp_path)
    corpus = MatrixCorpus(tmp_path)
    assert MATRIX_DATABASES == {
        "CAEd": Path("caed-dados/dados/caed.sqlite"),
        "SPAECE": Path("spaece-dados/dados/spaece.sqlite"),
    }
    status = corpus.source_status()
    assert status["status"] == "available"
    assert set(status["systems"]) == {"CAEd", "SPAECE"}

    result = corpus.search_descriptors("SINTÉTICO")
    assert result["matches"] == []
    assert "estudantes_restritos" not in json.dumps(result, ensure_ascii=False)


def test_matrix_mcp_lists_and_searches_with_bounded_parameterized_queries(tmp_path):
    from integrations.caed_spaece_mcp import MatrixCorpus

    _make_fixture(tmp_path)
    corpus = MatrixCorpus(tmp_path)
    matrices = corpus.list_matrices(system="CAEd", edition_year=2026)
    assert matrices["status"] == "ok"
    assert len(matrices["matrices"]) == 1
    assert matrices["matrices"][0]["descritor_count"] == 2

    results = corpus.search_descriptors("INFORMAÇÃO", system="CAEd", limit=10)
    assert len(results["matches"]) == 2
    assert all(item["fonte_sha256"] == "abc123" for item in results["matches"])

    legacy = corpus.get_matrix("SPAECE_LP_EF_5", system="SPAECE")
    assert legacy["matrix"]["edition_year"] is None
    assert legacy["matrix"]["year_serie"] == 5

    with pytest.raises(ValueError):
        corpus.search_descriptors("x", limit=1000)
    assert corpus.get_matrix("../outside", system="CAEd")["status"] == "not_found"


def test_workspace_airam_matrix_corpus_smoke_when_present():
    from integrations.caed_spaece_mcp import MatrixCorpus

    corpus = MatrixCorpus()
    status = corpus.source_status()
    if status["status"] != "available":
        pytest.skip("O corpus Airam Veras é local e não está presente neste checkout")
    caed = corpus.list_matrices(system="CAEd", limit=100)
    spaece = corpus.list_matrices(system="SPAECE", limit=100)
    assert caed["matrices"]
    assert spaece["matrices"]
    assert status["restricted_results_accessed"] is False
    assert status["scripts_executed"] is False
    forbidden_fields = {"nome", "student_id", "matricula", "cpf", "student_name"}
    assert not forbidden_fields.intersection(
        key for matrix in (*caed["matrices"], *spaece["matrices"]) for key in matrix
    )


def test_law_catalog_is_explicit_non_exhaustive_and_temporally_cautious():
    from integrations.educacao_legislacao_mcp import LawSourceRegistry

    registry = LawSourceRegistry()
    result = registry.list_sources()
    sources = {item["law_id"]: item for item in result["sources"]}
    assert result["scope_complete"] is False
    assert {"eca", "ldb", "lbi", "pne_2014", "pee_ce_2016"}.issubset(sources)
    assert sources["pne_2014"]["current_validity"] == "not_verified"
    assert sources["pee_ce_2016"]["declared_period"] == "2016–2024"
    assert sources["pee_ce_2016"]["current_validity"] == "not_verified"


def test_law_fetch_uses_only_fixed_official_sources_and_does_not_write(tmp_path):
    from integrations.educacao_legislacao_mcp import LawSourceRegistry

    registry = LawSourceRegistry()
    body = b"<html><body><h1>Lei de teste</h1><p>Art. 1o educacao.</p></body></html>"
    calls = []

    def fake_fetch(url, *, max_bytes, timeout_seconds):
        calls.append(url)
        return {"status_code": 200, "final_url": url, "body": body}

    before = list(tmp_path.iterdir())
    result = registry.fetch_source("eca", fetcher=fake_fetch)
    assert result["status"] == "retrieved"
    assert "Lei de teste" in result["text"]
    assert result["content_sha256"]
    assert result["current_validity"] == "not_determined_by_fetch"
    assert len(calls) == 1
    assert list(tmp_path.iterdir()) == before

    calls.clear()
    with pytest.raises(ValueError):
        registry.fetch_source("https://attacker.invalid/law", fetcher=fake_fetch)
    assert calls == []

    def redirected_fetch(url, *, max_bytes, timeout_seconds):
        return {"status_code": 200, "final_url": "https://attacker.invalid/x", "body": body}

    with pytest.raises(ValueError):
        registry.fetch_source("eca", fetcher=redirected_fetch)


def test_specialist_profiles_are_managed_read_only_and_bound_to_mcp_contracts():
    expectations = {
        "caed-spaece-matrix-specialist": (
            "caed-spaece-data",
            "PROJETO 1/Airam veras/caed-dados",
            "resultados-caed-ciclo-i-2026",
        ),
        "educacao-legislacao-ceara-specialist": (
            "educacao-legislacao",
            "vigência não verificada",
            "não substitui orientação jurídica",
        ),
    }
    for agent_id, phrases in expectations.items():
        report = AgentLifecycleService(ROOT).validate(agent_id)
        profile = report["profile"]
        _, prompt = _metadata((ROOT / report["source_file"]).read_bytes())
        lowered = prompt.casefold()
        assert report["definition_validated"] is True
        assert report["mode"] == "managed-v1"
        assert report["executed"] is False
        assert profile["allow_edit"] is False
        assert profile["permission"]["webfetch"] == "deny"
        assert profile["permission"]["task"] == "deny"
        assert profile["permission"]["bash"]["*"] == "deny"
        assert all(phrase.casefold() in lowered for phrase in phrases)


def test_existing_integrated_agent_uses_local_corpus_and_excludes_restricted_data():
    report = AgentLifecycleService(ROOT).validate("caed-spaece-educacao-ceara")
    _, prompt = _metadata((ROOT / report["source_file"]).read_bytes())
    lowered = prompt.casefold()
    for phrase in (
        "projeto 1/airam veras/caed-dados",
        "caed-dados/dados/descritores.csv",
        "spaece-dados/dados/spaece.sqlite",
        "resultados-caed-ciclo-i-2026",
        "restrito",
        "p2p.kiwi",
    ):
        assert phrase in lowered


def test_generated_config_registers_mcp_servers_and_specialists():
    from integrations.opencode_cli import build_config

    generated = build_config()
    assert generated["mcp"]["caed-spaece-data"]["type"] == "local"
    assert generated["mcp"]["educacao-legislacao"]["type"] == "local"
    assert generated["agent"]["caed-spaece-matrix-specialist"]["mode"] == "subagent"
    assert generated["agent"]["educacao-legislacao-ceara-specialist"]["mode"] == "subagent"

    actual = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    assert "caed-spaece-data" in actual["mcp"]
    assert "educacao-legislacao" in actual["mcp"]
    assert "biblioteca" in actual["command"]


def test_mcp_servers_expose_only_the_declared_read_only_tools():
    import asyncio
    from integrations.caed_spaece_mcp import MatrixCorpus, create_server as create_matrix_server
    from integrations.educacao_legislacao_mcp import LawSourceRegistry, create_server as create_law_server

    matrix_tools = asyncio.run(create_matrix_server(MatrixCorpus(AIRAM_ROOT)).list_tools())
    law_tools = asyncio.run(create_law_server(LawSourceRegistry()).list_tools())
    assert {tool.name for tool in matrix_tools} == {
        "source_status", "list_matrices", "get_matrix", "search_descriptors",
        "export_matrix_bundle",
    }
    assert {tool.name for tool in law_tools} == {"list_sources", "fetch_source"}
    assert all(tool.annotations.readOnlyHint is True for tool in (*matrix_tools, *law_tools))
    assert all(tool.annotations.destructiveHint is False for tool in (*matrix_tools, *law_tools))
