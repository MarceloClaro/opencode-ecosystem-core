# SPEC-935-R598 — Integração da CLI Goose (AAIF/Linux Foundation)

**Status:** implementado · **Gate TDD:** tests/test_r598_goose_cli.py
**Ciclo de evolução:** R598 · **Data:** 2026-09-25

## Objetivo

Integrar a **CLI oficial do Goose** (`aaif-goose/goose`, Apache-2.0, 53k+ stars,
parte da Agentic AI Foundation no Linux Foundation) ao OpenCode Ecosystem Core
como **executor externo orquestrável** — mesma família de integração de
bernostein/opencode-go-agent (padrão M7: invocação por subprocess com
healthcheck tolerante).

Goose é um agente de IA generalista em Rust (desktop + CLI + API) que suporta
15+ providers (Anthropic, OpenAI, Google, Ollama, OpenRouter, Azure, Bedrock —
inclusive via ACP com assinaturas existentes) e 70+ extensões via Model Context
Protocol (MCP).

## Escopo

1. `integrations/goose_cli.py` — runner tolerante: `status`, `run` (headless
   `goose run --text`), `doctor`, `install` (instrução oficial).
2. `agents/catalog/goose-cli.md` — Agent Card do Goose no catálogo (passa a
   existir como subagente `goose-cli` no OpenCode CLI após regeração).
3. `marceloclaro/doctor.py` — registro de `goose` em `EXTERNAL_CLIS`
   (ausente → `warn`, nunca `fail`; Goose é opcional).
4. `integrations/opencode_cli.py` — comando custom `/goose` (status/run/doctor).
5. `.opencode/skills/goose-cli/SKILL.md` — guia de uso da CLI Goose no Core.
6. Testes TDD com mocks (independem do Goose instalado).

## Critérios de aceitação

1. `pytest tests/test_r598_goose_cli.py tests/test_r598_r599_external_stubs.py`
   → 15/15 verdes (mocks) + testes de integração stub (subprocess real;
   sem depender do binário `goose` instalado).
2. `python3 -m integrations.goose_cli status` → resposta estruturada
   (`{disponivel, versao}`); com Goose ausente, `disponivel: false` sem erro.
3. `python3 -m integrations.goose_cli doctor` → formato DoctorCheck compatível
   (`name/status/detail`), `warn` quando ausente.
4. `python3 -m marceloclaro.cli doctor` continua 18/20, 0 falhas (goose ausente
   entra como warn na chave `external_clis`).
5. `python3 -m integrations.opencode_cli --check` → configuração reproduzível
   com o novo agente `goose-cli` e o comando `/goose`.

## Estrutura

```
integrations/goose_cli.py                # runner (subprocess, healthcheck, doctor)
agents/catalog/goose-cli.md              # Agent Card
tests/test_r598_goose_cli.py             # 15 testes TDD (mocks)
tests/test_r598_r599_external_stubs.py  # integração stub (subprocess real)
.opencode/skills/goose-cli/SKILL.md      # guia de uso
```

## Resultado real (validação)

- Goose **não instalado** no ambiente de validação → status `{disponivel: false}`,
  doctor `warn` com instrução oficial (`curl -fsSL ...aaif-goose/goose/.../download_cli.sh | bash`).
- Testes 15/15 verdes com mocks + testes de integração stub (subprocess
  real em tmp_path).
- Suíte completa do ecossistema sem regressão.
- Após `python3 -m integrations.opencode_cli`, catálogo passa a conter o
  subagente `goose-cli` (slug do arquivo) e o comando `/goose`.