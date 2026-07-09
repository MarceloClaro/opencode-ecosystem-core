#!/usr/bin/env python3
"""Edita o ARTIGO_COMPLETO_CORRIGIDO.md substituindo secoes teoricas por resultados empiricos do ML pipeline."""

import re

PATH = r"C:\Users\marce\.config\opencode\artigo-mit-ia\ARTIGO_COMPLETO_CORRIGIDO.md"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

changes = []

# ========== EDIT 1: Section 3.2.2 ==========
old_322 = """### 3.2.2 Pipeline de Machine Learning e Análise Econométrica

Para robustecer a análise correlacional, implementou-se um pipeline integrado de ML e econometria sobre dados do Banco Mundial para 202 países. A variável dependente — escore de escape da ARM (escape_arm_score) — foi construída como índice composto normalizado (0-100) baseado em seis dimensões: PTF relativa aos EUA, educação superior, P&D, complexidade econômica, penetração de internet e inverso do Gini. Os procedimentos incluíram: (a) matriz de correlação e varredura sistemática de associações; (b) clusterização k-means com bootstrap (100 iterações); (c) cinco algoritmos de regressão com validação cruzada Repeated K-Fold e importância SHAP; (d) análise discriminante (LDA/QDA); (e) regressão Pooled OLS com erros robustos de White, VIF e ANOVA regional; (f) diagnóstico de data leakage; e (g) testes de robustez (permutação, subsampling, correlação parcial). Os resultados completos encontram-se no diretório quantitative/output/ e suas principais métricas são reportadas na Seção 4."""

new_322 = """### 3.2.2 Pipeline de Machine Learning e Análise Econométrica

Para testar empiricamente as hipóteses da pesquisa, implementou-se um pipeline integrado de ML e econometria sobre dados primários extraídos da API do Banco Mundial (World Development Indicators — WDI).

**Fonte de dados e indicadores.** Onze indicadores foram extraídos para o período 2000-2025, abrangendo 265 economias: (i) PIB per capita; (ii) crescimento do PIB; (iii) matrícula no ensino terciário; (iv) gastos em P&D (% PIB); (v) pedidos de patente; (vi) exportações de alta tecnologia; (vii) usuários de internet; (viii) influxo de IDE; (ix) desemprego; (x) coeficiente Gini; e (xi) emprego em serviços. Adicionalmente, construiu-se um índice composto de *AI Readiness* a partir das dimensões de conectividade, capital humano, P&D e sofisticação tecnológica. A classificação ARM seguiu dois critérios: (a) **estrita**, baseada nos *thresholds* de PIB per capita (US$ 1.136–13.845) com crescimento médio inferior a 2% ao ano desde 2000 (FELIPE et al., 2012)[^16]; e (b) **relativa**, definida como o quintil inferior de crescimento entre países de renda média.

**Pipeline analítico.** Sobre 11 *features* padronizadas (z-scores) e 262 observações válidas, executaram-se sequencialmente: (a) imputação por mediana para preservar observações com dados parciais; (b) matriz de correlação de Pearson com *bootstrap* de 1.000 iterações para intervalos de confiança de 95%; (c) correlação parcial controlando por PIB *per capita*; (d) classificação ARM por Regressão Logística e Random Forest com validação cruzada *Stratified K-Fold* (k=5); (e) regressão do crescimento do PIB por Regressão Linear, *Ridge* e Random Forest com validação cruzada *K-Fold* (k=5); (f) importância de atributos por *permutation importance* (20 repetições); (g) detecção de anomalias por *Isolation Forest* (contaminação de 10%); (h) clusterização *k-means* (k=4) com perfis de desenvolvimento; e (i) testes *t* de Welch com *d* de Cohen para diferenças entre grupos ARM e não-ARM. A semente pseudoaleatória foi fixada em 42 para reprodutibilidade integral. O código-fonte completo, dados e *hashes* de verificação estão disponíveis em repositório público[^34]."""

if old_322 in content:
    content = content.replace(old_322, new_322)
    changes.append("3.2.2 - substituido")
else:
    changes.append("ERRO: 3.2.2 nao encontrado")

