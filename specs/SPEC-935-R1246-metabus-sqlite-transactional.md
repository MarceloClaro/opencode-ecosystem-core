---
spec_id: SPEC-935-R1246
title: Migração transacional do MetaBus para SQLite
component: mci.metabus
status: planned
test_file: tests/test_r1246_metabus_sqlite.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1246-MIGRATION:
      - tests/test_r1246_metabus_sqlite.py::test_legacy_json_and_jsonl_migrate_once_without_mutating_sources
      - tests/test_r1246_metabus_sqlite.py::test_malformed_event_lines_are_quarantined_and_preserved
      - tests/test_r1246_metabus_sqlite.py::test_corrupt_legacy_memory_blocks_migration_without_mutation
    R1246-TRANSACTION:
      - tests/test_r1246_metabus_sqlite.py::test_reflection_and_retention_commit_to_sqlite_atomically
      - tests/test_r1246_metabus_sqlite.py::test_failed_episode_insert_rolls_back_reflection_and_confidence
      - tests/test_r1246_metabus_sqlite.py::test_failed_event_insert_does_not_dispatch_subscribers
    R1246-CONCURRENCY:
      - tests/test_r1246_metabus_sqlite.py::test_concurrent_process_publishers_preserve_every_event
      - tests/test_r1246_metabus_sqlite.py::test_recent_event_filters_use_indexes_and_keep_chronological_order
    R1246-COMPATIBILITY:
      - tests/test_r1246_metabus_sqlite.py::test_memory_network_reads_sqlite_events_and_episodes
---

# SPEC-935-R1246 — Migração transacional do MetaBus para SQLite

## Objetivo

Substituir `shared_memory.json` e `metabus_events.jsonl` como armazenamento
ativo do MetaBus por SQLite, preservando os dados legados, as APIs públicas de
memória/eventos e os consumidores locais que observam o barramento. A alteração
é restrita ao MetaBus e à projeção de memória que lê seus arquivos de estado.

## Decisões normativas

- O banco padrão é `MCI_STATE_DIR/metabus.sqlite3`; `MCI_DATABASE_FILE` permite
  definir um caminho explícito. SQLite é a fonte autoritativa após a inicialização.
- Uma única transação de migração importa, em ordem, episódios, tópicos
  semânticos, confidence ledger e eventos legados. O marcador de migração,
  `PRAGMA user_version` e os registros importados são confirmados juntos. A
  migração é idempotente. Os JSON/JSONL de origem não são truncados, removidos
  nem reescritos e não recebem novas gravações depois da migração.
- Arquivo `shared_memory.json` presente, mas inválido ou estruturalmente
  incompatível, bloqueia a inicialização com erro explícito; não se cria memória
  vazia nem marcador de sucesso. Linhas inválidas no JSONL são preservadas na
  origem e copiadas para `migration_quarantine` com número da linha, hash,
  conteúdo bruto e motivo; linhas válidas continuam importáveis.
- Esquema v1: `events` (sequência de inserção e JSON integral), `episodes`
  (sequência e JSON integral), `semantic_topics`, `confidence_ledger`, `meta` e
  `migration_quarantine`. Eventos não têm retenção automática; episódios ficam
  limitados à cauda de 1.000 após gravações, mantendo a política R1243.
- Writers públicos usam transações SQLite curtas, `BEGIN IMMEDIATE`, WAL e
  `busy_timeout` finito. `add_reflection` grava episódio e EMA de confiança na
  mesma transação; `record_observation`, operações semânticas e publicação de
  evento também são atômicas. Falha de persistência é explícita. `publish` só
  despacha callbacks depois do commit.
- Consultas recentes e filtradas retornam eventos em ordem cronológica, respeitam
  `limit` e usam índices por tópico/sequência, origem/sequência e sequência.
  Consultas de memória mantêm os formatos de retorno existentes. `_save()` fica
  como compatibilidade explícita para snapshots mutáveis locais; não é o caminho
  normal de escrita multiprocesso.
- `CoreMemoryNetworkSource` consulta o SQLite em modo somente leitura quando o
  banco existe e válido; se o banco estiver ausente, mantém o fallback legado
  JSON/JSONL. Banco presente, porém inválido, produz aviso e não apresenta uma
  projeção legada possivelmente obsoleta como se fosse atual.

## Critérios de aceitação executáveis

- `R1246-MIGRATION` — todos os campos e eventos válidos são importados sem
  duplicação após reinicialização; fontes não mudam; linhas JSONL inválidas são
  preservadas em quarentena; memória legada inválida bloqueia a migração sem
  gravar marcador de conclusão.
- `R1246-TRANSACTION` — reflexão, episódio, confiança e retenção são coerentes
  após reinicialização; falha SQL reverte episódio e confiança; falha ao gravar
  evento não invoca subscribers.
- `R1246-CONCURRENCY` — múltiplos processos publicam eventos sem perda nem
  corrupção; filtros recentes usam os índices declarados e retornam janela
  cronológica correta.
- `R1246-COMPATIBILITY` — a visualização somente leitura vê episódios e eventos
  novos no SQLite, preservando o fallback existente quando o banco não existe.

## Limites

Os testes locais não demonstram durabilidade diante de falha física de hardware,
desempenho sob carga de produção, disponibilidade de rede, segurança geral do
host ou compatibilidade com leitores externos não inventariados. Os snapshots
mutáveis expostos por compatibilidade não são uma API de escrita concorrente;
escritas concorrentes devem usar os métodos públicos transacionais.
