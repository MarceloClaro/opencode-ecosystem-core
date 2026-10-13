"""R879: mapas provenientes de um snapshot Git, com contratos verificáveis."""
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def builder():
    source = Path(__file__).resolve().parents[1] / "scripts/build_architecture_maps.py"
    assert source.exists(), "O gerador R879 deve existir antes da entrega."
    module_spec = importlib.util.spec_from_file_location("r879_builder", source)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


@pytest.fixture
def repository(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    sources = {
        "pkg/__init__.py": "",
        "pkg/core.py": "from . import helper\nfrom pkg.helper import value\nimport json\nclass Core:\n    def run(self):\n        return value\n",
        "pkg/helper.py": "value = 1\n",
        "pkg/isolated.py": "def untouched():\n    return 3\n",
        "pkg/dynamic.py": "import importlib\nimportlib.import_module('external_optional')\n__import__(module_name)\n",
        "pkg/broken.py": "def invalid(:\n",
        "tests/test_example.py": "import pkg.core\n",
        "examples/example.py": "import pkg.core\n",
        "templates/core.py": "raise RuntimeError('template')\n",
        "docs/evidence/snapshot/pkg/core.py": "raise RuntimeError('never execute')\n",
        "artigos/private_domain.py": "import pkg.core\n",
        "outputs/receipt.json": '{"status":"historical"}',
        "ui/app.ts": "export class Panel {}\nexport function render() {}\n",
        "proof/Theorem.lean": "theorem simple : True := True.intro\n",
        "opencode.json": json.dumps({"default_agent": "marceloclaro", "model": "local/test", "agent": {"marceloclaro": {"prompt": "SECRET_PROMPT"}}, "mcp": {"core": {"environment": {"TOKEN": "SECRET_TOKEN"}}}, "command": {"rea": {"template": "SECRET_TEMPLATE"}}, "provider": {"options": {"apiKey": "SECRET_PROVIDER"}}}),
    }
    for name, content in sources.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=R879", "-c", "user.email=r879@example.invalid", "commit", "-qm", "fixture"], check=True)
    return tmp_path


def test_snapshot_is_deterministic_and_ignores_worktree(builder, repository):
    before = builder.build_snapshot(repository, "HEAD")
    (repository / "pkg/core.py").write_text("raise RuntimeError('uncommitted')")
    (repository / "untracked_secret.py").write_text("TOKEN='PRIVATE'")
    after = builder.build_snapshot(repository, "HEAD")
    assert before == after
    assert "untracked_secret.py" not in {item["path"] for item in after["files"]}
    assert len(after["git"]["commit"]) == 40
    assert all(len(item["sha256"]) == 64 for item in after["files"])


def test_absolute_relative_imports_symbols_and_isolated_modules(builder, repository):
    result = builder.build_snapshot(repository, "HEAD")
    modules = {item["module"]: item for item in result["modules"]}
    assert "pkg.isolated" in modules
    assert ("pkg.core", "pkg.helper") in {(edge["source"], edge["target"]) for edge in result["edges"]}
    core = modules["pkg.core"]
    assert [(symbol["name"], symbol["line"]) for symbol in core["symbols"]] == [("Core", 4), ("Core.run", 5)]
    assert any(item["import"] == "json" for item in result["external_imports"])
    assert any(item["path"] == "pkg/broken.py" for item in result["parse_errors"])
    assert len(result["dynamic_imports"]) == 2


def test_classification_excludes_snapshots_tests_and_domain_from_production(builder, repository):
    result = builder.build_snapshot(repository, "HEAD")
    categories = {item["path"]: item["classification"] for item in result["files"]}
    assert categories["tests/test_example.py"] == "test"
    assert categories["templates/core.py"] == "template"
    assert categories["docs/evidence/snapshot/pkg/core.py"] == "historical_snapshot"
    assert categories["artigos/private_domain.py"] == "domain_artifact"
    assert categories["outputs/receipt.json"] == "evidence_output"
    paths = {item["path"] for item in result["modules"]}
    assert not paths.intersection({"tests/test_example.py", "templates/core.py", "artigos/private_domain.py", "docs/evidence/snapshot/pkg/core.py"})


def test_configuration_allowlist_never_exports_values(builder, repository):
    result = builder.build_snapshot(repository, "HEAD")
    config = result["configurations"][0]
    assert config["agents"] == ["marceloclaro"]
    assert config["mcp_servers"] == ["core"]
    assert config["commands"] == ["rea"]
    encoded = json.dumps(result)
    for secret in ("SECRET_PROMPT", "SECRET_TOKEN", "SECRET_TEMPLATE", "SECRET_PROVIDER"):
        assert secret not in encoded
    assert config["default_agent"] == "marceloclaro"


def test_non_python_surfaces_label_the_parser_and_symbols(builder, repository):
    result = builder.build_snapshot(repository, "HEAD")
    surfaces = {item["path"]: item for item in result["surfaces"]}
    assert surfaces["ui/app.ts"]["parser"] == "lexical_declarations"
    assert {item["name"] for item in surfaces["ui/app.ts"]["symbols"]} == {"Panel", "render"}
    assert surfaces["proof/Theorem.lean"]["symbols"][0]["name"] == "simple"


def test_dot_labels_escaped_renderable_and_outputs_reproducible(builder, repository, tmp_path):
    result = builder.build_snapshot(repository, "HEAD")
    result["modules"][0]["module"] = 'danger"\\\n<svg onload="bad">'
    output = tmp_path / "maps"
    builder.write_artifacts(result, output)
    dot = output / "dependencies.dot"
    assert dot.exists()
    subprocess.run(["dot", "-Tsvg", str(dot), "-o", str(output / "verified.svg")], check=True, timeout=30)
    assert "<svg" in (output / "verified.svg").read_text()
    inventory = (output / "architecture-inventory.json").read_bytes()
    builder.write_artifacts(result, output)
    assert (output / "architecture-inventory.json").read_bytes() == inventory


def test_git_ref_rejection_is_explicit(builder, repository):
    with pytest.raises(ValueError, match="ref"):
        builder.build_snapshot(repository, "missing-ref")


def _commit(repository, name, content):
    path = repository / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(repository), "add", name], check=True)
    subprocess.run(["git", "-C", str(repository), "-c", "user.name=R879", "-c", "user.email=r879@example.invalid", "commit", "-qm", "additional fixture"], check=True)


