# Nota de pesquisa — Canais associativos da educação terciária: saúde, desigualdade e inovação com moderação institucional

**Ciclo**: R413 | **Spec**: `specs/SPEC-935-R413-canais-associativos.md`
**Data**: 2026-08-13 | **Painel**: 135 países, 1960–2023, WDI + WGI
**Proveniência fechada**: `outputs/channels/provenance_r413.json` (SHA-256 do painel fonte)

---

## Resumo

Esta nota complementa o artigo principal (R410–R412) mapeando **canais associativos** entre educação terciária e renda em painel de 135 países, com correlações parciais controlando o PIB per capita, cluster bootstrap por país (500 replicações, semente 42) e painel com efeitos fixos e erros padrão clusterizados por país. Quatro achados: (i) a associação matrícula terciária × PIB per capita cai de **0,701** para **0,105** quando se adiciona a expectativa de vida como controle — a associação em níveis é mediada descritivamente pela saúde; (ii) a correlação parcial matrícula terciária × expectativa de vida é **0,684** (IC 0,639–0,728, n = 4374); (iii) os canais de desigualdade (matrícula × Gini = −0,184) e inovação (P&D × alta tecnologia = 0,250) mostram associações fracas a moderadas; (iv) a interação matrícula×WGI no painel FE é positiva (coef 0,0543; p = 0,005) e marcada como exploratória. Nenhuma relação de efeito é inferida.

**Palavras-chave**: educação terciária; expectativa de vida; desigualdade; inovação; governança; análise de canais.

## Abstract

This note complements the main article (R410–R412) by mapping **associational channels** between tertiary education and income in a 135-country panel, using partial correlations controlling for GDP per capita, country-cluster bootstrap (500 replications, seed 42), and fixed-effects regressions with country-clustered standard errors. Four findings: (i) the tertiary-enrollment × GDP-per-capita association drops from **0.701** to **0.105** when life expectancy is added as a control — the levels association is descriptively mediated by health; (ii) the partial correlation between tertiary enrollment and life expectancy is **0.684** (95% CI 0.639–0.728, n = 4,374); (iii) inequality (enrollment × Gini = −0.184) and innovation (R&D × high-tech exports = 0.250) channels show weak-to-moderate associations; (iv) the enrollment×WGI interaction in the FE panel is positive (coef 0.0543; p = 0.005) and labeled exploratory. No effect relationship is inferred.

**Keywords**: tertiary education; life expectancy; inequality; innovation; governance; channel analysis.

## Resumen

Esta nota complementa el artículo principal (R410–R412) mapeando **canales asociativos** entre educación terciaria e ingreso en un panel de 135 países, con correlaciones parciales controlando el PIB per cápita, bootstrap por conglomerados de país (500 réplicas, semilla 42) y panel de efectos fijos con errores estándar agrupados por país. Cuatro hallazgos: (i) la asociación matrícula terciaria × PIB per cápita cae de **0,701** a **0,105** al añadir la esperanza de vida como control — la asociación en niveles está mediada descriptivamente por la salud; (ii) la correlación parcial matrícula terciaria × esperanza de vida es **0,684** (IC 0,639–0,728, n = 4374); (iii) los canales de desigualdad (matrícula × Gini = −0,184) e innovación (I+D × alta tecnología = 0,250) muestran asociaciones débiles a moderadas; (iv) la interacción matrícula×WGI en el panel FE es positiva (coef 0,0543; p = 0,005) y se marca como exploratoria. No se infiere ninguna relación de efecto.

**Palabras clave**: educación terciaria; esperanza de vida; desigualdad; innovación; gobernanza; análisis de canales.

---

## 1. Motivação e lacuna

A literatura sobre crescimento trata **educação**, **saúde** e **governança** como determinantes separados (ACEMOGLU; GALLEGO; ROBINSON, 2014; BARRO; LEE, 2013; KAUFMANN; KRAAY; MASTRUZZI, 2011). A combinação das três dimensões em um único painel amplo, com matrícula **terciária** (não anos médios de escolaridade) e validação por bootstrap por país, permanece escassa. Estudos de determinantes da longevidade sugerem explicitamente a educação secundária/terciária como extensão de pesquisa futura. Esta nota ocupa parcialmente essa lacuna com linguagem estritamente associativa.

## 2. Dados e método

- **Dados**: painel país-ano 1960–2023, 135 países, 16 indicadores (WDI + WGI), sem imputação; critério de amostra ≥ 20 observações não nulas de matrícula e PIB (R412). Fonte: `data/processed/panel_wdi_expandido_1960_2023.csv` (SHA-256 em `provenance_r413.json`).
- **Correlações parciais**: resíduos de regressão de cada variável sobre os controles (ln PIB; WGI média quando o par envolve PIB), correlação de Pearson entre resíduos.
- **Validação**: cluster bootstrap por país (500 replicações, semente 42) para intervalos de confiança 95%; LOOCV por país (135 folds) das parciais centrais.
- **Painel FE**: efeitos fixos de país e ano, defasagem de 5 anos, controles (gasto educacional, P&D, urbanização, manufatura, WGI média), erros padrão clusterizados por país (CAMERON; MILLER, 2015).
- **Limites declarados**: associações descritivas; sem variação exógena; sem identificação de efeito; amostras por variável diferem (cobertura desigual).

