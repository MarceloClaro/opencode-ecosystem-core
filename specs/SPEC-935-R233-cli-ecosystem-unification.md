---
spec_id: SPEC-935-R233
title: "Unificação Multilateral de CLIs (Antigravity CLI, Claude Code CLI e OpenAI Codex / OpenCode)"
component: integrations/cli_ecosystem_bridge.py
test_file: tests/test_r233_cli_ecosystem_unification.py
status: green
---

# SPEC-935-R233 — Ponte Multilateral de Ecossistemas CLI
======================================================

## 1. Visão Geral
Esta especificação provê o **`CliEcosystemBridge`**, um gerenciador que unifica os agentes, skills, especificações e comandos entre **Antigravity CLI**, **Claude Code CLI** e **OpenAI Codex / OpenCode CLI**, permitindo a sincronização automática de contextos, instruções e cartas de subagentes entre as três plataformas.

## 2. Requisitos Funcionais
- **Classe `CliEcosystemBridge`**:
  - `discover_cli_capabilities() -> Dict[str, Any]` (detecta Antigravity, Claude Code e Codex/OpenCode).
  - `export_agent_cards_to_claude() -> Dict[str, Any]` (sincroniza `CLAUDE.md` e subagentes).
  - `export_skills_to_antigravity() -> Dict[str, Any]` (sincroniza skills e slash commands do Antigravity).
  - `get_unified_status() -> Dict[str, Any]` (retorna a prontidão dos 3 ecossistemas).
