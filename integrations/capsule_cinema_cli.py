#!/usr/bin/env python3
# capsule-cinema CLI adapter (SPEC-935-R1117)

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

CAPSULE_SUFFIXES = {".capsule"}
DEFAULT_OUTPUT_ROOTS = (Path.cwd() / "out", Path("/tmp/opencode"))
SAFE_ENV_KEYS = (
    "PATH",
    "HOME",
    "TMPDIR",
    "TEMP",
    "TMP",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "PYTHONIOENCODING",
)

FORBIDDEN_COMMANDS = {
    "remake-run",
    "remake-plan",
    "assemble",
    "capsule",
    "remake",
}

FORBIDDEN_EXTRA_ARGS = {"--env-file", "--plugin"}


class CapsuleCinemaError(RuntimeError):
    pass


class CapsuleCinemaUnavailable(RuntimeError):
    pass


class CapsuleCinemaBlocked(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verification() -> dict[str, Any]:
    return {
        "scope": "local_observation",
        "externally_validated": False,
        "confidence_promoted": False,
    }


def find_cli(explicit: str | Path | None = None) -> Path | None:
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(Path(explicit).expanduser())
    env_value = os.environ.get("CAPSULE_CINEMA_BIN")
    if env_value:
        candidates.append(Path(env_value).expanduser())
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
        raise CapsuleCinemaUnavailable(
            f"binário capsule-cinema inválido ou não executável: {candidate}"
        )
    found = shutil.which("capsule-cinema")
    return Path(found).resolve() if found else None


def status(
    explicit: str | Path | None = None,
    *,
    run_help: bool = True,
    timeout: float = 10.0,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema": "capsule_cinema.status.v1",
        "available": False,
        "path": None,
        "help_exit_code": None,
        "help_first_line": None,
        "verification": _verification(),
    }
    try:
        cli = find_cli(explicit)
    except CapsuleCinemaUnavailable as error:
        base["error"] = str(error)
        return base
    if cli is None:
        base["error"] = "capsule-cinema não encontrado no PATH nem em CAPSULE_CINEMA_BIN"
        return base
    base["available"] = True
    base["path"] = str(cli)
    if run_help:
        try:
            completed = subprocess.run(
                [str(cli), "--help"],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as error:
            base["error"] = f"falha ao executar --help: {error}"
            return base
        output = (completed.stdout or completed.stderr or "").strip()
        base["help_exit_code"] = completed.returncode
        base["help_first_line"] = output.splitlines()[0] if output else None
    return base


def doctor(
    explicit: str | Path | None = None,
    *,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    try:
        cli = find_cli(explicit)
    except CapsuleCinemaUnavailable as error:
        cli = None
        checks.append({"name": "cli", "ok": False, "detail": str(error)})
    else:
        checks.append(
            {"name": "cli", "ok": cli is not None, "detail": str(cli) if cli else "não encontrado"}
        )
    for tool in ("ffmpeg", "ffprobe"):
        path = shutil.which(tool)
        checks.append({"name": tool, "ok": path is not None, "detail": path or "não encontrado"})
    root = Path(output_root or DEFAULT_OUTPUT_ROOTS[0]).expanduser()
    if root.exists():
        writable = root.is_dir() and os.access(root, os.W_OK)
        detail = str(root)
    else:
        parent = root.parent
        writable = parent.exists() and os.access(parent, os.W_OK)
        detail = f"{root} (ausente; pai gravável: {parent})"
    checks.append({"name": "output_root", "ok": writable, "detail": detail})
    return {
        "schema": "capsule_cinema.doctor.v1",
        "ok": all(check["ok"] for check in checks),
        "checks": checks,
        "verification": _verification(),
    }


def _validate_capsule(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_file():
        raise CapsuleCinemaError(f"cápsula não encontrada: {candidate}")
    if candidate.suffix.lower() not in CAPSULE_SUFFIXES:
        raise CapsuleCinemaError(
            f"extensão de cápsula não reconhecida: {candidate.suffix!r} "
            f"(aceitas: {', '.join(sorted(CAPSULE_SUFFIXES))})"
        )
    return candidate.resolve()


def _validate_output(path: str | Path, roots: Sequence[str | Path]) -> Path:
    target = Path(path).expanduser().resolve()
    for root in roots:
        root_resolved = Path(root).expanduser().resolve()
        if target == root_resolved or root_resolved in target.parents:
            return target
    raise CapsuleCinemaError(
        f"diretório de saída fora das raízes autorizadas: {target} "
        f"(autorizadas: {', '.join(str(root) for root in roots)})"
    )


def _prepare_output(path: Path, overwrite: bool) -> None:
    if path.exists():
        if not path.is_dir():
            raise CapsuleCinemaError(f"saída existe e não é diretório: {path}")
        if any(path.iterdir()) and not overwrite:
            raise CapsuleCinemaError(
                f"diretório de saída não vazio: {path}; use --overwrite para permitir"
            )
        return
    path.mkdir(parents=True, exist_ok=True)


def _build_argv(
    cli: Path,
    capsule: Path,
    out: Path,
    *,
    extra_args: Iterable[str] | None,
) -> list[str]:
    argv = [str(cli), "decompose", str(capsule), "-o", str(out)]
    for argument in extra_args or ():
        if argument in FORBIDDEN_COMMANDS:
            raise CapsuleCinemaBlocked(f"comando bloqueado em extra_args: {argument}")
        if argument in FORBIDDEN_EXTRA_ARGS:
            raise CapsuleCinemaBlocked(
                f"argumento bloqueado em extra_args: {argument} (segredos não são repassados)"
            )
        argv.append(argument)
    return argv


def _artifact_inventory(path: Path) -> dict[str, Any]:
    files: dict[str, Any] = {}
    for name in (
        "manifest.json",
        "breakdown.json",
        "report.html",
        "report.md",
        "storyboard.jpg",
        "audio.png",
        "VIDEO.md",
    ):
        candidate = path / name
        if candidate.is_file():
            files[name] = {"bytes": candidate.stat().st_size, "sha256": _sha256(candidate)}
    counts = {}
    for name in ("shots", "stems"):
        directory = path / name
        counts[name] = (
            len([entry for entry in directory.iterdir() if entry.is_file()])
            if directory.is_dir()
            else 0
        )
    return {"files": files, "counts": counts}


def decompose(
    capsule: str | Path,
    out: str | Path,
    *,
    cli: str | Path | None = None,
    dry_run: bool = False,
    yes: bool = False,
    overwrite: bool = False,
    timeout: float = 1800.0,
    allowed_output_roots: Sequence[str | Path] | None = None,
    env_passthrough: Iterable[str] | None = None,
) -> dict[str, Any]:
    cli_path = find_cli(cli)
    if cli_path is None:
        raise CapsuleCinemaUnavailable(
            "capsule-cinema não encontrado; instale com o operador ou defina CAPSULE_CINEMA_BIN"
        )
    capsule_path = _validate_capsule(capsule)
    roots = (
        list(allowed_output_roots) if allowed_output_roots is not None else list(DEFAULT_OUTPUT_ROOTS)
    )
    out_path = _validate_output(out, roots)
    argv = _build_argv(cli_path, capsule_path, out_path, extra_args=())

    result: dict[str, Any] = {
        "schema": "capsule_cinema.decompose.v1",
        "executed": False,
        "dry_run": dry_run,
        "ok": None,
        "command": argv,
        "out": str(out_path),
        "verification": _verification(),
    }
    if dry_run:
        return result
    if not yes:
        raise CapsuleCinemaBlocked(
            "decompose exige consentimento explícito (--yes); use --dry-run para revisar"
        )
    _prepare_output(out_path, overwrite)
    env = {key: os.environ[key] for key in SAFE_ENV_KEYS if key in os.environ}
    for key in env_passthrough or ():
        if key in os.environ:
            env[key] = os.environ[key]
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"timeout após {timeout}s ao executar capsule-cinema") from error
    except OSError as error:
        raise RuntimeError(f"falha ao executar capsule-cinema: {error}") from error
    result.update(
        {
            "executed": True,
            "ok": completed.returncode == 0,
            "exit_code": completed.returncode,
            "stdout_tail": (completed.stdout or "")[-4000:],
            "stderr_tail": (completed.stderr or "")[-4000:],
            "artifacts": _artifact_inventory(out_path),
        }
    )
    return result


def summary(capsule: str | Path) -> dict[str, Any]:
    path = Path(capsule).expanduser()
    if not path.is_file():
        raise CapsuleCinemaError(f"cápsula não encontrada: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CapsuleCinemaError(f"cápsula inválida: {error}") from error
    shots = data.get("shots") if isinstance(data, dict) else None
    if not isinstance(shots, list):
        shots = []
    types: Counter[str] = Counter()
    low_confidence = 0
    for shot in shots:
        if not isinstance(shot, dict):
            continue
        shot_type = (
            shot.get("type")
            or shot.get("shot_type")
            or shot.get("visual_type")
            or "unknown"
        )
        types[str(shot_type)] += 1
        confidence = shot.get("confidence")
        if shot.get("low_confidence") is True or (
            isinstance(confidence, (int, float)) and confidence < 0.5
        ):
            low_confidence += 1
    return {
        "schema": "capsule_cinema.summary.v1",
        "source": str(path),
        "source_sha256": _sha256(path),
        "top_level_keys": sorted(data.keys()) if isinstance(data, dict) else [],
        "shot_count": len(shots),
        "low_confidence_count": low_confidence,
        "types": dict(sorted(types.items())),
        "verification": _verification(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Adaptador somente leitura do capsule-cinema")
    sub = parser.add_subparsers(dest="command", required=True)
    status_parser = sub.add_parser("status", help="estado do binário")
    status_parser.add_argument("--cli")
    doctor_parser = sub.add_parser("doctor", help="checagens de ambiente")
    doctor_parser.add_argument("--cli")
    doctor_parser.add_argument("--output-root")
    decompose_parser = sub.add_parser("decompose", help="analisa uma cápsula")
    decompose_parser.add_argument("capsule")
    decompose_parser.add_argument("--out", required=True)
    decompose_parser.add_argument("--cli")
    decompose_parser.add_argument("--dry-run", action="store_true")
    decompose_parser.add_argument("--yes", action="store_true")
    decompose_parser.add_argument("--overwrite", action="store_true")
    decompose_parser.add_argument("--timeout", type=float, default=1800.0)
    summary_parser = sub.add_parser("summary", help="resume manifest.json")
    summary_parser.add_argument("capsule")
    remake_parser = sub.add_parser("remake-run", help="bloqueado por política")
    remake_parser.add_argument("args", nargs="*")
    args = parser.parse_args(argv)
    try:
        if args.command == "status":
            print(json.dumps(status(args.cli), indent=2, ensure_ascii=False))
            return 0
        if args.command == "doctor":
            print(json.dumps(doctor(args.cli, output_root=args.output_root), indent=2, ensure_ascii=False))
            return 0
        if args.command == "decompose":
            print(
                json.dumps(
                    decompose(
                        args.capsule,
                        args.out,
                        cli=args.cli,
                        dry_run=args.dry_run,
                        yes=args.yes,
                        overwrite=args.overwrite,
                        timeout=args.timeout,
                    ),
                    indent=2,
                    ensure_ascii=False,
                )
            )
            return 0
        if args.command == "summary":
            print(json.dumps(summary(args.capsule), indent=2, ensure_ascii=False))
            return 0
        if args.command == "remake-run":
            raise RuntimeError(
                "remake-run bloqueado: a operação chama provedores pagos e não é exposta "
                "pelo Core. Execute manualmente com autorização e orçamento explícitos."
            )
            return 0
    except CapsuleCinemaBlocked as error:
        print(json.dumps({"ok": False, "blocked": True, "error": str(error)}), indent=2, ensure_ascii=False)
        return 2
    except RuntimeError as error:
        print(json.dumps({"ok": False, "error": str(error)}), indent=2, ensure_ascii=False)
        return 1
    except Exception as error:
        print(json.dumps({"ok": False, "error": str(error)}), indent=2, ensure_ascii=False)
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())