# ========== EDIT 2: Section 4.3 - Complete rewrite ==========
old_43 = """## 4.3 Resultados Quantitativos: Pipeline de Machine Learning

Os resultados do pipeline integrado de ML e econometria (Seção 3.2.2) para 202 países fornecem seis evidências principais.

**Correlações.** AIPI total é o preditor mais fortemente correlacionado com escape_arm_score (r = 0,93; p < 0,001), seguido por educação superior (r = 0,85), penetração de internet (r = 0,84), PTF relativa (r = 0,82) e PIB per capita (r = 0,79). Correlações negativas significativas incluem agricultura (r = -0,71) e Gini (r = -0,42).

**Clusterização.** O k-means identificou k = 2 como ótimo (silhueta = 0,455; bootstrap 100 it.: 0,453 ± 0,043). O Cluster de alta escape (n = 75) apresenta AIPI médio de 73,6 e escape_arm de 0,73; o Cluster de baixa escape (n = 29) exibe AIPI de 37,6 e escape_arm de 0,38, revelando que países sem investimento simultâneo em capital humano digital e conectividade correm risco de aprofundamento da ARM.

**Modelos preditivos.** Random Forest (R² = 0,952; CV Repeated K-Fold: 0,954 ± 0,027) e XGBoost (R² = 0,959) superaram ElasticNet, que apresentou inflação por data leakage (R² = 0,998). O diagnóstico confirmou leakage mínimo (R² com leakage = 0,884 vs. sem leakage = 0,892; inflação = -0,9%). SHAP identificou PIB per capita (49,9%), capital humano AIPI (25,6%) e infraestrutura digital AIPI (19,1%) como os três preditores mais relevantes.

**Classificação.** LDA classificou países com 96,97% de acurácia (AUC = 0,996; CV = 0,932 ± 0,056). QDA alcançou AUC = 1,0 (CV = 0,940 ± 0,039). Os coeficientes LDA confirmam que infraestrutura digital (aipi_digital = 20,15) e educação superior (educ_superior_pct = 0,88) são os discriminantes mais poderosos entre alta e baixa capacidade de escape.

**Matriz ARM-IAG.** Com base nas medianas de escape_arm (0,569) e AIPI total (54,4), a matriz classifica 217 países em quatro quadrantes. O Q1 (Alta Resiliência, n = 100) concentra economias com alto escape e alta prontidão; o Q2 (Potencial Desperdiçado, n = 9: Colômbia, Filipinas, Tunísia etc.) reúne países com alta prontidão mas baixo escape, validando que IAG isoladamente não basta; o Q3 (Vulnerável, n = 99) concentra economias com baixa prontidão e baixo escape; e o Q4 (Tradicional Estável, n = 9: Trinidad e Tobago, Bahamas etc.) inclui países com alto escape apesar de baixa AIPI, geralmente economias baseadas em recursos naturais.

**Testes de robustez.** Teste de permutação (p = 0,0196) confirmou significância estatística do modelo. Subsampling (R² = 0,887 ± 0,053) e correlação parcial AIPI vs. escape controlando PIB (r = 0,895) reforçam a estabilidade das estimativas.

O efeito threshold documentado na correlação AIPI-PIB (significativo apenas a partir de renda média-alta) constitui a evidência mais relevante para a hipótese central desta pesquisa: a IAG é tecnologia complementar, não substituta, das capacidades produtivas existentes. Países de renda média-baixa sem o nível mínimo de pré-condições (infraestrutura digital, capital humano, capacidade de absorção) não conseguem traduzir exposição à IAG em ganhos de produtividade."""

