# SPEC-935-R506 — Executable Code IMO Benchmark

## Status
**APPROVED** — 2026-09-15

## Objetivo
Avaliar LLMs gratuitos pela capacidade de gerar **código Python executável** que resolve problemas da IMO, executando-o em sandbox seguro e comparando a saída com a resposta esperada.

## Diferença do R503
- **R503 (texto)**: LLM gera texto → regex extrai resposta → compara
- **R506 (código)**: LLM gera código Python → executa em sandbox → captura stdout → compara

## Requisitos funcionais

### REQ-01: Prompt de código
- O prompt instrui o modelo a gerar um script Python completo
- O script deve: (a) resolver o problema, (b) imprimir a resposta final
- Formato: bloco ` ```python ` markdown

### REQ-02: Extração de código
- Parser extrai o primeiro bloco ` ```python ... ``` ` do response
- Se não houver bloco, tenta extrair código que comece com `import` ou `def`
- Se nada for encontrado, marca como `code_missing`

### REQ-03: Sandbox de execução
- Executa o código em subprocess com timeout configurável (padrão 30s)
- Sem acesso a rede (`--network=none` se disponível)
- Sem acesso a arquivos além do `/tmp`
- Captura stdout e stderr separadamente

### REQ-04: Validação de output
- Compara `stdout.strip()` com resposta esperada
- Normalização: remove espaços, case-insensitive para strings
- Tipos numéricos: comparação numérica (não só string)

### REQ-05: Classificação de resultado
- `correct`: stdout matches expected
- `wrong_answer`: stdout diferente de expected
- `runtime_error`: código dá exceção
- `timeout`: execução excede timeout
- `code_missing`: nenhum código extraído
- `no_output`: código roda mas não imprime nada

## Requisitos não-funcionais
- Reprodutível: mesmos inputs → mesmos outputs
- Auditável: código fonte salvo em JSON
- Seguro: subprocess isolado, timeout, sem rede

## Dados de saída
```json
{
  "problem": "imo-bench-number-theory-002",
  "model": "opencode/mimo-v2.5-free",
  "expected": "{3}",
  "code": "import sympy\n...",
  "stdout": "3\n",
  "stderr": "",
  "status": "correct",
  "elapsed_s": 4.2,
  "exit_code": 0
}
```

## Critérios de aceitação
1. Todos os 9 problemas têm código gerado por pelo menos 1 modelo
2. Sandbox bloqueia código malicioso (timeout, sem rede)
3. Pelo menos 1 teste verifica `runtime_error` corretamente
4. Pelo menos 1 teste verifica `timeout` corretamente
5. Estatísticas completas: acurácia, IC, McNemar, kappa, latência