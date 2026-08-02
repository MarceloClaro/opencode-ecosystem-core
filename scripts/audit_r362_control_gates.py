#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica SpecVerifier e BehavioralGate à R362 sem abrir o release."""

from __future__ import annotations

import hashlib
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from economy.token_economy import SLASH_RATE, TokenEconomy  # noqa: E402
from sdd.spec_engine import spec_registry, spec_verifier  # noqa: E402
from scripts.audit_r362_pdf_layout import (  # noqa: E402
    BUILD_RECEIPTS_PATH,
    EDITIONS,
    _receipt_is_current,
    parse_latex_log,
)
from scripts.generate_r362_change_manifest import validate_manifest  # noqa: E402
from trust import create_trust_engine  # noqa: E402


BASE = ROOT / "validacao_externa" / "cultural_episteme"
PREFLIGHT_PATH = BASE / "molambudos_r362_preflight.json"
MANIFEST_PATH = BASE / "molambudos_r362_change_manifest.json"
CONTROL_PATH = BASE / "molambudos_r362_control_gates.json"
CANDIDATE_PATH = BASE / "molambudos_r362_control_gates.candidate.json"
LOCK_PATH = BASE / ".molambudos_r362_control_gates.lock"
EXPECTED_BOOTSTRAP_TESTS = 61
EXPECTED_FINAL_TESTS = 62
REGRESSION_TESTS = (
    "tests/test_r358_molambudos_polimento_cultural.py",
    "tests/test_r359_cultural_episteme_agent.py",
    "tests/test_r360_cultural_episteme_pilot.py",
    "tests/test_r361_molambudos_cultural_decision_matrix.py",
    "tests/test_r362_molambudos_route_a_pagination_preflight.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _all_flags_closed(payload: dict[str, Any]) -> bool:
    return bool(
        payload.get("external_validation") is False
        and payload.get("human_review_required") is True
        and payload.get("release_gate") == "blocked"
        and payload.get("quality_verdict_allowed") is False
    )


def _editions(preflight: dict[str, Any]) -> list[dict[str, Any]]:
    return list(preflight.get("editions", {}).values())


def _workspace_file(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f"caminho fora do workspace: {relative}")
    return path


def _artifact_freshness(preflight: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if (
        not BUILD_RECEIPTS_PATH.is_file()
        or preflight.get("build_receipts_sha256") != _sha256(BUILD_RECEIPTS_PATH)
    ):
        errors.append("recibo central de builds ausente ou divergente")
    expected_paths = {
        key: {
            "pdf_path": edition.pdf,
            "log_path": edition.log,
            "aux_path": edition.aux,
            "fls_path": edition.fls,
        }
        for key, edition in EDITIONS.items()
    }
    editions = preflight.get("editions", {})
    if set(editions) != set(EDITIONS):
        errors.append("conjunto de edições do preflight divergente")
    for key, edition in EDITIONS.items():
        report = editions.get(key, {})
        for field, expected_path in expected_paths[key].items():
            try:
                reported_path = _workspace_file(report.get(field, ""))
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if reported_path != expected_path.resolve():
                errors.append(f"{key}.{field} não aponta para artefato canônico")
        hash_fields = {
            "pdf_sha256": edition.pdf,
            "log_sha256": edition.log,
            "aux_sha256": edition.aux,
            "fls_sha256": edition.fls,
        }
        for field, path in hash_fields.items():
            if not path.is_file() or report.get(field) != _sha256(path):
                errors.append(f"{key}.{field} obsoleto")
        receipt = report.get("build", {})
        if not _receipt_is_current(edition, receipt):
            errors.append(f"recibo de build {key} não está atual")
        if edition.log.is_file():
            parsed = parse_latex_log(
                edition.log.read_text(encoding="utf-8", errors="replace")
            )
            if parsed != report.get("log") or parsed.get("passed") is not True:
                errors.append(f"log {key} diverge do relatório ou contém bloqueio")
    return {
        "passed": not errors,
        "errors": errors,
        "validated_edition_count": len(EDITIONS),
        "build_receipts_sha256": (
            _sha256(BUILD_RECEIPTS_PATH) if BUILD_RECEIPTS_PATH.is_file() else None
        ),
    }


def _register_criteria() -> None:
    spec = spec_registry.get("SPEC-935-R362")
    if spec is None:
        raise RuntimeError("SPEC-935-R362 não registrada")
    if spec.criteria:
        if len(spec.criteria) != 12:
            raise RuntimeError("registro parcial de critérios R362 detectado")
        return

    spec.add_criterion(
        "Nenhum arquivo ativo associa Senador Pompeu/Patu ao campo de 1915--1917",
        lambda out: out["preflight"]["source_checks"]["passed"] is True
        and out["preflight"]["source_checks"]["active_dependency_corpus"]["passed"] is True
        and all(
            not item["forbidden_route_phrases"]
            for item in out["preflight"]["source_checks"]["historical_route_a"].values()
        ),
    )
    spec.add_criterion(
        "Rota A trilíngue implementa origem, deslocamento e confinamento",
        lambda out: all(
            item["route_origin_and_destination"]
            and item["fortaleza_present"]
            and item["alagadico_confinement"]
            for item in out["preflight"]["source_checks"]["historical_route_a"].values()
        ),
    )
    spec.add_criterion(
        "Números não sustentados e pseudoarquivos afetados foram tratados",
        lambda out: all(
            not item["unsupported_exact_counts"]
            and item["pseudoarchives_marked_fictional"] is True
            for item in out["preflight"]["source_checks"]["historical_route_a"].values()
        ),
    )
    spec.add_criterion(
        "Paginação romana e arábica é válida nas cinco edições",
        lambda out: len(_editions(out["preflight"])) == 5
        and all(
            item["pagination"]["passed"] is True
            and item["pagination"]["frontmatter_style"] == "roman"
            and item["pagination"]["first_fragment_label"] == "1"
            and item["pagination"]["first_fragment_destination_matches"] is True
            and item["pagination"]["foliation_sequence_passed"] is True
            and item["all_page_dimensions_match_source_geometry"] is True
            and not item["pagination"]["duplicate_page_labels"]
            for item in _editions(out["preflight"])
        ),
    )
    spec.add_criterion(
        "Cinco builds em duas passadas e logs bloqueantes limpos",
        lambda out: len(_editions(out["preflight"])) == 5
        and all(
            item["build"]["passed"] is True
            and item["build"]["passes"] == 2
            and item["build"]["receipt_current"] is True
            and item["log"]["passed"] is True
            for item in _editions(out["preflight"])
        )
        and out["freshness"]["passed"] is True,
    )
    spec.add_criterion(
        "Auditor PDF não encontra conteúdo não permitido fora das caixas",
        lambda out: all(
            item["layout"]["passed"] is True
            and item["layout"]["violation_count"] == 0
            and item["layout"]["zone_violation_count"] == 0
            and len(item["layout"]["page_reports"]) == item["page_count"]
            for item in _editions(out["preflight"])
        ),
    )
    spec.add_criterion(
        "Exceções full bleed são identificadas e justificadas",
        lambda out: all(
            len(item["layout"]["full_bleed_exceptions"]) == 8
            and item["layout"]["full_bleed_allowlist_passed"] is True
            and all(
                exception["page_index"] >= 0
                and exception["source"].strip()
                and exception["justification"].strip()
                and len(exception["source_sha256"]) == 64
                for exception in item["layout"]["full_bleed_exceptions"]
            )
            for item in _editions(out["preflight"])
        ),
    )
    spec.add_criterion(
        "Rotas trilíngues concluem 540/540 sem ausências ou divergências",
        lambda out: out["preflight"]["routes"]["passed"] is True
        and out["preflight"]["routes"]["expected"]
        == out["preflight"]["routes"]["total"]
        == out["preflight"]["routes"]["valid"]
        == 540
        and out["preflight"]["routes"]["by_language"]
        == {"pt": 180, "en": 180, "zh": 180}
        and len(out["preflight"]["routes"]["editions"]) == 5
        and all(
            item["passed"] is True and item["source_multiset_match"] is True
            for item in out["preflight"]["routes"]["editions"].values()
        ),
    )
    spec.add_criterion(
        "Correções tipográficas são locais e preservam a narrativa global",
        lambda out: out["preflight"]["source_typography"]["passed"] is True
        and out["preflight"]["source_typography"]["global_narrative_class"] == "14pt"
        and out["preflight"]["source_typography"]["table_minimum"] == r"\footnotesize",
    )
    spec.add_criterion(
        "Regressão R358--R362 e encadeamento de proveniência passam",
        lambda out: out["regression"]["passed"] is True
        and out["regression"]["failed"] == 0
        and out["provenance"]["passed"] is True,
    )
    spec.add_criterion(
        "Somente patu_1915_chronology avança e nove bloqueios permanecem",
        lambda out: len(out["manifest"]["blockers"]) == 10
        and len(
            [
                item for item in out["manifest"]["blockers"]
                if item["blocker_id"] == "patu_1915_chronology"
                and item["status"] == "implemented_pending_external_review"
                and item["automatic_change_applied"] is True
            ]
        ) == 1
        and len(
            [
                item for item in out["manifest"]["blockers"]
                if item["blocker_id"] != "patu_1915_chronology"
                and item["status"] == "blocked_author_decision"
                and item["automatic_change_applied"] is False
            ]
        ) == 9,
    )
    spec.add_criterion(
        "Anti-overclaim e release bloqueado em todos os artefatos",
        lambda out: _all_flags_closed(out["preflight"])
        and _all_flags_closed(out["manifest"])
        and out["preflight"]["publication_constraints"]["release_allowed"] is False,
    )


def _junit_counts(path: Path) -> dict[str, int]:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    return {
        key: sum(int(suite.attrib.get(key, 0)) for suite in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }


def _run_pytest_gate(
    *, expected_tests: int, evidence_name: str, exclude_control: bool, control_override: Path | None = None
) -> dict[str, Any]:
    evidence_path = BASE / evidence_name
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{evidence_name}.", suffix=".tmp", dir=BASE
    )
    os.close(descriptor)
    Path(temporary_name).unlink()
    command = [sys.executable, "-m", "pytest", "-q", *REGRESSION_TESTS]
    if exclude_control:
        command.extend(
            ["-k", "not test_r362_control_gate_never_opens_release_or_claims_external_validation"]
        )
    command.append(f"--junitxml={temporary_name}")
    environment = os.environ.copy()
    if control_override is not None:
        environment["R362_CONTROL_PATH"] = str(control_override.resolve())
    completed = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, env=environment
    )
    combined = completed.stdout + "\n" + completed.stderr
    counts = {"tests": 0, "failures": 0, "errors": 1, "skipped": 0}
    temporary = Path(temporary_name)
    if temporary.is_file():
        try:
            counts = _junit_counts(temporary)
            os.replace(temporary, evidence_path)
        finally:
            if temporary.exists():
                temporary.unlink()
    passed_count = counts["tests"] - counts["failures"] - counts["errors"] - counts["skipped"]
    passed = bool(
        completed.returncode == 0
        and counts["tests"] == expected_tests
        and counts["failures"] == 0
        and counts["errors"] == 0
        and counts["skipped"] == 0
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "expected_test_count": expected_tests,
        "passed": passed,
        "passed_count": passed_count,
        "failed": counts["failures"],
        "errors": counts["errors"],
        "skipped": counts["skipped"],
        "total": counts["tests"],
        "junit_path": str(evidence_path.relative_to(ROOT)),
        "junit_sha256": _sha256(evidence_path) if evidence_path.is_file() else None,
        "output_tail": "\n".join(combined.splitlines()[-30:]),
        "excluded_bootstrap_test": (
            "test_r362_control_gate_never_opens_release_or_claims_external_validation"
            if exclude_control
            else None
        ),
    }


def _run_regression() -> dict[str, Any]:
    return _run_pytest_gate(
        expected_tests=EXPECTED_BOOTSTRAP_TESTS,
        evidence_name="molambudos_r362_regression_bootstrap.xml",
        exclude_control=True,
    )


def _run_candidate_regression(candidate_path: Path) -> dict[str, Any]:
    return _run_pytest_gate(
        expected_tests=EXPECTED_FINAL_TESTS,
        evidence_name="molambudos_r362_regression_final.xml",
        exclude_control=False,
        control_override=candidate_path,
    )


def _audit_economy() -> dict[str, Any]:
    economy = TokenEconomy()
    failures = (
        ("marceloclaro", "r362-sequential-build-interrupted-before-artifact", 1.0),
        ("marceloclaro", "r362-route-validator-import-path", 1.0),
        ("marceloclaro", "r362-provenance-regression-chain", 1.0),
        ("marceloclaro", "r362-premature-green-before-adversarial-review", 2.0),
        ("18_agente_engenharia_dados_datasets_proveniencia", "r362-provenance-subtask-cancelled", 1.0),
    )
    successes = (
        ("codebase-analyzer", "ses_0411935acffevuOw5rUnk9lBz4", 1.5),
        ("code-reviewer", "ses_040419cefffe6MIIVVsllUyQiF", 1.5),
        ("marceloclaro", "SPEC-935-R362-final-gates", 2.0),
    )
    failed_outcomes = []
    successful_outcomes = []
    for agent_id, task_id, stake in failures:
        if economy.commit(agent_id, task_id, stake) is None:
            raise RuntimeError(f"stake não criado para falha {task_id}")
        failed_outcomes.append(economy.resolve(task_id, success=False))
    for agent_id, task_id, stake in successes:
        if economy.commit(agent_id, task_id, stake) is None:
            raise RuntimeError(f"stake não criado para sucesso {task_id}")
        successful_outcomes.append(economy.resolve(task_id, success=True))
    return {
        "slash_rate": SLASH_RATE,
        "failures": failed_outcomes,
        "successes": successful_outcomes,
        "report": economy.report(),
        "audit_trail": economy.ledger.audit_trail(),
    }


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
        directory_fd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary = Path(temporary_name)
        if temporary.exists():
            temporary.unlink()


@contextmanager
def _control_lock():
    with LOCK_PATH.open("a+", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _invalidate_published_control(reason: str) -> None:
    _atomic_write(
        CONTROL_PATH,
        {
            "spec_id": "SPEC-935-R362",
            "generated_at": "2026-08-01",
            "external_validation": False,
            "human_review_required": True,
            "release_gate": "blocked",
            "quality_verdict_allowed": False,
            "spec_lifecycle_status": "red",
            "communicable_status": "gate_execution_in_progress_or_failed",
            "sdd_gate": {
                "verified": False,
                "status": "red",
                "external_validation_conferred": False,
                "release_conferred": False,
            },
            "behavioral_gate": {"allowed": False, "opens_release": False},
            "invalidation_reason": reason,
            "safe_claim": "Gate inválido ou em execução; nenhum estado verde ou release pode ser comunicado.",
        },
    )


def _publish_candidate(candidate: Path) -> None:
    os.replace(candidate, CONTROL_PATH)
    directory_fd = os.open(CONTROL_PATH.parent, os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def main() -> int:
    with _control_lock():
        _invalidate_published_control("nova execução do gate; publicação atômica ainda não concluída")
        if CANDIDATE_PATH.exists():
            CANDIDATE_PATH.unlink()

        preflight = _load(PREFLIGHT_PATH)
        manifest = _load(MANIFEST_PATH)
        freshness = _artifact_freshness(preflight)
        provenance = validate_manifest(manifest)
        if not freshness["passed"]:
            raise RuntimeError(f"gate de frescor reprovado: {freshness}")
        if not provenance["passed"]:
            raise RuntimeError(f"gate de proveniência reprovado: {provenance}")

        regression = _run_regression()
        if not regression["passed"]:
            raise RuntimeError(f"regressão bootstrap R358--R362 reprovada: {regression}")

        artifact = {
            "preflight": preflight,
            "manifest": manifest,
            "regression": regression,
            "freshness": freshness,
            "provenance": provenance,
        }
        _register_criteria()
        sdd_gate = spec_verifier.verify("SPEC-935-R362", artifact)
        if not sdd_gate["verified"]:
            raise RuntimeError(f"SpecVerifier reprovou: {sdd_gate}")
        sdd_gate.update(
            {
                "verifier": "SpecVerifier",
                "verification_scope": "internal_spec_conformance",
                "status_scope": "sdd_tdd",
                "external_validation_conferred": False,
                "release_conferred": False,
            }
        )

        trust = create_trust_engine()
        behavioral = trust.execute("r362_finalize_route_a_preflight", required_trust=0.4)
        if not behavioral.allowed:
            raise RuntimeError(f"BehavioralGate bloqueou: {behavioral.reason}")
        trust_outcome = trust.learn(
            "r362_finalize_route_a_preflight",
            success=True,
            delta=0.1,
            context="recibos íntegros, cinco preflights por zona, rotas multi-PDF e release bloqueado",
        )
        behavioral_payload = asdict(behavioral)
        behavioral_payload["opens_release"] = False

        control = {
            "spec_id": "SPEC-935-R362",
            "generated_at": "2026-08-01",
            "external_validation": False,
            "human_review_required": True,
            "release_gate": "blocked",
            "quality_verdict_allowed": False,
            "spec_lifecycle_status": sdd_gate["status"],
            "communicable_status": "internal_spec_checks_passed_release_blocked",
            "preflight_sha256": _sha256(PREFLIGHT_PATH),
            "change_manifest_sha256": _sha256(MANIFEST_PATH),
            "regression_contract": {
                "bootstrap_expected": EXPECTED_BOOTSTRAP_TESTS,
                "final_expected": EXPECTED_FINAL_TESTS,
                "skips_allowed": 0,
                "xfails_allowed": 0,
            },
            "regression": regression,
            "artifact_freshness_gate": freshness,
            "provenance_gate": provenance,
            "sdd_gate": sdd_gate,
            "behavioral_gate": behavioral_payload,
            "trust_outcome": asdict(trust_outcome),
            "trust_status": trust.status,
            "token_economy": _audit_economy(),
            "publication_constraints": preflight["publication_constraints"],
            "adversarial_review_gate": {
                "review_task_id": "ses_040419cefffe6MIIVVsllUyQiF",
                "initial_status": "FAIL_WITH_INTERNAL_BLOCKERS",
                "remediation_status": "implemented_pending_final_adversarial_review",
                "opens_release": False,
            },
            "safe_claim": (
                "Os critérios internos SDD/TDD da R362 passaram no candidato atômico. "
                "Isso não confere validação externa, qualidade literária ou autorização "
                "de publicação; nove bloqueios R361 e a restrição KDP permanecem."
            ),
        }
        _atomic_write(CANDIDATE_PATH, control)
        final_regression = _run_candidate_regression(CANDIDATE_PATH)
        if not final_regression["passed"]:
            CANDIDATE_PATH.unlink(missing_ok=True)
            raise RuntimeError(f"regressão do candidato R362 reprovada: {final_regression}")

        post_freshness = _artifact_freshness(preflight)
        post_provenance = validate_manifest(manifest)
        if (
            not post_freshness["passed"]
            or not post_provenance["passed"]
            or control["preflight_sha256"] != _sha256(PREFLIGHT_PATH)
            or control["change_manifest_sha256"] != _sha256(MANIFEST_PATH)
        ):
            CANDIDATE_PATH.unlink(missing_ok=True)
            raise RuntimeError("artefatos mudaram durante a regressão do candidato")
        control["post_control_regression"] = final_regression
        control["post_regression_freshness_gate"] = post_freshness
        control["post_regression_provenance_gate"] = post_provenance
        _atomic_write(CANDIDATE_PATH, control)
        _publish_candidate(CANDIDATE_PATH)

        print(
            f"R362 control gates: SDD {sdd_gate['passed_count']}/{sdd_gate['total_count']}; "
            f"bootstrap {regression['passed_count']}/{regression['total']}; "
            f"candidato {final_regression['passed_count']}/{final_regression['total']}; "
            "release bloqueado."
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