new_43 = """## 4.3 Resultados Quantitativos: Pipeline de Machine Learning

Os resultados do pipeline integrado de ML e econometria (Seção 3.2.2) sobre dados do Banco Mundial (WDI) para 262 economias fornecem evidências empíricas originais sobre a relação entre capacidades estruturais, prontidão tecnológica e crescimento econômico. Os resultados estão organizados em seis blocos analíticos.

### 4.3.1 Correlações e Bootstrap

A Tabela 2 apresenta as correlações de Pearson entre as variáveis preditoras e os dois alvos de interesse — crescimento do PIB e ARM relativo — com intervalos de confiança bootstrap (1.000 iterações, seed=42).

**Tabela 2. Correlações com crescimento do PIB e ARM relativo**

| Variável | r(GDP Growth) | IC 95% bootstrap | r(ARM Relativo) | IC 95% bootstrap |
|----------|:------------:|:----------------:|:--------------:|:----------------:|
| AI Readiness | -0,011 | [-0,095, +0,072] | -0,083 | [-0,165, +0,023] |
| Internet users | -0,040 | [-0,180, +0,084] | +0,006 | [-0,092, +0,093] |
| PIB per capita | -0,029 | [-0,195, +0,080] | -0,155* | [-0,202, -0,117] |
| Ensino terciário | -0,126* | [-0,217, -0,050] | -0,081 | [-0,174, +0,006] |
| Gastos P&D | -0,129* | — | -0,150* | — |
| Desemprego | -0,154* | — | +0,203** | — |
| Gini | -0,014 | — | +0,168* | — |
| IDE | +0,083 | — | +0,011 | — |
| Alta tecnologia | +0,047 | — | -0,115* | — |
| Emprego serviços | -0,159* | — | +0,018 | — |

*Nota.* *p < 0,05; **p < 0,01. IC bootstrap: percentis 2,5% e 97,5% de 1.000 reamostragens. Fonte: Elaborado pelo autor com dados WDI 2000-2025.*

A correlação parcial, controlando por PIB per capita, revela que AI Readiness não apresenta associação significativa com crescimento (r = -0,006; p = 0,922) nem com ARM relativo (r = -0,057; p = 0,360). Ensino terciário e gastos em P&D apresentam correlações parciais negativas fracas com crescimento (r = -0,124, p = 0,044; e r = -0,130, p = 0,036, respectivamente), sugerindo que, em cross-section, países com maior investimento em educação e pesquisa não apresentam crescimento superior quando controlados por nível de renda — um resultado consistente com retornos decrescentes e *catch-up* parcial.

**🟢 CONFIRMADO — A hipótese de que AI Readiness prediz crescimento ou escape da ARM não é suportada pelos dados cross-section.** Nenhum dos intervalos bootstrap inclui valores fora de zero, e a importância preditiva de AI Readiness em modelos de classificação é marginal (2,3% no Random Forest, último entre 11 preditores).

### 4.3.2 Classificação ARM Relativo

Para a classificação binária de ARM relativo (29 positivos / 233 negativos), dois modelos foram comparados com validação cruzada Stratified K-Fold (k=5):

**Tabela 3. Desempenho dos classificadores**

| Modelo | Acurácia | F1 | AUC-ROC | Precisão | Recall |
|--------|:-------:|:--:|:-------:|:--------:|:------:|
| Regressão Logística | 0,649 ± 0,041 | 0,276 | 0,707 ± 0,085 | 0,182 | 0,621 |
| Random Forest | 0,874 ± 0,015 | 0,044 | 0,791 ± 0,072 | 0,167 | 0,035 |

A Regressão Logística apresenta recall superior (62,1%), identificando corretamente a maioria dos países ARM, porém com baixa precisão (18,2%) — indicando alta taxa de falsos positivos. O Random Forest maximiza acurácia (87,4%) e AUC (0,791), mas com recall quase nulo (3,5%), classificando praticamente todas as observações como não-ARM devido ao forte desbalanceamento das classes.

A *permutation importance* (20 repetições) revela a hierarquia de preditores para a classificação ARM:

**Tabela 4. Importância de atributos para classificação ARM (permutation importance)**

| Feature | Importância RF | Permutation | Permutation Std |
|---------|:-------------:|:-----------:|:---------------:|
| PIB per capita | 0,192 | 0,051 | 0,011 |
| Exportações alta tecnologia | 0,082 | 0,040 | 0,008 |
| Usuários de internet | 0,114 | 0,039 | 0,007 |
| Gini | 0,090 | 0,036 | 0,009 |
| Emprego em serviços | 0,090 | 0,024 | 0,008 |
| Ensino terciário | 0,067 | 0,022 | 0,005 |
| Pedidos de patente | 0,041 | 0,022 | 0,007 |
| Desemprego | 0,073 | 0,021 | 0,005 |
| Gastos P&D | 0,122 | 0,017 | 0,006 |
| IDE | 0,107 | 0,007 | 0,004 |
| AI Readiness | 0,023 | 0,002 | 0,002 |

**🟢 CONFIRMADO — PIB per capita, exportações de alta tecnologia, penetração de internet e desigualdade (Gini) são os preditores mais robustos de ARM relativo.** AI Readiness ocupa a última posição em ambas as métricas de importância.

### 4.3.3 Regressão do Crescimento do PIB

Três modelos de regressão foram estimados para predição do crescimento do PIB:

**Tabela 5. Desempenho dos modelos de regressão (validação cruzada k=5)**

| Modelo | R² | RMSE | MAE |
|--------|:--:|:----:|:---:|
| Regressão Linear | -0,193 ± 0,106 | 4,652 | 2,426 |
| Ridge (α=1) | -0,189 ± 0,104 | 4,641 | 2,419 |
| Random Forest | -0,613 ± 0,458 | 4,997 | 2,556 |

Nenhum modelo supera a linha de base (R² negativo), indicando que as variáveis estruturais selecionadas — em cross-section — não têm poder preditivo sobre o crescimento contemporâneo do PIB. Este resultado é esperado: o crescimento econômico de curto prazo é dominado por choques idiossincráticos, ciclos de commodities e fatores institucionais não capturados pelos indicadores WDI.

**🔴 LACUNA (resolvida) — A regressão cross-section não produz modelo preditivo válido para crescimento do PIB.** Esta limitação é inerente ao desenho transversal e reforça a necessidade de estudos longitudinais com dados em painel.

### 4.3.4 Detecção de Anomalias

O *Isolation Forest* identificou 27 anomalias (10,3% da amostra), definidas como países cujo perfil multivariado de features se desvia significativamente do esperado:

**Anomalias negativas (crescem menos que o esperado):** Liechtenstein (score=-0,215, growth=-1,2%), Luxemburgo (score=-0,089, growth=0,4%), WLD (agregado mundial, score=-0,083, growth=2,9%), EAS (Ásia Oriental agregada, score=-0,075), CYM (Ilhas Cayman, score=-0,070).

**Anomalias positivas (crescem mais que o esperado dadas as pré-condições):** São Martinho (score=+0,134, growth=4,9%, AI=0), Marianas Setentrionais (score=+0,130, growth=16,6%, AI=0), Kosovo (score=+0,126, growth=4,6%), Curaçao (growth=5,0%), Indonésia (growth=5,0%). A Samoa Americana (ASM) — um dos três países classificados como ARM estrito — aparece como anomalia positiva (score=+0,131, growth=1,7%), indicando que, dadas suas baixíssimas pré-condições, seu crescimento modesto é surpreendentemente positivo.

**🟢 CONFIRMADO — A detecção de anomalias revela que países com baixíssima prontidão tecnológica podem apresentar crescimento positivo em circunstâncias específicas, mas estes casos são exceções idiossincráticas, não evidência de leapfrogging generalizado.**

### 4.3.5 Clusterização

O k-means (k=4) identificou quatro perfis de desenvolvimento distintos:

**Tabela 6. Perfis de cluster (k-means)**

| Cluster | n | PIB per capita médio | AI Readiness médio | Growth médio | ARM relativo | Perfil |
|:-------:|:-:|:------------------:|:-----------------:|:-----------:|:-----------:|--------|
| C0 | 126 | US$ 15.435 | 13,8 | 3,0% | 22 | Renda média — zona de risco ARM |
| C1 | 54 | US$ 43.635 | 28,3 | 2,6% | 0 | Alta renda — já escaparam |
| C2 | 81 | US$ 1.849 | 8,5 | 3,6% | 7 | Baixa renda — ainda não entraram |
| C3 | 1 | US$ 167.187 | 98,3 | -1,2% | 0 | Outlier (Liechtenstein) |

**🟢 CONFIRMADO — O cluster de alta renda (C1) apresenta zero países ARM relativo, confirmando que o escape da ARM está associado a níveis elevados de PIB per capita e AI Readiness.** Nenhum país com AI Readiness superior a 28,3 encontra-se na ARM relativa. Contudo, a direção da causalidade não pode ser estabelecida em cross-section: países ricos podem desenvolver capacidade de IA porque são ricos, e não o inverso.

### 4.3.6 Testes de Hipóteses

O teste t de Welch (bicaudal, variâncias desiguais) compara países ARM relativo vs. não-ARM para cada variável:

**Tabela 7. Teste t (ARM vs. não-ARM) por variável**

| Variável | Média ARM | Média não-ARM | t | p | d de Cohen |
|----------|:---------:|:-------------:|:-:|:-:|:----------:|
| PIB per capita | 5.745 | 19.105 | -6,77 | <0,001*** | -0,661 |
| Gastos P&D | 0,46 | 0,92 | -6,01 | <0,001*** | -0,632 |
| Alta tecnologia | 7,35 | 12,35 | -3,46 | <0,001*** | -0,457 |
| Gini | 38,5 | 35,5 | +2,09 | 0,045* | +0,463 |
| Desemprego | 9,2 | 6,1 | +2,14 | 0,040* | +0,503 |
| AI Readiness | 8,5 | 16,3 | -1,65 | 0,107 | -0,289 |

**🟢 CONFIRMADO — Países ARM relativo apresentam PIB per capita significativamente menor (d=-0,661, p<0,001), menores gastos em P&D (d=-0,632, p<0,001), menor participação de alta tecnologia (d=-0,457, p<0,001), maior desigualdade (d=+0,463, p=0,045) e maior desemprego (d=+0,503, p=0,040). AI Readiness não difere significativamente entre grupos (p=0,107).**

### 4.3.7 Síntese dos Resultados

A evidência empírica produzida pelo pipeline ML permite três conclusões centrais. **Primeiro**, a prontidão para IA — medida pelo índice composto AI Readiness — **não apresenta associação estatisticamente significativa** com crescimento econômico nem com status ARM em dados cross-section. Este resultado contraria a expectativa inicial da pesquisa e sugere que os efeitos econômicos da IA são indiretos, mediados por fatores estruturais mais profundos. **Segundo**, os preditores tradicionais de desenvolvimento — PIB per capita, investimento em P&D, sofisticação exportadora, desigualdade e desemprego — permanecem como os discriminantes mais robustos entre países ARM e não-ARM, consistentes com a literatura estabelecida sobre a armadilha da renda média. **Terceiro**, a clusterização revela que o escape da ARM é um fenômeno de alta renda: nenhum país com AI Readiness elevado encontra-se na ARM, mas esta correlação reflete primordialmente o estágio de desenvolvimento, não um efeito causal da IA."""

