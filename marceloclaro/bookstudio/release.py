"""Manifesto de release com SHA-256, tamanho e verificação."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


class ReleaseError(ValueError):
    """Manifesto ou artefato inválido."""


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    target = Path(path)
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class Artifact:
    path: str
    kind: str
    sha256: str
    bytes: int

    def __post_init__(self) -> None:
        if not self.path.strip():
            raise ReleaseError("artifact.path vazio")
        if len(self.sha256) != 64 or any(c not in "0123456789abcdef" for c in self.sha256):
            raise ReleaseError("artifact.sha256 inválido")
        if self.bytes < 0:
            raise ReleaseError("artifact.bytes negativo")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "kind": self.kind,
            "sha256": self.sha256,
            "bytes": self.bytes,
        }


@dataclass(frozen=True)
class ReleaseManifest:
    release_id: str
    created_at: str
    artifacts: Tuple[Artifact, ...]
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_versions: Dict[str, str] = field(default_factory=dict)
    status: str = "built"

    def __post_init__(self) -> None:
        if not self.release_id.strip():
            raise ReleaseError("release_id vazio")
        if not self.artifacts:
            raise ReleaseError("release sem artefatos")
        if len({a.path for a in self.artifacts}) != len(self.artifacts):
            raise ReleaseError("artefatos duplicados no manifesto")

    @classmethod
    def build(cls, release_id: str, paths: Iterable[str | Path], *,
              root: str | Path | None = None, kind: str = "artifact",
              metadata: Dict[str, Any] | None = None,
              tool_versions: Dict[str, str] | None = None) -> "ReleaseManifest":
        if not release_id.strip():
            raise ReleaseError("release_id vazio")
        base = Path(root).expanduser().resolve() if root is not None else None
        artifacts: List[Artifact] = []
        for raw in paths:
            target = Path(raw).expanduser().resolve()
            if not target.is_file():
                raise ReleaseError(f"artefato ausente: {raw}")
            if base is not None:
                try:
                    relative = target.relative_to(base)
                except ValueError as exc:
                    raise ReleaseError(f"artefato fora da raiz: {raw}") from exc
                path_str = relative.as_posix()
            else:
                path_str = str(target)
            artifacts.append(Artifact(
                path=path_str,
                kind=kind,
                sha256=sha256_file(target),
                bytes=target.stat().st_size,
            ))
        return cls(
            release_id=release_id.strip(),
            created_at=datetime.now(timezone.utc).isoformat(),
            artifacts=tuple(artifacts),
            metadata=dict(metadata or {}),
            tool_versions=dict(tool_versions or {}),
            status="built",
        )

    def verify(self, root: str | Path | None = None) -> Dict[str, Any]:
        base = Path(root).expanduser().resolve() if root is not None else Path.cwd()
        missing: List[str] = []
        mismatched: List[Dict[str, Any]] = []
        checked = 0
        for artifact in self.artifacts:
            target = Path(artifact.path)
            if not target.is_absolute():
                target = (base / target).resolve()
            if not target.is_file():
                missing.append(artifact.path)
                continue
            checked += 1
            actual_size = target.stat().st_size
            actual_hash = sha256_file(target)
            if actual_size != artifact.bytes or actual_hash != artifact.sha256:
                mismatched.append({
                    "path": artifact.path,
                    "expected_bytes": artifact.bytes,
                    "actual_bytes": actual_size,
                    "expected_sha256": artifact.sha256,
                    "actual_sha256": actual_hash,
                })
        return {
            "ok": not missing and not mismatched,
            "release_id": self.release_id,
            "checked": checked,
            "total": len(self.artifacts),
            "missing": missing,
            "mismatched": mismatched,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": 1,
            "release_id": self.release_id,
            "created_at": self.created_at,
            "status": self.status,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "metadata": self.metadata,
            "tool_versions": self.tool_versions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReleaseManifest":
        if not isinstance(data, dict):
            raise ReleaseError("manifesto deve ser objeto")
        artifacts = tuple(
            Artifact(
                path=str(row["path"]),
                kind=str(row.get("kind", "artifact")),
                sha256=str(row["sha256"]),
                bytes=int(row["bytes"]),
            )
            for row in data.get("artifacts", [])
        )
        return cls(
            release_id=str(data.get("release_id", "")),
            created_at=str(data.get("created_at", "")),
            artifacts=artifacts,
            metadata=dict(data.get("metadata") or {}),
            tool_versions={str(k): str(v) for k, v in (data.get("tool_versions") or {}).items()},
            status=str(data.get("status", "built")),
        )

    def save(self, path: str | Path) -> Path:
        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: str | Path) -> "ReleaseManifest":
        target = Path(path).expanduser().resolve()
        return cls.from_dict(json.loads(target.read_text(encoding="utf-8")))
