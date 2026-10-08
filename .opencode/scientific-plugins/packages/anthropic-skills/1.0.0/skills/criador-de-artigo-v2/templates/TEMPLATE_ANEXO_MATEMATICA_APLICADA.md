# Template - Anexo de Matematica Aplicada

## Cabecalho

```md
# Anexo de Matematica Aplicada

[Projeto]
[Versao]
[Data]
[Responsavel principal]
[Revisor cruzado]
```

## Bloco 1 - Inventario formal

```md
| ID | Modelo/formula | Objetivo | Dominio | Variaveis centrais | Implementacao associada |
|---|---|---|---|---|---|
| M01 | Sistema diferencial X | Descrever dinamica Y | t >= 0 | x(t), y(t), alpha | script_modelo_x.py |
```

## Bloco 2 - Simbolos e unidades

```md
| Simbolo | Nome | Unidade | Dominio | Interpretacao |
|---|---|---|---|---|
| alpha | taxa de crescimento | 1/dia | alpha > 0 | velocidade de crescimento |
```

## Bloco 3 - Hipoteses e derivacao

```md
### Hipoteses estruturais
- ...

### Passos de derivacao
1. ...
2. ...
3. ...
```

## Bloco 4 - Numerica e estabilidade

```md
| ID | Solver/aproximacao | Parametros numericos | Criterio de convergencia | Risco |
|---|---|---|---|---|
| N01 | Runge-Kutta 4 | dt = 0.01 | erro < 1e-6 | Medio |
```

## Bloco 5 - Limites de aplicacao

```md
### Onde o modelo vale
- ...

### Onde o modelo falha
- ...

### Impacto sobre o artigo
- ...
```