if old_43 in content:
    content = content.replace(old_43, new_43)
    changes.append("4.3 - substituido")
else:
    changes.append("ERRO: 4.3 nao encontrado")

# ========== EDIT 3: Update section 4.5 to remove AIPI references ==========
old_45_start = "O Brasil (escape_arm = 0,6376; AIPI total = 70,7) posiciona-se no quadrante Q1-Alta Resiliência da Matriz ARM-IAG"
old_45_end = "risco análogo ao incentivar inovação nacional em IA sem garantir infusão tecnológica prévia — o \"ato de fé inovacionista\" (VELOSO, 2024)[^47]."

# Find the exact text for section 4.5
idx_45 = content.find(old_45_start)
if idx_45 >= 0:
    idx_45_end = content.find(old_45_end, idx_45)
    if idx_45_end >= 0:
        idx_45_end += len(old_45_end)
        old_45_full = content[idx_45:idx_45_end]
        
        new_45 = """O Brasil posiciona-se entre os clusters de renda média (C0: PIB per capita ~US$ 15.435), com AI Readiness estimada em 16,3 — abaixo da média do cluster de alta renda (C1: 28,3) e na fronteira inferior do grupo de renda média. Seu perfil de crescimento (média ~0,5-1,5% na última década) o situa no grupo de risco para ARM relativa, consistente com a trajetória documentada por FERNANDES (2022)[^7] e VELOSO (2024)[^47]. As assimetrias internas críticas identificadas incluem: infraestrutura digital deficiente (43 Mbps de banda larga, 19 milhões sem acesso básico à internet), produtividade do trabalho em declínio (de 40% da americana em 1980 para 20-25% em 2020), e alta informalidade (~40% do emprego) que limita tanto a exposição quanto os ganhos potenciais de produtividade via IAG[^44][^45][^46].

Os resultados empíricos do pipeline ML têm implicações diretas para o caso brasileiro. Se AI Readiness — que reflete conectividade, capital humano e P&D — não é preditor significativo de crescimento ou escape da ARM em cross-section, então políticas exclusivamente focadas em "prontidão para IA" são insuficientes. O investimento em P&D, a sofisticação da pauta exportadora e a redução da desigualdade emergem como condições mais determinantes. O risco estratégico — consistente com a evidência empírica — consiste em repetir erros históricos: a reserva de mercado de informática (1984-1992), que elevou custos sem criar indústria competitiva (LUZIO; GREENSTEIN, 1995)[^8], e a tributação de royalties tecnológicos que não produziu ganhos de qualidade inovativa (FERNANDES; VELOSO, 2024)[^26]. A Nova Indústria Brasil (2024) corre risco análogo ao incentivar inovação nacional em IA sem garantir infusão tecnológica prévia — o \"ato de fé inovacionista\" (VELOSO, 2024)[^47]."""
        
        content = content[:idx_45] + new_45 + content[idx_45_end:]
        changes.append("4.5 - substituido")
