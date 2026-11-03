"""R1002: contratos funcionais/adversos; nenhum repositório ou modelo é executado."""
import asyncio
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess

import pytest


SOURCE = Path("outputs/pesquisa-inovacao-enfoque/quantica-repositorios.json")
DATABASE = Path("data/quantum_catalog/catalog.sqlite3")


def module():
    assert importlib.util.find_spec("research.quantum_catalog") is not None
    return importlib.import_module("research.quantum_catalog")


def loaded(source):
    cat = module().QuantumCatalog(root=source[0])
    assert cat.import_source()["status"] == "imported"
    return cat


def record(repo="Org/Cirq", **kw):
    return {"id": repo.lower().replace("/", "-"), "org_repo": repo,
            "tipo": "framework", "foco": "Simulação de ruído e VQC",
            "stacks": ["Python", "Cirq"], "secao": "Quantum simulators",
            "trl_estimado": 7, "licenca": "MIT", "status": "ativo",
            "justificativa_pesquisa": "Comparação de circuitos sob ruído.",
            "aplicacao_pesquisa": "Benchmark", **kw}


@pytest.fixture
def source(tmp_path):
    path = tmp_path / SOURCE
    path.parent.mkdir(parents=True)
    rows = [record(), record("org/cirq", trl_estimado=4, id="cirq-alias"),
            record("Fork/Cirq"), record("QuantumBFS"),
            record("Archive/Old", status="abandonado", secao="Abandoned projects"),
            record("javascript:alert(1)"), record("../secret")]
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return tmp_path, path


def test_source_identity_deduplication_and_claims(source):
    root, path = source
    before = path.read_bytes()
    cat = loaded(source)
    status = cat.execute({"operation": "status"})
    assert status["status"] == "ok"
    assert status["counts"] == {"raw_records": 7, "unique_entries": 4,
                               "repositories": 3, "organizations": 1,
                               "duplicates_collapsed": 1, "quarantined": 2,
                               "historical_entries": 1}
    assert status["source"]["sha256"] == hashlib.sha256(before).hexdigest()
    item = cat.execute({"operation": "get", "identifier": "https://github.com/ORG/Cirq/"})["results"][0]
    assert item["canonical_key"] == "org/cirq"
    assert set(item["aliases"]) == {"org-cirq", "cirq-alias"}
    assert item["verification_status"] == "unverified_catalog_claims"
    assert {c["claims"]["trl_estimado"] for c in item["records"]} == {4, 7}
    assert "trl_estimado" in item["conflicting_fields"]
    assert {c["json_pointer"] for c in item["records"]} == {"/0", "/1"}
    assert all(len(c["record_sha256"]) == 64 for c in item["records"])
    assert item["source_sha256"] == status["source"]["sha256"]
    assert status["policy"]["external_validation"] is False
    assert status["policy"]["instruction_authority"] == "none"
    assert path.read_bytes() == before


def test_explicit_import_history_and_staleness(source):
    root, path = source
    cat = loaded(source)
    first = cat.execute({"operation": "status"})
    original = path.read_bytes()
    db_before = (root / DATABASE).read_bytes()
    path.write_text(json.dumps([record("New/Source")]), encoding="utf-8")
    second = cat.execute({"operation": "status"})
    assert first["source"]["sha256"] == second["source"]["sha256"]
    assert second["source_stale"] is True
    assert (root / DATABASE).read_bytes() == db_before
    assert cat.import_source()["status"] == "imported"
    third = cat.execute({"operation": "status"})
    assert third["source_stale"] is False
    assert third["source"]["sha256"] != first["source"]["sha256"]
    assert third["counts"]["raw_records"] == 1
    assert cat.execute({"operation": "search", "query": "Cirq"})["total_matches"] == 1
    assert cat.execute({"operation": "history"})["total_matches"] == 2
    with sqlite3.connect(root / DATABASE) as conn:
        assert conn.execute("select source_bytes from imports order by id limit 1").fetchone()[0] == original
    path.unlink()
    result = cat.execute({"operation": "search", "query": "Cirq"})
    assert result["status"] == "ok" and result["source_stale"] is None
    assert result["current_source_state"] == "unavailable"


def test_import_is_idempotent_and_transactional(source, monkeypatch):
    root, path = source
    cat = loaded(source)
    before = cat.execute({"operation": "status"})
    assert cat.import_source()["status"] == "unchanged"
    assert cat.execute({"operation": "history"})["total_matches"] == 1
    path.write_text(json.dumps([record("New/Repo")]), encoding="utf-8")
    insert = cat._insert_snapshot
    def fail(conn, *args, **kwargs):
        insert(conn, *args, **kwargs)
        raise sqlite3.OperationalError("simulated interrupted import")
    monkeypatch.setattr(cat, "_insert_snapshot", fail)
    assert cat.import_source()["status"] == "unavailable"
    assert cat.execute({"operation": "status"})["source"]["sha256"] == before["source"]["sha256"]
    assert cat.execute({"operation": "history"})["total_matches"] == 1
    assert cat.execute({"operation": "search", "query": "Cirq"})["total_matches"] == 3


