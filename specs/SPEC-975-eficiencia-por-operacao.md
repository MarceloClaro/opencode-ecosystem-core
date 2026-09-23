# SPEC-975 — Instrumentação de Eficiência por Operação (R582)

**Status:** Aprovado (gate SDD aplicado)
**Ciclos de referência:** R581 (426) — frentes SPEC-974; decisão do usuário de medir
**Responsável:** orquestrador `marceloclaro`

## 1. Contexto

O usuário perguntou se o ecossistema ficou mais eficiente. A resposta foi medida
ponto-a-ponto, mas sem linha de base contínua. Para que a próxima sessão responda
com número auditado (não estimativa), instrumentamos o custo real de cada
operação automatizada (hooks + MCP).

## 2. Entregas e critérios de aceitação

| ID | Entrega | Critério |
|---|---|---|
| E1 | `integrations/op_timing.py` (recorder append-only + relatório) | grava `.mci_state/op_times.jsonl` (op, seconds, ok, round_id, ts); `report` imprime mediana/p90 por op |
| E2 | Hooks instrumentados | `js_smoke_dom.sh`/`budget_guard.sh`/`credential_guard.sh` registram tempo + ok via trap EXIT (OP_TIMING=1 default) |
| E3 | MCP instrumentado | `call_tool` do web-deploy-mcp registra duração + isError de cada tool |
| E4 | Comando `/efficiency` | `python3 -m integrations.op_timing report` exposto no opencode.json |
| E5 | Testes | `tests/test_r582_op_timing.py`: record+report com OP_TIMES_PATH temp (mediana/p90 corretos; append-only) |
| E6 | Linha de base | registrar medições da sessão atual (guards + provas) como baseline R582 |

## 3. Regras

- Jamais sobrescrever o JSONL (append-only).
- Falha na medição NUNCA quebra a operação medida (best-effort; try/except).
- `OP_TIMES_PATH` injetável para testes; `OP_ROUND_ID` para nomear o ciclo.
- Relatório em PT-BR formal, ms, com n e p90.