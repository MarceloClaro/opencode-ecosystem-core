# Desenvolvimento educacional em microrregião do Semiárido cearense: o padrão associativo entre desempenho escolar e renda no Sertão de Crateús

**Autor:** Marcelo Claro Laranjeira — ORCID: https://orcid.org/0000-0001-8996-2887

---

## Resumo

Este estudo testa, na microrregião do Sertão de Crateús (Ceará, IBGE 23018; nove municípios), a relação entre desempenho escolar (IDEB) e renda municipal em duas dimensões complementares: entre unidades (níveis) e dentro das unidades ao longo do tempo. Com dados oficiais e auditáveis (INEP, edições 2005–2025; IBGE, PIB municipal 2010–2021 deflacionado pelo IPCA; Censo Demográfico 2022) e protocolo inferencial conservador (estimador *between* com IC95% por bootstrap por cluster; correlação em níveis com bootstrap por cluster; primeiras diferenças; efeitos fixos de município×etapa e ano com erros clusterizados e correção de pequena amostra; *wild cluster bootstrap* para G=9; MDES e TOST com margem substantiva), encontramos: (i) na dimensão entre municípios (n = 9), a correlação entre IDEB e log do PIB per capita real defasado foi r = −0,24 (IC95% [−0,77; 0,50]; p = 0,52) — sem evidência de associação transversal discernível na microrregião; (ii) dentro das unidades, as primeiras diferenças foram próximas de zero (r = −0,07; p = 0,50) e o coeficiente de efeitos fixos não foi discernível de zero sob erros clusterizados (β = 2,61; IC95% cluster [−1,73; 6,95]; p = 0,20; p *wild* = 0,23); (iii) o estudo só detectaria efeitos de magnitude incomum (MDES ≈ 6,0 pontos de IDEB por unidade de log do PIB; ≈ 0,57 ponto por +10% do PIB per capita real), e o TOST com margem substantiva (±0,5 ponto) não foi significativo — portanto a precisão é insuficiente para sustentar tanto efeito quanto equivalência; e (iv) os nove municípios atingiram ou superaram as metas projetadas pelo INEP no mesmo ano de referência (99,1% das 108 comparações entre 2011 e 2021), com ganho médio de 5,93 pontos no IDEB de anos iniciais entre 2007 e 2025, sem associação estatisticamente discernível entre ganho educacional e renda do responsável (r = −0,14; p = 0,73; n = 9). Conclui-se que, no Sertão de Crateús, não se sustenta a hipótese de associação renda–desempenho nem entre nem dentro dos municípios; o crescimento educacional observado não acompanha variações de renda municipal — consistente com a literatura sobre políticas educacionais do Ceará, embora sem pretensão causal.

**Palavras-chave:** IDEB; renda; microrregião; Ceará; painel municipal; efeitos fixos; *wild cluster bootstrap*.

---

## Abstract

This study tests, in the Sertão de Crateús microregion (Ceará state, Brazil; IBGE 23018; nine municipalities), the relationship between school performance (IDEB) and municipal income in two complementary dimensions: across units (levels) and within units over time. Using official auditable data (INEP, 2005–2025 editions; IBGE, municipal GDP 2010–2021 deflated by the IPCA; 2022 Demographic Census) and a conservative inferential protocol (between estimator with cluster-bootstrap 95% CI; level correlation with cluster bootstrap; first differences; municipality×grade and year fixed effects with clustered errors and small-sample correction; wild cluster bootstrap for G=9; MDES and TOST with a substantive margin), we find: (i) across municipalities (n = 9), the correlation between IDEB and lagged real log GDP per capita was r = −0.24 (95% CI [−0.77, 0.50]; p = 0.52) — no discernible cross-sectional association in the microregion; (ii) within units, first differences were near zero (r = −0.07, p = 0.50) and the fixed-effects coefficient was not discernible from zero under clustered errors (β = 2.61; 95% clustered CI [−1.73, 6.95]; p = 0.20; wild p = 0.23); (iii) the study could only detect effects of unusual magnitude (MDES ≈ 6.0 IDEB points per log unit of GDP; ≈ 0.57 point per 10% real GDP per capita growth), and the TOST with a substantive margin (±0.5 point) was not significant — precision is therefore insufficient to claim either effect or equivalence; and (iv) all nine municipalities met the INEP agreed targets in the same reference year (99.1% of 108 comparisons between 2011 and 2021), with a mean gain of 5.93 IDEB points in early grades between 2007 and 2025, with no statistically discernible association between educational gain and household head income (r = −0.14, p = 0.73, n = 9). In Sertão de Crateús, the income–performance association is not supported either across or within municipalities, while observed educational growth does not track municipal income variation — consistent with the literature on Ceará's education policies, with no causal claims.

