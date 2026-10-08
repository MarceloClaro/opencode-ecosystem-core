# Template - Plano de Inferencia Avancada

## Cabecalho

```md
# Plano de Inferencia Avancada

[Projeto]
[Versao]
[Data]
[Responsavel principal]
[Revisor cruzado]
[Tipo de estudo]
```

## Bloco 1 - Perguntas, estimandos e unidade analitica

```md
| ID | Pergunta/hipotese | Estimando alvo | Unidade analitica | Janela temporal | Observacao |
|---|---|---|---|---|---|
| I01 | H1 | Efeito medio ajustado | Participante | baseline -> follow-up | Inferencia causal observacional |
```

## Bloco 2 - Estrutura estatistica

```md
| ID | Tipo de dado | Dependencia | Modelo/teste principal | Alternativa robusta | Justificativa |
|---|---|---|---|---|---|
| I01 | Binario | Cluster por escola | GLMM logit | GEE robusto | Dependencia hierarquica |
```

## Bloco 3 - Pressupostos e diagnosticos

```md
| ID | Pressuposto/diagnostico | Como sera verificado | Limiar/criterio | Acao se falhar |
|---|---|---|---|---|
| D01 | Multicolinearidade | VIF | < 5 | Revisar variaveis ou regularizacao |
```

## Bloco 4 - Missing, sensibilidade e incerteza

```md
### Missing data
- mecanismo presumido:
- estrategia principal:
- estrategia de sensibilidade:

### Incerteza
- intervalos:
- bootstrap/MCMC:
- ajuste multiplicidade:

### Sensibilidade
- ...
```

## Bloco 5 - Regras interpretativas

```md
### O que pode ser afirmado
- ...

### O que nao pode ser afirmado
- ...

### Linguagem obrigatoria de cautela
- ...
```
