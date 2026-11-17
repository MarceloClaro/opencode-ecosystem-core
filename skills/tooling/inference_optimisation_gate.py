"""Gate metodológico da SPEC-935-R1119.

Adapta apenas a disciplina auditável observada em repositórios externos:
proveniência explícita, baseline, métrica, orçamento, holdout, replay do
contexto integral e limitações declaradas. Nenhum código externo é copiado e
nenhuma otimização ou medição de desempenho é executada aqui.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SPEC_ID = "SPEC-935-R1119"

PROVENANCE: dict[str, Any] = {
    "repositories": {
        "MarceloClaro/skills": {
            "id": 1462012681,
            "tree_sha": "e4bb5d960d87126ff3b3a8af1a104b7db67560ba",
            "fork": True,
            "nature": "catálogo de Agent Skills; licenças por skill",
        },
        "MarceloClaro/paper-orchestra": {
            "id": 1461999883,
            "tree_sha": "d9bae997e793a015ed38bb1605be9eb58c00284f",
            "fork": True,
            "nature": "orquestração metodológica de escrita científica",
        },
        "MarceloClaro/inference-optimisation-skill": {
            "id": 1462014706,
            "tree_sha": "fda968e7fc1996aa23c67139c755fe541c9d4be0",
            "fork": True,
            "nature": "metodologia local de hill-climb e ledger auditável",
        },
    },
    "external_code_copied": False,
    "adaptation": "methodology_only",
    "rea_observation_id": "4baf8413-f1e5-4190-a606-2038bb931adc",
}

_REQUIRED_PROVENANCE = ("repo", "commit", "retrieved_at")
_REQUIRED_METHODOLOGY = ("baseline", "metric", "budget", "holdout")


def _check(criterion: str, ok: bool, evidence: str) -> dict[str, str]:
    """Cria um registro determinístico de verificação."""

    return {
        "criterion": criterion,
        "status": "PASS" if ok else "BLOCKED",
        "evidence": evidence,
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    """Devolve um mapeamento vazio quando a entrada não é um mapeamento."""

    return value if isinstance(value, Mapping) else {}


def _nonempty_text(value: Any) -> bool:
    """Valida texto não vazio sem normalizar ou descartar o original."""

    return isinstance(value, str) and bool(value.strip())


def evaluate_adaptation_contract(config: Mapping[str, Any]) -> dict[str, Any]:
    """Avalia um contrato de adoção metodológica sem efeitos externos.

    A função é pura: não lê arquivos, não consulta serviços, não altera a
    entrada e não registra inferência de desempenho.
    """

    data = _mapping(config)
    checks: list[dict[str, str]] = []

    copied = data.get("external_code_copied")
    checks.append(
        _check(
            "external_code_copied",
            copied is False,
            "código externo não copiado" if copied is False else "cópia externa detectada",
        )
    )

    provenance = _mapping(data.get("provenance"))
    for field in _REQUIRED_PROVENANCE:
        value = provenance.get(field)
        ok = _nonempty_text(value)
        checks.append(
            _check(
                f"provenance.{field}",
                ok,
                f"campo {field} presente" if ok else f"campo {field} ausente ou vazio",
            )
        )

    methodology = _mapping(data.get("methodology"))
    for field in _REQUIRED_METHODOLOGY:
        value = methodology.get(field)
        ok = _nonempty_text(value)
        checks.append(
            _check(
                f"methodology.{field}",
                ok,
                f"campo {field} presente" if ok else f"campo {field} ausente ou vazio",
            )
        )

    validation = _mapping(data.get("validation"))
    replay = validation.get("full_context_replay")
    checks.append(
        _check(
            "validation.full_context_replay",
            replay is True,
            "replay integral exigido" if replay is True else "replay integral ausente",
        )
    )

    limitations = data.get("limitations")
    limitation_ok = False
    if isinstance(limitations, (list, tuple)):
        limitation_ok = any(
            _nonempty_text(item)
            and "não comprova desempenho" in str(item).lower()
            for item in limitations
        )
    checks.append(
        _check(
            "limitations",
            limitation_ok,
            "limitação de desempenho declarada"
            if limitation_ok
            else "limitação de desempenho ausente",
        )
    )

    blocked = sum(1 for item in checks if item["status"] == "BLOCKED")
    return {
        "spec_id": SPEC_ID,
        "status": "PASS" if blocked == 0 else "BLOCKED",
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": len(checks) - blocked,
            "blocked": blocked,
        },
    }


def render_gate_report(result: Mapping[str, Any]) -> str:
    """Renderiza um relatório markdown determinístico a partir do resultado."""

    data = _mapping(result)
    status = str(data.get("status", "BLOCKED"))
    spec = str(data.get("spec_id", SPEC_ID))
    summary = _mapping(data.get("summary"))

    lines = [
        f"# Relatório do Gate {spec}",
        "",
        f"- Status: **{status}**",
        f"- Verificações: {summary.get('total', 0)}",
        f"- Aprovadas: {summary.get('passed', 0)}",
        f"- Bloqueadas: {summary.get('blocked', 0)}",
        "",
        "## Verificações",
        "",
    ]

    checks = data.get("checks")
    if isinstance(checks, (list, tuple)):
        for item in checks:
            record = _mapping(item)
            lines.append(
                "- [{status}] {criterion}: {evidence}".format(
                    status=record.get("status", "BLOCKED"),
                    criterion=record.get("criterion", "desconhecido"),
                    evidence=record.get("evidence", "sem evidência"),
                )
            )

    lines.extend(
        [
            "",
            "## Limitação",
            "",
            "Este gate é metodológico e não comprova desempenho de inferência, "
            "causalidade, aceite editorial ou validação externa.",
            "",
            f"Proveniência REA: {PROVENANCE['rea_observation_id']}.",
        ]
    )
    return "\n".join(lines)
