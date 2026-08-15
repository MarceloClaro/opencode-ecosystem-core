# Desenvolvimento educacional em microrregião do Semiárido cearense: o padrão associativo entre desempenho escolar e renda no Sertão de Cratéus

**Autor:** Marcelo Claro Laranjeira — ORCID: https://orcid.org/0000-0001-8996-2887

---

## Resumo

Este estudo testa, na microrregião do Sertão de Cratéus (Ceará, IBGE 23018; nove municípios), se o padrão associativo entre desempenho escolar (IDEB) e renda municipal identificado em nível nacional — forte em níveis, mas não discernível dentro das unidades ao longo do tempo — se reproduz em escala subnacional. Com dados oficiais e auditáveis (INEP, edições 2005–2025; IBGE, PIB municipal 2010–2021 e Censo Demográfico 2022) e protocolo de validação espelhado em estudo anterior (bootstrap por cluster, primeiras diferenças, efeitos fixos de município e ano, validação cruzada leave-one-out por município, MDES e TOST), encontramos: (i) correlação transversal moderada-forte entre IDEB e log do PIB per capita defasado (r = 0,49; IC95% [0,34; 0,64]), replicada fora da amostra em 9/9 municípios (LOOCV mediana r = 0,62); (ii) associação dentro da unidade nula (primeiras diferenças r = −0,05, p = 0,61) e coeficiente de efeitos fixos não significativo (β = 2,61; IC95% [−1,59; 6,80]; p = 0,23); (iii) MDES de 6,05 pontos e TOST não significativo, indicando não-detecção (não equivalência) dado o n municipal; e (iv) evidência de que a premissa de estagnação do IDEB não se sustenta com os dados mais recentes: os nove municípios atingiram a meta pactuada para 2021 e apresentaram ganho médio de 5,93 pontos (anos iniciais, 2007–2025), sem associação estatisticamente discernível entre ganho educacional e renda do responsável (r = −0,14; p = 0,73). Conclui-se que a associação renda–desempenho no Sertão de Cratéus reproduz o padrão nacional (associação em níveis, ausência de associação dentro), enquanto o crescimento educacional observado não acompanha variações de renda municipal — consistente com a literatura sobre políticas educacionais do Ceará, embora sem pretensão causal.

**Palavras-chave:** IDEB; renda; microrregião; Ceará; painel municipal; validação cruzada; efeitos fixos.

---

## Abstract

This study tests, in the Sertão de Cratéus microregion (Ceará state, Brazil; IBGE 23018; nine municipalities), whether the associative pattern between school performance (IDEB) and municipal income identified at the national level — strong across units, but not discernible within units over time — reproduces at the subnational scale. Using official auditable data (INEP, 2005–2025 editions; IBGE, municipal GDP 2010–2021 and 2022 Demographic Census) and a validation protocol mirrored on a previous study (cluster bootstrap, first differences, municipality-and-year fixed effects, leave-one-out cross-validation by municipality, MDES and TOST), we find: (i) moderate-to-strong cross-sectional correlation between IDEB and lagged log GDP per capita (r = 0.49; 95% CI [0.34; 0.64]), replicated out-of-sample in 9/9 municipalities (LOOCV median r = 0.62); (ii) null within-unit association (first differences r = −0.05, p = 0.61) and nonsignificant fixed-effects coefficient (β = 2.61; 95% CI [−1.59, 6.80]; p = 0.23); (iii) MDES of 6.05 points and nonsignificant TOST, indicating non-detection (not equivalence) given the municipal sample size; and (iv) evidence that the premise of IDEB stagnation does not hold in the most recent data: all nine municipalities met the pactuated target for 2021 and showed a mean gain of 5.93 points (early grades, 2007–2025), with no statistically discernible association between educational gain and household head income (r = −0.14; p = 0.73). The income–performance association in Sertão de Cratéus reproduces the national pattern (association in levels, absence of within-unit association), while observed educational growth does not track municipal income variation — consistent with the literature on Ceará's education policies, with no causal claims.

**Keywords:** IDEB; income; microregion; Ceará; municipal panel; cross-validation; fixed effects.

---

## 1. Introdução

A relação entre renda e desempenho educacional é um dos temas mais persistentes da pesquisa em educação comparada. Hanushek e Woessmann (2015) demonstraram que o "capital de conhecimento" de uma nação — medido por habilidades cognitivas, e não apenas por anos de escolaridade — associa-se fortemente ao crescimento econômico de longo prazo. No Brasil, análises de avaliação em larga escala mostram desigualdades substanciais associadas ao nível socioeconômico (Cito; Marôco, 2026), e estudos multiníveis documentam o impacto associativo da pobreza sobre o IDEB (Duarte, 2013; Andrews; Vries, 2012).

