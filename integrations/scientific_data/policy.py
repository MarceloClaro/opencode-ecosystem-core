"""R1065 — política de acesso a arquivos científicos locais."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config/scientific_data.json"
ALLOWED_SUFFIXES = {".nc", ".nc4", ".cdf", ".h5", ".hdf5", ".he5",
                    ".tif", ".tiff", ".gtiff", ".zarr"}
DEFAULT_ROOTS = (str(ROOT), "/mnt/c/Users/marce/Downloads", "/tmp/opencode")


class ScientificDenied(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ScientificConfig:
    allowed_roots: tuple[str, ...] = DEFAULT_ROOTS
    max_file_bytes: int = 2 * 1024 * 1024 * 1024
    max_preview_points: int = 2000

    def __post_init__(self) -> None:
        object.__setattr__(self, "allowed_roots", tuple(str(p) for p in self.allowed_roots))
        if not self.allowed_roots:
            raise ValueError("ao menos uma raiz é obrigatória")
        if self.max_file_bytes <= 0 or self.max_preview_points <= 0:
            raise ValueError("limites devem ser positivos")


def load_config(path: Path | None = None, environ: dict[str, str] | None = None) -> ScientificConfig:
    env = dict(os.environ if environ is None else environ)
    target = Path(path or DEFAULT_CONFIG).expanduser()
    data = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else {}
    roots = env.get("SCIENTIFIC_DATA_ROOTS", "").strip()
    if roots:
        data["allowed_roots"] = [p.strip() for p in roots.split(os.pathsep) if p.strip()]
    allowed = {"allowed_roots", "max_file_bytes", "max_preview_points"}
    if set(data) - allowed:
        raise ValueError(f"chaves desconhecidas: {sorted(set(data) - allowed)}")
    return ScientificConfig(**data)


def validate_path(config: ScientificConfig, path: str | Path) -> Path:
    if not isinstance(path, (str, Path)) or not str(path).strip():
        raise ScientificDenied("path_required", "caminho obrigatório")
    raw = Path(path).expanduser()
    if raw.is_symlink():
        raise ScientificDenied("symlink_denied", "symlink não é aceito")
    try:
        resolved = raw.resolve(strict=True)
    except OSError as exc:
        raise ScientificDenied("path_missing", "arquivo ou diretório inexistente") from exc
    roots = [Path(root).expanduser().resolve() for root in config.allowed_roots]
    if not any(resolved == root or resolved.is_relative_to(root) for root in roots):
        raise ScientificDenied("path_not_allowed", "caminho fora das raízes autorizadas")
    suffix = resolved.suffix.casefold()
    is_zarr = resolved.is_dir() and suffix == ".zarr"
    if not is_zarr and not resolved.is_file():
        raise ScientificDenied("path_invalid", "arquivo regular ou diretório .zarr obrigatório")
    if not is_zarr and suffix not in ALLOWED_SUFFIXES:
        raise ScientificDenied("format_not_supported", f"extensão não suportada: {suffix}")
    if not is_zarr and resolved.stat().st_size > config.max_file_bytes:
        raise ScientificDenied("file_too_large", "arquivo acima do limite local")
    return resolved