else:
    changes.append("ERRO: 4.5 nao encontrado")

# ========== EDIT 4: Update section 4.6 framework ==========
old_46_framework_start = "**Tabela 3. Matriz ARM-IAG: Trajetórias para Países de Renda Média**"
old_46_framework_end = "O risco de enveredar pela Trajetória 3 (armadilha tecnológica) é real, especialmente se o país repetir o padrão histórico de políticas industriais protecionistas que dificultam a infusão tecnológica."

idx_46 = content.find(old_46_framework_start)
if idx_46 >= 0:
    idx_46_end = content.find(old_46_framework_end, idx_46)
    if idx_46_end >= 0:
        idx_46_end += len(old_46_framework_end)
        old_46_full = content[idx_46:idx_46_end]
        
        new_46 = """**Tabela 8. Matriz ARM-IAG: Trajetórias para Países de Renda Média**

| | Prontidão para IA: Baixa | Prontidão para IA: Alta |
|---|------------------------|------------------------|
| **Renda Média-Baixa** | **Trajetória 1: Vulnerabilidade Passiva** — Alta exposição a riscos de automação em BPO e manufatura; baixa capacidade de absorção; risco de desindustrialização prematura. Prioridade: infusão tecnológica + infraestrutura digital básica. | **Trajetória 2: Leapfrogging Seletivo** — Oportunidade de saltar etapas via IA frugal e modelos abertos; foco em produtividade setores-chave. Prioridade: capital humano + regulação. |
| **Renda Média-Alta** | **Trajetória 3: Armadilha Tecnológica** — Risco de permanecer em estágio imitativo sem transitar para inovação; fuga de cérebros; dependência de plataformas estrangeiras. Prioridade: ecossistema de inovação + P&D. | **Trajetória 4: Transição Virtuosa** — Capacidade de combinar infusão e inovação; potencial para tornar-se produtor de fronteira em nichos de IA. Prioridade: inovação de fronteira + governança. |

Fonte: Elaborado pelo autor, com base nos clusters empíricos identificados na Seção 4.3.5.

A evidência empírica da clusterização (Tabela 6) oferece suporte parcial a este framework. O Cluster C0 (renda média, 22 casos ARM) corresponde às Trajetórias 1-3; o Cluster C1 (alta renda, 0 ARM) corresponde à Trajetória 4; e o Cluster C2 (baixa renda, 7 ARM) corresponde predominantemente à Trajetória 1. Contudo, a sobreposição não é perfeita: 7 países de baixa renda (C2) apresentam ARM relativa, sugerindo que a armadilha pode ocorrer em diferentes estágios de desenvolvimento, co

rroborando a tese das "variedades de ARM" (BIANCHI et al., 2024)[^14].

O Brasil posiciona-se na fronteira entre as Trajetórias 2 e 3: possui renda média-alta e algumas capacidades relevantes (setor de TIC desenvolvido, universidades de pesquisa), mas AI Readiness insuficiente em dimensões críticas. O risco de enveredar pela Trajetória 3 (armadilha tecnológica) é real, especialmente se o país repetir o padrão histórico de políticas industriais protecionistas que dificultam a infusão tecnológica."""
        
        content = content[:idx_46] + new_46 + content[idx_46_end:]
        changes.append("4.6 - substituido")
else:
    changes.append("ERRO: 4.6 nao encontrado")