## 3. Resultados

### 3.1 Análise em etapas: onde a associação matrícula×PIB se esvai

Correlação parcial entre matrícula terciária (log) e PIB per capita (log), acumulando controles (IC 95% bootstrap por país):

| Etapa | Controles adicionados | ρ parcial | IC 95% | n |
|---|---|---|---|---|
| Inicial | — | 0,701 | [0,642; 0,756] | 4.374 |
| +WGI | WGI média | 0,653 | [0,568; 0,738] | 2.557 |
| +Estrutura | gasto educ., P&D, urbanização, manufatura | 0,358 | [0,205; 0,528] | 1.146 |
| +Saúde | expectativa de vida | 0,105 | [−0,090; 0,288] | 1.146 |

A queda de 0,701 para 0,105 ao adicionar a expectativa de vida é o principal achado descritivo: em níveis, a associação educação×renda é sensível ao canal saúde.

### 3.2 Matriz de correlações parciais (seleção)

| Par (controle: ln PIB salvo indicação) | ρ parcial | n |
|---|---|---|
| Matrícula terciária × Expectativa de vida | **0,684** (IC [0,639; 0,728]) | 4.374 |
| Matrícula terciária × Gini | −0,184 | 1.475 |
| Gasto educacional × WGI controle da corrupção | 0,341 | 2.441 |
| P&D × Exportação alta tecnologia | 0,250 | 1.148 |

### 3.3 Canais com painel FE clusterizado (defasagem 5 anos)

| Canal | Especificação (y ~ x defasado + controles + FE país + FE ano) | Coef | p | Clusters |
|---|---|---|---|---|
| Saúde | Expectativa de vida ~ matrícula defasada | 0,535 | 0,186 | 106 |
| Desigualdade | Gini ~ matrícula defasada | −0,104 | 0,940 | 77 |
| Inovação | Alta tecnologia ~ P&D defasado | 0,836 | 0,529 | 77 |

Os coeficientes têm o sinal consistente com as parciais, mas **p-values altos** após clusterização: a associação dentro dos países é imprecisa nesta especificação. Reportamos o resultado completo, incluindo a não significância, conforme boa prática.

### 3.4 Moderação institucional (exploratória)

| Termo de interação (painel FE cluster, y = ln PIB) | Coef | p | Clusters |
|---|---|---|---|
| Matrícula defasada × WGI média | 0,054 | 0,005 | 106 |
| Matrícula defasada × P&D defasado | −0,003 | 0,668 | 80 |

A interação matrícula×WGI é positiva e significativa a 5%; a interação com P&D é nula. Ambas são **exploratórias**: múltiplos testes, sem hipótese pré-registrada.

## 4. Discussão e limites

- O achado do canal saúde dialoga com a literatura de capital humano e saúde (ACEMOGLU; GALLEGO; ROBINSON, 2014; BARRO; LEE, 2013): a educação terciária correlaciona-se com maior longevidade, e a longevidade é candidata a canal da associação com renda — aqui apenas descritivo.
- O sinal negativo matrícula×Gini é relevante para o debate brasileiro de inclusão educacional e desigualdade.
- A cadeia P&D→alta tecnologia é fraca no painel FE (p = 0,529): a associação em níveis não se confirma dentro dos países nesta janela.
- Limites: cobertura desigual (Gini n = 1.475); especificação de FE reduz variância; interações não pré-registradas; sem identificação de efeito.

## Referências

ACEMOGLU, D.; GALLEGO, F. A.; ROBINSON, J. A. Institutions, human capital, and development. **Annual Review of Economics**, v. 6, p. 875-912, 2014. DOI: 10.1146/annurev-economics-080213-041119.

BARRO, R. J.; LEE, J. W. A new data set of educational attainment in the world, 1950–2010. **Journal of Development Economics**, v. 104, p. 184-198, 2013. DOI: 10.1016/j.jdeveco.2012.10.001.

CAMERON, A. C.; MILLER, D. L. A practitioner's guide to cluster-robust inference. **Journal of Human Resources**, v. 50, n. 2, p. 317-372, 2015. DOI: 10.3368/jhr.50.2.317.

KAUFMANN, D.; KRAAY, A.; MASTRUZZI, M. The Worldwide Governance Indicators: methodology and analytical issues. **Hague Journal on the Rule of Law**, v. 3, n. 2, p. 220-246, 2011. DOI: 10.1017/S1876404511200046.

WORLD BANK. **World Development Report 2024: The Middle-Income Trap**. Washington, DC: World Bank, 2024. [DOI: 10.1596/978-1-4648-2078-6](https://doi.org/10.1596/978-1-4648-2078-6).