**Keywords:** IDEB; income; microregion; Ceará; municipal panel; fixed effects; wild cluster bootstrap.

---

## 1. Introdução

A relação entre renda e desempenho educacional é um dos temas mais persistentes da pesquisa em educação comparada. Hanushek e Woessmann (2015) demonstraram que o "capital de conhecimento" de uma nação — medido por habilidades cognitivas, e não apenas por anos de escolaridade — associa-se fortemente ao crescimento econômico de longo prazo. No Brasil, análises de avaliação em larga escala mostram desigualdades substanciais associadas ao nível socioeconômico (Cito; Marôco, 2026), e estudos multiníveis documentam o impacto associativo da pobreza sobre o IDEB (Duarte, 2013; Andrews; Vries, 2012).

Uma distinção analítica frequentemente negligenciada separa dois tipos de associação entre renda e desempenho escolar: a **transversal** (entre unidades: municípios mais ricos tendem a ter IDEB mais alto) e a **temporal** (dentro de uma mesma unidade: quando a renda de um município cresce, seu IDEB cresce?). A primeira é amplamente documentada; a segunda é mais incerta e raramente testada em pequenas escalas. Para o Semiárido brasileiro, onde a pobreza é estrutural e a política educacional estadual (regime de colaboração, alfabetização na idade certa) produziu ganhos notáveis de aprendizagem, essa distinção tem implicações práticas: se a associação for apenas transversal, políticas de crescimento econômico local não deveriam ser tratadas como condição necessária para o avanço educacional.

A microrregião do Sertão de Crateús (IBGE 23018), no Ceará, oferece um contexto privilegiado para esse teste: nove municípios pequenos, de baixa renda, sob a mesma coordenação estadual de políticas educacionais, com série histórica completa do IDEB (2005–2025) e indicadores municipais oficiais de renda (PIB municipal e Censo Demográfico 2022).

**Pergunta de pesquisa (RQ):** no Sertão de Crateús, a associação entre renda municipal e desempenho escolar no IDEB é transversal (entre municípios), temporal (dentro dos municípios), ou ambas? Em particular: (a) municípios com maior renda têm IDEB mais alto? (b) variações de renda dentro do município acompanham variações de IDEB? (c) o ganho educacional observado na região depende da renda municipal, e os municípios cumprem as metas pactuadas pelo INEP?

Deliberadamente, este estudo não testa causalidade: trata-se de evidência associativa, com descrição explícita dos limites de inferência. As hipóteses operacionalizadas na Seção 3 respondem diretamente à RQ.

## 2. Fundamentação

### 2.1 O IDEB como indicador e política

O IDEB, criado em 2007, combina fluxo escolar e proficiência no SAEB, atribuindo metas bianuais às escolas públicas (Soares; Xavier, 2013; Schneider; Nardi, 2014). A literatura critica seu caráter de accountability gerencial (Afonso, 2012), mas reconhece sua função mobilizadora (Lacruz; Américo; Carniel, 2019). Brunello e Kiss (2022) mostram, em contexto internacional, que alunos em séries de avaliações com consequências ("high stakes") apresentam desempenho superior em matemática.

### 2.2 O caso do Ceará: regime de colaboração e alfabetização

O Ceará tornou-se caso emblemático por seu regime de colaboração entre estado e municípios, institucionalizado pelo Programa Alfabetização na Idade Certa (PAIC, Lei estadual 14.026/2007). A literatura documenta ganhos expressivos de alfabetização e aprendizagem associados às políticas cearenses (Costa; Carnoy, 2015; Cruz; Ribeiro; Batista, 2022), com evidência de que a coordenação regional pode produzir resultados comparáveis à coordenação nacional (Segatto; Oliveira; Silva, 2024). Carnoy et al. (2017) mostraram, em análise intranacional, que diferenças estaduais de desempenho no Brasil podem ensinar sobre políticas eficazes — e o Ceará figura entre os casos de maior progresso. (A denominação legal do programa é "Alfabetização na Idade Certa"; a literatura às vezes usa a variação "Aprendizagem na Idade Certa", como no título de Cruz, Ribeiro e Batista, 2022.)

### 2.3 Renda e desempenho: associação transversal vs. temporal

