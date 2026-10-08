# SPEC-935-R744 — Cadeias fora do /tmp: custódia durável das decisões

**Status:** `em implementação`
**Ciclo:** R744→R745
**Data:** 2026-10-07
**Base:** R743 (clones duráveis; cadeias ainda em /tmp volátil, ~500KB)

## 1. Problema

Intenções, decisões, readiness, minutas, pareceres, pins e proposta vivem em
`/tmp/polymath_*`: um reboot apaga a trilha que sustenta os 16 federados.

## 2. Objetivo

Espelhar `/tmp/polymath_*` (exceto clones, já duráveis) em
`workbench/polymath/cadeias/<lote>/` com `MANIFESTO.json` (bytes+sha256 por
arquivo) e teste de integridade que reconfere hashes em disco.

## 3. Critérios de aceitação

- [ ] AC1 — Todos os JSONs/JSONL espelhados byte-idênticos (sha).
- [ ] AC2 — `MANIFESTO.json` com total de arquivos e sha por arquivo.
- [ ] AC3 — Teste hermético reconfere cada sha; `doctor` íntegro.
- [ ] AC4 — Sem commit neste turno (ordem futura explícita).

## 4. Fora de escopo

- Clones (R743), federação nova, commit.

## 5. Verificação

- Espelho + teste verdes.