O presente trabalho parte de um estudo anterior que identificou, em nível de países, um padrão associativo específico: correlação forte e consistente entre desempenho escolar e renda quando se comparam unidades entre si (níveis), mas associação nula ou frágil quando se examina a variação dentro das unidades ao longo do tempo (primeiras diferenças e efeitos fixos). A questão aqui é saber se esse padrão se reproduz em escala subnacional, em uma microrregião do Semiárido cearense historicamente associada a baixos indicadores socioeconômicos: o Sertão de Cratéus.

Deliberadamente, este estudo não testa causalidade: trata-se de evidência associativa, com descrição explícita dos limites de inferência. O objetivo é avaliar se o padrão nacional — forte em níveis, nulo dentro das unidades — se mantém quando a unidade de análise é o município, dentro de uma única microrregião, e se a premissa de estagnação do IDEB na região se sustenta com os dados oficiais mais recentes (2025).

## 2. Fundamentação

### 2.1 O IDEB como indicador e política

O IDEB, criado em 2007, combina fluxo escolar e proficiência no SAEB, atribuindo metas bianuais às escolas públicas (Soares; Xavier, 2013; Schneider; Nardi, 2014). A literatura critica seu caráter de accountability gerencial (Afonso, 2012), mas reconhece sua função mobilizadora (Lacruz; Américo; Carniel, 2019). Brunello e Kiss (2022) mostram, em contexto internacional, que avaliações com consequências ("high stakes") alteram o comportamento de escolas e professores.

### 2.2 O caso do Ceará: regime de colaboração e alfabetização

O Ceará tornou-se caso emblemático por seu regime de colaboração entre estado e municípios, institucionalizado pelo Programa Alfabetização na Idade Certa (PAIC, Lei 14.026/2007). A literatura documenta ganhos expressivos de alfabetização e aprendizagem associados ao PAIC (Costa; Carnoy, 2015; Cruz; Ribeiro; Batista, 2022), com evidência de que a coordenação regional pode produzir resultados comparáveis à coordenação nacional (Segatto; Oliveira; Silva, 2024). Carnoy et al. (2017) mostraram, em análise intranacional, que diferenças estaduais de desempenho no Brasil podem ensinar sobre políticas eficazes — e o Ceará figura entre os casos de maior progresso.

### 2.3 Renda e desempenho: o padrão associativo

Em análises transversais, municípios mais ricos tendem a apresentar IDEB mais alto (Duarte, 2013; Andrews; Vries, 2012). Contudo, dentro de uma mesma unidade ao longo do tempo, a variação da renda não costuma acompanhar a variação do desempenho — o crescimento do IDEB frequentemente ocorre mesmo onde a renda cresce pouco, como documentado para municípios pobres brasileiros (Andrews; Vries, 2012). Esse contraste entre associação em níveis e ausência de associação dentro das unidades é o "padrão associativo" que motivou o estudo nacional anterior e que aqui se testa em escala micro.

## 3. Método

### 3.1 Delimitação e dados

A microrregião do Sertão de Cratéus (IBGE 23018) compreende nove municípios: Ararendá (2301257), Crateús (2304103), Independência (2305605), Ipaporanga (2305654), Monsenhor Tabosa (2308609), Nova Russas (2309300), Novo Oriente (2309409), Quiterianópolis (2311264) e Tamboril (2313203). Usaram-se apenas fontes oficiais e auditáveis:

- **INEP — IDEB municipal**, edição 2025 (série 2005–2025), rede Municipal, anos iniciais e finais do ensino fundamental (download.inep.gov.br);
- **IBGE — PIB dos Municípios**, base 2010–2021 (ftp.ibge.gov.br), PIB per capita a preços correntes;
- **IBGE — Censo Demográfico 2022**, agregados por município: rendimento nominal médio mensal das pessoas responsáveis (V06004) e mediana (V06006);
- **IBGE — Malha municipal 2023** (geoftp), para os mapas.

Todos os downloads foram registrados em manifesto de proveniência (URL, timestamp, SHA-256), disponível em `data/raw/SOURCE_MANIFEST.json`. O IPCE (IPC Marketing Editora), mencionado na demanda original, é um índice comercial sem acesso público auditável; portanto, usaram-se como proxies oficiais o PIB per capita e a renda do responsável, com essa limitação declarada.