Em análises transversais, municípios mais ricos tendem a apresentar IDEB mais alto (Duarte, 2013; Andrews; Vries, 2012). Contudo, dentro de uma mesma unidade ao longo do tempo, a variação da renda não costuma acompanhar a variação do desempenho — o crescimento do IDEB frequentemente ocorre mesmo onde a renda cresce pouco, como documentado para municípios pobres brasileiros (Andrews; Vries, 2012). Esse contraste entre associação transversal (em níveis) e ausência de associação temporal (dentro das unidades) fundamenta a distinção operacional deste estudo: medir separadamente as duas dimensões na mesma microrregião, em vez de combiná-las em um único coeficiente. A literatura metodológica recomenda, nesse contexto, tratar o número de municípios como o tamanho efetivo da amostra transversal (Cameron; Gelbach; Miller, 2008) e usar procedimentos de inferência robustos a poucos clusters (MacKinnon; Webb, 2017).

## 3. Método

### 3.1 Delimitação e dados

A microrregião do Sertão de Crateús (IBGE 23018) compreende nove municípios: Ararendá (2301257), Crateús (2304103), Independência (2305605), Ipaporanga (2305654), Monsenhor Tabosa (2308609), Nova Russas (2309300), Novo Oriente (2309409), Quiterianópolis (2311264) e Tamboril (2313203). Usaram-se apenas fontes oficiais e auditáveis:

- **INEP — IDEB municipal**, edição 2025 (série 2005–2025), rede Municipal, anos iniciais e finais do ensino fundamental (download.inep.gov.br);
- **IBGE — PIB dos Municípios**, base 2010–2021 (ftp.ibge.gov.br), PIB per capita a preços correntes, **deflacionado para R$ de 2021** pelo IPCA médio anual (IPEA Data, série PRECOS12_IPCA12, dezen/1993 = 100; fonte original IBGE/SNIPC);
- **IBGE — Censo Demográfico 2022**, agregados por município: rendimento nominal médio mensal das pessoas responsáveis (V06004) e mediana (V06006);
- **IBGE — Malha municipal 2023** (geoftp), para os mapas.

Todos os downloads foram registrados em manifesto de proveniência (URL, timestamp, SHA-256), disponível em `data/raw/SOURCE_MANIFEST.json`. O IPCE (IPC Marketing Editora), mencionado na demanda original, é um índice comercial sem acesso público auditável; portanto, usaram-se como proxies oficiais o PIB per capita e a renda do responsável, com essa limitação declarada.

### 3.2 Painel e variáveis

O painel emparelha, por município e ano, o IDEB observado ao log do PIB per capita real defasado em dois anos (IDEB do ano *t* com PIB de *t*−2), suavizando contemporaneidade mecânica. Para a microrregião, o painel de estimação cobre os anos IDEB 2013–2023 (n = 108 observações; 9 municípios × 6 anos × 2 etapas), com missingness de IDEB de 0,5% (1 de 198 pares município-etapa-ano); no Ceará, 1,3%, e no Brasil, 26,2% (o painel nacional de níveis usa os anos disponíveis em lista completa, sem imputação). A defasagem principal de 2 anos foi declarada *a priori*; a Seção 4.6 mostra a robustez para lags 0–4. Para contextualização, repetiram-se as análises para o Ceará (184 municípios) e o Brasil (5.360 municípios).

### 3.3 Hipóteses

- **H1 (níveis):** a correlação transversal entre IDEB e log do PIB per capita real é positiva e estatisticamente discernível (r ≥ 0,3; IC95% sem 0). Estimada na dimensão *entre municípios* (médias temporais, n = 9), com IC95% por bootstrap por cluster.
- **H2 (dentro):** a associação dentro das unidades é fraca ou nula — primeiras diferenças r próximo de zero e coeficiente de efeitos fixos de município×etapa e ano não significativo sob erros clusterizados. A hipótese é avaliada por **não-detecção** (ver 3.5), não por "confirmação" de nulidade.
- **H3 (metas e ganho):** (a) os municípios cumprem as metas projetadas pelo INEP no **mesmo ano de referência** (IDEB observado em *t* ≥ meta em *t*, para *t* ∈ {2011, 2013, 2015, 2017, 2019, 2021}); (b) o ganho educacional 2007→2025 (anos iniciais) não se associa à renda municipal. São proposições separadas e testadas independentemente.

### 3.4 Procedimentos de validação