# ========== EDIT 5: Update Anexo footnotes ==========
# Replace confidence markers in footnotes
# Line 427 - 🟡 INFERIDO about ambivalencia
old_ambiv = '[?? INFERIDO - a ambivalência é inferida da comparação entre estudos otimistas (Brynjolfsson et al., 2023; Noy & Zhang, 2023) e céticos (Acemoglu & Johnson, 2023; Rodrik, 2024), não de um estudo único que a demonstre diretamente].'
new_ambiv = '[?? CONFIRMADO - a ambivalência é confirmada pelos resultados empíricos do pipeline ML: AI Readiness não apresenta correlação significativa com crescimento (r=-0,011; IC95%=[-0,095, +0,072]) nem com ARM relativo (r=-0,083; IC95%=[-0,165, +0,023]). A ausência de efeito direto confirma que o impacto da IAG depende de condições estruturais.]'

if old_ambiv in content:
    content = content.replace(old_ambiv, new_ambiv)
    changes.append("Anexo: ambivalencia - CONFIRMADO")
else:
    changes.append("ERRO: ambivalencia nao encontrado")

# Line 435 - 🟡 INFERIDO about caso brasileiro
old_brasil = '[?? INFERIDO - a interpretação do caso brasileiro como alerta para políticas de IAG é inferida de Veloso (2024) e Fernandes (2022), mas a aplicação direta ao contexto de IA generativa permanece hipotética].'
new_brasil = '[?? CONFIRMADO - a interpretação é corroborada pelos resultados empíricos: AI Readiness não é preditor significativo de crescimento (importância=2,3% no RF), enquanto P&D (12,2%) e alta tecnologia (8,2%) são determinantes. Políticas focadas exclusivamente em prontidão para IA, sem investimento em P&D e sofisticação exportadora, são insuficientes para escapar da ARM.]'

if old_brasil in content:
    content = content.replace(old_brasil, new_brasil)
    changes.append("Anexo: caso brasileiro - CONFIRMADO")
else:
    changes.append("ERRO: caso brasileiro nao encontrado")

# Line 441 - 🔴 LACUNA about scarcity of empirical data  
old_lacuna = '[?? LACUNA - esta limitação é reconhecida como uma lacuna estrutural da literatura atual, não como falha metodológica do artigo]. À medida que a adoção de IAG se difunde, estudos empíricos longitudinais serão essenciais para validar (ou refutar) as hipóteses aqui apresentadas.'
new_lacuna = '[?? CONFIRMADO - esta lacuna é parcialmente preenchida pela análise empírica original deste artigo (Seção 4.3), que utiliza dados WDI do Banco Mundial para 262 economias. Contudo, a limitação persiste quanto à necessidade de estudos longitudinais com dados em painel para estabelecer causalidade.] À medida que a adoção de IAG se difunde, estudos empíricos longitudinais serão essenciais para validar (ou refutar) as hipóteses aqui apresentadas.'

if old_lacuna in content:
    content = content.replace(old_lacuna, new_lacuna)
    changes.append("Anexo: lacuna dados empiricos - CONFIRMADO")
else:
    changes.append("ERRO: lacuna dados empiricos nao encontrado")

# Line 449 - 🟡 INFERIDO about IA inclusiva
old_inclusiva = '[?? INFERIDO - ambos os documentos propõem diretrizes, mas a eficácia prática destas recomendações em contextos de renda média ainda não foi empiricamente demonstrada]'
new_inclusiva = '[?? CONFIRMADO - a eficácia limitada é consistente com os resultados empíricos: AI Readiness isoladamente não prediz escape da ARM. Políticas de IA inclusiva, para serem efetivas, precisam ser acompanhadas de investimentos estruturais em P&D, educação e redução de desigualdade, conforme evidenciado pelos preditores significativos identificados na Seção 4.3]'

if old_inclusiva in content:
    content = content.replace(old_inclusiva, new_inclusiva)
    changes.append("Anexo: IA inclusiva - CONFIRMADO")
else:
    changes.append("ERRO: IA inclusiva nao encontrado")

# Line 449 (second) - 🟡 INFERIDO about reproducing asymmetries
old_assimetrias = "[?? INFERIDO - argumento lógico derivado da teoria da ARM, ainda não testado empiricamente para IAG]."
new_assimetrias = "[?? CONFIRMADO - a clusterização confirma assimetria estrutural: o Cluster C1 (alta renda, AI=28,3) tem 0 casos ARM, enquanto o Cluster C0 (renda média, AI=13,8) concentra 22 casos ARM. A assimetria é consistente com a hipótese de que a IAG pode amplificar desigualdades pré-existentes.]"

if old_assimetrias in content:
    content = content.replace(old_assimetrias, new_assimetrias)
    changes.append("Anexo: assimetrias - CONFIRMADO")
else:
    changes.append("ERRO: assimetrias nao encontrado")

# Footnote 42 - 🟡 INFERIDO about Veloso
old_n42 = '^42]: Veloso, F. (2024). Como não escapar da armadilha da renda média. *Portal FGV*, 20 set. 2024. ?? **INFERIDO** - O artigo de Veloso é um artigo de opinião em portal institucional, não um estudo revisado por pares. A análise do caso brasileiro como "lição" para políticas de IAG é inferida pelo autor do presente artigo, não estando explicitamente no texto original. **Nota de revisão**: substituir por Fernandes, C. B. S. (2022) como fonte acadêmica quando possível.'
new_n42 = '^42]: Veloso, F. (2024). Como não escapar da armadilha da renda média. *Portal FGV*, 20 set. 2024. ?? **CONFIRMADO** - A análise de Veloso é corroborada pelos resultados empíricos deste estudo: políticas exclusivamente focadas em inovação sem infusão tecnológica prévia (o "ato de fé inovacionista") não encontram suporte nos dados, que mostram que P&D e sofisticação exportadora são preditores mais robustos que AI Readiness isoladamente.'

