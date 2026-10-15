"""R896: grafo AST estático; fixtures não comprovam execução dos alvos."""
from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
from pathlib import Path

import pytest


def api():
    try:
        return importlib.import_module("integrations.python_code_graph").analyze_python_graph
    except (ImportError, AttributeError):
        pytest.fail("R896 requer um adaptador Python AST real")


def corpus(**files):
    return {path: {"_data": text.encode(), "sha256": hashlib.sha256(text.encode()).hexdigest(),
                   "bytes": len(text.encode())} for path, text in files.items()}


def graph(files, tool="get_call_tree", symbol="app.py::calculate", **arguments):
    return api()(files, tool, {"symbol_name": symbol, **arguments})


def pairs(result, kind="call"):
    return {(edge["source_id"], edge["target_id"]) for edge in result["edges"] if edge["kind"] == kind}


def test_minimal_upstream_counterexample_has_the_correct_caller():
    files = corpus(**{"app.py": "def add(a, b): return a + b\ndef calculate(): return add(2, 3)\n"})
    usages = graph(files, "get_symbol_usages", "app.py::add")
    assert usages["ok"] is True
    assert [(item["caller_id"], item["start_line"]) for item in usages["usages"]] == [("app.py::calculate", 2)]
    assert pairs(graph(files)) == {("app.py::calculate", "app.py::add")}
    radius = graph(files, "get_blast_radius", "app.py::add")
    assert radius["affected_symbol_ids"] == ["app.py::calculate"]
    assert radius["affected_count"] == 1


def test_chain_diamond_and_cycle_are_bounded_and_distinguished():
    files = corpus(**{"app.py": "def a():\n b(); c()\ndef b(): d()\ndef c(): d()\ndef d(): a()\n"})
    out = graph(files, symbol="app.py::a", depth=3)
    assert pairs(out) == {("app.py::a", "app.py::b"), ("app.py::a", "app.py::c"),
                          ("app.py::b", "app.py::d"), ("app.py::c", "app.py::d"), ("app.py::d", "app.py::a")}
    assert len(out["symbols"]) == 4
    assert out["cycles"] and all(item["path"][0] == item["path"][-1] for item in out["cycles"])
    shallow = graph(files, symbol="app.py::a", depth=0)
    assert shallow["edges"] == [] and len(shallow["symbols"]) == 1
    assert shallow["depth_limited"] is True


def test_cycle_behind_diamond_join_is_detected_even_when_node_was_seen():
    files = corpus(**{"app.py": "def a():\n b(); c()\ndef b(): d()\ndef c(): d()\ndef d(): c()\n"})
    out = graph(files, symbol="app.py::a", depth=3)
    assert ("app.py::c", "app.py::d") in pairs(out) and ("app.py::d", "app.py::c") in pairs(out)
    assert any(set(item["path"]) == {"app.py::c", "app.py::d"} for item in out["cycles"])


def test_references_without_calls_are_not_invented_as_calls():
    files = corpus(**{"app.py": "def add(): return 1\ndef calculate(): return add\n"})
    usages = graph(files, "get_symbol_usages", "app.py::add")
    assert [item["kind"] for item in usages["usages"]] == ["reference"]
    assert graph(files)["edges"] == []
    assert graph(files, "get_blast_radius", "app.py::add")["affected_symbol_ids"] == ["app.py::calculate"]


def test_import_aliases_and_relative_imports_resolve_exactly():
    files = corpus(**{"pkg/__init__.py": "", "pkg/math.py": "def add(): return 1\n",
                      "pkg/api.py": "from .math import add as plus\nimport pkg.math as arithmetic\ndef calculate():\n return plus() + arithmetic.add()\n"})
    out = graph(files, symbol="pkg/api.py::calculate")
    assert pairs(out) == {("pkg/api.py::calculate", "pkg/math.py::add")}
    assert len(out["edges"]) == 2
    assert all(edge["start_line"] == 4 for edge in out["edges"])


