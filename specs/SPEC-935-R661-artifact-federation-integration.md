---
spec_id: SPEC-935-R661
title: Skills e plugins federados preservam identidade e politicas
status: green
validation_scope: local_runtime
release_gate: docs/evidence/R659_R662_RELEASE_GATE.json
component: integrations/harness_federation + reversa_universal/skill_dispatch.py
test_file: tests/test_r661_artifact_integration.py
---

# R661 — Descoberta e portabilidade fiel dos artefatos

## Contratos

1. Descobrir skills Codex modernas em skills/ e plugins/cache explicitamente
   configurados, sem perder superfícies existentes nem executar conteúdo.
2. Skills homônimas com conteúdo distinto têm IDs e destinos distintos;
   espelhos idênticos mantêm deduplicação com proveniência.
3. Emissão preserva disable-model-invocation e policy.allow_implicit_invocation
   e fornece referências locais contidas, suficientes para leitura da skill.
4. Leitura/emissão verifica hashes atuais, impede escape por symlink/path e
   recusa conteúdo alterado. Emissão não equivale a instalação no aplicativo.
5. Templates de prompts de plugin preservam tipo/string ou lista, ordem e valor.
   Não executar hooks/scripts importados nem inventar endpoints MCP.
6. Dispatcher encontra skill emitida e conserva modo read-and-execute quando
   aplicável; TDD e prova no disco cobrem descoberta → emissão → handoff.

## Critérios de aceitação executáveis

- `R661-DISCOVERY` — Raízes modernas e nomes iguais não perdem artefatos.
- `R661-POLICY` — Emissão e dispatcher mantêm políticas de invocação.
- `R661-PROVENANCE` — Referências e hashes pertencem à fonte atual e contida.
