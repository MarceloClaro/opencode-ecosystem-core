# SPEC-935-R466: Fallback Operacional do runai via Código-Fonte

## Objetivo
Tornar a integração do `runai` **operacional mesmo sem publicação no npm**,
usando um checkout válido do repositório oficial `midudev/canirun.ai` como
fonte de execução (`RUNAI_SOURCE_DIR`).

## Descoberta empírica que motiva esta spec
- O site público e o instalador estável apontam para `@canirun/runai@latest`.
- O endpoint do npm para esse pacote respondeu **404** durante validação real.
- O repositório público `midudev/canirun.ai` contém `packages/runai/package.json`
  com `name: @canirun/runai`, `version: 0.2.1` e documentação de CLI/API.
- Validação real mostrou que o CLI funciona a partir do workspace fonte após:
  - `pnpm install`
  - `pnpm packages:build`
  - `pnpm --filter @canirun/runai run dev -- doctor --json`
  - `pnpm --filter @canirun/runai run dev -- browse qwen --limit 3 --json`

## Escopo
### Incluído
- `RunAIProvisioner` com **source mode** quando `RUNAI_SOURCE_DIR` aponta para
  um checkout válido do repositório oficial.
- Diagnóstico explícito distinguindo:
  1. binário publicado instalado;
  2. fallback via código-fonte pronto;
  3. upstream npm inconsistente.
- Smoke real não destrutivo do CLI via código-fonte.

### Excluído
- Baixar modelos pesados por padrão.
- Integrar `serve` ao `ModelRouter.route_and_complete()` sem smoke com modelo real.

## Critérios de Aceitação
- [E1] `RunAIProvisioner.runtime_mode()` distingue `binary`, `source`, `unavailable`.
- [E2] `source_diagnosis()` reporta checkout, bun/pnpm, dependências e build.
- [E3] `doctor()`/`help()`/`version()` funcionam em source mode.
- [E4] O `doctor` do ecossistema informa corretamente o problema upstream do npm.
- [E5] Há teste real em `/tmp/opencode` comprovando `doctor --json` e `browse --json`
      no workspace oficial.

## Anti-overclaim
- O fallback por código-fonte prova operacionalidade do CLI, não a publicação
  correta do pacote no npm.
- A existência de endpoints OpenAI-compatible no README do `runai` não implica
  integração automática ao roteador do Core sem smoke adicional com modelo real.

## Registro
- Autores: Marcelo Claro Laranjeira
- Data: 03 de setembro de 2026
- Ciclo: R466
