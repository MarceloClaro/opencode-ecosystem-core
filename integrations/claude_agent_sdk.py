# -*- coding: utf-8 -*-
"""
Ponte Claude Agent SDK Python (SPEC-935-R647) — biblioteca externa orquestrável.

Upstream: anthropics/claude-agent-sdk-python (LICENSE MIT; uso regido pelos
Commercial Terms da Anthropic). Fork: MarceloClaro/claude-agent-sdk-python.
SDK: `query()` async, `ClaudeSDKClient` (tools in-process + hooks), CLI
`claude` embutido no wheel (ou `cli_path=` custom). Requer Python 3.10+ e
conta Claude (chamadas faturáveis).

Esta ponte NÃO executa `query()`: expõe presença/versão, monta options no
schema `ClaudeAgentOptions`, documenta instalação e registra saúde tolerante
(padrão M7). A execução pertence ao operador (anti-overclaim R110).
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional

_CLAUDE_BIN = "claude"
_SDK_DEP = "claude_agent_sdk"
_SEMVER_RE = r"(\d+(?:\.\d+){1,3}(?:[-+][0-9A-Za-z.-]+)?)"

UPSTREAM_REPO = "https://github.com/anthropics/claude-agent-sdk-python"
FORK_REPO = "https://github.com/MarceloClaro/claude-agent-sdk-python"
COMMERCIAL_TERMS = "https://www.anthropic.com/legal/commercial-terms"


def claude_available() -> bool:
    """True se o binário `claude` (CLI) estiver no PATH."""
    return shutil.which(_CLAUDE_BIN) is not None


def cli_version(timeout: int = 15) -> Optional[str]:
    """Versão semântica via `claude --version` (None se ausente/falha)."""
    if not claude_available():
        return None
    try:
        proc = subprocess.run(
            [_CLAUDE_BIN, "--version"], capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
        match = re.search(_SEMVER_RE, combined)
        return match.group(1) if match else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def sdk_dep_status() -> bool:
    """True se o pacote `claude_agent_sdk` for importável (sem importá-lo)."""
    try:
        return importlib.util.find_spec(_SDK_DEP) is not None
    except (ImportError, ValueError):
        return False


def sdk_available() -> bool:
    """True se a dep Python do SDK estiver presente (CLI é check separado)."""
    return sdk_dep_status()


def build_query_options(
    prompt: str,
    system_prompt: Optional[str] = None,
    allowed_tools: Optional[List[str]] = None,
    disallowed_tools: Optional[List[str]] = None,
    max_turns: Optional[int] = None,
    cwd: Optional[str] = None,
    permission_mode: Optional[str] = None,
    cli_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Monta options no schema `ClaudeAgentOptions` (puro, sem rede/execução).

    Lança ValueError em português se o prompt for vazio ou tipos inválidos.
    Nota: `allowed_tools` é allowlist de auto-aprovação (não remove tools;
    bloquear exige `disallowed_tools`).
    """
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("O prompt deve ser uma string não vazia.")
    if max_turns is not None and (not isinstance(max_turns, int) or max_turns <= 0):
        raise ValueError("max_turns deve ser um inteiro positivo ou None.")
    options: Dict[str, Any] = {"prompt": prompt}
    if system_prompt:
        options["system_prompt"] = system_prompt
    if allowed_tools:
        options["allowed_tools"] = list(allowed_tools)
    if disallowed_tools:
        options["disallowed_tools"] = list(disallowed_tools)
    if max_turns is not None:
        options["max_turns"] = max_turns
    if cwd:
        options["cwd"] = cwd
    if permission_mode:
        options["permission_mode"] = permission_mode
    if cli_path:
        options["cli_path"] = cli_path
    return options


def doctor_check() -> Dict[str, str]:
    """DoctorCheck no formato do Core (name/status/detail; nunca fail)."""
    dep = sdk_dep_status()
    cli = claude_available()
    version = cli_version() if cli else None
    if dep and cli:
        sufixo = f" (CLI {version})" if version else " (CLI presente)"
        return {
            "name": "claude-agent-sdk",
            "status": "pass",
            "detail": f"Ponte Claude Agent SDK pronta{sufixo}. SPEC-935-R647.",
        }
    faltas = []
    if not dep:
        faltas.append("pacote `claude-agent-sdk` (pip install claude-agent-sdk, Python 3.10+)")
    if not cli:
        faltas.append("CLI `claude` (embutido no wheel ou curl https://claude.ai/install.sh | bash)")
    return {
        "name": "claude-agent-sdk",
        "status": "warn",
        "detail": "Ponte parcial — faltam: " + "; ".join(faltas) + ". SPEC-935-R647.",
    }