1. **Between-estimator (dimensão transversal):** média temporal de IDEB e de log do PIB real por município; correlação de Pearson entre as médias (n = 9), com IC95% e p por bootstrap por cluster reamostrando municípios (seed 42, 5.000 réplicas) e jackknife por município.
2. **Correlações em níveis (pooled):** Pearson em todas as observações, com IC95% por bootstrap por cluster (município), 5.000 réplicas (500 quando o número de clusters excede 50). Reportada como complemento, sem reivindicação de tamanho efetivo de amostra transversal.
3. **Primeiras diferenças:** correlação de Pearson das diferenças de primeira ordem dentro de cada município-etapa (p nominal; n pequeno, poder baixo — declarado).
4. **Efeitos fixos:** regressão com efeitos fixos de **município×etapa** (par único) e ano via within-transformation dupla. Reportam-se erros padrão homocedásticos (transparência) e **erros padrão clusterizados por município** (CRVE com correção de pequena amostra, t com G−1 graus de liberdade). Com G = 9, o teste t cluster pode super-rejeitar; reporta-se também o **wild cluster bootstrap** (Rademacher, 9.999 réplicas) sob H0 (Cameron; Gelbach; Miller, 2008; MacKinnon; Webb, 2017).
5. **Validação interna (LOOCV por município):** para cada um dos nove municípios, calcula-se a correlação *dentro* do município retido (12 observações: 6 anos × 2 etapas) e reporta-se a distribuição. Trata-se de estabilidade do sinal *dentro da unidade* (co-tendência temporal) — **não** é réplica da associação transversal entre municípios nem validação externa.
6. **MDES/TOST:** mínimo efeito detectável (poder 80%, α 5%) baseado no erro padrão clusterizado, traduzido em pontos de IDEB por +10% do PIB per capita real; teste de equivalência (TOST) com margem substantiva **SESOI ±0,5 ponto de IDEB** (Lakens; Scheel; Isager, 2018; Bloom, 1995) e reporte de margem ±0,10 como transparência.
7. **Transparência:** scripts `baixar_dados.py`, `analise_crateus.py`, `analise_crateus_r428.py`; saídas completas em `outputs/expanded/resultados_r428.json` e proveniência `provenance_r428.json`; deflator em `data/processed/ipca_medias_anuais.json`.

### 3.5 Critérios de invalidação empírica (falsificabilidade)

Para que as hipóteses sejam testáveis, cada uma tem critérios de rejeição pré-definidos, passíveis de refutação pelos dados:

- **H1 seria rejeitada** se o IC95% do bootstrap por cluster incluísse zero ou se a correlação entre municípios fosse negativa.
- **H2 seria rejeitada** se o coeficiente de efeitos fixos (clusterizado, ou o p do wild cluster bootstrap) fosse estatisticamente discernível de zero ao nível de 5% ou se as primeiras diferenças mostrassem correlação |r| ≥ 0,30 com p < 0,05.
- **H3(a) seria rejeitada** se a maioria dos municípios (≥ 5 de 9) ficasse abaixo da meta do INEP no mesmo ano em algum ciclo de 2011 a 2021; **H3(b) seria rejeitada** se o ganho educacional correlacionasse positiva e significativamente com a renda municipal (r > 0,30; p < 0,05).

A não-detecção (MDES alto, TOST não significativo) é tratada como resultado informativo de poder estatístico, não como confirmação de ausência de efeito: **não-detecção ≠ equivalência** (Lakens; Scheel; Isager, 2018).

## 4. Resultados

### 4.1 Dimensão entre municípios (H1)

Na microrregião, a correlação entre as médias municipais de IDEB e de log do PIB per capita real defasado foi r = −0,24 (IC95% bootstrap por cluster [−0,77; 0,50]; p = 0,52; n = 9 municípios) — sem evidência de associação transversal discernível, e o sinal estimado é inclusive negativo. O jackknife confirma a fragilidade: o r varia de −0,48 (removendo Independência) a +0,02 (removendo Crateús). Na escala Ceará, o between foi r = 0,03 (IC95% [−0,10; 0,15]; p = 0,76; n = 184); no Brasil, r = 0,49 (IC95% [0,47; 0,51]; p < 0,001; n = 5.360). A associação transversal só aparece no agregado nacional, não na microrregião nem no Ceará; H1 **é rejeitada** para a microrregião (Figura 1).

![Figura 1 — Associação em níveis entre IDEB e log do PIB per capita real (Sertão de Crateús, 2013–2023), por etapa.](outputs/figuras/fig_scatter_niveis_micro.png)

**Tabela 1 — Between-estimator (médias municipais) por escala**

