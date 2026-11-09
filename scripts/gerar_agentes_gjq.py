"""Gera os 19 cards de agente do catálogo GJQ a partir do registro R1104.

Uso:
    python3 scripts/gerar_agentes_gjq.py
    python3 scripts/gerar_agentes_gjq.py --force

Sem `--force`, não sobrescreve cards existentes. O script não registra nem
executa agentes; apenas escreve definições válidas para o catálogo.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from integrations.gjq_backend_registry import BACKENDS, Backend, guidance_for  # noqa: E402

SPEC = "specs/SPEC-935-R1104-gjq-backend-agents.md"
TEST = "tests/test_r1104_gjq_backend_agents.py"
CATALOG = ROOT / "agents" / "catalog"


def _agent_id(backend: Backend) -> str:
    return f"gjq-backend-{backend.id}"


def _unique(backend: Backend) -> str:
    return "profile_" + _agent_id(backend).replace("-", "_")


def _tags(backend: Backend) -> list[str]:
    suffix = backend.id.replace("-", "_")
    tags = [
        _unique(backend),
        f"gjq_backend_{suffix}",
        f"gjq_{backend.family}",
        "gjq_backend_research",
        "backend_selection",
    ]
    if backend.requires_allow_hardware:
        tags.append("gjq_hardware_gate")
    if backend.amplitude_index_required:
        tags.append("gjq_single_amplitude")
    if backend.partial_amplitude:
        tags.append("gjq_partial_amplitude")
    if backend.simulator_config_required:
        tags.append("gjq_simulator_config")
    return tags


def _description(backend: Backend) -> str:
    kind = "emulação de hardware" if backend.kind == "emulated_hardware" else backend.kind
    gate = "o gate de hardware" if backend.requires_allow_hardware else "o limite de simulador"
    return (
        f"Especialista no backend GJQ {backend.display_name} "
        f"({backend.family}, {kind}, {backend.qubits} qubits). "
        f"Resolve o nome vivo, respeita {gate} e não declara fidelidade sem evidência."
    )


def _body(backend: Backend) -> str:
    api = backend.api_name or "não verificado"
    verified = "verificado na documentação" if backend.api_name_verified else (
        "não verificado; confirme com gjq_list_backends"
    )
    if backend.requires_allow_hardware:
        gate = (
            "Hardware/emulação: use `allow_hardware=True` e `confirm=True` no MCP "
            "`gjq-runtime`; sem isso, a submissão deve retornar bloqueada."
        )
    else:
        gate = (
            "Simulador: não é hardware. A execução não mede um chip e não deve ser "
            "descrita como medida física."
        )
    t1 = f"{backend.t1_us} µs" if backend.t1_us is not None else "não se aplica"
    t2 = f"{backend.t2_us} µs" if backend.t2_us is not None else "não se aplica"
    calibration = backend.calibrated_at or "não se aplica"
    restrictions = []
    if backend.amplitude_index_required:
        restrictions.append("single-amplitude exige `amplitude_index`")
    if backend.partial_amplitude:
        restrictions.append("partial-amplitude: declare o subconjunto medido")
    if backend.simulator_config_required:
        restrictions.append("MPS exige `simulator_config` e não garante praticidade")
    if backend.kind == "noise":
        restrictions.append("ruído modelado não é calibração real")
    if backend.kind == "emulated_hardware":
        restrictions.append(
            "a UI de 2026-11-09 mostra `(simulate)`; resultados históricos "
            "rotulados Guoji08 devem ser lidos com a data e a calibração da época"
        )
    if not restrictions:
        restrictions.append("nenhuma restrição específica além dos limites do runtime")
    guidance = guidance_for(backend)
    melhor = "\n".join(f"- {item}" for item in guidance["best_for"])
    evitar = "\n".join(f"- {item}" for item in guidance["avoid"])
    experimentos = "\n".join(f"- `{item}`" for item in guidance["recommended_experiments"])

    return f"""# Especialista GJQ — {backend.display_name}

Você é o especialista do recurso **{backend.display_name}** (`{backend.id}`),
família **{backend.family}**, tipo **{backend.kind}**, com **{backend.qubits} qubits**
no snapshot de 2026-11-09.

