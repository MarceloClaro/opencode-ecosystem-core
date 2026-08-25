# -*- coding: utf-8 -*-
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

import os
import time
import logging
from typing import Dict, List, Any, Callable, Optional

from sdd.spec_engine import spec_verifier
from mci.metabus import metabus

logger = logging.getLogger("self-correction")
logger.setLevel(logging.INFO)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORRIGENDUM_PATH = os.path.join(REPO_ROOT, "CORRIGENDUM.md")


class SelfCorrectionEngine:
    """Motor de autocorreção autônoma em circuito fechado."""

    def __init__(self, corrigendum_path: Optional[os.PathLike[str] | str] = None):
        self.history: List[Dict[str, Any]] = []
        self.corrigendum_path = (
            os.fspath(corrigendum_path)
            if corrigendum_path is not None
            else CORRIGENDUM_PATH
        )

    def run_correction_cycle(
        self,
        spec_id: str,
        error_context: Dict[str, Any],
        fix_fn: Callable[[], bool],
    ) -> Dict[str, Any]:
        """Executa o fluxo completo: Diagnóstico -> Correção -> Validação -> Aplicação."""
        start_time = time.time()
        
        # 1. Diagnóstico
        issue_desc = error_context.get("description", "Falha não especificada")
        logger.info("[FASE 1: DIAGNÓSTICO] Analisando falha em %s: %s", spec_id, issue_desc)

        # 2. Correção (Tentativa de aplicar fix_fn em ambiente controlado)
        logger.info("[FASE 2: CORREÇÃO] Aplicando proposta de correção...")
        try:
            fix_applied = fix_fn()
        except Exception as exc:
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
        logger.info("[FASE 3: VALIDAÇÃO] Verificando critérios da especificação %s...", spec_id)
        verification = spec_verifier.verify(spec_id, {"status": "corrected", "fix_applied": True})
        
        is_valid = verification.get("verified", False)
        if not is_valid:
            logger.warning("[FASE 3: VALIDAÇÃO] Correção não atendeu aos critérios da spec %s.", spec_id)
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

        logger.info("[FASE 4: APLICAÇÃO] Autocorreção concluída com sucesso em %.3fs!", duration)
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
        except Exception as exc:
            logger.warning("Falha ao atualizar CORRIGENDUM.md: %s", exc)

    def get_correction_history(self) -> List[Dict[str, Any]]:
        return list(self.history)


self_correction_engine = SelfCorrectionEngine()
