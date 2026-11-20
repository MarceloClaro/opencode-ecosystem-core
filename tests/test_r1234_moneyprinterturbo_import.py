"""R1234: MPT 1.3.10 isolation metadata and confined local MP4 import."""
import asyncio
import hashlib
import importlib
import json
from pathlib import Path

import pytest


def api():
    return importlib.import_module("integrations.moneyprinterturbo")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def roots(tmp_path, *, media=b"mock-mp4"):
    mpt_root = tmp_path / "mpt" / "storage" / "tasks"
    task = mpt_root / "8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1"
    task.mkdir(parents=True)
    source = task / "final-1.mp4"
    source.write_bytes(media)
    editor_root = tmp_path / "editor"
    editor_root.mkdir()
    return mpt_root, editor_root, source


def probe_for(path, *, audio=True):
    return {
        "path": str(path),
        "sha256": digest(path),
        "duration_seconds": 2.0,
        "video": {"width": 1080, "height": 1920, "fps": "30/1", "frames": 60,
                  "variable_frame_rate": False},
        "audio": ({"sample_rate": 48000, "channels": 2} if audio else None),
    }


def test_manifest_pins_upstream_version_commit_and_wheel_hash():
    m = api()
    assert m.UPSTREAM["repository"] == "https://github.com/harry0703/MoneyPrinterTurbo"
    assert m.UPSTREAM["version"] == "1.3.10"
    assert m.UPSTREAM["commit"] == "8b0206be2c7977e3bc3cf25ff99a2adc3c9c65f9"
    assert m.UPSTREAM["package"] == "mpt"
    assert m.UPSTREAM["wheel_sha256"] == "5a2a9ca8b3e43502f32c8e27ae1a8c7c13ff75e6adad6be45a3e051b088f8c9f"


def test_install_plan_uses_private_environment_and_data_root(tmp_path):
    plan = api().installation_plan(tmp_path)
    assert plan["isolated"] is True
    assert Path(plan["venv"]) == tmp_path / "tools" / "mpt" / "1.3.10" / "venv"
    assert Path(plan["mpt_home"]) == tmp_path / "data" / "mpt" / "1.3.10"
    assert plan["python_requires"] == ">=3.11"
    assert plan["launch_application"] is False
    assert plan["configure_credentials"] is False
    assert plan["generation_enabled"] is False


def test_no_core_dependency_or_secret_configuration():
    m = api()
    plan = m.installation_plan()
    assert plan["core_requirements_changed"] is False
    assert plan["read_credentials"] is False
    assert plan["create_config_toml"] is False
    assert any("starlette==1.3.1" in item for item in m.UPSTREAM["dependency_conflicts"])


def test_import_copies_mp4_and_creates_single_clip_project(tmp_path, monkeypatch):
    from integrations import video_editor

    mpt_root, editor_root, source = roots(tmp_path)
    monkeypatch.setattr(video_editor, "probe_media", lambda path, **kwargs: probe_for(path))
    result = api().import_task_output(
        mpt_root, editor_root, "8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/final-1.mp4",
        "mpt-demo",
    )
    assert result["status"] == "imported"
    assert result["sha256"] == digest(source)
    asset = editor_root / result["media_path"]
    assert asset.is_file() and asset.read_bytes() == source.read_bytes()
    project_path = editor_root / "editor-projects" / "mpt-demo.json"
    project = json.loads(project_path.read_text())
    assert project["sources"][result["media_path"]]["sha256"] == result["sha256"]
    video_track = next(track for track in project["tracks"] if track["kind"] == "video")
    audio_track = next(track for track in project["tracks"] if track["kind"] == "audio")
    assert len(video_track["clips"]) == 1
    assert len(audio_track["clips"]) == 1
    assert video_track["clips"][0]["start_frame"] == 0
    assert audio_track["clips"][0]["out_frame"] == 60