| Escala | n (municípios) | r between | IC95% bootstrap | p |
|---|---|---|---|---|
| Microrregião Sertão de Crateús | 9 | −0,24 | [−0,77; 0,50] | 0,52 |
| Ceará | 184 | 0,03 | [−0,10; 0,15] | 0,76 |
| Brasil | 5.360 | 0,49 | [0,47; 0,51] | < 0,001 |

### 4.2 Associação dentro das unidades (H2)

As primeiras diferenças dentro de município-etapa na microrregião foram próximas de zero: r = −0,07 (p = 0,50; n = 90). O coeficiente de efeitos fixos de município×etapa e ano foi β = 2,61 (SE homocedástico 1,28, p nominal 0,046; SE clusterizado 1,88; IC95% cluster [−1,73; 6,95]; p = 0,20 com t(G−1); wild cluster bootstrap p = 0,23; n = 108; 9 clusters): positivo, mas **não discernível de zero sob inferência cluster-robusta**. Para o Ceará, β = −0,0006 (SE cluster 0,14; IC95% [−0,27; 0,27]; p = 0,997). Para o Brasil, β = 0,11 (SE cluster 0,024; IC95% [0,07; 0,16]; p < 0,001): pequeno, embora discernível dado o enorme n. H2 não é rejeitada na microrregião: dentro das unidades, a associação entre variação de renda e variação de IDEB não é discernível — mas, dada a precisão limitada, o correto é **não-detecção**, não "confirmação" de nulidade.

**Tabela 2 — Associação dentro das unidades por escala**

| Escala | 1ª diferenças r (p) | n (1ª dif.) | FE β (IC95% cluster; p cluster) | p wild | n (FE) |
|---|---|---|---|---|---|
| Microrregião Sertão de Crateús | −0,07 (0,50) | 90 | 2,61 ([−1,73; 6,95]; 0,20) | 0,23 | 108 |
| Ceará | −0,01 (0,77) | 1.834 | −0,0006 ([−0,27; 0,27]; 0,997) | — | 2.202 |
| Brasil | 0,04 (< 0,001) | 39.760 | 0,11 ([0,07; 0,16]; < 0,001) | — | 48.695 |

### 4.3 Validação interna: estabilidade do sinal dentro da unidade

A correlação *dentro* de cada município retido (12 observações em níveis) foi positiva em 9/9 municípios (100%), com média r = 0,44 (mediana 0,46; DP 0,20). Os valores variam de 0,08 (Quiterianópolis) a 0,72 (Ararendá). Essa estabilidade reflete **co-tendência temporal** de IDEB e renda dentro da unidade e não replica a associação transversal entre municípios: trata-se de validação **interna**, não de validação externa nem de réplica da dimensão entre unidades (Figuras 2 e 3).

![Figura 2 — Trajetória do IDEB por município, 2007–2025 (anos iniciais e finais).](outputs/figuras/fig_serie_ideb_micro.png)

![Figura 3 — Validação interna: correlação dentro do município retido (r em níveis).](outputs/figuras/fig_loocv_r_teste.png)

**Tabela 3 — Validação interna por município (r dentro da unidade, 12 observações)**

| Município | r dentro | Município | r dentro |
|---|---|---|---|
| Ararendá | 0,72 | Nova Russas | 0,65 |
| Crateús | 0,51 | Novo Oriente | 0,27 |
| Independência | 0,30 | Quiterianópolis | 0,08 |
| Ipaporanga | 0,46 | Tamboril | 0,67 |
| Monsenhor Tabosa | 0,32 | | |

### 4.4 MDES e TOST

Com n municipal de 9 e 108 observações, o mínimo efeito detectável foi de 6,01 pontos de IDEB por unidade de log do PIB real (erro clusterizado, G−1 = 8 graus de liberdade; 3,63 com erro homocedástico) — muito acima de qualquer coeficiente plausível. Traduzido em termos substantivos: o estudo **não detectaria** um efeito de +10% de crescimento do PIB per capita real que movesse o IDEB em cerca de 0,57 ponto. O teste de equivalência (TOST) com margem substantiva ±0,5 ponto não foi significativo (p = 0,85; com margem ±0,10, p = 0,89). Portanto, o correto é declarar **precisão insuficiente**: a amostra não permite afirmar efeito, mas tampouco permite declarar equivalência. Essa é uma limitação central, explicitamente assumida (Lakens; Scheel; Isager, 2018).

### 4.5 H3 — metas do INEP e ganho educacional

