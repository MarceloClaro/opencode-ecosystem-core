"""R1049: QC técnico de vídeo com FFmpeg real e contrato de falha."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/video_qa.py"

pytestmark = pytest.mark.skipif(
    not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
    reason="FFmpeg/ffprobe necessários")


@pytest.fixture()
def sample(tmp_path):
    path = tmp_path / "sample.mp4"
    subprocess.run([
        "ffmpeg", "-nostdin", "-v", "error",
        "-f", "lavfi", "-i", "testsrc2=s=320x180:r=25:d=1",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=1",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-shortest",
        "-y", str(path)], check=True, timeout=60)
    return path


def run_qa(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, timeout=120)


def test_qa_pass_and_contact_sheet(sample, tmp_path):
    out = tmp_path / "qa.json"
    sheet = tmp_path / "sheet.png"
    proc = run_qa("--video", str(sample), "--out", str(out),
                  "--expect-frames", "25", "--expect-fps", "25/1",
                  "--contact-sheet", str(sheet))
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text())
    assert data["status"] == "pass"
    assert data["probe"]["video"]["frames"] == 25
    assert data["probe"]["video"]["fps"] == "25/1"
    assert data["probe"]["audio"]["sample_rate"] == 48000
    assert data["checks"]["frame_count"]["ok"] is True
    assert sheet.is_file() and sheet.stat().st_size > 0


def test_qa_fails_wrong_frame_count(sample, tmp_path):
    out = tmp_path / "qa.json"
    proc = run_qa("--video", str(sample), "--out", str(out),
                  "--expect-frames", "30")
    assert proc.returncode == 1
    data = json.loads(out.read_text())
    assert data["status"] == "fail"
    assert data["checks"]["frame_count"]["ok"] is False


def test_qa_rejects_missing_file(tmp_path):
    proc = run_qa("--video", str(tmp_path / "missing.mp4"),
                  "--out", str(tmp_path / "qa.json"))
    assert proc.returncode == 2
