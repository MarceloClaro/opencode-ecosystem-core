---
spec_id: SPEC-935-R1243
title: Guardrails de integridade e eficiência do MetaBus
component: mci.metabus
status: planned
test_file: tests/test_r1243_metabus_guardrails.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1243-LIMITS:
      - tests/test_r1243_metabus_guardrails.py::test_memory_context_limit_zero_is_empty_and_invalid_limits_are_rejected
      - tests/test_r1243_metabus_guardrails.py::test_memory_search_limit_zero_is_empty_and_invalid_limits_are_rejected
      - tests/test_r1243_metabus_guardrails.py::test_metabus_recent_events_limit_zero_is_empty_and_invalid_limits_are_rejected
    R1243-REFLECTION:
      - tests/test_r1243_metabus_guardrails.py::test_reflection_score_must_be_finite_normalized_and_does_not_mutate_on_rejection
      - tests/test_r1243_metabus_guardrails.py::test_reflection_persistence_failure_rolls_back_episode_and_confidence
    R1243-RETENTION:
      - tests/test_r1243_metabus_guardrails.py::test_successful_save_keeps_runtime_and_disk_retention_in_sync
---

# SPEC-935-R1243 — Guardrails de integridade e eficiência do MetaBus

## Objetivo

Corrigir falhas locais, reproduzíveis e compatíveis com o contrato histórico do
MetaBus que podem expor mais contexto que o limite solicitado, corromper a
confiança do ledger por pontuação inválida, declarar reflexão persistida quando
a gravação falhou e divergir entre a retenção em memória e a retenção em disco.
Esta entrega é uma primeira mitigação de baixo risco; não substitui a auditoria
de produção de todos os subsistemas nem migra o formato de armazenamento.

## Limites

- Não instalar frameworks nem copiar código de repositórios externos.
- Preservar os contratos de compatibilidade de `add_reflection` para escores
  finitos normalizados em `[0, 1]`, fórmula EMA e `record_observation` sem
  promoção de confiança.
- Mudar apenas validação de entrada, atomicidade local dos métodos tocados,
  semântica de limites e consistência da retenção episódica limitada a 1.000.
- Não alterar configuração OpenCode, contratos de subagentes ou fornecedores.
- Pesquisa GitHub/Gitee/GitTrend serve como referência arquitetural, não como
  validação independente da qualidade deste projeto.

## Critérios de aceitação executáveis

- `R1243-LIMITS` — `get_recent_context`, `search_memory` e `get_recent_events`
  aceitam apenas limites inteiros não booleanos em `[0, 1000]`. Limite zero
  retorna lista vazia; valores inválidos geram `ValueError` antes de percorrer
  memória/log.
- `R1243-REFLECTION` — `add_reflection` exige agente, contexto e reflexão úteis;
  score numérico, finito, não booleano e em `[0, 1]`. Rejeição não altera
  episódio/ledger. Falha de persistência gera erro explícito e restaura ambos.
  Sucesso mantém a fórmula EMA de SPEC-001.
- `R1243-RETENTION` — após gravação bem-sucedida, episódios em memória e arquivo
  JSON preservam a mesma cauda de até 1.000 registros. Falha não trunca memória.

## Evidência e limites inferenciais

Os critérios são cobertos por testes offline com caminhos temporários. A
aprovação demonstra apenas o contrato local implementado e executado nesta
versão; não comprova concorrência entre processos, recuperação de arquivo
corrompido, segurança geral, calibração estatística do ledger ou prontidão
comercial do ecossistema.

## Pesquisa externa observada

Referências somente conceituais, consultadas em 2026-11-20: `mem0ai/mem0`,
`vectorize-io/hindsight`, `topoteretes/cognee`, `letta-ai/letta` e
`langchain-ai/langgraph`; GitTrend `/`, `/best`, `/topics`, `/rising`,
`/hidden-gems`, `/insights`, `/languages`, `/trending/developers`,
`/best/ai-memory`, `/best/ai-agent` e `/best/ai-workflow`. GitTrend é tratado
como índice/ranking derivado de atividade e estrelas GitHub, não como evidência
de qualidade ou auditoria de segurança. O endpoint público Gitee API v5 de
busca retornou listas vazias para consultas em inglês durante esta análise; isso
não prova ausência de repositórios relevantes no Gitee.
