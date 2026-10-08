# SPEC-935-R735 — Cadeias trAIce + repro_audit com janela por classe

**Status:** `em implementação`
**Ciclo:** R735→R736
**Data:** 2026-10-07
**Base:** R715 (trAIce proposto 300d≤730d MIT; repro_audit proposto 298d≤1095d MIT)

## 1. Problema

Ambos têm pin bloqueado na lógica API de 90d apesar de dentro da janela da
classe e com licença viva. O readiness só lia `pin.federavel`, sem janelas —
cadeia honesta exigiria re-pin que repetiria o bloqueio.

## 2. Objetivo

Readiness aceita `janelas` opcional (classe→dias via `polymath_federacao`):
bloqueio só-idade suprido quando `idade ≤ janela da classe` + commit válido +
não arquivado + licença ok ou override. Lotes `/tmp/polymath_lote7_traice` e
`/tmp/polymath_lote8_repro` com cadeia completa, sem federação.

## 3. Critérios de aceitação

- [ ] AC1 — Janelas nunca suprem licença, arquivo ausente ou commit inválido.
- [ ] AC2 — trAIce: 1 aprovada, readiness pronta em 730d, minuta 1, parecer.
- [ ] AC3 — repro_audit: 1 aprovada, readiness pronta em 1095d, minuta 1, parecer; auditoria fecha o tipo.
- [ ] AC4 — Testes R718 verdes + novo caso janela; `doctor` sem novos falhos.
- [ ] AC5 — Nada federado; rede-8 intacta.

## 4. Fora de escopo

- Federação, rede, novas aprovações além das 2.

## 5. Verificação

- Cadeias completas nos 2 diretórios.