## Dados do snapshot

- Nome de API: `{api}` ({verified}).
- Status: `{backend.status}`; jobs no snapshot: `{backend.jobs}`.
- T1: {t1}; T2: {t2}; calibração: `{calibration}`.
- Aliases: {", ".join(f"`{a}`" for a in backend.aliases)}.

## Melhor uso

{melhor}

## Evitar

{evitar}

## Experimentos recomendados

{experimentos}

## Regras de uso

- {gate}
- {"; ".join(restrictions)}.
- Confirme o nome e o estado ao vivo com `gjq-runtime.gjq_list_backends` antes de
  submeter. O snapshot não é estado ao vivo.
- Use `gjq-backend-research` para resolver nome, selecionar backend, montar o
  plano e preencher a proveniência. Para submeter, use `gjq-runtime`.
- Registre `task_id`, backend, shots, timestamp, SHA-256 do QASM, versão do SDK
  e status. Não reenvie o mesmo circuito sem necessidade.
- Não declare fidelidade, emaranhamento, vantagem quântica ou qualidade
  científica sem evidência externa. Counts corretos não provam nada disso.
- Não aceite API key no prompt; a chave, se necessária, vem de `GJQ_API_KEY`
  no ambiente do operador.

## Nota do recurso

{backend.notes or "Sem nota adicional."}

## Coordenação e evidência

Receba tarefas pelo MarceloClaro. Leia a spec e o contexto compartilhado antes
de atuar. Apresente status, findings, evidence (arquivo/hash/linhas ou recibo)
e limitations. Declarar instalação, atribuição ou análise estática não comprova
inferência, execução, qualidade científica ou aprovação externa. Sem evidência
suficiente, devolva blocked ou partial. Não delegue fora do primário nem eleve
confiança pela própria avaliação.
"""


def _card(backend: Backend) -> str:
    agent_id = _agent_id(backend)
    tags = _tags(backend)
    description = _description(backend)
    meta = {
        "agent_id": agent_id,
        "name": f"Especialista GJQ — {backend.display_name}",
        "description": description,
        "version": "1.0.0",
        "type": "specialist",
        "category": "audit",
        "language": "pt-BR",
        "lifecycle": "managed-v1",
        "parent": "marceloclaro",
        "spec_file": SPEC,
        "test_file": TEST,
        "source": "user_requested_gjq_backend_registry",
        "allow_edit": False,
        "tags": list(tags),
        "skills": [{
            "id": agent_id,
            "name": f"Especialista GJQ — {backend.display_name}",
            "description": description,
            "tags": list(tags),
            "examples": ["Execute o escopo solicitado e cite os arquivos e limites observados."],
        }],
        "capabilities": {"extendedAgentCard": True},
        "permission": {
            "read": "allow",
            "glob": "allow",
            "grep": "allow",
            "edit": "deny",
            "webfetch": "deny",
            "task": "deny",
            "bash": {
                "*": "deny",
                "python3 -m marceloclaro.cli doctor": "allow",
                f"python3 -m pytest {TEST} -q": "allow",
            },
        },
        "tools": {
            "read": True,
            "glob": True,
            "grep": True,
            "bash": True,
            "edit": False,
            "write": False,
        },
        "output_contract": {
            "required_fields": ["status", "findings", "evidence", "limitations"],
            "evidence_required": True,
            "external_validation": False,
        },
    }
    header = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{header}---\n{_body(backend)}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera cards de agente GJQ R1104")
    parser.add_argument("--force", action="store_true", help="sobrescreve cards existentes")
    args = parser.parse_args()
    CATALOG.mkdir(parents=True, exist_ok=True)
    written, skipped = 0, 0
    for backend in BACKENDS:
        path = CATALOG / f"{_agent_id(backend)}.md"
        if path.exists() and not args.force:
            skipped += 1
            continue
        path.write_text(_card(backend), encoding="utf-8")
        written += 1
    print(f"cards escritos: {written}; preservados: {skipped}; total: {len(BACKENDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