def test_search_filters_and_pagination(source):
    cat = loaded(source)
    query = {"operation": "search", "query": "SIMULACAO RUIDO", "limit": 1, "kind": "repository"}
    first = cat.execute(query)
    second = cat.execute({**query, "offset": 1})
    assert first["total_matches"] == 2 and first["has_more"]
    assert first["results"][0]["canonical_key"] != second["results"][0]["canonical_key"]
    assert not second["has_more"]
    assert first == cat.execute(query)
    assert "justificativa_pesquisa" in first["searched_fields"]
    assert cat.execute({**query, "stack": "JULIA"})["results"] == []
    assert cat.execute({**query, "category": "Quantum simulators"})["total_matches"] == 2
    assert cat.execute({"operation": "list", "include_historical": True})["total_matches"] == 4
    assert cat.execute({"operation": "list", "kind": "organization"})["results"][0]["canonical_key"] == "quantumbfs"
    assert cat.execute({"operation": "search", "query": "Comparação circuitos"})["total_matches"] == 3


def test_get_and_abstention(source):
    cat = loaded(source)
    assert cat.execute({"operation": "get", "identifier": "cirq-alias"})["results"][0]["canonical_key"] == "org/cirq"
    old = cat.execute({"operation": "get", "identifier": "archive/old"})
    assert old["results"][0]["historical_in_source"]
    for config in ({"operation": "search", "query": "inexistente-xyz-999"},
                   {"operation": "get", "identifier": "missing/repo"}):
        result = cat.execute(config)
        assert result["abstained"] is True and result["results"] == []
        assert result["status"] == "no_matches"


def test_fts_literals_not_query_operators(source):
    cat = loaded(source)
    assert cat.execute({"operation": "search", "query": '"CIRQ"'})["total_matches"] == 3
    assert cat.execute({"operation": "search", "query": "Cirq OR inexistente"})["results"] == []
    assert cat.execute({"operation": "search", "query": "Cir*"})["results"] == []
    assert cat.execute({"operation": "search", "query": "Cirq' ; DROP TABLE imports; --"})["results"] == []
    assert cat.execute({"operation": "history"})["total_matches"] == 1


@pytest.mark.parametrize("config", [
    {}, {"operation": "run"}, {"operation": "search", "query": " "},
    {"operation": "search", "query": ".*"}, {"operation": "search", "query": "a" * 501},
    {"operation": "search", "query": 2}, {"operation": "list", "limit": True},
    {"operation": "list", "limit": 21}, {"operation": "list", "offset": -1},
    {"operation": "list", "include_historical": "false"},
    {"operation": "list", "kind": "shell"}, {"operation": "get", "identifier": "../secrets"},
    {"operation": "status", "path": "/etc/passwd"},
    {"operation": "get", "identifier": "http://evil.example/org/repo"},
])
def test_invalid_requests(source, config):
    with pytest.raises(ValueError):
        module().QuantumCatalog(root=source[0]).execute(config)


@pytest.mark.parametrize("data", [None, b"{bad", b"{}", b"[NaN]", b'[{"id":1,"id":2}]'])
def test_invalid_sources(source, data):
    root, path = source
    cat = loaded(source)
    before = cat.execute({"operation": "status"})["source"]["sha256"]
    if data is None:
        path.unlink()
    else:
        path.write_bytes(data)
    result = cat.import_source()
    assert result["status"] == "unavailable" and result["abstained"]
    assert result["results"] == [] and result["error_code"]
    assert cat.execute({"operation": "status"})["source"]["sha256"] == before


def test_symlinks_and_size_are_rejected(source, monkeypatch):
    root, path = source
    cat = module().QuantumCatalog(root=root)
    monkeypatch.setattr(module(), "MAX_BYTES", 5)
    assert cat.import_source()["status"] == "unavailable"
    monkeypatch.undo()
    original = path.read_bytes()
    outside = root / "outside.json"
    outside.write_bytes(original)
    path.unlink()
    path.symlink_to(outside)
    assert cat.import_source()["status"] == "unavailable"
    path.unlink()
    path.parent.rmdir()
    elsewhere = root / "redirect"
    elsewhere.mkdir()
    (elsewhere / path.name).write_bytes(original)
    path.parent.symlink_to(elsewhere, target_is_directory=True)
    assert cat.import_source()["status"] == "unavailable"


