---
name: reasonix-cli
description: >
  Integração da CLI Reasonix (esengine/DeepSeek-Reasonix, MIT) como executor
  externo orquestrável (SPEC-935-R602). Use para delegar tarefas one-shot ao
  Reasonix em modo pipes (`reasonix run "tarefa"`), checar saúde (`/reasonix
  doctor`), consultar versão/status, obter instruções de instalação e chave
  DeepSeek (`/reasonix install`, `/reasonix setup`). NÃO é o motor de qualidade
  do Core: o orquestrador marceloclaro permanece dono do ciclo SDD/TDD e
  resultados do Reasonix nunca são declarados verificados sem validação
  (anti-overclaim R110). Exige DeepSeek API key
  (platform.deepseek.com/api_keys), persistida por `reasonix setup`.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R602
spec: SPEC-935-R602-reasonix.md
---

# Skill: Reasonix CLI (SPEC-935-R602)

Executor externo orquestrável. O orquestrador deve ler este SKILL.md e executar
as instruções no contexto atual (padrão continuidade de pipelines).

## Comandos

| Comando | Ação |
|---|---|
| `/reasonix status` | Binário, versão semântica e disponibilidade |
| `/reasonix run '<tarefa>' [--timeout SEG]` | One-shot `reasonix run "<tarefa>"` (pipes) |
| `/reasonix doctor` | Health check (Node, API key, MCP wiring) — pass/warn |
| `/reasonix install` | Instruções npm/npx + DeepSeek API key |
| `/reasonix setup` | Instruções de configuração (provider/modelo) |
| `/reasonix --help` | Uso completo |

## Uso programático

```python
from integrations.reasonix_cli import reasonix_run, reasonix_version, doctor_check

r = reasonix_run("implemente os TODOs do main.py")
print(r["ok"], r["returncode"], r["stdout"])
```

## Autenticação

```bash
npm install -g reasonix   # binário nativo Go (v2) + alias dsnix
reasonix setup            # colar a DeepSeek API key (persistida)
# key: https://platform.deepseek.com/api_keys
```

## Regras

- Nunca declarar resultado do Reasonix como "verificado" sem validação do Core.
- Sem API key, `run` falha por auth (returncode != 0) — comportamento esperado,
  não é bug da integração.
- O TUI interativo (`reasonix` puro) é manual; a orquestração usa `run`/`doctor`.