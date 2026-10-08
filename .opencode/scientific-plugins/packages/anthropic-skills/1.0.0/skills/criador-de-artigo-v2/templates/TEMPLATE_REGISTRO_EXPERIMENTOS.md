# Template - Registro de Experimentos

## Cabecalho

```md
# Registro de Experimentos

[Projeto]
[Versao]
[Data]
[Responsavel principal]
[Revisor cruzado]
```

## Tabela de runs

```md
| Run ID | Pipeline | Dataset/split | Seed | Configuracao | Metrica principal | Resultado | Status |
|---|---|---|---|---|---|---|---|
| R01 | baseline_lr | D01/train-val-test | 42 | C=1.0 | F1 | 0.81 | OK |
| R02 | transformer_x | D02/holdout | 123 | lr=2e-5; epochs=5 | Macro-F1 | 0.87 | OK |
```

## Bloco de anomalias

```md
### Falhas de execucao
- ...

### Runs descartadas
- ...

### Desvios em relacao ao plano
- ...
```
