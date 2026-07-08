# SPEC-925: Interface Web para Scanner Jurídico de Impacto

```yaml
spec_id: SPEC-925
title: Integração do Legal Impact Scanner à interface web Streamlit
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-924, SPEC-923, SPEC-922, SPEC-921]
origin: pedido do usuário para ligar o scanner jurídico ao webapp/app.py
```

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Conectar o `LegalImpactScanner` (SPEC-924) à interface web `webapp/app.py`, oferecendo uma forma prática de avaliar corpus, pesquisas e produções sob uma ótica jurídica e metacognitiva.

## 2. Escopo

### 2.1 Backend

- expandir `MarceloClaroOrchestrator.diagnose()` com:
  - `include_legal_impact: bool = False`
  - `legal_params: Optional[Dict[str, Any]] = None`
- propagar os parâmetros para `DiagnosticPipeline.run()`.

### 2.2 Webapp

- adicionar controles no tab de diagnóstico para:
  - habilitar visão jurídica de impacto
  - informar título, metodologia, resultados, conclusões, palavras-chave e área
- renderizar métricas resumidas:
  - `overall_score`
  - `metacognitive_gain_score`
  - `high_risk_flags`

### 2.3 Helpers testáveis

- criar `webapp/legal_impact_helpers.py` com funções puras para:
  - montar `legal_params`
  - resumir a seção `legal_impact`

## 3. Critérios de Aceitação (TDD)

1. `build_legal_params()` normaliza palavras-chave CSV em lista
2. `summarize_legal_impact_section()` retorna métricas principais
3. `MarceloClaroOrchestrator.diagnose(..., include_legal_impact=True)` inclui `legal_impact`
4. `webapp/app.py` expõe controles de visão jurídica
5. modo antigo continua funcionando sem `include_legal_impact`

## 4. Resultado Esperado

A webapp passa a oferecer uma camada prática de análise jurídica e metacognitiva, permitindo uso operacional do scanner sem exigir Python/CLI direto.
