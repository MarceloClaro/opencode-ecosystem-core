---
name: auditoria-experimentos-quanticos
description: Audita counts, task IDs, incerteza, sobreposição e limites de experimentos quânticos de simulação e hardware. Use ao validar E01–E18, ler JSON/CSV ou comparar backend; não trate sobreposição como fidelidade de estado nem uma execução como prova estatística.
metadata:
  version: "1"
  origem: "R1099 — ledger e pilotos do livro Do Bit ao Todo"
---

# Auditoria de experimentos quânticos

## Entrada

- JSON em `educacao_quantica_bohm/dados_experimentos/E*.json`.
- Counts, backend, shots, task IDs e timestamp.
- Ledger em `livro_pixel/LEDGER_AFIRMACOES.md`.

## Verificações

1. **Soma:** `Σ counts = shots`.
2. **Probabilidade:** `p = count / total`.
3. **Erro padrão:** `EP = sqrt(p(1-p)/N)`.
4. **Sobreposição:** `Σ min(p_sim, p_real)`; não é fidelidade.
5. **Task ID:** existe, backend coincide, data registrada.
6. **Limite:** o que o número não prova.

## Ferramentas

```bash
.venv/bin/python - <<'PY'
from integrations.livro_quantico_mcp import audit_counts
print(audit_counts({"0": 530, "1": 494}, 1024))
PY
```

## Critério de passagem

- Nenhum alerta de soma.
- Task ID e backend registrados.
- Conta reproduzida à mão.
- Limite escrito em uma frase.

## Limites

Auditar não é aprovar. Um count correto não prova emaranhamento, fidelidade,
vantagem quântica ou interpretação de Bohm.
