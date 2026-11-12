# -*- coding: utf-8 -*-
"""Adaptador somente leitura para o `rea-video` (SPEC-935-R1116).

O adaptador lê um vídeo local e escreve apenas em um diretório de saída
explicitamente autorizado. Ele **não** instala o rea-video, **não** baixa
modelos e **não** expõe comandos pagos (`remake-run`, `remake-plan`,
`capsule-draft`, `assemble`).

Uso:
    python3 -m integrations.rea_video_cli status
    python3 -m integrations.rea_video_cli doctor
    python3 -m integrations.rea_video_cli decompose clip.mp4 --out out/clip --dry-run
    python3 -m integrations.rea_video_cli decompose clip.mp4 --out out/clip --yes
    python3 -m integrations.rea_video_cli summary out/clip/breakdown.json
"""

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

VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
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
    "capsule-draft",
    "assemble",
    "capsule",
    "remake",
}
FORBIDDEN_EXTRA_ARGS = {"--env-file"}


class ReaVideoError(RuntimeError):
    """Falha controlada do adaptador."""


class ReaVideoUnavailable(ReaVideoError):
    """O binário rea-video não foi encontrado."""


class ReaVideoBlocked(ReaVideoError):
    """Operação bloqueada por política (pagamento, consentimento ou escopo)."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verification() -> dict[str, Any]:
    return {
        "scope": "local_observation",
        "externally_validated": False,
        "confidence_promoted": False,
    }


def find_cli(explicit: str | Path | None = None) -> Path | None:
    """Localiza o binário: argumento > REA_VIDEO_BIN > PATH."""
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(Path(explicit).expanduser())
    env_value = os.environ.get("REA_VIDEO_BIN")
    if env_value:
        candidates.append(Path(env_value).expanduser())
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
        raise ReaVideoUnavailable(
            f"binário rea-video inválido ou não executável: {candidate}"
        )
    found = shutil.which("rea-video")
    return Path(found).resolve() if found else None


def status(
    explicit: str | Path | None = None,
    *,
    run_help: bool = True,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Estado do binário. Não escreve no disco; lê apenas `--help`."""
    base: dict[str, Any] = {
        "schema": "rea_video.status.v1",
        "available": False,
        "path": None,
        "help_exit_code": None,
        "help_first_line": None,
        "verification": _verification(),
    }
    try:
        cli = find_cli(explicit)
    except ReaVideoUnavailable as error:
        base["error"] = str(error)
        return base
    if cli is None:
        base["error"] = "rea-video não encontrado no PATH nem em REA_VIDEO_BIN"
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
    explicit: str | Path | None = None, *, output_root: str | Path | None = None
) -> dict[str, Any]:
    """Confere binário, ffmpeg, ffprobe e escrita no diretório de saída."""
    checks: list[dict[str, Any]] = []
    try:
        cli = find_cli(explicit)
    except ReaVideoUnavailable as error:
        cli = None
        checks.append({"name": "cli", "ok": False, "detail": str(error)})
    else:
        checks.append(
            {
                "name": "cli",
                "ok": cli is not None,
                "detail": str(cli) if cli else "não encontrado",
            }
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
        "schema": "rea_video.doctor.v1",
        "ok": all(check["ok"] for check in checks),
        "checks": checks,
        "verification": _verification(),
    }


