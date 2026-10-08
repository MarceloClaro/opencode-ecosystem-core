# SPEC-935-R733 — Cadeia do EvidenceSynthesis com override Apache sem federar

**Status:** `em implementação`
**Ciclo:** R733→R734
**Data:** 2026-10-07
**Base:** R715 (EvidenceSynthesis proposto 197d≤730d + override Apache via DESCRIPTION)

## 1. Problema

O `OHDSI/EvidenceSynthesis` (HADES, meta-análise multi-site) tem proposta e
Apache declarado em `DESCRIPTION`, mas pin API bloqueado e zero cadeia local.

## 2. Objetivo

Diretório `/tmp/polymath_lote6_evidence` com aprovação única + clone + readiness
com override + inventário + minuta + parecer, sem federação.

## 3. Critérios de aceitação

- [ ] AC1 — 1 aprovada, 15 aguardando.
- [ ] AC2 — Clone com HEAD, readiness pronta com override, minuta 1, parecer.
- [ ] AC3 — Testes R716–R722 verdes; `doctor` sem novos falhos.
- [ ] AC4 — Nada federado; rede-6 intacta.

## 4. Fora de escopo

- Federação, rede, decisão das 15.

## 5. Verificação

- Cadeia completa em `/tmp/polymath_lote6_evidence`.
