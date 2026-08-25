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
import re
import uuid
from collections.abc import Mapping
from typing import Dict, List, Any, Callable, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdd.spec_engine import (
    Specification,
    TrustedTestEvidence,
    _canonical_pytest_target,
    _canonical_spec_test_file,
    _issue_criterion_runtime_record,
    _issue_trusted_test_evidence,
    _strict_contract_targets_for_spec,
    spec_verifier,
)

logger = logging.getLogger("tdd-runner")
logger.setLevel(logging.INFO)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TDDRunner:
    """Executa o ciclo Red-Green-Refactor sobre uma especificação de tarefa."""

    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations

    def run_spec_test(self, spec: Specification) -> TrustedTestEvidence:
        """Executa a modalidade de evidência declarada pela especificação."""
        if getattr(spec, "requires_criterion_runtime_records", False):
            return self._run_criterion_runtime_spec_test(spec)
        return self._run_legacy_spec_test(spec)

    def _run_legacy_spec_test(self, spec: Specification) -> TrustedTestEvidence:
        """Executa o ``test_file`` vinculado e emite evidência selada.

        O caminho é deliberadamente fail-closed: arquivo ausente, caminho fora
        do repositório, resultado inconsistente ou exceção do executor jamais
        se tornam evidência verde. A saída do agente não participa da emissão.
        """
        spec_id = spec.spec_id if isinstance(spec.spec_id, str) else str(spec.spec_id)
        test_file = _canonical_spec_test_file(spec.test_file)
        if test_file is None:
            return _issue_trusted_test_evidence(
                spec_id,
                "",
                executed=False,
                passed=False,
                returncode=None,
                summary="test_file ausente, inválido ou fora do repositório.",
                error="invalid_test_file",
            )

        absolute_test_file = os.path.join(REPO_ROOT, test_file)
        # Uma spec pode vincular a entrega a uma suíte inteira (por exemplo,
        # ``tests``) quando seus critérios abrangem mais de um módulo. O alvo
        # ainda precisa existir e permanecer contido no checkout.
        if not (os.path.isfile(absolute_test_file) or os.path.isdir(absolute_test_file)):
            return _issue_trusted_test_evidence(
                spec_id,
                test_file,
                executed=False,
                passed=False,
                returncode=None,
                summary=f"Arquivo de teste não encontrado: {test_file}",
                error="test_file_not_found",
            )

        try:
            outcome = run_pytest(test_file)
        except Exception as exc:
            logger.warning(
                "Falha ao executar test_file da spec %s: %s", spec_id, exc
            )
            return _issue_trusted_test_evidence(
                spec_id,
                test_file,
                executed=False,
                passed=False,
                returncode=None,
                summary="Executor de testes indisponível.",
                error="test_runner_error",
            )

        if not isinstance(outcome, Mapping):
            return _issue_trusted_test_evidence(
                spec_id,
                test_file,
                executed=True,
                passed=False,
                returncode=None,
                summary="Executor de testes retornou um resultado inválido.",
                error="invalid_test_result",
            )

        try:
            raw_returncode = outcome.get("returncode")
            all_passed = outcome.get("all_passed") is True
            summary = outcome.get("summary", "")
            raw_error = outcome.get("error")
        except Exception as exc:
            logger.warning(
                "Resultado do executor da spec %s não pôde ser lido: %s",
                spec_id,
                exc,
            )
            return _issue_trusted_test_evidence(
                spec_id,
                test_file,
                executed=True,
                passed=False,
                returncode=None,
                summary="Resultado do executor de testes não pôde ser interpretado.",
                error="unreadable_test_result",
            )

        returncode = raw_returncode if type(raw_returncode) is int else None
        summary_text = summary if isinstance(summary, str) else str(summary)
        error = raw_error if isinstance(raw_error, str) else None
        passed = returncode == 0 and all_passed
        if not passed and error is None:
            error = "test_execution_failed"

        return _issue_trusted_test_evidence(
            spec_id,
            test_file,
            executed=True,
            passed=passed,
            returncode=returncode,
            summary=summary_text,
            error=error,
        )

    @staticmethod
    def _strict_outcome_fields(outcome: Any) -> Dict[str, Any]:
        """Converte um retorno de ``run_pytest`` em campos defensivos v1."""
        defaults: Dict[str, Any] = {
            "executed": True,
            "returncode": None,
            "summary": "Resultado de pytest inválido.",
            "error": "invalid_test_result",
            "passed_count": 0,
            "failed_count": 0,
            "skipped_count": 0,
            "xfailed_count": 0,
            "xpassed_count": 0,
            "error_count": 0,
            "collected_count": 0,
            "passed": False,
        }
        if not isinstance(outcome, Mapping):
            return defaults

        raw_returncode = outcome.get("returncode")
        returncode = raw_returncode if type(raw_returncode) is int else None
        raw_summary = outcome.get("summary", "")
        summary = raw_summary if isinstance(raw_summary, str) else str(raw_summary)
        raw_error = outcome.get("error")
        if raw_error is None:
            error: Optional[str] = None
        elif isinstance(raw_error, str) and raw_error:
            error = raw_error
        else:
            error = "invalid_test_result"

        counts: Dict[str, int] = {}
        malformed_counts = False
        for key in (
            "passed_count",
            "failed_count",
            "skipped_count",
            "xfailed_count",
            "collected_count",
        ):
            value = outcome.get(key)
            if type(value) is not int or value < 0:
                malformed_counts = True
                counts[key] = 0
            else:
                counts[key] = value
        # Estes dois campos foram adicionados junto ao runtime v1. O fallback
        # zero mantém testes legados de adaptadores compatíveis, sem relaxar os
        # cinco contadores que estabelecem coleta e êxito por nodeid.
        for key in ("xpassed_count", "error_count"):
            value = outcome.get(key, 0)
            if type(value) is not int or value < 0:
                malformed_counts = True
                counts[key] = 0
            else:
                counts[key] = value

        timed_out = outcome.get("timed_out") is True or error == "timeout"
        if malformed_counts:
            error = error or "invalid_test_counts"
        elif timed_out:
            error = error or "timeout"

        passed = (
            returncode == 0
            and outcome.get("all_passed") is True
            and error is None
            and not timed_out
            and counts["passed_count"] >= 1
            and counts["collected_count"] >= 1
            and counts["failed_count"] == 0
            and counts["skipped_count"] == 0
            and counts["xfailed_count"] == 0
            and counts["xpassed_count"] == 0
            and counts["error_count"] == 0
        )
        return {
            "executed": True,
            "returncode": returncode,
            "summary": summary,
            "error": error,
            **counts,
            "passed": passed,
        }

    def _run_criterion_runtime_spec_test(
        self,
        spec: Specification,
    ) -> TrustedTestEvidence:
        """Executa todos os nodeids v1 e emite um registro selado por alvo."""
        spec_id = spec.spec_id if isinstance(spec.spec_id, str) else str(spec.spec_id)
        test_file = _canonical_spec_test_file(spec.test_file)
        contract_sha256 = getattr(spec, "evidence_contract_sha256", None)
        targets_by_criterion = _strict_contract_targets_for_spec(spec)
        if test_file is None or targets_by_criterion is None:
            detail = getattr(spec, "evidence_contract_error", None)
            return _issue_trusted_test_evidence(
                spec_id,
                test_file or "",
                executed=False,
                passed=False,
                returncode=None,
                summary="Contrato de evidência granular inválido; testes não executados.",
                error=(
                    f"invalid_evidence_contract: {detail}"
                    if isinstance(detail, str) and detail
                    else "invalid_evidence_contract"
                ),
                contract_sha256=(
                    contract_sha256 if isinstance(contract_sha256, str) else None
                ),
            )

        execution_id = uuid.uuid4().hex
        run_seal = object()
        records = []
        for criterion_id, targets in targets_by_criterion.items():
            for target in targets:
                try:
                    outcome = run_pytest(target)
                    fields = self._strict_outcome_fields(outcome)
                except Exception as exc:
                    logger.warning(
                        "Falha ao executar nodeid %s da spec %s: %s",
                        target,
                        spec_id,
                        exc,
                    )
                    fields = {
                        "executed": False,
                        "returncode": None,
                        "summary": "Executor de testes indisponível.",
                        "error": "test_runner_error",
                        "passed_count": 0,
                        "failed_count": 0,
                        "skipped_count": 0,
                        "xfailed_count": 0,
                        "xpassed_count": 0,
                        "error_count": 1,
                        "collected_count": 0,
                        "passed": False,
                    }
                records.append(
                    _issue_criterion_runtime_record(
                        spec_id=spec_id,
                        test_file=test_file,
                        criterion_id=criterion_id,
                        test_target=target,
                        executed=fields["executed"],
                        passed=fields["passed"],
                        returncode=fields["returncode"],
                        summary=fields["summary"],
                        error=fields["error"],
                        passed_count=fields["passed_count"],
                        failed_count=fields["failed_count"],
                        skipped_count=fields["skipped_count"],
                        xfailed_count=fields["xfailed_count"],
                        xpassed_count=fields["xpassed_count"],
                        error_count=fields["error_count"],
                        collected_count=fields["collected_count"],
                        contract_sha256=contract_sha256,
                        execution_id=execution_id,
                        _run_seal=run_seal,
                    )
                )

        all_records_passed = bool(records) and all(record.passed for record in records)
        failing_returncodes = [
            record.returncode
            for record in records
            if type(record.returncode) is int and record.returncode != 0
        ]
        returncode: Optional[int]
        if all_records_passed:
            returncode = 0
        elif failing_returncodes:
            returncode = failing_returncodes[0]
        else:
            returncode = None
        passed_count = sum(1 for record in records if record.passed)
        return _issue_trusted_test_evidence(
            spec_id,
            test_file,
            # Cada alvo foi tentado, mesmo se um deles falhou. A validade do
            # registro individual, e não este agregado, determina cada critério.
            executed=bool(records),
            passed=all_records_passed,
            returncode=returncode,
            summary=(
                f"{passed_count}/{len(records)} nodeid(s) de critério aprovados."
            ),
            error=None if all_records_passed else "criterion_test_execution_failed",
            contract_sha256=contract_sha256,
            criterion_records=tuple(records),
            execution_id=execution_id,
            _run_seal=run_seal,
        )

    def run_spec_tests(self, spec: Specification) -> TrustedTestEvidence:
        """Alias explícito para consumidores que usam o plural histórico."""
        return self.run_spec_test(spec)

    def _verify_output(self, spec: Specification, output: Any) -> Dict[str, Any]:
        """Verifica a entrega e injeta prova de teste apenas quando ela é exigida."""
        trusted_test_evidence = (
            self.run_spec_test(spec)
            if spec.requires_trusted_test_evidence
            else None
        )
        return spec_verifier.verify(
            spec.spec_id,
            output,
            trusted_test_evidence=trusted_test_evidence,
        )

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
            green_result = self._verify_output(spec, output)
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
            refactor_check = self._verify_output(spec, refactored)
            history.append({"phase": "refactor", "verification": refactor_check})
            if refactor_check["verified"]:
                output = refactored  # aceita a refatoração somente se continuar verde
                logger.info(f"[REFACTOR] {spec.spec_id}: mantido verde, refatoração aceita")
            else:
                logger.warning(f"[REFACTOR] {spec.spec_id}: refatoração quebrou critérios, revertida")

        spec.status = "verified"
        return {"phase": "verified", "success": True, "output": output, "history": history}


