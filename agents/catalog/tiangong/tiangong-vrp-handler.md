# Agent Card: tiangong-vrp-handler

## Metadados
- **agent_id**: tiangong-vrp-handler
- **name**: Handler Tiangong VRP
- **description**: Analisa e processa o problema de roteamento de veículos com capacidade (CVRP) na aplicação Tiangong VRP, com técnicas estáticas observáveis via REA.
- **version**: 1.0.0
- **type**: specialist
- **category**: engineering
- **language**: pt-BR
- **license**: MIT (skill apenas; código fonte da aplicação não reutilizável)
- **tags**: [ "tiangong", "VRP", "vehicle-routing", "QAOA", "QUBO", "static-analysis" ]
- **capabilities**: [ "static_analysis", "json_handler", "technique_extraction", "harness_invocation" ]
- **extendedAgentCard**: true

## Habilidades (skills)
- **id**: tiangong-vrp-handler-skill
- **name**: tiangong-vrp-handler
- **description**: Handler para roteamento de veículos com QAOA/QUBO e framework híbrido clássico-quântico.
- **tags**: [ "tiangong", "VRP", "handler", "vehicle-routing" ]

## Entrada (schema JSON)
```json
{
  "action": "solve|upload|compare",
  "dataset_type": "built-in|custom",
  "n_nodes": "number",
  "n_vehicles": "number",
  "vehicle_capacity": "number",
  "custom_dataset": {
    "demands": "[array]",
    "coordinates": "[[x,y],[x,y],...]"
  },
  "metadata": {
    "app_version": "string",
    "retrieval_timestamp": "string",
    "source_sha256": "string"
  }
}
```

## Saída (schema JSON)
```json
{
  "status": "success|error|unknown",
  "technique": "QAOA-solve|classical-heuristic|QUBO-model|unknown",
  "result": {
    "task_id": "string",
    "route_for_cars": "[[car_route], ...]",
    "route_len": "string",
    "load": "string",
    "car_demand": "string",
    "car_id": "string",
    "solution_quality": "string",
    "energy_convergence": "string (opcional)"
  },
  "evidence": {
    "sha256_observed": "string",
    "method": "static_analysis_REA",
    "provider": "REA_6.8.0_static_analysis",
    "limitations": ["array"]
  },
  "limitations": ["array"]
}
```

## Permissões (policy)
- read: allow
- glob: allow
- grep: allow
- edit: deny
- webfetch: deny
- task: deny
- bash: "python3 -m marceloclaro.cli doctor": allow
- python3 -m pytest tests/ -q": allow

## Referências
- Fonte: https://tiangongqs.com/application/quantum-application/VRP
- HTML: .opencode/rea/tiangong-r1089/raw/VRP.html (SHA-256: 8040aca9...)
- Bundle JS: .opencode/rea/tiangong-r1089/raw/index-tr-dGsa5.js (SHA-256: <hash>)
- REA Analysis: .opencode/rea/tiangong-r1089/rea-summary.json
- SPEC: specs/SPEC-935-R1089-tiangong-app-harness.md