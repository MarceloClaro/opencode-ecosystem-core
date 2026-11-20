"""R1230: análise de cena e cortes propostos sem render automático."""
from __future__ import annotations

import asyncio
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs/SPEC-935-R1230-video-analysis-adapters.md"


def api():
    return importlib.import_module("integrations.video_analysis")


def media_file(tmp_path: Path) -> Path:
    target = tmp_path / "source.mp4"
    target.write_bytes(b"synthetic-media-for-unit-tests")
    return target


def media_probe(path: Path, *, fps="30/1", frames=120, vfr=False) -> dict:
    return {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "video": {
            "fps": fps,
            "frames": frames,
            "variable_frame_rate": vfr,
            "width": 160,
            "height": 120,
        },
        "audio": None,
    }


def auto_v1(path: Path, *, fps="30/1", chunks=None) -> dict:
    return {
        "version": "1",
        "source": str(path.resolve()),
        "timebase": fps,
        "chunks": chunks or [[0, 60, 1], [60, 75, 0], [75, 120, 1]],
    }


def test_spec_declares_review_only_and_no_whisperx_install():
    text = SPEC.read_text(encoding="utf-8")
    assert "approval_state=\"pending\"" in text
    assert "não instala nem integra WhisperX" in text
    assert "sem baixar pesos" in text


def test_diagnose_tools_reports_ffmpeg_ffprobe_versions_separately():
    m = api()
    calls = []

    def which(name):
        return f"/opt/tools/{name}"

    def runner(argv, **kwargs):
        calls.append((argv, kwargs))
        tool = Path(argv[0]).name
        output = "31.9.0\n" if tool == "auto-editor" else f"{tool} version 8.0-test\n"
        return SimpleNamespace(returncode=0, stdout=output, stderr="")

    result = m.diagnose_tools(which_fn=which, runner=runner)
    assert result["status"] == "ready"
    assert result["tools"]["ffmpeg"]["version"] == "8.0-test"
    assert result["tools"]["ffprobe"]["version"] == "8.0-test"
    assert result["tools"]["auto-editor"]["status"] == "ready"
    assert result["tools"]["auto-editor"]["version"] == "31.9.0"
    assert all(call[1].get("shell") is False for call in calls)
    assert all(isinstance(call[0], list) for call in calls)


def test_diagnose_tools_does_not_hide_missing_or_failed_binary():
    m = api()
    calls = []

    def which(name):
        return None if name == "ffprobe" else f"/opt/tools/{name}"

    def runner(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=1, stdout="", stderr="bad binary")

    result = m.diagnose_tools(which_fn=which, runner=runner)
    assert result["status"] == "blocked"
    assert result["tools"]["ffmpeg"]["status"] == "failed"
    assert result["tools"]["ffprobe"]["status"] == "missing"
    assert result["tools"]["auto-editor"]["status"] == "failed"
    assert len(calls) == 2


