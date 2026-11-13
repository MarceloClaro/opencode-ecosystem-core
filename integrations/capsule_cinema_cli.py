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


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verification():
    return {
        "scope": "local_observation",
        "externally_validated": False,
        "confidence_promoted": False,
    }


def find_cli(explicit=None):
    candidates = []
    if explicit is not None:
        candidates.append(Path(explicit).expanduser())
    env_value = os.environ.get("CAPSULE_CINEMA_BIN")
    if env_value:
        candidates.append(Path(env_value).expanduser())
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
        raise CapsuleCinemaUnavailable(
            f"binario capsule-cinema invalido ou nao executavel: {candidate}"
        )
    found = shutil.which("capsule-cinema")
    return Path(found).resolve() if found else None


def status(explicit=None, *, run_help=True, timeout=10.0):
    base = {
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
        base["error"] = "capsule-cinema nao encontrado no PATH nem em CAPSULE_CINEMA_BIN"
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


def doctor(explicit=None, *, output_root=None):
    checks = []
    try:
        cli = find_cli(explicit)
    except CapsuleCinemaUnavailable as error:
        cli = None
        checks.append({"name": "cli", "ok": False, "detail": str(error)})
    else:
        checks.append(
            {"name": "cli", "ok": cli is not None, "detail": str(cli) if cli else "nao encontrado"}
        )
    for tool in ("ffmpeg", "ffprobe"):
        path = shutil.which(tool)
        checks.append({"name": tool, "ok": path is not None, "detail": path or "nao encontrado"})
    root = Path(output_root or DEFAULT_OUTPUT_ROOTS[0]).expanduser()
    if root.exists():
        writable = root.is_dir() and os.access(root, os.W_OK)
        detail = str(root)
    else:
        parent = root.parent
        writable = parent.exists() and os.access(parent, os.W_OK)
        detail = f"{root} (ausente; pai gravavel: {parent})"
    checks.append({"name": "output_root", "ok": writable, "detail": detail})
    return {
        "schema": "capsule_cinema.doctor.v1",
        "ok": all(check["ok"] for check in checks),
        "checks": checks,
        "verification": _verification(),
    }


def _validate_capsule(path):
    candidate = Path(path).expanduser()
    if not candidate.is_file():
        raise CapsuleCinemaError(f"capsula nao encontrada: {candidate}")
    if candidate.suffix.lower() not in CAPSULE_SUFFIXES:
        raise CapsuleCinemaError(
            f"extensao de capsula nao reconhecida: {candidate.suffix!r} "
            f"(aceitas: {', '.join(sorted(CAPSULE_SUFFIXES))})"
        )
    return candidate.resolve()


def _validate_output(path, roots):
    target = Path(path).expanduser().resolve()
    for root in roots:
        root_resolved = Path(root).expanduser().resolve()
        if target == root_resolved or root_resolved in target.parents:
            return target
    raise CapsuleCinemaError(
        f"diretorio de saida fora das raizes autorizadas: {target} "
        f"(autorizadas: {', '.join(str(root) for root in roots)})"
    )


def _prepare_output(path, overwrite):
    if path.exists():
        if not path.is_dir():
            raise CapsuleCinemaError(f"saida existe e nao eh diretorio: {path}")
        if any(path.iterdir()) and not overwrite:
            raise CapsuleCinemaError(
                f"diretorio de saida nao vazio: {path}; use --overwrite para permitir"
            )
        return
    path.mkdir(parents=True, exist_ok=True)


def _build_argv(cli, capsule, out, *, extra_args=None):
    argv = [str(cli), "decompose", str(capsule), "-o", str(out)]
    for argument in (extra_args or ()):
        if argument in FORBIDDEN_COMMANDS:
            raise CapsuleCinemaBlocked(f"comando bloqueado em extra_args: {argument}")
        if argument in FORBIDDEN_EXTRA_ARGS:
            raise CapsuleCinemaBlocked(
                f"argumento bloqueado em extra_args: {argument} (segredos nao sao repassados)"
            )
        argv.append(argument)
    return argv


def _artifact_inventory(path):
    files = {}
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
    capsule,
    out,
    *,
    cli=None,
    dry_run=False,
    yes=False,
    overwrite=False,
    timeout=1800.0,
    allowed_output_roots=None,
    env_passthrough=None,
):
    cli_path = find_cli(cli)
    if cli_path is None:
        raise CapsuleCinemaUnavailable(
            "capsule-cinema nao encontrado; instale com o operador ou defina CAPSULE_CINEMA_BIN"
        )
    capsule_path = _validate_capsule(capsule)
    roots = (
        list(allowed_output_roots) if allowed_output_roots is not None else list(DEFAULT_OUTPUT_ROOTS)
    )
    out_path = _validate_output(out, roots)
    argv = _build_argv(cli_path, capsule_path, out_path, extra_args=())

    result = {
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
            "decompose exige consentimento explicito (--yes); use --dry-run para revisar"
        )
    _prepare_output(out_path, overwrite)
    env = {key: os.environ[key] for key in SAFE_ENV_KEYS if key in os.environ}
    for key in (env_passthrough or ()):
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
        raise RuntimeError(f"timeout apos {timeout}s ao executar capsule-cinema") from error
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


def summary(capsule):
    path = Path(capsule).expanduser()
    if not path.is_file():
        raise CapsuleCinemaError(f"capsula nao encontrada: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CapsuleCinemaError(f"capsula invalida: {error}") from error
    shots = data.get("shots") if isinstance(data, dict) else None
    if not isinstance(shots, list):
        shots = []
    types = Counter()
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


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Adaptador somente leitura do capsule-cinema")
    sub = parser.add_subparsers(dest="command", required=True)
    status_p = sub.add_parser("status", help="estado do binario")
    status_p.add_argument("--cli")
    doctor_p = sub.add_parser("doctor", help="checagens de ambiente")
    doctor_p.add_argument("--cli")
    doctor_p.add_argument("--output-root")
    decompose_p = sub.add_parser("decompose", help="analisa uma capsula")
    decompose_p.add_argument("capsule")
    decompose_p.add_argument("--out", required=True)
    decompose_p.add_argument("--cli")
    decompose_p.add_argument("--dry-run", action="store_true")
    decompose_p.add_argument("--yes", action="store_true")
    decompose_p.add_argument("--overwrite", action="store_true")
    decompose_p.add_argument("--timeout", type=float, default=1800.0)
    summary_p = sub.add_parser("summary", help="resume manifest.json")
    summary_p.add_argument("capsule")
    remake_p = sub.add_parser("remake-run", help="bloqueado por politica")
    remake_p.add_argument("args", nargs="*")
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
                "remake-run bloqueado: a operacao chama provedores pagos e nao eh exposta "
                "pelo Core. Execute manualmente com autorizacao e orcamento explicitos."
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
