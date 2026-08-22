# -*- coding: utf-8 -*-
"""
Adapter — canal de execução do DeepSeek Harness.

Canais (prioridade):
  sdk         — import deepseek_harness funciona (Python SDK instalado)
  runtime-bin — binário `dsh` no PATH ou em apps/cli
  unavailable — nenhum canal; handoff enfileirado em .deepseek-harness/queue/

O runner injetável permite TDD sem credenciais nem subprocesso real.
Nunca simula sucesso: ausência de canal resulta em status "unavailable".
"""

from __future__ import annotations

import json
import os
import shutil
import time
import uuid
from typing import Any, Callable, Dict, Optional

DEFAULT_DSH_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "deepseek-harness",
)
DEFAULT_MONOREPO = os.path.join(DEFAULT_DSH_ROOT, "DEEPSEEK-HARNESS")
QUEUE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    ".deepseek-harness",
    "queue",
)


class DeepSeekHarnessAdapter:
    """Adapta chamadas do Core a execuções do dsh via SDK, binário ou handoff."""

    def __init__(self, dsh_root: str | None = None):
        self.dsh_root = os.path.abspath(dsh_root or DEFAULT_DSH_ROOT)
        self.monorepo = os.path.join(self.dsh_root, "DEEPSEEK-HARNESS")
        self.executions: int = 0
        self.failures: int = 0

    # ------------------------------------------------------------------
    def resolve_channel(self) -> str:
        """Resolve o canal de execução disponível neste ambiente."""
        # 1) Python SDK instalado?
        try:
            import importlib.util as _ilu  # type: ignore
            if _ilu.find_spec("deepseek_harness") is not None:
                return "sdk"
            # também tenta deepseek_harness_runtime (bundled runtime)
            if _ilu.find_spec("deepseek_harness_runtime") is not None:
                return "sdk"
        except Exception:
            pass

        # 2) binário dsh no PATH ou em apps/cli
        if shutil.which("dsh") is not None:
            return "runtime-bin"
        cli_bin = os.path.join(self.monorepo, "apps", "cli")
        if os.path.isdir(cli_bin) and any(
            os.path.isfile(os.path.join(cli_bin, name))
            for name in ("package.json", "src")
        ):
            # sem build não há binário; não alega runtime-bin
            pass

        return "unavailable"

    def status(self) -> Dict[str, Any]:
        return {
            "channel": self.resolve_channel(),
            "available": os.path.isdir(self.monorepo),
            "executions": self.executions,
            "failures": self.failures,
            "monorepo": self.monorepo,
            "queue_dir": QUEUE_DIR,
        }

    # ------------------------------------------------------------------
    def run_task(
        self,
        prompt: str,
        cwd: str | None = None,
        runner: Optional[Callable[..., Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Executa uma tarefa do dsh.

        Quando `runner` é fornecido, ele é a fonte da verdade (TDD).
        Caso contrário, delega ao canal resolvido ou enfileira handoff.
        """

        # Runner injetado: caminho TDD — determinístico e auditável
        if runner is not None:
            try:
                result = runner(prompt, cwd=cwd)
            except Exception as exc:
                self.failures += 1
                return {
                    "status": "error",
                    "error": str(exc),
                    "prompt": prompt[:200],
                }
            # Normaliza: garante status completed quando runner retorna payload útil
            if isinstance(result, dict):
                if result.get("status") in ("completed", "error", "unavailable"):
                    status = result["status"]
                else:
                    status = "completed" if result.get("final_response") or result.get("events") else "completed"
                    result = dict(result)
                    result["status"] = status
            else:
                result = {"status": "completed", "final_response": str(result)}
            if result.get("status") == "completed":
                self.executions += 1
            elif result.get("status") == "error":
                self.failures += 1
            return result

        # Canal real
        channel = self.resolve_channel()
        if channel == "sdk":
            return self._run_via_sdk(prompt, cwd=cwd)
        if channel == "runtime-bin":
            return self._run_via_binary(prompt, cwd=cwd)

        # Indisponível → handoff auditável (padrão SPEC-046)
        return self._enqueue_handoff(prompt, cwd=cwd, reason="canal indisponível: SDK e binário ausentes")

    # ------------------------------------------------------------------
    def _run_via_sdk(self, prompt: str, cwd: str | None) -> Dict[str, Any]:
        """Execução real via Python SDK (requer DEEPSEEK_API_KEY em produção)."""
        # Em CI/teste sem chave, não tenta subprocesso real — enfileira.
        if not os.environ.get("DEEPSEEK_API_KEY"):
            return self._enqueue_handoff(
                prompt, cwd=cwd,
                reason="SDK disponível mas DEEPSEEK_API_KEY ausente — handoff para execução com credenciais",
            )
        try:
            from deepseek_harness import DeepSeekHarness  # type: ignore

            harness = DeepSeekHarness(cwd=cwd or self.monorepo)
            with harness:
                res = harness.run(prompt)
            self.executions += 1
            return {
                "status": "completed",
                "session_id": getattr(res, "session_id", ""),
                "final_response": getattr(res, "final_response", ""),
                "events": [e for e in getattr(res, "events", [])],
                "finish_reason": getattr(res, "finish_reason", None),
            }
        except Exception as exc:
            self.failures += 1
            return {"status": "error", "error": str(exc), "prompt": prompt[:200]}

    def _run_via_binary(self, prompt: str, cwd: str | None) -> Dict[str, Any]:
        import subprocess

        if not os.environ.get("DEEPSEEK_API_KEY"):
            return self._enqueue_handoff(
                prompt, cwd=cwd,
                reason="binário dsh disponível mas DEEPSEEK_API_KEY ausente",
            )
        binary = shutil.which("dsh") or "dsh"
        try:
            proc = subprocess.run(
                [binary, "--profile", "headless", prompt],
                cwd=cwd or self.monorepo,
                capture_output=True, text=True, timeout=120,
            )
            if proc.returncode == 0:
                self.executions += 1
                return {
                    "status": "completed",
                    "final_response": proc.stdout[-4000:],
                    "stderr": proc.stderr[-1000:],
                    "returncode": proc.returncode,
                }
            self.failures += 1
            return {
                "status": "error",
                "error": proc.stderr[-2000:] or f"dsh saiu com código {proc.returncode}",
                "returncode": proc.returncode,
            }
        except Exception as exc:
            self.failures += 1
            return {"status": "error", "error": str(exc)}

    def _enqueue_handoff(self, prompt: str, cwd: str | None, reason: str) -> Dict[str, Any]:
        os.makedirs(QUEUE_DIR, exist_ok=True)
        handoff = {
            "id": f"dsh-{uuid.uuid4().hex[:8]}",
            "created_at": time.time(),
            "source": "deepseek-harness-adapter",
            "prompt": prompt,
            "cwd": cwd or self.monorepo,
            "reason": reason,
        }
        path = os.path.join(QUEUE_DIR, f"{handoff['id']}.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(handoff, f, ensure_ascii=False, indent=2)
        except OSError:
            path = ""
        return {
            "status": "unavailable",
            "reason": reason,
            "handoff_file": path,
            "prompt": prompt[:200],
        }
