# -*- coding: utf-8 -*-
"""
Plandex CLI Integration — agente de codificação AI open source (MIT)
=====================================================================
Integra a CLI `plandex` (https://github.com/plandex-ai/plandex, MIT, Go) ao
OpenCode Ecosystem Core como executor externo orquestrável (padrão M7, mesmo
padrão da integração Goose — SPEC-935-R598): invocação por subprocess com
healthcheck tolerante; ausência vira ``warn`` no doctor, nunca ``fail``
(SPEC-935-R599).

Plandex: agente terminal-based para tarefas grandes e projetos reais — planos
incrementais, sandbox de diff, até 2M tokens de contexto, tree-sitter project
maps, autonomia configurável e mistura de modelos (Anthropic, OpenAI, Google,
open source). O Plandex Cloud está sendo encerrado (03/10/2025); esta
integração assume uso local/self-hosted ou BYO key (ex.: OpenRouter).

Fluxo natural de scripting:
    plandex new            -> cria um plano
    plandex tell '<tarefa>' -> descreve a tarefa (gera/executa)
    plandex diff --plain   -> revisa mudanças pendentes (sandbox)
    plandex apply [--commit] -> aplica (aqui, com revisão humana no gate SDD/TDD)

Uso:
    python3 -m integrations.plandex_cli status
    python3 -m integrations.plandex_cli plans
    python3 -m integrations.plandex_cli new [-n nome] [--semi|--full]
    python3 -m integrations.plandex_cli tell '<tarefa>' [--apply] [--commit]
    python3 -m integrations.plandex_cli chat '<pergunta>'   # sem alterações
    python3 -m integrations.plandex_cli diff
    python3 -m integrations.plandex_cli apply [--commit]
    python3 -m integrations.plandex_cli doctor
    python3 -m integrations.plandex_cli install
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

PLANDEX_INSTALL_CMD = "curl -sL https://plandex.ai/install.sh | bash"

_ALIASES = ("plandex", "pdx")


def _binary() -> Optional[str]:
    """Retorna o binário disponível (plandex ou pdx), ou None."""
    for name in _ALIASES:
        found = shutil.which(name)
        if found:
            return found
    return None


def plandex_available() -> bool:
    """True se `plandex` (ou alias `pdx`) estiver no PATH."""
    return _binary() is not None


_SEMVER_RE = r"(\d+(?:\.\d+){1,3}(?:[-+][0-9A-Za-z.-]+)?)"

# Cache de versão em disco (SPEC-935-R603-perf): o doctor (R110) exige
# run_doctor < 5s e o subprocess Go do plandex custa ~1-2s. Guardamos a versão
# SEMÂNTICA detectada keyed por (realpath, size, mtime_ns) do binário — se o
# binário for atualizado, o cache é invalidado e a versão é redescoberta.
_VERSION_CACHE_DIR = Path.home() / ".cache" / "opencode-ecosystem-core"


def _version_cache_key(binary: str) -> Optional[tuple]:
    """Chave de invalidação do cache: (realpath, size, mtime_ns)."""
    try:
        st = os.stat(binary)
        return (os.path.realpath(binary), st.st_size, st.st_mtime_ns)
    except OSError:
        return None


def _read_cached_version(binary: str) -> Optional[str]:
    key = _version_cache_key(binary)
    if key is None:
        return None
    try:
        payload = json.loads(
            (_VERSION_CACHE_DIR / "plandex_version.json").read_text(encoding="utf-8")
        )
        if payload.get("key") == list(key):
            version = payload.get("version")
            if isinstance(version, str) and version:
                return version
    except (OSError, ValueError):
        pass
    return None


def _write_cached_version(binary: str, version: str) -> None:
    key = _version_cache_key(binary)
    if key is None:
        return
    try:
        _VERSION_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        payload = {"key": list(key), "version": version}
        (_VERSION_CACHE_DIR / "plandex_version.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )
    except OSError:
        pass


def plandex_version() -> Optional[str]:
    """Versão semântica instalada via `plandex` (None se ausente).

    No primeiro uso o binário abre o onboarding interativo para ``--version``;
    por isso tenta ``--version`` e, em seguida, o subcomando ``version``
    (ex.: ``"2.2.1"``). Extrai apenas o número de versão semântica.

    Resultado é cacheado em disco (keyed pelo binário) para manter o doctor
    estrutural rápido (R110); a invalidação por size+mtime reexecuta o
    subprocess apenas quando o binário muda de fato.
    """
    binary = _binary()
    if binary is None:
        return None
    cached = _read_cached_version(binary)
    if cached is not None:
        return cached
    for args in ([binary, "--version"], [binary, "version"]):
        try:
            proc = subprocess.run(
                args, capture_output=True, text=True, timeout=10, check=False
            )
            match = re.search(_SEMVER_RE, (proc.stdout or "").strip())
            if match:
                version = match.group(1)
                _write_cached_version(binary, version)
                return version
        except (OSError, subprocess.TimeoutExpired):
            continue
    return None


def _run(
    args: List[str],
    cwd: Optional[str] = None,
    timeout: int = 300,
) -> Dict[str, object]:
    """Executa um subcomando plandex e normaliza o retorno (nunca lança)."""
    binary = _binary()
    if binary is None:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": "plandex não está instalado. Instale com: " + PLANDEX_INSTALL_CMD,
            "timeout": False,
            "version": None,
            "comando": None,
        }
    cmd = [binary, *args]
    timeout_flag = False
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": int(proc.returncode) == 0,
            "returncode": int(proc.returncode),
            "stdout": (proc.stdout or ""),
            "stderr": (proc.stderr or ""),
            "timeout": False,
            "version": plandex_version(),
            "comando": " ".join(cmd),
        }
    except subprocess.TimeoutExpired:
        timeout_flag = True
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"plandex excedeu o limite de {timeout}s.",
            "timeout": True,
            "version": plandex_version(),
            "comando": " ".join(cmd),
        }
    except OSError as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"Falha ao invocar plandex: {exc}",
            "timeout": False,
            "version": plandex_version(),
            "comando": " ".join(cmd),
        }


def plandex_plans(cwd: Optional[str] = None, timeout: int = 60) -> Dict[str, object]:
    """Lista os planos existentes no diretório (`plandex plans`)."""
    return _run(["plans"], cwd=cwd, timeout=timeout)


def plandex_new(
    name: Optional[str] = None,
    auto: Optional[str] = None,
    cwd: Optional[str] = None,
    timeout: int = 60,
) -> Dict[str, object]:
    """Cria um novo plano (`plandex new [-n nome] [--semi|--full|...]`).

    `auto` aceita: none, basic, plus, semi, full (autonomia inicial).
    """
    args = ["new"]
    if name:
        args += ["-n", name]
    if auto in {"basic", "plus", "semi", "full"}:
        args.append(f"--{auto}")
    return _run(args, cwd=cwd, timeout=timeout)


def plandex_tell(
    prompt: str,
    apply: bool = False,
    commit: bool = False,
    auto_load: bool = True,
    cwd: Optional[str] = None,
    timeout: int = 600,
) -> Dict[str, object]:
    """Descreve uma tarefa em modo scripting (`plandex tell "<prompt>"`).

    `apply=True` → `--apply` (aplica mudanças automaticamente; aqui o Core
    exige revisão humana antes — use apenas com consentimento explícito).
    `commit=True` → `--commit` (commita git junto com o apply).
    """
    args = ["tell", prompt]
    if apply:
        args.append("--apply")
    if commit:
        args.append("--commit")
    if auto_load:
        args.append("--auto-load-context")
    args.append("--skip-menu")
    return _run(args, cwd=cwd, timeout=timeout)


def plandex_chat(
    prompt: str,
    cwd: Optional[str] = None,
    timeout: int = 300,
) -> Dict[str, object]:
    """Pergunta/conversa sem alterar arquivos (`plandex chat "<prompt>"`)."""
    return _run(["chat", prompt], cwd=cwd, timeout=timeout)


def plandex_diff(cwd: Optional[str] = None, timeout: int = 60) -> Dict[str, object]:
    """Mostra as mudanças pendentes em texto puro (`plandex diff --plain`)."""
    return _run(["diff", "--plain"], cwd=cwd, timeout=timeout)


def plandex_apply(
    commit: bool = False,
    cwd: Optional[str] = None,
    timeout: int = 300,
) -> Dict[str, object]:
    """Aplica mudanças pendentes (`plandex apply [--commit]`)."""
    args = ["apply"]
    if commit:
        args.append("--commit")
    return _run(args, cwd=cwd, timeout=timeout)


def doctor_check() -> Dict[str, str]:
    """DoctorCheck no formato do doctor do Core (name/status/detail)."""
    version = plandex_version()
    if version is not None:
        return {
            "name": "plandex",
            "status": "pass",
            "detail": f"Plandex CLI instalado (versão {version}). "
            "Executor externo orquestrável via integrations.plandex_cli (SPEC-935-R599).",
        }
    return {
        "name": "plandex",
        "status": "warn",
        "detail": "Plandex CLI ausente (específica do SPEC-935-R599). Anterior a "
        f"integrar, instale com: {PLANDEX_INSTALL_CMD}",
    }


def install_instructions() -> str:
    """Instrução oficial de instalação do Plandex CLI (uso local/BYO key)."""
    return (
        "Instalação oficial do Plandex CLI:\n"
        f"  {PLANDEX_INSTALL_CMD}\n"
        "Alternativas: https://github.com/plandex-ai/plandex#install\n"
        "Hosting: o Plandex Cloud está encerrando (03/10/2025). Use modo local/"
        "self-hosted (Docker) ou BYO key (ex.: export OPENROUTER_API_KEY=...).\n"
        "Alias: `pdx` equivale a `plandex`."
    )


def _format_status() -> str:
    available = plandex_available()
    version = plandex_version()
    versao_json = "null" if version is None else json.dumps(version)
    return "\n".join(
        [
            "{",
            f'  "especificacao": "SPEC-935-R599",',
            f'  "disponivel": {str(available).lower()},',
            f'  "versao": {versao_json},',
            f'  "fluxo": "new -> tell -> diff --plain -> apply [--commit]",',
            f'  "contexto": "ate 2M tokens, tree-sitter project maps, sandbox de diff",',
            f'  "licenca": "MIT",',
            f'  "origem": "https://github.com/plandex-ai/plandex",',
            "}",
        ]
    )


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"--help", "-h", "help"}:
        print(
            "Uso: python3 -m integrations.plandex_cli "
            "<status|plans|new|tell|chat|diff|apply|doctor|install> [args...]\n"
            "  new [-n NOME] [--auto none|basic|plus|semi|full]\n"
            "  tell '<tarefa>' [--apply] [--commit]\n"
            "  apply [--commit]\n"
            "  ex.: /plandex tell 'implemente a feature X' --apply --commit"
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
    if command == "plans":
        result = plandex_plans()
    elif command == "new":
        name = None
        auto = None
        if rest and not rest[0].startswith("-"):
            name, *rest = rest
        if rest:
            if rest[0] == "--auto" and len(rest) > 1:
                auto = rest[1]
                del rest[:2]
            elif rest[0].startswith("--auto="):
                auto = rest[0].split("=", 1)[1]
                del rest[:1]
            elif rest[0].lstrip("-") in {"none", "basic", "plus", "semi", "full"}:
                auto = rest[0].lstrip("-")
                del rest[:1]
            if rest:
                print(f"Argumentos inesperados: {' '.join(rest)}")
                return 2
        if auto not in {None, "none", "basic", "plus", "semi", "full"}:
            print(f"Modo de autonomia inválido: {auto} (none|basic|plus|semi|full)")
            return 2
        result = plandex_new(name=name, auto=auto)
    elif command == "tell":
        flags = {"--apply": False, "--commit": False}
        prompt_parts = []
        for token in rest:
            if token in flags:
                flags[token] = True
            else:
                prompt_parts.append(token)
        prompt = " ".join(prompt_parts).strip()
        if not prompt:
            print("Uso: python3 -m integrations.plandex_cli tell '<tarefa>' [--apply] [--commit]")
            return 2
        result = plandex_tell(prompt, apply=flags["--apply"], commit=flags["--commit"])
    elif command == "chat":
        prompt = " ".join(rest).strip()
        if not prompt:
            print("Uso: python3 -m integrations.plandex_cli chat '<pergunta>'")
            return 2
        result = plandex_chat(prompt)
    elif command == "diff":
        result = plandex_diff()
    elif command == "apply":
        result = plandex_apply(commit="--commit" in rest)
    else:
        print(f"Comando desconhecido: {command}")
        return 2
    print(result.get("stdout") or result.get("stderr") or "")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())