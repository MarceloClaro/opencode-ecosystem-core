"""R1024 — plano de edição de vídeo auditável, sem rede ou execução de mídia."""

from __future__ import annotations

import ast
import copy
import io
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs/SPEC-935-R1024-plano-edicao-video.md"
MANIFEST = ROOT / "federation/video-editing-sources-r1024.json"
MODULE = ROOT / "integrations/video_edit_plan.py"


def plan_document() -> dict:
    return {
        "schema_version": "1.0",
        "project": {
            "id": "demo",
            "title": "Demonstração",
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "sample_rate": 48000,
        },
        "sources": [
            {
                "id": "cam",
                "path": "input/cam.mp4",
                "sha256": "a" * 64,
                "duration_frames": 900,
                "width": 1920,
                "height": 1080,
                "rights": "authorized",
            },
            {
                "id": "broll",
                "path": "input/broll.mp4",
                "duration_frames": 600,
                "width": 1920,
                "height": 1080,
                "rights": "cc_by",
            },
        ],
        "video": [
            {"id": "v1", "source": "cam", "in_frame": 0, "out_frame": 300,
             "timeline_start": 0},
            {"id": "v2", "source": "broll", "in_frame": 100, "out_frame": 400,
             "timeline_start": 300},
        ],
        "audio": [
            {"id": "a1", "source": "cam", "in_frame": 0, "out_frame": 300,
             "timeline_start": 0, "gain_db": 0},
        ],
        "captions": [
            {"id": "c1", "start_frame": 0, "end_frame": 90,
             "text": "Uma frase curta de teste."},
        ],
        "output": {
            "path": "out/final.mp4",
            "container": "mp4",
            "video_codec": "h264",
            "audio_codec": "aac",
            "loudness_lufs": -16,
        },
    }


def write_plan(tmp_path: Path, document: dict | None = None) -> Path:
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(document or plan_document()), encoding="utf-8")
    return path


def engine():
    assert SPEC.is_file(), "Spec R1024 ausente"
    assert MODULE.is_file(), "Módulo de plano de edição ausente"
    from integrations import video_edit_plan

    return video_edit_plan


def validate(document: dict) -> dict:
    return engine().validate_plan(document)


def codes(result: dict) -> set[str]:
    return {item["code"] for item in result["errors"]}


def warnings(result: dict) -> set[str]:
    return {item["code"] for item in result["warnings"]}


def test_valid_plan_is_accepted() -> None:
    result = validate(plan_document())
    assert result["status"] == "valid", result
    assert result["errors"] == []
    assert result["summary"]["timeline_frames"] == 600
    assert result["summary"]["source_count"] == 2
    assert result["summary"]["video_clips"] == 2
    assert len(result["digest_sha256"]) == 64
    assert result["visual_quality_verified"] is False


def test_unknown_field_is_rejected() -> None:
    document = plan_document()
    document["video"][0]["timline_start"] = 0
    result = validate(document)
    assert result["status"] == "invalid"
    assert "unknown_field" in codes(result)


def test_duplicate_ids_are_rejected() -> None:
    document = plan_document()
    document["sources"].append(dict(document["sources"][0]))
    result = validate(document)
    assert "duplicate_id" in codes(result)


def test_unknown_source_is_rejected() -> None:
    document = plan_document()
    document["video"][0]["source"] = "ausente"
    result = validate(document)
    assert "source_not_found" in codes(result)


def test_load_rejects_symlink(tmp_path: Path) -> None:
    vp = engine()
    target = write_plan(tmp_path)
    link = tmp_path / "link.json"
    link.symlink_to(target)
    with pytest.raises(vp.PlanError) as error:
        vp.load_plan(link)
    assert error.value.code == "unsafe_file"


def test_load_rejects_oversized_plan(tmp_path: Path) -> None:
    vp = engine()
    path = tmp_path / "big.json"
    path.write_text('{"x":"' + "a" * (2 * 1024 * 1024) + '"}', encoding="utf-8")
    with pytest.raises(vp.PlanError) as error:
        vp.load_plan(path)
    assert error.value.code == "file_too_large"


def test_load_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    vp = engine()
    path = tmp_path / "dup.json"
    path.write_text('{"schema_version":"1.0","schema_version":"1.0"}', encoding="utf-8")
    with pytest.raises(vp.PlanError) as error:
        vp.load_plan(path)
    assert error.value.code == "invalid_json"


def test_source_bounds_are_enforced() -> None:
    document = plan_document()
    document["video"][0]["out_frame"] = 901
    assert "source_bounds" in codes(validate(document))
    document = plan_document()
    document["video"][0]["in_frame"] = -1
    assert "source_bounds" in codes(validate(document))


