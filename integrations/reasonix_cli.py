# -*- coding: utf-8 -*-
"""Integração Reasonix (DeepSeek-Reasonix) — SPEC-935-R602.

Reasonix é um agente de codificação DeepSeek-native (MIT) orquestrável no modo
one-shot `run` (pipes) e `doctor` (health check). A linha ativa é o rewrite Go
(v2, instalado via `npm install -g reasonix`).

Nunca lança exceções no caminho de orquestração; falhas viram dicts com ok=False.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from typing import Optional

_BIN_CACHE: Optional[str] = None
_AVAILABLE_CACHE: Optional[bool] = None
_SEMVER_RE = re.compile(r"(\d+\.\d+\.\d+(?:[-\w.]+)?)")


def _find_binary() -> Optional[str]:
    """Localiza o binário reasonix (ou alias dsnix) no PATH."""
    global _BIN_CACHE, _AVAILABLE_CACHE
    if _BIN_CACHE is not None:
        return _BIN_CACHE or None
    for name in ("reasonix", "dsnix"):
        path = shutil.which(name)
        if path:
            _BIN_CACHE = path
            _AVAILABLE_CACHE = True
            return path
    _BIN_CACHE = ""  # cache de ausência ("") — nunca "None" para evitar re-consulta
    _AVAILABLE_CACHE = False
    return None


def reasonix_available() -> bool:
    return bool(_find_binary())


def reasonix_version() -> Optional[str]:
    """Versão semver via `reasonix --version` (tolerante)."""
    binary = _find_binary()
    if not binary:
        return None
    try:
        proc = subprocess.run(
            [binary, "--version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        saida = proc.stdout or proc.stderr
        match = _SEMVER_RE.search(saida)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def reasonix_run(
    task: str,
    directory: Optional[str] = None,
    timeout: int = 180,
) -> dict:
    """Executa `reasonix run "<task>"` (one-shot). Nunca lança.

    Retorna dict com: ok, returncode, stdout, stderr, comando, timed_out.
    Sem DeepSeek API key o run real retorna não-zero (auth) — comportamento
    esperado, documentado na especificação.
    """
    binary = _find_binary()
    if not binary:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": "reasonix não instalado. Rode `npm install -g reasonix` "
                      "(detalhes: reasonix_cli.install_instructions()).",
            "comando": [],
            "timed_out": False,
        }
    comando = [binary]
    if directory:
        comando += ["--dir", directory]
    comando += ["run", task]
    try:
        proc = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "comando": comando,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"reasonix run excedeu o timeout de {timeout}s.",
            "comando": comando,
            "timed_out": True,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "comando": comando,
            "timed_out": False,
        }


def doctor_check() -> dict:
    """Health check estilo doctor global: pass/warn (nunca fail)."""
    binary = _find_binary()
    if not binary:
        return {
            "name": "reasonix",
            "status": "warn",
            "detail": "não instalado — npm install -g reasonix",
        }
    try:
        proc = subprocess.run(
            [binary, "doctor"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        versao = reasonix_version() or "desconhecida"
        if proc.returncode == 0:
            return {
                "name": "reasonix",
                "status": "pass",
                "detail": f"v{versao} — doctor ok",
            }
        return {
            "name": "reasonix",
            "status": "warn",
            "detail": f"v{versao} — doctor exit {proc.returncode} "
                      f"(provavelmente falta chave DeepSeek): "
                      f"{(proc.stderr or proc.stdout).strip()[:120]}",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "name": "reasonix",
            "status": "warn",
            "detail": f"erro ao rodar doctor: {exc}",
        }


def install_instructions() -> str:
    return (
        "Instalação Reasonix (DeepSeek-Reasonix, MIT):\n"
        "  1. npm install -g reasonix          # binário nativo Go (v2) + alias dsnix\n"
        "     # alternativa one-shot: npx reasonix@latest run \"tarefa\"\n"
        "  2. reasonix setup                   # colar DeepSeek API key (persistida)\n"
        "     # key: https://platform.deepseek.com/api_keys\n"
        "  3. reasonix doctor                  # health check (Node, key, MCP)\n"
        "  4. reasonix run \"sua tarefa\"        # one-shot (pipes)\n"
        "Requisitos: Node >= 22 (instalado). License MIT.\n"
    )


# ---------------------------------------------------------------------------
# CLI orquestrada (comando /reasonix)
# ---------------------------------------------------------------------------

_USO = """\
Uso: python -m integrations.reasonix_cli SUBCOMANDO [OPCOES]

Subcomandos:
  status              Binário, versão e disponibilidade
  run <prompt>        One-shot: reasonix run "<prompt>"
  doctor              Health check (Node, API key, MCP)
  install             Instruções de instalação (npm/npx + API key)
  setup               Instruções de configuração (provider/modelo)
  --help              Esta ajuda

Opções de run:
  --timeout SEG       Timeout em segundos (padrão 180)

Exemplos:
  python -m integrations.reasonix_cli run "implemente os TODOs do main.py"
  python -m integrations.reasonix_cli doctor
"""


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv[0] in ("--help", "-h"):
        print(_USO)
        return 0

    sub = argv[0]
    if sub == "status":
        binary = _find_binary()
        versao = reasonix_version()
        if not binary:
            print("reasonix: NÃO INSTALADO")
            print(install_instructions())
            return 1
        print(f"reasonix: disponível  binário={binary}")
        print(f"reasonix: versão      {versao or 'desconhecida'}")
        return 0

    if sub in ("install", "setup"):
        print(install_instructions())
        if sub == "setup":
            print(
                "  Depois de instalar, rode `reasonix setup` no seu terminal e\n"
                "  cole a DeepSeek API key (https://platform.deepseek.com/api_keys)."
            )
        return 0

    if sub == "run":
        if len(argv) < 2:
            print("Erro: `run` exige um prompt.", file=sys.stderr)
            return 2
        prompt = argv[1]
        timeout = 180
        resto = argv[2:]
        if resto:
            if resto[0] == "--timeout" and len(resto) >= 2:
                try:
                    timeout = int(resto[1])
                except ValueError:
                    print("Erro: --timeout deve ser inteiro.", file=sys.stderr)
                    return 2
            else:
                print(f"Erro: opção desconhecida {resto[0]}", file=sys.stderr)
                return 2
        resultado = reasonix_run(prompt, timeout=timeout)
        if resultado["stdout"]:
            print(resultado["stdout"], end="")
        if resultado["stderr"]:
            print(resultado["stderr"], end="", file=sys.stderr)
        if not resultado["ok"]:
            return 1
        return 0

    if sub == "doctor":
        check = doctor_check()
        print(f"{check['name']}: {check['status']} — {check['detail']}")
        return 0 if check["status"] == "pass" else 1

    print(f"Erro: subcomando desconhecido: {sub}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())