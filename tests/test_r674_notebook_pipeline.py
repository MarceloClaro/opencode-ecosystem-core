"""Preflight de definições oficiais; nunca usa cookies ou executa pipeline."""

import hashlib
import json

import pytest

from integrations.gemini_notebook_pipeline import pipeline_preflight


@pytest.fixture
def official(tmp_path, monkeypatch):
    module = tmp_path / "official_pipeline.py"
    templates = {
        "builtin": {"name": "builtin", "description": "Research", "steps": [
            {"action": "source_add", "params": {"type": "url", "url": "$INPUT_URL"}},
            {"action": "notebook_query", "params": {"query": "Summarize"}},
        ]},
    }
    module.write_text("BUILTIN_PIPELINES = " + repr(templates), encoding="utf-8")
    monkeypatch.setattr("integrations.gemini_notebook_pipeline._official_module", lambda: module)
    storage = tmp_path / "storage"
    storage.mkdir()
    return module, storage


def custom(storage, name, value):
    directory = storage / "pipelines"
    directory.mkdir(exist_ok=True)
    path = directory / f"{name}.yaml"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_builtin_has_actual_steps_effect_source_and_hashes(official):
    module, storage = official
    result = pipeline_preflight("builtin", "notebook-id", "https://example.org/paper", root=storage)
    assert result["status"] == "prepared"
    assert result["effect"] == "write"
    assert result["steps"][0]["params"]["url"] == "https://example.org/paper"
    assert all(step["notebook_id"] == "notebook-id" for step in result["steps"])
    assert result["definition_source"]["kind"] == "builtin"
    assert result["definition_source"]["sha256"] == hashlib.sha256(module.read_bytes()).hexdigest()
    assert len(result["definition_sha256"]) == len(result["effective_steps_sha256"]) == 64
    assert result["process_executed"] is result["remote_operation_executed"] is False


def test_builtin_wins_over_user_file_with_same_name(official):
    _, storage = official
    custom(storage, "builtin", {"steps": [{"action": "notebook_delete"}]})
    result = pipeline_preflight("builtin", "n", "https://example.org", root=storage)
    assert result["definition_source"]["kind"] == "builtin"
    assert result["effect"] == "write"


def test_custom_definition_all_steps_are_classified(official):
    _, storage = official
    path = custom(storage, "custom", {"name": "custom", "steps": [
        {"action": "notebook_query", "params": {"query": "Q"}},
        {"action": "notebook_delete", "params": {}},
    ]})
    result = pipeline_preflight("custom", "n", root=storage)
    assert result["effect"] == "destructive"
    assert result["definition_source"]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert [step["action"] for step in result["steps"]] == ["notebook_query", "notebook_delete"]


def test_unknown_pipeline_does_not_create_directories_or_touch_auth(official):
    _, storage = official
    sentinel = storage / "cookies.json"
    sentinel.write_text("THIS_FILE_MUST_NEVER_BE_READ", encoding="utf-8")
    result = pipeline_preflight("missing", "n", root=storage)
    assert result["status"] == "blocked"
    assert result["reason"] == "pipeline_not_found"
    assert not (storage / "pipelines").exists()
    assert sentinel.read_text() == "THIS_FILE_MUST_NEVER_BE_READ"


@pytest.mark.parametrize("name", ["../auth", "/tmp/auth", "..", "", "a/b", "a\\b", "x" * 65])
def test_unsafe_names_are_rejected_before_read(official, name):
    _, storage = official
    result = pipeline_preflight(name, "n", root=storage)
    assert result["status"] == "blocked"
    assert result["reason"] == "invalid_pipeline_request"


@pytest.mark.parametrize("definition", [
    {"steps": [{"action": "shell", "params": {}}]},
    {"steps": [{"action": "notebook_query", "params": {"query": "$UNKNOWN"}}]},
    {"steps": [{"action": "notebook_query", "params": {"query": "Q", "cookies": "secret"}}]},
    {"steps": [{"action": "notebook_query", "params": {"query": "Bearer this-is-private"}}]},
    {"steps": [{"action": "studio_create", "params": {"artifact_type": "shell"}}]},
    {"steps": [{"action": "source_add", "params": {"type": "file", "text": "local-file"}}]},
    {"steps": [{"action": "notebook_delete", "params": {"notebook_id": "different"}}]},
    {"steps": []},
    {"steps": [{"action": "notebook_query", "params": "shell"}]},
    {"steps": [{"action": "notebook_query"}] * 101},
    {"steps": [{"action": "notebook_query", "params": {"query": "Q"}}], "unknown_config": True},
])
def test_invalid_or_private_definitions_block_before_execution(official, definition):
    _, storage = official
    custom(storage, "bad", definition)
    result = pipeline_preflight("bad", "n", root=storage)
    assert result["status"] == "blocked"
    assert result["process_executed"] is False


def test_unresolved_input_variable_blocks_the_builtin(official):
    _, storage = official
    result = pipeline_preflight("builtin", "n", root=storage)
    assert result["status"] == "blocked"
    assert result["reason"] == "unresolved_pipeline_variable"


