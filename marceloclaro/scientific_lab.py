"""Entrada nativa do Pesquisador Universal v4.1 dentro do Core.

Uso:
    python -m marceloclaro.scientific_lab status
    python -m marceloclaro.scientific_lab doctor
    python -m marceloclaro.scientific_lab research harvest "tema" --workspace .
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from scientific_lab.runtime import core_compatibility, dispatch, installed_status

HELP = """Pesquisador Universal v4.1 — bridge do OpenCode Ecosystem Core

Comandos:
  status       mostra discovery/versionamento da supercamada
  core-check   verifica componentes estruturais do Core hospedeiro
  doctor       executa core-check e, se instalada, valida contratos/estrutura v4.1
  research/articles, mesh, mission, review, living, synthesis, grade,
  causal, federation, production

Variável opcional:
  PESQUISADOR_UNIVERSAL_HOME=/caminho/para/skill
"""


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
        if status["status"] != "installed":
            return 4
        return _run_validation(Path(status["home"]))
    return dispatch(cmd, rest)


if __name__ == "__main__":
    raise SystemExit(main())