def test_import_preserves_audio_and_accepts_explicit_silent_media(tmp_path, monkeypatch):
    from integrations import video_editor

    mpt_root, editor_root, _ = roots(tmp_path)
    monkeypatch.setattr(video_editor, "probe_media",
                        lambda path, **kwargs: probe_for(path, audio=False))
    rel = "8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/final-1.mp4"
    with pytest.raises(ValueError, match="silent"):
        api().import_task_output(mpt_root, editor_root, rel, "mpt-silent")
    result = api().import_task_output(
        mpt_root, editor_root, rel, "mpt-silent", allow_silent=True)
    project = json.loads((editor_root / "editor-projects" / "mpt-silent.json").read_text())
    assert result["has_audio"] is False
    assert next(t for t in project["tracks"] if t["kind"] == "audio")["clips"] == []
    assert len(next(t for t in project["tracks"] if t["kind"] == "video")["clips"]) == 1


def test_import_rejects_traversal_nested_intermediate_non_mp4_and_invalid_id(
        tmp_path, monkeypatch):
    from integrations import video_editor

    mpt_root, editor_root, _ = roots(tmp_path)
    monkeypatch.setattr(video_editor, "probe_media", lambda path, **kwargs: probe_for(path))
    cases = [
        ("../outside/final-1.mp4", "bad"),
        ("8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/../final-1.mp4", "bad"),
        ("8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/nested/final-1.mp4", "bad"),
        ("8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/clip-1.mp4", "bad"),
        ("8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/final-1.mov", "bad"),
        ("8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/final-1.mp4", "../bad"),
    ]
    for relative, project_id in cases:
        with pytest.raises(ValueError):
            api().import_task_output(mpt_root, editor_root, relative, project_id)


def test_import_rejects_symlink_source(tmp_path, monkeypatch):
    from integrations import video_editor

    mpt_root, editor_root, source = roots(tmp_path)
    link = source.parent / "final-2.mp4"
    link.symlink_to(source)
    monkeypatch.setattr(video_editor, "probe_media", lambda path, **kwargs: probe_for(path))
    with pytest.raises(ValueError, match="symlink"):
        api().import_task_output(
            mpt_root, editor_root,
            "8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/final-2.mp4", "mpt-link")


def test_import_refuses_existing_project_and_hash_collision(tmp_path, monkeypatch):
    from integrations import video_editor

    mpt_root, editor_root, source = roots(tmp_path)
    monkeypatch.setattr(video_editor, "probe_media", lambda path, **kwargs: probe_for(path))
    project_dir = editor_root / "editor-projects"
    project_dir.mkdir()
    (project_dir / "existing.json").write_text("{}")
    rel = "8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/final-1.mp4"
    with pytest.raises(ValueError, match="project"):
        api().import_task_output(mpt_root, editor_root, rel, "existing")

    asset_dir = editor_root / "editor-assets" / "moneyprinterturbo"
    asset_dir.mkdir(parents=True)
    colliding = asset_dir / f"{digest(source)}.mp4"
    colliding.write_bytes(b"different-content")
    with pytest.raises(ValueError, match="integrity"):
        api().import_task_output(mpt_root, editor_root, rel, "new-project")
    assert colliding.read_bytes() == b"different-content"


