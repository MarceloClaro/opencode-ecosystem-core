"""Executor alternativo multi-provedor baseado no agente de terminal `tig`
(M7 da SPEC-935-R471; subspec SPEC-935-R473).

Integração estritamente por invocação externa: o upstream `rsrohan99/tig`
não declara licença (license: null), portanto é vedada a incorporação,
redistribuição ou inclusão em bundle de qualquer código-fonte do projeto.
Este módulo apenas lambe o binário `tig` (se disponível) com fallback entre
provedores de LLM e registra um recibo de auditoria por tentativa.

Invariantes (SPEC-935-R473):
- `shell=False` obrigatório; argumentos sempre em lista; task via stdin.
- Provedor fora da allowlist, modo desconhecido ou task vazia => negação
  sem qualquer chamada ao binário (fail-closed).
- Ausência do binário (`shutil.which` / `TIG_BIN`) => indisponível; nunca
  instala nada automaticamente.
- Anti-overclaim: o recibo reporta apenas exit_code/success/motivo; não
  declara mérito, verificação ou qualidade de topo.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Set

# Provedores reconhecidos pelo upstream tig (R473, invocação --provider).
ALLOWED_PROVIDERS: Set[str] = {
    "ollama",
    "deepseek",
    "groq",
    "gemini",
    "openai",
    "anthropic",
    "openrouter",
}

# Ordem de fallback preferida: Ollama local como âncora, depois externos.
DEFAULT_PROVIDER_FALLBACK: List[str] = [
    "ollama",
    "deepseek",
    "groq",
    "gemini",
    "openai",
]

# Modos do tig que espelham o par SDD/implementação.
MODES: Set[str] = {"architect", "code"}

ORCHESTRATOR = "marceloclaro"

Runner = Callable[..., object]


@dataclass
class TigExecutionReceipt:
    """Recibo auditável de uma execução/deferência do executor tig."""

    orchestrator: str = ORCHESTRATOR
    invoked_at_utc: str = ""
    mode: str = ""
    task_sha256: str = ""
    bin_path: Optional[str] = None
    provider: Optional[str] = None
    exit_code: Optional[int] = None
    success: bool = False
    attempted_providers: List[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class TigExecutor:
    """Despacha tarefas ao agente `tig` com fallback multi-provedor e recibo.

    O runner é injetável para testes herméticos; em produção usa
    `subprocess.run` com `shell=False`.
    """

    def __init__(
        self,
        bin_path: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        allowlist: Optional[Set[str]] = None,
        runner: Optional[Runner] = None,
    ) -> None:
        self.env = env if env is not None else os.environ
        self.allowlist = set(allowlist) if allowlist is not None else set(ALLOWED_PROVIDERS)
        self._runner: Callable[..., object] = runner or self._default_runner
        self.bin_path = self._resolve_bin(bin_path)

    @staticmethod
    def _default_runner(cmd: Sequence[str], **kwargs: object) -> object:
        return subprocess.run(cmd, **kwargs)

    def _resolve_bin(self, bin_path: Optional[str]) -> Optional[str]:
        if bin_path:
            return bin_path
        if os.environ.get("TIG_BIN"):
            return os.environ["TIG_BIN"]
        found = shutil.which("tig")
        return found

    def available(self) -> bool:
        return bool(self.bin_path)

    def status(self) -> Dict[str, object]:
        return {
            "name": "tig",
            "available": self.available(),
            "bin_path": self.bin_path,
            "providers": sorted(self.allowlist),
            "modes": sorted(MODES),
            "note": "integracao por invocacao externa; upstream sem licenca declarada",
        }

    def run(
        self,
        task: str,
        mode: str = "architect",
        provider_fallback: Optional[Sequence[str]] = None,
        timeout: int = 300,
    ) -> TigExecutionReceipt:
        receipt = TigExecutionReceipt(
            invoked_at_utc=_utc_now(),
            mode=mode,
            task_sha256=_sha256(task),
            bin_path=self.bin_path,
        )

        if not task.strip():
            receipt.reason = "task vazia; despacho negado"
            return receipt

        if mode not in MODES:
            receipt.reason = f"modo desconhecido: {mode}; modos validos: {sorted(MODES)}"
            return receipt

        if not self.bin_path:
            receipt.reason = "binario tig indisponivel; nenhuma execucao"
            return receipt

        ordered = list(provider_fallback or DEFAULT_PROVIDER_FALLBACK)
        ordered = [p for p in ordered if p in self.allowlist]
        if not ordered:
            receipt.reason = "nenhum provedor na allowlist; fail-closed"
            return receipt

        receipt.attempted_providers = list(ordered)
        for provider in ordered:
            rc, error = self._invoke(task, mode, provider, timeout)
            if rc == 0:
                receipt.provider = provider
                receipt.exit_code = 0
                receipt.success = True
                receipt.reason = f"execucao concluida via provedor {provider}"
                return receipt
            receipt.exit_code = rc
            receipt.reason = error or f"provedor {provider} falhou (exit={rc})"

        receipt.success = False
        return receipt

    def _invoke(self, task: str, mode: str, provider: str, timeout: int):
        cmd = [self.bin_path, "--mode", mode, "--provider", provider]
        try:
            proc = self._runner(
                cmd,
                shell=False,
                input=task.encode("utf-8"),
                capture_output=True,
                timeout=timeout,
                env=self.env,
            )
            return int(getattr(proc, "returncode", -1)), ""
        except subprocess.TimeoutExpired as exc:
            return -1, f"timeout ({timeout}s) no provedor {provider}"
        except Exception as exc:  # runner injetado pode falhar de forma estranha
            return -1, f"excecao controlada no provedor {provider}: {type(exc).__name__}"


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()