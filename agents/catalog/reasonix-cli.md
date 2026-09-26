---
id: reasonix-cli
name: reasonix-cli
type: integration
round: R602
spec: SPEC-935-R602-reasonix.md
trust: 0.9
---

# reasonix-cli — Integração Reasonix (DeepSeek-Reasonix)

Executor externo orquestrável: `reasonix` (`esengine/DeepSeek-Reasonix`, MIT).
Agente de codificação DeepSeek-native; linha ativa é o rewrite Go (v2,
instalável via `npm install -g reasonix`; alias `dsnix`).

## Capacidades

- `reasonix_available()` / `reasonix_version()` — presença e versão semântica.
- `reasonix_run(task, directory, timeout)` — one-shot `reasonix run "<tarefa>"`
  (streams para stdout, bom para pipes), sem shell (lista), nunca lança.
- `doctor_check()` — pass se binário + `reasonix doctor` exit 0, warn caso
  contrário (ex.: sem DeepSeek API key).
- `install_instructions()` — npm/npx + DeepSeek API key (+ `reasonix setup`).
- CLI `/reasonix status|run|doctor|install|setup` com `--timeout` e `--help`.

## Limites (anti-overclaim R110)

- Execução externa: resultados NÃO são "verificados" sem validação do Core.
- Sem DeepSeek API key (`platform.deepseek.com/api_keys`) o `run` falha por
  auth — comportamento esperado, documentado.
- O TUI interativo (`reasonix` puro) fica fora da orquestração (limitação de
  infraestrutura — lição R601); orquestramos `run` e `doctor`.
- `--dir` existe no upstream para retarget de pasta; não exposto como flag na
  camada orquestrada nesta ronda (posição de flag varia entre v0.x/v2).