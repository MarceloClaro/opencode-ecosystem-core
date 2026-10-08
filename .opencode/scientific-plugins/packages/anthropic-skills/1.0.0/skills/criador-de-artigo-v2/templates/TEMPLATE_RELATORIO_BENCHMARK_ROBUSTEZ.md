# Template - Relatorio de Benchmark e Robustez

## Cabecalho

```md
# Relatorio de Benchmark e Robustez

[Projeto]
[Versao]
[Data]
[Responsavel principal]
[Revisor cruzado]
```

## Comparacao principal

```md
| Modelo/abordagem | Tipo | Baseline? | Metrica principal | IC/variacao | Sensibilidade a seed | Custo computacional | Comentario |
|---|---|---|---|---|---|---|---|
| Regressao logistica | Classico | Sim | AUROC 0.79 | +-0.01 | Baixa | Baixo | Baseline forte |
| Modelo profundo X | Deep learning | Nao | AUROC 0.83 | +-0.03 | Media | Alto | Ganho modesto |
```

## Robustez

```md
### Ablacoes
- ...

### Analise de sensibilidade
- ...

### Fairness / slices / subgrupos
- ...

### Leakage checks
- ...

### Shift de dominio
- ...

### Analise de erro
- ...

### Criticidade do ganho
- ganho absoluto:
- ganho relativo:
- ganho estatisticamente/operacionalmente relevante?:

### Condicao de stop-the-line
- ...
```
