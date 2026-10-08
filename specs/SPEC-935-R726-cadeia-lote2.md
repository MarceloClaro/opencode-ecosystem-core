# SPEC-935-R726 — Cadeia completa do lote2 (dowhy + CausalPy) sem federar

**Status:** `em implementação`
**Ciclo:** R726→R727
**Data:** 2026-10-07
**Base:** R725 (dowhy + CausalPy rejeitados por falta de cadeia, prioritários)

## 1. Problema

Os prioritários têm pin fresco e proposta, mas zero cadeia local: sem clone,
readiness, inventário, minuta ou parecer. Nova decisão sem cadeia repetiria a
rejeição R725.

## 2. Objetivo

Diretório `/tmp/polymath_lote2` com importação fresca + `decidir_lote` aprovando
só dowhy + CausalPy (pin fresco 0d + proposta ativo + licença viva API) +
clone `--depth 1` + readiness + inventário + minuta + pareceres, sem rede além
dos clones, sem federação, sem tocar no final 2/14.

## 3. Critérios de aceitação

- [ ] AC1 — Lote2: 16 intenções, 2 aprovadas (dowhy, CausalPy) com motivos de pin fresco, 14 aguardando.
- [ ] AC2 — Clones `dowhy__dowhy`, `causalpy__causalpy` com HEAD legível + `aquisicoes.jsonl`.
- [ ] AC3 — Readiness 2 prontas (pin federável + clone), inventário com marcos, minuta 2, pareceres 2.
- [ ] AC4 — Testes R716–R722 verdes (reuso, sem código novo salvo colagem); `doctor` sem novos falhos.
- [ ] AC5 — Anti-overclaim: tudo `candidato`, nada federado; decisão das 2 restrita ao lote2.

## 4. Fora de escopo

- Federação, rede, re-pin, decisão das 14 do lote2.

## 5. Verificação

- `resumo` 2/0/14; readiness 2 prontas; minuta 2; pareceres 2.
