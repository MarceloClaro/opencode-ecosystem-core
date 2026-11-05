"""R1069: QA técnico de vídeo com ffmpeg/ffprobe, sem executar o alvo."""
from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from integrations.video_qa import probe


def _ffmpeg(args: list[str]) -> None:
    result = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args],
                            capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip("ffmpeg indisponível para o fixture: " + result.stderr[-300:])


def make_black_video(path: Path) -> None:
    _ffmpeg([
        "-f", "lavfi", "-i", "color=c=black:s=160x120:d=0.5",
        "-f", "lavfi", "-i", "color=c=red:s=160x120:d=1.0",
        "-f", "lavfi", "-i", "color=c=black:s=160x120:d=0.5",
        "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]",
        "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path),
    ])


def make_silence_video(path: Path) -> None:
    _ffmpeg([
        "-f", "lavfi", "-i", "color=c=blue:s=160x120:d=2.0",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=1.0",
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo:d=1.0",
        "-filter_complex", "[1:a][2:a]concat=n=2:v=0:a=1[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", str(path),
    ])


def test_black_frames_and_frames(tmp_path):
    video = tmp_path / "black.mp4"
    make_black_video(video)
    result = probe(video, output_dir=tmp_path / "qa", frames=3)
    assert result["status"] == "completed"
    assert result["metadata"]["video"]["width"] == 160
    assert len(result["black_intervals"]) >= 2
    assert any(row["duration"] >= 0.3 for row in result["black_intervals"])
    assert "black_frames" in result["issues"]
    assert len(result["frames"]) == 3
    assert all(Path(frame["path"]).is_file() for frame in result["frames"])
    assert result["human_review_required"] is True
    assert result["external_validation"] is False


def test_silence_and_loudness(tmp_path):
    video = tmp_path / "silence.mp4"
    make_silence_video(video)
    result = probe(video, output_dir=tmp_path / "qa", frames=1)
    assert result["metadata"]["audio"] is not None
    assert any(row["duration"] >= 0.8 for row in result["silence_intervals"])
    assert "silence" in result["issues"]
    assert result["loudness"]["integrated_lufs"] is not None


def test_missing_or_invalid_input(tmp_path):
    with pytest.raises(ValueError):
        probe(tmp_path / "missing.mp4")
    directory = tmp_path / "dir"
    directory.mkdir()
    with pytest.raises(ValueError):
        probe(directory)
