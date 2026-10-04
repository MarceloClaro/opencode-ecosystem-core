---
id: kaggle-cli
name: kaggle-cli
description: >-
  Executor externo orquestrável: `kaggle` (Kaggle/kaggle-cli) — competições,
  datasets, kernels, models, quota via passthrough com auth do operador.
type: integration
round: R650
spec: SPEC-935-R650-kaggle-cli.md
trust: 0.9
---

# kaggle-cli — Kaggle CLI (passthrough)

`integrations/kaggle_cli.py`: presença/versão, `kaggle_run_args` em lista,
`auth_check()` sem rede, doctor tolerante. Credencial `~/.kaggle/kaggle.json`.
