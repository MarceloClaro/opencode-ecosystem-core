"""
Self-Correction Engine — Motor de Autocorreção em Circuito Fechado
===================================================================
Implementa o ciclo de 4 fases para autocorreção autônoma:
  Diagnóstico → Correção → Validação → Aplicação/Registro

Integrado com:
  - SpecVerifier (sdd/spec_engine.py) para validação RED -> GREEN
  - MetaBus (mci/metabus.py) para rastreabilidade metacognitiva
  - CORRIGENDUM.md para registro histórico transparente
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable
from typing import Any

from mci.metabus import metabus
from sdd.spec_engine import spec_verifier

logger = logging.getLogger("self-correction")
logger.setLevel(logging.INFO)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORRIGENDUM_PATH = os.path.join(REPO_ROOT, "CORRIGENDUM.md")


class SelfCorrectionEngine:
    """Motor de autocorreção autônoma em circuito fechado."""

    def __init__(
        self, corrigendum_path: os.PathLike[str] | str | None = None, *, history=None
    ):
        self.history: list[dict[str, Any]] = []
        self.tdd_history = history
        self.corrigendum_path = (
            os.fspath(corrigendum_path)
            if corrigendum_path is not None
            else CORRIGENDUM_PATH
        )

    def run_correction_cycle(
        self,
        spec_id: str,
        error_context: dict[str, Any],
        fix_fn: Callable[[], bool],
    ) -> dict[str, Any]:
        """Executa o fluxo completo: Diagnóstico -> Correção -> Validação -> Aplicação."""
        start_time = time.time()

        # 1. Diagnóstico
        issue_desc = error_context.get("description", "Falha não especificada")
        logger.info(
            "[FASE 1: DIAGNÓSTICO] Analisando falha em %s: %s", spec_id, issue_desc
        )

        spec = spec_verifier.registry.get(spec_id)
        if spec is None:
            return {
                "spec_id": spec_id,
                "success": False,
                "stage": "red",
                "error": "Especificação não encontrada.",
            }
        software_contract = bool(spec.test_file or spec.requires_trusted_test_evidence)
        history = self.tdd_history
        if software_contract:
            from pathlib import Path

            from sdd import spec_engine as spec_module
            from sdd.tdd_history import TDDHistory

            history = history or TDDHistory(root=spec_module.REPO_ROOT)
            if (
                type(history) is not TDDHistory
                or history.root != Path(spec_module.REPO_ROOT).resolve()
            ):
                preflight = {
                    "verified": False,
                    "reason_codes": ["history_scope_invalid"],
                }
            else:
                preflight = history.preflight(spec)
            if preflight.get("verified") is not True:
                return {
                    "spec_id": spec_id,
                    "success": False,
                    "stage": "red",
                    "red_history": preflight,
                }

        # 2. Correção (Tentativa de aplicar fix_fn em ambiente controlado)
        logger.info("[FASE 2: CORREÇÃO] Aplicando proposta de correção...")
        try:
            fix_applied = fix_fn()
        except Exception as exc:  # noqa: BLE001 — callback externo não possui classe única de falha.
            logger.error("[FASE 2: CORREÇÃO] Falha ao executar fix_fn: %s", exc)
            fix_applied = False

        if not fix_applied:
            return {
                "spec_id": spec_id,
                "success": False,
                "stage": "patch",
                "error": "Função de correção retornou False ou falhou.",
            }

        # 3. Validação (Testes formais via SpecVerifier RED -> GREEN)
        logger.info(
            "[FASE 3: VALIDAÇÃO] Verificando critérios da especificação %s...", spec_id
        )
        evidence = None
        if software_contract:
            from sdd.tdd_runner import TDDRunner

            evidence = TDDRunner().run_delivery_test(spec, history=history)
        verification = spec_verifier.verify(
            spec_id,
            {"status": "corrected", "fix_applied": True},
            trusted_test_evidence=evidence,
            require_red_history=software_contract,
            history=history,
        )

        is_valid = verification.get("verified", False)
        if not is_valid:
            logger.warning(
                "[FASE 3: VALIDAÇÃO] Correção não atendeu aos critérios da spec %s.",
                spec_id,
            )
            return {
                "spec_id": spec_id,
                "success": False,
                "stage": "validation",
                "verification_result": verification,
            }

        # 4. Aplicação & Registro (MetaBus + CORRIGENDUM.md)
        duration = round(time.time() - start_time, 3)
        record = {
            "spec_id": spec_id,
            "issue": issue_desc,
            "success": True,
            "duration_seconds": duration,
            "timestamp": time.time(),
        }
        self.history.append(record)

        metabus.publish_subsystem_event(
            "self_correction",
            "correction.applied",
            record,
            source_agent="self_correction_engine",
        )

        self._append_to_corrigendum(spec_id, issue_desc, duration)

        logger.info(
            "[FASE 4: APLICAÇÃO] Autocorreção concluída com sucesso em %.3fs!", duration
        )
        return {
            "spec_id": spec_id,
            "success": True,
            "stage": "applied",
            "duration_seconds": duration,
            "verification_result": verification,
        }

    def _append_to_corrigendum(self, spec_id: str, issue: str, duration: float) -> None:
        """Registra a autocorreção bem-sucedida no arquivo CORRIGENDUM.md."""
        if not os.path.exists(self.corrigendum_path):
            return

        try:
            entry = f"\n- **[Autocorreção Circuito Fechado - {time.strftime('%Y-%m-%d %H:%M:%S')}]**: Spec `{spec_id}` — {issue} (verificado em {duration}s)\n"
            with open(self.corrigendum_path, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as exc:  # noqa: BLE001 — registro auxiliar não altera o aceite do teste.
            logger.warning("Falha ao atualizar CORRIGENDUM.md: %s", exc)

    def get_correction_history(self) -> list[dict[str, Any]]:
        return list(self.history)


self_correction_engine = SelfCorrectionEngine()
