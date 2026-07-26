---
spec_id: SPEC-935-R235
title: "Hardening do Orquestrador Primário marceloclaro e Instalador 1-Click Windows"
component: marceloclaro/orchestrator.py, installer/windows/provision.sh
test_file: tests/test_r235_orchestrator_installer_hardening.py
status: green
---

# SPEC-935-R235 — Hardening da Orquestração Global e Instalador 1-Click Windows
=============================================================================

## 1. Visão Geral
Esta especificação garante que **nenhuma funcionalidade, agente, skill ou pipeline (incluindo MIRA Presentation R126, ResearchHub R123, SuperRigor Pipeline e CliEcosystemBridge) fique isolada em uma ilha**, estando todas integralmente conectadas e auditadas pelo Orquestrador Primário `marceloclaro`. Além disso, atualiza e valida o provisionamento automático do Instalador 1-Click do Windows (`Install-OpenCodeEcosystem.ps1` e `provision.sh`).

## 2. Requisitos Funcionais
- **Orquestração Primária (`MarceloClaroOrchestrator`)**:
  - Garantir o roteamento unificado de `MiraPresentationAgent`, `ResearchHub`, `SuperRigorPipeline`, `CliEcosystemBridge` e `StandaloneReadinessEval` em `audit_and_certify()`.
  - Confirmar zero ilhas isoladas em todo o catálogo de 187 agentes e MCPs.

- **Instalador 1-Click Windows (`provision.sh`)**:
  - Compilação automática do binário C do motor Colibri MoE (`colibri/c/olmoe`).
  - Provisionamento completo de ambientes Python (`.venv`), dependências, servidores MCP, LiteRT-LM, Ollama, OpenCode CLI, Antigravity CLI e Claude Code CLI.
  - Execução de autodiagnóstico `python3 -m marceloclaro.cli doctor`.
