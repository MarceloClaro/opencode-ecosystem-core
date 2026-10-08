# SPEC-935-R741 — Core herdando o programa polímata: MCP registrado + artefatos persistidos

**Status:** `em implementação`
**Ciclo:** R741→R742
**Data:** 2026-10-07
**Base:** R711→R740 (16 federados, 35+ testes, artefatos em /tmp efêmero)

## 1. Problema

O programa polímata vive em `/tmp` (proposta, pins, gate) e o MCP
`polymath-labs-mcp` não está registrado: reiniciar a máquina apaga as provas e
o orquestrador não invoca as 8 ferramentas. Melhoria do Core = durabilidade +
registrabilidade.

## 2. Objetivo

1. Registrar `polymath-labs-mcp` no gerador `integrations/opencode_cli.py` e
   regenerar `opencode.json` (14→15 MCPs). 2. Persistir proposta+pins+gate em
   `workbench/polymath/` com `INDICE.json` (bytes+sha256). 3. Teste de contrato
   `tests/test_r741_core_polimata.py`.

## 3. Critérios de aceitação

- [ ] AC1 — `opencode.json` contém `polymath-labs-mcp` local habilitado no comando do módulo.
- [ ] AC2 — `workbench/polymath/INDICE.json` lista proposta, pins e gate com sha256 conferíveis.
- [ ] AC3 — Teste hermético valida registro + persistência + ausência de segredo.
- [ ] AC4 — `pytest` verde; `doctor` sem novos falhos.

## 4. Fora de escopo

- R621, clones em repo, federação nova.

## 5. Verificação

- Regeneração auditada; teste verde.
