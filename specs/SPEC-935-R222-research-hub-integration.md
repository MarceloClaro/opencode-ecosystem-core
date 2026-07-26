---
spec_id: SPEC-935-R222
title: "Integração Unificada do ResearchHub com Orquestrador, Blackboard e MetaBus"
component: research/hub_router_bridge.py, marceloclaro/orchestrator.py
test_file: tests/test_r222_research_hub_integration.py
status: green
---

# SPEC-935-R222 — Unificação do ResearchHub e Pontes de Orquestração
=====================================================================

## 1. Visão Geral
Esta especificação desfaz qualquer isolamento funcional ("ilha") do **ResearchHub** (PubMed, bioRxiv, CORE, Crossref, OpenAlex, arXiv, etc.), conectando-o diretamente ao **Blackboard A2A**, ao **MetaBus** e ao orquestrador central **`marceloclaro`**.

## 2. Requisitos Funcionais
- **Integração no Blackboard A2A**: Registrar eventos de publicação de pesquisa no Blackboard A2A para que agentes de revisão (`ReviewerAgent`, `MultiCriticReviewer`) consumam os achados automaticamente.
- **Roteamento de Pesquisa**: Conectar a busca federada ao `ModelRouter` e ao `DataKnowledgeHub`.
- **Rastreabilidade**: Garantir que todo manifesto de pesquisa gere um evento no `MetaBus` e atualize a memória metacognitiva.