def test_timeline_overlap_is_rejected() -> None:
    document = plan_document()
    document["video"][1]["timeline_start"] = 200
    result = validate(document)
    assert result["status"] == "invalid"
    assert "timeline_overlap" in codes(result)


def test_timeline_gap_is_a_warning() -> None:
    document = plan_document()
    document["video"][1]["timeline_start"] = 330
    result = validate(document)
    assert result["status"] == "valid", result
    assert "timeline_gap" in warnings(result)


def test_frame_math_is_exact() -> None:
    document = plan_document()
    document["project"]["fps"] = 29.97
    result = validate(document)
    assert result["status"] == "valid"
    assert result["summary"]["timeline_frames"] == 600
    assert result["summary"]["duration_seconds"] == pytest.approx(600 / 29.97, abs=1e-6)


def test_caption_reading_speed_is_enforced() -> None:
    document = plan_document()
    document["captions"][0].update(
        start_frame=0, end_frame=30, text="uma frase bastante longa para exigir leitura rapida demais"
    )
    result = validate(document)
    assert "caption_too_fast" in codes(result)


def test_caption_overlap_is_rejected() -> None:
    document = plan_document()
    document["captions"].append(
        {"id": "c2", "start_frame": 30, "end_frame": 120, "text": "Outra frase."}
    )
    assert "caption_overlap" in codes(validate(document))


def test_caption_beyond_timeline_is_rejected() -> None:
    document = plan_document()
    document["captions"][0]["end_frame"] = 700
    assert "caption_beyond_timeline" in codes(validate(document))


def test_crop_outside_source_is_rejected() -> None:
    document = plan_document()
    document["video"][0]["crop"] = [0, 0, 2000, 1080]
    assert "crop_outside_source" in codes(validate(document))


def test_aspect_mismatch_is_a_warning() -> None:
    document = plan_document()
    document["video"][0]["crop"] = [0, 0, 1000, 1000]
    result = validate(document)
    assert result["status"] == "valid", result
    assert "aspect_mismatch" in warnings(result)


def test_output_cannot_overwrite_source() -> None:
    document = plan_document()
    document["output"]["path"] = "input/cam.mp4"
    assert "output_overwrites_source" in codes(validate(document))


def test_extension_and_codec_compatibility() -> None:
    document = plan_document()
    document["output"]["path"] = "out/final.mkv"
    assert "container_extension_mismatch" in codes(validate(document))
    document = plan_document()
    document["output"]["video_codec"] = "vp9"
    assert "codec_container_incompatible" in codes(validate(document))


def test_rights_must_be_resolved() -> None:
    document = plan_document()
    document["sources"][0]["rights"] = "unknown"
    assert "rights_unresolved" in codes(validate(document))
    document = plan_document()
    document["sources"][0].pop("rights")
    assert "rights_unresolved" in codes(validate(document))


def test_hash_and_loudness_are_validated() -> None:
    document = plan_document()
    document["sources"][0]["sha256"] = "abc"
    assert "hash_invalid" in codes(validate(document))
    document = plan_document()
    document["output"]["loudness_lufs"] = -30
    assert "loudness_out_of_range" in codes(validate(document))


def test_unsafe_paths_are_rejected() -> None:
    for value in ("../cam.mp4", "/tmp/cam.mp4", "input\\cam.mp4"):
        document = plan_document()
        document["sources"][0]["path"] = value
        assert "unsafe_path" in codes(validate(document)), value
    document = plan_document()
    document["output"]["path"] = "/tmp/final.mp4"
    assert "unsafe_path" in codes(validate(document))


def test_plan_is_deterministic_and_not_mutated() -> None:
    document = plan_document()
    before = copy.deepcopy(document)
    first = validate(document)
    second = validate(document)
    assert first == second
    assert document == before
    assert first["digest_sha256"] == second["digest_sha256"]


def test_render_metadata_match() -> None:
    vp = engine()
    result = vp.verify_render(
        plan_document(),
        {
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "duration_seconds": 20.0,
            "video_codec": "h264",
            "audio_codec": "aac",
            "container": "mp4",
            "loudness_lufs": -16,
        },
    )
    assert result["status"] == "render_metadata_matched", result
    assert result["render_verified"] is True
    assert result["visual_quality_verified"] is False
    assert result["reasons"] == []


