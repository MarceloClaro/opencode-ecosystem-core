# Template - Validacao Analitica

## Finalidade

Este arquivo documenta a validacao tecnica do plano de analise, dos testes aplicados, dos pressupostos, dos reportes numericos e dos limites inferenciais.

## Cabecalho

```md
# Validacao Analitica

[Projeto]
[Versao avaliada]
[Data]
[Responsavel principal]
[Revisor cruzado]
```

## Bloco 1 - Compatibilidade entre pergunta e metodo

```md
| Hipotese/objetivo | Tipo de dado | Analise proposta | Analise adequada? | Observacao |
|---|---|---|---|---|
| H1 | Contínuo | t de Student | Sim | Dados e comparacao compatveis |
| H2 | Categórico | Regressao linear | Nao | Trocar por regressao logistica ou outro modelo adequado |
```

## Bloco 2 - Pressupostos

```md
| Analise | Pressuposto | Verificacao | Status | Impacto | Acao |
|---|---|---|---|---|---|
| ANOVA | Homogeneidade | Levene | OK | - | - |
| Regressao | Multicolinearidade | VIF | PENDENTE | Risco medio | Verificar antes do reporte final |
```

## Bloco 3 - Reporte dos resultados

```md
| Resultado | Estatistica | gl | p | IC95% | Efeito | Reporte completo? | Problema |
|---|---|---|---|---|---|---|---|
| R1 | t = 3,21 | 48 | 0,002 | [0,20; 0,66] | d = 0,91 | Sim | - |
| R2 | F = 5,11 | 2,45 | 0,011 | - | - | Nao | Falta IC e efeito |
```

## Bloco 4 - Limites inferenciais

```md
### Pontos de overclaim detectados
- ...

### Pontos em que a discussao excede o desenho
- ...

### Ajustes obrigatorios de linguagem
- ...
```

## Bloco 5 - Parecer tecnico

```md
[Status]
- APTO
- APTO COM RESSALVAS
- BLOQUEADO

[Razao principal]
- ...

[Correcoes obrigatorias]
- ...
```
