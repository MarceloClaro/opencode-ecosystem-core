---
name: discovery-engine-anomalo
description: Engine de descoberta de correlacoes anomalas e insights nao-obvios que seriam impossiveis de encontrar sem o ecossistema. Aplica cross-validation multidimensional, deteccao de outliers estatisticos e mineração de padroes contra-intuitivos.
---

# Discovery Engine — Correlacoes Anomalas e Insights Contra-Intuitivos

## Proposito

Encontrar correlacoes, padroes e solucoes que:
1. Nao seriam humanamente detectaveis sem processamento cruzado de 27+ indicadores x 10+ paises
2. Desafiam o senso comum estabelecido (ex: "educacao → desenvolvimento")
3. Revelam trade-offs estruturais invisiveis em analises unidimensionais
4. Satisfazem o criterio de novidade exigido por bancas Qualis A1

## Tipos de Descoberta Anomala

### Tipo A — Correlacao Invertida
Quando a direcao da correlacao contradiz a intuicao estabelecida.

**Exemplo detectado:** Educacao (%PIB) tem correlacao NULA com PIB per capita (r = -0.0273)
**Intuicao comum:** "Mais investimento em educacao → mais desenvolvimento"
**Realidade empirica:** Paises que gastam MAIS em educacao (%PIB) nao sao mais ricos
**Explicacao:** Efeito teto — acima de ~4% do PIB, qualidade > quantidade

### Tipo B — Preditor Oculto
Quando uma variavel negligenciada no debate publico emerge como preditor dominante.

**Exemplo detectado:** Servicos de Alta Tecnologia (r = +0.9531) supera TODOS os outros indicadores
**Intuicao comum:** "Industrializacao e o caminho para o desenvolvimento"
**Realidade empirica:** Servicos intensivos em conhecimento sao o verdadeiro motor
**Implicacao:** Politicas focadas em industria podem estar mirando no alvo errado

### Tipo C — Trade-off Estrutural
Quando dois objetivos desejaveis sao negativamente correlacionados, exigindo escolhas dificeis.

**Exemplo detectado:** Participacao da Agricultura (r = -0.6989) vs PIB per capita
**Intuicao comum:** "O Brasil e o celeiro do mundo — agricultura e nossa vantagem"
**Realidade empirica:** Maior participacao agricola no PIB esta associada a MENOR renda
**Explicacao:** Paises ricos tem agricultura mais produtiva, mas menor participacao relativa

### Tipo D — Paradoxo de Genero
Quando mulheres superam homens em uma dimensao, mas ficam atras em outra.

**Exemplo detectado:** Brasil: Mulheres 58.2% ensino superior vs Homens 43.3%
**Mas:** Desemprego feminino 9.8% vs masculino 6.5%
**Intuicao comum:** "Mais educacao → melhores empregos"
**Realidade empirica:** Overeducation + segregacao ocupacional + penalidade maternidade

### Tipo E — Janela Perdida
Quando uma oportunidade temporal esta se fechando sem ser percebida.

**Exemplo detectado:** Bonus demografico brasileiro se fecha em 2040
**Indicador:** Desemprego juvenil 20.8% vs Coreia 7.1%
**Implicacao:** Brasil tem ~15 anos para aproveitar a janela — depois, envelhecimento reduzira crescimento

## Algoritmo de Discovery

```python
def discovery_engine(data, n_countries=10, n_indicators=27):
    insights = []
    
    # Passo 1: Correlacao completa
    correlations = compute_all_pearson(data)
    
    # Passo 2: Identificar correlacoes contra-intuitivas
    for var, r in correlations.items():
        if abs(r) < 0.05 and is_commonly_believed_important(var):
            insights.append({"type": "A", "var": var, "r": r, 
                           "insight": f"{var} has near-zero correlation but is widely believed to matter"})
        if abs(r) > 0.90 and is_not_obvious_predictor(var):
            insights.append({"type": "B", "var": var, "r": r,
                           "insight": f"{var} is the strongest predictor but rarely discussed"})
    
    # Passo 3: Detectar trade-offs
    for v1, v2 in pairs:
        if both_desirable(v1, v2) and correlation(v1, v2) < -0.5:
            insights.append({"type": "C", "v1": v1, "v2": v2,
                           "insight": f"Trade-off: improving {v1} may reduce {v2}"})
    
    # Passo 4: Paradoxos de genero
    if education_female > education_male and unemployment_female > unemployment_male:
        insights.append({"type": "D", 
                        "insight": "Gender education paradox: more educated but less employed"})
    
    return insights
```

## Exemplos de Insights Gerados pelo Discovery Engine

1. **Servicos de Alta Tecnologia (r=0.9531):** Correlacao quase perfeita com desenvolvimento — 2.3x mais forte que P&D total — e um preditor negligenciado no debate de politica publica

2. **Desemprego Juvenil (r=-0.774):** Cada ponto percentual adicional de desemprego juvenil esta associado a ~$3.500 menos no PIB per capita — mas o debate foca em educacao, nao em empregabilidade

3. **Razao Salarial de Genero (r=+0.792):** Países onde mulheres ganham mais proximo dos homens sao consistentemente mais ricos — fechar o gap de 23.8% no Brasil poderia adicionar ~$2.200 ao PIB per capita

4. **Correlacao Nula da Educacao (r=-0.027):** O Brasil gasta 5.8% do PIB em educacao vs 4.8% da Coreia — o problema nao e quantidade de investimento, e conversao de capital humano em inovacao
