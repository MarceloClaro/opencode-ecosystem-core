# -*- coding: utf-8 -*-
"""Auditoria de risco epistêmico do Core (SPEC-935-R1132).

Detecta overclaim, falsa objetividade, viés de automação, perda de habilidades,
sobrecarga de atenção/manutenção e confiança sem calibração. As regras são
heurísticas estruturais; não medem eficácia nem substituem revisão humana.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_SEVERITY = {"info": 0, "warning": 1, "critical": 2}

OVERCLAIM = "overclaim"
UNFALSIFIABLE = "unfalsifiable"
FALSE_OBJECTIVITY = "false_objectivity"
CONFIDENCE_WITHOUT_EVIDENCE = "confidence_without_evidence"
EVIDENCE_WITHOUT_HASH = "evidence_without_hash"
AUTOMATION_BIAS = "automation_bias"
DESKILLING = "deskilling"
ATTENTION_OVERLOAD = "attention_overload"
MAINTENANCE_OVERLOAD = "maintenance_overload"
TRUST_WITHOUT_CALIBRATION = "trust_without_calibration"
OVERCLAIM_POLICY_MISSING = "overclaim_policy_missing"

MITIGATIONS = {
    OVERCLAIM: "require_external_validation",
    UNFALSIFIABLE: "add_falsifier",
    FALSE_OBJECTIVITY: "show_evidence_not_just_score",
    CONFIDENCE_WITHOUT_EVIDENCE: "lower_confidence_or_add_evidence",
    EVIDENCE_WITHOUT_HASH: "attach_source_hash",
    AUTOMATION_BIAS: "independent_first_pass",
    DESKILLING: "no_tool_session",
    ATTENTION_OVERLOAD: "pause_and_resume",
    MAINTENANCE_OVERLOAD: "stop_and_simplify",
    TRUST_WITHOUT_CALIBRATION: "calibration_exercise",
    OVERCLAIM_POLICY_MISSING: "restore_corrigendum_and_gate",
}


@dataclass(frozen=True)
class RiskFinding:
    code: str
    severity: str
    message: str
    evidence: dict[str, Any]
    mitigation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _finding(
    code: str,
    severity: str,
    message: str,
    evidence: dict[str, Any] | None = None,
) -> RiskFinding:
    if severity not in _SEVERITY:
        raise ValueError(f"severidade inválida: {severity}")
    return RiskFinding(
        code=code,
        severity=severity,
        message=message,
        evidence=evidence or {},
        mitigation=MITIGATIONS[code],
    )


def _valid_external(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("independent") is True
        and isinstance(value.get("verifier"), str)
        and bool(value["verifier"].strip())
        and isinstance(value.get("artifact_sha256"), str)
        and bool(_HEX64.fullmatch(value["artifact_sha256"]))
    )


def _evidence_count(claim: dict[str, Any]) -> int:
    evidence = claim.get("evidence")
    if not isinstance(evidence, list):
        return 0
    return len(evidence)


def _missing_hashes(claim: dict[str, Any]) -> int:
    evidence = claim.get("evidence")
    if not isinstance(evidence, list):
        return 0
    count = 0
    for item in evidence:
        if not isinstance(item, dict):
            count += 1
            continue
        if not isinstance(item.get("source_sha256"), str) or not _HEX64.fullmatch(
            item["source_sha256"]
        ):
            count += 1
        if item.get("literal_verified") is not True:
            count += 1
    return count


def audit_claim(
    claim: dict[str, Any],
    *,
    external_validation: dict[str, Any] | None = None,
    trust_score: float | None = None,
) -> list[RiskFinding]:
    """Audita um claim isolado.

    O claim deve conter, no mínimo, ``text``, ``confidence``, ``evidence`` e
    ``falsifier``. ``status`` é opcional; ``verified`` e
    ``externally_validated`` exigem validação externa independente.
    """

    if not isinstance(claim, dict):
        raise ValueError("claim deve ser um objeto")
    text = claim.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("claim.text deve ser texto não vazio")
    confidence = claim.get("confidence", 0.0)
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError("claim.confidence deve ser numérico")
    if not 0.0 <= float(confidence) <= 1.0:
        raise ValueError("claim.confidence deve estar em [0, 1]")

    findings: list[RiskFinding] = []
    status = str(claim.get("status", "inference")).lower()
    external_ok = _valid_external(external_validation)

    if status in {"verified", "externally_validated"} and not external_ok:
        findings.append(
            _finding(
                OVERCLAIM,
                "critical",
                "Claim declarado verificado sem validação externa independente.",
                {"status": status, "text": text[:160]},
            )
        )

    falsifier = claim.get("falsifier")
    if not isinstance(falsifier, str) or not falsifier.strip():
        findings.append(
            _finding(
                UNFALSIFIABLE,
                "warning",
                "Claim sem critério de refutação declarado.",
                {"text": text[:160]},
            )
        )

    evidence_count = _evidence_count(claim)
    if trust_score is not None:
        if isinstance(trust_score, bool) or not isinstance(trust_score, (int, float)):
            raise ValueError("trust_score deve ser numérico")
        if not 0.0 <= float(trust_score) <= 1.0:
            raise ValueError("trust_score deve estar em [0, 1]")
        if float(trust_score) >= 0.8 and evidence_count == 0:
            findings.append(
                _finding(
                    FALSE_OBJECTIVITY,
                    "critical",
                    "Trust score alto tratado como se fosse evidência, sem evidência anexada.",
                    {"trust_score": float(trust_score), "evidence_count": 0},
                )
            )

    if float(confidence) >= 0.8 and evidence_count == 0:
        findings.append(
            _finding(
                CONFIDENCE_WITHOUT_EVIDENCE,
                "warning",
                "Confiança alta sem evidência anexada.",
                {"confidence": float(confidence), "evidence_count": 0},
            )
        )

    missing_hashes = _missing_hashes(claim)
    if missing_hashes:
        findings.append(
            _finding(
                EVIDENCE_WITHOUT_HASH,
                "warning",
                "Evidência sem hash de fonte ou sem verificação literal.",
                {"missing": missing_hashes, "total": evidence_count},
            )
        )

    return sorted(findings, key=lambda item: (-_SEVERITY[item.severity], item.code))


def audit_session(session: dict[str, Any]) -> list[RiskFinding]:
    """Audita uma sessão de uso, com foco em automação e cuidado."""

    if not isinstance(session, dict):
        raise ValueError("session deve ser um objeto")
    findings: list[RiskFinding] = []

    accepted = session.get("agent_output_accepted") is True
    independent = session.get("independent_judgment") is True
    external = session.get("external_validation") is True
    if accepted and not independent and not external:
        findings.append(
            _finding(
                AUTOMATION_BIAS,
                "critical",
                "Saída do agente aceita sem julgamento independente nem validação externa.",
                {
                    "agent_output_accepted": True,
                    "independent_judgment": False,
                    "external_validation": False,
                },
            )
        )

    manual = session.get("manual_verifications", 0)
    without_manual = session.get("sessions_without_manual", 0)
    if isinstance(manual, int) and isinstance(without_manual, int):
        if manual == 0 and without_manual >= 5:
            findings.append(
                _finding(
                    DESKILLING,
                    "warning",
                    "Cinco ou mais sessões sem verificação manual; risco de perda de habilidade.",
                    {"manual_verifications": 0, "sessions_without_manual": without_manual},
                )
            )

    minutes = session.get("session_minutes", 0)
    switches = session.get("context_switches", 0)
    if isinstance(minutes, (int, float)) and minutes >= 120:
        findings.append(
            _finding(
                ATTENTION_OVERLOAD,
                "warning",
                "Sessão longa; risco de fadiga e perda de contexto.",
                {"session_minutes": minutes},
            )
        )
    if isinstance(switches, int) and switches >= 20:
        findings.append(
            _finding(
                ATTENTION_OVERLOAD,
                "warning",
                "Muitas trocas de contexto; risco de fragmentação da atenção.",
                {"context_switches": switches},
            )
        )

    maintenance = session.get("maintenance_minutes", 0)
    productive = session.get("productive_minutes", 0)
    if isinstance(maintenance, (int, float)) and isinstance(productive, (int, float)):
        if productive > 0 and maintenance / productive >= 1.0:
            findings.append(
                _finding(
                    MAINTENANCE_OVERLOAD,
                    "warning",
                    "Tempo de manutenção maior ou igual ao tempo produtivo.",
                    {"maintenance_minutes": maintenance, "productive_minutes": productive},
                )
            )

    trust = session.get("trust_score")
    if isinstance(trust, (int, float)) and trust >= 0.8 and session.get("calibration_checked") is not True:
        findings.append(
            _finding(
                TRUST_WITHOUT_CALIBRATION,
                "warning",
                "Confiança alta sem verificação de calibração.",
                {"trust_score": trust},
            )
        )

    return sorted(findings, key=lambda item: (-_SEVERITY[item.severity], item.code))


def audit_repository(repo_root: str | Path) -> dict[str, Any]:
    """Auditoria estrutural do checkout, sem executar o sistema."""

    root = Path(repo_root)
    specs = len(list((root / "specs").glob("SPEC-*.md")))
    tests = len(list((root / "tests").glob("test_*.py")))
    cycles_path = root / "evolution" / "cycles.json"
    cycles = 0
    if cycles_path.exists():
        try:
            payload = json.loads(cycles_path.read_text(encoding="utf-8"))
            cycles = len(payload.get("cycles", []))
        except (OSError, ValueError, TypeError):
            cycles = 0

    findings: list[RiskFinding] = []
    if cycles > 0:
        specs_per_cycle = specs / cycles
        tests_per_cycle = tests / cycles
        if specs_per_cycle > 3.0 or tests_per_cycle > 3.0:
            findings.append(
                _finding(
                    MAINTENANCE_OVERLOAD,
                    "warning",
                    "Razão de especificações/testes por ciclo acima do limiar estrutural.",
                    {
                        "specs": specs,
                        "tests": tests,
                        "cycles": cycles,
                        "specs_per_cycle": round(specs_per_cycle, 3),
                        "tests_per_cycle": round(tests_per_cycle, 3),
                    },
                )
            )

    if not (root / "CORRIGENDUM.md").exists() or not (
        root / "mci" / "metacognitive_gate.py"
    ).exists():
        findings.append(
            _finding(
                OVERCLAIM_POLICY_MISSING,
                "critical",
                "Política pública de correção ou gate metacognitivo ausente.",
                {
                    "corrigendum": (root / "CORRIGENDUM.md").exists(),
                    "metacognitive_gate": (root / "mci" / "metacognitive_gate.py").exists(),
                },
            )
        )

    return {
        "status": summarize(findings)["status"],
        "counts": {"specs": specs, "tests": tests, "cycles": cycles},
        "findings": [finding.to_dict() for finding in findings],
    }


def recommend(findings: Iterable[RiskFinding]) -> list[dict[str, str]]:
    """Converte achados em mitigações legíveis."""

    return [
        {
            "code": finding.code,
            "severity": finding.severity,
            "mitigation": finding.mitigation,
            "message": finding.message,
        }
        for finding in findings
    ]


def summarize(findings: Iterable[RiskFinding]) -> dict[str, Any]:
    items = list(findings)
    critical = sum(1 for item in items if item.severity == "critical")
    warning = sum(1 for item in items if item.severity == "warning")
    if critical:
        status = "fail"
    elif warning:
        status = "warn"
    else:
        status = "pass"
    return {
        "status": status,
        "total": len(items),
        "critical": critical,
        "warning": warning,
        "findings": [item.to_dict() for item in items],
    }