def test_definition_change_produces_a_new_preview_hash(official):
    _, storage = official
    definition = {"steps": [{"action": "notebook_query", "params": {"query": "First"}}]}
    custom(storage, "custom", definition)
    first = pipeline_preflight("custom", "n", root=storage)
    definition["steps"][0]["params"]["query"] = "Second"
    custom(storage, "custom", definition)
    second = pipeline_preflight("custom", "n", root=storage)
    assert first["definition_sha256"] != second["definition_sha256"]
    assert first["effective_steps_sha256"] != second["effective_steps_sha256"]


def test_symlink_definition_is_not_followed(official):
    module, storage = official
    directory = storage / "pipelines"
    directory.mkdir()
    (directory / "custom.yaml").symlink_to(module)
    result = pipeline_preflight("custom", "n", root=storage)
    assert result["status"] == "blocked"
    assert result["reason"] == "unsafe_pipeline_definition"


def test_definition_size_is_bounded_before_loading(official):
    _, storage = official
    path = custom(storage, "large", {"steps": []})
    path.write_text("#" + "x" * 131073)
    result = pipeline_preflight("large", "n", root=storage)
    assert result["status"] == "blocked"
    assert result["reason"] == "pipeline_definition_too_large"


def test_notebook_id_placeholder_has_an_honest_execution_limit(official):
    _, storage = official
    custom(storage, "custom", {"steps": [{"action": "notebook_query", "params": {"query": "$NOTEBOOK_ID"}}]})
    result = pipeline_preflight("custom", "actual-notebook", root=storage)
    assert result["steps"][0]["params"]["query"] == "actual-notebook"
    assert result["status"] == "blocked"
    assert result["reason"] == "unsupported_upstream_variable"
    assert result["unsupported_variables"] == ["NOTEBOOK_ID"]


def test_default_storage_uses_environment_without_making_it(official, monkeypatch, tmp_path):
    _, _ = official
    storage = tmp_path / "does-not-exist"
    monkeypatch.setenv("NOTEBOOKLM_MCP_CLI_PATH", str(storage))
    result = pipeline_preflight("missing", "n")
    assert result["status"] == "blocked"
    assert not storage.exists()


def test_actual_installed_builtin_templates_are_inspected_without_import_callbacks():
    result = pipeline_preflight("multi-format", "notebook-probe")
    assert result["status"] == "prepared"
    assert result["effect"] == "write"
    assert [step["params"]["artifact_type"] for step in result["steps"]] == ["audio", "report", "flashcards"]
    assert result["process_executed"] is False


def test_upstream_module_is_parsed_instead_of_executed(official, tmp_path):
    module, storage = official
    sentinel = tmp_path / "executed"
    original = module.read_text()
    module.write_text(f"open({str(sentinel)!r}, 'w').write('unexpected')\n" + original)
    result = pipeline_preflight("builtin", "n", "https://example.org", root=storage)
    assert result["status"] == "prepared"
    assert not sentinel.exists()


def test_nonliteral_builtin_expression_is_blocked_without_execution(official, tmp_path):
    module, storage = official
    sentinel = tmp_path / "executed"
    module.write_text(f"BUILTIN_PIPELINES = __import__('pathlib').Path({str(sentinel)!r}).touch()")
    result = pipeline_preflight("builtin", "n", root=storage)
    assert result["status"] == "blocked"
    assert result["reason"] == "official_pipeline_templates_not_literal"
    assert not sentinel.exists()


def test_duplicate_yaml_keys_are_blocked_as_ambiguous(official):
    _, storage = official
    path = custom(storage, "custom", {"steps": []})
    path.write_text("steps: []\nsteps: [{action: notebook_delete}]\n")
    result = pipeline_preflight("custom", "n", root=storage)
    assert result["status"] == "blocked"
    assert result["reason"] == "ambiguous_pipeline_mapping"


def test_recursive_yaml_aliases_are_blocked(official):
    _, storage = official
    path = custom(storage, "custom", {"steps": []})
    path.write_text("steps: &recursive [*recursive]\n")
    result = pipeline_preflight("custom", "n", root=storage)
    assert result["status"] == "blocked"


def test_symlink_pipeline_directory_is_not_followed(official, tmp_path):
    _, storage = official
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "custom.yaml").write_text('{"steps":[{"action":"notebook_delete"}]}')
    (storage / "pipelines").symlink_to(outside, target_is_directory=True)
    result = pipeline_preflight("custom", "n", root=storage)
    assert result["status"] == "blocked"
    assert result["reason"] == "unsafe_pipeline_definition"


def test_finite_json_is_required_for_pipeline_configuration(official):
    _, storage = official
    path = custom(storage, "custom", {"steps": []})
    path.write_text("steps: [{action: notebook_query, params: {query: .nan}}]\n")
    result = pipeline_preflight("custom", "n", root=storage)
    assert result["status"] == "blocked"
