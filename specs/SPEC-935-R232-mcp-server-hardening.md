---
spec_id: SPEC-935-R232
title: "Fortalecimento do Protocolo MCP SDK em scanners_mcp_server e colibri_mcp_server"
component: scanners/scanners_mcp_server.py, colibri/colibri_mcp_server.py
test_file: tests/test_r232_mcp_server_hardening.py
status: green
---

# SPEC-935-R232 — Fortalecimento dos Servidores MCP com o SDK Oficial
===================================================================

## 1. Visão Geral
Esta especificação consolida a integração do **MCP SDK oficial (`mcp.server.Server`)** em `scanners/scanners_mcp_server.py` e `colibri/colibri_mcp_server.py`, implementando os handlers assíncronos `@app.list_tools()` e `@app.call_tool()`, transporte stdio (`stdio_server()`) e resiliência contra erros de payload.

## 2. Requisitos Funcionais
- **Servidor `scanners-mcp`**: Suporte completo a `super_rigor_audit`, `scientific_reasoning_scan` e `merkle_integrity_check` com envelope JSON de resposta e tratamento de exceções.
- **Servidor `colibri-mcp`**: Suporte a `colibri_generate` e `colibri_status` via protocolo MCP stdio.
- **Compatibilidade Dual**: Manter as classes wrapper síncronas `ScannersMcpServer` e `ColibriMcpServer` para invocações internas e unit testes.