@pytest.mark.parametrize("body,reason", [
    ("def calculate(add): return add()", "shadowed_or_rebound"),
    ("def calculate():\n add = lambda: 2\n return add()", "shadowed_or_rebound"),
    ("def calculate(): return self.add()", "dynamic_attribute"),
    ("def calculate(): return object.add()", "dynamic_attribute"),
    ("def calculate(): return getattr(object, 'add')()", "dynamic_call"),
    ("def calculate(): return eval('add()')", "dynamic_call"),
    ("def calculate(): return [add() for add in []]", "unsupported_comprehension"),
    ("def calculate(): return (lambda add: add())(None)", "unsupported_lambda"),
])
def test_dynamic_shadowed_and_unsupported_calls_are_unresolved(body, reason):
    out = graph(corpus(**{"app.py": "def add(): return 1\n" + body + "\n"}))
    assert pairs(out) == set()
    assert reason in {item["reason"] for item in out["unresolved"]}
    assert out["coverage_complete"] is False


def test_wildcard_import_is_not_guessed():
    files = corpus(**{"app.py": "from other import *\ndef calculate(): return add()\n",
                      "other.py": "def add(): return 1\n"})
    out = graph(files)
    assert out["edges"] == []
    assert "wildcard_import" in {item["reason"] for item in out["unresolved"]}


def test_wildcard_module_exports_are_not_assumed_unmodified():
    files = corpus(**{"app.py": "from other import add\ndef calculate(): return add()\n",
                      "other.py": "def add(): return 1\nfrom unknown import *\n"})
    out = graph(files)
    assert out["edges"] == []
    assert "wildcard_import" in {item["reason"] for item in out["unresolved"]}


def test_module_alias_reassignment_and_attribute_write_do_not_resolve():
    for body in ("arithmetic = None\n", "arithmetic.add = None\n"):
        files = corpus(**{"app.py": "import mathmod as arithmetic\n" + body + "def calculate(): return arithmetic.add()\n",
                          "mathmod.py": "def add(): return 1\n"})
        out = graph(files)
        assert out["edges"] == []
        assert out["unresolved"]


def test_defaults_and_decorators_belong_to_enclosing_scope():
    text = "def add(): return 1\ndef decorate(fn): return fn\n@decorate\ndef calculate(value=add()): return value\n"
    files = corpus(**{"app.py": text})
    out = graph(files)
    assert out["edges"] == []
    usages = graph(files, "get_symbol_usages", "app.py::add")
    assert [row["caller_id"] for row in usages["usages"]] == ["app.py::<module>"]
    assert [row["start_line"] for row in usages["usages"]] == [4]


def test_decorated_target_is_not_assumed_to_keep_its_callable_identity():
    files = corpus(**{"app.py": "def decoration(fn): return fn\n@decoration\ndef add(): return 1\ndef calculate(): return add()\n"})
    out = graph(files)
    assert out["edges"] == []
    assert "decorated_symbol" in {item["reason"] for item in out["unresolved"]}


def test_method_scope_does_not_capture_class_body_names():
    files = corpus(**{"app.py": "def add(): return 1\nclass Worker:\n def add(): return 2\n def calculate(): return add()\n"})
    out = graph(files, symbol="app.py::Worker.calculate")
    assert pairs(out) == {("app.py::Worker.calculate", "app.py::add")}


def test_nested_class_body_does_not_capture_outer_class_namespace():
    files = corpus(**{"app.py": "def add(): return 1\nclass Outer:\n def add(): return 2\n class Inner:\n  value = add()\n"})
    out = graph(files, symbol="app.py::Outer.Inner")
    assert pairs(out) == {("app.py::Outer.Inner", "app.py::add")}


def test_import_attribute_collision_is_not_guessed_as_submodule():
    files = corpus(**{"pkg/__init__.py": "def member(): pass\n", "pkg/member.py": "def add(): pass\n",
                      "app.py": "from pkg import member\ndef calculate(): return member.add()\n"})
    out = graph(files)
    assert out["edges"] == [] and out["unresolved"]


