"""SPEC-935-R640: executores de análise para CLIs instaladas de fato.

O inventário não testa autenticação nem chama modelos. Execuções usam argumentos
separados, modo de planejamento/leitura e respostas estruturadas, sem shell ou
aprovação automática. A interface ChatGPT não é controlada por este módulo.
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from integrations.harness_health import HarnessHealthStore


class HarnessRuntime:
    """Inventaria instalações e executa tarefas de texto com evidência da CLI."""

    _CLI_NAMES = {"claude": "claude", "antigravity": "agy", "codex": "codex", "opencode": "opencode"}
    _ALIASES = {"claude_code": "claude", "claude-code": "claude", "antigravity_cli": "antigravity"}
    _PLACEHOLDERS = {"pending", "queued", "formatted", "placeholder", "simulated", "resposta simulada", "pronto_para_delegacao"}

    def __init__(self, repo_root: str | Path | None = None):
        self.repo_root = Path(repo_root or Path(__file__).resolve().parent.parent).resolve()
        health_path = os.environ.get("HARNESS_HEALTH_PATH") or self.repo_root / ".mci_state" / "harness_health.sqlite3"
        self.health_store = HarnessHealthStore(health_path)

    @staticmethod
    def _is_executable(path: Path) -> bool:
        return path.is_file() and os.access(path, os.X_OK)

    @staticmethod
    def _is_wsl() -> bool:
        if os.environ.get("WSL_DISTRO_NAME"):
            return True
        for metadata in (Path("/proc/sys/kernel/osrelease"), Path("/proc/version")):
            try:
                if "microsoft" in metadata.read_text(encoding="utf-8").lower():
                    return True
            except OSError:
                continue
        return False

    def _windows_codex_candidates(self) -> list[Path]:
        """Inclui o bundle desktop sem fixar usuário nem versão do aplicativo."""
        bases: list[Path] = []
        if os.name == "nt":
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                bases.append(Path(local_app_data) / "OpenAI" / "Codex" / "bin")
        elif self._is_wsl():
            users = Path("/mnt/c/Users")
            if users.is_dir():
                bases.extend(users.glob("*/AppData/Local/OpenAI/Codex/bin"))
        candidates = [binary for base in bases for binary in base.glob("*/codex.exe")]
        return sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)

    def _resolve_cli(self, name: str) -> str | None:
        override_name = {"agy": "ANTIGRAVITY_BIN"}.get(name, f"{name.upper()}_BIN")
        override = os.environ.get(override_name)
        if override:
            candidate = Path(override).expanduser()
            return str(candidate.resolve()) if self._is_executable(candidate) else None
        found = shutil.which(name)
        if found:
            return found
        home = Path.home()
        paths = [home / ".local" / "bin" / name, home / ".npm-global" / "bin" / name, home / ".opencode" / "bin" / name]
        if os.name == "nt":
            paths += [home / "AppData" / "Roaming" / "npm" / f"{name}.exe", home / ".local" / "bin" / f"{name}.exe"]
        if name == "codex":
            paths += self._windows_codex_candidates()
        return next((str(path) for path in paths if self._is_executable(path)), None)

    def resolve_cli_path(self, name: str) -> str | None:
        """Resolver compartilhado com diagnóstico, sem iniciar executores."""
        return self._resolve_cli(name)

    def status(self) -> dict[str, Any]:
        """Disponível indica instalação utilizável, sem afirmar login/LLM validado."""
        executors: dict[str, Any] = {}
        for ecosystem, cli in self._CLI_NAMES.items():
            cli_path = self._resolve_cli(cli)
            supported = ecosystem != "opencode"
            health = self.health_store.snapshot(ecosystem, cli_path)
            available = bool(cli_path) and supported
            windows_interop = bool(cli_path and cli_path.lower().endswith(".exe") and os.name != "nt")
            executors[ecosystem] = {
                "installed": bool(cli_path),
                "available": available,
                "eligible_for_auto": available and health["cooldown_remaining_seconds"] <= 0,
                "cli": cli,
                "path": cli_path,
                "execution_mode": "cli-read-only-windows-interop" if windows_interop else "cli-read-only",
                "verification": health["verification"],
                "health": health,
                "reason": (
                    "Execução OpenCode externa desativada para evitar recursão do orquestrador."
                    if not supported else "CLI não instalada ou executável inacessível."
                    if not cli_path else "Executor em pausa automática temporária após falha observada."
                    if health["cooldown_remaining_seconds"] > 0 else "Última execução concluiu com resultado válido; nova execução depende do provedor."
                    if health["last_outcome"] == "success" else "Última execução falhou; nova tentativa automática está disponível."
                    if health["last_outcome"] == "failure" else "Instalação detectada; autenticação e inferência ainda não verificadas."
                ),
            }
        executors["chatgpt"] = {
            "installed": False, "available": False, "eligible_for_auto": False, "cli": None, "path": None,
            "execution_mode": "unavailable", "verification": "installation_only",
            "health": self.health_store.snapshot("chatgpt", None),
            "reason": "A interface ChatGPT não é controlada. Selecione explicitamente codex para usar a CLI Codex.",
        }
        return {**executors, "executors": executors, "available_executors": [name for name, state in executors.items() if state["available"]], "eligible_for_auto_executors": [name for name, state in executors.items() if state["eligible_for_auto"]]}

    def _execution_root(self, cli_path: str) -> str:
        if os.name == "nt" or not cli_path.lower().endswith(".exe"):
            return str(self.repo_root)
        repository = self.repo_root.as_posix()
        drive_match = re.match(r"^/mnt/([a-zA-Z])/(.*)$", repository)
        if drive_match:
            return drive_match[1].upper() + ":\\" + drive_match[2].replace("/", "\\")
        distro = os.environ.get("WSL_DISTRO_NAME")
        if distro and re.fullmatch(r"[A-Za-z0-9_.-]+", distro):
            return "\\\\wsl.localhost\\" + distro + repository.replace("/", "\\")
        converter = shutil.which("wslpath")
        if converter is None and self._is_executable(Path("/usr/bin/wslpath")):
            converter = "/usr/bin/wslpath"
        if converter:
            try:
                converted = subprocess.run([converter, "-w", str(self.repo_root)], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=2, shell=False)
                windows_path = converted.stdout.strip()
                if converted.returncode == 0 and re.match(r"^(?:\\\\(?:wsl\.localhost|wsl\$)\\[^\\]+\\|[A-Za-z]:\\)", windows_path, re.IGNORECASE):
                    return windows_path
            except (OSError, subprocess.TimeoutExpired):
                pass
        raise ValueError("Não foi possível converter o caminho WSL para o executor Windows.")

    def _prompt_with_context(self, prompt: str, agent_id: str | None) -> str:
        instruction = (
            "Tarefa de análise em modo somente leitura. Não altere arquivos, não execute hooks, "
            "não publique conteúdo nem delegue novamente ao orquestrador. "
            "Responda com o resultado concreto em português brasileiro.\n"
        )
        if agent_id is not None:
            if not re.fullmatch(r"[A-Za-z0-9_-]+", agent_id):
                raise ValueError("Identificador de agente inválido.")
            candidates = [self.repo_root / folder / f"{agent_id}.md" for folder in ("agents/catalog", "agents", ".opencode/agents", ".claude/agents")]
            card = next((path for path in candidates if path.is_file() and path.resolve().is_relative_to(self.repo_root)), None)
            if card is None:
                raise ValueError(f"Carta do agente {agent_id} não encontrada no repositório.")
            instruction += f"\nContexto da carta {card.relative_to(self.repo_root)}:\n{card.read_text(encoding='utf-8')}\n"
        return instruction + "\nTarefa recebida:\n" + prompt

    @classmethod
    def _has_real_output(cls, value: Any) -> bool:
        if not isinstance(value, str) or not value.strip():
            return False
        normalized = value.strip().lower().strip(".[] ")
        return normalized not in cls._PLACEHOLDERS and not normalized.startswith("placeholder:")

    def _parse_output(self, ecosystem: str, output: str) -> tuple[str, str]:
        if not output.strip():
            return "", "A CLI encerrou sem entregar resultado."
        if len(output) > 2_000_000:
            return "", "A resposta estruturada excedeu o limite de captura."
        if ecosystem == "codex":
            try:
                events = [json.loads(line) for line in output.splitlines() if line.strip()]
            except json.JSONDecodeError:
                return "", "A CLI Codex não retornou eventos JSON válidos."
            if any(not isinstance(event, dict) for event in events):
                return "", "Formato de evento Codex inválido."
            if any(event.get("type") in ("error", "turn.failed") for event in events):
                return "", "A CLI Codex relatou falha no turno."
            messages = [event.get("item", {}).get("text", "") for event in events if event.get("type") == "item.completed" and isinstance(event.get("item"), dict) and event["item"].get("type") == "agent_message"]
            text = messages[-1] if messages else ""
            if not any(event.get("type") == "turn.completed" for event in events) or not self._has_real_output(text):
                return "", "A CLI Codex não confirmou um turno completo com resultado final."
            return text.strip(), ""
        try:
            result = json.loads(output)
        except json.JSONDecodeError:
            return "", "A CLI não retornou resultado JSON válido."
        if not isinstance(result, dict) or result.get("is_error") or result.get("error"):
            return "", "A CLI relatou falha ou resultado estruturado inválido."
        raw_status = result.get("status")
        normalized_status = raw_status.lower() if isinstance(raw_status, str) else raw_status
        if result.get("subtype") not in (None, "success") or normalized_status not in (None, "success", "completed", "ok"):
            return "", "A CLI não confirmou a conclusão da tarefa."
        text = result.get("result", result.get("response", result.get("output", "")))
        if not self._has_real_output(text):
            return "", "A CLI não entregou conteúdo final verificável."
        return text.strip(), ""

    @staticmethod
    def _failure_category(stderr: str) -> str:
        """Converte detalhes transitórios do provedor em categoria permitida."""
        message = stderr.lower()
        if any(marker in message for marker in ("not logged in", "authentication", "unauthorized", "invalid api key", "credentials", "http 401")):
            return "authentication"
        if any(marker in message for marker in ("rate limit", "quota", "insufficient", "billing", "credit balance", "balance is too low", "too many requests", "http 429")):
            return "account_limit"
        if any(marker in message for marker in ("service unavailable", "temporarily unavailable", "connection refused", "connection reset", "failed to connect", "network error", "http 503", "http 502", "econnrefused", "econnreset", "etimedout", "fetch failed")):
            return "unavailable"
        if any(marker in message for marker in ("unknown option", "unrecognized", "unexpected argument")):
            return "unsupported_arguments"
        if any(marker in message for marker in ("sandbox", "access denied", "permission denied")):
            return "read_restrictions"
        return "execution_failed"

    @classmethod
    def _failure_reason(cls, stderr: str, returncode: int) -> str:
        """Classifica erros conhecidos sem propagar texto/segredos do provedor."""
        category = cls._failure_category(stderr)
        if category != "execution_failed":
            return HarnessHealthStore._ERRORS[category]
        return f"A CLI encerrou com código {returncode}, sem confirmar conclusão."

    @staticmethod
    def _failure_details(stderr: str, stdout: str) -> str:
        details = stderr or ""
        try:
            structured = json.loads(stdout)
            events = [structured]
        except json.JSONDecodeError:
            events = []
            for line in stdout.splitlines():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(event, dict) and event.get("type") in ("error", "turn.failed"):
                    events.append(event)
        for event in events:
            if isinstance(event, dict):
                details += " " + " ".join(str(event.get(key, "")) for key in ("result", "error", "message"))
        return details

    def execute(self, ecosystem: str, prompt: str, timeout: float = 180, agent_id: str | None = None) -> dict[str, Any]:
        ecosystem = self._ALIASES.get(ecosystem, ecosystem)
        result = {"success": False, "output": "", "error": "", "ecosystem": ecosystem, "execution_mode": "unavailable"}
        if ecosystem == "chatgpt":
            result["error"] = "A interface ChatGPT não é controlada; selecione explicitamente codex para a CLI Codex."
            return result
        if ecosystem not in {"claude", "antigravity", "codex"}:
            result["error"] = "Executor externo não suportado."
            return result
        cli_path = self._resolve_cli(self._CLI_NAMES[ecosystem])
        if cli_path is None:
            result["error"] = "CLI não instalada ou executável inacessível."
            return result
        if not isinstance(prompt, str) or not prompt.strip():
            result["error"] = "A tarefa precisa conter um prompt de texto."
            return result
        try:
            timeout_value = float(timeout)
            if not math.isfinite(timeout_value) or timeout_value <= 0:
                raise ValueError("Timeout inválido.")
            bounded_timeout = min(600.0, timeout_value)
            context = self._prompt_with_context(prompt, agent_id)
            execution_root = self._execution_root(cli_path)
        except (TypeError, ValueError, OSError) as exc:
            result["error"] = str(exc)
            return result
        result["execution_mode"] = "cli-read-only-windows-interop" if cli_path.lower().endswith(".exe") and os.name != "nt" else "cli-read-only"
        options: dict[str, Any] = {"cwd": str(self.repo_root), "capture_output": True, "text": True, "encoding": "utf-8", "errors": "replace", "timeout": bounded_timeout, "shell": False}
        if ecosystem == "claude":
            command = [cli_path, "-p", "--output-format", "json", "--safe-mode", "--tools", "Read,Glob,Grep", "--permission-mode", "plan", "--permission-prompts", "none", "--no-session-persistence"]
            options["input"] = context
        elif ecosystem == "antigravity":
            # Sintaxe validada pela AntigravityBridge (R393), com os gates de
            # leitura que a interface legada delegate() ainda não parametriza.
            # --disable-slash-commands anula --mode plan nesta CLI real; não
            # combiná-los, pois o planejamento é o gate de leitura necessário.
            command = [cli_path, "--print", context, "--output-format", "json", "--mode", "plan", "--sandbox"]
        else:
            command = [cli_path, "exec", "--sandbox", "read-only", "--json", "--ephemeral", "--ignore-user-config", "--cd", execution_root, "-"]
            options["input"] = context
        started = time.monotonic()
        binary_identity = self.health_store.identity_for(cli_path)

        def finish(category: str | None = None) -> dict[str, Any]:
            duration = max(0.0, time.monotonic() - started)
            result["duration_seconds"] = duration
            self.health_store.record(ecosystem, cli_path, success=result["success"], duration_seconds=duration, error_category=category, observed_identity=binary_identity)
            return result

        try:
            process = subprocess.run(command, **options)
        except subprocess.TimeoutExpired:
            result["error"] = f"A CLI excedeu o limite de {bounded_timeout:g} segundos."
            return finish("timeout")
        except OSError:
            result["error"] = "Falha ao iniciar a CLI instalada."
            return finish("unavailable")
        result["returncode"] = process.returncode
        if process.returncode != 0:
            # Não espelhar stderr: provedores podem imprimir credenciais em erros.
            failure_details = self._failure_details(process.stderr, process.stdout)
            result["error"] = self._failure_reason(failure_details, process.returncode)
            return finish(self._failure_category(failure_details))
        output, error = self._parse_output(ecosystem, process.stdout)
        category = None
        if error:
            failure_details = self._failure_details(process.stderr, process.stdout)
            category = self._failure_category(failure_details)
            if category == "execution_failed":
                category = "invalid_output"
            else:
                error = self._failure_reason(failure_details, process.returncode)
        result.update(success=not error, output=output, error=error)
        return finish(category)