**H3(a):** comparando o IDEB observado com a projeção do INEP no **mesmo ano** (2011–2021), os nove municípios cumpriram a meta em 107 de 108 comparações (99,1%); no único desvio, um município, em 2013, não atingiu a meta. Em 2021, todos os 18 pares município-etapa cumpriram a meta; em anos iniciais, todos os nove municípios a atingiram ou superaram (ex.: Crateús, 6,5 vs. meta 5,2; Novo Oriente, 8,9 vs. 5,6). **H3(b):** o ganho médio do IDEB de anos iniciais entre 2007 e 2025 foi de 5,93 pontos, com todos os municípios acima da meta; a correlação entre ganho e renda média do responsável foi r = −0,14 (p = 0,73; n = 9; Figura 4). Não há evidência de que municípios com maior renda tenham tido maior ganho educacional.

![Figura 4 — Ganho de IDEB (2007→2025, anos iniciais) e renda média do responsável (Censo 2022).](outputs/figuras/fig_scatter_ganho_renda.png)

**Tabela 4 — IDEB 2025, ganho 2007–2025 e meta 2021 (anos iniciais)**

| Município | IDEB 2007 | IDEB 2025 | Ganho | Meta 2021 | IDEB 2021 | Atingiu 2021 |
|---|---|---|---|---|---|---|
| Ararendá | 3,4 | 9,8 | 6,4 | 5,3 | 9,5 | Sim |
| Crateús | 3,4 | 8,5 | 5,1 | 5,2 | 6,5 | Sim |
| Independência | 3,7 | 9,8 | 6,1 | 5,2 | 8,7 | Sim |
| Ipaporanga | 3,2 | 9,9 | 6,7 | 6,1 | 6,6 | Sim |
| Monsenhor Tabosa | 2,6 | 9,4 | 6,8 | 4,4 | 6,3 | Sim |
| Nova Russas | 3,0 | 9,7 | 6,7 | 5,1 | 7,2 | Sim |
| Novo Oriente | 3,4 | 9,6 | 6,2 | 5,6 | 8,9 | Sim |
| Quiterianópolis | 3,6 | 6,8 | 3,2 | 5,9 | 5,9 | Sim |
| Tamboril | 3,1 | 9,3 | 6,2 | 4,4 | 6,6 | Sim |

### 4.6 Robustez da defasagem

Para as defasagens 0–4, a correlação pooled (níveis) variou entre r = 0,16 e r = 0,26 na microrregião e as primeiras diferenças oscilaram entre −0,07 e +0,18, sem padrão monotônico — reforçando que nenhuma especificação produz associação temporal discernível na microrregião.

### 4.7 Mapas

Os mapas coropléticos (Figuras 5 e 6) apresentam os dois proxies oficiais de desenvolvimento por município: renda média mensal do responsável (Censo 2022, IBGE) e PIB per capita (2021, IBGE). Crateús, sede regional, destaca-se em ambos os indicadores; os demais municípios concentram-se nas faixas inferiores, retratando a heterogeneidade intra-regional que a análise transversal explora.

![Figura 5 — Renda média mensal do responsável por município (Censo 2022, IBGE).](outputs/mapas/mapa_renda_responsavel_censo2022.png)

![Figura 6 — PIB per capita por município (2021, IBGE).](outputs/mapas/mapa_pib_per_capita_2021.png)

## 5. Discussão

Os resultados indicam que, no Sertão de Crateús, **não se sustenta a hipótese de associação renda–desempenho em nenhuma das duas dimensões testadas**: entre municípios, a correlação estimada é negativa e não discernível de zero (r = −0,24; IC95% [−0,77; 0,50]; Figura 1); dentro dos municípios, as primeiras diferenças são próximas de zero e os efeitos fixos não são discerníveis de zero sob erros clusterizados (β = 2,61; IC95% [−1,73; 6,95]; p = 0,20; Figuras 2 e 3). A precisão do estudo é limitada (MDES ≈ 6,0; TOST não significativo mesmo com margem substantiva), de modo que a leitura correta é de **precisão insuficiente para detectar efeitos plausíveis**, e não de prova de ausência de efeito.

Dois pontos merecem destaque. Primeiro, a ausência de associação transversal discernível na microrregião — ao contrário do agregado nacional (r = 0,49 no Brasil) — sugere que, em contextos de pobreza estrutural com política educacional coordenada, a variação de renda entre municípios pequenos explica pouco da variação de desempenho. Segundo, o crescimento educacional não acompanhou a renda: municípios pobres da microrregião alcançaram IDEB 2025 elevado (até 9,9 pontos) e todos cumpriram as metas do INEP no ano de referência — o que é compatível com a literatura sobre políticas educacionais cearenses (PAIC, regime de colaboração, alfabetização na idade certa), que associa os ganhos a fatores institucionais e pedagógicos, e não à variação econômica local (Costa; Carnoy, 2015; Cruz; Ribeiro; Batista, 2022; Segatto; Oliveira; Silva, 2024).

