"""CLI do Book Studio Universal (fase R1078)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .contracts import load_project
from .kdp import KDPError, kdp_cover_spec
from .license_gate import LicenseViolation, validate_landscape
from .release import ReleaseError, ReleaseManifest
from .tokens import default_tokens

__version__ = "0.1.0"


def _print(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _cmd_kdp(args: argparse.Namespace) -> int:
    spec = kdp_cover_spec(
        args.trim, args.pages, paper=args.paper, ink=args.ink,
        bleed_in=args.bleed, safe_margin_in=args.safe_margin,
    )
    _print(spec.to_dict())
    return 0


def _cmd_tokens(_: argparse.Namespace) -> int:
    tokens = default_tokens()
    _print(tokens.to_dict())
    return 0 if tokens.valid else 1


def _cmd_license(args: argparse.Namespace) -> int:
    result = validate_landscape(args.manifest)
    _print(result)
    return 0 if result["status"] == "ok" else 1


def _cmd_manifest_build(args: argparse.Namespace) -> int:
    manifest = ReleaseManifest.build(
        args.release, args.files, root=args.root, kind=args.kind,
        metadata={"note": args.note} if args.note else None,
        tool_versions={"bookstudio": __version__},
    )
    target = manifest.save(args.out)
    payload = manifest.to_dict()
    payload["saved_to"] = str(target)
    payload["verify"] = manifest.verify(args.root)
    _print(payload)
    return 0 if payload["verify"]["ok"] else 1


def _cmd_manifest_verify(args: argparse.Namespace) -> int:
    manifest = ReleaseManifest.load(args.manifest)
    result = manifest.verify(args.root)
    _print(result)
    return 0 if result["ok"] else 1


def _cmd_project_validate(args: argparse.Namespace) -> int:
    project = load_project(args.project)
    payload = {
        "project": str(Path(args.project).expanduser().resolve()),
        "ok": project.ok,
        "issues": project.validate(),
        "kdp": project.kdp_spec().to_dict() if project.ok else None,
    }
    if payload["kdp"] is None:
        try:
            payload["kdp"] = project.kdp_spec().to_dict()
        except (KDPError, ValueError) as exc:
            payload["kdp"] = {"error": str(exc)}
    _print(payload)
    return 0 if project.ok else 1


def _cmd_status(_: argparse.Namespace) -> int:
    _print({
        "status": "ready",
        "version": __version__,
        "scope": "R1078 — contratos, KDP, design tokens, licença e release",
        "kdp_formula": "page_count x paper_thickness; capa = 2*bleed + 2*trim + spine",
        "external_validation": False,
        "limitations": [
            "Não calcula arte, prova física ou aprovação KDP.",
            "A lista de trims é conservadora; confirmar no previewer.",
            "Nenhum PDF/UA, EPUB ou build é executado por este CLI.",
        ],
    })
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bookstudio",
        description="Book Studio Universal — fase R1078",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    kdp = sub.add_parser("kdp", help="calcula capa, lombada e bleed")
    kdp.add_argument("--pages", type=int, required=True)
    kdp.add_argument("--trim", default="6x9in")
    kdp.add_argument("--paper", choices=("white", "cream"), default="cream")
    kdp.add_argument("--ink", choices=("bw", "standard_color", "premium_color"), default="bw")
    kdp.add_argument("--bleed", type=float, default=0.125)
    kdp.add_argument("--safe-margin", type=float, default=0.25)
    kdp.set_defaults(func=_cmd_kdp)

    tokens = sub.add_parser("tokens", help="valida paleta, contraste e TAC")
    tokens.set_defaults(func=_cmd_tokens)

    license_cmd = sub.add_parser("license", help="valida o gate de licença")
    license_cmd.add_argument("manifest")
    license_cmd.set_defaults(func=_cmd_license)

    manifest = sub.add_parser("manifest", help="manifesto de release")
    manifest_sub = manifest.add_subparsers(dest="manifest_command", required=True)
    build = manifest_sub.add_parser("build")
    build.add_argument("--release", required=True)
    build.add_argument("--out", required=True)
    build.add_argument("--root")
    build.add_argument("--kind", default="artifact")
    build.add_argument("--note")
    build.add_argument("files", nargs="+")
    build.set_defaults(func=_cmd_manifest_build)
    verify = manifest_sub.add_parser("verify")
    verify.add_argument("--manifest", required=True)
    verify.add_argument("--root")
    verify.set_defaults(func=_cmd_manifest_verify)

    project = sub.add_parser("project", help="contrato de projeto")
    project_sub = project.add_subparsers(dest="project_command", required=True)
    validate = project_sub.add_parser("validate")
    validate.add_argument("project")
    validate.set_defaults(func=_cmd_project_validate)

    status = sub.add_parser("status")
    status.set_defaults(func=_cmd_status)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (KDPError, ReleaseError, LicenseViolation, ValueError, OSError) as exc:
        _print({"status": "blocked", "error": str(exc), "executed": False})
        return 2


if __name__ == "__main__":
    sys.exit(main())
