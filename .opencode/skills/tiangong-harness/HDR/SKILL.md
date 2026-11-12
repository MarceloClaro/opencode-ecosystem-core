---
name: tiangong-hdr-handler
description: >
  Handler Tiangong HDR para validação, pré-processamento PNG/pixels, comparação de vetores e contrato honesto de reconhecimento indisponível.
metadata:
  round: R1089
  spec: SPEC-935-R1089-MCP.md
  license: MIT (skill apenas; código-fonte da aplicação não reutilizável)
  source: https://tiangongqs.com/application/quantum-application/HDR
  adaptation: Recriação original a partir de análise estática REA; sem cópia do frontend.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
---

# Skill: tiangong-HDR-handler

## Visão geral
Skill de handler para a aplicação Tiangong HDR (Handwritten Digit Recognition).
Objetivo: prover técnicas observáveis e um contrato de harness local para o
reconhecimento de dígitos manuscritos usando QNN (Quantum Convolutional Neural
Networks) conforme documentado na interface pública da aplicação.

## Origem
Aplicação disponível em https://tiangongqs.com/application/quantum-application/HDR
HTML retratado em 2026-11-12T01:24:31.813628Z, SHA-256: 8040aca93fb0c658ff15108ecf2cbca9a5442fa2e395a579545a41cbeb73f342
Bundle JS em .opencode/rea/tiangong-r1089/raw/index-CqCZGp9w.js, SHA-256: 7f6e3f71fa4fcc42cd6dafef79f881f0a32afe44db43f001eac9893e7d1f9eea

## Entrada (JSON)
```json
{
  "action": "recognize" | "export" | "compare",
  "image_base64": "<base64 PNG/JPEG opcional>",
  "image_path": "<caminho local opcional>",
  "metadata": {
    "app_version": "observado_na_interface",
    "retrieval_timestamp": "2026-11-12T01:24:31Z",
    "source_sha256": "<sha256 do bundle>"
  }
}
```

## Saída (JSON)
```json
{
  "status": "success" | "error" | "unknown",
  "technique": "QNN-handler | canvas-processing | feature-extraction",
  "result": {
    "digit": "<0-9 ou null>",
    "confidence": "<number 0-1 ou null>",
    "processed_image": "<caminho ou data URL>",
    "feature_vector": "<array de 784 valores ou null>"
  },
  "evidence": {
    "sha256_observed": "<sha256 do código fonte>",
    "method": "static_analysis_REA",
    "provider": "REA_6.8.0_static_analysis",
    "limitations": ["execução não realizada", "backend quântico não verificado"]
  },
  "limitations": [
    "Backend quântico não observado; interface descreve QNN mas não expõe endpoint.",
    "Análise estática apenas; código JavaScript parseado como texto inertes.",
    "Não afirmar vantagem quântica sem execução real de circuito.",
    "Imagens de entrada devem ser fornecidas pelo usuário; não há serviço de geração."
  ]
}
```

## Técnicas observáveis (REA)
1. **Canvas processing**: A aplicação usa um canvas para entrada de dígitos manuscritos;
   captura de entrada do usuário via mouse/touch, rendering em 2D canvas, e conversão
   para dados de pixel via `toDataURL` ou `toBase64`.
2. **Feature extraction**: Feature vector de 784 valores (28×28 pixels) extraído da
   entrada do usuário; normalização para escala 0-1 observada no código.
3. **QNN reference**: O código fonte menciona "Quantum Convolutional Neural Networks"
   mas não expõe API de circuito quântico; referência apenas na interface de texto,
   não em backend executável.

## Testes (RED)
- Teste com entrada inválida → status "error", campo "digit" = null
- Teste com entrada ausente → status "error", mensagem apropriada
- Teste com imagem PNG válida 28×28 → status "success", digit 0-9 se reconhecido

## Execução local (Harness)
```bash
# Exemplo de invocação do harness
tiangong-handler --action recognize --image-path /caminho/para/digit.png
# Saída JSON padronizada conforme contrato acima
```

## MCP local (SPEC-935-R1089-MCP)
Servidor stdio `integrations/tiangong_mcp.py`, registrado como `tiangong-hdr` em
`opencode.json` com `command=[".venv/bin/python", "-m", "integrations.tiangong_mcp"]`
e `cwd` na raiz do repositório. Ferramentas: `tiangong_catalog`, `hdr_handler`,
`rsir_handler`, `vrp_handler`. Sem rede, credenciais, shell ou leitura arbitrária
de arquivos. `recognize` retorna `unavailable` (backend QNN não observado), sem
dígito ou confiança fabricados; `preprocess` aceita PNG 8 bits ou matriz `pixels`
e devolve vetor 784 determinístico. Para desativar: `enabled: false` na entrada.