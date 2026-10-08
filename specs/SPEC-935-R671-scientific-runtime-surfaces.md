---
spec_id: SPEC-935-R671
title: Orquestração central de runtimes externos, datasets e plugins científicos
status: green
validation_scope: local_runtime
component: marceloclaro/runtime_actions.py + marceloclaro/orchestrator.py + marceloclaro/science_cli.py + integrations/ecosystem_mcp.py
test_file: tests/test_r671_runtime_surfaces.py
---

# R671 — Interfaces funcionais do percurso científico

CLI e MCP validam configurações finitas antes de criar o orquestrador ou executar
efeitos. Runtimes, downloads, construção de datasets e plugins usam a entrada
MarceloClaroOrchestrator e registram observação delimitada no MetaBus sem nota
científica automática. Controles de erro e diretórios novos são preservados.

Oito perfis do catálogo orientam tarefas pelo Blackboard. Chamadas a conectores
hospedados são completadas pelo host autenticado com recibo vinculado, sem
transferir credenciais. Ciência, simulação e inspeção de infraestrutura recebem
escopos distintos. A configuração OpenCode é reproduzível e contém comandos
para os novos métodos. Testes RED precedem implementação e os probes reais
complementam os testes herméticos; não se confundem com eles.

RED: `docs/evidence/R671_RED.xml`; GREEN: `docs/evidence/R667_R671_GREEN.xml`.
Prova atual: `docs/evidence/R671_REAL_20261004_195302/probe.json`.
Gate: `docs/evidence/R667_R671_RELEASE_GATE.json`.