def test_probe_failure_rolls_back_new_asset_without_partial_project(tmp_path):
    mpt_root, editor_root, _ = roots(tmp_path)
    calls = 0

    def probe(path, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return probe_for(path)
        raise RuntimeError("probe failure")

    with pytest.raises(RuntimeError, match="probe failure"):
        api().import_task_output(
            mpt_root, editor_root,
            "8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/final-1.mp4",
            "mpt-probe-failure", probe_fn=probe)
    asset_dir = editor_root / "editor-assets" / "moneyprinterturbo"
    assert not list(asset_dir.glob("*.mp4"))
    assert not (editor_root / "editor-projects" / "mpt-probe-failure.json").exists()


def test_import_does_not_launch_mpt_or_render_or_publish(tmp_path, monkeypatch):
    from integrations import video_editor

    mpt_root, editor_root, _ = roots(tmp_path)
    monkeypatch.setattr(video_editor, "probe_media", lambda path, **kwargs: probe_for(path))
    monkeypatch.setattr(video_editor, "render",
                        lambda *a, **k: pytest.fail("render must not be called"))
    monkeypatch.setattr(video_editor, "subprocess", object())
    result = api().import_task_output(
        mpt_root, editor_root,
        "8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/final-1.mp4", "mpt-no-run")
    assert result["status"] == "imported"
    assert result["application_started"] is False
    assert result["generated"] is False
    assert result["rendered"] is False
    assert result["published"] is False


def test_release_import_contract_does_not_assume_scene_clips():
    plan = api().installation_plan()
    assert plan["import_contract"] == "task_final_mp4_only"
    assert plan["scene_clips_supported"] is False


def test_toolchain_registers_only_confined_asset_import():
    from integrations import video_toolchain

    report = video_toolchain.validate_registry()
    assert "moneyprinterturbo" in report["ids"]
    row = next(item for item in video_toolchain.REGISTRY
               if item["id"] == "moneyprinterturbo")
    assert row["status"] == "integrated"
    assert row["adapter"] == "integrations.moneyprinterturbo"
    assert row["roles"] == ["asset_import"]
    assert "não inicia" in row["notes"]


def test_mcp_exposes_only_local_import_not_generation(tmp_path, monkeypatch):
    from integrations import video_editor_mcp

    mpt_root, editor_root, _ = roots(tmp_path)
    server = video_editor_mcp.create_server(editor_root, mpt_output_root=mpt_root)
    tools = asyncio.run(server.list_tools())
    names = {tool.name for tool in tools}
    assert "editor_import_mpt_output" in names
    assert not any(name.startswith("mpt_") for name in names)
    imported = next(tool for tool in tools if tool.name == "editor_import_mpt_output")
    assert imported.annotations.openWorldHint is False


def test_mcp_import_creates_project_from_configured_local_root(tmp_path, monkeypatch):
    from integrations import video_editor, video_editor_mcp

    mpt_root, editor_root, source = roots(tmp_path)
    monkeypatch.setattr(video_editor, "probe_media", lambda path, **kwargs: probe_for(path))
    server = video_editor_mcp.create_server(editor_root, mpt_output_root=mpt_root)
    result = asyncio.run(server.call_tool("editor_import_mpt_output", {
        "media_path": "8f4f8a75-1c27-47ed-b2d3-45a9940e9ed1/final-1.mp4",
        "project_id": "mcp-mpt-demo",
    }))
    text = "\n".join(getattr(item, "text", "") for item in result)
    assert "imported" in text
    project = json.loads((editor_root / "editor-projects" / "mcp-mpt-demo.json").read_text())
    video = next(track for track in project["tracks"] if track["kind"] == "video")
    assert len(video["clips"]) == 1
    assert video["clips"][0]["source"] == "editor-assets/moneyprinterturbo/" + digest(source) + ".mp4"


def test_mpt_mcp_tool_is_not_exposed_without_explicit_output_root(tmp_path, monkeypatch):
    from integrations import video_editor_mcp

    _mpt_root, editor_root, _ = roots(tmp_path)
    monkeypatch.delenv("MPT_OUTPUT_ROOT", raising=False)
    monkeypatch.delenv("MPT_HOME", raising=False)
    server = video_editor_mcp.create_server(editor_root)
    tools = asyncio.run(server.list_tools())
    assert "editor_import_mpt_output" not in {tool.name for tool in tools}


def test_mpt_home_configures_only_its_tasks_directory(tmp_path, monkeypatch):
    from integrations import video_editor_mcp

    _mpt_root, editor_root, _ = roots(tmp_path)
    mpt_home = tmp_path / "configured-home"
    tasks = mpt_home / "storage" / "tasks"
    tasks.mkdir(parents=True)
    monkeypatch.delenv("MPT_OUTPUT_ROOT", raising=False)
    monkeypatch.setenv("MPT_HOME", str(mpt_home))
    server = video_editor_mcp.create_server(editor_root)
    tools = asyncio.run(server.list_tools())
    assert "editor_import_mpt_output" in {tool.name for tool in tools}
