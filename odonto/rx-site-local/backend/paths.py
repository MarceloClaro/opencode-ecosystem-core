"""Resolução de caminhos locais com fail-closed — SPEC-935-R900.

Nenhum caminho vem do usuário sem verificação: ``resolve_dataset`` só aceita
nomes do inventário real ou caminhos contidos em ``odonto/local/datasets``.
"""
from __future__ import annotations

import sys
from pathlib import Path

# backend/paths.py → parents[0]=backend, [1]=rx-site-local, [2]=odonto
ODONTO = Path(__file__).resolve().parents[2]
LOCAL = ODONTO / "local"
DATASETS = LOCAL / "datasets"
OUTPUTS = LOCAL / "outputs"
MANUSCRIPT = ODONTO / "manuscript_assets" / "robust_audit"
TABLE_S1 = MANUSCRIPT / "Table_S1.xlsx"


class DatasetPathError(ValueError):
    """Nome/caminho de dataset recusado (fora da allowlist)."""


def ensure_import_path() -> None:
    """Garante que ``import odontoca`` funcione (o pacote vive em odonto/local)."""
    local = str(LOCAL)
    if local not in sys.path:
        sys.path.insert(0, local)


def under(child: Path, parent: Path) -> bool:
    child, parent = child.resolve(), parent.resolve()
    return child == parent or parent in child.parents


def resolve_dataset(name: str) -> Path:
    """Resolve um nome do inventário para um caminho real permitido."""
    if not name or "\x00" in name:
        raise DatasetPathError("nome de dataset vazio ou inválido")
    candidate = Path(name)
    if candidate.is_absolute():
        raise DatasetPathError("caminho absoluto não é aceito")
    target = (DATASETS / name).resolve()
    if not under(target, DATASETS):
        raise DatasetPathError(f"caminho fora de datasets/: {name}")
    if not target.is_file():
        raise DatasetPathError(f"dataset inexistente: {name}")
    return target


def resolve_table_s1() -> Path:
    if not TABLE_S1.is_file():
        raise DatasetPathError(f"Table_S1.xlsx ausente em {MANUSCRIPT}")
    return TABLE_S1
