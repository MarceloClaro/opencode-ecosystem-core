# -*- coding: utf-8 -*-
"""Adaptador REAP para OpenCode (SPEC-935-R1113).

Instala packs da biblioteca REA-Prompts de forma determinística, com
``dry-run``, manifesto de hashes e rollback. Não executa scripts do
repositório de origem e não instala as 26 skills no topo do catálogo.

Uso:
    python3 -m integrations.reap_adapter plan --source /tmp/opencode/REA-Prompts \
        --target .opencode/skills/reap-prompts --layout references
    python3 -m integrations.reap_adapter install ... --dry-run
    python3 -m integrations.reap_adapter install ... --yes
    python3 -m integrations.reap_adapter validate --manifest .../.reap-manifest.json
    python3 -m integrations.reap_adapter rollback --manifest ... --yes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA_PLAN = "reap.install-plan.v1"
SCHEMA_MANIFEST = "reap.manifest.v1"
PACK_RE = re.compile(r"^reap-[a-z0-9][a-z0-9-]*$")


class AdapterError(RuntimeError):
    """Falha controlada do adaptador."""


@dataclass(frozen=True)
class Pack:
    name: str
    source_dir: Path
    skill_md: Path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_pack_name(name: str) -> str:
    if not isinstance(name, str) or not PACK_RE.match(name):
        raise AdapterError(f"nome de pack inválido: {name!r}")
    if "/" in name or "\\" in name or name in {".", ".."}:
        raise AdapterError(f"nome de pack inseguro: {name!r}")
    return name


def discover_packs(source: Path) -> list[Pack]:
    source = Path(source).expanduser().resolve()
    skills_dir = source / "Skills" if (source / "Skills").is_dir() else source
    if not skills_dir.is_dir():
        raise AdapterError(f"diretório de origem não encontrado: {skills_dir}")
    packs: list[Pack] = []
    for child in sorted(skills_dir.iterdir()):
        if child.is_dir() and (child / "SKILL.md").is_file():
            validate_pack_name(child.name)
            packs.append(
                Pack(
                    name=child.name,
                    source_dir=child.resolve(),
                    skill_md=(child / "SKILL.md").resolve(),
                )
            )
    if not packs:
        raise AdapterError(f"nenhum pack reap-* encontrado em {skills_dir}")
    return packs


def default_allowed_roots() -> list[Path]:
    return [
        Path.cwd() / ".opencode" / "skills",
        Path.home() / ".config" / "opencode" / "skills",
        Path.home() / ".local" / "share" / "opencode" / "skills",
    ]


def _resolve_within(path: Path, roots: Sequence[Path]) -> Path:
    target = Path(path).expanduser().resolve()
    for root in roots:
        root_resolved = Path(root).expanduser().resolve()
        if target == root_resolved or root_resolved in target.parents:
            return target
    raise AdapterError(
        f"destino fora das raízes permitidas: {target} "
        f"(permitidas: {', '.join(str(root) for root in roots)})"
    )


def _pack_files(pack: Pack, layout: str) -> list[tuple[Path, Path]]:
    files: list[tuple[Path, Path]] = []
    for source in sorted(p for p in pack.source_dir.rglob("*") if p.is_file()):
        relative = source.relative_to(pack.source_dir)
        if layout == "skills":
            destination = Path(pack.name) / relative
        elif layout == "references":
            if relative == Path("SKILL.md"):
                destination = Path("references") / "packs" / f"{pack.name}.md"
            else:
                destination = Path("references") / "packs" / pack.name / relative
        else:
            raise AdapterError(f"layout inválido: {layout}")
        files.append((source, destination))
    return files


def plan_install(
    source: Path,
    target_root: Path,
    *,
    layout: str = "skills",
    packs: Iterable[str] | None = None,
    allowed_roots: Sequence[Path] | None = None,
) -> dict[str, Any]:
    """Calcula o plano sem escrever no disco."""
    roots = list(allowed_roots) if allowed_roots is not None else default_allowed_roots()
    target = _resolve_within(target_root, roots)
    discovered = discover_packs(source)
    by_name = {pack.name: pack for pack in discovered}

    if packs is None:
        selected = discovered
    else:
        selected = []
        for name in packs:
            validate_pack_name(name)
            if name not in by_name:
                raise AdapterError(f"pack não encontrado: {name}")
            selected.append(by_name[name])

    entries: list[dict[str, Any]] = []
    summary = {"create": 0, "overwrite": 0, "identical": 0}
    for pack in selected:
        for source_file, relative_destination in _pack_files(pack, layout):
            destination = target / relative_destination
            if target not in destination.resolve().parents:
                raise AdapterError(f"destino escapa da raiz: {destination}")
            digest = _sha256(source_file)
            if destination.exists():
                action = (
                    "identical"
                    if destination.is_file() and _sha256(destination) == digest
                    else "overwrite"
                )
            else:
                action = "create"
            summary[action] += 1
            entries.append(
                {
                    "pack": pack.name,
                    "source": str(source_file),
                    "destination": str(relative_destination),
                    "sha256": digest,
                    "bytes": source_file.stat().st_size,
                    "action": action,
                }
            )

    return {
        "schema": SCHEMA_PLAN,
        "source": str(Path(source).expanduser().resolve()),
        "target_root": str(target),
        "layout": layout,
        "entries": entries,
        "summary": summary,
        "writes": summary["create"] + summary["overwrite"] > 0,
    }


def _git_commit(source: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def apply_install(
    plan: dict[str, Any],
    *,
    dry_run: bool = True,
    backup: bool = True,
) -> dict[str, Any]:
    """Aplica um plano. ``dry_run=True`` não escreve nada."""
    if plan.get("schema") != SCHEMA_PLAN:
        raise AdapterError("plano inválido: schema ausente ou desconhecido")
    if dry_run:
        return {**plan, "dry_run": True, "applied": False}

    target = Path(plan["target_root"])
    target.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = target / ".reap-backup" / timestamp
    backups: list[dict[str, str]] = []
    written: list[str] = []

    for entry in plan["entries"]:
        if entry["action"] == "identical":
            continue
        destination = target / entry["destination"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and backup:
            backup_path = backup_root / entry["destination"]
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, backup_path)
            backups.append(
                {
                    "destination": entry["destination"],
                    "backup": str(backup_path.relative_to(target)),
                }
            )

        descriptor, temporary = tempfile.mkstemp(
            dir=str(destination.parent), prefix=".reap-", suffix=".tmp"
        )
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(Path(entry["source"]).read_bytes())
        os.replace(temporary, destination)
        written.append(entry["destination"])

    manifest = {
        "schema": SCHEMA_MANIFEST,
        "source": plan["source"],
        "source_commit": _git_commit(Path(plan["source"])),
        "target_root": plan["target_root"],
        "layout": plan["layout"],
        "created_at": _now(),
        "entries": plan["entries"],
        "backups": backups,
        "written": written,
    }
    manifest_path = target / ".reap-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {
        **plan,
        "dry_run": False,
        "applied": True,
        "manifest": str(manifest_path),
        "written": written,
        "backups": backups,
    }


def validate_manifest(manifest_path: Path) -> dict[str, Any]:
    path = Path(manifest_path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    target = Path(manifest["target_root"])
    mismatches: list[dict[str, str]] = []
    for entry in manifest.get("entries", []):
        destination = target / entry["destination"]
        if not destination.is_file():
            mismatches.append({"destination": entry["destination"], "reason": "missing"})
        elif _sha256(destination) != entry["sha256"]:
            mismatches.append({"destination": entry["destination"], "reason": "hash"})
    return {
        "ok": not mismatches,
        "checked": len(manifest.get("entries", [])),
        "mismatches": mismatches,
        "manifest": str(path),
    }


def rollback(manifest_path: Path, *, dry_run: bool = False) -> dict[str, Any]:
    path = Path(manifest_path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    target = Path(manifest["target_root"])
    removed: list[str] = []
    preserved: list[str] = []
    preserved_set: set[str] = set()
    restored: list[str] = []

    for entry in manifest.get("entries", []):
        destination = target / entry["destination"]
        if not destination.exists():
            continue
        if destination.is_file() and _sha256(destination) == entry["sha256"]:
            if not dry_run:
                destination.unlink()
            removed.append(str(destination))
        else:
            preserved.append(str(destination))
            preserved_set.add(entry["destination"])

    for item in manifest.get("backups", []):
        backup = target / item["backup"]
        destination = target / item["destination"]
        if not backup.is_file() or item["destination"] in preserved_set:
            continue
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup, destination)
        restored.append(str(destination))

    if not dry_run:
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    return {
        "ok": True,
        "dry_run": dry_run,
        "removed": removed,
        "preserved": preserved,
        "restored": restored,
    }


def _print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", required=True, help="raiz do REA-Prompts ou Skills/")
    parser.add_argument("--target", required=True, help="raiz de destino")
    parser.add_argument(
        "--layout", choices=("skills", "references"), default="skills"
    )
    parser.add_argument("--packs", help="lista separada por vírgula")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Adaptador REAP para OpenCode")
    sub = parser.add_subparsers(dest="command", required=True)

    plan_parser = sub.add_parser("plan", help="calcula o plano sem escrever")
    _add_common(plan_parser)

    install_parser = sub.add_parser("install", help="aplica o plano")
    _add_common(install_parser)
    install_parser.add_argument("--dry-run", action="store_true")
    install_parser.add_argument("--no-backup", action="store_true")
    install_parser.add_argument("--yes", action="store_true")

    validate_parser = sub.add_parser("validate", help="confere hashes do manifesto")
    validate_parser.add_argument("--manifest", required=True)

    rollback_parser = sub.add_parser("rollback", help="desfaz uma instalação")
    rollback_parser.add_argument("--manifest", required=True)
    rollback_parser.add_argument("--dry-run", action="store_true")
    rollback_parser.add_argument("--yes", action="store_true")

    args = parser.parse_args(argv)

    try:
        if args.command == "plan":
            packs = args.packs.split(",") if args.packs else None
            _print(
                plan_install(
                    Path(args.source),
                    Path(args.target),
                    layout=args.layout,
                    packs=packs,
                )
            )
            return 0

        if args.command == "install":
            packs = args.packs.split(",") if args.packs else None
            plan = plan_install(
                Path(args.source),
                Path(args.target),
                layout=args.layout,
                packs=packs,
            )
            if not args.dry_run and not args.yes:
                _print({**plan, "applied": False, "reason": "use --yes para escrever"})
                return 2
            _print(
                apply_install(plan, dry_run=args.dry_run, backup=not args.no_backup)
            )
            return 0

        if args.command == "validate":
            report = validate_manifest(Path(args.manifest))
            _print(report)
            return 0 if report["ok"] else 1

        if args.command == "rollback":
            if not args.dry_run and not args.yes:
                _print({"ok": False, "reason": "use --yes para desfazer"})
                return 2
            _print(rollback(Path(args.manifest), dry_run=args.dry_run))
            return 0
    except AdapterError as error:
        _print({"ok": False, "error": str(error)})
        return 2

    return 1


if __name__ == "__main__":
    sys.exit(main())