def test_unsafe_records_and_queries(source, monkeypatch):
    root, path = source
    rows = [record(), "bad", record("Org/TooBig", foco="x" * 8001),
            record("Org/List", stacks="Python"), record("https://github.com/a/b/tree/main")]
    path.write_text(json.dumps(rows), encoding="utf-8")
    import socket
    monkeypatch.setattr(socket, "create_connection", lambda *a, **kw: pytest.fail("network forbidden"))
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: pytest.fail("execution forbidden"))
    cat = loaded(source)
    assert cat.execute({"operation": "status"})["counts"]["quarantined"] == 4
    assert cat.execute({"operation": "search", "query": "$(touch impossible-proof)"})["abstained"]
    assert not (root / "impossible-proof").exists()


def test_queries_are_readonly_and_never_autoimport(source):
    root, path = source
    cat = module().QuantumCatalog(root=root)
    assert cat.execute({"operation": "status"})["status"] == "unavailable"
    assert not (root / DATABASE).exists()
    assert cat.import_source()["status"] == "imported"
    before = (root / DATABASE).read_bytes()
    with cat._connect() as conn:
        with pytest.raises(sqlite3.OperationalError):
            conn.execute("delete from imports")
    assert cat.execute({"operation": "search", "query": "Cirq"})["total_matches"] == 3
    assert (root / DATABASE).read_bytes() == before


def test_unsafe_database_is_refused(source):
    root, path = source
    cat = loaded(source)
    db = root / DATABASE
    backup = db.read_bytes()
    db.write_bytes(b"not a sqlite database")
    assert cat.execute({"operation": "status"})["status"] == "unavailable"
    assert cat.import_source()["status"] == "unavailable"
    db.write_bytes(backup)
    with sqlite3.connect(db) as conn:
        conn.execute("PRAGMA user_version=999")
    assert cat.execute({"operation": "status"})["status"] == "unavailable"
    db.unlink()
    outside = root / "outside.sqlite3"
    outside.write_bytes(backup)
    db.symlink_to(outside)
    assert cat.execute({"operation": "status"})["status"] == "unavailable"
    assert cat.import_source()["status"] == "unavailable"
    assert outside.read_bytes() == backup


def primary_for(cat):
    from marceloclaro.orchestrator import MarceloClaroOrchestrator
    orch = object.__new__(MarceloClaroOrchestrator)
    orch._quantum_catalog = cat
    return orch


def test_orchestrator_and_cli(source, monkeypatch, capsys):
    cat = loaded(source)
    orch = primary_for(cat)
    expected = orch.quantum_catalog_action({"operation": "search", "query": "ruido"})
    from marceloclaro import cli
    monkeypatch.setattr(cli, "MarceloClaroOrchestrator", lambda **kw: orch)
    monkeypatch.chdir(source[0])
    monkeypatch.setattr(cli.sys, "argv", ["core", "quantum-catalog", "buscar", "ruido"])
    assert cli.main() == 0
    assert json.loads(capsys.readouterr().out) == expected
    monkeypatch.setattr(cli.sys, "argv", ["core", "quantum-catalog", "buscar", " "])
    assert cli.main() == 2
    assert json.loads(capsys.readouterr().out)["status"] == "invalid"


def test_mcp_tool_resource_and_primary_delegation(source, monkeypatch):
    cat = loaded(source)
    orch = primary_for(cat)
    from integrations import ecosystem_mcp as mcp
    monkeypatch.setattr(mcp, "get_library_orchestrator", lambda: orch)
    tools = {t.name: t for t in asyncio.run(mcp.mcp.list_tools())}
    assert "ecosystem_quantum_catalog" in tools
    assert tools["ecosystem_quantum_catalog"].annotations.readOnlyHint
    assert tools["ecosystem_quantum_catalog"].annotations.openWorldHint is False
    args = {"operation": "get", "identifier": "Org/Cirq"}
    assert asyncio.run(mcp.ecosystem_quantum_catalog(args)) == orch.quantum_catalog_action(args)
    assert json.loads(asyncio.run(mcp.ecosystem_quantum_catalog_inventory()))["counts"]["raw_records"] == 7
    resources = asyncio.run(mcp.mcp.list_resources())
    assert "ecosystem://quantum/catalog" in {str(r.uri) for r in resources}
    with pytest.raises(ValueError):
        asyncio.run(mcp.ecosystem_quantum_catalog({"operation": "panel"}))
    with pytest.raises(ValueError):
        asyncio.run(mcp.ecosystem_quantum_catalog({"operation": "import"}))


