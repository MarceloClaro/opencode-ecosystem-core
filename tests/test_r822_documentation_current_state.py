"""Comportamento da sincronização documental da SPEC-935-R822."""
from __future__ import annotations

import importlib.util
import json
import re
import shlex
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/reconcile_operational_docs.py"
DOCS = (
    "README.md", "MANUAL.md", "ARCHITECTURE.md", "CLAUDE.md", "PROGRESS.md",
    "installer/README.md", "installer/windows/README.md",
)
HISTORY = "Registro histórico de 2026-09-26: 215 agentes, 7 MCPs, 20 checks.\n"


def _synchronizer():
    assert SCRIPT.is_file(), "Falta a sincronização que evita contagens documentais obsoletas."
    spec = importlib.util.spec_from_file_location("r822_doc_sync", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.synchronize


def _checkout(tmp_path: Path) -> Path:
    config = {
        "agent": {"primary": {}, "reviewer": {}},
        "mcp": {"zeta": {}, "alpha": {}},
        "command": {"audit": {}, "status": {}, "read": {}},
    }
    (tmp_path / "opencode.json").write_text(json.dumps(config), encoding="utf-8")
    for name in DOCS:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        body = HISTORY + "<!-- core-state:start -->\nInventário antigo.\n<!-- core-state:end -->\n"
        if name == "ARCHITECTURE.md":
            body += "<!-- core-mcp:start -->\nLista antiga.\n<!-- core-mcp:end -->\n"
        if name == "README.md":
            body += "<!-- core-runtime-diagram:start -->\nMapa antigo.\n<!-- core-runtime-diagram:end -->\n"
        body += "Evidência histórica mantida; 0,701 → 0,105; sem inferência causal.\n"
        path.write_text(body, encoding="utf-8")
    return tmp_path


def _bytes(root: Path):
    return {name: (root / name).read_bytes() for name in DOCS}


def test_check_reports_every_stale_document_without_writing(tmp_path):
    root = _checkout(tmp_path)
    original = _bytes(root)
    changes = _synchronizer()(root, check_count=4, write=False)
    assert set(changes) == set(DOCS)
    assert _bytes(root) == original


def test_sync_derives_cardinalities_and_preserves_history(tmp_path):
    root = _checkout(tmp_path)
    sync = _synchronizer()
    sync(root, check_count=4, write=True)
    for name in DOCS:
        text = (root / name).read_text(encoding="utf-8")
        assert "**2 agentes**" in text
        assert "**2 MCPs**" in text
        assert "**3 comandos**" in text
        assert "**4 checks**" in text
        assert text.startswith(HISTORY)
        assert text.endswith("Evidência histórica mantida; 0,701 → 0,105; sem inferência causal.\n")
    architecture = (root / "ARCHITECTURE.md").read_text(encoding="utf-8")
    assert architecture.index("1. `alpha`") < architecture.index("2. `zeta`")


def test_new_agent_and_server_update_inventory_and_list(tmp_path):
    root = _checkout(tmp_path)
    sync = _synchronizer()
    sync(root, check_count=4, write=True)
    path = root / "opencode.json"
    config = json.loads(path.read_text())
    config["agent"]["new-specialist"] = {}
    config["mcp"]["middle"] = {}
    path.write_text(json.dumps(config), encoding="utf-8")
    assert set(sync(root, check_count=4, write=True)) == set(DOCS)
    text = (root / "ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "**3 agentes**" in text and "**3 MCPs**" in text
    assert "1. `alpha`" in text and "2. `middle`" in text and "3. `zeta`" in text
    diagram = (root / "README.md").read_text(encoding="utf-8")
    assert "Agents2[3 agentes configurados]" in diagram
    assert "MCP2[3 MCPs configurados]" in diagram


def test_repeated_sync_and_check_leave_bytes_identical(tmp_path):
    root = _checkout(tmp_path)
    sync = _synchronizer()
    sync(root, check_count=4, write=True)
    original = _bytes(root)
    assert sync(root, check_count=4, write=True) == []
    assert sync(root, check_count=4, write=False) == []
    assert _bytes(root) == original


@pytest.mark.parametrize("damage", ["missing", "duplicate", "reversed"])
def test_bad_marker_in_last_document_prevents_all_writes(tmp_path, damage):
    root = _checkout(tmp_path)
    path = root / DOCS[-1]
    body = path.read_text()
    if damage == "missing":
        body = body.replace("<!-- core-state:end -->", "")
    elif damage == "duplicate":
        body += "<!-- core-state:start -->\n"
    else:
        body = body.replace("<!-- core-state:start -->", "TEMP").replace(
            "<!-- core-state:end -->", "<!-- core-state:start -->"
        ).replace("TEMP", "<!-- core-state:end -->")
    path.write_text(body, encoding="utf-8")
    original = _bytes(root)
    with pytest.raises(ValueError, match="[Mm]arcador"):
        _synchronizer()(root, check_count=4, write=True)
    assert _bytes(root) == original


def test_non_mapping_configuration_prevents_all_writes(tmp_path):
    root = _checkout(tmp_path)
    config = json.loads((root / "opencode.json").read_text())
    config["mcp"] = []
    (root / "opencode.json").write_text(json.dumps(config), encoding="utf-8")
    original = _bytes(root)
    with pytest.raises(ValueError, match="mcp"):
        _synchronizer()(root, check_count=4, write=True)
    assert _bytes(root) == original


@pytest.mark.parametrize("invalid_config", [[], None])
def test_non_object_configuration_prevents_all_writes(tmp_path, invalid_config):
    root = _checkout(tmp_path)
    (root / "opencode.json").write_text(json.dumps(invalid_config), encoding="utf-8")
    original = _bytes(root)
    with pytest.raises(ValueError, match="objeto JSON"):
        _synchronizer()(root, check_count=4, write=True)
    assert _bytes(root) == original


def test_profile_guide_root_readme_link_resolves_to_real_guide():
    guide = ROOT / "docs/HF_HUB_PROFILE_SETUP.md"
    target = re.search(r"\[README Principal\]\(([^)]+)\)", guide.read_text()).group(1)
    destination = (guide.parent / target).resolve()
    assert destination.is_file(), "O link de retorno do guia aponta para arquivo ausente."
    assert destination == ROOT / "README.md"


def test_nano_quick_check_executes_local_preview_with_output():
    guide = (ROOT / "docs/MANUAL_NANO_ORCHESTRATION.md").read_text()
    section = guide.split("### Verificação rápida", 1)[1].split("### Configuração do Pool", 1)[0]
    command = next(line for line in section.splitlines() if line.startswith("python3 "))
    argv = shlex.split(command)
    argv[0] = str(ROOT / ".venv/bin/python")
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), "O comando de verificação não apresenta diagnóstico nem plano."
    preview = json.loads(result.stdout)
    assert preview["total_pages"] == 12
    assert preview["total_blocks"] > 0 and preview["estimated_tokens"] > 0
    assert all(pages > 0 for _, pages in preview["sections"]), "O preview não pode alocar páginas negativas."
    assert sum(pages for _, pages in preview["sections"]) == preview["total_pages"]