_PYTEST_SUMMARY_COUNT_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?P<count>\d+)\s+"
    r"(?P<label>passed|failed|skipped|xfailed|xpassed|errors?)(?![A-Za-z0-9_])",
    re.IGNORECASE,
)
_PYTEST_COLLECTED_RE = re.compile(
    r"collected\s+(?P<count>\d+)\s+items?",
    re.IGNORECASE,
)


def _closed_pytest_result(
    *,
    returncode: Optional[int],
    summary: str,
    error: Optional[str],
    timed_out: bool = False,
    passed_count: int = 0,
    failed_count: int = 0,
    skipped_count: int = 0,
    xfailed_count: int = 0,
    xpassed_count: int = 0,
    error_count: int = 0,
    collected_count: int = 0,
) -> Dict[str, Any]:
    """Produz a forma defensiva única consumida pelo runtime granular."""
    return {
        "returncode": returncode,
        "all_passed": returncode == 0 and error is None,
        "summary": summary,
        "error": error,
        "timed_out": timed_out,
        "timeout_count": 1 if timed_out else 0,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "skipped_count": skipped_count,
        "xfailed_count": xfailed_count,
        "xpassed_count": xpassed_count,
        "error_count": error_count,
        "collected_count": collected_count,
    }


def _parse_pytest_counts(output: str, returncode: Optional[int]) -> Dict[str, int]:
    """Extrai contagens conservadoras da última linha-resumo do pytest."""
    counts = {
        "passed_count": 0,
        "failed_count": 0,
        "skipped_count": 0,
        "xfailed_count": 0,
        "xpassed_count": 0,
        "error_count": 0,
        "collected_count": 0,
    }
    summary_line = ""
    for line in reversed(output.splitlines()):
        if _PYTEST_SUMMARY_COUNT_RE.search(line) or "no tests ran" in line.casefold():
            summary_line = line
            break
    for match in _PYTEST_SUMMARY_COUNT_RE.finditer(summary_line):
        count = int(match.group("count"))
        label = match.group("label").casefold()
        key = {
            "passed": "passed_count",
            "failed": "failed_count",
            "skipped": "skipped_count",
            "xfailed": "xfailed_count",
            "xpassed": "xpassed_count",
            "error": "error_count",
            "errors": "error_count",
        }[label]
        counts[key] += count

    collected_matches = list(_PYTEST_COLLECTED_RE.finditer(output))
    if collected_matches:
        counts["collected_count"] = int(collected_matches[-1].group("count"))
    else:
        counts["collected_count"] = sum(
            counts[key]
            for key in (
                "passed_count",
                "failed_count",
                "skipped_count",
                "xfailed_count",
                "xpassed_count",
            )
        )

    # Códigos não verdes sem item reprovado explícito normalmente representam
    # erro de coleta/uso. Não os deixamos parecer uma execução sem erro.
    if returncode not in (None, 0) and not (
        counts["failed_count"] or counts["error_count"]
    ):
        counts["error_count"] = 1
    return counts


