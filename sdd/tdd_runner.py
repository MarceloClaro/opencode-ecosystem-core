# -*- coding: utf-8 -*-
"""
TDD Runner — Ciclo Red-Green-Refactor
=====================================
Orquestra o ciclo TDD sobre entregas de agentes e integra com o
TransformerPipeline (gerar→verificar→revisar) e a memória metacognitiva:

- RED:      a especificação nasce com critérios definidos e nenhuma entrega
- GREEN:    a entrega mínima satisfaz todos os critérios (SpecVerifier)
- REFACTOR: novas iterações melhoram a entrega mantendo os critérios verdes

Também expõe `run_pytest()` para executar a bateria real de testes do
repositório e reportar o resultado ao Global Workspace (metacognição de código).

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import os
import sys
import subprocess
import logging
from typing import Dict, List, Any, Callable, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdd.spec_engine import spec_registry, spec_verifier, Specification

logger = logging.getLogger("tdd-runner")
logger.setLevel(logging.INFO)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TDDRunner:
    """Executa o ciclo Red-Green-Refactor sobre uma especificação de tarefa."""

    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations

    def run_cycle(self, spec: Specification,
                  producer_fn: Callable[[str, Dict[str, Any]], Any],
                  refactor_fn: Optional[Callable[[Any, Dict[str, Any]], Any]] = None) -> Dict[str, Any]:
        """
        Ciclo TDD completo:
        1. RED: valida que a spec tem critérios e que nada foi entregue ainda
        2. GREEN: chama producer_fn até os critérios passarem (máx. N iterações)
        3. REFACTOR: se refactor_fn for dada, melhora a entrega e re-verifica
        """
        history: List[Dict[str, Any]] = []

        # --- FASE RED ---
        if not spec.criteria:
            return {"phase": "red", "success": False,
                    "error": "Spec sem critérios de aceitação: TDD exige critérios antes da implementação."}
        spec.status = "red"
        red_check = spec_verifier.verify(spec.spec_id, None)
        history.append({"phase": "red", "verification": red_check})
        logger.info(f"[RED] {spec.spec_id}: {red_check['passed_count']}/{red_check['total_count']} (esperado: 0)")

        # --- FASE GREEN ---
        output = None
        green_result = None
        for iteration in range(1, self.max_iterations + 1):
            feedback = {"iteration": iteration, "last_verification": green_result}
            output = producer_fn(spec.objective, feedback)
            green_result = spec_verifier.verify(spec.spec_id, output)
            history.append({"phase": "green", "iteration": iteration, "verification": green_result})
            logger.info(f"[GREEN it.{iteration}] {spec.spec_id}: "
                        f"{green_result['passed_count']}/{green_result['total_count']}")
            if green_result["verified"]:
                break

        if not (green_result and green_result["verified"]):
            return {"phase": "green", "success": False, "output": output, "history": history}

        # --- FASE REFACTOR ---
        if refactor_fn is not None:
            refactored = refactor_fn(output, {"spec": spec.to_dict()})
            refactor_check = spec_verifier.verify(spec.spec_id, refactored)
            history.append({"phase": "refactor", "verification": refactor_check})
            if refactor_check["verified"]:
                output = refactored  # aceita a refatoração somente se continuar verde
                logger.info(f"[REFACTOR] {spec.spec_id}: mantido verde, refatoração aceita")
            else:
                logger.warning(f"[REFACTOR] {spec.spec_id}: refatoração quebrou critérios, revertida")

        spec.status = "verified"
        return {"phase": "verified", "success": True, "output": output, "history": history}


def run_pytest(test_path: str = "tests/") -> Dict[str, Any]:
    """
    Executa a bateria pytest real do repositório e retorna resultado estruturado.
    Usado pelo agente coder/auditor para metacognição de qualidade de código.
    """
    cmd = [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no"]
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=300)
    output = proc.stdout.strip().splitlines()
    summary = output[-1] if output else ""
    return {
        "returncode": proc.returncode,
        "all_passed": proc.returncode == 0,
        "summary": summary,
    }


# Singleton global
tdd_runner = TDDRunner()
