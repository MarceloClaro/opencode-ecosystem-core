---
name: kaggle-cli
description: >-
  Integração do Kaggle CLI como executor externo orquestrável
  (SPEC-935-R650). Use para competições, datasets, kernels, models, forums,
  benchmarks, config, auth e quota via passthrough (kaggle run ...).
  Exige kaggle.json do operador; downloads/quota consomem a conta.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R650
spec: SPEC-935-R650-kaggle-cli.md
---

# Skill: Kaggle CLI (SPEC-935-R650)

## Comandos

| Comando | Ação |
|---|---|
| `/kaggle status` | Versão + estado da credencial (sem rede) |
| `/kaggle run [--timeout SEG] <args...>` | Passthrough (`competitions list`, `datasets download`, `quota`…) |
| `/kaggle auth` | `{"present", "path"}` da credencial |
| `/kaggle doctor` / `/kaggle install` | Saúde / `pip install kaggle` + token |

## Autenticação

kaggle.com → Settings → Account → API token → `~/.kaggle/kaggle.json`
(`chmod 600`). Verificar: `kaggle competitions list --page-size 2`
(provado ao vivo: ARC Prize 2026 listado).

## Regras

- Doctor nunca sonda a API (só filesystem).
- Nunca declarar resultados como verificados sem validação (R110).
