# SPEC-935-R728 — Cadeia do scir com nota GPL sem federar

**Status:** `em implementação`
**Ciclo:** R728→R729
**Data:** 2026-10-07
**Base:** R715 (scir proposto ativo 12d) + pin vivo GPL-3.0 federável

## 1. Problema

O `idiap/scir` é o próximo prioritário com pin fresco e licença viva, mas sem
cadeia local. Atenção: API declara `GPL-3.0` (copyleft) — a decisão e a futura
federação exigem nota explícita de que uso como referência não contamina, mas
derivação de código exigiria GPL.

## 2. Objetivo

Diretório `/tmp/polymath_lote3_scir` com importação fresca + aprovação única do
scir + clone `--depth 1` + readiness + inventário + minuta + parecer com nota
GPL, sem federação, sem tocar em final/lote2/rede-4.

## 3. Critérios de aceitação

- [ ] AC1 — Lote3: 16 intenções, 1 aprovada (scir, pin 12d GPL viva), 15 aguardando.
- [ ] AC2 — Clone `idiap__scir` com HEAD + `aquisicoes.jsonl`; readiness 1 pronta; inventário com marcos; minuta 1; parecer com `nota_gpl`.
- [ ] AC3 — Testes R716–R722 verdes (reuso); `doctor` sem novos falhos.
- [ ] AC4 — Anti-overclaim: `candidato`, nota copyleft explícita, nada federado.

## 4. Fora de escopo

- Federação, rede, decisão das 15 restantes.

## 5. Verificação

- `resumo` 1/0/15; readiness 1 pronta; minuta 1; parecer com GPL.
