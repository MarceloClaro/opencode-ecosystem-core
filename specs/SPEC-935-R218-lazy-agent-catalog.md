---
spec_id: SPEC-935-R218
title: "Carregador Preguiçoso de Catálogo de Agentes (Lazy Agent Catalog)"
component: agents/lazy_catalog.py
test_file: tests/test_r218_lazy_agent_catalog.py
status: green
---

# SPEC-935-R218 — Lazy Agent Catalog Loader
===========================================

## 1. Visão Geral
Esta especificação introduz o mecanismo de **carregamento preguiçoso (Lazy Loading)** para a biblioteca de 186+ cartões de agentes em `agents/catalog/*.md`.

## 2. Requisitos Funcionais
- **Carregamento sob demanda**: Indexar apenas os caminhos e metadados básicos no boot. O conteúdo integral dos prompts dos cartões é lido do disco e armazenado em cache (`@lru_cache`) apenas quando o agente for selecionado pelo orquestrador.
- **Redução do Tempo de Startup**: Reduzir a sobrecarga de I/O em >70% na fase de inicialização.
- **Interface da Classe `LazyAgentCatalog`**:
  - `get_agent(agent_id: str) -> Optional[Dict[str, Any]]`
  - `list_agents() -> List[str]`
  - `clear_cache()`
