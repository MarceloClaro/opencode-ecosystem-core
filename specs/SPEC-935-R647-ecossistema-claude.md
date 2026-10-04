# SPEC-935-R647 — Ecossistema Claude: harness + plugins + Agent SDK Python

**Ronda:** R647 (SPEC) / evolução R650
**Status:** em implementação
**Data:** 2026-10-03
**Autor:** marceloclaro (orquestrador central)
**Padrão:** M7 federado — ponte/curadoria (espelho de R621 federação + R645/R646 pontes)

## Objetivo

Orquestrar três forks Claude no OpenCode Ecosystem Core, cada um na trilha
adequada ao seu tipo (nenhum vira executor padrão; `marceloclaro` segue dono
do SDD/TDD; anti-overclaim R110):

| # | Repo (fork) | Upstream | Tipo | Trilha |
|---|---|---|---|---|
| 1 | `MarceloClaro/claude-code-harness` | `Chachamaru127/claude-code-harness` (MIT, 1326 commits) | Harness metodológico Plan→Work→Review com `opencode/` + `scripts/setup-opencode.sh` (tier internal-compatible), 5 verb skills, `bin/harness doctor` | Curadoria metodológica + federação de artefatos opencode |
| 2 | `MarceloClaro/claude-plugins-official` | `anthropics/claude-plugins-official` (73 commits, **licença por plugin**) | Marketplace `/plugins` + `/external_plugins`, install `/plugin install {n}@claude-plugin-directory` | Federação R621 com gate de licença por plugin + aviso de trust |
| 3 | `MarceloClaro/claude-agent-sdk-python` | `anthropics/claude-agent-sdk-python` (892 commits, LICENSE MIT **+ Commercial Terms no README**) | SDK Python (`query()`, `ClaudeSDKClient`, in-process MCP, hooks; CLI `claude` embutido) | Ponte `integrations/claude_agent_sdk.py` (presença/versão/payload, sem disparo faturável) |

## Fonte de verdade (anti-overclaim)

Páginas GitHub lidas em 2026-10-03 (webfetch) + API:
- Harness: "Plan. Work. Review. Ship", tiers (Claude supported; Codex/OpenCode
  internal-compatible; Copilot candidate; Antigravity future/unsupported),
  `not_observed != absent`, Go-native (sem Node), `harness-mem` opcional.
- Plugins: aviso oficial — Anthropic não controla MCP servers/arquivos dos
  plugins; checar homepage de cada plugin. Licença: por plugin.
- SDK: `pip install claude-agent-sdk` (Python 3.10+), CLI embutido (ou
  `curl claude.ai/install.sh | bash`, `cli_path=` custom), `query()` async,
  `allowed_tools` é allowlist (não remove tools; bloquear via
  `disallowed_tools`), erros `CLINotFoundError/ProcessError/ResultError`,
  `Commercial Terms` regem o uso.

## Escopo

- `integrations/claude_agent_sdk.py`: `claude_available/cli_version`,
  `sdk_dep_status()`, `sdk_available()`, `build_query_options()` (puro),
  `doctor_check()`, `install_instructions()`, `main()` —
  `status|doctor|install|options`.
- `agents/catalog/claude-code-harness.md`, `claude-plugins-official.md`,
  `claude-agent-sdk-python.md`: cards (harness/plugins = curadoria;
  sdk = ponte).
- `.opencode/skills/`: `claude-code-harness/SKILL.md` (loop + setup-opencode),
  `claude-plugins/SKILL.md` (marketplace + trust gate),
  `claude-agent-sdk-python/SKILL.md` (ponte + exemplos sem execução).
- `integrations/opencode_cli.py`: comando `/claude-sdk` (ponte).
  Harness/plugins **sem comando** (sem runner; docs via skills/cards).
- `tests/test_r647_claude_agent_sdk.py` (unit, mocks).
- Sem `EXTERNAL_CLIS` novas (`claude` já existe); sem execução faturável.
- Ciclo de evolução R650.

## Critérios de aceitação

1. `claude_available()` = `shutil.which("claude")`; `cli_version()` semver
   de `claude --version`; `None` se ausente; nunca lança.
2. `sdk_dep_status()` = `find_spec("claude_agent_sdk")` sem importar.
3. `sdk_available()` = dep presente (CLI é check separado).
4. `build_query_options(prompt, system_prompt, allowed_tools, max_turns,
   cwd, permission_mode)` valida prompt não vazio → dict no schema
   `ClaudeAgentOptions`; `ValueError` em português se inválido.
5. `doctor_check()`: `pass` com dep + CLI; `warn` indicando a peça (NUNCA fail).
6. `install_instructions()`: pip + CLI embutido/custom + Python 3.10+ +
   aviso Commercial Terms + auth (conta Claude).
7. `main()`: `status|doctor|install|options` + `--help`; exit 2 em misuse.
8. Gate TDD: `pytest tests/test_r647_claude_agent_sdk.py` 100% (mocks).
9. `/claude-sdk` no `opencode.json` regenerado + 3 cards + 3 skills.
10. Doctor global 0 fail. Ciclo R650 registrado.

## Decisões registradas

- Harness NÃO é clonado/executado: 1326 commits, metodologia; o Core absorve
  o loop (spec→plan→work→review→release já é o nosso SDD/TDD) e referencia o
  `setup-opencode.sh` como rota opt-in do operador.
- Plugins NÃO são instalados: licença por plugin + aviso de trust exigem
  curadoria caso a caso (federação R621 futura, não nesta ronda).
- SDK NÃO dispara `query()`: chamadas são faturáveis e exigem conta; a ponte
  monta options e documenta — execução pertence ao operador.
- `allowed_tools ≠ remoção`: registrar a semântica correta no SKILL para
  evitar falha de permissão por modelo mental errado.
