"""R1141 — Core como framework de pesquisa quântica GJQ.

Camada de orquestração sobre o provider GJQ:

- status do SDK, credencial, orçamento e catálogo E01–E18;
- plano de pesquisa com fases SDD/TDD, gates e manifesto;
- roteamento de agentes por capacidade;
- nenhuma execução de hardware, nenhuma taxa medida.

O framework organiza o trabalho; não substitui revisão humana, validação
externa ou análise científica.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from gjq_hardware_opt.benchmarks import list_circuits
from integrations import gjq_core_provider as provider
from integrations.gjq_backend_registry import resolve_backend
from integrations.gjq_budget import check_budget

AGENTS = {
    "research": "gjq-quantum-research",
    "experiment": "gjq-experiment-runner",
    "optimization": "gjq-hardware-optimizer",
    "readout": "gjq-readout-mitigation",
    "audit": "quantum-experiment-auditor",
    "classification": "22_agente_ml_dl_datamining",
    "cooking": "42_agente_desenvolvedor_cientista_computacao",
}
DOMAIN_PHASES = {
    "general": [],
    "classification": [
        "dataset e split sem vazamento",
        "feature map e kernel quântico",
        "baseline clássico (RBF/kernel ridge)",
        "curva de aprendizado e calibração",
        "robustez a ruído e shots",
    ],
    "cooking": [
        "variáveis de processo e objetivo",
        "restrições e baseline clássico",
        "QUBO/QAOA ou VQE híbrido",
        "validação fora do conjunto e sensorial",
        "declaração de que não é ciência de alimentos",
    ],
}
LIMITS = (
    "Framework de orquestração offline. Não executa hardware, não mede taxas "
    "e não declara descoberta científica. Hardware exige confirm, "
    "allow_hardware, orçamento e auditoria de compilação."
)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _catalog() -> dict:
    synthetic = list_circuits("synthetic")
    experiments = list_circuits("experiments")
    return {
        "synthetic": [item["name"] for item in synthetic],
        "experiments": [
            {"name": item["name"], "experiment": item.get("experiment")}
            for item in experiments
        ],
    }


def status() -> dict:
    """Inventário local; não abre rede."""
    catalog = _catalog()
    base = provider.status()
    return {
        "schema_version": 1,
        "framework": "core-gjq-quantum-research",
        "provider": base,
        "catalog": catalog,
        "agents": AGENTS,
        "domains": list(DOMAIN_PHASES),
        "mcp_server": "gjq-runtime",
        "mcp_tools": [
            "gjq_provider_status",
            "gjq_provider_submit",
            "gjq_provider_result",
            "gjq_provider_compilation",
            "gjq_research_status",
            "gjq_research_plan",
        ],
        "framework_ready": bool(base.get("sdk") not in (None, "absent") and catalog["experiments"]),
        "hardware_executed": False,
        "rates_measured": False,
        "network_access": False,
        "limits": LIMITS,
    }


def plan(
    objective: str,
    *,
    backend_name: str = "FAS-CPU",
    experiment: str | None = None,
    shots: int = 1024,
    hardware: bool = False,
    required_capabilities: list[str] | None = None,
    domain: str = "general",
) -> dict:
    if not isinstance(objective, str) or not objective.strip():
        raise ValueError("objective obrigatório")
    if domain not in DOMAIN_PHASES:
        raise ValueError(f"domínio desconhecido: {domain}")
    if isinstance(shots, bool) or not isinstance(shots, int) or shots < 1:
        raise ValueError("shots deve ser inteiro >= 1")
    matches = resolve_backend(backend_name)
    if not matches:
        raise ValueError(f"backend desconhecido: {backend_name}")
    selected = matches[0]
    catalog = _catalog()
    names = {item["name"] for item in catalog["experiments"]}
    if experiment is not None and experiment not in names:
        raise ValueError(f"experimento desconhecido: {experiment}")
    capabilities = set(required_capabilities or [])
    routed = {
        capability: AGENTS[capability]
        for capability in capabilities
        if capability in AGENTS
    }
    if domain in AGENTS:
        routed[domain] = AGENTS[domain]
    budget = check_budget(
        selected["id"],
        shots,
        bool(hardware),
    )
    payload = {
        "schema_version": 1,
        "framework": "core-gjq-quantum-research",
        "objective": objective.strip(),
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "backend": selected,
        "experiment": experiment,
        "domain": domain,
        "shots": int(shots),
        "hardware": bool(hardware),
        "required_capabilities": sorted(capabilities),
        "routed_agents": routed,
        "phases": [
            "spec: objetivo, critérios e não objetivos",
            "tdd: testes antes da implementação",
            "simulation: executar em simulador e comparar",
            "preregistration: n, shots, hipótese e gates",
            "compilation_audit: initial_layout e QASM",
            "hardware_gate: confirm, allow_hardware, orçamento",
            "execution: provider submete um job",
            "audit: soma, incerteza e limites",
            "reflection: lições no MetaBus/Evolution",
            *DOMAIN_PHASES[domain],
        ],
        "gates": {
            "confirm": True,
            "allow_hardware": bool(hardware),
            "budget": budget,
            "compilation_audit": True,
            "provider_credential": bool(
                provider.status().get("credential") not in (None, "absent")
            ),
        },
        "executed": False,
        "hardware_executed": False,
        "rates_measured": False,
        "limits": LIMITS,
    }
    payload["manifest_sha256"] = _sha(payload)
    return payload
