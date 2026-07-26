---
spec_id: SPEC-935-R237
title: "Reparo e Expansão dos Fluxogramas Mermaid e Mapa da Arquitetura Completa"
component: README.md, ARCHITECTURE.md
test_file: tests/test_r237_diagrams_repair.py
status: green
---

# SPEC-935-R237 — Reparo e Expansão dos Diagramas de Arquitetura em Mermaid
===========================================================================

## 1. Visão Geral
Esta especificação provê a correção integral da renderização dos diagramas Mermaid no `README.md` e `ARCHITECTURE.md`, incluindo o **Mapa da Arquitetura Completa (v3.6.0)** em formato multi-subgrafo com todas as 11 camadas conectadas (Orquestrador, MCI MetaBus/Blackboard, Colibri MoE, LiteRT-LM, 6 Servidores MCP, Pipeline Acadêmico v3.0, Scanners, MIRA Presentation R126, ResearchHub R120 e Catálogo de 187 Agentes).

## 2. Requisitos Funcionais
- **Validação de Sintaxe Mermaid**: Garantir que todos os diagramas Mermaid sejam sintetizados sem erros de parse.
- **4 Visões Complementares**:
  1. Visão Intuitiva (Leigos).
  2. Arquitetura Multilateral CLI & MCP (Devs).
  3. Diagrama de Sequência SDD/TDD & Autocorreção RED-GREEN.
  4. Mapa Geral da Arquitetura v3.6.0 (Completo com 11 subgrafos).
