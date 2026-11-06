"""R1061 — política de raízes, caminhos e nomes remotos."""

from __future__ import annotations

import fnmatch
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config/storage_operator.json"
DEFAULT_STATE = "~/.local/state/opencode-storage-operator"
SECRET_PATTERNS = (
    ".env", ".env.*", "*.key", "*.pem", "id_rsa*", "id_ed25519*",
    "*.kdbx", "*.pfx", "*.p12", "credentials*", "token*", "*.secret",
)
PARTIAL_SUFFIXES = (".crdownload", ".part", ".tmp", ".partial")
SENSITIVE_SUFFIXES = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
                      ".jpg", ".jpeg", ".png", ".csv", ".txt", ".zip", ".rar")


class StorageDenied(Exception):
    def __init__(self, code: str, reason: str):
        super().__init__(reason)
        self.code = code
        self.reason = reason


@dataclass(frozen=True)
class StorageConfig:
    allowed_roots: tuple[str, ...]
    state_dir: str = DEFAULT_STATE
    drive_remote: str = "gdrive"
    drive_parent: str = ""
    max_file_bytes: int = 1024 * 1024 * 1024
    bandwidth: str = "8M"
    transfers: int = 4
    exclude_globs: tuple[str, ...] = field(default_factory=lambda: SECRET_PATTERNS)

    def __post_init__(self) -> None:
        object.__setattr__(self, "allowed_roots", tuple(str(p) for p in self.allowed_roots))
        if not self.allowed_roots:
            raise ValueError("ao menos uma raiz autorizada é obrigatória")
        if not self.drive_remote or ":" in self.drive_remote:
            raise ValueError("drive_remote deve ser o nome do remote, sem ':'")
        if self.max_file_bytes <= 0 or self.transfers <= 0:
            raise ValueError("limites devem ser positivos")


def load_config(path: Path | None = None, environ: dict[str, str] | None = None) -> StorageConfig:
    env = dict(os.environ if environ is None else environ)
    selected = env.get("STORAGE_OPERATOR_CONFIG")
    path = Path(selected).expanduser() if selected else (path or DEFAULT_CONFIG)
    data: dict[str, Any] = {}
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("configuração deve ser objeto")
    allowed = set(StorageConfig.__dataclass_fields__)
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"chaves desconhecidas: {sorted(unknown)}")
    roots = env.get("STORAGE_OPERATOR_ROOTS", "").strip()
    if roots:
        data["allowed_roots"] = [p.strip() for p in roots.split(",") if p.strip()]
    if "state_dir" in env:
        data["state_dir"] = env["state_dir"]
    return StorageConfig(**data)


def _resolved_roots(config: StorageConfig) -> list[Path]:
    return [Path(root).expanduser().resolve(strict=True) for root in config.allowed_roots]


def validate_root(config: StorageConfig, root: str | Path) -> Path:
    try:
        candidate = Path(root).expanduser().resolve(strict=True)
    except OSError as exc:
        raise StorageDenied("root_invalid", "raiz inexistente ou inacessível") from exc
    if not candidate.is_dir():
        raise StorageDenied("root_invalid", "raiz não é diretório")
    for allowed in _resolved_roots(config):
        try:
            candidate.relative_to(allowed)
            return candidate
        except ValueError:
            continue
    raise StorageDenied("root_not_allowed", "raiz fora da allowlist")


def is_excluded(config: StorageConfig, relpath: str) -> bool:
    name = Path(relpath).name
    patterns = tuple(config.exclude_globs) + SECRET_PATTERNS
    return any(fnmatch.fnmatch(name.casefold(), p.casefold()) or
               fnmatch.fnmatch(relpath.casefold(), p.casefold()) for p in patterns)


def validate_file(config: StorageConfig, root: Path, relpath: str) -> Path:
    if not isinstance(relpath, str) or not relpath or Path(relpath).is_absolute():
        raise StorageDenied("path_invalid", "caminho relativo obrigatório")
    if ".." in Path(relpath).parts:
        raise StorageDenied("path_traversal", "caminho com '..'")
    root = Path(root).resolve(strict=True)
    raw = root / relpath
    if raw.is_symlink():
        raise StorageDenied("symlink_denied", "symlink não é aceito")
    candidate = raw.resolve(strict=True)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise StorageDenied("path_escape", "arquivo fora da raiz") from exc
    if not candidate.is_file():
        raise StorageDenied("not_regular_file", "arquivo regular obrigatório")
    if is_excluded(config, relpath):
        raise StorageDenied("excluded_secret", "arquivo excluído por padrão de segredo")
    return candidate


def remote_folder(root: Path, now: float | None = None) -> str:
    stamp = datetime.fromtimestamp(0 if now == 0 else (now or datetime.now().timestamp()))
    return f"{Path(root).name}_{stamp:%Y-%m-%d_%H-%M-%S}"


def remote_path(config: StorageConfig, folder: str) -> str:
    parent = config.drive_parent.strip("/")
    return f"{config.drive_remote}:{parent + '/' if parent else ''}{folder}"