def run_pytest(test_path: str = "tests/", timeout: int = 1200) -> Dict[str, Any]:
    """
    Executa a bateria pytest real do repositório e retorna resultado estruturado.
    Usado pelo agente coder/auditor para metacognição de qualidade de código.
    """
    canonical_target = _canonical_pytest_target(test_path)
    if canonical_target is None:
        return _closed_pytest_result(
            returncode=None,
            summary="Alvo de teste ausente, inválido ou fora do repositório.",
            error="invalid_test_target",
            error_count=1,
        )
    if type(timeout) is not int or timeout <= 0:
        return _closed_pytest_result(
            returncode=None,
            summary="Timeout de pytest ausente ou inválido.",
            error="invalid_test_timeout",
            error_count=1,
        )

    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=no", "--", canonical_target]
    try:
        proc = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return _closed_pytest_result(
            returncode=None,
            summary=f"Tempo esgotado ao executar pytest em {canonical_target}.",
            error="timeout",
            timed_out=True,
            error_count=1,
        )
    except Exception as exc:
        logger.warning("Não foi possível executar pytest em %s: %s", canonical_target, exc)
        return _closed_pytest_result(
            returncode=None,
            summary=f"Falha ao executar pytest em {canonical_target}: {exc}",
            error="runner_error",
            error_count=1,
        )

    stdout = proc.stdout if isinstance(proc.stdout, str) else ""
    stderr = proc.stderr if isinstance(proc.stderr, str) else ""
    output = "\n".join(part for part in (stdout, stderr) if part)
    returncode = proc.returncode if type(proc.returncode) is int else None
    counts = _parse_pytest_counts(output, returncode)
    lines = [line for line in output.splitlines() if line.strip()]
    summary = lines[-1] if lines else ""
    error = None if returncode == 0 else "test_execution_failed"
    return _closed_pytest_result(
        returncode=returncode,
        summary=summary,
        error=error,
        **counts,
    )


# Singleton global
tdd_runner = TDDRunner()
