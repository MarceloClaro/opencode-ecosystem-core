#!/usr/bin/env python3
"""Prévia ou migração preservadora R983 do EvolutionRegistry.

Sem --apply, o comando é somente leitura. A aplicação usa o caminho
versionado fixo do Core e cria backup byte-a-byte antes da publicação atômica.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = ROOT / "evolution" / "cycles.json"
DEFAULT_BACKUP = ROOT / "evolution" / "migrations" / "R983" / "cycles.json.before"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Aplicar a migração depois da prévia humana.")
    mode.add_argument("--dry-run", action="store_true", help="Prévia somente leitura (padrão).")
    parser.add_argument("--backup", type=Path, default=DEFAULT_BACKUP,
                        help="Destino exclusivo do backup byte-a-byte (diretório deve existir).")
    args = parser.parse_args(argv)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from evolution.cycles import EvolutionRegistry

    registry = EvolutionRegistry(state_path=DEFAULT_STATE)
    if args.apply:
        result = registry.migrate_legacy_entries(backup_path=args.backup)
    else:
        result = registry.preview_legacy_migration()
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    if result.get("unmigratable_count", 0) or result.get("remaining_unmodelled_count", 0):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