def _validate_video(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.is_file():
        raise ReaVideoError(f"vídeo não encontrado: {candidate}")
    if candidate.suffix.lower() not in VIDEO_SUFFIXES:
        raise ReaVideoError(
            f"extensão de vídeo não reconhecida: {candidate.suffix!r} "
            f"(aceitas: {', '.join(sorted(VIDEO_SUFFIXES))})"
        )
    return candidate.resolve()


def _validate_output(path: str | Path, roots: Sequence[str | Path]) -> Path:
    target = Path(path).expanduser().resolve()
    for root in roots:
        root_resolved = Path(root).expanduser().resolve()
        if target == root_resolved or root_resolved in target.parents:
            return target
    raise ReaVideoError(
        f"diretório de saída fora das raízes autorizadas: {target} "
        f"(autorizadas: {', '.join(str(root) for root in roots)})"
    )


def _prepare_output(path: Path, overwrite: bool) -> None:
    if path.exists():
        if not path.is_dir():
            raise ReaVideoError(f"saída existe e não é diretório: {path}")
        if any(path.iterdir()) and not overwrite:
            raise ReaVideoError(
                f"diretório de saída não vazio: {path}; use --overwrite para permitir"
            )
        return
    path.mkdir(parents=True, exist_ok=True)


def _build_argv(
    cli: Path,
    video: Path,
    out: Path,
    *,
    vlm: bool,
    lang: str | None,
    extra_args: Sequence[str] | None,
) -> list[str]:
    argv = [str(cli), "decompose", str(video), "-o", str(out)]
    if vlm:
        argv.append("--vlm")
    if lang:
        argv.extend(["--lang", lang])
    for argument in extra_args or ():
        if argument in FORBIDDEN_COMMANDS:
            raise ReaVideoBlocked(f"comando bloqueado em extra_args: {argument}")
        if argument in FORBIDDEN_EXTRA_ARGS:
            raise ReaVideoBlocked(
                f"argumento bloqueado em extra_args: {argument} (segredos não são repassados)"
            )
        argv.append(argument)
    return argv


def _artifact_inventory(path: Path) -> dict[str, Any]:
    files: dict[str, Any] = {}
    for name in (
        "VIDEO.md",
        "breakdown.json",
        "report.html",
        "report.md",
        "storyboard.jpg",
        "audio.png",
        "capsule_analysis.json",
    ):
        candidate = path / name
        if candidate.is_file():
            files[name] = {
                "bytes": candidate.stat().st_size,
                "sha256": _sha256(candidate),
            }
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
    video: str | Path,
    out: str | Path,
    *,
    cli: str | Path | None = None,
    dry_run: bool = False,
    yes: bool = False,
    overwrite: bool = False,
    timeout: float = 1800.0,
    vlm: bool = False,
    lang: str | None = None,
    extra_args: Sequence[str] | None = None,
    allowed_output_roots: Sequence[str | Path] | None = None,
    env_passthrough: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Executa `rea-video decompose` com consentimento e saída autorizada.

    ``dry_run`` não cria diretório nem executa o binário. Sem ``yes``, a
    execução é bloqueada. O vídeo de entrada nunca é modificado.
    """
    cli_path = find_cli(cli)
    if cli_path is None:
        raise ReaVideoUnavailable(
            "rea-video não encontrado; instale com o operador ou defina REA_VIDEO_BIN"
        )

    video_path = _validate_video(video)
    roots = (
        list(allowed_output_roots)
        if allowed_output_roots is not None
        else list(DEFAULT_OUTPUT_ROOTS)
    )
    out_path = _validate_output(out, roots)
    argv = _build_argv(
        cli_path, video_path, out_path, vlm=vlm, lang=lang, extra_args=extra_args
    )

    result: dict[str, Any] = {
        "schema": "rea_video.decompose.v1",
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
        raise ReaVideoBlocked(
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
        raise ReaVideoError(
            f"timeout após {timeout}s ao executar rea-video"
        ) from error
    except OSError as error:
        raise ReaVideoError(f"falha ao executar rea-video: {error}") from error

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


def summary(breakdown: str | Path) -> dict[str, Any]:
    """Lê `breakdown.json` e resume shots, tipos e baixa confiança."""
    path = Path(breakdown).expanduser()
    if not path.is_file():
        raise ReaVideoError(f"breakdown não encontrado: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReaVideoError(f"breakdown inválido: {error}") from error

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
        "schema": "rea_video.summary.v1",
        "source": str(path),
        "source_sha256": _sha256(path),
        "top_level_keys": sorted(data.keys()) if isinstance(data, dict) else [],
        "shot_count": len(shots),
        "low_confidence_count": low_confidence,
        "types": dict(sorted(types.items())),
        "verification": _verification(),
    }


def remake_run(*_args: Any, **_kwargs: Any) -> None:
    """Comando pago: bloqueado por política."""
    raise ReaVideoBlocked(
        "remake-run bloqueado: a operação chama provedores pagos e não é exposta "
        "pelo Core. Execute manualmente com autorização e orçamento explícitos."
    )


def _print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Adaptador somente leitura do rea-video"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    status_parser = sub.add_parser("status", help="estado do binário")
    status_parser.add_argument("--cli")

    doctor_parser = sub.add_parser("doctor", help="checagens de ambiente")
    doctor_parser.add_argument("--cli")
    doctor_parser.add_argument("--output-root")

    decompose_parser = sub.add_parser("decompose", help="analisa um vídeo")
    decompose_parser.add_argument("video")
    decompose_parser.add_argument("--out", required=True)
    decompose_parser.add_argument("--cli")
    decompose_parser.add_argument("--dry-run", action="store_true")
    decompose_parser.add_argument("--yes", action="store_true")
    decompose_parser.add_argument("--overwrite", action="store_true")
    decompose_parser.add_argument("--timeout", type=float, default=1800.0)
    decompose_parser.add_argument("--vlm", action="store_true")
    decompose_parser.add_argument("--lang", choices=("zh", "en"))
    decompose_parser.add_argument("--extra", action="append", default=[])

    summary_parser = sub.add_parser("summary", help="resume breakdown.json")
    summary_parser.add_argument("breakdown")

    remake_parser = sub.add_parser("remake-run", help="bloqueado por política")
    remake_parser.add_argument("args", nargs="*")

    args = parser.parse_args(argv)

    try:
        if args.command == "status":
            _print(status(args.cli))
            return 0

        if args.command == "doctor":
            _print(doctor(args.cli, output_root=args.output_root))
            return 0

        if args.command == "decompose":
            _print(
                decompose(
                    args.video,
                    args.out,
                    cli=args.cli,
                    dry_run=args.dry_run,
                    yes=args.yes,
                    overwrite=args.overwrite,
                    timeout=args.timeout,
                    vlm=args.vlm,
                    lang=args.lang,
                    extra_args=args.extra,
                )
            )
            return 0

        if args.command == "summary":
            _print(summary(args.breakdown))
            return 0

        if args.command == "remake-run":
            remake_run()
            return 0
    except ReaVideoBlocked as error:
        _print({"ok": False, "blocked": True, "error": str(error)})
        return 2
    except ReaVideoError as error:
        _print({"ok": False, "error": str(error)})
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
