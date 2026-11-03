"""R1025 — skill, MCP e plugin de guarda para Remotion (sem executar Remotion)."""

from __future__ import annotations

import ast
import asyncio
import hashlib
import json
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "integrations/remotion_guard.py"
MCP_MODULE = ROOT / "integrations/remotion_mcp.py"
SKILL = ROOT / ".opencode/skills/remotion-auditavel"
PLUGIN = ROOT / ".opencode/plugins/remotion-guard.ts"
POLICY = ROOT / ".opencode/plugins/remotion_policy.mjs"
COMMIT = "1e55bdc62fb2a9e828060b9728a767f27816f762"


def engine():
    assert MODULE.is_file(), "Módulo de guarda Remotion ausente"
    from integrations import remotion_guard

    return remotion_guard


def mcp_module():
    assert MCP_MODULE.is_file(), "Servidor MCP Remotion ausente"
    from integrations import remotion_mcp

    return remotion_mcp


def plan_document() -> dict:
    return {
        "schema_version": "1.0",
        "project": {
            "id": "demo", "title": "Demonstração", "fps": 30,
            "width": 1920, "height": 1080, "sample_rate": 48000,
        },
        "sources": [
            {
                "id": "cam", "path": "input/cam.mp4",
                "duration_frames": 900, "width": 1920, "height": 1080,
                "rights": "authorized",
            }
        ],
        "video": [
            {"id": "v1", "source": "cam", "in_frame": 0, "out_frame": 600,
             "timeline_start": 0}
        ],
        "captions": [
            {"id": "c1", "start_frame": 0, "end_frame": 90,
             "text": "Uma frase curta de teste."}
        ],
        "output": {
            "path": "out/final.mp4", "container": "mp4",
            "video_codec": "h264", "audio_codec": "aac",
            "loudness_lufs": -16,
        },
    }


def make_project(tmp_path: Path) -> Path:
    project = tmp_path / "remotion-project"
    (project / "src").mkdir(parents=True)
    (project / "node_modules" / "evil").mkdir(parents=True)
    (project / "package.json").write_text(
        json.dumps(
            {
                "name": "demo-remotion",
                "version": "1.0.0",
                "scripts": {"studio": "remotion studio", "render": "remotion render Intro out/video.mp4"},
                "dependencies": {"remotion": "4.0.539"},
                "devDependencies": {"@remotion/cli": "^4.0.539"},
            }
        ),
        encoding="utf-8",
    )
    (project / "LICENSE").write_text(
        "Remotion License\n\nFree License for individuals and small companies.\n",
        encoding="utf-8",
    )
    (project / "remotion.config.ts").write_text(
        'import { Config } from "@remotion/cli/config";\nConfig.setVideoImageFormat("jpeg");\n',
        encoding="utf-8",
    )
    (project / "src" / "Root.tsx").write_text(
        'import { Composition } from "remotion";\n'
        "export const Root = () => (\n"
        "  <>\n"
        '    <Composition id="Intro" component={Intro} durationInFrames={90} fps={30} width={1920} height={1080} />\n'
        '    <Composition id="Outro" component={Outro} durationInFrames={60} fps={30} width={1080} height={1080} />\n'
        "  </>\n"
        ");\n",
        encoding="utf-8",
    )
    (project / "node_modules" / "evil" / "Root.tsx").write_text(
        '<Composition id="Evil" durationInFrames={1} fps={30} width={10} height={10} />',
        encoding="utf-8",
    )
    return project


def snapshot(root: Path) -> dict:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return result


def test_license_free_eligibility() -> None:
    vp = engine()
    for entity, employees in (
        ("individual", None),
        ("nonprofit", 500),
        ("for_profit", 1),
        ("for_profit", 3),
    ):
        result = vp.license_scope(entity_type=entity, employees=employees)
        assert result["status"] == "eligible_free", (entity, employees, result)
        assert result["legal_advice"] is False


def test_license_company_or_blocked() -> None:
    vp = engine()
    assert vp.license_scope("for_profit", 4)["status"] == "company_license_required"
    missing = vp.license_scope("for_profit", None)
    assert missing["status"] == "blocked"
    assert "employees_required" in missing["reasons"]
    assert vp.license_scope("unknown", 1)["status"] == "blocked"
    assert "entity_unknown" in vp.license_scope("unknown", 1)["reasons"]
    resell = vp.license_scope("individual", None, resell=True)
    assert resell["status"] == "blocked"
    assert "resale_forbidden" in resell["reasons"]
    invalid = vp.license_scope("for_profit", -1)
    assert invalid["status"] == "blocked"
    assert "employees_invalid" in invalid["reasons"]


