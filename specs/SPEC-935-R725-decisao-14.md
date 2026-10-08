# SPEC-935-R725 — Decisão individual das 14 restantes sem baixar a barra

**Status:** `em implementação`
**Ciclo:** R725→R726
**Data:** 2026-10-07
**Base:** R724 (`/tmp/polymath_federacao_final` 2 aprovadas + 14 aguardando)

## 1. Problema

Quatorze intenções seguem aguardando sem motivo individual. Aprovar sem a
tríade (minuta+parecer+readiness pronto, padrão pgmpy/prisma) baixaria a barra
e fabricaria prontidão. Falta decisão nominal uma a uma que preserve o padrão.

## 2. Objetivo

Rejeitar neste lote, com motivo individual por URL derivado de proposta R715 +
pin R714 (dias, janela, licença, cadeia ausente), as 14 restantes em
`/tmp/polymath_federacao_final` via `inten.decidir` com `humano=true`,
`responsavel=titular`, mantendo as 2 aprovações e as 5 retidas. Rejeição é
`aguardar cadeia completa`, nunca veto permanente; re-propositura futura com
minuta/parecer/readiness permanece aberta.

## 3. Critérios de aceitação

- [ ] AC1 — 14 chamadas nominais, cada motivo cita dias/janela ou licença/cadeia daquela URL.
- [ ] AC2 — Resumo final: `total 16, aprovadas 2, rejeitadas 14, aguardando 0, retidas 5`.
- [ ] AC3 — `decisoes_humanas.jsonl` com 16 linhas (2 aprovações + 14 rejeições).
- [ ] AC4 — Nenhuma aprovação sem tríade; nenhum `federado|verificado` novo.
- [ ] AC5 — Rede e federados seguem com 2; sem escrita em harness.

## 4. Fora de escopo

- Nova aprovação, clone, federação, re-pin.

## 5. Verificação

- `resumo()` confere 2/14/0; `pytest` R716+R724 verde; `doctor` sem novos falhos.