### 3.2 Painel e variáveis

O painel emparelha, por município e ano, o IDEB observado ao log do PIB per capita defasado em dois anos (IDEB do ano *t* com PIB de *t*−2), suavizando contemporaneidade mecânica. Para a microrregião, o painel de estimação cobre os anos IDEB 2013–2023 (n = 108 observações; 9 municípios × 6 anos × 2 etapas). Para robustez, repetiram-se as análises para o Ceará (184 municípios) e o Brasil (5.360 municípios).

### 3.3 Hipóteses

- **H1 (níveis):** a correlação transversal entre IDEB e log do PIB per capita é positiva e estatisticamente discernível (r ≥ 0,3; IC95% sem 0).
- **H2 (dentro):** a associação dentro das unidades é fraca ou nula — primeiras diferenças r próximo de zero e coeficiente de efeitos fixos de município e ano não significativo.
- **H3 (estagnação):** o ganho de IDEB (2007→último disponível) é inferior à meta pactuada pelo INEP (VL_PROJECAO_2021) e não se associa à renda municipal.

### 3.4 Procedimentos de validação

1. **Correlações em níveis:** Pearson com intervalo de confiança por bootstrap por cluster (município), seed 42, 2.000 réplicas (500 quando o número de clusters excede 50).
2. **Primeiras diferenças:** correlação de Pearson das diferenças de primeira ordem dentro de cada município-etapa.
3. **Efeitos fixos:** regressão com efeitos fixos de município e ano via within-transformation dupla (município e ano), com erros padrão convencionais.
4. **LOOCV por município:** para cada um dos nove municípios, estima-se a correlação nos oito restantes e avalia-se a replicação no município retido, reportando a distribuição dos r de teste.
5. **MDES/TOST:** mínimo efeito detectável (poder 80%, α 5%) e teste de equivalência com margem ±0,10 no coeficiente de efeitos fixos.
6. **Transparência:** scripts `baixar_dados.py`, `analise_crateus.py` e `mapa_crateus.py`; saídas completas em `outputs/expanded/resultados_r426.json` e proveniência `provenance_r426.json`.

## 4. Resultados

### 4.1 H1 — associação em níveis

Na microrregião, a correlação transversal entre IDEB e log do PIB per capita defasado foi r = 0,49 (IC95% bootstrap por cluster [0,34; 0,64]; p < 0,001; n = 108; 9 clusters), confirmando H1. Para o Ceará, r = 0,26 (IC95% [0,20; 0,33]); para o Brasil, r = 0,46 (IC95% [0,44; 0,47]; n = 48.695). A associação em níveis está presente na microrregião, embora com magnitude moderada — não tão elevada quanto a documentada em nível de países, mas consistente com a literatura municipal brasileira.

### 4.2 H2 — associação dentro das unidades

As primeiras diferenças dentro de município-etapa na microrregião foram nulas: r = −0,05 (p = 0,61; n = 90). O coeficiente de efeitos fixos de município e ano foi β = 2,61 (IC95% [−1,59; 6,80]; p = 0,23; n = 108): positivo, mas não estatisticamente discernível de zero. Para o Ceará, β = 0,001 (IC95% [−0,28; 0,29]; p = 0,99). Para o Brasil, β = 0,11 (IC95% [0,08; 0,15]; p < 0,001): pequeno, embora discernível dado o enorme n. H2 se confirma na microrregião e no Ceará: dentro das unidades, a associação entre variação de renda e variação de IDEB não é discernível.

### 4.3 Validação cruzada leave-one-out por município

A correlação de níveis estimada fora da amostra (treino nos oito municípios restantes, teste no município retido) foi positiva em 9/9 municípios (100%), com mediana r = 0,62 (média 0,65; DP 0,11). Os r de teste por município variaram de 0,43 (Quiterianópolis) a 0,81 (Ararendá). A associação em níveis não depende de um único município: é replicável em todos os nove.

### 4.4 MDES e TOST

Com n municipal de 9 e 108 observações, o mínimo efeito detectável foi de 6,05 pontos de IDEB por unidade de log do PIB — muito acima de qualquer coeficiente plausível. O teste de equivalência (TOST, margem ±0,10) não foi significativo (p = 0,88). Portanto, o correto é declarar **não-detecção**: a amostra não permite afirmar efeito, mas tampouco permite declarar equivalência. Essa é uma limitação central, explicitamente assumida.

