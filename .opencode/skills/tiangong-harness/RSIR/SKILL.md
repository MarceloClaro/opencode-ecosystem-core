---
name: tiangong-rsir-handler
description: >
  Handler Tiangong RSIR para validar vetores e declarar análise/classificação ViT/QViT indisponíveis sem rótulo fabricado.
metadata:
  round: R1089
  spec: SPEC-935-R1089-MCP.md
  license: MIT (skill apenas; código-fonte da aplicação não reutilizável)
  source: https://tiangongqs.com/application/quantum-application/RSIR
  adaptation: Recriação original a partir de análise estática REA; sem cópia do frontend.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
---

# Skill: tiangong-RSIR-handler

## Visão geral
Skill de handler para a aplicação Tiangong RSIR (Radio Signal Image Recognition).
Objetivo: prover técnicas observáveis e um contrato de harness local para o
reconhecimento de imagens de sinais de rádio rápidos (Fast Radio Bursts) usando
mecanismos de atenção quantum-enhanced conforme documentado na interface pública.

## Origem
Aplicação disponível em https://tiangongqs.com/application/quantum-application/RSIR
HTML retratado em 2026-11-12T01:24:32.725845Z, SHA-256: 8040aca93fb0c658ff15108ecf2cbca9a5442fa2e395a579545a41cbeb73f342
Bundle JS em .opencode/rea/tiangong-r1089/raw/index-CvWdnf6C.js, SHA-256: <hash do REA>

## Entrada (JSON)
```json
{
  "action": "analyze" | "classify" | "compare",
  "signal_data": "<JSON com dinamica espectro-temporal ou caminho de arquivo>",
  "model_select": "ViT | QViT | auto",  # Visão Transformer ou Quantum Vision Transformer
  "metadata": {
    "app_version": "observado_na_interface",
    "retrieval_timestamp": "2026-11-12T01:24:32Z",
    "source_sha256": "<sha256 do bundle>"
  }
}
```

## Saída (JSON)
```json
{
  "status": "success" | "error" | "unknown",
  "technique": "ViT-inference | QViT-inference | feature-extraction | unknown",
  "result": {
    "class_label": "<rótulo da classe observada>",
    "probabilities": {"classe_A": <0-1>, "classe_B": <0-1>},
    "quantum_enhanced": <boolean observado>,
    "feature_vector": "<array de features extraídas>",
    "model_used": "<nome do modelo selecionado>"
  },
  "evidence": {
    "sha256_observed": "<sha256 do código fonte>",
    "method": "static_analysis_REA",
    "provider": "REA_6.8.0_static_analysis",
    "limitations": ["backend quântico não verificado", "execução não realizada"]
  },
  "limitations": [
    "A aplicação requer login para acesso completo; apenas fluxo público inspecionado.",
    "Backend quântico não observado; interface descreve 'quantum-enhanced attention'
    mas não expõe endpoint de circuito.",
    "Análise estática apenas; código JavaScript parseado como texto inertes.",
    "Não afirmar vantagem quântica sem execução real de circuito.",
    "Requere dados de sinais de rádio reais; não há serviço de geração simulada."
  ]
}
```

## Técnicas observáveis (REA)
1. **Vision Transformer (ViT)**: O código implementa um modelo ViT para classificação
   de imagens de sinais de rádio. A arquitetura inclui blocos de atenção, posições
   embutidas e head(s) de classificação. Referenciado como `ViT` nas rotas do router.
2. **Quantum Vision Transformer (QViT)**: Variante que afirma "quantum-enhanced attention
   mechanism". O código referencia `QViT` como modelo alternativo, mas a implementação
   é estática — não há execução de circuito quântico observada.
3. **Time-frequency image preprocessing**: Conversão de dados dinâmicos espectro-temporais
   de FRBs em imagens time-frequency (corte, RFI mitigation, normalização, resize)
   conforme descrito no `desc` da aplicação.

## Testes (RED)
- Teste com dados de sinal inválidos → status "error", class_label = null
- Teste com modelo inexistente → status "error", model_select rejeitado
- Teste com dados de FRB vazios → status "error", probabilidades undefined

## Execução local (Harness)
```bash
# Exemplo de invocação do harness
tiangong-handler --action analyze --signal-data '{"dynamic_spectrum": [...]}' --model-select QViT
# Saída JSON padronizada conforme contrato acima
```

## MCP local (SPEC-935-R1089-MCP)
Servidor stdio `integrations/tiangong_mcp.py`, registrado como `tiangong-hdr` em
`opencode.json` com `command=[".venv/bin/python", "-m", "integrations.tiangong_mcp"]`
e `cwd` na raiz do repositório. Ferramenta: `rsir_handler`. Sem rede, credenciais,
shell ou leitura arbitrária de arquivos. `analyze` e `classify` retornam
`unavailable` (modelo ViT/QViT não observado), sem rótulo ou probabilidade
fabricados; `features` apenas valida e resume um vetor fornecido. Para desativar:
`enabled: false` na entrada.