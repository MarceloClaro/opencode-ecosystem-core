---
id: antigravity-cli
name: antigravity-cli
description: >-
  Runner direto do Antigravity CLI `agy` (google-antigravity, oficial):
  status/version/run/doctor no padrão M7, com detecção de falha silenciosa.
  Complementa bridge + MCP + executor (não substitui).
type: integration
round: R651
spec: SPEC-935-R651-antigravity-cli-runner.md
trust: 0.9
---

# antigravity-cli — runner direto (complemento)

`integrations/antigravity_cli.py`: forma canônica
`--agent/--print/--output-format`, stdin DEVNULL, inspeção de `CLI error:`.
Para análise com revisão, usar o executor `antigravity` (R621).
