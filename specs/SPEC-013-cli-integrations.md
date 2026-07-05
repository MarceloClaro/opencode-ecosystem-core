# SPEC-013 — Integrações CLI (OpenCode CLI + Antigravity)

```yaml
spec_id: SPEC-013
title: Integrações Externas — OpenCode CLI e Antigravity CLI
module: integrations/opencode_cli.py, integrations/antigravity/bridge.py
origin: OpenCode_Ecosystem opencode.json + SPEC-046 (Antigravity)
status: implemented
```

## Objetivo

Expor o ecossistema completo ao **OpenCode CLI** (opencode.json com todos os agentes, orquestrador primário `marceloclaro`, MCP servers e comandos) e à **Antigravity CLI** (delegação externa com fila de handoff resiliente quando a CLI não está instalada).

## Requisitos

| ID | Requisito | Critério de Aceitação |
|---|---|---|
| REQ-013.1 | `build_config()` gera opencode.json com ≥ 128 agentes | `len(config["agent"]) >= 128` |
| REQ-013.2 | `marceloclaro` é o único agente `primary` (prevalece sobre homônimos do catálogo) | `config["agent"]["marceloclaro"]["mode"] == "primary"` |
| REQ-013.3 | MCP servers registrados: metacognitive-interconnect e antigravity-bridge | presentes em `config["mcp"]` |
| REQ-013.4 | Comandos customizados expostos (diagnose, academic, quantum, evolve) | `"diagnose" in config["command"]` |
| REQ-013.5 | Antigravity: sem CLI instalada, o handoff é enfileirado em arquivo (nunca perde a solicitação) | `delegate()` ⇒ `status: queued` + `handoff_file` existente |

## Invariantes

- INV-013.1: O opencode.json gerado é JSON válido conforme schema `https://opencode.ai/config.json`.
- INV-013.2: O bridge Antigravity nunca lança exceção por CLI ausente.

## Testes

`tests/test_advanced_subsystems.py::TestIntegrations` (2 testes).
