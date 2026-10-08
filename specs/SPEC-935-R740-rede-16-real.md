# SPEC-935-R740 — sympy pronto + reasonkit encadeado, rede 14→16

**Status:** `em implementação`
**Ciclo:** R740→R741
**Data:** 2026-10-07
**Base:** R739 errata (caminho real: sympy re-chain + reasonkit cadeia)

## 1. Problema

Faltam 2 para 16: `sympy` com clone+parecer mas sem readiness/minuta com
override; `reasonkit-core` sem cadeia alguma.

## 2. Objetivo

1. Piloto: readiness com override BSD + inventário + minuta + parecer do sympy;
   estender rede 14→15. 2. Lote10: cadeia completa do reasonkit-core;
   estender 15→16. Tudo idempotente, escopo polimata.

## 3. Critérios de aceitação

- [ ] AC1 — sympy pronto (pin suprido + clone) com minuta e parecer.
- [ ] AC2 — reasonkit: 1 aprovada, clone, readiness, minuta, parecer.
- [ ] AC3 — Rede 16/16, federados 16/16; testes verdes; doctor íntegro.

## 4. Fora de escopo

- R621, as 5 retidas.

## 5. Verificação

- Merges auditados 15 e 16; `pytest` verde.
