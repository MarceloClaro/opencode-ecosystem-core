"""Auditoria determinística de Loop Engineering (R1100).

O módulo lê uma especificação de loop e devolve um checklist pontuado.
Ele não executa o loop, não acessa a rede e não escreve arquivos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

LEVELS = ("L0", "L1", "L2", "L3")
CRITICAL = ("stop", "verification", "maker_checker", "state", "safety")
WEIGHTS = {
    "purpose": 1.0,
    "trigger": 1.0,
    "action": 0.5,
    "stop": 1.5,
    "verification": 1.5,
    "maker_checker": 1.5,
    "state": 1.0,
    "budget": 0.5,
    "observability": 0.5,
    "safety": 1.0,
}
MAX_SCORE = sum(WEIGHTS.values())


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _section(text: str, title: str) -> str:
    match = re.search(rf"^##\s+{re.escape(title)}\s*$", text, re.M)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"^##\s+", text[start:], re.M)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def _field(text: str, label: str) -> str:
    pattern = (
        rf"(?:^|\n)\s*(?:[-*]\s*)?(?:\*\*)?{re.escape(label)}"
        rf"(?:\*\*)?\s*:\s*(.+)"
    )
    match = re.search(pattern, text, re.I)
    return match.group(1).strip() if match else ""


def parse_loop_markdown(text: str) -> dict[str, Any]:
    """Converte o formato de ``specs/loops/*.md`` em um dicionário auditável."""
    name = ""
    first = re.search(r"^#\s+(.+?)\s+—\s+Loop Specification\s*$", text, re.M)
    if first:
        name = first.group(1).strip()

    descricao = _field(text, "Descrição")
    use_quando = _field(text, "Use quando")
    trigger = _section(text, "Trigger")
    objetivo = _section(text, "Objetivo e Verificação")
    arquitetura = _section(text, "Arquitetura")
    estados = _section(text, "Estados Terminais Nomeados")
    parada = _section(text, "Regra de Parada")
    memoria = _section(text, "Memória")
    guardrails = _section(text, "Guardrails")

    check = _field(objetivo, "Check real")
    verificavel = "verificável: sim" in objetivo.lower() or "verificavel: sim" in objetivo.lower()
    cap = re.search(r"Teto de orçamento:\s*(\d+)", parada, re.I)
    hard_max = int(cap.group(1)) if cap else None
    maker_checker = "maker_checker" in arquitetura.lower() or "maker-checker" in arquitetura.lower()
    independente = any(
        termo in (check + " " + arquitetura).lower()
        for termo in ("determin", "gate", "maker_checker", "maker-checker")
    )

    return {
        "name": name,
        "purpose": descricao,
        "use_when": use_quando,
        "non_goals": [],
        "trigger": trigger,
        "action": arquitetura,
        "architecture": arquitetura,
        "terminal_states": re.findall(r"`([^`]+)`", estados),
        "stop_condition": parada,
        "hard_max_iterations": hard_max,
        "verification": {
            "kind": "deterministic" if "determin" in check.lower() else "text",
            "check": check,
            "independent": independente and verificavel,
        },
        "maker": "",
        "checker": "",
        "checker_read_only": None,
        "state": {"raw": memoria} if memoria else {},
        "budget": {"stop_raw": parada} if "orçamento" in parada.lower() else {},
        "observability": {},
        "safety": {"guardrails": guardrails} if guardrails else {},
        "requested_level": "L2",
        "observed_days": 0,
    }


def _check(
    name: str,
    points: float,
    reason: str,
) -> dict[str, Any]:
    weight = WEIGHTS[name]
    return {
        "points": round(points, 3),
        "max": weight,
        "ok": points >= weight,
        "reason": reason,
    }


def audit_loop(spec: dict[str, Any]) -> dict[str, Any]:
    """Pontua uma especificação de loop sem executá-la."""
    if not isinstance(spec, dict):
        raise ValueError("spec deve ser um dicionário")

    checks: dict[str, dict[str, Any]] = {}
    red_flags: list[str] = []
    missing: list[str] = []

    purpose = _text(spec.get("purpose") or spec.get("description"))
    non_goals = spec.get("non_goals") or spec.get("non_goals_text") or []
    non_goals_ok = bool(non_goals) if isinstance(non_goals, (list, tuple)) else bool(_text(non_goals))
    pontos = (0.5 if purpose else 0.0) + (0.5 if non_goals_ok else 0.0)
    checks["purpose"] = _check(
        "purpose", pontos,
        "objetivo presente" if purpose else "objetivo ausente",
    )
    if not non_goals_ok:
        checks["purpose"]["reason"] += "; não objetivos ausentes"
        missing.append("non_goals")
        red_flags.append("Objetivo sem não objetivos explícitos.")

    trigger = _text(spec.get("trigger"))
    checks["trigger"] = _check("trigger", 1.0 if trigger else 0.0,
                               "gatilho explícito" if trigger else "gatilho ausente")
    if not trigger:
        missing.append("trigger")

    action = _text(spec.get("action") or spec.get("architecture"))
    checks["action"] = _check("action", 0.5 if action else 0.0,
                              "ação/arquitetura presente" if action else "ação ausente")
    if not action:
        missing.append("action")

    stop = _text(spec.get("stop_condition") or spec.get("stop"))
    hard = spec.get("hard_max_iterations")
    hard_ok = isinstance(hard, int) and not isinstance(hard, bool) and hard > 0
    if not hard_ok:
        runtime = spec.get("max_runtime_minutes")
        hard_ok = isinstance(runtime, (int, float)) and not isinstance(runtime, bool) and runtime > 0
    if not hard_ok and stop:
        match = re.search(r"(?:teto de orçamento|max(?:imo)?(?:\s+de)?\s+itera[çc][õo]es)\D{0,12}(\d+)", stop, re.I)
        if match:
            hard_ok = int(match.group(1)) > 0
            hard = int(match.group(1))
    pontos = (0.75 if stop else 0.0) + (0.75 if hard_ok else 0.0)
    checks["stop"] = _check(
        "stop", pontos,
        "parada declarada" if stop else "parada ausente",
    )
    if not stop:
        missing.append("stop_condition")
    if not hard_ok:
        checks["stop"]["reason"] += "; sem teto duro de iterações/tempo"
        missing.append("hard_max_iterations")
        red_flags.append("Loop sem hard stop de iterações ou tempo.")

    verification = spec.get("verification")
    v_kind = ""
    v_check = ""
    v_independent = False
    if isinstance(verification, dict):
        v_kind = _text(verification.get("kind"))
        v_check = _text(verification.get("check") or verification.get("command"))
        v_independent = verification.get("independent") is True
    else:
        v_check = _text(verification)
        v_independent = any(t in v_check.lower() for t in ("determin", "teste", "gate"))
    if v_kind == "human":
        v_independent = False
    pontos = (0.75 if v_check else 0.0) + (0.75 if v_independent else 0.0)
    checks["verification"] = _check(
        "verification", pontos,
        "verificação declarada" if v_check else "verificação ausente",
    )
    if not v_check:
        missing.append("verification")
    if not v_independent:
        checks["verification"]["reason"] += "; verificador não independente"
        missing.append("verification.independent")
        red_flags.append("Verificação não é independente do executor.")

    maker = _text(spec.get("maker"))
    checker = _text(spec.get("checker"))
    read_only = spec.get("checker_read_only")
    architecture = _text(spec.get("architecture"))
    same_agent = bool(maker and checker and maker == checker)
    read_only_false = read_only is False
    full_mc = bool(maker and checker and maker != checker and read_only is True)
    partial_mc = bool(
        not full_mc
        and not same_agent
        and not read_only_false
        and (
            "maker_checker" in architecture.lower()
            or "maker-checker" in architecture.lower()
            or (maker and checker)
        )
    )
    pontos = 0.0 if (same_agent or read_only_false) else (1.5 if full_mc else (0.75 if partial_mc else 0.0))
    checks["maker_checker"] = _check(
        "maker_checker", pontos,
        "maker e checker separados" if full_mc else (
            "maker-checker declarado, papéis não verificados" if partial_mc else "sem separação maker/checker"
        ),
    )
    if same_agent:
        red_flags.append("Maker e checker são o mesmo agente/sessão.")
    if read_only_false:
        red_flags.append("Checker não é read-only.")
    if not full_mc:
        missing.append("maker_checker")

    state = spec.get("state")
    state_nonempty = (
        isinstance(state, dict) and bool(state)
    ) or (
        isinstance(state, str) and bool(state.strip())
    ) or bool(_text(spec.get("memory")))
    state_ok = False
    if isinstance(state, dict) and state:
        state_ok = bool(_text(state.get("path") or state.get("store"))) and bool(
            _text(state.get("schema") or state.get("fields"))
        ) and state.get("prune") is True
    pontos = 1.0 if state_ok else (0.5 if state_nonempty else 0.0)
    checks["state"] = _check(
        "state", pontos,
        "estado durável com schema e prune" if state_ok else (
            "memória declarada; schema/prune não verificados" if state_nonempty else "estado ausente"
        ),
    )
    if not state_ok:
        missing.append("state")
        red_flags.append("Loop sem estado durável com schema e prune.")

    budget = spec.get("budget")
    budget_ok = False
    budget_partial = False
    if isinstance(budget, dict) and budget:
        has_cap = any(
            isinstance(budget.get(k), (int, float)) and not isinstance(budget.get(k), bool) and budget.get(k) > 0
            for k in ("max_tokens_per_run", "max_tokens", "max_runs_per_day", "max_cost")
        )
        budget_ok = has_cap and bool(_text(budget.get("kill_switch")))
        budget_partial = True
    elif _text(spec.get("budget")) or "orçamento" in stop.lower():
        budget_partial = True
    pontos = 0.5 if budget_ok else (0.25 if budget_partial else 0.0)
    checks["budget"] = _check(
        "budget", pontos,
        "orçamento e kill switch" if budget_ok else (
            "orçamento parcial; kill switch não verificado" if budget_partial else "orçamento ausente"
        ),
    )
    if not budget_ok:
        missing.append("budget")

    observability = spec.get("observability")
    obs_ok = False
    obs_partial = False
    if isinstance(observability, dict) and observability:
        obs_ok = bool(_text(observability.get("run_log"))) and bool(observability.get("metrics"))
        obs_partial = True
    elif _text(observability):
        obs_partial = True
    pontos = 0.5 if obs_ok else (0.25 if obs_partial else 0.0)
    checks["observability"] = _check(
        "observability", pontos,
        "run log e métricas" if obs_ok else (
            "observabilidade parcial" if obs_partial else "observabilidade ausente"
        ),
    )
    if not obs_ok:
        missing.append("observability")

    safety = spec.get("safety")
    safety_nonempty = isinstance(safety, dict) and bool(safety)
    safety_ok = False
    auto_merge = False
    allowlist: list[Any] = []
    if safety_nonempty:
        auto_merge = safety.get("auto_merge") is True
        allowlist = safety.get("allowlist") or []
        safety_ok = (
            bool(safety.get("denylist"))
            and bool(_text(safety.get("human_gate")))
            and (not auto_merge or bool(allowlist))
        )
    pontos = 0.0 if (not safety_nonempty or (auto_merge and not allowlist)) else (
        1.0 if safety_ok else 0.5
    )
    checks["safety"] = _check(
        "safety", pontos,
        "denylist e gate humano" if safety_ok else (
            "guardrails parciais" if safety_nonempty else "safety ausente"
        ),
    )
    if not safety_ok:
        missing.append("safety")
    if auto_merge and not allowlist:
        red_flags.append("Auto-merge habilitado sem allowlist.")

    score = round(sum(item["points"] for item in checks.values()), 3)
    critical_zero = [name for name in CRITICAL if checks[name]["points"] <= 0]
    critical_partial = [
        name for name in CRITICAL
        if 0 < checks[name]["points"] < checks[name]["max"]
    ]

    if critical_zero:
        computed = "L1" if score >= 4.0 else "L0"
    elif critical_partial:
        computed = "L2" if score >= 7.0 else "L1"
    elif score >= 9.5:
        computed = "L3"
    elif score >= 7.0:
        computed = "L2"
    elif score >= 4.0:
        computed = "L1"
    else:
        computed = "L0"

    requested = _text(spec.get("requested_level") or "L1").upper()
    if requested not in LEVELS:
        requested = "L1"
    try:
        observed_days = float(spec.get("observed_days") or 0)
    except (TypeError, ValueError):
        observed_days = 0.0

    allowed = computed
    if LEVELS.index(allowed) > LEVELS.index(requested):
        allowed = requested
    if requested in ("L2", "L3") and observed_days < 1:
        allowed = "L1"
        red_flags.append("L2/L3 exigem ao menos 1 dia de L1 observado.")
    if requested == "L3" and observed_days < 7:
        if LEVELS.index(allowed) > LEVELS.index("L2"):
            allowed = "L2"
        red_flags.append("L3 exige ao menos 7 dias de L1 observado.")
    if computed == "L3" and observed_days < 7 and LEVELS.index(allowed) > LEVELS.index("L2"):
        allowed = "L2"

    for name in critical_zero:
        red_flags.append(f"Check crítico ausente: {name}.")
    for name in critical_partial:
        red_flags.append(f"Check crítico parcial: {name}.")

    return {
        "score": score,
        "max_score": round(MAX_SCORE, 3),
        "computed_level": computed,
        "allowed_level": allowed,
        "requested_level": requested,
        "observed_days": observed_days,
        "checks": checks,
        "critical_failures": critical_zero,
        "critical_partial": critical_partial,
        "red_flags": sorted(set(red_flags)),
        "missing": sorted(set(missing)),
        "human_review_required": True,
        "scientifically_validated": False,
        "limits": [
            "Checklist determinístico; não prova que o loop funciona.",
            "Não executa loop, não acessa rede e não mede produtividade.",
            "L3 exige uma semana de L1 observado, além dos checks.",
            "O humano continua responsável por custo, segurança e merge.",
        ],
    }


def audit_loop_file(path: str | Path) -> dict[str, Any]:
    """Audita um arquivo Markdown de loop e registra fonte e hash."""
    caminho = Path(path)
    texto = caminho.read_text(encoding="utf-8")
    resultado = audit_loop(parse_loop_markdown(texto))
    resultado["source"] = str(caminho)
    resultado["sha256"] = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    return resultado


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Auditor de Loop Engineering (R1100)")
    parser.add_argument("path", help="arquivo Markdown de especificação de loop")
    args = parser.parse_args(argv)
    resultado = audit_loop_file(args.path)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
