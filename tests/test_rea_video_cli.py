# -*- coding: utf-8 -*-
"""Testes do adaptador somente leitura do rea-video (SPEC-935-R1116)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from integrations.rea_video_cli import (
    ReaVideoBlocked,
    ReaVideoError,
    decompose,
    doctor,
    remake_run,
    status,
    summary,
)

FAKE_CLI = '''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path

if "--help" in sys.argv:
    print("rea-video fake 0.1.0")
    sys.exit(0)

if len(sys.argv) >= 2 and sys.argv[1] == "decompose":
    out = Path(sys.argv[sys.argv.index("-o") + 1])
    out.mkdir(parents=True, exist_ok=True)
    (out / "breakdown.json").write_text(json.dumps({"shots": [
        {"id": "s1", "type": "live", "confidence": 0.9},
        {"id": "s2", "type": "ai", "confidence": 0.3, "low_confidence": True}
    ]}), encoding="utf-8")
    (out / "VIDEO.md").write_text("# video\\n", encoding="utf-8")
    (out / ".executed").write_text("1", encoding="utf-8")
    (out / ".secret").write_text(os.environ.get("SECRET", ""), encoding="utf-8")
    print("ok")
    sys.exit(0)

print("unsupported", file=sys.stderr)
sys.exit(2)
'''


def _fake_cli(tmp_path: Path) -> Path:
    path = tmp_path / "rea-video"
    path.write_text(FAKE_CLI, encoding="utf-8")
    path.chmod(0o755)
    return path


def _video(tmp_path: Path, name: str = "clip.mp4") -> Path:
    path = tmp_path / name
    path.write_bytes(b"fake-video")
    return path


def _roots(tmp_path: Path) -> list[Path]:
    allowed = tmp_path / "allowed"
    allowed.mkdir(exist_ok=True)
    return [allowed]


def test_status_finds_fake_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _fake_cli(tmp_path)
    monkeypatch.setenv("REA_VIDEO_BIN", str(fake))
    result = status()
    assert result["available"] is True
    assert Path(result["path"]) == fake
    assert result["help_exit_code"] == 0
    assert "rea-video fake" in result["help_first_line"]


def test_status_missing_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("REA_VIDEO_BIN", raising=False)
    monkeypatch.setattr("integrations.rea_video_cli.shutil.which", lambda _: None)
    result = status()
    assert result["available"] is False
    assert result["path"] is None


def test_doctor_reports_checks(tmp_path: Path) -> None:
    fake = _fake_cli(tmp_path)
    result = doctor(fake, output_root=tmp_path / "allowed")
    checks = {check["name"]: check for check in result["checks"]}
    assert checks["cli"]["ok"] is True
    assert "ffmpeg" in checks
    assert "ffprobe" in checks
    assert "output_root" in checks


def test_decompose_dry_run_does_not_execute(tmp_path: Path) -> None:
    fake = _fake_cli(tmp_path)
    video = _video(tmp_path)
    out = tmp_path / "allowed" / "run"
    result = decompose(
        video,
        out,
        cli=fake,
        dry_run=True,
        allowed_output_roots=_roots(tmp_path),
    )
    assert result["executed"] is False
    assert result["dry_run"] is True
    assert not out.exists()
    assert result["command"][0] == str(fake)


def test_decompose_requires_yes(tmp_path: Path) -> None:
    fake = _fake_cli(tmp_path)
    with pytest.raises(ReaVideoBlocked):
        decompose(
            _video(tmp_path),
            tmp_path / "allowed" / "run",
            cli=fake,
            dry_run=False,
            allowed_output_roots=_roots(tmp_path),
        )


def test_decompose_executes_and_hashes_artifacts(tmp_path: Path) -> None:
    fake = _fake_cli(tmp_path)
    out = tmp_path / "allowed" / "run"
    result = decompose(
        _video(tmp_path),
        out,
        cli=fake,
        yes=True,
        allowed_output_roots=_roots(tmp_path),
    )
    assert result["executed"] is True
    assert result["exit_code"] == 0
    assert (out / ".executed").is_file()
    assert result["artifacts"]["files"]["breakdown.json"]["sha256"]
    assert result["artifacts"]["files"]["VIDEO.md"]["sha256"]
    assert result["verification"]["externally_validated"] is False


def test_decompose_refuses_non_empty_output(tmp_path: Path) -> None:
    fake = _fake_cli(tmp_path)
    out = tmp_path / "allowed" / "run"
    out.mkdir(parents=True)
    (out / "existing.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ReaVideoError):
        decompose(
            _video(tmp_path),
            out,
            cli=fake,
            yes=True,
            allowed_output_roots=_roots(tmp_path),
        )


def test_decompose_rejects_output_outside_roots(tmp_path: Path) -> None:
    fake = _fake_cli(tmp_path)
    with pytest.raises(ReaVideoError):
        decompose(
            _video(tmp_path),
            tmp_path / "outside",
            cli=fake,
            yes=True,
            allowed_output_roots=_roots(tmp_path),
        )


def test_decompose_rejects_non_video(tmp_path: Path) -> None:
    fake = _fake_cli(tmp_path)
    text = tmp_path / "notes.txt"
    text.write_text("not a video", encoding="utf-8")
    with pytest.raises(ReaVideoError):
        decompose(
            text,
            tmp_path / "allowed" / "run",
            cli=fake,
            yes=True,
            allowed_output_roots=_roots(tmp_path),
        )


def test_decompose_does_not_leak_secret(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _fake_cli(tmp_path)
    monkeypatch.setenv("SECRET", "top-secret")
    out = tmp_path / "allowed" / "run"
    decompose(
        _video(tmp_path),
        out,
        cli=fake,
        yes=True,
        allowed_output_roots=_roots(tmp_path),
    )
    assert (out / ".secret").read_text(encoding="utf-8") == ""


def test_decompose_accepts_path_with_spaces(tmp_path: Path) -> None:
    fake = _fake_cli(tmp_path)
    video = _video(tmp_path, name="my clip.mp4")
    out = tmp_path / "allowed" / "run with spaces"
    result = decompose(
        video,
        out,
        cli=fake,
        yes=True,
        allowed_output_roots=_roots(tmp_path),
    )
    assert result["executed"] is True


def test_summary_reads_breakdown(tmp_path: Path) -> None:
    breakdown = tmp_path / "breakdown.json"
    breakdown.write_text(
        json.dumps(
            {
                "shots": [
                    {"id": "s1", "type": "live", "confidence": 0.9},
                    {"id": "s2", "type": "ai", "confidence": 0.3, "low_confidence": True},
                ]
            }
        ),
        encoding="utf-8",
    )
    result = summary(breakdown)
    assert result["shot_count"] == 2
    assert result["low_confidence_count"] == 1
    assert result["types"] == {"ai": 1, "live": 1}
    assert result["source_sha256"]


def test_summary_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ReaVideoError):
        summary(tmp_path / "missing.json")


def test_remake_run_is_blocked(tmp_path: Path) -> None:
    with pytest.raises(ReaVideoBlocked):
        remake_run(_video(tmp_path), tmp_path / "allowed" / "run")


def test_timeout_is_reported(tmp_path: Path) -> None:
    slow = tmp_path / "slow-rea-video"
    slow.write_text(
        "#!/usr/bin/env python3\nimport time\ntime.sleep(5)\n", encoding="utf-8"
    )
    slow.chmod(0o755)
    with pytest.raises(ReaVideoError, match="timeout"):
        decompose(
            _video(tmp_path),
            tmp_path / "allowed" / "run",
            cli=slow,
            yes=True,
            timeout=0.2,
            allowed_output_roots=_roots(tmp_path),
        )
