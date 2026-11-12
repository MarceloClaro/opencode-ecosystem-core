---
name: tiangong-vrp-handler
description: >
  Handler Tiangong VRP para validar instâncias e resolver CVRP com heurística clássica, sem alegar QAOA ou otimalidade.
metadata:
  round: R1089
  spec: SPEC-935-R1089-MCP.md
  license: MIT (skill apenas; código-fonte da aplicação não reutilizável)
  source: https://tiangongqs.com/application/quantum-application/VRP
  adaptation: Recriação original a partir de análise estática REA; sem cópia do frontend.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
---

# Skill: tiangong-VRP-handler

## Visão geral
Skill de handler para a aplicação Tiangong VRP (Capacitated Vehicle Routing Problem).
Objetivo: prover técnicas observáveis e um contrato de harness local para o
problema de roteamento de veículos com capacidade (CVRP) usando combinação de
heurísticas clássicas e QAOA (Quantum Approximate Optimization Algorithm) conforme
documentado na interface pública.

## Origem
Aplicação disponível em https://tiangongqs.com/application/quantum-application/VRP
HTML retratado em 2026-11-12T01:24:33.603565Z, SHA-256: 8040aca93fb0c658ff15108ecf2cbca9a5442fa2e395a579545a41cbeb73f342
Bundle JS em .opencode/rea/tiangong-r1089/raw/index-tr-dGsa5.js, SHA-256: <hash do REA>

## Entrada (JSON)
```json
{
  "action": "solve" | "upload" | "compare",
  "dataset_type": "built-in | custom",
  "n_nodes": "<número de nós>",
  "n_vehicles": "<número de veículos>",
  "vehicle_capacity": "<capacidade do veículo>",
  "custom_dataset": {
    "demands": "[...]",
    "coordinates": "[[{x,y},...]]"
  },
  "metadata": {
    "app_version": "observado_na_interface",
    "retrieval_timestamp": "2026-11-12T01:24:33Z",
    "source_sha256": "<sha256 do bundle>"
  }
}
```

## Saída (JSON)
```json
{
  "status": "success" | "error" | "unknown",
  "technique": "QAOA-solve | classical-heuristic | QUBO-model | unknown",
  "result": {
    "task_id": "<ID da tarefa submetida>",
    "route_for_cars": "[[car_route], ...]",
    "route_len": "<comprimento da rota>",
    "load": "<carga por carro>",
    "car_demand": "<demanda por carro>",
    "car_id": "<ID do carro>",
    "solution_quality": "<descritivo>",
    "energy_convergence": "<curva de convergência se disponível>"
  },
  "evidence": {
    "sha256_observed": "<sha256 do código fonte>",
    "method": "static_analysis_REA",
    "provider": "REA_6.8.0_static_analysis",
    "limitations": ["backend quântico não verificado", "execução não realizada"]
  },
  "limitations": [
    "A aplicação requer login para acesso completo; apenas fluxo público inspecionado.",
    "Backend quântico não observado; interface descreve QAOA e quantum annealing
    mas não expõe endpoint de circuito quântico real.",
    "Análise estática apenas; código JavaScript parseado como texto inertes.",
    "Não afirmar vantagem quântica sem execução real de circuito de annealing.",
    "Dados de entrada devem ser fornecidos pelo usuário; datasets built-in requerem
    autenticação para download."
  ]
}
```

## Técnicas observáveis (REA)
1. **QAOA (Quantum Approximate Optimization Algorithm)**: O código referencia QAOA
   com `single-layer QAOA quantum circuit`, `optimize parameters with Powell optimizer`,
   `run QAOA quantum circuit with optimized parameters`. Referência arquitetural apenas.
2. **QUBO Modeling**: O problema CVRP é mapeado para um modelo QUBO (Quadratic Unconstrained
   Binary Optimization). O código referencia `QUBO Modeling and Solving`, `Builds the CVRP
   problem from input parameters and maps it to a standard QUBO model`.
3. **Classical hybrid framework**: A aplicação combina "classical heuristic algorithms with
   quantum annealing" via "intelligent clustering and greedy strategy" para gerar "high-quality
   route candidate sets".
4. **Dataset formats**: Suporta datasets built-in (E, P) e upload customizado no formato `.vrp`.
   Dataset E: n22-k4 (22 nós, 4 veículos). Dataset P: n50-k4 (50 nós, 4 veículos).

## Testes (RED)
- Teste com dataset_type inválido → status "error", task_id = null
- Teste com n_nodes <= 0 → status "error", validação de entrada
- Teste com dataset custom sem coordenadas → status "error", campos obrigatórios ausentes

## Execução local (Harness)
```bash
# Exemplo de invocação do harness
tiangong-handler --action solve --dataset-type built-in --n-nodes 22 --n-vehicles 4
# Ou com dataset custom
tiangong-handler --action solve --dataset-type custom \
  --custom-dataset '{"demands":[1,2,3,...],"coordinates":[[0,0],[1,1],...]}'
# Saída JSON padronizada conforme contrato acima
```

## MCP local (SPEC-935-R1089-MCP)
Servidor stdio `integrations/tiangong_mcp.py`, registrado como `tiangong-hdr` em
`opencode.json` com `command=[".venv/bin/python", "-m", "integrations.tiangong_mcp"]`
e `cwd` na raiz do repositório. Ferramenta: `vrp_handler`. Sem rede, credenciais,
shell ou leitura arbitrária de arquivos. `solve` usa heurística clássica
determinística (vizinho mais próximo + 2-opt) com `backend="classical-heuristic"`,
`quantum=false` e `optimality="not_proven"`; `upload` retorna `unavailable`. Não é
QAOA nem prova de otimalidade. Para desativar: `enabled: false` na entrada.