def test_pattern_and_exception_bindings_shadow_global_functions():
    for body in ("match {}:\n  case {**add}: pass\n return add()", "try: pass\n except Exception as add: pass\n return add()"):
        files = corpus(**{"app.py": "def add(): return 1\ndef calculate():\n " + body + "\n"})
        out = graph(files)
        assert not pairs(out)
        assert out["unresolved"]


def test_nested_lexical_names_and_recursion_resolve_without_attribute_guessing():
    files = corpus(**{"app.py": "def outer():\n def add(): return add()\n def calculate(): return add()\n return calculate()\n"})
    out = graph(files, symbol="app.py::outer.calculate", depth=3)
    assert pairs(out) == {("app.py::outer.calculate", "app.py::outer.add"), ("app.py::outer.add", "app.py::outer.add")}
    assert out["cycles"]


def test_walrus_in_comprehension_shadows_the_enclosing_function():
    files = corpus(**{"app.py": "def add(): return 1\ndef calculate():\n [(add := None) for item in []]\n return add()\n"})
    out = graph(files)
    assert pairs(out) == set()
    assert "shadowed_or_rebound" in {item["reason"] for item in out["unresolved"]}


def test_same_names_and_duplicate_definitions_are_ambiguous():
    files = corpus(**{"one.py": "def add(): pass\n", "two.py": "def add(): pass\n"})
    out = graph(files, symbol="add")
    assert out["ok"] is False and out["status"] == "ambiguous_symbol"
    assert len(out["candidates"]) == 2
    repeated = graph(corpus(**{"app.py": "def add(): pass\ndef add(): pass\n"}), symbol="app.py::add")
    assert repeated["ok"] is False and repeated["status"] == "ambiguous_symbol"


def test_syntax_errors_missing_empty_and_non_python_are_explicit():
    files = corpus(**{"app.py": "def calculate(): return 1\n", "broken.py": "def nope(:\n", "web.js": "function add() {}"})
    out = graph(files)
    assert out["ok"] is True and out["coverage_complete"] is False
    assert out["parse_errors"][0]["file_path"] == "broken.py"
    assert graph(files, symbol="broken.py::nope")["status"] == "syntax_error_target"
    assert graph(files, symbol="web.js::add")["status"] == "unsupported_language"
    assert graph(files, symbol="unknown")["status"] == "symbol_not_found"
    assert graph({})["status"] == "empty_python_corpus"
    assert graph(corpus(**{"web.js": "function add() {}"}), symbol="web.js::add")["status"] == "unsupported_language"


def test_comments_strings_and_unrelated_same_name_are_not_references():
    files = corpus(**{"app.py": "def add(): return 1\ndef calculate():\n # add()\n text = 'add()'\n return text\n"})
    assert graph(files, "get_symbol_usages", "app.py::add")["usages"] == []


def test_provenance_lines_hashes_and_source_text_are_real():
    text = "def add(): return 1\n\ndef calculate():\n    return add()\n"
    out = graph(corpus(**{"app.py": text}))
    assert out["static_only"] is True and out["backend"] == "core_python_ast"
    for symbol in out["symbols"]:
        assert symbol["source_sha256"] == hashlib.sha256(text.encode()).hexdigest()
        assert symbol["signature"] == text.splitlines()[symbol["start_line"] - 1].strip()
    edge = out["edges"][0]
    assert edge["file_path"] == "app.py" and edge["start_line"] == 4
    assert edge["source_sha256"] == hashlib.sha256(text.encode()).hexdigest()


def test_target_code_is_never_imported_or_executed(tmp_path):
    sentinel = tmp_path / "executed"
    text = f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('BAD')\ndef calculate(): return 1\n"
    assert graph(corpus(**{"app.py": text}))["ok"] is True
    assert not sentinel.exists()


@pytest.mark.parametrize("arguments", [{"depth": True}, {"depth": 4}, {"depth": -1},
                                      {"direction": "sideways"}, {"root": "/"}])
def test_invalid_query_arguments_are_rejected(arguments):
    with pytest.raises(ValueError):
        graph(corpus(**{"app.py": "def calculate(): pass\n"}), **arguments)


