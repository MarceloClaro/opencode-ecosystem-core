# SPEC-935-R746 — Rodada 1→5: re-pin, retidos, quarentena, dossiê vivo, cota

**Status:** `em implementação`
**Ciclo:** R746→R747
**Data:** 2026-10-07
**Base:** R745 (vigia: 15 ok, 1 aviso)

## 1. Problema

Melhorias ranqueadas pendentes: pins envelhecendo, 5 retidos sem rechecagem,
quarentena sem verificação recorrente, dossiê estático e clones sem cota.

## 2. Objetivo

1. Re-pin vivo dos 21 sem token (respeitando 60 req/h) + vigia atualizada.
2. Rechecagem dos 5 retidos: só avança com mudança real (push, licença, jurídico).
3. Reverificação da quarentena alheia sem tocar em código alheio.
4. Dossiê + painel regenerados do estado atual.
5. Cota de clones medida e registrada (teto 2GB, alerta).

## 3. Critérios de aceitação

- [ ] AC1 — Pins atualizados com tolerância; sem token segue documentado.
- [ ] AC2 — Retidos: mudança real ou `sem_mudanca` registrado por lab.
- [ ] AC3 — Quarentena reverificada, sem edição alheia.
- [ ] AC4 — Dossiê/painel regenerados; testes verdes; doctor íntegro.
- [ ] AC5 — Cota medida; `doctor` íntegro.

## 4. Fora de escopo

- Correção alheia, federação nova, token.

## 5. Verificação

- Artefatos datados + evolução.
