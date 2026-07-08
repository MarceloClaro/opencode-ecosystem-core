# SPEC-926: Aba Jurídica Dedicada na Webapp

```yaml
spec_id: SPEC-926
title: Aba jurídica dedicada para Legal Impact Scanner e avaliação metacognitiva na webapp
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-925, SPEC-924, SPEC-923, SPEC-922, SPEC-921]
origin: pedido do usuário para criar uma aba jurídica dedicada na interface web e depois commitar/pushar
```

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Criar uma **aba jurídica dedicada** na interface Streamlit (`webapp/app.py`) separada do diagnóstico geral, para operar o Legal Impact Scanner de maneira mais direta, legível e orientada a uso jurídico.

## 2. Escopo

### 2.1 UX

- nova aba: `⚖️ Jurídico`
- entrada dedicada para:
  - título da análise
  - corpus jurídico
  - metodologia
  - resultados
  - conclusões
  - palavras-chave
  - área do conhecimento
- exibição dedicada de:
  - score jurídico
  - ganho metacognitivo jurídico
  - readiness jurídica
  - flags de alto risco
  - JSON auditável completo

### 2.2 Backward compatibility

- a aba `🔬 Diagnóstico` continua funcionando
- a integração anterior (`include_legal_impact=True`) permanece suportada

## 3. Critérios de Aceitação (TDD)

1. `webapp/app.py` contém a aba `⚖️ Jurídico`
2. a aba jurídica usa `build_legal_params()` e `summarize_legal_impact_section()`
3. a aba jurídica aciona `orch.diagnose(..., include_legal_impact=True)`
4. a aba mostra `Score Jurídico`, `Ganho Metacognitivo`, `Readiness` e `Flags de Alto Risco`
5. a aba de diagnóstico geral continua presente

## 4. Resultado Esperado

A interface web passa a ter um **espaço jurídico próprio**, permitindo operação mais natural do scanner, sem misturar a análise jurídica com o diagnóstico técnico geral.