def test_scene_markers_are_frame_aligned_hashed_and_review_only(tmp_path):
    m = api()
    source = media_file(tmp_path)
    invoked = []

    def detect(path, *, threshold, min_scene_len):
        invoked.append((path, threshold, min_scene_len))
        return [(0, 30), (30, 120)]

    result = m.detect_scene_markers(
        source,
        threshold=24.0,
        min_scene_len=5,
        probe_fn=lambda path, **kwargs: media_probe(Path(path)),
        scene_detect_fn=detect,
    )
    assert result["kind"] == "scene_markers"
    assert result["source"]["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert result["source"]["fps"] == "30/1"
    assert result["markers"] == [
        {"index": 0, "start_frame": 0, "end_frame": 30},
        {"index": 1, "start_frame": 30, "end_frame": 120},
    ]
    assert result["review_required"] is True
    assert result["source_modified"] is False
    assert invoked == [(str(source.resolve()), 24.0, 5)]


def test_scene_markers_reject_symlink_vfr_and_bad_detector_output(tmp_path):
    m = api()
    source = media_file(tmp_path)
    alias = tmp_path / "alias.mp4"
    alias.symlink_to(source)
    with pytest.raises(ValueError, match="symlink"):
        m.detect_scene_markers(alias, scene_detect_fn=lambda *a, **k: [])

    calls = []
    with pytest.raises(ValueError, match="VFR"):
        m.detect_scene_markers(
            source,
            probe_fn=lambda path, **kwargs: media_probe(Path(path), vfr=True),
            scene_detect_fn=lambda *a, **k: calls.append(True) or [],
        )
    assert calls == []

    with pytest.raises(ValueError, match="scene"):
        m.detect_scene_markers(
            source,
            probe_fn=lambda path, **kwargs: media_probe(Path(path)),
            scene_detect_fn=lambda *a, **k: [(0, 130)],
        )


def test_auto_editor_v1_becomes_pending_cut_proposal_without_frame_drift(tmp_path):
    m = api()
    source = media_file(tmp_path)
    probe = media_probe(source)
    result = m.parse_auto_editor_v1(auto_v1(source), source_path=source, probe=probe)
    assert result["kind"] == "rough_cut_proposal"
    assert result["approval_state"] == "pending"
    assert result["review_required"] is True
    assert result["rendered"] is False
    assert [(x["in_frame"], x["out_frame"], x["action"]) for x in result["segments"]] == [
        (0, 60, "keep"), (60, 75, "cut"), (75, 120, "keep")]
    assert result["segments"][2]["timeline_start_frame"] == 60
    assert result["summary"]["kept_frames"] == 105
    assert result["summary"]["proposed_cut_frames"] == 15


@pytest.mark.parametrize("chunks", [
    [[1, 60, 1], [60, 120, 1]],               # first chunk must start at zero
    [[0, 50, 1], [60, 120, 1]],              # gap
    [[0, 70, 1], [60, 120, 1]],              # overlap
    [[0, 60, 2], [60, 120, 1]],              # retime unsupported by cut proposal
    [[0, 120, float("nan")]],                # non-finite speed
])
def test_auto_editor_parser_rejects_invalid_or_unmapped_chunks(tmp_path, chunks):
    m = api()
    source = media_file(tmp_path)
    with pytest.raises(ValueError):
        m.parse_auto_editor_v1(
            auto_v1(source, chunks=chunks),
            source_path=source,
            probe=media_probe(source),
        )


def test_auto_editor_parser_rejects_vfr_and_non_frame_aligned_timebase(tmp_path):
    m = api()
    source = media_file(tmp_path)
    with pytest.raises(ValueError, match="VFR"):
        m.parse_auto_editor_v1(
            auto_v1(source), source_path=source,
            probe=media_probe(source, vfr=True))
    with pytest.raises(ValueError, match="frame"):
        m.parse_auto_editor_v1(
            auto_v1(source, fps="24/1", chunks=[[0, 1, 1], [1, 120, 1]]),
            source_path=source,
            probe=media_probe(source, fps="30/1"),
        )


def test_auto_editor_parser_preserves_ntsc_rational_timebase_exactly(tmp_path):
    m = api()
    source = media_file(tmp_path)
    probe = media_probe(source, fps="30000/1001", frames=1000)
    document = auto_v1(
        source,
        fps="30000/1001",
        chunks=[[0, 300, 1], [300, 500, 99999], [500, 1000, 1]],
    )
    result = m.parse_auto_editor_v1(document, source_path=source, probe=probe)
    assert result["timebase"] == "30000/1001"
    assert [(x["in_frame"], x["out_frame"]) for x in result["segments"]] == [
        (0, 300), (300, 500), (500, 1000)]
    assert result["summary"]["kept_frames"] == 800
    assert result["segments"][2]["timeline_start_frame"] == 300
    with pytest.raises(ValueError, match="frame"):
        m.parse_auto_editor_v1(
            auto_v1(source, fps="30/1", chunks=[[0, 1, 1], [1, 1000, 1]]),
            source_path=source,
            probe=probe,
        )


def test_auto_editor_runner_exports_only_v1_and_preserves_source(tmp_path, monkeypatch):
    m = api()
    source = media_file(tmp_path)
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    monkeypatch.setattr(m.shutil, "which", lambda name: "/opt/bin/auto-editor")
    calls = []

    def runner(argv, **kwargs):
        calls.append((argv, kwargs))
        output = Path(argv[argv.index("-o") + 1])
        output.write_text(json.dumps(auto_v1(source)), encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    result = m.propose_auto_editor_cuts(
        source,
        probe_fn=lambda path, **kwargs: media_probe(Path(path)),
        runner=runner,
        timeout=17,
    )
    argv, kwargs = calls[0]
    assert argv[0] == "/opt/bin/auto-editor"
    assert "--export" in argv and argv[argv.index("--export") + 1] == "v1"
    assert Path(argv[argv.index("-o") + 1]).suffix == ".v1"
    assert kwargs["shell"] is False and kwargs["timeout"] == 17
    assert result["approval_state"] == "pending"
    assert result["rendered"] is False
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert not Path(argv[argv.index("-o") + 1]).exists()


def test_auto_editor_runner_reports_timeout_and_missing_cli(tmp_path, monkeypatch):
    m = api()
    source = media_file(tmp_path)
    probe = lambda path, **kwargs: media_probe(Path(path))
    monkeypatch.setattr(m.shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError, match="auto-editor"):
        m.propose_auto_editor_cuts(source, probe_fn=probe)

    monkeypatch.setattr(m.shutil, "which", lambda name: "/opt/bin/auto-editor")
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])
    with pytest.raises(RuntimeError, match="timed out"):
        m.propose_auto_editor_cuts(source, probe_fn=probe, runner=timeout)


