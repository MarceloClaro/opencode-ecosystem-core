---
spec_id: SPEC-935-R662
title: Interfaces centrais de diagnostico e handoff das integracoes
status: green
validation_scope: local_runtime
release_gate: docs/evidence/R659_R662_RELEASE_GATE.json
component: marceloclaro/integration_service.py + marceloclaro/orchestrator.py + integrations/ecosystem_mcp.py
test_file: tests/test_r662_integration_surface.py
---

# R662 — Integrações acessíveis pelo orquestrador, CLI e MCP

## Contratos

1. Diagnóstico local verifica configuração reproduzível, referências de agentes
   e comandos, schemas MCP e resolução de skills; usa contagens atuais e
   distingue descoberta, emissão, instalação e execução comprovada.
2. Handoff de skill fornece instruções e referências sob o orquestrador, com
   hash atual e limites de leitura. Não executa scripts ou eleva permissões.
3. Expor status/check e plano de skill pela CLI integracoes, MCP somente leitura
   e comando /integracoes gerado; todos usam o mesmo serviço central.
4. Argumentos inválidos falham antes de efeitos, limite de leitura e IDs/nomes
   são explícitos; CLI retorna não zero ao falhar ou encontrar inconsistências.
5. Preservar R657/R658 e ferramentas da rede, regenerar opencode.json e executar
   testes de regressão, lint, doctor e probes reais; registrar ciclos sem
   alegar instalação externa, auditoria independente externa ou ganho cognitivo.

## Critérios de aceitação executáveis

- `R662-CONTRACT` — Diagnóstico encontra inconsistências acionáveis e conta fontes reais.
- `R662-HANDOFF` — Handoff preserva políticas, fonte e limites sem executar código.
- `R662-SURFACES` — CLI e MCP encaminham os mesmos contratos pelo orquestrador.
