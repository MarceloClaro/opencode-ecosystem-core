# -*- coding: utf-8 -*-
"""
Integração Google Colab CLI (SPEC-935-R645) — executor externo orquestrável.

Repositórios: MarceloClaro/google-colab-cli (fork de googlecolab/google-colab-cli,
Apache-2.0) + MarceloClaro/colab-mcp (fork de googlecolab/colab-mcp).
Entry point: `colab`

Fluxo terminal/headless (fonte: README oficial googlecolab/google-colab-cli):
    colab new [-s NAME] [--gpu GPU] [--tpu TPU] [--high-mem]
    echo 'print("Hi")' | colab exec [-s NAME]
    colab run [--gpu GPU] [--tpu TPU] [--high-mem] [--keep] SCRIPT [ARGS...]
    colab stop [-s NAME]

Autenticação: --auth {oauth2,adc}; metadados em ~/.config/colab-cli/.
Suporte: Linux e macOS apenas. Windows NÃO suportado.
GPU/TPU e --high-mem exigem direito Colab Pro/Pro+ e consomem compute units.

A execução é EXTERNA ao Core: o orquestrador marceloclaro permanece dono do
ciclo SDD/TDD; resultados nunca são "verificados" sem validação (R110).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from typing import Dict, List, Optional

_BIN_NAME = "colab"
_SEMVER_RE = r"(\d+(?:\.\d+){1,3}(?:[-+][0-9A-Za-z.-]+)?)"
_BIN_CACHE: Optional[str] = None
_AVAILABLE_CACHE: Optional[bool] = None

COLAB_INSTALL_UV = "uv tool install google-colab-cli"
COLAB_INSTALL_PIP = "pip install google-colab-cli"


def _find_binary() -> Optional[str]:
    """Caminho do binário `colab`, com cache por sessão (None se ausente)."""
    global _BIN_CACHE
    if _BIN_CACHE is None:
        _BIN_CACHE = shutil.which(_BIN_NAME)
    return _BIN_CACHE


def colab_available() -> bool:
    """True se o binário `colab` estiver no PATH."""
    global _AVAILABLE_CACHE
    if _AVAILABLE_CACHE is None:
        _AVAILABLE_CACHE = _find_binary() is not None
    return _AVAILABLE_CACHE


def colab_version() -> Optional[str]:
    """Versão semântica via `colab version` (None se ausente/falha).

    Extrai apenas o número (ex.: "colab, version 0.3.1" → "0.3.1").
    """
    binary = _find_binary()
    if binary is None:
        return None
    try:
        proc = subprocess.run(
            [binary, "version"], capture_output=True, text=True,
            timeout=15, check=False,
        )
        combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
        match = re.search(_SEMVER_RE, combined)
        return match.group(1) if match else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def colab_run_args(
    args: List[str],
    timeout: int = 300,
    stdin_text: Optional[str] = None,
) -> Dict[str, object]:
    """Executa `colab <args>` e retorna dict estável — nunca lança exceção.

    `args` é a lista após o binário (ex.: ["sessions"], ["exec", "-f", "t.py"]).
    Usa lista (sem shell) para auditabilidade. `stdin_text` alimenta stdin
    (equivale a `echo ... | colab exec`).
    Retorna {ok, returncode, stdout, stderr, timeout(bool), version, comando(str)}.
    """
    binary = _find_binary()
    if binary is None:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": "Colab CLI não instalado. Execute /colab install.",
            "timeout": False,
            "version": None,
            "comando": None,
        }
    cmd: List[str] = [binary] + list(args)
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            input=stdin_text, timeout=timeout, check=False,
        )
        returncode = int(proc.returncode)
        return {
            "ok": returncode == 0,
            "returncode": returncode,
            "stdout": (proc.stdout or ""),
            "stderr": (proc.stderr or ""),
            "timeout": False,
            "version": colab_version(),
            "comando": " ".join(cmd),
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"colab {' '.join(args)} excedeu o limite de {timeout}s.",
            "timeout": True,
            "version": colab_version(),
            "comando": " ".join(cmd),
        }
    except OSError as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"Falha ao invocar colab: {exc}",
            "timeout": False,
            "version": None,
            "comando": " ".join(cmd),
        }


def colab_new(
    session: Optional[str] = None,
    gpu: Optional[str] = None,
    tpu: Optional[str] = None,
    high_mem: bool = False,
    timeout: int = 300,
) -> Dict[str, object]:
    """Atalho para `colab new [-s NAME] [--gpu GPU] [--tpu TPU] [--high-mem]`."""
    args = ["new"]
    if session:
        args += ["-s", session]
    if gpu:
        args += ["--gpu", gpu]
    if tpu:
        args += ["--tpu", tpu]
    if high_mem:
        args.append("--high-mem")
    return colab_run_args(args, timeout=timeout)


def colab_exec(
    session: Optional[str] = None,
    file: Optional[str] = None,
    stdin_text: Optional[str] = None,
    output_image: Optional[str] = None,
    timeout: int = 300,
) -> Dict[str, object]:
    """Atalho para `colab exec [-s NAME] [-f FILE] [--output-image PATH]`."""
    args = ["exec"]
    if session:
        args += ["-s", session]
    if file:
        args += ["-f", file]
    if output_image:
        args += ["--output-image", output_image]
    return colab_run_args(args, timeout=timeout, stdin_text=stdin_text)


def colab_run_script(
    script: str,
    script_args: Optional[List[str]] = None,
    gpu: Optional[str] = None,
    tpu: Optional[str] = None,
    high_mem: bool = False,
    keep: bool = False,
    timeout: int = 600,
) -> Dict[str, object]:
    """Atalho para `colab run [--gpu ..] [--tpu ..] [--high-mem] [--keep] SCRIPT [ARGS...]`."""
    args = ["run"]
    if gpu:
        args += ["--gpu", gpu]
    if tpu:
        args += ["--tpu", tpu]
    if high_mem:
        args.append("--high-mem")
    if keep:
        args.append("--keep")
    args.append(script)
    if script_args:
        args += list(script_args)
    return colab_run_args(args, timeout=timeout)


def colab_stop(
    session: Optional[str] = None, timeout: int = 120,
) -> Dict[str, object]:
    """Atalho para `colab stop [-s NAME]`."""
    args = ["stop"] + (["-s", session] if session else [])
    return colab_run_args(args, timeout=timeout)


def colab_sessions(timeout: int = 60) -> Dict[str, object]:
    """Atalho para `colab sessions`."""
    return colab_run_args(["sessions"], timeout=timeout)


def doctor_check() -> Dict[str, str]:
    """DoctorCheck no formato do Core (name/status/detail; nunca fail)."""
    version = colab_version()
    if version is not None:
        return {
            "name": "colab",
            "status": "pass",
            "detail": f"Colab CLI instalado (versão {version}). "
            "Executor externo orquestrável via integrations.colab_cli (SPEC-935-R645).",
        }
    if colab_available():
        return {
            "name": "colab",
            "status": "pass",
            "detail": "Colab CLI instalado (versão não detectada). "
            "Executor externo orquestrável via integrations.colab_cli (SPEC-935-R645).",
        }
    return {
        "name": "colab",
        "status": "warn",
        "detail": "Colab CLI ausente (SPEC-935-R645, Linux/macOS apenas). "
        f"Instale com: {COLAB_INSTALL_UV}  (alternativa: {COLAB_INSTALL_PIP}).",
    }


def install_instructions() -> str:
    """Instrução oficial de instalação + autenticação do Colab CLI."""
    return (
        "Instalação oficial do Google Colab CLI (Linux/macOS apenas — Windows NÃO suportado):\n"
        f"  {COLAB_INSTALL_UV}\n"
        f"  # alternativa: {COLAB_INSTALL_PIP}\n"
        "\n"
        "Autenticação (OAuth2 ou ADC; sessões em ~/.config/colab-cli/sessions.json):\n"
        "  colab auth [-s NAME]            # libera GCP (BigQuery, GCS, ...)\n"
        "  colab drivemount [-s NAME]      # monta o Drive em /content/drive\n"
        "  # global: colab --auth {oauth2,adc} ...\n"
        "\n"
        "Uso no Core (fluxo 80/20):\n"
        "  /colab status  |  colab sessions / colab status [-s NOME]\n"
        "  /colab new <nome> [--gpu T4|L4|A100] [--high-mem]\n"
        "  /colab exec -f script.py  |  echo 'print(1)' | colab exec\n"
        "  /colab run --gpu T4 train.py  (efêmero: provisiona → executa → destrói)\n"
        "  colab stop [-s NOME]\n"
        "\n"
        "Custo: GPU/TPU e --high-mem exigem Colab Pro/Pro+ e consomem compute units\n"
        "  (verifique com: colab usage; gerencie em: colab pay)."
    )


def _format_status() -> str:
    available = colab_available()
    version = colab_version()
    versao_json = "null" if version is None else json.dumps(version)
    return "\n".join([
        "{",
        '  "especificacao": "SPEC-935-R645",',
        f'  "disponivel": {str(available).lower()},',
        f'  "versao": {versao_json},',
        '  "binario": "colab",',
        '  "plataforma": "linux/macos (windows nao suportado)",',
        '  "licenca": "Apache-2.0",',
        '  "origem": "https://github.com/googlecolab/google-colab-cli",',
        '  "fork": "https://github.com/MarceloClaro/google-colab-cli",',
        "}",
    ])


def _parse_run_argv(tokens: List[str]) -> Dict[str, object]:
    """Separa `--timeout N` e `--input TEXTO`; o resto é passthrough ao `colab`."""
    parsed: Dict[str, object] = {"passthrough": [], "timeout": 300, "stdin_text": None}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--timeout" and index + 1 < len(tokens):
            try:
                parsed["timeout"] = int(tokens[index + 1])
            except ValueError:
                parsed["timeout"] = 300
            index += 2
            continue
        if token.startswith("--timeout="):
            try:
                parsed["timeout"] = int(token.split("=", 1)[1])
            except ValueError:
                parsed["timeout"] = 300
            index += 1
            continue
        if token == "--input" and index + 1 < len(tokens):
            parsed["stdin_text"] = tokens[index + 1]
            index += 2
            continue
        parsed["passthrough"].append(token)  # type: ignore[attr-defined]
        index += 1
    return parsed


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"--help", "-h", "help"}:
        print(
            "Uso: python3 -m integrations.colab_cli <status|run|new|exec|stop|sessions|doctor|install> [args...]\n"
            "  run [--timeout SEG] [--input TEXTO] <args do colab...>\n"
            "    ex.: run sessions | run status -s trainer | run exec -f train.py\n"
            "  new <nome> [--gpu T4] [--tpu v5e1] [--high-mem]\n"
            "  exec [-s NOME] [-f ARQ] [--output-image IMG] [--input TEXTO]\n"
            "  stop [-s NOME] | sessions\n"
            "  ex.: /colab run --gpu T4 train.py  (via: run run --gpu T4 train.py)"
        )
        return 0
    command, *rest = argv
    if command == "status":
        print(_format_status())
        return 0
    if command == "doctor":
        check = doctor_check()
        print(f"{check['name']}: {check['status']} — {check['detail']}")
        return 0 if check["status"] == "pass" else 1
    if command == "install":
        print(install_instructions())
        return 0
    if command == "sessions":
        result = colab_sessions()
        print(result.get("stdout") or result.get("stderr") or "")
        return 0 if result.get("ok") else 1
    if command == "stop":
        session = None
        toks = list(rest)
        if "-s" in toks:
            idx = toks.index("-s")
            if idx + 1 < len(toks):
                session = toks[idx + 1]
        result = colab_stop(session)
        print(result.get("stdout") or result.get("stderr") or "")
        return 0 if result.get("ok") else 1
    if command == "new":
        session = rest[0] if rest and not rest[0].startswith("-") else None
        extra = rest[1:] if session else rest
        gpu = tpu = None
        high_mem = "--high-mem" in extra
        if "--gpu" in extra:
            gpu = extra[extra.index("--gpu") + 1] if extra.index("--gpu") + 1 < len(extra) else None
        if "--tpu" in extra:
            tpu = extra[extra.index("--tpu") + 1] if extra.index("--tpu") + 1 < len(extra) else None
        result = colab_new(session, gpu=gpu, tpu=tpu, high_mem=high_mem)
        print(result.get("stdout") or result.get("stderr") or "")
        return 0 if result.get("ok") else 1
    if command == "exec":
        parsed = _parse_run_argv(rest)
        passthrough = list(parsed["passthrough"])  # type: ignore[arg-type]
        session = f = out = None
        if "-s" in passthrough:
            idx = passthrough.index("-s")
            if idx + 1 < len(passthrough):
                session = passthrough[idx + 1]
        if "-f" in passthrough:
            idx = passthrough.index("-f")
            if idx + 1 < len(passthrough):
                f = passthrough[idx + 1]
        if "--output-image" in passthrough:
            idx = passthrough.index("--output-image")
            if idx + 1 < len(passthrough):
                out = passthrough[idx + 1]
        result = colab_exec(
            session=session, file=f, output_image=out,
            stdin_text=str(parsed["stdin_text"]) if parsed.get("stdin_text") else None,
            timeout=int(parsed.get("timeout", 300) or 300),  # type: ignore[arg-type]
        )
        print(result.get("stdout") or result.get("stderr") or "")
        return 0 if result.get("ok") else 1
    if command == "run":
        parsed = _parse_run_argv(rest)
        passthrough = list(parsed["passthrough"])  # type: ignore[arg-type]
        if not passthrough:
            print("Uso: python3 -m integrations.colab_cli run [--timeout SEG] <args do colab...>")
            return 2
        result = colab_run_args(
            passthrough,
            timeout=int(parsed.get("timeout", 300) or 300),  # type: ignore[arg-type]
            stdin_text=str(parsed["stdin_text"]) if parsed.get("stdin_text") else None,
        )
        print(result.get("stdout") or result.get("stderr") or "")
        return 0 if result.get("ok") else 1
    print(f"Comando desconhecido: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