def test_registry_records_native_auto_editor_and_optional_longcat():
    from integrations import video_toolchain
    rows = {row["id"]: row for row in video_toolchain.REGISTRY}
    assert rows["auto-editor"]["runtime"] in {"native", "native_nim"}
    assert rows["longcat-video"]["status"] == "reference_only"
    assert rows["longcat-video"]["adapter"] is None
    assert "gpu" in rows["longcat-video"]["requires"]


def _mcp_text(result):
    return "\n".join(getattr(item, "text", "") for item in result)


def test_mcp_exposes_confined_analysis_and_review_proposal_tools(tmp_path, monkeypatch):
    from integrations import video_analysis, video_editor_mcp
    root = tmp_path / "project"
    (root / "media").mkdir(parents=True)
    source = root / "media/source.mp4"
    source.write_bytes(b"mcp-media")
    (root / "editor-projects").mkdir()
    project = {
        "schema_version": 1, "version": "R1042-1", "project_id": "demo",
        "root": str(root), "fps": [30, 1], "width": 160, "height": 120,
        "sample_rate": 48000, "channels": 2,
        "sources": {"media/source.mp4": {
            "path": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "frames": 120, "fps": [30, 1]}},
        "tracks": [{"id": "v1", "kind": "video", "clips": []}],
    }
    (root / "editor-projects/demo.json").write_text(json.dumps(project), encoding="utf-8")
    monkeypatch.setattr(video_analysis, "detect_scene_markers", lambda path, **kwargs: {
        "kind": "scene_markers", "source": {"sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
        "markers": [{"index": 0, "start_frame": 0, "end_frame": 120}],
        "review_required": True, "source_modified": False})
    monkeypatch.setattr(video_analysis, "propose_auto_editor_cuts", lambda path, **kwargs: {
        "kind": "rough_cut_proposal", "source": {"sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
        "segments": [{"in_frame": 0, "out_frame": 120, "action": "keep"}],
        "approval_state": "pending", "review_required": True, "rendered": False})

    server = video_editor_mcp.create_server(root)
    names = {tool.name for tool in asyncio.run(server.list_tools())}
    assert {"editor_analyze_scenes", "editor_propose_auto_cuts"} <= names

    scene = asyncio.run(server.call_tool("editor_analyze_scenes", {
        "project_id": "demo", "source_id": "media/source.mp4"}))
    scene_cached = asyncio.run(server.call_tool("editor_analyze_scenes", {
        "project_id": "demo", "source_id": "media/source.mp4"}))
    cut = asyncio.run(server.call_tool("editor_propose_auto_cuts", {
        "project_id": "demo", "source_id": "media/source.mp4"}))
    assert "analysis_id" in _mcp_text(scene)
    assert "cached" in _mcp_text(scene_cached)
    assert "proposal_id" in _mcp_text(cut)
    assert list((root / "editor-analysis").glob("*.json"))
    proposals = list((root / "editor-proposals").glob("*.json"))
    assert len(proposals) == 1
    assert json.loads(proposals[0].read_text())["approval_state"] == "pending"
    with pytest.raises(Exception):
        asyncio.run(server.call_tool("editor_analyze_scenes", {
            "project_id": "demo", "source_id": "../outside.mp4"}))
    with pytest.raises(Exception):
        asyncio.run(server.call_tool("editor_analyze_scenes", {
            "project_id": "../demo", "source_id": "media/source.mp4"}))
    with pytest.raises(Exception):
        asyncio.run(server.call_tool("editor_analyze_scenes", {
            "project_id": "demo", "source_id": "media/not-registered.mp4"}))
    other = root / "media/other.mp4"
    other.write_bytes(b"other")
    alias = root / "media/alias.mp4"
    alias.symlink_to(other)
    project["sources"]["media/alias.mp4"] = {
        "path": str(alias), "sha256": hashlib.sha256(other.read_bytes()).hexdigest(),
        "frames": 120, "fps": [30, 1]}
    (root / "editor-projects/demo.json").write_text(json.dumps(project), encoding="utf-8")
    with pytest.raises(Exception):
        asyncio.run(server.call_tool("editor_analyze_scenes", {
            "project_id": "demo", "source_id": "media/alias.mp4"}))


@pytest.mark.skipif(
    shutil.which("ffmpeg") is None or importlib.util.find_spec("scenedetect") is None,
    reason="optional real PySceneDetect smoke test requires FFmpeg and scenedetect",
)
def test_real_scene_detection_on_synthetic_hard_cuts(tmp_path):
    from integrations import video_analysis
    output = tmp_path / "three-scenes.mp4"
    subprocess.run([
        shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "color=c=red:s=160x120:r=10:d=1",
        "-f", "lavfi", "-i", "color=c=blue:s=160x120:r=10:d=1",
        "-f", "lavfi", "-i", "color=c=green:s=160x120:r=10:d=1",
        "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1:a=0,format=yuv420p[outv]",
        "-map", "[outv]", "-c:v", "mpeg4", str(output),
    ], check=True, capture_output=True, text=True, shell=False, timeout=30)
    result = video_analysis.detect_scene_markers(output, threshold=15.0, min_scene_len=3)
    assert result["source_modified"] is False
    assert result["review_required"] is True
    assert len(result["markers"]) >= 2
    assert result["markers"][0]["start_frame"] == 0
    assert result["markers"][-1]["end_frame"] == result["source"]["frames"]


@pytest.mark.skipif(shutil.which("auto-editor") is None, reason="Auto-Editor CLI not installed")
def test_real_auto_editor_exports_pending_proposal_without_render(tmp_path):
    from integrations import video_analysis
    source = tmp_path / "source.mp4"
    subprocess.run([
        shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "color=c=red:s=160x120:r=10:d=2",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2",
        "-shortest", "-c:v", "mpeg4", "-c:a", "aac", str(source),
    ], check=True, capture_output=True, text=True, shell=False, timeout=30)
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    result = video_analysis.propose_auto_editor_cuts(source)
    assert result["approval_state"] == "pending"
    assert result["rendered"] is False
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert not list(tmp_path.glob("*_edited.*"))
