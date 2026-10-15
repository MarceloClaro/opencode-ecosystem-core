"""R893: persistência e concorrência usando apenas índices temporários."""

from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

from skills.tooling import whoosh3_engine as module


@pytest.fixture
def engine(tmp_path):
    return module.Whoosh3Engine("contract", storage_dir=str(tmp_path))


def test_document_survives_memory_cache_reset(engine):
    assert engine.index({"id": "original", "title": "Persistencia auditavel"}) is True
    module._INDEX_CACHE.clear()
    reopened = module.Whoosh3Engine(
        engine.index_name, storage_dir=str(engine.index_dir.parent)
    )
    assert [item["id"] for item in reopened.search("auditavel")] == ["original"]


def test_another_interpreter_opens_existing_documents(engine):
    assert (
        engine.index(
            {"id": "persisted", "content": "documento persistente entre processos"}
        )
        is True
    )
    script = """import json,sys
from skills.tooling.whoosh3_engine import Whoosh3Engine
engine=Whoosh3Engine('contract',storage_dir=sys.argv[1])
print(json.dumps(engine.search('persistente')))
"""
    process = subprocess.run(
        [sys.executable, "-c", script, str(engine.index_dir.parent)],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert process.returncode == 0, process.stderr
    assert [item["id"] for item in json.loads(process.stdout)] == ["persisted"]


def test_four_processes_create_and_write_without_losing_documents(tmp_path):
    script = """import json,sys
from skills.tooling.whoosh3_engine import Whoosh3Engine
sys.stdin.readline()
engine=Whoosh3Engine('parallel',storage_dir=sys.argv[1])
succeeded=engine.index({'id':sys.argv[2],'content':'concorrencia persistente'})
print(json.dumps({'success':succeeded}))
sys.exit(0 if succeeded else 2)
"""
    workers = [
        subprocess.Popen(
            [sys.executable, "-c", script, str(tmp_path), str(index)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for index in range(4)
    ]
    try:
        for worker in workers:
            worker.stdin.write("go\n")
            worker.stdin.close()
            worker.stdin = None
        results = [worker.communicate(timeout=20) for worker in workers]
        assert [worker.returncode for worker in workers] == [0] * 4, results
        module._INDEX_CACHE.clear()
        reopened = module.Whoosh3Engine("parallel", storage_dir=str(tmp_path))
        assert {hit["id"] for hit in reopened.search("concorrencia")} == {
            "0",
            "1",
            "2",
            "3",
        }
    finally:
        for worker in workers:
            if worker.poll() is None:
                worker.kill()
                worker.wait(timeout=5)


def test_initialization_cache_is_guarded_across_threads(tmp_path):
    def initialize(_index):
        return module.Whoosh3Engine("threads", storage_dir=str(tmp_path))

    with ThreadPoolExecutor(max_workers=8) as executor:
        engines = list(executor.map(initialize, range(16)))
    assert len({id(engine._ix) for engine in engines}) == 1
    assert (
        engines[0].index({"id": "threaded", "content": "threaded persistencia"}) is True
    )
    assert engines[-1].search("persistencia")[0]["id"] == "threaded"


def fail_one_commit(engine, monkeypatch):
    real_writer = engine._ix.writer
    attempts = []

    def writer(*args, **kwargs):
        instance = real_writer(*args, **kwargs)
        attempts.append(instance)
        if len(attempts) == 1:

            def fail(*args, **kwargs):
                raise OSError("commit failure injected before TOC publication")

            monkeypatch.setattr(instance, "commit", fail)
        return instance

    monkeypatch.setattr(engine._ix, "writer", writer)


@pytest.mark.parametrize("operation", ["single", "batch", "remove"])
def test_failed_commit_never_reports_success_and_releases_writer(
    engine, monkeypatch, operation
):
    if operation == "remove":
        assert (
            engine.index({"id": "original", "content": "original preservado"}) is True
        )
    previous = engine.stats()["documents"]
    fail_one_commit(engine, monkeypatch)
    if operation == "single":
        assert engine.index({"id": "failed", "content": "mustnotexist"}) is False
    elif operation == "batch":
        assert engine.index_batch([{"id": "failed", "content": "mustnotexist"}]) == 0
    else:
        assert engine.remove("original") is False
        assert engine.search("preservado")[0]["id"] == "original"
    assert engine.stats()["documents"] == previous
    assert (
        engine.index({"id": "recovered", "content": "recuperacao comprovada"}) is True
    )
    assert engine.search("comprovada")[0]["id"] == "recovered"
    assert engine.search("mustnotexist") == []


@pytest.mark.parametrize("operation", ["single", "batch"])
def test_update_failure_cancels_all_uncommitted_documents(engine, operation):
    invalid = {"id": "bad", "content": "neverindexed", "tags": [["invalid"]]}
    if operation == "single":
        assert engine.index(invalid) is False
    else:
        assert (
            engine.index_batch([{"id": "first", "content": "mustnotexist"}, invalid])
            == 0
        )
    assert engine.stats()["documents"] == 0
    assert engine.index({"id": "later", "content": "recovery"}) is True
    assert engine.search("mustnotexist") == []
    assert engine.search("recovery")[0]["id"] == "later"


def test_corrupt_existing_toc_is_not_silently_recreated(engine):
    assert engine.index({"id": "saved", "content": "conteudo preservado"}) is True
    toc = max(engine.index_dir.glob("_MAIN_*.toc"))
    toc.write_bytes(b"invalid TOC must not be overwritten")
    before = {
        path.name: path.read_bytes()
        for path in engine.index_dir.iterdir()
        if path.is_file()
    }
    module._INDEX_CACHE.clear()
    with pytest.raises(module.whoosh_index.IndexError):
        module.Whoosh3Engine(
            engine.index_name, storage_dir=str(engine.index_dir.parent)
        )
    after = {
        path.name: path.read_bytes()
        for path in engine.index_dir.iterdir()
        if path.is_file()
    }
    assert after == before


def test_existing_zero_document_index_uses_official_open_without_create(
    engine, monkeypatch
):
    module._INDEX_CACHE.clear()
    monkeypatch.setattr(
        module.whoosh_index,
        "create_in",
        lambda *args, **kwargs: pytest.fail("existing index recreated"),
    )
    reopened = module.Whoosh3Engine(
        engine.index_name, storage_dir=str(engine.index_dir.parent)
    )
    assert reopened.search("absent") == []


def test_failed_initialization_releases_process_lock_and_does_not_cache(
    tmp_path, monkeypatch
):
    original = module.whoosh_index.create_in

    def unavailable(*args, **kwargs):
        raise OSError("creation failed before index publication")

    monkeypatch.setattr(module.whoosh_index, "create_in", unavailable)
    with pytest.raises(OSError):
        module.Whoosh3Engine("recover-init", storage_dir=str(tmp_path))
    assert str((tmp_path / "recover-init").resolve()) not in module._INDEX_CACHE
    monkeypatch.setattr(module.whoosh_index, "create_in", original)
    recovered = module.Whoosh3Engine("recover-init", storage_dir=str(tmp_path))
    assert (
        recovered.index({"id": "later", "content": "recovered initialization"}) is True
    )


def test_cancel_failure_still_releases_owned_write_lock(engine, monkeypatch):
    real_writer = engine._ix.writer
    calls = []

    def writer(*args, **kwargs):
        result = real_writer(*args, **kwargs)
        calls.append(result)
        if len(calls) == 1:

            def fail(*args, **kwargs):
                raise OSError("cleanup or commit unavailable")

            monkeypatch.setattr(result, "commit", fail)
            monkeypatch.setattr(result, "cancel", fail)
        return result

    monkeypatch.setattr(engine._ix, "writer", writer)
    assert engine.index_batch([{"id": "failed", "content": "unpublished"}]) == 0
    assert engine.stats()["documents"] == 0
    assert (
        engine.index({"id": "later", "content": "recovery after failed cleanup"})
        is True
    )
    assert engine.search("unpublished") == []


def test_process_initialization_lock_has_bounded_timeout_then_recovers(
    tmp_path, monkeypatch
):
    target = tmp_path / "locked"
    target.mkdir()
    holder = module.FileLock(str(target / "CORE_INITLOCK"))
    assert holder.acquire() is True
    monkeypatch.setattr(module, "_INIT_TIMEOUT", 0.05)
    try:
        with pytest.raises(TimeoutError):
            module.Whoosh3Engine("locked", storage_dir=str(tmp_path))
    finally:
        holder.release()
    recovered = module.Whoosh3Engine("locked", storage_dir=str(tmp_path))
    assert recovered.search("absent") == []


@pytest.fixture
def legacy_engine(tmp_path):
    from whoosh.analysis import StemmingAnalyzer
    from whoosh.fields import ID, KEYWORD, TEXT, Schema

    target = tmp_path / "legacy"
    target.mkdir()
    schema = Schema(
        id=ID(unique=True, stored=True),
        title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
        content=TEXT(stored=False, analyzer=StemmingAnalyzer()),
        tags=KEYWORD(stored=True, commas=True),
        source=TEXT(stored=True),
        doctype=TEXT(stored=True),
    )
    index = module.whoosh_index.create_in(str(target), schema)
    writer = index.writer()
    writer.update_document(
        id="legacy-document",
        title="Título antigo",
        content="irrecuperavel legado",
        tags="fixture",
        source="fonte-antiga",
        doctype="fixture",
    )
    writer.commit()
    before = {
        path.name: path.read_bytes()
        for path in target.iterdir()
        if path.suffix in {".toc", ".seg"}
    }
    return module.Whoosh3Engine("legacy", storage_dir=str(tmp_path)), before


def test_new_index_returns_actual_stored_body_after_reopen(engine):
    body = "O experimento temporário encontrou ligação recuperável entre memória e contexto."
    assert (
        engine.index({"id": "body", "content": body, "source": "fixture-local"}) is True
    )
    module._INDEX_CACHE.clear()
    reopened = module.Whoosh3Engine(
        engine.index_name, storage_dir=str(engine.index_dir.parent)
    )
    hit = reopened.search("recuperável")[0]
    assert hit["content"] == body
    assert hit["content_unavailable"] is False
    assert hit["evidence_scope"] == "document_text"
    assert hit["source"] == "fixture-local"


def test_reopened_zero_session_counter_engine_reaches_real_grounding(
    engine, monkeypatch
):
    from types import SimpleNamespace

    import integrations.deepseek_harness.free_model_amplifier as consumer

    body = "Conteúdo recuperado real: persistência lexical auditável sem inferência de rede."
    assert (
        engine.index(
            {
                "id": "connected",
                "title": "Contrato local",
                "content": body,
                "source": "fixture-R893",
            }
        )
        is True
    )
    module._INDEX_CACHE.clear()
    reopened = module.Whoosh3Engine(
        engine.index_name, storage_dir=str(engine.index_dir.parent)
    )
    assert (
        reopened.stats()["documents"] == 0
    )  # contador de operações desta sessão, não tamanho persistido
    monkeypatch.setattr(
        consumer,
        "Whoosh3Engine",
        lambda *args, **kwargs: pytest.fail("engine fornecido descartado"),
    )
    amplifier = consumer.ContextAmplifier(
        whoosh_engine=reopened, data_hub=SimpleNamespace()
    )
    assert amplifier.whoosh is reopened
    evidence = amplifier.expand_context("auditável", sources=["whoosh"])
    assert len(evidence) == 1
    assert evidence[0]["content"] == body
    assert evidence[0]["evidence_scope"] == "document_text"
    assert body in amplifier.format_grounding_block(evidence)
    assert "fixture-R893" in amplifier.format_grounding_block(evidence)


def test_legacy_schema_is_preserved_and_reports_missing_body(legacy_engine):
    engine, before = legacy_engine
    hit = engine.search("irrecuperavel")[0]
    assert hit["id"] == "legacy-document"
    assert hit["content"] == ""
    assert hit["content_unavailable"] is True
    assert hit["evidence_scope"] == "metadata"
    assert engine._schema["content"].stored is False
    after = {
        path.name: path.read_bytes()
        for path in engine.index_dir.iterdir()
        if path.suffix in {".toc", ".seg"}
    }
    assert after == before


def test_legacy_metadata_cannot_be_invented_as_fulltext_grounding(
    legacy_engine, monkeypatch
):
    from types import SimpleNamespace

    import integrations.deepseek_harness.free_model_amplifier as consumer

    engine, before = legacy_engine
    monkeypatch.setattr(
        consumer,
        "Whoosh3Engine",
        lambda *args, **kwargs: pytest.fail("legacy engine descartado"),
    )
    amplifier = consumer.ContextAmplifier(
        whoosh_engine=engine, data_hub=SimpleNamespace()
    )
    evidence = amplifier.expand_context("irrecuperavel", sources=["whoosh"])
    assert evidence == []
    assert amplifier.format_grounding_block(evidence) == ""
    after = {
        path.name: path.read_bytes()
        for path in engine.index_dir.iterdir()
        if path.suffix in {".toc", ".seg"}
    }
    assert after == before


def test_empty_stored_body_is_explicit_metadata(engine):
    assert (
        engine.index({"id": "metadata-only", "title": "metadados auditiveis"}) is True
    )
    hit = engine.search("auditiveis")[0]
    assert hit["content"] == ""
    assert hit["content_unavailable"] is True
    assert hit["evidence_scope"] == "metadata"


def test_retrieved_context_limit_is_explicit_and_source_not_invented(engine):
    from types import SimpleNamespace

    from integrations.deepseek_harness.free_model_amplifier import ContextAmplifier

    body = "contextual " + "x" * 5000
    assert engine.index({"id": "bounded", "content": body, "source": ""}) is True
    amplifier = ContextAmplifier(whoosh_engine=engine, data_hub=SimpleNamespace())
    evidence = amplifier.expand_context("contextual", sources=["whoosh"])
    assert len(evidence) == 1
    assert evidence[0]["content"] == body[:4000]
    assert evidence[0]["content_truncated"] is True
    assert evidence[0]["content_characters"] == len(body)
    assert evidence[0]["source"] == "whoosh:"
    assert evidence[0]["source_document_id"] == "bounded"


def test_separate_process_reopens_and_builds_grounding_from_real_text(engine):
    body = "Artefato local persistido sustenta recuperação lexical em outro processo."
    assert (
        engine.index(
            {"id": "process-rag", "content": body, "source": "fixture-process"}
        )
        is True
    )
    script = """import json,sys
from types import SimpleNamespace
from skills.tooling.whoosh3_engine import Whoosh3Engine
from integrations.deepseek_harness.free_model_amplifier import ContextAmplifier
engine=Whoosh3Engine('contract',storage_dir=sys.argv[1])
amplifier=ContextAmplifier(whoosh_engine=engine,data_hub=SimpleNamespace())
evidence=amplifier.expand_context('persistido',sources=['whoosh'])
print(json.dumps({'evidence':evidence,'grounding':amplifier.format_grounding_block(evidence)}))
"""
    process = subprocess.run(
        [sys.executable, "-c", script, str(engine.index_dir.parent)],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert process.returncode == 0, process.stderr
    result = json.loads(process.stdout)
    assert result["evidence"][0]["content"] == body
    assert result["evidence"][0]["source_document_id"] == "process-rag"
    assert body in result["grounding"]


@pytest.mark.parametrize("operation", ["single", "batch"])
@pytest.mark.parametrize("content", [None, {"unsupported": "structured body"}])
def test_nontext_content_is_rejected_without_replacing_documents(
    engine, operation, content
):
    """Um valor não textual não pode virar corpo documental por stringificação."""
    assert engine.index({"id": "preserved", "content": "original preservado"}) is True
    previous = engine.stats()["documents"]
    invalid = {"id": "preserved", "title": "invalidbodymarker", "content": content}
    if operation == "single":
        assert engine.index(invalid) is False
    else:
        assert (
            engine.index_batch(
                [
                    {"id": "uncommitted", "content": "partialbatchmarker"},
                    invalid,
                ]
            )
            == 0
        )
    assert engine.stats()["documents"] == previous
    assert engine.search("invalidbodymarker") == []
    assert engine.search("partialbatchmarker") == []
    assert [hit["id"] for hit in engine.search("preservado")] == ["preserved"]
    assert engine.index({"id": "recovered", "content": "recoveredbodymarker"}) is True
    assert [hit["id"] for hit in engine.search("recoveredbodymarker")] == ["recovered"]
