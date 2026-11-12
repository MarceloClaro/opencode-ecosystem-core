# SPEC-935-R1108 — Reconciliação de MCP, federação, skill e documentação

Data: 2026-11-12. Estado: implementado e verificado localmente.

## Demanda

O checkout continha entregas R1088–R1107 sem commit, além de três artefatos
inconsistentes: `federation/activated.json` sobrescrito por Markdown,
`evolution/cycles.json` poluído com ciclos de teste e uma skill Tiangong
incompleta em `.opencode/skills/tiangong-harness` cujos stubs simulavam
resultados. A documentação operacional ainda declarava 30 MCPs e 35 comandos.

## Escopo

1. Restaurar `federation/activated.json` como JSON válido no schema
   `federation-activated-mcp/v2`, sem inventar probe ou smoke.
2. Remover de `evolution/cycles.json` somente os ciclos de teste
   `R-test-001` e `R1102-iit-003/004/005`, preservando `R1108`.
3. Publicar a skill Tiangong em `.opencode/skills/tiangong-harness/{HDR,RSIR,VRP}`
   com `SKILL.md`, `skill.py` que delega a `integrations.tiangong_mcp` e testes
   próprios; remover stubs que retornavam resultado simulado.
4. Alinhar os 13 testes Colibri de `tests/test_r660_mcp_validation.py` à API
   JSON-RPC atual e validar entradas antes do provedor.
5. Corrigir o gate de licença do harness para ler `metadata.license` e o teste
   R394 para enviar `argv` explícito em `/federacao`.
6. Sincronizar contagens e estado em `README.md`, `docs/README.md`,
   `ARCHITECTURE.md`, `MANUAL.md`, `CLAUDE.md`, `PROGRESS.md`, `CHANGELOG.md`
   e instaladores.
7. Impedir no `.gitignore` que o pacote externo `educacao_quantica_bohm-*`
   (177 MB) e o staging `.skills/`/`.specs/` entrem no Git.
8. Commitar e enviar para `origin/main` somente depois de testes verdes.

## Fora do escopo

- Regenerar `opencode.json` inteiro: a divergência com `build_config()` inclui
  escolhas locais (`uvx`, `npx`) e `playwright` com smoke falho.
- Declarar disponibilidade de MCP, autenticação de provider ou execução real
  dos adaptadores R1106–R1107.
- Calcular Φ, validar consciência ou promover trust por autoavaliação.

## Critérios de aceitação

- CA01: `federation/activated.json` é JSON válido e contém os seis servidores
  históricos; `activation.md` reflete o smoke observado.
- CA02: `evolution/cycles.json` é JSON válido, não contém os quatro ciclos de
  teste e mantém `R1108` como último ciclo.
- CA03: as três skills Tiangong passam em **20 testes** e não retornam dígito,
  rótulo ou rota fabricados.
- CA04: `tests/test_r660_mcp_validation.py` passa com a API JSON-RPC atual;
  entrada inválida retorna `-32602` antes de instanciar o provedor.
- CA05: 95 testes de R1088–R1107 permanecem verdes.
- CA06: `doctor` via `.venv/bin/python` termina com 0 falhas.
- CA07: contagens reconciliadas: 337 agentes, 32 MCPs, 39 comandos, 22 checks.
- CA08: o commit não inclui o pacote externo de 177 MB nem staging local.

## Evidência

- `tests/test_r1088_mcp_recovery.py` … `tests/test_r1107_opencode_cli_adapter.py`
  → 95 passed.
- `.opencode/skills/tiangong-harness/*/test_*_skill.py` → 20 passed.
- `tests/test_r660_mcp_validation.py` + `tests/test_r1088_mcp_recovery.py`
  → 86 passed.
- Bateria final (R394, R621, R660, R1088–R1107, federação, R652 e skills
  Tiangong) → 322 passed.
- `.venv/bin/python -m marceloclaro.cli doctor` → 16 pass, 6 warn, 0 fail.
- `scripts/reconcile_operational_docs.py --check` → sem documentos divergentes
  após a sincronização.

## Limites

Testes locais não comprovam disponibilidade futura de MCP, autenticação de
provider, execução real de modelo ou validação externa. A skill e o MCP são
contratos locais; o backend Tiangong permanece não observado.