### 4.5 H3 — ganho educacional e metas

Contrariando a premissa de estagnação, os dados INEP 2025 mostram crescimento expressivo do IDEB nos nove municípios (anos iniciais, 2007→2025): ganho médio de 5,93 pontos, com todos os municípios **acima da meta pactuada para 2021**. O IDEB 2025 em anos iniciais variou de 6,8 (Quiterianópolis) a 9,9 (Ipaporanga), valores superiores à média nacional da rede municipal. Em anos finais, todos os nove municípios também atingiram a meta 2021. A correlação entre ganho de IDEB (anos iniciais) e renda média do responsável foi nula: r = −0,14 (p = 0,73; n = 9). Ou seja: não há evidência de que municípios com maior renda tenham tido maior ganho educacional — o crescimento ocorreu de forma generalizada e não acompanhou a variação de renda.

### 4.6 Mapas

Os mapas coropléticos (Figuras 1 e 2, em `outputs/mapas/`) apresentam os dois proxies oficiais de desenvolvimento por município: renda média mensal do responsável (Censo 2022, IBGE) e PIB per capita (2021, IBGE). Crateús, sede regional, destaca-se em ambos os indicadores; os demais municípios concentram-se nas faixas inferiores, retratando a heterogeneidade intra-regional que a análise de níveis explora.

## 5. Discussão

Os resultados indicam que o padrão associativo nacional — forte em níveis, nulo dentro das unidades — se reproduz na microrregião do Sertão de Cratéus: municípios com maior PIB per capita tendem a ter IDEB mais alto (r = 0,49), mas a variação temporal da renda não acompanha a variação do desempenho escolar (primeiras diferenças nulas; efeitos fixos não significativos). A validação cruzada por município sugere que a associação de níveis é robusta e generalizada.

Dois pontos merecem destaque. Primeiro, a associação em níveis não deve ser lida como "a pobreza determina o baixo desempenho": municípios pobres da microrregião alcançaram IDEB 2025 elevado (até 9,9 pontos), consistentemente acima da meta. Segundo, o crescimento educacional não acompanhou a renda — o que é compatível com a literatura sobre políticas educacionais cearenses (PAIC, regime de colaboração, alfabetização na idade certa), que associa os ganhos a fatores institucionais e pedagógicos, e não à variação econômica local (Costa; Carnoy, 2015; Cruz; Ribeiro; Batista, 2022; Segatto; Oliveira; Silva, 2024).

As limitações são explícitas: (i) n municipal de 9 e 108 observações implica poder estatístico baixo (MDES de 6,05), tornando a ausência de associação dentro das unidades uma **não-detecção** e não uma prova de ausência; (ii) o PIB municipal e a renda do responsável são proxies do desenvolvimento local — o IPCE original não é auditável; (iii) não há pretensão causal; (iv) os efeitos fixos controlam fatores invariantes no tempo e choques comuns por ano, mas não outros confundidores variáveis; (v) as correlações de níveis podem refletir fatores omitidos (infraestrutura, gestão) correlacionados com renda e desempenho.

## 6. Considerações finais

Este estudo contribui com evidência associativa subnacional sobre a relação entre renda e desempenho escolar: o padrão nacional (níveis fortes, dentro nula) se reproduz em uma microrregião do Semiárido cearense. Adicionalmente, os dados oficiais mais recentes refutam a premissa de estagnação: todos os nove municípios do Sertão de Cratéus superaram as metas pactuadas, com ganhos médios de cerca de seis pontos no período 2007–2025 e IDEB 2025 elevado mesmo em municípios de baixa renda. A ausência de associação entre ganho educacional e renda sugere que fatores de política educacional — e não a variação econômica — estão associados à trajetória observada, em linha com a literatura do Ceará. Recomenda-se, para estudos futuros, ampliar o painel para todas as microrregiões cearenses e estaduais, incorporar controles de política (PAIC, ICMS educacional) e utilizar estratégias quase-experimentais para testar mecanismos causais específicos.

## Referências

AFONSO, A. J. Para uma concetualização alternativa de accountability em educação. *Educação & Sociedade*, Campinas, v. 33, n. 119, p. 471–484, 2012. https://doi.org/10.1590/S0101-73302012000200008

ANDREWS, C. W.; VRIES, M. S. de. Pobreza e municipalização da educação: análise dos resultados do IDEB (2005-2009). *Cadernos de Pesquisa*, São Paulo, v. 42, n. 147, p. 826–847, 2012. https://doi.org/10.1590/S0100-15742012000300010

