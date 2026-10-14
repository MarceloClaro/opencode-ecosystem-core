"""R887: controles do provedor de código, sem binário/rede nos testes herméticos."""
import importlib
import subprocess

import pytest


def provider_class():
    assert importlib.util.find_spec("integrations.code_context"), "backend R887 ausente"
    return importlib.import_module("integrations.code_context").CodeContextProvider


def test_public_provider_contract_exists():
    assert provider_class().__name__ == "CodeContextProvider"


@pytest.fixture
def local(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "app.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "test_app.py").write_text("SECRET = 'fixture'\n")
    (root / ".env").write_text("TOKEN=private\n")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture", "-c", "user.email=fixture@local", "commit", "-qm", "fixture"], check=True)
    return provider_class()(root, tmp_path / "private"), root


def test_uninstalled_status_never_claims_available(local):
    p, _ = local
    out = p.run({"operation": "status"})
    assert out["installed"] is False
    assert out["index_ready"] is False
    assert out["available"] is False


@pytest.mark.parametrize("tool", ["reindex_project", "store_symbol_memory", "get_symbol_memories", "shell", ""])
def test_mutation_and_unknown_tools_rejected_before_provider(local, tool):
    p, _ = local
    assert p.run({"operation": "query", "tool": tool, "arguments": {}})["status"] == "invalid_request"


@pytest.mark.parametrize("arguments", [{"file_path": "../app.py"}, {"file_path": "/etc/passwd"}, {"file_path": "C:\\secret.py"}, {"file_path": "app.py", "root": "/"}, {"file_path": ["app.py"]}])
def test_paths_and_unknown_arguments_fail_closed(local, arguments):
    p, _ = local
    assert p.run({"operation": "query", "tool": "get_file_skeleton", "arguments": arguments})["status"] == "invalid_request"


@pytest.mark.parametrize("arguments", [{"query": "a", "top_k": True}, {"query": "a", "top_k": 0}, {"query": "a", "top_k": 11}, {"query": "a", "min_similarity": float("nan")}, {"query": "a", "unknown": "x"}, {"query": ["x"]}])
def test_query_schema_has_typed_bounds(local, arguments):
    p, _ = local
    assert p.run({"operation": "query", "tool": "semantic_search_symbols", "arguments": arguments})["status"] == "invalid_request"


def test_missing_provider_does_not_install_or_index(local):
    p, root = local
    out = p.run({"operation": "query", "tool": "ping", "arguments": {}})
    assert out["status"] == "not_installed"
    assert not p.state_root.exists()
    assert (root / "app.py").read_text().startswith("def add")


def test_corpus_only_tracked_production_copies(local, tmp_path):
    p, root = local
    (root / "untracked.py").write_text("private=True\n")
    (root / "linked.py").symlink_to(root / "app.py")
    subprocess.run(["git", "-C", str(root), "add", "linked.py"], check=True)
    corpus = tmp_path / "corpus"
    manifest = p._export_corpus(corpus)
    assert set(manifest["files"]) == {"app.py"}
    assert (corpus / "app.py").read_bytes() == (root / "app.py").read_bytes()
    assert (corpus / "app.py").stat().st_ino != (root / "app.py").stat().st_ino
    assert not (corpus / ".env").exists()
    assert manifest["excluded"]["symlink"] == 1


def test_stale_detects_edit_and_new_production_file(local, tmp_path):
    p, root = local
    manifest = p._export_corpus(tmp_path / "corpus")
    assert p._manifest_current(manifest) is True
    (root / "app.py").write_text("def changed(): pass\n")
    assert p._manifest_current(manifest) is False


def test_added_tracked_source_invalidates_manifest(local, tmp_path):
    p, root = local
    manifest = p._export_corpus(tmp_path / "corpus")
    (root / "new.py").write_text("def new(): pass\n")
    subprocess.run(["git", "-C", str(root), "add", "new.py"], check=True)
    assert p._manifest_current(manifest) is False


def test_no_network_isolation_blocks_index(local, monkeypatch):
    p, _ = local
    monkeypatch.setattr(p, "_installation", lambda: {"installed": True, "binary_sha256": "fixture"})
    monkeypatch.setattr(p, "_network_probe", lambda: {"available": False, "reason": "fixture unavailable"})
    out = p.run({"operation": "index"})
    assert out["status"] == "isolation_unavailable"
    assert out["index_ready"] is False


def test_schema_validation_rejects_provider_tools_not_in_allowlist(local):
    p, _ = local
    with pytest.raises(ValueError, match="allowlist"):
        p._validate_tools([{"name": "shell", "inputSchema": {"type": "object"}}])


def test_timeout_is_reported_without_inference(local, monkeypatch):
    p, _ = local
    monkeypatch.setattr(p, "_query", lambda config: (_ for _ in ()).throw(TimeoutError("deadline")))
    out = p.run({"operation": "query", "tool": "ping", "arguments": {}, "timeout_seconds": 1})
    assert out["status"] == "timeout"
    assert out["ok"] is False


def test_invalid_timeout_and_operations(local):
    p, _ = local
    for cfg in [{"operation": "delete"}, {"operation": "status", "root": "/"}, {"operation": "status", "timeout_seconds": True}, {"operation": "status", "timeout_seconds": 121}]:
        assert p.run(cfg)["status"] == "invalid_request"


def test_state_symlink_refused(local, tmp_path):
    _, root = local
    target = tmp_path / "shared"
    target.mkdir()
    link = tmp_path / "alias"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        provider_class()(root, link)


def test_oversized_and_private_keys_not_exported(local, tmp_path):
    p, root = local
    (root / "oversize.py").write_bytes(b"a" * (512 * 1024 + 1))
    (root / "private.py").write_text('KEY = "-----BEGIN PRIVATE KEY-----"\n')
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    manifest = p._export_corpus(tmp_path / "corpus")
    assert set(manifest["files"]) == {"app.py"}
    assert manifest["excluded"]["oversized"] == 1
    assert manifest["excluded"]["secret_marker"] == 1


def test_credentials_named_source_and_literal_secrets_are_excluded(local, tmp_path):
    p, root = local
    (root / "credentials.py").write_text('value = "private"\n')
    (root / "client.py").write_text('API_KEY = "abcdef1234567890abcdef"\n')
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    manifest = p._export_corpus(tmp_path / "corpus")
    assert set(manifest["files"]) == {"app.py"}


def test_success_alias_is_strict(local):
    p, _ = local
    assert p.run({"operation": "status"})["success"] is True
    assert p.run({"operation": "query", "tool": "shell"})["success"] is False


@pytest.mark.parametrize("tool", ["get_symbol_usages", "get_call_tree", "get_blast_radius"])
def test_failed_graph_oracle_is_blocked_before_launch(local, tool):
    p, _ = local
    out = p.run({"operation": "query", "tool": tool, "arguments": {"symbol_name": "add"}})
    assert out["success"] is False
    assert out["status"] == "blocked_semantic_validation"
    assert out["counterexample"]["expected_caller"] == "calculate"
    assert not p.state_root.exists()


def test_index_smoke_error_never_promotes_generation(local, monkeypatch):
    p, _ = local
    monkeypatch.setattr(p, "_installation", lambda: {"installed": True, "binary_sha256": "fixture"})
    monkeypatch.setattr(p, "_network_probe", lambda: {"available": True})
    monkeypatch.setattr(p, "_command", lambda *args: ["/usr/bin/python3", "-c", "pass"])
    async def failed_ping(*args):
        return {"isError": True, "status": "response_too_large", "tools": list(importlib.import_module("integrations.code_context").TOOLS)}
    monkeypatch.setattr(p, "_mcp_call", failed_ping)
    out = p.run({"operation": "index"})
    assert out["success"] is False
    assert out["status"] == "index_smoke_failed"
    assert not (p.state_root / "current.json").exists()


def test_modified_private_corpus_is_stale_even_if_original_unchanged(local, tmp_path):
    p, _ = local
    corpus = tmp_path / "corpus"
    manifest = p._export_corpus(corpus)
    assert p._manifest_current(manifest, corpus) is True
    (corpus / "app.py").chmod(0o600)
    (corpus / "app.py").write_text("def forged(): pass\n")
    assert p._manifest_current(manifest, corpus) is False
