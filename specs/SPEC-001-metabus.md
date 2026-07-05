---
spec_id: SPEC-001
component: mci.metabus
title: MetaBus e Memória Metacognitiva (Global Workspace)
version: 1.0.0
status: approved
test_file: tests/test_ecosystem.py
---

# SPEC-001 — MetaBus e Memória Metacognitiva

## Objetivo
Prover um barramento de eventos unificado (Global Workspace) com memória metacognitiva compartilhada (episódica, semântica e confidence ledger) para todos os agentes do ecossistema.

## Requisitos Funcionais

| ID | Requisito | Critério de Aceitação | Teste |
|---|---|---|---|
| RF-001.1 | Publicar eventos em tópicos | `publish(topic, payload, source)` retorna nº de handlers despachados >= 0 | `test_metabus_publish_subscribe` |
| RF-001.2 | Assinar tópicos | Handler inscrito recebe o evento com `payload` íntegro | `test_metabus_publish_subscribe` |
| RF-001.3 | Registrar reflexões | `add_reflection` insere entrada episódica com `agent_id`, `context`, `reflection`, `score` | `test_memory_reflection_updates_confidence` |
| RF-001.4 | Atualizar confiança via EMA | Após reflexão com score 1.0, confiança do agente aumenta; com score 0.0, diminui | `test_memory_reflection_updates_confidence`, `test_failed_task_lowers_confidence` |
| RF-001.5 | Persistir estado | Estado da memória sobrevive a reinicializações via diretório `MCI_STATE_DIR` | `test_metabus_persistence` |

## Invariantes (Contratos)

1. **INV-001.1**: `confidence_ledger[agent_id]` DEVE permanecer no intervalo [0.0, 1.0].
2. **INV-001.2**: Toda entrada episódica DEVE conter `id`, `timestamp`, `agent_id`.
3. **INV-001.3**: A fórmula EMA é fixa: `nova_conf = conf_atual * 0.7 + score * 0.3`.
4. **INV-001.4**: `publish` NUNCA deve lançar exceção por falha de um handler individual.

## Não-Objetivos
- Comunicação entre processos/máquinas (escopo: in-process).
- Garantias de ordem de entrega entre tópicos distintos.
