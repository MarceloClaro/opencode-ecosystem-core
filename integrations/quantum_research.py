"""Deterministic research planning for NISQ and quantum-method gap analysis.

This module prepares a research protocol; it does not solve problems, execute
circuits, contact providers, or establish quantum advantage. The input is a
strict JSON contract and all declared readiness fields remain unverified.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from typing import Any


MAX_CLI_INPUT_BYTES = 1_000_000
MAX_TEXT_LENGTH = 1_000
MAX_LIST_ITEMS = 64
MAX_REFERENCE_LENGTH = 240


class QuantumResearchContractError(ValueError):
    """Invalid or over-budget input with a stable public error type."""


_METHODS: tuple[dict[str, Any], ...] = (
    {
        "id": "classical_baselines",
        "name": "Baselines clássicos",
        "family": "classical",
        "required_inputs": [
            "problem_formulation", "baseline_selection_rationale", "comparison_baseline"
        ],
        "protocol": [
            "Fixar formulação, instâncias, métricas, limites de tempo/memória e critérios de parada.",
            "Usar método exato apenas em instâncias cujo limite seja declarado; comparar heurísticas sob orçamento equivalente.",
        ],
        "limitations": [
            "Baseline escolhido deve corresponder à estrutura do problema; não usar comparação incompatível.",
            "Um ótimo exato de instância pequena não demonstra escalabilidade.",
        ],
    },
    {
        "id": "hybrid_variational",
        "name": "Métodos variacionais híbridos clássico-quânticos",
        "family": "hybrid_quantum_classical",
        "required_inputs": [
            "problem_encoding", "classical_optimizer", "noise_characterization",
            "measurement_budget", "comparison_baseline",
        ],
        "protocol": [
            "Justificar a codificação e a relação entre função objetivo e observáveis medidos.",
            "Declarar ansatz/profundidade, otimizador, inicialização, shots, seeds, repetições e regra de parada.",
            "Comparar com baseline clássico no mesmo conjunto de instâncias e orçamento reportado.",
        ],
        "limitations": [
            "QAOA/VQE e otimizadores são candidatos de pesquisa, não garantia de solução ou vantagem.",
            "Ruído, barren plateaus, custo de amostragem e compilação devem ser medidos no contexto concreto.",
        ],
    },
    {
        "id": "classical_simulation",
        "name": "Simulação clássica de circuitos/dinâmicas quânticas",
        "family": "simulation",
        "required_inputs": [
            "circuit_or_dynamics_spec", "qubit_count", "simulator_resource_budget",
            "benchmark_instances",
        ],
        "protocol": [
            "Especificar circuito/dinâmica, observáveis, modelo de ruído e simulador pretendido.",
            "Registrar método (statevector, tensor network/MPS ou simulação ruidosa), memória, tempo e limites.",
            "Separar simulação exata, aproximação e execução em dispositivo; registrar erro de aproximação.",
        ],
        "limitations": [
            "Simulação clássica não é execução em QPU; limites dependem da estrutura e do hardware clássico.",
            "Statevector cresce exponencialmente em qubits; MPS/tensor networks dependem de entanglement e bond dimension.",
        ],
    },
    {
        "id": "quantum_annealing",
        "name": "Cozi­mento quântico / annealing",
        "family": "annealing",
        "required_inputs": [
            "qubo_or_ising_encoding", "penalty_validation", "embedding_or_connectivity",
            "anneal_schedule_or_simulator", "comparison_baseline",
        ],
        "protocol": [
            "Validar que o QUBO/Ising representa o objetivo e que penalidades não alteram indevidamente o ótimo.",
            "Documentar conectividade/embedding, precisão de coeficientes, cadeia, escala e agenda de annealing.",
            "Reportar amostras, distribuição de energia, violações de restrição e baseline clássico.",
        ],
        "limitations": [
            "Um annealer clássico ou simulador não equivale a hardware quântico.",
            "Embedding, cadeia e escala podem dominar custo e qualidade; não inferir otimalidade da melhor amostra.",
        ],
    },
    {
        "id": "quantum_cellular_automata",
        "name": "Autômatos celulares quânticos",
        "family": "quantum_dynamics",
        "required_inputs": [
            "state_space", "local_rule", "boundary_conditions", "evolution_validity",
            "comparison_baseline",
        ],
        "protocol": [
            "Formalizar espaço de estados, regra local, vizinhança, condições de contorno e estado inicial.",
            "Demonstrar/validar as condições matemáticas de evolução exigidas pelo modelo escolhido (por exemplo, localidade e unitariedade quando aplicáveis).",
            "Definir observáveis, invariantes, tamanho finito, baseline clássico e testes de convergência.",
        ],
        "limitations": [
            "O rótulo Tiangong `CA` não é interpretado como autômato celular quântico sem fonte confirmatória.",
            "Nenhuma dinâmica, regra ou solver QCA é implementado por este planejador.",
        ],
    },
    {
        "id": "error_mitigation",
        "name": "Mitigação de erros em NISQ",
        "family": "error_mitigation",
        "required_inputs": [
            "noise_model_or_calibration", "raw_observables", "mitigation_method",
            "shot_overhead_budget", "unmitigated_baseline",
        ],
        "protocol": [
            "Preservar resultados brutos e não mitigados; especificar calibração e janela de validade.",
            "Comparar técnicas candidatas (readout calibration, ZNE, PEC ou dynamical decoupling) apenas quando suas hipóteses se aplicarem.",
            "Reportar overhead de shots/tempo, incerteza, estabilidade e sensibilidade ao modelo de ruído.",
        ],
        "limitations": [
            "Mitigação não elimina ruído nem corrige automaticamente erros de formulação.",
            "PEC pode ter overhead elevado; ZNE depende de extrapolação; calibração e DD são dependentes do dispositivo.",
        ],
    },
)

_METHOD_BY_ID = {method["id"]: method for method in _METHODS}
_METHOD_IDS = tuple(method["id"] for method in _METHODS)
_APP_LABELS = ("VRP", "WSA", "HDR", "QSS", "OPC", "PTO", "CA", "RSA", "ECC", "SDES")
_APP_URL = "https://tiangongqs.com/application/quantum-application/{}"
_REA_EVIDENCE_ID = "ev_d4fafa5023de258fbccba21eaec6f8845ddd4302d6467740bdc659f0018808ef"
_REA_ROOT_SHA256 = "bfddef3dce8945269bcadd62a18f83ddc11740260ac2f20420e8863f9ad79888"

_APP_LOCAL_STATUS: dict[str, dict[str, str | None]] = {
    "VRP": {
        "capture": "partial_static_capture",
        "local_harness_status": "classical_only",
        "local_route": "integrations.tiangong_mcp.vrp_handler",
        "local_scope": "Heurística clássica CVRP; não é QAOA e não prova ótimo.",
    },
    "HDR": {
        "capture": "partial_static_capture",
        "local_harness_status": "preprocessing_only",
        "local_route": "integrations.tiangong_mcp.hdr_handler",
        "local_scope": "Validação/pré-processamento; reconhecimento retorna indisponível.",
    },
}


def _json_hash(value: Any) -> str:
    try:
        encoded = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise QuantumResearchContractError("solicitação não pode ser canonicalizada como JSON finito.") from exc
    return hashlib.sha256(encoded).hexdigest()


def research_catalog() -> dict[str, Any]:
    """Return research method candidates and their prerequisites; never executes them."""
    return {
        "schema_version": 1,
        "methods": copy.deepcopy(list(_METHODS)),
        "method_semantics": "candidatos para investigação; não são recomendações automáticas",
        "network": False,
        "execution_attempted": False,
        "limitations": [
            "Catálogo metodológico estático; não avalia adequação sem problema, dados e evidência.",
            "Presença de um método no catálogo não significa implementação, disponibilidade de dependência, simulador ou QPU.",
        ],
    }


def tiangong_application_catalog() -> list[dict[str, Any]]:
    """Return the ten user-supplied labels without inferring their expansions."""
    rows: list[dict[str, Any]] = []
    for label in _APP_LABELS:
        local = _APP_LOCAL_STATUS.get(label)
        rows.append({
            "label": label,
            "url": _APP_URL.format(label),
            "source_semantics": "unverified",
            "capture_status": (
                local["capture"] if local else "not_captured_in_existing_R1089_bundle"
            ),
            "local_harness_status": (
                local["local_harness_status"] if local else "not_implemented_pending_contract"
            ),
            "local_route": local["local_route"] if local else None,
            "local_scope": local["local_scope"] if local else None,
            "evidence_refs": ["SPEC-935-R1089", _REA_EVIDENCE_ID],
            "rea_root_sha256": _REA_ROOT_SHA256,
            "runtime_or_backend_observed": False,
        })
    return rows


def _text(value: Any, field: str, *, max_length: int = MAX_TEXT_LENGTH) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise QuantumResearchContractError(f"{field} deve ser texto ou null.")
    value = value.strip()
    if len(value) > max_length:
        raise QuantumResearchContractError(f"{field} excede {max_length} caracteres.")
    return value or None


def _text_list(value: Any, field: str, *, limit: int = MAX_LIST_ITEMS,
               item_length: int = MAX_TEXT_LENGTH) -> list[str]:
    if not isinstance(value, list) or len(value) > limit:
        raise QuantumResearchContractError(f"{field} deve ser lista com até {limit} itens.")
    result: list[str] = []
    for index, item in enumerate(value):
        text = _text(item, f"{field}[{index}]", max_length=item_length)
        if text is None:
            raise QuantumResearchContractError(f"{field}[{index}] não pode ser vazio.")
        result.append(text)
    return result


def _positive_number(value: Any, field: str, *, integer: bool = False,
                     maximum: float = 1_000_000_000) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise QuantumResearchContractError(f"{field} deve ser número positivo finito.")
    if integer and not isinstance(value, int):
        raise QuantumResearchContractError(f"{field} deve ser inteiro positivo.")
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise QuantumResearchContractError(f"{field} deve ser número positivo finito.") from exc
    if not math.isfinite(number) or number <= 0 or number > maximum:
        raise QuantumResearchContractError(f"{field} fora do limite positivo finito.")
    return int(value) if integer else number


def _normalize_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise QuantumResearchContractError("payload deve ser objeto JSON.")
    allowed = {
        "schema_version", "question", "application_label", "problem_class", "objective",
        "constraints", "baseline_methods", "evaluation_metrics", "evidence_refs",
        "candidate_methods", "method_inputs", "resource_limits", "seed",
    }
    if set(payload) - allowed:
        raise QuantumResearchContractError("payload contém chaves não permitidas.")
    if type(payload.get("schema_version")) is not int or payload["schema_version"] != 1:
        raise QuantumResearchContractError("schema_version deve ser o inteiro 1.")

    app_label = payload.get("application_label")
    if app_label is not None and (not isinstance(app_label, str) or app_label not in _APP_LABELS):
        raise QuantumResearchContractError("application_label deve ser um dos dez rótulos Tiangong exatos.")

    raw_methods = payload.get("candidate_methods")
    if raw_methods is None:
        candidate_methods = list(_METHOD_IDS)
    else:
        candidate_methods = _text_list(raw_methods, "candidate_methods", limit=len(_METHOD_IDS), item_length=80)
        if not candidate_methods:
            raise QuantumResearchContractError("candidate_methods não pode ser vazio quando informado.")
        if len(candidate_methods) != len(set(candidate_methods)):
            raise QuantumResearchContractError("candidate_methods não aceita duplicatas.")
        if any(method not in _METHOD_BY_ID for method in candidate_methods):
            raise QuantumResearchContractError("candidate_methods contém método desconhecido.")

    raw_method_inputs = payload.get("method_inputs", {})
    if not isinstance(raw_method_inputs, dict):
        raise QuantumResearchContractError("method_inputs deve ser objeto.")
    if set(raw_method_inputs) - set(candidate_methods):
        raise QuantumResearchContractError("method_inputs só pode declarar métodos candidatos.")
    method_inputs: dict[str, list[str]] = {}
    for method_id, raw_fields in raw_method_inputs.items():
        if not isinstance(method_id, str) or method_id not in _METHOD_BY_ID:
            raise QuantumResearchContractError("method_inputs contém método desconhecido.")
        fields = _text_list(raw_fields, f"method_inputs.{method_id}", limit=32, item_length=100)
        allowed_fields = set(_METHOD_BY_ID[method_id]["required_inputs"])
        if set(fields) - allowed_fields:
            raise QuantumResearchContractError(f"method_inputs.{method_id} contém pré-requisito desconhecido.")
        if len(fields) != len(set(fields)):
            raise QuantumResearchContractError(f"method_inputs.{method_id} não aceita duplicatas.")
        method_inputs[method_id] = sorted(fields)

    raw_limits = payload.get("resource_limits", {})
    if not isinstance(raw_limits, dict):
        raise QuantumResearchContractError("resource_limits deve ser objeto.")
    limit_schema = {
        "qubits": (True, 100_000),
        "shots": (True, 1_000_000_000),
        "simulator_memory_gib": (False, 1_000_000),
        "runtime_seconds": (False, 1_000_000_000),
    }
    if set(raw_limits) - set(limit_schema):
        raise QuantumResearchContractError("resource_limits contém campo desconhecido.")
    resource_limits = {
        key: _positive_number(value, f"resource_limits.{key}", integer=limit_schema[key][0], maximum=limit_schema[key][1])
        for key, value in raw_limits.items()
    }

    seed = payload.get("seed")
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed <= 2**32 - 1):
        raise QuantumResearchContractError("seed deve ser inteiro em 0..2^32-1.")

    return {
        "schema_version": 1,
        "question": _text(payload.get("question"), "question"),
        "application_label": app_label,
        "problem_class": _text(payload.get("problem_class"), "problem_class", max_length=120),
        "objective": _text(payload.get("objective"), "objective", max_length=300),
        "constraints": _text_list(payload.get("constraints", []), "constraints", limit=MAX_LIST_ITEMS),
        "baseline_methods": _text_list(payload.get("baseline_methods", []), "baseline_methods", limit=32, item_length=200),
        "evaluation_metrics": _text_list(payload.get("evaluation_metrics", []), "evaluation_metrics", limit=32, item_length=200),
        "evidence_refs": _text_list(payload.get("evidence_refs", []), "evidence_refs", limit=64, item_length=MAX_REFERENCE_LENGTH),
        "candidate_methods": candidate_methods,
        "method_inputs": method_inputs,
        "resource_limits": resource_limits,
        "seed": seed,
    }


def _gap(field: str, description: str, next_step: str, severity: str = "high") -> dict[str, str]:
    return {"field": field, "severity": severity, "description": description, "next_step": next_step}


def build_research_plan(payload: Any) -> dict[str, Any]:
    """Build an auditable method/gap plan from declared inputs, without execution."""
    request = _normalize_payload(payload)
    request_hash = _json_hash(request)
    gaps: list[dict[str, str]] = []

    common_fields = (
        ("question", "Pergunta de pesquisa não definida.", "Delimitar pergunta, escopo e critério de refutação.", "critical"),
        ("problem_class", "Classe/estrutura do problema não declarada.", "Formalizar a classe e suas propriedades relevantes."),
        ("objective", "Objetivo/função de avaliação não declarada.", "Definir função objetivo ou observável e unidade."),
        ("constraints", "Restrições não foram declaradas (inclusive explicitamente como nenhuma).", "Listar restrições e regra de validação de factibilidade."),
        ("baseline_methods", "Baselines clássicos não definidos.", "Selecionar baselines compatíveis e orçamento comparável."),
        ("evaluation_metrics", "Métricas e regra de comparação não definidas.", "Definir métricas, unidade, agregação e critério de sucesso."),
        ("evidence_refs", "Não há referências de evidência declaradas.", "Vincular fontes/artefatos, versões, hashes e afirmações suportadas."),
    )
    for field, description, next_step, *severity in common_fields:
        value = request[field]
        missing = value is None if field in {"question", "problem_class", "objective"} else not value
        if missing:
            gaps.append(_gap(field, description, next_step, severity[0] if severity else "high"))

    has_quantum_candidate = any(method != "classical_baselines" for method in request["candidate_methods"])
    if has_quantum_candidate and not request["resource_limits"]:
        gaps.append(_gap(
            "resource_limits",
            "Limites de recursos NISQ/simulação não declarados.",
            "Fixar limites de qubits, shots, memória/tempo de simulação e orçamento antes de comparar métodos.",
        ))

    application = None
    if request["application_label"] is not None:
        application = next(
            row for row in tiangong_application_catalog()
            if row["label"] == request["application_label"]
        )
        gaps.append(_gap(
            "application_semantics",
            f"A semântica da página Tiangong rotulada {request['application_label']} permanece não verificada.",
            "Obter e preservar fonte primária que revele problema, entradas, saídas e critérios antes de vincular um solver.",
            "blocker",
        ))

    methods: list[dict[str, Any]] = []
    for method_id in request["candidate_methods"]:
        method = _METHOD_BY_ID[method_id]
        declared = set(request["method_inputs"].get(method_id, []))
        missing_inputs = [field for field in method["required_inputs"] if field not in declared]
        method_common_missing = [
            field for field in ("question", "problem_class", "objective", "constraints", "baseline_methods", "evaluation_metrics", "evidence_refs")
            if (request[field] is None if field in {"question", "problem_class", "objective"} else not request[field])
        ]
        if method_id != "classical_baselines" and not request["resource_limits"]:
            method_common_missing.append("resource_limits")
        all_missing = list(dict.fromkeys([*method_common_missing, *missing_inputs]))
        methods.append({
            "id": method_id,
            "name": method["name"],
            "family": method["family"],
            "status": "protocol_requirements_complete" if not all_missing else "blocked_on_gaps",
            "missing_inputs": all_missing,
            "declared_method_inputs": sorted(declared),
            "declaration_status": "operator_declared_not_independently_verified",
            "protocol": list(method["protocol"]),
            "limitations": list(method["limitations"]),
            "execution_status": "not_attempted",
        })
        for field in missing_inputs:
            gaps.append(_gap(
                f"method_inputs.{method_id}.{field}",
                f"Pré-requisito de {method['name']} não foi declarado: {field}.",
                f"Especificar e validar {field} antes de afirmar prontidão metodológica.",
                "method_specific",
            ))

    return {
        "status": "plan_only",
        "schema_version": 1,
        "request_sha256": request_hash,
        "question": request["question"],
        "application": application,
        "problem": {
            "problem_class": request["problem_class"],
            "objective": request["objective"],
            "constraints": request["constraints"],
        },
        "evidence_refs": request["evidence_refs"],
        "baseline_methods": request["baseline_methods"],
        "evaluation_metrics": request["evaluation_metrics"],
        "resource_limits": request["resource_limits"],
        "seed": request["seed"],
        "methods": methods,
        "gaps": gaps,
        "study_sequence": [
            "Fechar a definição do problema, proveniência, dados e métricas.",
            "Implementar e validar baseline(s) clássico(s) antes de comparar métodos quânticos.",
            "Resolver pré-requisitos e lacunas por método; manter resultados brutos e seeds.",
            "Executar simulação/ablação com limites explícitos e reportar erro, custo e incerteza.",
            "Considerar hardware apenas em ciclo separado, com autorização por chamada e recibo.",
        ],
        "automatic_method_recommendation": None,
        "execution_authorized": False,
        "execution_attempted": False,
        "jobs_submitted": 0,
        "network": False,
        "quantum_advantage": "not_assessed",
        "limitations": [
            "Plano determinístico de pesquisa; não é solver, simulação, benchmark ou execução em hardware.",
            "Campos de prontidão são declarações do solicitante e não foram verificados independentemente.",
            "Rótulos Tiangong não têm semântica atribuída sem evidência primária suficiente.",
            "Nenhuma conclusão de vantagem quântica, superioridade, otimalidade, eficácia de mitigação ou custo é produzida.",
        ],
    }


def _emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Planejamento local de pesquisa NISQ; sem solver/QPU.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("catalog", help="lista métodos candidatos e rótulos Tiangong sem rede")
    subparsers.add_parser("plan", help="lê contrato JSON v1 de stdin e retorna lacunas/plano")
    args = parser.parse_args(argv)

    if args.command == "catalog":
        _emit({
            "status": "catalogued",
            "network": False,
            "research": research_catalog(),
            "tiangong_applications": tiangong_application_catalog(),
        })
        return 0

    raw = sys.stdin.read(MAX_CLI_INPUT_BYTES + 1)
    if len(raw.encode("utf-8")) > MAX_CLI_INPUT_BYTES:
        _emit({"status": "error", "code": "input_limit_exceeded"})
        return 2
    try:
        payload = json.loads(raw)
        _emit(build_research_plan(payload))
        return 0
    except (json.JSONDecodeError, QuantumResearchContractError) as exc:
        _emit({"status": "error", "code": "invalid_research_request", "message": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