def test_license_never_gives_legal_clearance() -> None:
    vp = engine()
    for result in (
        vp.license_scope("individual"),
        vp.license_scope("for_profit", 4),
        vp.license_scope("unknown"),
    ):
        assert result["legal_advice"] is False
        assert result["warranty"] is False
        assert result["license_commit"] == COMMIT
        assert COMMIT in result["license_url"]
        assert "Remotion License" in result["license"]


def test_project_scan_detects_remotion_project(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    result = engine().scan_project(project)
    assert result["status"] == "scanned", result
    assert result["package"]["name"] == "demo-remotion"
    assert set(result["package"]["remotion_dependencies"]) == {"remotion", "@remotion/cli"}
    assert result["package"]["pinned"]["remotion"] is True
    assert result["package"]["pinned"]["@remotion/cli"] is False
    assert result["license"]["remotion_license_detected"] is True
    assert "remotion.config.ts" in result["config_files"]
    assert sorted(item["id"] for item in result["compositions"]) == ["Intro", "Outro"]
    assert result["executed"] is False
    assert result["network"] is False


def test_project_scan_rejects_symlink(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    link = tmp_path / "link"
    link.symlink_to(project, target_is_directory=True)
    with pytest.raises(engine().RemotionError) as error:
        engine().scan_project(link)
    assert error.value.code == "unsafe_path"


def test_project_scan_skips_node_modules_and_limits(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    result = engine().scan_project(project)
    assert "Evil" not in {item["id"] for item in result["compositions"]}
    assert result["limits"]["max_files"] == 2000
    assert result["limits"]["max_bytes"] == 20 * 1024 * 1024


def test_project_scan_is_read_only(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    before = snapshot(project)
    result = engine().scan_project(project)
    assert snapshot(project) == before
    assert result["executed"] is False


def test_render_preflight_accepts_valid_plan() -> None:
    result = engine().render_preflight(plan_document())
    assert result["status"] == "ready", result
    assert result["render_executed"] is False
    assert result["visual_quality_verified"] is False


def test_render_preflight_blocks_invalid_plan() -> None:
    document = plan_document()
    document["video"][0]["out_frame"] = 9999
    result = engine().render_preflight(document)
    assert result["status"] == "blocked"
    assert "plan_invalid" in {item["code"] for item in result["reasons"]}
    assert result["render_executed"] is False


def test_render_preflight_checks_composition_and_output(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    document = plan_document()
    ok = engine().render_preflight(document, composition_id="Intro", project_path=project)
    assert ok["status"] == "ready", ok
    missing = engine().render_preflight(document, composition_id="Missing", project_path=project)
    assert missing["status"] == "blocked"
    assert "composition_not_found" in {item["code"] for item in missing["reasons"]}
    wrong = engine().render_preflight(document, output_path="out/other.mp4")
    assert wrong["status"] == "blocked"
    assert "output_path_mismatch" in {item["code"] for item in wrong["reasons"]}


def test_command_policy_preview_and_unrelated() -> None:
    vp = engine()
    assert vp.command_policy("npx remotion studio --no-open")["code"] == "preview_allowed"
    assert vp.command_policy("npx remotion compositions")["code"] == "remotion_readonly"
    assert vp.command_policy("ls -la")["code"] == "unrelated"
    assert vp.command_policy("npm install left-pad")["code"] == "unrelated"
    assert vp.command_policy("")["decision"] == "block"
    assert vp.command_policy("")["code"] == "invalid_command"


def test_command_policy_render_requires_approval() -> None:
    vp = engine()
    for command in (
        "npx remotion render Intro out/video.mp4",
        "npx remotion still Intro out/frame.png",
        "npx remotion bundle",
        "npx -y remotion render Intro out/video.mp4",
    ):
        result = vp.command_policy(command)
        assert result["decision"] == "block", command
        assert result["code"] == "render_requires_approval"
    approved = vp.command_policy("npx remotion render Intro out/video.mp4", render_approved=True)
    assert approved["decision"] == "allow"
    assert approved["code"] == "render_approved"


def test_command_policy_install_requires_license_ack() -> None:
    vp = engine()
    for command in ("npm install remotion", "pnpm add @remotion/cli", "yarn add remotion"):
        result = vp.command_policy(command)
        assert result["decision"] == "block", command
        assert result["code"] == "license_ack_required"
    allowed = vp.command_policy("npm install remotion", license_ack=True)
    assert allowed["decision"] == "allow"
    assert allowed["code"] == "install_license_acknowledged"


def test_plugin_policy_matches_python() -> None:
    assert POLICY.is_file(), "Política JS do plugin ausente"
    script = ROOT / "tests/remotion_policy_test.mjs"
    assert script.is_file(), "Teste Node da política ausente"
    completed = subprocess.run(
        ["node", str(script)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    assert payload["ok"] is True and payload["cases"] >= 5


def test_plugin_blocks_render_in_source() -> None:
    assert PLUGIN.is_file(), "Plugin Remotion ausente"
    source = PLUGIN.read_text(encoding="utf-8")
    for marker in (
        "Plugin.define", "execute.before", "decideCommand",
        "REMOTION_RENDER_APPROVED", "REMOTION_LICENSE_ACK", "throw new Error",
    ):
        assert marker in source, marker


def test_skill_structure_and_discovery() -> None:
    path = SKILL / "SKILL.md"
    assert path.is_file(), "Skill Remotion ausente"
    text = path.read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1])
    assert front["name"] == "remotion-auditavel"
    assert len(front["description"]) >= 30
    for section in (
        "## Licença", "## Inspeção", "## Prévia e render",
        "## Composição e QC", "## Limites",
    ):
        assert section in text, section
    from reversa_universal.skill_dispatch import ReversaSkillDispatcher

    dispatcher = ReversaSkillDispatcher(ROOT)
    assert dispatcher.resolve_skill("remotion-auditavel") == SKILL / "SKILL.md"


def test_skill_references_resolve() -> None:
    import re

    assert SKILL.is_dir(), "Skill Remotion ausente"
    for file in SKILL.rglob("*.md"):
        for link in re.findall(r"\]\(([^\s)]+)\)", file.read_text(encoding="utf-8")):
            if link.startswith(("https://", "http://", "#")):
                continue
            target = (file.parent / link.split("#")[0]).resolve()
            assert target.is_file(), (file, link)


def test_mcp_server_exposes_tools() -> None:
    server = mcp_module().create_server()
    assert server.name == "remotion-audit"
    tools = asyncio.run(server.list_tools())
    names = {tool.name for tool in tools}
    assert names == {"license_scope", "project_scan", "render_preflight", "command_policy"}


def test_opencode_config_registers_mcp() -> None:
    from integrations.opencode_cli import build_config

    config_map = build_config()["mcp"]
    assert "remotion-audit" in config_map, "MCP remotion-audit não registrado no gerador"
    entry = config_map["remotion-audit"]
    assert entry["enabled"] is True
    assert "integrations.remotion_mcp" in entry["command"]
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    assert config["mcp"]["remotion-audit"] == entry


def test_no_remotion_code_copied_or_network() -> None:
    assert MODULE.is_file(), "Módulo de guarda Remotion ausente"
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.names[0].name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
    }
    imports |= {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert imports <= {"__future__", "json", "re", "os", "pathlib", "integrations"}
    for forbidden in ("subprocess", "requests", "urllib", "http.client"):
        assert forbidden not in source
    plugin_source = PLUGIN.read_text(encoding="utf-8")
    assert 'from "remotion"' not in plugin_source
    assert 'from "remotion"' not in POLICY.read_text(encoding="utf-8")
    assert not (SKILL / "node_modules").exists()


def test_plugin_and_skill_are_text_only() -> None:
    assert SKILL.is_dir(), "Skill Remotion ausente"
    assert PLUGIN.is_file(), "Plugin Remotion ausente"
    assert POLICY.is_file(), "Política JS do plugin ausente"
    for path in SKILL.rglob("*"):
        if path.is_file():
            assert path.suffix in {".md", ".json"}, path
    assert PLUGIN.suffix == ".ts"
    assert POLICY.suffix == ".mjs"
