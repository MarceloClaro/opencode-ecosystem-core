"""Validate and apply preparation effects embedded in an approved workflow plan."""

from __future__ import annotations

import json
import shutil
from pathlib import Path, PurePosixPath
from typing import Any, Literal
from urllib.parse import urlparse

from ngs_workbench_daemon import ssh
from ngs_workbench_daemon.hashing import file_identity, sha256_bytes
from pydantic import BaseModel, ConfigDict, Field

from .compute_targets import resolve_compute_target
from .plans import PreparationOperation, PreparationSpec

_SHA256_PATTERN = r"^(?:sha256:)?[0-9a-f]{64}$"
_MAX_DOWNLOADS = 64
_MAX_GENERATED_FILES = 32
_MAX_GENERATED_FILE_BYTES = 1024 * 1024


class VerifiedDownloadRequest(BaseModel):
    """One exact remote file to download and verify before workflow launch."""

    model_config = ConfigDict(extra="forbid")

    relative_path: str = Field(min_length=1)
    url: str = Field(min_length=1)
    bytes: int = Field(ge=0)
    sha256: str = Field(pattern=_SHA256_PATTERN)
    role: str = Field(default="workflow input", min_length=1, max_length=200)


class GeneratedFileRequest(BaseModel):
    """One bounded text file whose exact content is part of the workflow plan."""

    model_config = ConfigDict(extra="forbid")

    relative_path: str = Field(min_length=1)
    content: str
    media_type: Literal["application/json", "text/csv", "text/plain"] = "text/plain"


class PreparationRequest(BaseModel):
    """Typed, analysis-owned effects that run under the workflow plan approval."""

    model_config = ConfigDict(extra="forbid")

    destination_dir: str = Field(min_length=1)
    downloads: list[VerifiedDownloadRequest] = Field(default_factory=list)
    generated_files: list[GeneratedFileRequest] = Field(default_factory=list)


def _resolve_destination(value: str) -> Path:
    destination = Path(value).expanduser()
    if not destination.is_absolute():
        raise ValueError("preparation destination_dir must be an absolute path")
    if destination.is_symlink():
        raise ValueError(f"preparation destination_dir must not be a symlink: {destination}")
    destination = destination.resolve(strict=False)
    if destination == Path(destination.anchor):
        raise ValueError("preparation destination_dir must not be a filesystem root")
    if destination.exists() and not destination.is_dir():
        raise ValueError(f"preparation destination_dir is not a directory: {destination}")
    return destination


def _safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path == Path("."):
        raise ValueError(f"unsafe preparation relative_path: {value!r}")
    return path


def _normalized_sha256(value: str) -> str:
    return value if value.startswith("sha256:") else f"sha256:{value}"


def normalize_preparation(
    request: PreparationRequest | dict[str, Any] | None,
    target_id: str = "local",
) -> PreparationSpec | None:
    """Create a destination-read-only preparation description for a workflow plan."""
    if request is None:
        return None
    validated = PreparationRequest.model_validate(request)
    if not validated.downloads and not validated.generated_files:
        raise ValueError("preparation must contain at least one supported operation")
    if len(validated.downloads) > _MAX_DOWNLOADS:
        raise ValueError(f"preparation supports at most {_MAX_DOWNLOADS} downloads")
    if len(validated.generated_files) > _MAX_GENERATED_FILES:
        raise ValueError(f"preparation supports at most {_MAX_GENERATED_FILES} generated files")

    target = resolve_compute_target(target_id)
    remote = target.controller_transport == "ssh"
    destination = (
        resolve_input_path(validated.destination_dir, target_id)
        if remote
        else _resolve_destination(validated.destination_dir)
    )
    if destination == Path("/"):
        raise ValueError("preparation destination_dir must not be a filesystem root")
    operations: list[PreparationOperation] = []
    for request_item in validated.downloads:
        relative = _safe_relative_path(request_item.relative_path)
        parsed = urlparse(request_item.url)
        if (
            parsed.scheme != "https"
            or parsed.hostname is None
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
        ):
            raise ValueError(
                "download URL must use HTTPS with a host and without credentials or fragments: "
                f"{request_item.url}"
            )
        operations.append(
            PreparationOperation(
                operation="download_verified_file",
                relative_path=relative.as_posix(),
                path=str(destination / relative),
                role=request_item.role,
                url=request_item.url,
                bytes=request_item.bytes,
                sha256=_normalized_sha256(request_item.sha256),
            )
        )

    for request_item in validated.generated_files:
        relative = _safe_relative_path(request_item.relative_path)
        encoded = request_item.content.encode("utf-8")
        if len(encoded) > _MAX_GENERATED_FILE_BYTES:
            raise ValueError(f"generated file exceeds 1 MiB: {relative}")
        if request_item.media_type == "application/json":
            try:
                json.loads(request_item.content)
            except json.JSONDecodeError as exc:
                raise ValueError(f"generated JSON is invalid for {relative}: {exc}") from exc
        operations.append(
            PreparationOperation(
                operation="write_generated_file",
                relative_path=relative.as_posix(),
                path=str(destination / relative),
                media_type=request_item.media_type,
                content=request_item.content,
                bytes=len(encoded),
                sha256=sha256_bytes(encoded),
            )
        )

    paths = [item.relative_path for item in operations]
    if len(paths) != len(set(paths)):
        raise ValueError("preparation contains duplicate destination paths")
    curl_path = (
        ssh.preparation_executable(target.model_dump(), str(destination), bool(validated.downloads))
        if remote
        else shutil.which("curl")
        if validated.downloads
        else None
    )
    if validated.downloads and curl_path is None:
        raise ValueError("curl is required for verified-file preparation")
    return PreparationSpec(
        destination_dir=str(destination),
        operations=operations,
        transfer_executable=curl_path
        if remote
        else str(Path(curl_path).resolve())
        if curl_path
        else None,
        download_bytes=sum(item.bytes for item in operations if item.url is not None),
        writes=[item.path for item in operations],
    )


def operation_for_path(
    spec: PreparationSpec | None, path: Path | None
) -> PreparationOperation | None:
    """Return the exact planned operation for a prospective file path."""
    if spec is None or path is None:
        return None
    return next((item for item in spec.operations if Path(item.path) == path), None)


def generated_text(spec: PreparationSpec | None, path: Path | None) -> str | None:
    operation = operation_for_path(spec, path)
    return operation.content if operation is not None else None


def resolve_input_path(value: str | None, target_id: str) -> Path | None:
    if value is None:
        return None
    if target_id != "local":
        path = PurePosixPath(value)
        if not path.is_absolute() or ".." in path.parts:
            raise ValueError("SSH input paths must be absolute paths on the selected target")
        return Path(path)
    path = Path(value)
    if not path.is_absolute():
        raise ValueError("input paths must be absolute paths on the selected target")
    return path.resolve()


def inspect_input(
    path: Path, spec: PreparationSpec | None, target_id: str, *, read_text: bool = False
) -> dict[str, Any]:
    operation = operation_for_path(spec, path)
    if operation is not None:
        return {"bytes": operation.bytes, "sha256": operation.sha256, "content": operation.content}
    if target_id != "local":
        target = resolve_compute_target(target_id)
        return ssh.inspect_input(target.model_dump(), str(path), read_text=read_text)
    size, digest = file_identity(path)
    return {
        "bytes": size,
        "sha256": digest,
        **({"content": path.read_text(encoding="utf-8-sig")} if read_text else {}),
    }
