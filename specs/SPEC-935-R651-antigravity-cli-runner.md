# SPEC-935-R651 — Runner direto Antigravity CLI (complemento ao bridge)

**Ronda:** R651 (SPEC)
**Status:** em implementação
**Data:** 2026-10-04
**Autor:** marceloclaro (orquestrador central)
**Padrão:** M7 — Executor externo orquestrável (espelho de R600 gemini-cli)

## Objetivo

Dar ao Core invocação direta do `agy` (1.2.16 instalado) no padrão M7
(`status/version/run/doctor/install` + `/agy`), **sem substituir** a
integração profunda existente (`integrations/antigravity/bridge.py` +
MCP + executor `antigravity` no ecosystem-network, SPEC-046/R621).

## Fonte de verdade (anti-overclaim)

- `agy --help` local: `--agent`, `--print/-p`, `--output-format text|json|
  stream-json`, `--model`, `--effort`, `--sandbox`, subcomando `agent`.
- `bridge.py::delegate`: modo não-interativo = `--agent A --print PROMPT
  --output-format text`; sintaxe errada abre TUI (`bubbletea: error
  opening TTY`); `returncode == 0` com stdout `CLI error:/Error:` = falha
  silenciosa (inspecionar saída, não só rc). Este runner replica a forma
  canônica e a inspeção.
- Upstream: `google-antigravity/antigravity-cli` (oficial, 2459 stars);
  licença não declarada na API (registrar como desconhecida até checagem).

## Escopo

- `integrations/antigravity_cli.py`: `agy_available/version/run`
  (forma canônica + inspeção de falha silenciosa), `doctor_check()`,
  `install_instructions()` (script oficial), `main()` —
  `status|run|doctor|install`.
- `agents/catalog/antigravity-cli.md` (runner; aponta o bridge/executor) +
  `.opencode/skills/antigravity-cli/SKILL.md`.
- `marceloclaro/doctor.py`: versionamento de `agy` (entrada já existe).
- `integrations/opencode_cli.py`: `/agy`.
- `tests/test_r651_antigravity_cli.py` (mocks, incl. falha silenciosa) +
  prova ao vivo (`--agent default --print`, limitada por provedor).

## Critérios de aceitação

1. `agy_version()` semver de `agy --version`.
2. `agy_run()` monta `[agy, --agent, A, --print, P, --output-format, F]`
   (+ extras); stdout com prefixo de erro ⇒ `ok: False` mesmo com rc 0.
3. `doctor_check()` pass/warn; `install_instructions()` com script oficial.
4. `main()` completo + exits 0/1/2.
5. Gate TDD 100% + `/agy` no `opencode.json` + ciclo de evolução.
