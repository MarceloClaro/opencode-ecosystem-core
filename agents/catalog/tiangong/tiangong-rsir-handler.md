# Agent Card: tiangong-rsir-handler

## Metadados
- **agent_id**: tiangong-rsir-handler
- **name**: Handler Tiangong RSIR
- **description**: Analisa e processa reconhecimento de imagens de sinais de rádio rápidos (FRBs) na aplicação Tiangong RSIR, com técnicas estáticas observáveis via REA.
- **version**: 1.0.0
- **type**: specialist
- **category**: engineering
- **language**: pt-BR
- **license**: MIT (skill apenas; código fonte da aplicação não reutilizável)
- **tags**: [ "tiangong", "RSIR", "radio-signal-recognition", "ViT", "QViT", "static-analysis" ]
- **capabilities**: [ "static_analysis", "json_handler", "technique_extraction", "harness_invocation" ]
- **extendedAgentCard**: true

## Habilidades (skills)
- **id**: tiangong-rsir-handler-skill
- **name**: tiangong-rsir-handler
- **description**: Handler para reconhecimento de sinais de rádio com ViT/QViT e processamento de images time-frequency.
- **tags**: [ "tiangong", "RSIR", "handler", "radio-signal" ]

## Entrada (schema JSON)
```json
{
  "action": "analyze|classify|compare",
  "signal_data": "JSON com dinamica espectro-temporal ou caminho de arquivo",
  "model_select": "ViT|QViT|auto",
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
  "technique": "ViT-inference|QViT-inference|feature-extraction|unknown",
  "result": {
    "class_label": "string",
    "probabilities": {"classe_A": "number 0-1", "classe_B": "number 0-1"},
    "quantum_enhanced": "boolean observado",
    "feature_vector": "array",
    "model_used": "string"
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
- Fonte: https://tiangongqs.com/application/quantum-application/RSIR
- HTML: .opencode/rea/tiangong-r1089/raw/RSIR.html (SHA-256: 8040aca9...)
- Bundle JS: .opencode/rea/tiangong-r1089/raw/index-CvWdnf6C.js (SHA-256: <hash>)
- REA Analysis: .opencode/rea/tiangong-r1089/rea-summary.json
- SPEC: specs/SPEC-935-R1089-tiangong-app-harness.md