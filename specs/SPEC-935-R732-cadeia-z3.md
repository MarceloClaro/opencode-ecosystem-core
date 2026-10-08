# SPEC-935-R732 — Cadeia do z3 com override MIT sem federar

**Status:** `em implementação`
**Ciclo:** R732→R733
**Data:** 2026-10-07
**Base:** R715 (z3 proposto formal-estavel 0d + override MIT sha e617cad2)

## 1. Problema

O pilar dedutivo/formal segue sem cadeia: `Z3Prover/z3` tem pin fresco 0d e
MIT confirmado em `LICENSE.txt`, mas pin API bloqueado e clone grande. Falta
cadeia local com override para futura decisão.

## 2. Objetivo

Diretório `/tmp/polymath_lote5_z3` com aprovação única + clone `--depth 1` +
readiness com override + inventário + minuta + parecer, sem federação.

## 3. Critérios de aceitação

- [ ] AC1 — 1 aprovada (z3), 15 aguardando.
- [ ] AC2 — Clone com HEAD, readiness pronta com override, minuta 1, parecer.
- [ ] AC3 — Testes R716–R722 verdes; `doctor` sem novos falhos; tolerar clone pesado com timeout e fallback documentado.
- [ ] AC4 — Nada federado; rede-6 intacta.

## 4. Fora de escopo

- Federação, rede, decisão das 15.

## 5. Verificação

- Cadeia completa em `/tmp/polymath_lote5_z3` ou fallback justificado.
