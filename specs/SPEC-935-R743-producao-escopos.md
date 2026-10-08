# SPEC-935-R743 — Produção por escopos: persistência, CI segregado, registro MCP

**Status:** `em implementação`
**Ciclo:** R743→R744
**Data:** 2026-10-07
**Base:** auditoria (5795 ok, 41F+82E alheios e pré-existentes, zero polímata)

## 1. Problema

Produção plena bloqueada por: clones em `/tmp` volátil, CI monolítico de
20min com 123 quebras de outras frentes, registro MCP fora do git. Reescrever
lógica alheia para zerar é outro programa — entrega-se contenção auditada.

## 2. Objetivo

1. Clones em `/home/marceloclaro/polymath_clones` (fora do repo e do /tmp) com
   `REMAP.json` e integridade por sha. 2. `.github/workflows/ci-escopos.yml`
   com escopos `polimata`, `nucleo-cientifico`, `config` verdes-gate e escopos
   alheios em `allow-failure` com donos. 3. Commit cirúrgico só do hunk MCP no
   gerador + `opencode.json` regenerado documentado.

## 3. Critérios de aceitação

- [ ] AC1 — Clones fora do /tmp e do repo, shas conferidos.
- [ ] AC2 — Workflow novo sem editar testes alheios; escopos próprios verdes.
- [ ] AC3 — Commit contém só hunk MCP + json regenerado documentado; resto alheio intocado.
- [ ] AC4 — Triagem das 123 arquivada com donos por spec.

## 4. Fora de escopo

- Correção de lógica alheia (livro, notebook, deepmind).

## 5. Verificação

- Escopos verdes locais; `doctor` íntegro; commit com stat auditado.