As limitações são explícitas: (i) n municipal de 9 e 108 observações implica poder estatístico baixo (MDES ≈ 6,0 com erro clusterizado), tornando a ausência de associação temporal e transversal uma **não-detecção** e não uma prova de ausência; (ii) com G = 9, o teste t cluster pode super-rejeitar — daí o wild cluster bootstrap como robustez (MacKinnon; Webb, 2017); (iii) o PIB municipal e a renda do responsável são proxies do desenvolvimento local — o IPCE original não é auditável; (iv) não há pretensão causal; (v) os efeitos fixos controlam fatores invariantes no tempo e choques comuns por ano, mas não outros confundidores variáveis; (vi) a comparação das metas do INEP é descritiva e não controla por tendências subjacentes.

## 6. Considerações finais

Este estudo responde à pergunta de pesquisa com evidência associativa subnacional: no Sertão de Crateús, a relação entre renda e desempenho escolar **não é discernível nem entre nem dentro dos municípios** — a associação transversal observada no agregado nacional não se reproduz na microrregião, e a variação temporal da renda não acompanha a variação do desempenho. Adicionalmente, os dados oficiais mostram que os nove municípios atingiram ou superaram as metas projetadas pelo INEP na grande maioria das 108 comparações município-etapa-ano (99,1%; único desvio em Ipaporanga, 2013) — e, em 2021, todos os 18 pares cumpriram a meta —, com ganhos médios de cerca de seis pontos no período 2007–2025 e IDEB 2025 elevado mesmo em municípios de baixa renda. A ausência de associação entre ganho educacional e renda sugere que fatores de política educacional — e não a variação econômica — estão associados à trajetória observada, em linha com a literatura do Ceará. Recomenda-se, para estudos futuros, ampliar o painel para todas as microrregiões cearenses e estaduais (aumentando o número efetivo de unidades), incorporar controles de política (PAIC, ICMS educacional) e utilizar estratégias quase-experimentais para testar mecanismos causais específicos.

## Referências

AFONSO, A. J. Para uma concetualização alternativa de accountability em educação. *Educação & Sociedade*, Campinas, v. 33, n. 119, p. 471–484, 2012. https://doi.org/10.1590/S0101-73302012000200008

ANDREWS, C. W.; VRIES, M. S. de. Pobreza e municipalização da educação: análise dos resultados do IDEB (2005-2009). *Cadernos de Pesquisa*, São Paulo, v. 42, n. 147, p. 826–847, 2012. https://doi.org/10.1590/S0100-15742012000300010

BLOOM, H. S. Minimum detectable effects: a simple way to report the statistical power of experimental designs. *Evaluation Review*, Thousand Oaks, v. 19, n. 5, p. 547–556, 1995. https://doi.org/10.1177/0193841X9501900504

BRUNELLO, G.; KISS, D. Math scores in high stakes grades. *Economics of Education Review*, v. 87, 102219, 2022. https://doi.org/10.1016/j.econedurev.2021.102219

CAMERON, A. C.; GELBACH, J. B.; MILLER, D. L. Bootstrap-based improvements for inference with clustered errors. *The Review of Economics and Statistics*, Cambridge, MA, v. 90, n. 3, p. 414–427, 2008. https://doi.org/10.1162/rest.90.3.414

CARNOY, M.; MAROTTA, L.; LOUZANO, P.; KHAVENSON, T.; GUIMARÃES, F. R. F.; CARNAUBA, F. Intranational comparative education: what state differences in student achievement can teach us about improving education — the case of Brazil. *Comparative Education Review*, Chicago, v. 61, n. 4, p. 726–759, nov. 2017. https://doi.org/10.1086/693981

CITO, L.; MARÔCO, J. Beyond the average: mapping educational inequality in Brazil with PISA 2022. *Large-scale Assessments in Education*, v. 14, art. 30, 2026. https://doi.org/10.1186/s40536-026-00302-0

COSTA, L. O.; CARNOY, M. The effectiveness of an early-grade literacy intervention on the cognitive achievement of Brazilian students. *Educational Evaluation and Policy Analysis*, v. 37, n. 4, p. 567–590, 2015. https://doi.org/10.3102/0162373715571437

