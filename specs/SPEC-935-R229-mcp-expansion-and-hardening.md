---
spec_id: SPEC-935-R229
title: "Expansão e Fortalecimento dos Servidores MCP (Model Context Protocol)"
component: colibri/colibri_mcp_server.py, scanners/scanners_mcp_server.py, integrations/opencode_cli.py
test_file: tests/test_r229_mcp_expansion.py
status: green
---

# SPEC-935-R229 — Expansão dos Servidores MCP do Ecossistema
============================================================

## 1. Visão Geral
Esta especificação expande o suporte MCP do ecossistema, criando servidores dedicados para o motor **Colibri MoE** (`colibri_mcp_server.py`) e para a suíte **SuperRigor / Scanners** (`scanners_mcp_server.py`), além de registrá-los em `integrations/opencode_cli.py` e em `opencode.json`.

## 2. Requisitos Funcionais
- **Servidor MCP Colibri Engine (`colibri/colibri_mcp_server.py`)**: Expor as ferramentas `colibri_generate`, `colibri_status` e `colibri_health`.
- **Servidor MCP Scanners (`scanners/scanners_mcp_server.py`)**: Expor `super_rigor_audit`, `scientific_reasoning_scan` e `merkle_integrity_check`.
- **Integração no CLI Generator**: Atualizar `integrations/opencode_cli.py` para incluir os 6 servidores MCP no `opencode.json`.
