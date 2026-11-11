"""R1150 — auditoria de duplicidade de agentes e MCPs."""
from __future__ import annotations

import json

from integrations import catalog_audit


def _write(path, front):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + front.strip() + "\n---\n", encoding="utf-8")


def _fixture(tmp_path):
    catalog = tmp_path / "agents" / "catalog"
    _write(catalog / "alpha.md", """
agent_id: alpha
name: Alpha
description: "planeja e simula mitigação de erro quântico com zne pec dd"
""")
    _write(catalog / "beta.md", """
agent_id: alpha
name: Beta
description: "planeja e simula mitigação de erro quântico com zne pec dd"
""")
    _write(catalog / "gamma.md", """
agent_id: gamma
name: Gamma
description: "audita licença e proveniência de repositórios com evidência"
""")
    _write(catalog / "delta.md", """
agent_id: delta
name: Delta
description: "planeja e simula mitigação de erro quântico com zne pec dd"
""")
    config = {
        "agent": {
            "alpha": {"prompt": "{file:./agents/catalog/alpha.md}"},
            "beta": {"prompt": "{file:./agents/catalog/alpha.md}"},
            "gamma": {"prompt": "{file:./agents/catalog/gamma.md}"},
        },
        "mcp": {
            "m1": {"type": "local", "command": ["python", "-m", "x"]},
            "m2": {"type": "local", "command": ["python", "-m", "x"]},
            "m3": {"type": "remote", "url": "https://example.org/mcp"},
            "m4": {"type": "remote", "url": "https://example.org/mcp"},
        },
    }
    path = tmp_path / "opencode.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return catalog, path


def test_detects_duplicate_ids_prompts_and_mcp(tmp_path):
    catalog, config = _fixture(tmp_path)
    report = catalog_audit.audit_catalog(
        catalog_dir=catalog, config_path=config, near_duplicate_threshold=0.9
    )
    assert report["counts"]["catalog_files"] == 4
    assert report["duplicates"]["catalog_ids"] == []
    declared = report["duplicates"]["declared_agent_ids"]
    assert len(declared) == 1
    assert declared[0]["declared_agent_id"] == "alpha"
    mismatches = report["duplicates"]["metadata_id_mismatches"]
    assert len(mismatches) == 1
    assert mismatches[0]["file"] == "beta.md"
    assert len(report["duplicates"]["config_prompts"]) == 1
    assert len(report["duplicates"]["mcp_signatures"]) == 2
    assert report["auto_removed"] is False
    assert len(report["report_sha256"]) == 64


def test_detects_near_duplicates_and_drift(tmp_path):
    catalog, config = _fixture(tmp_path)
    report = catalog_audit.audit_catalog(
        catalog_dir=catalog, config_path=config, near_duplicate_threshold=0.9
    )
    pairs = {
        tuple(sorted((item["left"], item["right"])))
        for item in report["near_duplicate_agents"]
    }
    assert ("alpha", "beta") in pairs
    assert "delta" in report["drift"]["catalog_not_in_config"]
    assert report["drift"]["config_not_in_catalog"] == []


def test_cli_writes_report(tmp_path):
    catalog, config = _fixture(tmp_path)
    output = tmp_path / "report.json"
    code = catalog_audit.main([
        "--catalog", str(catalog),
        "--config", str(config),
        "--output", str(output),
    ])
    assert code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["counts"]["config_mcps"] == 4


def test_real_catalog_has_auditable_shape():
    report = catalog_audit.audit_catalog(
        near_duplicate_threshold=0.95, max_near_duplicates=5
    )
    assert report["counts"]["catalog_files"] > 0
    assert report["counts"]["config_agents"] > 0
    assert report["counts"]["config_mcps"] > 0
    assert "duplicates" in report
