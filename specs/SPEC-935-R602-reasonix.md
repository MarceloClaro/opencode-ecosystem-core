# SPEC-935-R602 — Integração da CLI Reasonix (DeepSeek-Reasonix)

**Ronda:** R602
**Status:** implementado
**Data:** 2026-09-26
**Autor:** marceloclaro (orquestrador central)
**Padrão:** M7 — Executor externo orquestrável (espelho R598/R599/R600)

## Objetivo

Tornar o **Reasonix** (`esengine/DeepSeek-Reasonix`, MIT) orquestrável pelo
OpenCode Ecosystem Core com SDD/TDD. Reasonix é um agente de codificação
DeepSeek-native: loop otimizado para prefix-cache (custo baixo em sessões
longas), modo one-shot `run` para pipes e `doctor` para health check.

## Fonte de verdade (anti-overclaim — consultado 2026-09-26)

- README oficial (`main` e `main-v2`): v2 é o rewrite Go ativo ("a single Go
  binary"); a v0.x TypeScript é maintenance mode. Instalação via npm global
  (`npm install -g reasonix`), alias `dsnix`, npx one-shot, Homebrew (macOS).
- Comandos: `reasonix setup` (provider/modelo), `reasonix run "<task>"`
  (one-shot, streams stdout, bom para pipes), `reasonix doctor` (Node, API key,
  MCP wiring), `reasonix update`, subcomandos `replay|diff|events|stats|index|
  mcp|prune-sessions`; `--dir` retarget de pasta.
- Auth: DeepSeek API key colada no primeiro uso (platform.deepseek.com/api_keys);
  persistida. Config v2: `reasonix.toml` (config-driven; qualquer endpoint
  OpenAI-compatível, DeepSeek é preset).

## Escopo

- `integrations/reasonix_cli.py`: status, versão, run one-shot, doctor, install,
  CLI `main()` com flags reais.
- `agents/catalog/reasonix-cli.md` (Agent Card), skill, comando `/reasonix`.
- `marceloclaro/doctor.py`: entrada `reasonix` em `EXTERNAL_CLIS`.
- `tests/test_r602_reasonix.py` (unit mocks) + stub de integração em
  `tests/test_r598_r599_external_stubs.py` (subprocess real).
- Ciclo R602 no formato canônico (timestamp + objective — lição R581/R110/R601).

## Critérios de aceitação

1. `reasonix_available()` via `shutil.which("reasonix")` (tolerante).
2. `reasonix_version()` → semver (`reasonix --version`); None se ausente/falha.
3. `reasonix_run(task)` monta `[reasonix, "run", task]` (lista, sem shell);
   captura stdout/stderr/returncode; nunca lança.
4. `doctor_check()`: pass se `reasonix doctor` exit 0; warn se binário ausente.
5. `install_instructions()` documenta npm/npx + DeepSeek API key.
6. `main()`: `status|run|doctor|install|setup` + `--help`; `run` exige prompt
   (exit 2 se vazio) e aceita `--timeout`.
7. Gate TDD: unit mocks + integração stub (subprocess real em `tmp_path`).
8. Doctor global: `reasonix` listado; comando `/reasonix` no opencode.json.
9. Ciclo R602 registrado em formato canônico.

## Estratégia de validação

- Unit (mocks): versão, comando montado exatamente, doctor pass/warn, exit codes
  do main (0/1/2), tolerância a binário ausente.
- Integração stub: binário `reasonix` stub executável em `tmp_path` + PATH
  sobreposto (paths: `run`, `doctor`, `--version`).
- Sem DeepSeek API key, `run` real retorna não-zero (auth) — comportamento
  esperado, não falha da integração.

## Decisões registradas

- Orquestramos apenas `run` (one-shot) e `doctor` — o TUI interativo fica fora
  do escopo da orquestração (limitação de infraestrutura já documentada R601).
- `--dir` não é exposto nesta ronda (posição de flag incerta entre v0.x/v2);
  documentado na skill como opção manual.
- Reasonix não substitui o orquestrador como dono do ciclo SDD/TDD do Core.