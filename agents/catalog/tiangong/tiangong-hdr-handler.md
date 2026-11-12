# Agent Card: tiangong-hdr-handler

## Metadados
- **agent_id**: tiangong-hdr-handler
- **name**: Handler Tiangong HDR
- **description**: Analisa e processa reconhecimento de dígitos manuscritos na aplicação Tiangong HDR, com técnicas estáticas observáveis via REA.
- **version**: 1.0.0
- **type**: specialist
- **category**: engineering
- **language**: pt-BR
- **license**: MIT (skill apenas; código fonte da aplicação não reutilizável)
- **tags**: [ "tiangong", "HDR", "handwritten-digit-recognition", "QNN", "static-analysis" ]
- **capabilities**: [ "static_analysis", "json_handler", "technique_extraction", "harness_invocation" ]
- **extendedAgentCard**: true

## Habilidades (skills)
- **id**: tiangong-hdr-handler-skill
- **name**: tiangong-hdr-handler
- **description**: Handler para reconhecimento de dígitos manuscritos com QNN e processamento de canvas.
- **tags**: [ "tiangong", "HDR", "handler", "digit-recognition" ]

## Entrada (schema JSON)
```json
{
  "action": "recognize|export|compare",
  "image_base64": "string (opcional)",
  "image_path": "string (opcional)",
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
  "technique": "QNN-handler|canvas-processing|feature-extraction",
  "result": {
    "digit": "0-9 or null",
    "confidence": "number 0-1 or null",
    "processed_image": "string or null",
    "feature_vector": "array or null"
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
- Fonte: https://tiangongqs.com/application/quantum-application/HDR
- HTML: .opencode/rea/tiangong-r1089/raw/HDR.html (SHA-256: 8040aca9...)
- Bundle JS: .opencode/rea/tiangong-r1089/raw/index-CqCZGp9w.js (SHA-256: 7f6e3f71...)
- REA Analysis: .opencode/rea/tiangong-r1089/rea-summary.json
- SPEC: specs/SPEC-935-R1089-tiangong-app-harness.md