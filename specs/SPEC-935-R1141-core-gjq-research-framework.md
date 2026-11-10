# SPEC-935-R1141 — Core como framework de pesquisa GJQ

**Status:** habilitado localmente; nenhum hardware executado
**Data:** 2026-11-10
**Componente:** `integrations/gjq_research_framework.py`

## 1. Objetivo

Habilitar o Core como camada de orquestração para pesquisa quântica avançada
na GJQ, reunindo catálogo, plano, gates, agentes e proveniência.

## 2. Requisitos

- **R1.** `status` local com SDK, credencial, orçamento, catálogo e agentes.
- **R2.** `plan` com objetivo, backend, experimento, shots, hardware e
  capacidades; fases e gates explícitos.
- **R3.** Manifesto determinístico com SHA-256.
- **R4.** Tools MCP `gjq_research_status` e `gjq_research_plan`.
- **R5.** Nenhum hardware/rede na operação de status/plan.
- **R6.** Testes de status, plano, rejeições e MCP.
- **R7.** Documentação, skill e harness atualizados.

## 3. Critérios

- status `network_access=False`, `hardware_executed=False`;
- catálogo E01–E18 presente;
- plano com 9 fases, gates e hash;
- plano rejeita objetivo/backend/experimento inválidos;
- MCP expõe as duas tools;
- nenhum task ID fictício.

## 4. Limites

O framework organiza o processo; não prova correção científica, não executa
hardware e não substitui SDD/TDD, revisão humana ou validação externa.
