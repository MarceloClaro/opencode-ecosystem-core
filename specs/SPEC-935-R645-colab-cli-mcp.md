# SPEC-935-R645 — Integração Google Colab CLI + Colab MCP Server

**Ronda:** R645
**Status:** em implementação
**Data:** 2026-10-03
**Autor:** marceloclaro (orquestrador central)
**Padrão:** M7 — Executor externo orquestrável (espelho de R598/R599/R600/R602)

## Objetivo

Tornar os dois repositórios Colab orquestráveis pelo OpenCode Ecosystem Core
com protocolo SDD/TDD, sem substituir o orquestrador `marceloclaro` como dono
do ciclo de qualidade:

1. `google-colab-cli` (`MarceloClaro/google-colab-cli`, fork de
   `googlecolab/google-colab-cli`, Apache-2.0) — CLI de terminal para
   provisionar runtimes CPU/GPU/TPU, executar código, gerenciar arquivos e
   orquestrar jobs efêmeros (`colab new | exec | run | repl | console | ssh |
   ls | upload | download | install | drivemount | auth | log | usage`).
2. `colab-mcp` (`MarceloClaro/colab-mcp`, fork de `googlecolab/colab-mcp`,
   Apache-2.0) — servidor MCP para codificação assistida interativa
   dentro do notebook (complemento do fluxo terminal, cf. README do CLI:
   *"See the Colab MCP Server"*).

Execução é EXTERNA ao Core; resultados nunca são declarados "verificados"
sem validação (anti-overclaim R110).

## Fonte de verdade (anti-overclaim)

README oficial `googlecolab/google-colab-cli@main` (consultado em 2026-10-03
via webfetch):
- Instalação: `uv tool install google-colab-cli` (recomendado) ou
  `pip install google-colab-cli`.
- Suporte: **Linux e macOS apenas. Windows não suportado.**
- Sessão: `colab new [-s NAME] [--gpu GPU] [--tpu TPU] [--high-mem]`;
  `colab sessions | status | restart-kernel | stop | url`.
- Execução: `colab run [--gpu GPU] [--tpu TPU] [--high-mem] [--keep] SCRIPT
  [ARGS...]`; `colab exec [-s NAME] [-f FILE] [--output-image PATH]`;
  `colab repl | console | ssh`.
- Arquivos: `colab ls | upload | download | rm | edit`.
- Automação: `colab auth | drivemount | install | log | usage | pay |
  version | update`.
- Globais: `--auth {oauth2,adc}`, `-c/--client-oauth-config`,
  `--config PATH` (padrão `~/.config/colab-cli/sessions.json`), `--logtostderr`.
- Metadados locais: `~/.config/colab-cli/sessions.json` e `settings.json`.

API GitHub (2026-10-03): ambos Apache-2.0, linguagem Python, forks criados
em 2026-10-03 pelo operador. `colab-mcp` = *"An MCP server for interacting
with Google Colab"* (layout `src/`, `tests/`, `pyproject.toml`).

## Escopo

- `integrations/colab_cli.py`: status, versão, exec genérico (`colab <args>`),
  atalhos `new/exec/run/stop/sessions`, doctor, install (uv/pip), CLI `main()`.
- `integrations/colab_mcp.py`: presença do servidor MCP (`colab-mcp` / `uvx`),
  versão, montagem de config stdio para `opencode.json` (`mcp_config()`),
  doctor, install.
- `agents/catalog/colab-cli.md` + `agents/catalog/colab-mcp.md`: Agent Cards A2A.
- `marceloclaro/doctor.py`: entradas `colab` e `colab-mcp` em `EXTERNAL_CLIS`.
- `integrations/opencode_cli.py`: comandos `/colab` e `/colab-mcp`.
- `.opencode/skills/colab-cli/SKILL.md` + `.opencode/skills/colab-mcp/SKILL.md`.
- `tests/test_r645_colab_cli.py` (unit, mocks) + `tests/test_r645_colab_mcp.py`.
- Ciclo de evolução R645 (EvolutionRegistry).

## Critérios de aceitação

1. `colab_cli.colab_available()` usa `shutil.which("colab")` (tolerante).
2. `colab_version()` retorna semver via `colab version` (regex semver);
   `None` se ausente/falha.
3. `colab_run_args(args, timeout)` monta `["colab"] + args` em lista, nunca
   shell; captura stdout/stderr/returncode; nunca lança exceção; timeout vira
   `ok: False, timeout: True`.
4. Atalhos `colab_new/session/exec/run/stop` delegam ao runner genérico.
5. `doctor_check()` em ambos: `pass` se presente, `warn` se ausente (NUNCA fail).
6. `install_instructions()` documenta `uv tool install` + `pip` + auth
   (`--auth oauth2|adc`) + aviso Linux/macOS + custo compute units.
7. `colab_mcp.mcp_config()` retorna dict stdio
   (`command: ["uvx", "colab-mcp"]` ou binário local) pronto para `opencode.json`.
8. `main()` em ambos: `status|run|doctor|install` + `--help`; `run` sem args
   → exit 2.
9. Gate TDD: `pytest tests/test_r645_colab_cli.py tests/test_r645_colab_mcp.py`
   → 100% verdes (mocks + stub subprocess real em `tmp_path`).
10. Doctor global continua 0 fail; `colab`/`colab-mcp` ausentes entram como warn.
11. `python3 -m integrations.opencode_cli --check` reproduzível com agentes
    `colab-cli`, `colab-mcp` e comandos `/colab`, `/colab-mcp`.
12. Ciclo R645 registrado com score e lições.

## Estratégia de validação

- Unit (mocks): binário ausente/presente; versão com prefixos
  (`"colab, version 0.3.1"` → `"0.3.1"`); comando montado exatamente;
  doctor pass/warn; exit codes 0/1/2.
- Integração stub: binário `colab`/`colab-mcp` fake executável em `tmp_path` +
  PATH sobreposto; subprocess real cobre sucesso.
- Auth sem credencial (`colab sessions` sem login) é `returncode != 0`
  esperado, não bug da integração.

## Decisões registradas

- Runner genérico `colab_run_args` em vez de amarrar cada subcomando: o CLI
  tem 20+ subcomandos; atalhos cobrem o fluxo 80/20 (`new/exec/run/stop`).
- MCP via `uvx colab-mcp` preferencial (sem instalar global); fallback para
  binário `colab-mcp` no PATH.
- Sem auto-instalação e sem auto-auth: instrução oficial + consentimento.
- Aviso explícito Windows não suportado (interop `codex` roda no lado Linux).