def test_common_knowledge_interface(source, monkeypatch, capsys):
    cat = loaded(source)
    orch = primary_for(cat)
    calls = []
    def book_query(query, top_k=5):
        calls.append((query, top_k))
        return {"abstained": True, "evidence": [], "reason": "not_indexed"}
    orch.library_query = book_query
    orch.library_status = lambda: {"status": "missing", "indexed": False}
    sources = orch.knowledge_sources_action({"operation": "sources"})
    assert {s["source_id"] for s in sources["sources"]} == {"quantum_catalog", "books"}
    assert sources["external_validation"] is False
    request = {"operation": "search", "source_id": "quantum_catalog", "query": "ruido", "limit": 2}
    report = orch.knowledge_sources_action(request)
    assert report["result"]["total_matches"] == 3
    assert report["source_id"] == "quantum_catalog"
    books = orch.knowledge_sources_action({**request, "source_id": "books"})
    assert books["result"]["abstained"] and calls == [("ruido", 2)]
    for bad in ({"operation": "search", "source_id": "secrets", "query": "token"},
                {"operation": "sources", "path": "/etc"},
                {"operation": "import", "source_id": "books"}):
        with pytest.raises(ValueError):
            orch.knowledge_sources_action(bad)
    from integrations import ecosystem_mcp as surface
    monkeypatch.setattr(surface, "get_library_orchestrator", lambda: orch)
    assert asyncio.run(surface.ecosystem_knowledge_query(request)) == report
    tool = next(t for t in asyncio.run(surface.mcp.list_tools()) if t.name == "ecosystem_knowledge_query")
    assert tool.annotations.readOnlyHint and tool.annotations.openWorldHint is False
    from marceloclaro import cli
    monkeypatch.setattr(cli, "MarceloClaroOrchestrator", lambda **kw: orch)
    monkeypatch.setattr(cli.sys, "argv", ["core", "conhecimento", "buscar", "ruido", "--fonte", "quantum_catalog", "--limite", "2"])
    assert cli.main() == 0
    assert json.loads(capsys.readouterr().out) == report


def test_panel_escaping_identity_and_dom(source, tmp_path):
    root, path = source
    hostile = '</script><script>alert("injected")</script>'
    path.write_text(json.dumps([record(foco=hostile), record("Other/Julia", stacks=["Julia"])]), encoding="utf-8")
    mod = module()
    cat = loaded(source)
    before = path.read_bytes()
    result = cat.export_panel()
    html_path = Path(result["path"])
    html = html_path.read_text(encoding="utf-8")
    assert hostile not in html and "&lt;/script&gt;" in html
    assert cat.execute({"operation": "status"})["source"]["sha256"] in html
    assert html.count('class="repo-card"') == 2
    assert "innerHTML" not in html and "eval(" not in html
    assert "não verificado" in html.lower()
    assert path.read_bytes() == before
    node = shutil.which("node")
    assert node, "Node é necessário para o teste DOM, não aceitar somente presença do HTML"
    js = re.search(r"<script>([\s\S]*?)</script>", html).group(1)
    harness = r'''
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const q={value:'',addEventListener(event,fn){this.callback=fn}};
const category={value:'',addEventListener(event,fn){this.callback=fn}};
const history={checked:false,addEventListener(event,fn){this.callback=fn}};
const count={textContent:''};
const cards=[{dataset:{search:'org cirq ruido',category:'Quantum simulators',historical:'false'},hidden:false},
{dataset:{search:'other julia',category:'Algorithms',historical:'true'},hidden:false}];
const nodes={'#catalog-query':q,'#catalog-category':category,'#catalog-history':history,'#catalog-count':count};
const document={querySelector(s){assert(s in nodes);return nodes[s]},querySelectorAll(s){assert.equal(s,'.repo-card');return cards}};
vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8'),{document});
assert.equal(cards[0].hidden,false); assert.equal(cards[1].hidden,true);
history.checked=true; history.callback(); assert.equal(cards[1].hidden,false);
q.value='CIRQ'; q.callback(); assert.equal(cards[0].hidden,false); assert.equal(cards[1].hidden,true);
q.value='none'; q.callback(); assert(cards.every(c=>c.hidden));
q.value=''; category.value='Algorithms'; category.callback(); assert.equal(cards[0].hidden,true); assert.equal(cards[1].hidden,false);
'''
    js_path = tmp_path / "panel-script.js"
    js_path.write_text(js, encoding="utf-8")
    harness_path = tmp_path / "dom-test.cjs"
    harness_path.write_text(harness, encoding="utf-8")
    run = subprocess.run([node, str(harness_path), str(js_path)], capture_output=True, text=True, timeout=10)
    assert run.returncode == 0, run.stderr


def test_panel_blocks_unsafe_output(source):
    root, path = source
    cat = loaded(source)
    target = path.parent / "index_quantica.html"
    other = root / "not-a-panel.txt"
    other.write_text("preserve", encoding="utf-8")
    target.symlink_to(other)
    assert cat.export_panel()["status"] == "unavailable"
    assert other.read_text() == "preserve"
