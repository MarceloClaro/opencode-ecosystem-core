---
name: gemini-cli
description: >
  Integração da CLI Gemini (Google) como executor externo orquestrável
  (SPEC-935-R600). Use para delegar tarefas ao Gemini CLI em modo headless
  (`gemini -p`) com saída JSON estruturada, consultar versão, checar saúde
  (`/gemini doctor`), obter instruções de instalação (`/gemini install`) ou
  rodar prompts com modelo específico (`--model`/`-m`) e formatos
  (`--output-format json|stream-json`). NÃO é o motor de qualidade do Core:
  o orquestrador marceloclaro permanece dono do ciclo SDD/TDD e resultados do
  Gemini nunca são declarados verificados sem validação (anti-overclaim R110).
  Exige autenticação: `GEMINI_API_KEY` (aistudio.google.com/apikey) ou Vertex
  AI (`GOOGLE_API_KEY` + `GOOGLE_GENAI_USE_VERTEXAI=true`).
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R600
spec: SPEC-935-R600-gemini-cli.md
---

# Skill: Gemini CLI (SPEC-935-R600)

Executor externo orquestrável. O orquestrador deve ler este SKILL.md e executar
as instruções no contexto atual (padrão continuidade de pipelines).

## Comandos

| Comando | Ação |
|---|---|
| `/gemini status` | JSON com presença, binário e versão semântica |
| `/gemini run '<tarefa>' [--model MODELO] [--output-format json\|stream-json] [--timeout SEG]` | Executa Gemini headless `-p` |
| `/gemini doctor` | Checagem de saúde (pass/warn, nunca fail) |
| `/gemini install` | Instruções npm/npx/Homebrew + variáveis de auth |
| `/gemini --help` | Uso completo |

## Uso programático

```python
from integrations.gemini_cli import gemini_run, gemini_version, doctor_check

r = gemini_run("explique o arquivo", model="gemini-2.5-flash", output_format="json")
print(r["ok"], r["stdout"])
```

## Autenticação

```bash
export GEMINI_API_KEY="sua_chave"        # aistudio.google.com/apikey (free tier)
# ou Vertex AI:
export GOOGLE_API_KEY="sua_chave"
export GOOGLE_GENAI_USE_VERTEXAI=true
```

## Regras

- Nunca declarar resultado do Gemini como "verificado" sem validação do Core.
- Sem API key, `run` falha por auth (returncode != 0) — comportamento esperado,
  não é bug da integração.
- Sem Node.js/npm, instalação não é possível (doctor mostra warn).