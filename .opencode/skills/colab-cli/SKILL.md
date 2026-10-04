---
name: colab-cli
description: >-
  Integração do Google Colab CLI como executor externo orquestrável
  (SPEC-935-R645). Use para provisionar runtimes CPU/GPU/TPU no Colab
  (colab new/sessions/status), executar código (colab exec/run/repl),
  gerenciar arquivos (ls/upload/download) e jobs efêmeros
  (colab run --gpu T4 script.py). NÃO instala nem autentica sozinho;
  exige consentimento. Linux/macOS apenas; GPU/TPU consomem compute units.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R645
spec: SPEC-935-R645-colab-cli-mcp.md
---

# Skill: Colab CLI (SPEC-935-R645)

Executor externo orquestrável. O orquestrador deve ler este SKILL.md e executar
as instruções no contexto atual (padrão continuidade de pipelines).

## Comandos

| Comando | Ação |
|---|---|
| `/colab status` | JSON com presença, versão, plataforma e origem |
| `/colab run [--timeout SEG] [--input TEXTO] <args do colab...>` | Passthrough genérico (`sessions`, `status -s N`, `exec -f t.py`, ...) |
| `/colab new <nome> [--gpu T4\|L4\|A100] [--tpu v5e1] [--high-mem]` | Atalho `colab new` |
| `/colab exec [-s NOME] [-f ARQ] [--input TEXTO]` | Atalho `colab exec` (stdin via `--input`) |
| `/colab stop [-s NOME]` \| `/colab sessions` | Encerra / lista sessões |
| `/colab doctor` | Saúde (pass/warn, nunca fail) |
| `/colab install` | Instruções uv/pip + auth + custos |

## Uso programático

```python
from integrations.colab_cli import colab_new, colab_exec, colab_run_script, colab_stop

n = colab_new("trainer", gpu="T4")                 # {"ok", "stdout", ...}
e = colab_exec(session="trainer", file="train.py")
j = colab_run_script("train.py", script_args=["--epochs", "2"], gpu="T4")
s = colab_stop("trainer")
```

## Autenticação e custos

```bash
uv tool install google-colab-cli   # ou: pip install google-colab-cli
colab auth [-s NOME]               # GCP (BigQuery, GCS)
colab drivemount [-s NOME]         # Drive em /content/drive
colab usage                        # compute units; colab pay gerencia assinatura
```

## Regras

- Linux/macOS apenas — Windows NÃO suportado (rode no lado Linux).
- Nunca declarar resultado como "verificado" sem validação do Core (R110).
- Sem login, `sessions/status` falha com auth — esperado, não é bug.
- GPU/TPU e `--high-mem` exigem Colab Pro/Pro+; prefira T4 nos testes.