def install_instructions() -> str:
    """Instrução oficial de uso do Claude Agent SDK Python."""
    return (
        "Claude Agent SDK Python (anthropics/claude-agent-sdk-python):\n"
        f"  Upstream: {UPSTREAM_REPO}\n"
        f"  Fork: {FORK_REPO}\n"
        "\n"
        "Instalação (Python 3.10+):\n"
        "  pip install claude-agent-sdk\n"
        "  # CLI `claude` vem embutida; alternativa:\n"
        "  #   curl -fsSL https://claude.ai/install.sh | bash\n"
        "  #   ClaudeAgentOptions(cli_path='/path/to/claude')\n"
        "\n"
        "Uso (execução do operador — chamadas faturáveis, requer conta Claude):\n"
        "  from claude_agent_sdk import query, ClaudeAgentOptions\n"
        "  async for m in query(prompt='...', options=ClaudeAgentOptions(max_turns=1)):\n"
        "      print(m)\n"
        "\n"
        "Avisos:\n"
        f"  Uso regido pelos Commercial Terms: {COMMERCIAL_TERMS}\n"
        "  allowed_tools = allowlist de auto-aprovação (não remove tools;\n"
        "  bloquear exige disallowed_tools). Erros: CLINotFoundError,\n"
        "  ProcessError, ResultError, CLIJSONDecodeError.\n"
        "\n"
        "Uso no Core:\n"
        "  /claude-sdk status    # CLI + dep Python\n"
        "  /claude-sdk options --prompt '...' [--max-turns 1]  # monta options (sem executar)"
    )


def _format_status() -> str:
    return json.dumps(
        {
            "especificacao": "SPEC-935-R647",
            "cli_presente": claude_available(),
            "cli_versao": cli_version(),
            "sdk_dep": sdk_dep_status(),
            "ponte_pronta": sdk_available() and claude_available(),
            "licenca_codigo": "MIT (LICENSE)",
            "termos_uso": COMMERCIAL_TERMS,
            "origem": UPSTREAM_REPO,
            "fork": FORK_REPO,
        },
        ensure_ascii=False,
        indent=2,
    )


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"--help", "-h", "help"}:
        print(
            "Uso: python3 -m integrations.claude_agent_sdk <status|doctor|install|options> [args...]\n"
            "  options --prompt '...' [--system-prompt '...'] [--allow Read,Write]\n"
            "          [--disallow Bash] [--max-turns N] [--cwd DIR] [--permission-mode M]"
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
    if command == "options":
        prompt = ""
        kwargs: Dict[str, Any] = {}
        idx = 0
        while idx < len(rest):
            tok = rest[idx]
            if tok == "--prompt" and idx + 1 < len(rest):
                prompt = rest[idx + 1]
                idx += 2
                continue
            if tok == "--system-prompt" and idx + 1 < len(rest):
                kwargs["system_prompt"] = rest[idx + 1]
                idx += 2
                continue
            if tok == "--allow" and idx + 1 < len(rest):
                kwargs["allowed_tools"] = [t.strip() for t in rest[idx + 1].split(",") if t.strip()]
                idx += 2
                continue
            if tok == "--disallow" and idx + 1 < len(rest):
                kwargs["disallowed_tools"] = [t.strip() for t in rest[idx + 1].split(",") if t.strip()]
                idx += 2
                continue
            if tok == "--max-turns" and idx + 1 < len(rest):
                try:
                    kwargs["max_turns"] = int(rest[idx + 1])
                except ValueError:
                    print("max-turns deve ser inteiro.")
                    return 2
                idx += 2
                continue
            if tok == "--cwd" and idx + 1 < len(rest):
                kwargs["cwd"] = rest[idx + 1]
                idx += 2
                continue
            if tok == "--permission-mode" and idx + 1 < len(rest):
                kwargs["permission_mode"] = rest[idx + 1]
                idx += 2
                continue
            idx += 1
        if not prompt.strip():
            print("Uso: options --prompt '...' [--max-turns N]")
            return 2
        try:
            print(json.dumps(build_query_options(prompt, **kwargs), ensure_ascii=False, indent=2))
        except ValueError as exc:
            print(str(exc))
            return 2
        return 0
    print(f"Comando desconhecido: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