def test_mixed_import_keeps_external_and_missing_module_explicit(builder, repository):
    _commit(repository, "pkg/mixed.py", "import pkg.helper, decimal\nimport pkg.absent\nfrom ..too_far import missing\n")
    result = builder.build_snapshot(repository)
    imports = [item for item in result["external_imports"] if item["path"] == "pkg/mixed.py"]
    assert any(item["import"] == "decimal" for item in imports)
    assert any(item["import"] == "pkg.absent" and item["reason"] == "partial_internal_prefix" for item in imports)
    assert any(item["reason"] == "relative_beyond_package" for item in imports)


def test_configuration_wrong_shapes_do_not_promote_values_to_names(builder, repository):
    _commit(repository, "opencode.json", json.dumps({"agent": "SECRET", "mcp": ["SECRET"], "command": "SECRET"}))
    config = builder.build_snapshot(repository)["configurations"][0]
    assert config["agents"] == []
    assert config["mcp_servers"] == []
    assert config["commands"] == []


def test_symlink_target_never_read_or_parsed(builder, repository):
    (repository / "outside-secret").write_text("SECRET_OUTSIDE")
    (repository / "pkg/symlink.py").symlink_to(repository / "outside-secret")
    subprocess.run(["git", "-C", str(repository), "add", "pkg/symlink.py"], check=True)
    subprocess.run(["git", "-C", str(repository), "-c", "user.name=R879", "-c", "user.email=r879@example.invalid", "commit", "-qm", "symlink"], check=True)
    snapshot = builder.build_snapshot(repository)
    assert not any(item["path"] == "pkg/symlink.py" for item in snapshot["modules"])
    assert "SECRET_OUTSIDE" not in json.dumps(snapshot)
    entry = next(item for item in snapshot["files"] if item["path"] == "pkg/symlink.py")
    assert entry["git_mode"] == "120000"


def test_cli_check_detects_tampering_without_rewriting(builder, repository, tmp_path):
    output = tmp_path / "generated"
    snapshot = builder.build_snapshot(repository)
    builder.write_artifacts(snapshot, output, render=False)
    assert builder.main(["--root", str(repository), "--output", str(output), "--check"]) == 0
    original = output / "dependencies.dot"
    original.write_text("tampered\n")
    assert builder.main(["--root", str(repository), "--output", str(output), "--check"]) == 1
    assert original.read_text() == "tampered\n"


def test_domain_generators_and_external_plugin_packages_have_explicit_categories(builder, repository):
    _commit(repository, "gerar_notebook_didatico.py", "def invalid(:\n")
    _commit(repository, ".opencode/scientific-plugins/packages/foreign/server.py", "import pkg.core\n")
    result = builder.build_snapshot(repository)
    categories = {item["path"]: item["classification"] for item in result["files"]}
    assert categories["gerar_notebook_didatico.py"] == "domain_artifact"
    assert categories[".opencode/scientific-plugins/packages/foreign/server.py"] == "vendor"
    assert not any(item["path"] == "gerar_notebook_didatico.py" for item in result["modules"])
