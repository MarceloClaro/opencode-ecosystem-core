---
id: colab-cli
name: colab-cli
description: >-
  Executor externo orquestrável: `colab` (googlecolab/google-colab-cli,
  Apache-2.0). Provisiona runtimes CPU/GPU/TPU, executa código e jobs
  efêmeros, gerencia arquivos do Colab via terminal.
type: integration
round: R645
spec: SPEC-935-R645-colab-cli-mcp.md
trust: 0.9
---

# colab-cli — Google Colab CLI (terminal/headless)

Executor externo orquestrável: `colab` (pacote `google-colab-cli`,
repositório `googlecolab/google-colab-cli`, fork
`MarceloClaro/google-colab-cli`). Roda localmente, chama a API Colab
(auth própria `oauth2|adc`).

## Capacidades

- `colab_available()` / `colab_version()` — presença e versão semântica.
- `colab_run_args(args, timeout, stdin_text)` — passthrough genérico em lista,
  sem shell, nunca lança (timeout vira `timeout: True`).
- Atalhos `colab_new | colab_exec | colab_run_script | colab_stop | colab_sessions`.
- `doctor_check()` — pass se instalado, warn se ausente (nunca fail).
- `install_instructions()` — uv/pip + auth + aviso Linux/macOS + compute units.
- CLI `/colab status|run|new|exec|stop|sessions|doctor|install`.

## Limites (anti-overclaim R110)

- Execução externa: resultados NÃO são "verificados" sem validação do Core.
- Linux/macOS apenas; Windows não suportado.
- Sem login, falhas de auth são esperadas.
- GPU/TPU e `--high-mem` exigem Pro/Pro+ e consomem compute units.