def test_source_paths_hashes_and_declared_sizes_are_checked():
    for path in ("../app.py", "/app.py", "C:\\app.py"):
        with pytest.raises(ValueError):
            graph(corpus(**{path: "def calculate(): pass\n"}))
    files = corpus(**{"app.py": "def calculate(): pass\n"})
    files["app.py"]["sha256"] = "a" * 64
    with pytest.raises(ValueError):
        graph(files)


def test_response_and_graph_limits_do_not_silently_claim_completeness():
    text = "def root():\n" + "".join(f"    f{i}()\n" for i in range(1100))
    text += "".join(f"def f{i}(): pass\n" for i in range(1100))
    out = graph(corpus(**{"app.py": text}), symbol="app.py::root", depth=1)
    assert out["truncated"] is True and out["coverage_complete"] is False
    assert len(out["symbols"]) <= 1000
    assert len(json.dumps(out).encode()) <= 56_000
    ids = {item["symbol_id"] for item in out["symbols"]}
    assert all(edge["source_id"] in ids and edge["target_id"] in ids for edge in out["edges"])


def test_explicit_provider_route_works_without_installation_and_preserves_native_block(tmp_path, monkeypatch):
    from integrations.code_context import CodeContextProvider
    root = tmp_path / "repo"
    root.mkdir()
    (root / "app.py").write_text("def add(): return 1\ndef calculate(): return add()\n")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "app.py"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture", "-c", "user.email=fixture@local", "commit", "-qm", "fixture"], check=True)
    provider = CodeContextProvider(root, tmp_path / "private")
    monkeypatch.setattr(provider, "_mcp_call", lambda *args: pytest.fail("Upstream não pode executar o grafo R896"))
    monkeypatch.setattr(provider, "_installation", lambda: pytest.fail("AST não depende de instalação"))
    config = {"operation": "python_graph", "tool": "get_call_tree", "arguments": {"symbol_name": "app.py::calculate"}}
    result = provider.run(config)
    assert result["success"] is True, result
    assert result["backend"] == "core_python_ast" and result["static_only"] is True
    assert result["version"] == "r896.v1" and result["source_commit"] is None
    assert result["upstream_not_used"] is True
    assert result["provenance"]["sources"][0]["path"] == "app.py"
    assert not provider.state_root.exists()
    native = provider.run({**config, "operation": "query"})
    assert native["success"] is False and native["status"] == "blocked_semantic_validation"


def test_provider_drift_is_rejected_and_sources_are_not_written(tmp_path, monkeypatch):
    from integrations.code_context import CodeContextProvider
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    provider = CodeContextProvider(root, tmp_path / "private")
    files = corpus(**{"app.py": "def calculate(): return 1\n"})
    monkeypatch.setattr(provider, "_source_files", lambda: (files, {}, 27))
    monkeypatch.setattr(provider, "_manifest_current", lambda *args: False)
    result = provider.run({"operation": "python_graph", "tool": "get_call_tree", "arguments": {"symbol_name": "app.py::calculate"}})
    assert result["success"] is False and result["status"] == "sources_changed"


def test_real_core_sample_has_a_cited_cross_file_call():
    root = Path(__file__).resolve().parents[1]
    paths = ("research/scientific_release.py", "research/provenance_pipeline.py", "research/statistical_methods.py")
    files = {path: {"_data": (root / path).read_bytes(), "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest(),
                    "bytes": (root / path).stat().st_size} for path in paths}
    out = graph(files, symbol="research/scientific_release.py::verify_scientific_package", depth=1)
    assert out["ok"] is True
    assert ("research/scientific_release.py::verify_scientific_package", "research/scientific_release.py::_replay") in pairs(out)
    assert ("research/scientific_release.py::verify_scientific_package", "research/provenance_pipeline.py::_json") in pairs(out)
    assert any(item["expression"] == "time.monotonic" and item["reason"] == "ambiguous_or_external_import"
               for item in out["unresolved"])
    assert out["unresolved_scope_count"] >= out["unresolved_sample_count"]
