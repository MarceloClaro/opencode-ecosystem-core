"""R840: contratos funcionais no código real, carregado em módulo independente."""

from __future__ import annotations

import builtins
import importlib.util
import os
from pathlib import Path
import uuid

import pytest


BASE = Path(__file__).resolve().parent
DEFAULT_SOURCE = BASE.parent / "marceloclaro/catalog_loader.py"


def _load_product_module():
    source = DEFAULT_SOURCE
    spec = importlib.util.spec_from_file_location(
        "r840_private_" + uuid.uuid4().hex, source
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def loader():
    return _load_product_module()


def test_environment_cannot_select_external_implementation(tmp_path, monkeypatch):
    external = tmp_path / "external_candidate.py"
    external.write_text("EXTERNAL_MARKER = True\n", encoding="utf-8")
    monkeypatch.setenv("R840_LOADER_SOURCE", str(external))
    actual = _load_product_module()
    assert Path(actual.__file__).resolve() == DEFAULT_SOURCE.resolve()
    assert callable(actual.load_catalog_definitions)


def card(path, *, name="alpha", description="first", newline="\n", body=""):
    description = description if description else '""'
    text = (
        "---\nname: " + name + "\ndescription: " + description + "\n"
        "category: engineering\nskills:\n  - id: review\n    name: Review\n"
        "    tags: [review]\n    examples: [example]\n---\n" + body
    )
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def spy_parser(loader, monkeypatch):
    original = loader._parse_frontmatter_v2
    calls = []

    def parser(content):
        calls.append(content)
        return original(content)

    monkeypatch.setattr(loader, "_parse_frontmatter_v2", parser)
    return calls


def test_repeated_load_parses_equal_bytes_once(loader, tmp_path, monkeypatch):
    card(tmp_path / "alpha.md")
    calls = spy_parser(loader, monkeypatch)
    first = loader.load_catalog_definitions(str(tmp_path))
    second = loader.load_catalog_definitions(str(tmp_path))
    assert first == second
    assert len(calls) == 1


def test_same_bytes_different_paths_share_only_frontmatter(
    loader, tmp_path, monkeypatch
):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    card(a / "first.md")
    card(b / "second.md")
    calls = spy_parser(loader, monkeypatch)
    first = loader.load_catalog_definitions(str(a))[0]
    second = loader.load_catalog_definitions(str(b))[0]
    assert first["agent_id"] == "first"
    assert second["agent_id"] == "second"
    assert first["source_file"] == str(a / "first.md")
    assert second["source_file"] == str(b / "second.md")
    assert len(calls) == 1


def test_changed_content_same_mtime_size_is_reparsed_then_reused(
    loader, tmp_path, monkeypatch
):
    path = tmp_path / "alpha.md"
    card(path, description="first")
    calls = spy_parser(loader, monkeypatch)
    assert loader.load_catalog_definitions(str(tmp_path))[0]["description"] == "first"
    before = path.stat()
    card(path, description="other")
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert path.stat().st_size == before.st_size
    assert path.stat().st_mtime_ns == before.st_mtime_ns
    assert loader.load_catalog_definitions(str(tmp_path))[0]["description"] == "other"
    assert loader.load_catalog_definitions(str(tmp_path))[0]["description"] == "other"
    assert len(calls) == 2


def test_parser_identity_change_invalidates_cache(loader, tmp_path, monkeypatch):
    card(tmp_path / "alpha.md")
    old_calls = spy_parser(loader, monkeypatch)
    loader.load_catalog_definitions(str(tmp_path))
    original = loader._parse_frontmatter_v2
    calls = []

    def new_parser(content):
        calls.append(content)
        meta = original(content)
        meta["description"] = "new parser"
        return meta

    monkeypatch.setattr(loader, "_parse_frontmatter_v2", new_parser)
    assert (
        loader.load_catalog_definitions(str(tmp_path))[0]["description"] == "new parser"
    )
    assert (
        loader.load_catalog_definitions(str(tmp_path))[0]["description"] == "new parser"
    )
    assert len(old_calls) == 2
    assert len(calls) == 1


def test_nested_results_are_independent_of_prior_consumer(loader, tmp_path):
    card(tmp_path / "alpha.md")
    first = loader.load_catalog_definitions(str(tmp_path))
    second = loader.load_catalog_definitions(str(tmp_path))
    assert first == second and first is not second
    assert first[0] is not second[0]
    assert first[0]["skills"] is not second[0]["skills"]
    assert first[0]["skills"][0] is not second[0]["skills"][0]
    first[0]["skills"][0]["tags"].append("corrupted")
    first[0]["skills"][0]["examples"].clear()
    first[0]["capabilities"].clear()
    first[0]["metadata"]["a2a_version"] = "corrupted"
    first.clear()
    assert loader.load_catalog_definitions(str(tmp_path)) == second


def test_cache_stores_independent_parser_result(loader, tmp_path, monkeypatch):
    card(tmp_path / "alpha.md")
    original = loader._parse_frontmatter_v2
    captured = []

    def parser(content):
        meta = original(content)
        captured.append(meta)
        return meta

    monkeypatch.setattr(loader, "_parse_frontmatter_v2", parser)
    expected = loader.load_catalog_definitions(str(tmp_path))
    captured[0]["skills"][0]["tags"].append("corrupted")
    captured[0]["description"] = "corrupted"
    assert loader.load_catalog_definitions(str(tmp_path)) == expected
    assert len(captured) == 1


def test_files_are_read_again_on_cache_hit(loader, tmp_path, monkeypatch):
    path = tmp_path / "alpha.md"
    card(path)
    loader.load_catalog_definitions(str(tmp_path))
    original_open = builtins.open
    reads = []

    def read_spy(name, *args, **kwargs):
        if os.fspath(name) == str(path):
            reads.append((name, args, kwargs))
        return original_open(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", read_spy)
    assert len(loader.load_catalog_definitions(str(tmp_path))) == 1
    assert len(reads) == 1


def test_removed_file_is_not_returned_from_cache(loader, tmp_path):
    path = tmp_path / "alpha.md"
    card(path)
    assert len(loader.load_catalog_definitions(str(tmp_path))) == 1
    path.unlink()
    assert loader.load_catalog_definitions(str(tmp_path)) == []


def test_added_file_is_seen_in_sorted_current_listing(loader, tmp_path):
    card(tmp_path / "b.md", name="beta")
    assert [d["agent_id"] for d in loader.load_catalog_definitions(str(tmp_path))] == [
        "b"
    ]
    card(tmp_path / "a.md", name="alpha")
    assert [d["agent_id"] for d in loader.load_catalog_definitions(str(tmp_path))] == [
        "a",
        "b",
    ]


def test_unreadable_file_does_not_reuse_previous_card(loader, tmp_path, monkeypatch):
    path = tmp_path / "alpha.md"
    card(path)
    assert len(loader.load_catalog_definitions(str(tmp_path))) == 1
    original_open = builtins.open

    def unavailable(name, *args, **kwargs):
        if os.fspath(name) == str(path):
            raise PermissionError("R840 unreadable")
        return original_open(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", unavailable)
    assert loader.load_catalog_definitions(str(tmp_path)) == []


def test_invalid_utf8_is_not_hidden_by_cache(loader, tmp_path):
    path = tmp_path / "alpha.md"
    card(path)
    loader.load_catalog_definitions(str(tmp_path))
    path.write_bytes(b"\xff")
    with pytest.raises(UnicodeDecodeError):
        loader.load_catalog_definitions(str(tmp_path))


def test_missing_directory_remains_empty(loader, tmp_path):
    assert loader.load_catalog_definitions(str(tmp_path / "missing")) == []


def test_body_change_is_observed_and_raw_bytes_form_key(loader, tmp_path, monkeypatch):
    path = tmp_path / "alpha.md"
    card(path, description="", body="First body\n")
    calls = spy_parser(loader, monkeypatch)
    assert (
        loader.load_catalog_definitions(str(tmp_path))[0]["description"] == "First body"
    )
    card(path, description="", body="Other body\n")
    assert (
        loader.load_catalog_definitions(str(tmp_path))[0]["description"] == "Other body"
    )
    assert (
        loader.load_catalog_definitions(str(tmp_path))[0]["description"] == "Other body"
    )
    assert len(calls) == 2


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_original_universal_newline_semantics_are_preserved(loader, tmp_path, newline):
    card(tmp_path / "alpha.md", newline=newline)
    result = loader.load_catalog_definitions(str(tmp_path))[0]
    assert result["description"] == "first"
    assert result["skills"][0]["tags"] == ["review"]


def test_capability_taxonomy_is_rederived_on_cache_hit(loader, tmp_path, monkeypatch):
    path = tmp_path / "alpha.md"
    path.write_text("---\nname: alpha\ncategory: engineering\n---\n", encoding="utf-8")
    calls = spy_parser(loader, monkeypatch)
    assert (
        "new_capability"
        not in loader.load_catalog_definitions(str(tmp_path))[0]["capabilities"]
    )
    monkeypatch.setitem(loader.CATEGORY_CAPABILITIES, "engineering", ["new_capability"])
    assert loader.load_catalog_definitions(str(tmp_path))[0]["capabilities"] == [
        "new_capability"
    ]
    assert len(calls) == 1


def test_cache_has_bounded_lru_and_evicts_oldest(loader, tmp_path, monkeypatch):
    assert hasattr(loader, "_cached_frontmatter"), "Frontmatter cache is absent"
    cache = loader._cached_frontmatter
    assert cache.cache_info().maxsize == 512
    calls = spy_parser(loader, monkeypatch)
    path = tmp_path / "alpha.md"
    for n in range(512):
        card(path, description=f"entry-{n}")
        loader.load_catalog_definitions(str(tmp_path))
    assert cache.cache_info().currsize == 512
    card(path, description="entry-0")
    loader.load_catalog_definitions(str(tmp_path))
    assert len(calls) == 512
    card(path, description="entry-512")
    loader.load_catalog_definitions(str(tmp_path))
    assert len(calls) == 513
    card(path, description="entry-0")
    loader.load_catalog_definitions(str(tmp_path))
    assert len(calls) == 513, "A cache hit must retain the recently touched entry"
    card(path, description="entry-1")
    loader.load_catalog_definitions(str(tmp_path))
    assert len(calls) == 514
    assert cache.cache_info().currsize == 512


def test_oversized_cards_are_parsed_without_storage(loader, tmp_path, monkeypatch):
    assert hasattr(loader, "_cached_frontmatter"), "Frontmatter cache is absent"
    assert loader._FRONTMATTER_CACHE_MAX_BYTES == 128 * 1024
    path = tmp_path / "alpha.md"
    card(path, body="x" * (128 * 1024))
    calls = spy_parser(loader, monkeypatch)
    first = loader.load_catalog_definitions(str(tmp_path))
    second = loader.load_catalog_definitions(str(tmp_path))
    assert first == second and first[0]["description"] == "first"
    assert len(calls) == 2
    assert loader._cached_frontmatter.cache_info().currsize == 0


def test_parser_exception_is_not_cached(loader, tmp_path, monkeypatch):
    card(tmp_path / "alpha.md")
    calls = []

    def parser(content):
        calls.append(content)
        raise ValueError("R840 parser failure")

    monkeypatch.setattr(loader, "_parse_frontmatter_v2", parser)
    for _ in range(2):
        with pytest.raises(ValueError, match="R840 parser failure"):
            loader.load_catalog_definitions(str(tmp_path))
    assert len(calls) == 2
