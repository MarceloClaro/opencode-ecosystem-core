---
name: gjq-experimentos-quanticos
description: Executa E01–E18 no backend GJQ/Tiangong com simulação prévia, API key no ambiente, task ID, leitura de JSON e auditoria de counts. Use ao rodar hardware real; não exponha a chave, não crie conta de menor sem responsável e não trate uma execução como fidelidade de estado.
metadata:
  version: "1"
  origem: "R1099 — integração GJQ do livro Do Bit ao Todo"
---

# Experimentos GJQ

## Pré-requisitos

1. Conta e API key na Tiangong (ou conta do responsável).
2. `GJQ_API_KEY` exportada no ambiente.
3. `gjq-client` instalado.
4. Script `08_experimentos_18.py`.
5. JSON simulado do experimento.

## Fluxo

```bash
export GJQ_API_KEY="sua-chave"
cd educacao_quantica_bohm/laboratorio_leitor
python 08_experimentos_18.py --sim --only E09
python 08_experimentos_18.py --real --backend Guoji08 --only E09
```

## MCP

Use `gjq_status`, `gjq_prepare`, `gjq_sim`, `gjq_run`, `gjq_result`, `gjq_audit`.
`gjq_run` exige `confirm=True`; sem chave ou simulação, retorna blocked.

## Auditoria

- backend;
- shots;
- task IDs;
- timestamp;
- soma dos counts;
- `sobreposicao` (não é fidelidade).

## Limites

Uma execução não é prova estatística. Não declare emaranhamento, fidelidade,
vantagem quântica ou interpretação de Bohm a partir de um count.
