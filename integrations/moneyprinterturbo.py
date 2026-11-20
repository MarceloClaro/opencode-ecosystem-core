"""R1234: isolated MoneyPrinterTurbo metadata and local MP4 handoff only.

This module never imports MoneyPrinterTurbo, starts its application, invokes a
provider, renders media, or publishes. It only copies a completed task export
into the Core editor's confined root and records it as a one-clip project.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from integrations import video_editor

VERSION = "R1234-1"
UPSTREAM = {
    "repository": "https://github.com/harry0703/MoneyPrinterTurbo",
    "version": "1.3.10",
    "commit": "8b0206be2c7977e3bc3cf25ff99a2adc3c9c65f9",
    "package": "mpt",
    "wheel": "mpt-1.3.10-py3-none-any.whl",
    "wheel_sha256": "5a2a9ca8b3e43502f32c8e27ae1a8c7c13ff75e6adad6be45a3e051b088f8c9f",
    "python_requires": ">=3.11",
    "license": "MIT",
    "dependency_conflicts": [
        "starlette==1.3.1 conflicts with the Core Starlette pin; keep MPT in its private venv"
    ],
}

_TASK_EXPORT = re.compile(
    r"(?P<task>[A-Za-z0-9][A-Za-z0-9_-]{0,63})/final-(?P<number>[1-9][0-9]*)\.mp4"
)
_PROJECT_ID = re.compile(r"[A-Za-z0-9_-]{1,80}")


def installation_plan(home: str | Path | None = None) -> dict:
    """Describe paths/pins without installing, launching, or reading secrets."""
    base = Path(home).expanduser().absolute() if home is not None else (
        Path.home() / ".local" / "share" / "marceloclaro"
    )
    install_root = base / "tools" / "mpt" / UPSTREAM["version"]
    data_root = base / "data" / "mpt" / UPSTREAM["version"]
    return {
        "version": UPSTREAM["version"],
        "commit": UPSTREAM["commit"],
        "package": UPSTREAM["package"],
        "wheel_sha256": UPSTREAM["wheel_sha256"],
        "python_requires": UPSTREAM["python_requires"],
        "isolated": True,
        "install_root": str(install_root),
        "venv": str(install_root / "venv"),
        "mpt_home": str(data_root),
        "mpt_output_root": str(data_root / "storage" / "tasks"),
        "core_requirements_changed": False,
        "read_credentials": False,
        "create_config_toml": False,
        "configure_credentials": False,
        "launch_application": False,
        "generation_enabled": False,
        "render_enabled": False,
        "publish_enabled": False,
        "import_contract": "task_final_mp4_only",
        "scene_clips_supported": False,
        "status": "plan_only",
    }


def _safe_root(raw: str | Path, label: str) -> Path:
    root = Path(raw).expanduser().absolute()
    for node in (root, *root.parents):
        if node.is_symlink():
            raise ValueError(f"{label} root symlink blocked")
    if not root.is_dir():
        raise ValueError(f"{label} root must be an existing directory")
    return root


def _confined(root: Path, relative: str, *, must_exist: bool = False) -> Path:
    if (not isinstance(relative, str) or not relative or "\x00" in relative
            or "\\" in relative):
        raise ValueError("relative POSIX path required")
    candidate = Path(relative)
    if candidate.is_absolute() or any(part in ("", ".", "..") for part in candidate.parts):
        raise ValueError("relative path required; escape blocked")
    target = root / candidate
    for node in (target, *target.parents):
        if node.is_symlink():
            raise ValueError("symlink blocked")
        if node == root:
            break
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("path escape blocked")
    if must_exist and not target.is_file():
        raise ValueError("regular media file required")
    return target


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_asset(source: Path, editor_root: Path, expected_sha: str) -> tuple[Path, bool]:
    relative = f"editor-assets/moneyprinterturbo/{expected_sha}.mp4"
    target = _confined(editor_root, relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    target = _confined(editor_root, relative)

    if target.exists():
        if target.is_symlink() or not target.is_file() or _hash(target) != expected_sha:
            raise ValueError("asset integrity collision")
        return target, False

    fd, temp_name = tempfile.mkstemp(prefix=".mpt-import-", suffix=".tmp",
                                     dir=target.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as destination, source.open("rb") as origin:
            shutil.copyfileobj(origin, destination, length=1024 * 1024)
            destination.flush()
            os.fsync(destination.fileno())
        if _hash(temp) != expected_sha:
            raise ValueError("source changed during import; SHA-256 mismatch")
        try:
            # Same-directory hard-link creation is atomic and never overwrites.
            os.link(temp, target)
            created = True
        except FileExistsError:
            if target.is_symlink() or not target.is_file() or _hash(target) != expected_sha:
                raise ValueError("asset integrity collision")
            created = False
    finally:
        temp.unlink(missing_ok=True)
    return target, created


def _create_project(project_dir: Path, project_file: Path, serialized: str) -> None:
    """Atomically create a project without replacing an existing path."""
    fd, temp_name = tempfile.mkstemp(prefix=".mpt-project-", suffix=".tmp",
                                     dir=project_dir)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temp, project_file)
        except FileExistsError as exc:
            raise ValueError("project already exists; refusing overwrite") from exc
    finally:
        temp.unlink(missing_ok=True)


def import_task_output(
    mpt_output_root: str | Path,
    editor_root: str | Path,
    media_path: str,
    project_id: str,
    *,
    allow_silent: bool = False,
    probe_fn=None,
) -> dict:
    """Copy one completed ``<task-id>/final-N.mp4`` into a new editor project.

    The call is filesystem-only except for the editor's media probe. It does not
    execute MPT or call the editor render backend.
    """
    if not isinstance(project_id, str) or not _PROJECT_ID.fullmatch(project_id):
        raise ValueError("valid project_id required")
    if type(allow_silent) is not bool:
        raise ValueError("allow_silent must be boolean")
    if not isinstance(media_path, str) or not _TASK_EXPORT.fullmatch(media_path):
        raise ValueError("MPT export must be <task_id>/final-N.mp4")

    source_root = _safe_root(mpt_output_root, "MPT output")
    destination_root = _safe_root(editor_root, "editor")
    source = _confined(source_root, media_path, must_exist=True)
    project_dir = _confined(destination_root, "editor-projects")
    project_file = _confined(destination_root, f"editor-projects/{project_id}.json")
    if project_file.exists():
        raise ValueError("project already exists; refusing overwrite")

    probe_fn = probe_fn or video_editor.probe_media
    initial_sha = _hash(source)
    source_probe = probe_fn(source, allow_silent=True)
    if source_probe.get("sha256") != initial_sha:
        raise ValueError("source integrity changed during media probe")
    source_audio = source_probe.get("audio")
    has_audio = isinstance(source_audio, dict)
    if not has_audio and not allow_silent:
        raise ValueError("silent MPT output requires allow_silent=true")

    asset_path, created_asset = _write_asset(source, destination_root, initial_sha)
    try:
        media_probe = probe_fn(asset_path, allow_silent=True)
        if media_probe.get("sha256") != initial_sha:
            raise ValueError("copied asset integrity mismatch")
        if isinstance(media_probe.get("audio"), dict) != has_audio:
            raise ValueError("source audio metadata changed during import")

        relative_asset = str(asset_path.relative_to(destination_root))
        project = video_editor.project_from_probe(
            relative_asset, media_probe, project_id=project_id, allow_silent=allow_silent
        )
        project["root"] = str(destination_root)
        video_track = next(track for track in project["tracks"] if track["kind"] == "video")
        audio_track = next(track for track in project["tracks"] if track["kind"] == "audio")
        frames = project["sources"][relative_asset]["frames"]
        video_track["clips"].append({
            "id": "mpt-video-1", "track": video_track["id"], "source": relative_asset,
            "in_frame": 0, "out_frame": frames, "start_frame": 0,
            "speed": 1.0, "volume": 1.0,
        })
        if has_audio:
            audio_track["clips"].append({
                "id": "mpt-audio-1", "track": audio_track["id"], "source": relative_asset,
                "in_frame": 0, "out_frame": frames, "start_frame": 0,
                "speed": 1.0, "volume": 1.0,
            })
        serialized = video_editor.dumps_project(project)
        project_dir.mkdir(parents=True, exist_ok=True)
        project_file = _confined(destination_root, f"editor-projects/{project_id}.json")
        _create_project(project_dir, project_file, serialized)
    except Exception:
        if created_asset:
            asset_path.unlink(missing_ok=True)
        raise

    return {
        "status": "imported", "project_id": project_id,
        "media_path": relative_asset, "sha256": initial_sha,
        "frames": frames, "fps": media_probe["video"]["fps"],
        "has_audio": has_audio, "application_started": False,
        "generated": False, "rendered": False, "published": False,
        "scene_clips_imported": False,
    }