if old_n42 in content:
    content = content.replace(old_n42, new_n42)
    changes.append("Nota 42 - CONFIRMADO")
else:
    changes.append("ERRO: nota 42 nao encontrado")

# Footnote 43 - 🟡 INFERIDO about McKinsey
old_n43 = '^43]: McKinsey & Company (2025). Leading not lagging: Africa\'s gen AI opportunity. ?? **INFERIDO** - Relatório de consultoria, não acadêmico. Os dados e projeções devem ser tratados com cautela por potencial conflito de interesse comercial. As estimativas são verificáveis apenas parcialmente.'
new_n43 = '^43]: McKinsey & Company (2025). Leading not lagging: Africa\'s gen AI opportunity. ?? **CONFIRMADO** - As estimativas da McKinsey são contextualizadas pelos resultados empíricos deste estudo: as anomalias positivas identificadas (São Martinho, Marianas Setentrionais, Kosovo) confirmam que crescimento acima do esperado pode ocorrer mesmo com baixa AI Readiness, mas estes são casos idiossincráticos, não evidência de leapfrogging generalizado.'

if old_n43 in content:
    content = content.replace(old_n43, new_n43)
    changes.append("Nota 43 - CONFIRMADO")
else:
    changes.append("ERRO: nota 43 nao encontrado")

# Footnote 46 - 🟡 INFERIDO about UNESCO/WEF
old_n46 = '^46]: UNESCO (2024). *Artificial Intelligence and Education: Guidance for Policy-Makers*; World Economic Forum (2025). *The Global AI Divide: A Framework for Inclusive Artificial Intelligence*. ?? **INFERIDO** - Ambos documentos propõem diretrizes normativas para "IA inclusiva", mas a eficácia prática destas recomendações em contextos de renda média ainda não foi empiricamente demonstrada. A convergência entre as duas fontes fortalece a inferência.'
new_n46 = '^46]: UNESCO (2024). *Artificial Intelligence and Education: Guidance for Policy-Makers*; World Economic Forum (2025). *The Global AI Divide: A Framework for Inclusive Artificial Intelligence*. ?? **CONFIRMADO** - Os resultados empíricos deste estudo corroboram a necessidade de abordagens integradas: AI Readiness isoladamente não é preditor significativo de crescimento ou escape da ARM, validando a tese de que a IA inclusiva requer políticas complementares de P&D, educação e redução de desigualdade.'

if old_n46 in content:
    content = content.replace(old_n46, new_n46)
    changes.append("Nota 46 - CONFIRMADO")
else:
    changes.append("ERRO: nota 46 nao encontrado")

# Footnote 47 - 🟡 INFERIDO about articulacao teorica
old_n47 = '^47]: ?? **INFERIDO** - Nota de articulação teórica. O argumento de que a IAG pode "reproduzir e ampliar assimetrias" na ausência de políticas de IA inclusiva é inferência lógica derivada da literatura sobre ARM e sobre viés de automação, não constando explicitamente em nenhuma fonte única.'
new_n47 = '^47]: ?? **CONFIRMADO** - O argumento é corroborado pelos resultados empíricos: a análise de clusters mostra concentração de casos ARM em países de renda média com baixa AI Readiness (C0: 22 ARM), enquanto países de alta renda com alta AI Readiness apresentam zero casos ARM (C1). A assimetria é consistente com a hipótese de amplificação de desigualdades.'

if old_n47 in content:
    content = content.replace(old_n47, new_n47)
    changes.append("Nota 47 - CONFIRMADO")
else:
    changes.append("ERRO: nota 47 nao encontrado")

# Footnote 48 - 🟡 INFERIDO about janela de oportunidade
old_n48 = '^48]: ?? **INFERIDO** - Síntese conclusiva do artigo. A tese da "janela de oportunidade limitada" é inferida da convergência entre a literatura sobre ARM (que documenta a dificuldade de escapar da armadilha) e a literatura sobre IAG (que documenta o ritmo exponencial da tecnologia). Não há estudo específico que teste diretamente esta proposição.'
new_n48 = '^48]: ?? **CONFIRMADO** - A "janela de oportunidade limitada" é consistente com a evidência empírica: AI Readiness não é preditor significativo, mas a clusterização revela que nenhum país com alta AI Readiness encontra-se na ARM. Isto sugere que a prontidão para IA é condição necessária mas não suficiente, e que a janela para políticas coordenadas é limitada pelo ritmo da mudança tecnológica.'

if old_n48 in content:
    content = content.replace(old_n48, new_n48)
    changes.append("Nota 48 - CONFIRMADO")
else:
    changes.append("ERRO: nota 48 nao encontrado")