def test_render_mismatch_and_alias_handling() -> None:
    vp = engine()
    base = {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "duration_seconds": 20.0,
        "video_codec": "avc1",
        "audio_codec": "mp4a",
        "container": "mp4",
        "loudness_lufs": -16,
    }
    assert vp.verify_render(plan_document(), base)["status"] == "render_metadata_matched"
    wrong = dict(base, width=1280)
    result = vp.verify_render(plan_document(), wrong)
    assert result["status"] == "blocked"
    assert "render_width_mismatch" in {item["code"] for item in result["reasons"]}
    longer = dict(base, duration_seconds=25.0)
    assert "render_duration_mismatch" in {
        item["code"] for item in vp.verify_render(plan_document(), longer)["reasons"]
    }


def test_render_requires_valid_plan() -> None:
    vp = engine()
    document = plan_document()
    document["video"][0]["out_frame"] = 9999
    result = vp.verify_render(document, {"width": 1920, "height": 1080})
    assert result["status"] == "blocked"
    assert "plan_invalid" in {item["code"] for item in result["reasons"]}
    assert result["render_verified"] is False


def test_render_never_claims_visual_quality() -> None:
    vp = engine()
    result = vp.verify_render(
        plan_document(),
        {
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "duration_seconds": 20.0,
            "video_codec": "h264",
            "audio_codec": "aac",
            "container": "mp4",
        },
    )
    assert result["visual_quality_verified"] is False
    assert result["metadata_only"] is True
    assert "loudness_not_measured" in {item["code"] for item in result["warnings"]}
    assert "content_verified" not in result


def test_cli_validate_compile_and_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    vp = engine()
    path = write_plan(tmp_path)
    assert vp.main(["validate", str(path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "valid"
    assert vp.main(["compile", str(path)]) == 0
    compiled = json.loads(capsys.readouterr().out)
    assert compiled["canonical_plan"]["project"]["fps"] == 30
    assert len(compiled["digest_sha256"]) == 64
    document = plan_document()
    document["video"][0]["out_frame"] = 9999
    bad = write_plan(tmp_path, document)
    assert vp.main(["validate", str(bad)]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "invalid"
    assert payload["errors"]


def test_no_network_or_execution_imports() -> None:
    assert MODULE.is_file(), "Módulo de plano de edição ausente"
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    imports |= {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert imports <= {"__future__", "argparse", "hashlib", "json", "re", "sys", "pathlib"}
    forbidden = {"exec", "eval", "__import__", "open", "system", "popen", "run", "check_output"}
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not called & forbidden
    assert "requests" not in source and "urllib" not in source and "subprocess" not in source


def test_source_manifest_is_pinned_and_scoped() -> None:
    assert MANIFEST.is_file(), "Manifesto de fontes de vídeo ausente"
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["schema_version"] == "r1024.v1"
    rows = data["sources"]
    assert len(rows) == 11
    names = {row["repo"] for row in rows}
    assert "AcademySoftwareFoundation/OpenTimelineIO" in names
    assert "remotion-dev/remotion" in names
    for row in rows:
        assert row["installed"] is False and row["executed"] is False
        assert len(row["commit"]) == 40
        assert row["license_declared"] and row["license_scope"]
        assert row["contribution"] and row["limitations"]
        assert row["documents"]
        for doc in row["documents"]:
            assert doc["url"].startswith(
                f"https://raw.githubusercontent.com/{row['repo']}/{row['commit']}/"
            )
            assert len(doc["sha256"]) == 64 and doc["bytes"] > 0 and doc["http_status"] == 200
    by_repo = {row["repo"]: row for row in rows}
    assert "Remotion License" in by_repo["remotion-dev/remotion"]["license_declared"]
    assert "LGPL" in by_repo["FFmpeg/FFmpeg"]["license_declared"]
    assert "BSD-2-Clause-Patent" in by_repo["Netflix/vmaf"]["license_declared"]
    assert "Unlicense" in by_repo["WyattBlue/auto-editor"]["license_declared"]
    assert any("pausad" in item.lower() for item in by_repo["jianfch/stable-ts"]["limitations"])


def test_skills_reference_the_validator() -> None:
    links = {
        ".claude/skills/cp-direcao-de-edicao/SKILL.md": "references/plano-de-edicao-auditavel.md",
        ".claude/skills/meia-legendas-e-enquadramento/SKILL.md": "references/plano-de-edicao-auditavel.md",
        ".claude/skills/meia-revisao-economia/SKILL.md": "references/plano-de-edicao-auditavel.md",
    }
    for relative, marker in links.items():
        skill = ROOT / relative
        assert skill.is_file(), relative
        assert marker in skill.read_text(encoding="utf-8")
        reference = skill.parent / marker
        assert reference.is_file(), reference
        assert "video_edit_plan" in reference.read_text(encoding="utf-8")
