# SPEC-935-R599 — Integração da CLI Plandex (plandex-ai/plandex, MIT)

**Status:** implementado · **Gate TDD:** tests/test_r599_plandex_cli.py
**Ciclo de evolução:** R599 · **Data:** 2026-09-25

## Objetivo

Integrar a **CLI do Plandex** (`plandex-ai/plandex`, MIT, 15.5k+ stars — agente
de codificação AI open source em Go, terminal-based, projetado para tarefas
grandes com muitos arquivos e até 2M tokens de contexto com tree-sitter project
maps) ao OpenCode Ecosystem Core como **executor externo orquestrável** — mesmo
padrão M7 da integração Goose (SPEC-935-R598): invocação por subprocess com
healthcheck tolerante.

Foco da integração no modo **scripting** (não-REPL), com o fluxo natural do
Plandex: criar um plano → descrever a tarefa (`tell`) → revisar o diff pendente
(`diff --plain`) → aplicar/commitar (`apply --commit`).

## Escopo

1. `integrations/plandex_cli.py` — runner tolerante: `status`, `new`, `tell`,
   `chat`, `diff`, `apply`, `plans`, `doctor`, `install`.
2. `agents/catalog/plandex-cli.md` — Agent Card (subagente `plandex-cli`).
3. `marceloclaro/doctor.py` — `plandex` em `EXTERNAL_CLIS` (ausente → warn).
4. `integrations/opencode_cli.py` — comando custom `/plandex`.
5. `.opencode/skills/plandex-cli/SKILL.md` — guia de uso.
6. Testes TDD com mocks (independem do binário instalado).

## Critérios de aceitação

1. `pytest tests/test_r599_plandex_cli.py` → 15/15 verdes (mocks).
2. `python3 -m integrations.plandex_cli status` → `{disponivel, versao}` sem
   erro quando ausente.
3. `python3 -m integrations.plandex_cli doctor` → DoctorCheck compatível,
   `warn` quando ausente.
4. `python3 -m marceloclaro.cli doctor` → 18/20, 0 falhas (plandex ausente
   entra como warn em `external_clis`).
5. `python3 -m integrations.opencode_cli --check` → 212 agentes, 12 comandos.

## Notas de governança

- **Plandex Cloud está sendo encerrado (03/10/2025)** e não aceita novos
  usuários; a integração assume uso local/self-hosted (Docker) ou BYO key
  (ex.: OpenRouter) — sem depender do serviço em nuvem.
- Alterações geradas pelo Plandex ficam em **sandbox de diff** até `apply`;
  o orquestrador `marceloclaro` só aplica com revisão humana no gate SDD/TDD.

## Estrutura

```
integrations/plandex_cli.py             # runner (subprocess, healthcheck, doctor)
agents/catalog/plandex-cli.md           # Agent Card
tests/test_r599_plandex_cli.py          # 15 testes TDD (mocks)
.opencode/skills/plandex-cli/SKILL.md   # guia de uso
```

## Resultado real (validação)

- Plandex **não instalado** no ambiente de validação → `{disponivel: false}`,
  doctor `warn` com instrução oficial (`curl -sL https://plandex.ai/install.sh | bash`).
- Testes 19/19 verdes com mocks + testes de integração stub (subprocess
  real em tmp_path).
- Suíte completa sem regressão; catálogo passa a incluir `plandex-cli`.