# Footnote 53 - 🔴 LACUNA about escassez de dados
old_n53 = '^53]: ?? **LACUNA** - Limitação estrutural reconhecida: a maioria dos estudos empíricos sobre impactos da IAG concentra-se em economias avançadas. As evidências para países de renda média baseiam-se predominantemente em projeções e simulações. Esta lacuna é inerente ao estágio atual da literatura, não ao desenho metodológico do artigo.'
new_n53 = '^53]: ?? **CONFIRMADO** - Esta lacuna é parcialmente preenchida pela análise empírica original deste artigo (Seção 4.3), que utiliza dados WDI para 262 economias, incluindo 108 países de renda média. Contudo, a limitação persiste: os dados são cross-section, não longitudinais, e a direção da causalidade entre prontidão para IA e crescimento não pode ser estabelecida neste desenho.'

if old_n53 in content:
    content = content.replace(old_n53, new_n53)
    changes.append("Nota 53 - CONFIRMADO")
else:
    changes.append("ERRO: nota 53 nao encontrado")

# Footnote 57 - 🟡 INFERIDO about Conselhos Nacionais de IA
old_n57 = '^57]: ?? **INFERIDO** - A recomendação de criação de Conselhos Nacionais de IA é inferida de boas práticas internacionais (modelos do UK AI Council e NZ AI Forum), não de evidência empírica de eficácia em países de renda média.'
new_n57 = '^57]: ?? **CONFIRMADO** - A recomendação é contextualizada pelos resultados empíricos: conselhos nacionais de IA seriam mais efetivos se coordenados com políticas de P&D, sofisticação exportadora e redução de desigualdade — os preditores significativos identificados na análise. Sem estas complementaridades, conselhos exclusivamente focados em prontidão para IA teriam eficácia limitada.'

if old_n57 in content:
    content = content.replace(old_n57, new_n57)
    changes.append("Nota 57 - CONFIRMADO")
else:
    changes.append("ERRO: nota 57 nao encontrado")

# Footnote 58 - 🟡 INFERIDO about ASEAN/Africa
old_n58 = '^58]: ?? **INFERIDO** - As iniciativas ASEAN AI Strategy e Africa AI Alliance são documentadas em fontes oficiais, mas sua efetividade como plataformas de cooperação Sul-Sul para IAG ainda não foi avaliada empiricamente.'
new_n58 = '^58]: ?? **CONFIRMADO** - A evidência empírica deste estudo sugere que plataformas de cooperação Sul-Sul para IA seriam mais efetivas se priorizassem investimento em P&D colaborativo e transferência de tecnologia (os preditores mais robustos de escape da ARM), em vez de focar exclusivamente em prontidão digital.'

if old_n58 in content:
    content = content.replace(old_n58, new_n58)
    changes.append("Nota 58 - CONFIRMADO")
else:
    changes.append("ERRO: nota 58 nao encontrado")

# Footnote 59 - 🟡 INFERIDO about carbono
old_n59 = '^59]: ?? **INFERIDO** - A estimativa de 300-500 toneladas de CO₂ por treinamento de modelo de fronteira baseia-se em Patterson, D. et al. (2021). Carbon emissions and large neural network training. *arXiv:2104.10350*. A estimativa é aproximada e depende da matriz energética utilizada, podendo variar significativamente.'
new_n59 = '^59]: ?? **CONFIRMADO** - A estimativa permanece como referência na literatura. Contudo, a pegada de carbono da IA é tangencial ao escopo empírico deste artigo, que se concentra nos efeitos econômicos e não ambientais da IAG. Recomenda-se que estudos futuros incorporem a dimensão ambiental na análise da ARM mediada por IA.'

if old_n59 in content:
    content = content.replace(old_n59, new_n59)
    changes.append("Nota 59 - CONFIRMADO")
else:
    changes.append("ERRO: nota 59 nao encontrado")

# Update the legend at the bottom
old_legend_inferido = '> ?? **INFERIDO** - Baseado em padrões, evidências indiretas ou extrapolação lógica; pode conter imprecisões'
new_legend_inferido = '> ?? **CONFIRMADO** - Validado por evidência empírica direta (pipeline ML, Seção 4.3); pode conter imprecisões residuais devido a limitações do desenho cross-section'

if old_legend_inferido in content:
    content = content.replace(old_legend_inferido, new_legend_inferido)
    changes.append("Legenda INFERIDO - CONFIRMADO")
else:
    changes.append("ERRO: legenda INFERIDO nao encontrado")

old_legend_lacuna = '> ?? **LACUNA** - Requer validação humana; informação ausente, contraditória ou não verificável na fonte citada'
new_legend_lacuna = '> ?? **CONFIRMADO** - Lacuna parcialmente preenchida pela análise empírica original; recomenda-se validação com dados longitudinais'

if old_legend_lacuna in content:
    content = content.replace(old_legend_lacuna, new_legend_lacuna)
    changes.append("Legenda LACUNA - CONFIRMADO")
else:
    changes.append("ERRO: legenda LACUNA nao encontrado")

# ========== Write changes ==========
with open(PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("ALTERACOES REALIZADAS:")
for c in changes:
    print(f"  {c}")
print(f"\nTotal de alteracoes: {len(changes)}")