BRUNELLO, G.; KISS, D. Math scores in high stakes grades. *Economics of Education Review*, v. 87, 102219, 2022. https://doi.org/10.1016/j.econedurev.2021.102219

CARNOY, M.; MAROTTA, L.; LOUZANO, P.; et al. Intranational comparative education: what state differences in student achievement can teach us about improving education — the case of Brazil. *Comparative Education Review*, v. 61, n. 4, 2017. https://doi.org/10.1086/693981

CITO, L.; MARÔCO, J. Beyond the average: mapping educational inequality in Brazil with PISA 2022. *Large-scale Assessments in Education*, v. 14, 2026. https://doi.org/10.1186/s40536-026-00302-0

COSTA, L. O.; CARNOY, M. The effectiveness of an early-grade literacy intervention on the cognitive achievement of Brazilian students. *Educational Evaluation and Policy Analysis*, v. 37, n. 4, p. 567–590, 2015. https://doi.org/10.3102/0162373715571437

CRUZ, M. C. M. T.; RIBEIRO, V. M.; BATISTA, J. M. Contexto de implementação do Programa de Aprendizagem na Idade Certa (PAIC). *Revista Ibero-Americana de Estudos em Educação*, Araraquara, v. 17, n. esp. 3, p. 2405–2432, 2022. https://doi.org/10.21723/riaee.v17iesp.3.16719

DUARTE, N. de S. O impacto da pobreza no Ideb: um estudo multinível. *Revista Brasileira de Estudos Pedagógicos*, Brasília, DF, v. 94, n. 237, p. 343–363, 2013. https://doi.org/10.1590/S2176-66812013000200002

HANUSHEK, E. A.; WOESSMANN, L. *The Knowledge Capital of Nations: education and the economics of growth*. Cambridge, MA: MIT Press, 2015. https://doi.org/10.7551/mitpress/9780262029179.001.0001

LACRUZ, A. J.; AMÉRICO, B. L.; CARNIEL, F. Indicadores de qualidade na educação: análise discriminante dos desempenhos na Prova Brasil. *Revista Brasileira de Estudos Pedagógicos*, Brasília, DF, v. 100, n. 254, 2019. https://doi.org/10.1590/S1413-24782019240002

SCHNEIDER, M. P.; NARDI, E. L. O IDEB e a construção de um modelo de accountability na educação básica brasileira. *Revista Portuguesa de Educação*, Braga, v. 27, n. 1, p. 7–28, 2014. https://doi.org/10.21814/rpe.4295

SEGATTO, C. I.; OLIVEIRA, K. de; SILVA, A. L. N. da. Os limites do PNE (2014-2024) no regime de colaboração. *Estudos em Avaliação Educacional*, São Paulo, v. 35, e10549, 2024. https://doi.org/10.18222/eae.v35.10549

SOARES, J. F.; XAVIER, F. P. Pressupostos educacionais e estatísticos do Ideb. *Educação & Sociedade*, Campinas, v. 34, n. 124, p. 903–923, 2013. https://doi.org/10.1590/S0101-73302013000300013

## Apêndice A — Proveniência e reprodutibilidade

- Scripts: `scripts/baixar_dados.py`, `scripts/analise_crateus.py`, `scripts/mapa_crateus.py`.
- Manifesto de fontes (URL, timestamp, SHA-256): `data/raw/SOURCE_MANIFEST.json`.
- Resultados completos: `outputs/expanded/resultados_r426.json`; proveniência computacional: `outputs/expanded/provenance_r426.json`.
- Mapas: `outputs/mapas/mapa_renda_responsavel_censo2022.png`, `outputs/mapas/mapa_pib_per_capita_2021.png`.
- Fontes: INEP — IDEB municipal, edição 2025 (https://download.inep.gov.br/ideb/resultados/divulgacao_anos_iniciais_municipios_2025.zip e _anos_finais_); IBGE — PIB dos Municípios 2021 (https://ftp.ibge.gov.br/Pib_Municipios/2021/base/base_de_dados_2010_2021_xlsx.zip); IBGE — Censo 2022, rendimento do responsável (https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/.../Agregados_por_municipios_renda_responsavel_BR_20260508_csv.zip); IBGE — malha 2023 (https://geoftp.ibge.gov.br/.../CE_Municipios_2023.zip).
- Declaração de limites: evidência associativa; n municipal de 9; MDES 6,05; não-detecção declarada; IPCE substituído por proxies oficiais.
