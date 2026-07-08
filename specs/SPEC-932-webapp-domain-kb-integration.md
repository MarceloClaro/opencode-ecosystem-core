# SPEC-932: Integração das Knowledge Bases Segmentadas à Aba Jurídica

```yaml
spec_id: SPEC-932
title: Integração das knowledge bases jurídicas segmentadas por ramo à aba jurídica da webapp
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-931, SPEC-926, SPEC-925, SPEC-927]
origin: pedido do usuário para ligar as knowledge bases segmentadas à aba jurídica da webapp
```

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Integrar as knowledge bases jurídicas segmentadas por ramo à aba `⚖️ Jurídico` da webapp, permitindo que o usuário:

- deixe o sistema escolher automaticamente o ramo;
- escolha manualmente um ramo especializado;
- visualize a base jurídica ativa e os documentos mais relevantes;
- use essa base como grounding contextual da análise jurídica.

## 2. Escopo

### 2.1 Helpers web

- resolver seleção automática/manual do ramo;
- expor preview da base ativa;
- retornar títulos e snippets dos documentos mais relevantes.

### 2.2 Webapp

- adicionar seletor de ramo jurídico:
  - `Automático`
  - `Manual`
- mostrar:
  - ramo jurídico ativo
  - base jurídica ativa
  - número de documentos
  - preview dos documentos mais relevantes

## 3. Critérios de Aceitação (TDD)

1. `resolve_domain_knowledge_base_selection()` suporta modo automático
2. `resolve_domain_knowledge_base_selection()` suporta modo manual
3. `summarize_domain_knowledge_base()` retorna preview com documentos relevantes
4. `webapp/app.py` contém controles de seleção automática/manual do ramo
5. `build_legal_params()` passa `domain_id` quando fornecido

## 4. Resultado Esperado

A aba jurídica deixa de ser apenas um formulário para o scanner e passa a ser uma interface de **grounding jurídico especializado por ramo**.
