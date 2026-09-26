---
id: gemini-cli
name: gemini-cli
type: integration
round: R600
spec: SPEC-935-R600-gemini-cli.md
trust: 0.9
---

# gemini-cli — Integração da CLI Gemini (Google)

Executor externo orquestrável: `gemini` (pacote `@google/gemini-cli`,
repositório `google-gemini/gemini-cli`). Roda localmente, chama a API Gemini
(key própria `GEMINI_API_KEY` ou Vertex AI).

## Capacidades

- `gemini_available()` / `gemini_version()` — presença e versão semântica.
- `gemini_run(prompt, model, output_format, timeout)` — headless `-p` com
  `--output-format json|stream-json`, sem shell (lista), nunca lança.
- `doctor_check()` — pass se instalado (com versão), warn se ausente.
- `install_instructions()` — npm/npx/Homebrew + variáveis de auth.
- CLI `/gemini status|run|doctor|install` com flags `-m/--model`,
  `--output-format`, `--timeout` e `--help`.

## Limites (anti-overclaim R110)

- Execução externa: resultados NÃO são "verificados" sem validação do Core.
- Sem `GEMINI_API_KEY` o `run` falha por auth — comportamento esperado.
- Depende de Node.js/`npm` (instalação) — ausência vira warn no doctor.