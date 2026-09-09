"""Entrada nativa do Pesquisador Universal v4.1 dentro do Core.

Uso:
    python -m marceloclaro.scientific_lab status
    python -m marceloclaro.scientific_lab doctor
    python -m marceloclaro.scientific_lab research harvest "tema" --workspace .
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from scientific_lab import restricted_resolver
from scientific_lab.runtime import core_compatibility, dispatch, installed_status

HELP = """Pesquisador Universal v4.1 — bridge do OpenCode Ecosystem Core

Comandos:
  status       mostra discovery, versão e verificação do release instalado
  core-check   verifica componentes estruturais do Core hospedeiro
  doctor       exige Core compatível + release científico v4.1 verificado
  research/articles, mesh, mission, review, living, synthesis, grade,
  causal, federation, production

Subcomando opt-in (R470, desabilitado por omissão):
  restricted --help   explica os gates de autorização (sem rede, sem execução)

Variável opcional:
  PESQUISADOR_UNIVERSAL_HOME=/caminho/para/skill
"""

RESTRICTED_HELP = """Resolvedor de acesso restrito — opt-in auditável R470 (desabilitado por omissão)

Padrão preservado: open_science_only. Nenhum fallback automático para restrito.
Gates cumulativos (esta ordem; qualquer falha nega com recibo auditável):
  1. habilitação: --enable-restricted-resolver + RESTRICTED_RESOLVER_ENABLED=1
  2. política: RESTRICTED_RESOLVER_POLICY=deny|ask|allow (omissão deny)
  3. allowlist: --resolver <nome> presente em RESTRICTED_RESOLVER_ALLOWLIST
  4. autorização humana: --authorize <id> ou RESTRICTED_RESOLVER_AUTHORIZATION_ID
  5. base legal declarada: --rights-basis "<texto>" (registrada, não validada)
  6. evidência referenciada: --evidence-ref "<ref>" (sem conteúdo protegido)
  7. política ask exige ainda --confirm adicional.

Tentativas negadas imprimem recibo JSON de negação; nada é executado nem
baixado por esta fachada (caminho autorizado retorna pending_manual_execution).
Isto não é aconselhamento jurídico. Ver SPEC-935-R470 e SECURITY.md.
"""


def _flag_value(args: list[str], *names: str) -> str | None:
    for name in names:
        if name in args:
            idx = args.index(name)
            if idx + 1 < len(args) and not args[idx + 1].startswith("--"):
                return args[idx + 1]
            return None
    return "__absent__"  # type: ignore[return-value]


def _handle_restricted(rest: list[str]) -> int:
    if any(item in {"-h", "--help", "help"} for item in rest):
        print(RESTRICTED_HELP)
        return 0
    parsed_resolver = _flag_value(rest, "--resolver")
    parsed_auth = _flag_value(rest, "--authorize")
    parsed_rights = _flag_value(rest, "--rights-basis")
    parsed_evidence = _flag_value(rest, "--evidence-ref")
    flag_enable = "--enable-restricted-resolver" in rest
    confirm = "--confirm" in rest
    request = restricted_resolver.request_from_env(
        resolver=None if parsed_resolver == "__absent__" else parsed_resolver,
        confirm=confirm,
    )
    # Habilitação exige flag E ambiente (camadas cumulativas, fail-closed).
    request.enable = bool(flag_enable) and bool(request.enable)
    if parsed_resolver != "__absent__":
        request.resolver = parsed_resolver
    if parsed_auth != "__absent__":
        request.authorization_id = parsed_auth
    if parsed_rights != "__absent__":
        request.rights_basis = parsed_rights
    if parsed_evidence != "__absent__":
        request.evidence_ref = parsed_evidence
    request.confirm = confirm
    exit_code, cli_receipt, download_receipt = restricted_resolver.dispatch_restricted(request)
    print(json.dumps(
        {"exit_code": exit_code, "receipt": cli_receipt, "download": download_receipt},
        ensure_ascii=False,
        indent=2,
    ))
    return exit_code


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run_validation(home: Path) -> int:
    import subprocess
    codes = []
    for name in ("validate_contracts.py", "validate_ecosystem.py"):
        codes.append(subprocess.call([sys.executable, str(home / "scripts" / name)]))
    return 0 if all(code == 0 for code in codes) else max(codes)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help", "help"}:
        print(HELP)
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "status":
        print(json.dumps(installed_status(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "core-check":
        report = core_compatibility(_repo_root())
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["compatible"] else 3
    if cmd == "doctor":
        core = core_compatibility(_repo_root())
        status = installed_status()
        result = {"core": core, "scientific_layer": status}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not core["compatible"]:
            return 3
        if not status.get("verified_release"):
            return 5 if status["status"] != "not_installed" else 4
        return _run_validation(Path(status["home"]))
    if cmd == "restricted":
        return _handle_restricted(rest)
    return dispatch(cmd, rest)


if __name__ == "__main__":
    raise SystemExit(main())
