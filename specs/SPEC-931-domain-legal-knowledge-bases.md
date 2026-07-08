# SPEC-931: Knowledge Bases Jurídicas Segmentadas por Ramo

```yaml
spec_id: SPEC-931
title: Bases de conhecimento jurídicas segmentadas por domínio
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-923, SPEC-927, SPEC-928]
origin: pedido do usuário para criar knowledge bases segmentadas por ramo e aumentar precisão especialista
```

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Evoluir a `LegalKnowledgeBase` de uma base jurídica geral para um sistema de **bases segmentadas por ramo**, permitindo grounding mais preciso para cada domínio jurídico especializado.

## 2. Escopo

### 2.1 Domínios cobertos

- penal
- trabalhista
- tributario
- empresarial
- administrativo
- ambiental
- digital_lgpd

### 2.2 Capacidades novas

1. documentos jurídicos com marcação por domínio;
2. inventário de documentos segmentados por ramo;
3. `get_domain_documents(domain_id)`;
4. `build_domain_knowledge_base(domain_id)`;
5. `route_domain_knowledge_base(query)` usando o roteador jurídico por domínio;
6. busca opcional filtrada por `domain_id`.

## 3. Critérios de Aceitação (TDD)

1. existe inventário segmentado cobrindo os 7 ramos
2. `build_domain_knowledge_base("digital_lgpd")` produz base orientada a LGPD
3. `search(..., domain_id="tributario")` recupera documento tributário relevante
4. `route_domain_knowledge_base(query)` usa o roteador jurídico para escolher a base
5. a base geral existente continua funcionando sem quebra retrocompatível

## 4. Resultado Esperado

O ecossistema deixa de depender apenas de uma base jurídica generalista e passa a oferecer **grounding especializado por ramo**, elevando a precisão dos agentes e dos benchmarks jurídicos.