CRUZ, M. C. M. T.; RIBEIRO, V. M.; BATISTA, J. M. Contexto de implementação do Programa de Aprendizagem na Idade Certa (PAIC). *Revista Ibero-Americana de Estudos em Educação*, Araraquara, v. 17, n. esp. 3, p. 2405–2432, 2022. https://doi.org/10.21723/riaee.v17iesp.3.16719. [Nota: o título do artigo usa a variação "Aprendizagem"; a denominação legal do programa é "Alfabetização na Idade Certa" (Lei estadual 14.026/2007).]

DUARTE, N. de S. O impacto da pobreza no Ideb: um estudo multinível. *Revista Brasileira de Estudos Pedagógicos*, Brasília, DF, v. 94, n. 237, p. 343–363, 2013. https://doi.org/10.1590/S2176-66812013000200002

HANUSHEK, E. A.; WOESSMANN, L. *The Knowledge Capital of Nations: education and the economics of growth*. Cambridge, MA: MIT Press, 2015. https://doi.org/10.7551/mitpress/9780262029179.001.0001

LACRUZ, A. J.; AMÉRICO, B. L.; CARNIEL, F. Indicadores de qualidade na educação: análise discriminante dos desempenhos na Prova Brasil. *Revista Brasileira de Educação*, Rio de Janeiro, v. 24, e240002, p. 1–26, 2019. https://doi.org/10.1590/S1413-24782019240002

LAKENS, D.; SCHEEL, A. M.; ISAGER, P. M. Equivalence testing for psychological research: a tutorial. *Advances in Methods and Practices in Psychological Science*, Thousand Oaks, v. 1, n. 2, p. 259–269, 2018. https://doi.org/10.1177/2515245918770963

MACKINNON, J. G.; WEBB, M. D. Wild bootstrap inference for wildly different cluster sizes. *Journal of Applied Econometrics*, Chichester, v. 32, n. 2, p. 233–254, 2017. https://doi.org/10.1002/jae.2508

SCHNEIDER, M. P.; NARDI, E. L. O IDEB e a construção de um modelo de accountability na educação básica brasileira. *Revista Portuguesa de Educação*, Braga, v. 27, n. 1, p. 7–28, 2014. https://doi.org/10.21814/rpe.4295

SEGATTO, C. I.; OLIVEIRA, K. de; SILVA, A. L. N. da. Os limites do PNE (2014-2024) no regime de colaboração. *Estudos em Avaliação Educacional*, São Paulo, v. 35, e10549, 2024. https://doi.org/10.18222/eae.v35.10549

SOARES, J. F.; XAVIER, F. P. Pressupostos educacionais e estatísticos do Ideb. *Educação & Sociedade*, Campinas, v. 34, n. 124, p. 903–923, 2013. https://doi.org/10.1590/S0101-73302013000300013

## Apêndice A — Proveniência e reprodutibilidade

- Scripts: `scripts/baixar_dados.py`, `scripts/analise_crateus.py`, `scripts/analise_crateus_r428.py`, `scripts/mapa_crateus.py`, `scripts/graficos_crateus.py`.
- Manifesto de fontes (URL, timestamp, SHA-256): `data/raw/SOURCE_MANIFEST.json`.
- Deflator: `data/processed/ipca_medias_anuais.json` (IPEA Data, série PRECOS12_IPCA12; fonte original IBGE/SNIPC; fator 2021/ano).
- Resultados completos: `outputs/expanded/resultados_r428.json`; proveniência computacional: `outputs/expanded/provenance_r428.json`.
- Figuras: `outputs/figuras/` (scatter de níveis, séries temporais, LOOCV interno, ganho×renda) e `outputs/mapas/` (renda do responsável, PIB per capita).
- Fontes: INEP — IDEB municipal, edição 2025 (https://download.inep.gov.br/ideb/resultados/divulgacao_anos_iniciais_municipios_2025.zip e _anos_finais_); IBGE — PIB dos Municípios 2021 (https://ftp.ibge.gov.br/Pib_Municipios/2021/base/base_de_dados_2010_2021_xlsx.zip); IBGE — Censo 2022, rendimento do responsável (https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/.../Agregados_por_municipios_renda_responsavel_BR_20260508_csv.zip); IBGE — malha 2023 (https://geoftp.ibge.gov.br/.../CE_Municipios_2023.zip).
- Declaração de limites: evidência associativa; n municipal de 9; MDES ≈ 6,0 (cluster); não-detecção ≠ equivalência; IPCE substituído por proxies oficiais; G=9 com wild cluster bootstrap (MacKinnon; Webb, 2017).
