# SPEC-935-R600 — Integração da CLI Gemini (google-gemini/gemini-cli)

**Ronda:** R600
**Status:** implementado
**Data:** 2026-09-25
**Autor:** marceloclaro (orquestrador central)
**Padrão:** M7 — Executor externo orquestrável (espelho de R598/R599)

## Objetivo

Tornar a CLI oficial do Google Gemini (`gemini`, pacote `@google/gemini-cli`)
orquestrável pelo OpenCode Ecosystem Core com protocolo SDD/TDD, sem substituir
o orquestrador `marceloclaro` como dono do ciclo de qualidade.

O Gemini CLI é um agente de código da Google em TypeScript/Node que opera no
terminal, com modo não-interativo (`-p`) para scripts e JSON estruturado
(`--output-format json`). Roda localmente, mas chama a API Gemini (key própria
ou Vertex AI) — execução externa, resultado nunca é "verificado" sem validação
(anti-overclaim R110).

## Escopo

- `integrations/gemini_cli.py`: status, versão, run headless `-p`, doctor, install
  (npx/npm), CLI `main()` com flags reais.
- `agents/catalog/gemini-cli.md`: Agent Card A2A.
- `marceloclaro/doctor.py`: entrada `gemini` em `EXTERNAL_CLIS` + versão no detail.
- `integrations/opencode_cli.py`: comando `/gemini`.
- `.opencode/skills/gemini-cli/SKILL.md`: guia de uso.
- `tests/test_r600_gemini_cli.py` (unit, mocks) + stub de integração em
  `tests/test_r598_r599_external_stubs.py` (subprocess real).
- Ciclo de evolução R600 (EvolutionRegistry).

## Fonte de verdade (anti-overclaim)

README oficial do repositório `google-gemini/gemini-cli@main` (consultado em
2026-09-25):
- Instalação: `npm install -g @google/gemini-cli` (alternativas: npx, Homebrew,
  Anaconda; tags `@preview` e `@nightly`).
- Headless/scripts: `gemini -p "<prompt>"`; `--output-format json` para saída
  estruturada; `--output-format stream-json` para eventos NDJSON.
- Modelo: `-m gemini-2.5-flash` (ou `--model`).
- Autenticação: `GEMINI_API_KEY` (aistudio.google.com/apikey; free tier 1000
  req/dia com Gemini 3) ou Vertex AI (`GOOGLE_API_KEY` + `GOOGLE_GENAI_USE_VERTEXAI=true`).

## Critérios de aceitação

1. `gemini_cli.gemini_available()` usa `shutil.which("gemini")` (tolerante).
2. `gemini_version()` retorna apenas a versão semântica (regex semver) via
   `gemini --version`; `None` se ausente/falha.
3. `gemini_run(prompt, model=None, provider=None, output_format=None)` monta
   `gemini -p <prompt> [--model <model>] [--output-format <fmt>]`; usa listas,
   nunca shell; captura stdout/stderr/returncode; nunca lança exceção.
4. `doctor_check()`: `pass` se binário presente, `warn` se ausente (NUNCA fail).
5. `install_instructions()` documenta npm/npx/Homebrew e variáveis de auth.
6. `main()`: `status|run|doctor|install` + `--help`; `run` aceita
   `--model/-m`, `--output-format`, `--timeout`; prompt obrigatório → exit 2.
7. Gate TDD: unit mocks + integração stub (subprocess real em `tmp_path`).
8. Doctor global: `gemini` listado em `EXTERNAL_CLIS`; versão no detail quando
   instalado.
9. Comando `/gemini` presente no `opencode.json` regenerado.
10. Ciclo R600 registrado com score e lições.

## Estratégia de validação

- Unit (mocks): versão sem verbo binário (simula `--version` → semver); comando
  montado exatamente; doctor pass/warn; CLI main exit codes (0/1/2).
- Integração stub: binário `gemini` stub executável em `tmp_path` + PATH
  sobreposto; subprocess real cobre caminho de sucesso.
- Mensagem de erro de auth (API key ausente) em `run` real é tratada como
  `returncode != 0` — comportamento esperado, não falha da integração.

## Decisões registradas

- Não há binário npm padrão no `$PATH` em ambientes minimalistas; a integração
  é tolerante (warn no doctor, mensagem de instalação no `install`).
- Preferência por entry point simples: apenas `-p` no modo headless (mais
  estável que o modo interativo para orquestração).
- Gemini CLI não deve ser usado como motor de teste do Core (o orquestrador
  permanece o dono do ciclo SDD/TDD).