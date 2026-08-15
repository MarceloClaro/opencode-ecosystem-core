# Desenvolvimento educacional em microrregião do Semiárido cearense: o padrão associativo entre desempenho escolar e renda no Sertão de Crateús

**Autor:** Marcelo Claro Laranjeira — ORCID: https://orcid.org/0000-0001-8996-2887

---

## Resumo

Este estudo testa, na microrregião do Sertão de Crateús (Ceará; nove municípios), a associação entre desempenho escolar (IDEB) e renda municipal, entre e dentro das unidades. Com dados oficiais (INEP 2005–2025; IBGE, PIB real deflacionado pelo IPCA; Censo 2022) e inferência conservadora (bootstrap por cluster; efeitos fixos com erros clusterizados e correção de pequena amostra; *wild cluster bootstrap*), os resultados indicam: ausência de associação transversal discernível (r = −0,24; IC95% [−0,77; 0,50]); efeitos fixos não discerníveis de zero (β = 2,61; p = 0,20; p *wild* = 0,23), com precisão insuficiente (MDES ≈ 6,0); 107 de 108 metas do INEP cumpridas no mesmo ano de referência (99,1%), com ganho médio de 5,93 pontos (2007–2025) sem associação com a renda (r = −0,14). Conclui-se que fatores de política educacional coordenada, e não a variação econômica local, estão associados ao avanço observado.

**Palavras-chave:** IDEB; renda; microrregião; Ceará; painel municipal; efeitos fixos; *wild cluster bootstrap*.

---

## Abstract

This study tests, in the Sertão de Crateús microregion (Ceará, Brazil; nine municipalities), the association between school performance (IDEB) and municipal income, across and within units. Using official data (INEP 2005–2025; IBGE real GDP deflated by the IPCA; 2022 Census) and conservative inference (cluster bootstrap; fixed effects with clustered errors and small-sample correction; wild cluster bootstrap), results indicate: no discernible cross-sectional association (r = −0.24; 95% CI [−0.77, 0.50]); fixed effects not discernible from zero (β = 2.61; p = 0.20; wild p = 0.23), with insufficient precision (MDES ≈ 6.0); 107 of 108 INEP targets met in the same reference year (99.1%), with a mean gain of 5.93 points (2007–2025) unrelated to income (r = −0.14). Coordinated education policies, rather than local economic variation, are associated with the observed progress.

**Keywords:** IDEB; income; microregion; Ceará; municipal panel; fixed effects; wild cluster bootstrap.

---

## 1. Introdução

A relação entre renda e desempenho educacional é um dos temas mais persistentes da pesquisa em educação comparada. Hanushek e Woessmann (2015) demonstraram que o "capital de conhecimento" de uma nação — medido por habilidades cognitivas, e não apenas por anos de escolaridade — associa-se fortemente ao crescimento econômico de longo prazo. No Brasil, análises de avaliação em larga escala mostram desigualdades substanciais associadas ao nível socioeconômico (Cito; Marôco, 2026), e estudos multiníveis documentam o impacto associativo da pobreza sobre o IDEB (Duarte, 2013; Andrews; Vries, 2012).

Essa literatura, contudo, concentra-se majoritariamente em duas escalas: a nacional, que compara países ou estados, e a de escolas ou alunos, que modela o efeito do nível socioeconômico individual. Entre essas escalas há uma lacuna: a escala **municipal**, em que a unidade de política pública é o próprio ente federado responsável pela oferta da educação básica. No Brasil, a Constituição de 1988 e a municipalização do ensino fundamental tornaram os municípios atores centrais da política educacional; compreender se a renda municipal associa-se ao desempenho escolar nessa escala é, portanto, uma questão diretamente relevante para o desenho de políticas locais. O IDEB, ao combinar fluxo e proficiência e atribuir metas bianuais, criou um indicador comum e comparável que permite examinar essa associação com dados oficiais, mas também produziu uma estrutura de incentivos que a literatura analisa criticamente (Afonso, 2012; Schneider; Nardi, 2014; Lacruz; Américo; Carniel, 2019).

Uma distinção analítica frequentemente negligenciada separa dois tipos de associação entre renda e desempenho escolar: a **transversal** (entre unidades: municípios mais ricos tendem a ter IDEB mais alto) e a **temporal** (dentro de uma mesma unidade: quando a renda de um município cresce, seu IDEB cresce?). A primeira é amplamente documentada; a segunda é mais incerta e raramente testada em pequenas escalas. Para o Semiárido brasileiro, onde a pobreza é estrutural e a política educacional estadual (regime de colaboração, alfabetização na idade certa) produziu ganhos notáveis de aprendizagem, essa distinção tem implicações práticas: se a associação for apenas transversal, políticas de crescimento econômico local não deveriam ser tratadas como condição necessária para o avanço educacional.

A microrregião do Sertão de Crateús (IBGE 23018), no Ceará, oferece um contexto privilegiado para esse teste: nove municípios pequenos, de baixa renda, sob a mesma coordenação estadual de políticas educacionais, com série histórica completa do IDEB (2005–2025) e indicadores municipais oficiais de renda (PIB municipal e Censo Demográfico 2022). Além disso, trata-se de uma região do Semiárido cuja pobreza é estrutural e persistente, o que torna o contraste entre os resultados educacionais recentes — entre os mais altos do país em anos iniciais — e o nível de renda local um fenômeno digno de investigação empírica sistemática. O presente estudo contribui ao testar explicitamente as duas dimensões (entre e dentro) na mesma unidade de análise, com protocolo inferencial conservador e adequado ao pequeno número de unidades.

A pergunta de pesquisa que orienta o estudo é, portanto: **no Sertão de Crateús, a renda municipal associa-se ao desempenho escolar, entre municípios e dentro de cada município ao longo do tempo?** Respondê-la importa para a política pública em duas frentes. Primeira, porque municípios pobres do Semiárido são frequentemente tratados como "desafiadores" do ponto de vista educacional, e a evidência sobre o Ceará sugere que a política coordenada pode superar o determinismo socioeconômico — mas essa evidência raramente é testada na escala municipal com painel e protocolo inferencial explícito. Segunda, porque a interpretação dos resultados do IDEB em municípios pobres depende de saber se o nível de renda é um condicionante intransponível ou apenas um correlato: se a associação for fraca ou nula na dimensão temporal, gestores podem tratar o avanço educacional como objetivo alcançável no horizonte de poucos ciclos de política, independentemente do ciclo econômico local.

**Pergunta de pesquisa (RQ):** no Sertão de Crateús, a associação entre renda municipal e desempenho escolar no IDEB é transversal (entre municípios), temporal (dentro dos municípios), ou ambas? Em particular: (a) municípios com maior renda têm IDEB mais alto? (b) variações de renda dentro do município acompanham variações de IDEB? (c) o ganho educacional observado na região depende da renda municipal, e os municípios cumprem as metas pactuadas pelo INEP?

Deliberadamente, este estudo não testa causalidade: trata-se de evidência associativa, com descrição explícita dos limites de inferência. As hipóteses operacionalizadas na Seção 3 respondem diretamente à RQ.

## 2. Fundamentação

### 2.1 O IDEB como indicador e política

O IDEB, criado em 2007, combina fluxo escolar e proficiência no SAEB, atribuindo metas bianuais às escolas públicas (Soares; Xavier, 2013; Schneider; Nardi, 2014). Em sua formulação original, o indicador integra em um único número a dimensão de acesso (aprovação) e a dimensão de aprendizagem (proficiência padronizada), o que permite acompanhar a evolução de cada escola, município e estado em relação a metas projetadas pelo INEP a partir do desempenho inicial. Essa arquitetura faz do IDEB, simultaneamente, instrumento de diagnóstico e de responsabilização: as metas funcionam como balizas temporais explícitas e publicamente verificáveis. A literatura critica seu caráter de accountability gerencial, apontando riscos de estreitamento do currículo e de pressão por resultados (Afonso, 2012), mas reconhece sua função mobilizadora, ao dar visibilidade ao desempenho e incentivar a ação dos gestores (Lacruz; Américo; Carniel, 2019). Brunello e Kiss (2022) mostram, em contexto internacional, que alunos em séries de avaliações com consequências ("high stakes") apresentam desempenho superior em matemática — evidência compatível com a hipótese de que a combinação de medida pública e meta explícita altera o comportamento dos atores escolares.

### 2.2 O caso do Ceará: regime de colaboração e alfabetização

O Ceará tornou-se caso emblemático por seu regime de colaboração entre estado e municípios, institucionalizado pelo Programa Alfabetização na Idade Certa (PAIC, Lei estadual 14.026/2007). O programa articula formação de professores, material didático, acompanhamento pedagógico e avaliação externa anual, com coordenação estadual e adesão municipal formalizada em convênios; sua lógica é a da intervenção coordenada sobre o início da escolarização, quando o aprendizado da leitura e da escrita define as trajetórias subsequentes. A literatura documenta ganhos expressivos de alfabetização e aprendizagem associados às políticas cearenses (Costa; Carnoy, 2015; Cruz; Ribeiro; Batista, 2022), com evidência de que a coordenação regional pode produzir resultados comparáveis à coordenação nacional (Segatto; Oliveira; Silva, 2024). Carnoy et al. (2017) mostraram, em análise intranacional, que diferenças estaduais de desempenho no Brasil podem ensinar sobre políticas eficazes — e o Ceará figura entre os casos de maior progresso, com avanços concentrados nos anos iniciais e nas redes municipais. Esse quadro sugere que, no contexto cearense, o desempenho educacional pode estar associado a fatores institucionais e pedagógicos mais do que à variação econômica local — hipótese que o presente estudo permite examinar de forma direta na escala municipal. (A denominação legal do programa é "Alfabetização na Idade Certa"; a literatura às vezes usa a variação "Aprendizagem na Idade Certa", como no título de Cruz, Ribeiro e Batista, 2022.)

### 2.3 Renda e desempenho: associação transversal vs. temporal

Em análises transversais, municípios mais ricos tendem a apresentar IDEB mais alto (Duarte, 2013; Andrews; Vries, 2012). Contudo, dentro de uma mesma unidade ao longo do tempo, a variação da renda não costuma acompanhar a variação do desempenho — o crescimento do IDEB frequentemente ocorre mesmo onde a renda cresce pouco, como documentado para municípios pobres brasileiros (Andrews; Vries, 2012). Esse contraste entre associação transversal (em níveis) e ausência de associação temporal (dentro das unidades) fundamenta a distinção operacional deste estudo: medir separadamente as duas dimensões na mesma microrregião, em vez de combiná-las em um único coeficiente. A literatura metodológica recomenda, nesse contexto, tratar o número de municípios como o tamanho efetivo da amostra transversal (Cameron; Gelbach; Miller, 2008) e usar procedimentos de inferência robustos a poucos clusters (MacKinnon; Webb, 2017): quando há poucas unidades, os erros padrão convencionais superestimam a precisão, e a inferência assintótica em número de unidades deixa de ser válida — daí a necessidade de bootstrap por cluster e de correções de pequena amostra, adotadas neste estudo e detalhadas na Seção 3.

Uma ressalva metodológica importante é que o desenho aqui adotado é **observacional e associativo**: não há variação exógena de renda, e o termo "efeito" é usado apenas em sentido estatístico (coeficiente de regressão). A comparação entre escalas (microrregião, Ceará, Brasil) funciona como triangulação descritiva: se a associação transversal for uma regularidade robusta, ela deveria aparecer também dentro de contextos homogêneos; se aparecer apenas no agregado, sua interpretação como relação causal entre renda e desempenho fica enfraquecida. É nesse sentido que a ausência de associação na microrregião e no Ceará é informativa, ainda que não prove a irrelevância da renda: ela delimita o escopo em que o padrão agregado nacional opera.

## 3. Método

### 3.1 Delimitação e dados

A microrregião do Sertão de Crateús (IBGE 23018) compreende nove municípios: Ararendá (2301257), Crateús (2304103), Independência (2305605), Ipaporanga (2305654), Monsenhor Tabosa (2308609), Nova Russas (2309300), Novo Oriente (2309409), Quiterianópolis (2311264) e Tamboril (2313203). Usaram-se apenas fontes oficiais e auditáveis:

- **INEP — IDEB municipal**, edição 2025 (série 2005–2025), rede Municipal, anos iniciais e finais do ensino fundamental (download.inep.gov.br);
- **IBGE — PIB dos Municípios**, base 2010–2021 (ftp.ibge.gov.br), PIB per capita a preços correntes, **deflacionado para R$ de 2021** pelo IPCA médio anual (IPEA Data, série PRECOS12_IPCA12, dezen/1993 = 100; fonte original IBGE/SNIPC);
- **IBGE — Censo Demográfico 2022**, agregados por município: rendimento nominal médio mensal das pessoas responsáveis (V06004) e mediana (V06006);
- **IBGE — Malha municipal 2023** (geoftp), para os mapas.

Todos os downloads foram registrados em manifesto de proveniência (URL, timestamp, SHA-256), disponível em `data/raw/SOURCE_MANIFEST.json`. O IPCE (IPC Marketing Editora), mencionado na demanda original, é um índice comercial sem acesso público auditável; portanto, usaram-se como proxies oficiais o PIB per capita e a renda do responsável, com essa limitação declarada.

### 3.2 Painel e variáveis

**Variável de resultado — IDEB:** nota do IDEB municipal por etapa (anos iniciais e finais do ensino fundamental), rede pública municipal, edições bienais de 2005 a 2025. No painel de estimação da dimensão dentro, usam-se as edições cujo PIB defasado em dois anos existe (IDEB 2013–2023, emparelhado ao PIB 2011–2021), totalizando 6 ondas.

**Variável explicativa — log do PIB per capita real:** logaritmo natural do PIB per capita municipal a preços correntes (IBGE, base 2010–2021), deflacionado para R$ de 2021. O deflator foi construído a partir da série de IPCA médio anual (IPEA Data, série PRECOS12_IPCA12, dezen/1993 = 100; fonte original IBGE/SNIPC), com 1.680 registros mensais; para cada ano, calculou-se a média anual do índice e o fator de conversão fator_ano = IPCA_2021 / IPCA_ano. O logaritmo é usado por simetria com a literatura e por interpretação elasticidade: uma variação de 10% no PIB per capita real corresponde a aproximadamente 0,095 unidades de log.

**Variável de contexto — renda do responsável:** rendimento nominal médio mensal das pessoas responsáveis pelo domicílio (Censo Demográfico 2022, variáveis V06004/V06006), usada exclusivamente na análise do ganho educacional (H3b) e nos mapas, por ser a única fonte censitária de renda domiciliar disponível para todos os nove municípios no período recente.

**Painel de estimação:** emparelha, por município e ano, o IDEB observado ao log do PIB per capita real defasado em dois anos (IDEB do ano *t* com PIB de *t*−2), suavizando contemporaneidade mecânica — o PIB do ano em que a prova foi aplicada não pode influenciar o desempenho já ocorrido, e uma defasagem de dois anos aproxima a renda do período em que a coorte estudou. Para a microrregião, o painel de estimação cobre os anos IDEB 2013–2023 (n = 108 observações; 9 municípios × 6 anos × 2 etapas), com missingness de IDEB de 0,5% (1 de 198 pares município-etapa-ano); no Ceará, 1,3%, e no Brasil, 26,2% (o painel nacional de níveis usa os anos disponíveis em lista completa, sem imputação). A defasagem principal de 2 anos foi declarada *a priori*; a Seção 4.6 mostra a robustez para lags 0–4. Para contextualização, repetiram-se as análises para o Ceará (184 municípios) e o Brasil (5.360 municípios).

### 3.3 Hipóteses

- **H1 (níveis):** a correlação transversal entre IDEB e log do PIB per capita real é positiva e estatisticamente discernível (r ≥ 0,3; IC95% sem 0). Estimada na dimensão *entre municípios* (médias temporais, n = 9), com IC95% por bootstrap por cluster.
- **H2 (dentro):** a associação dentro das unidades é fraca ou nula — primeiras diferenças r próximo de zero e coeficiente de efeitos fixos de município×etapa e ano não significativo sob erros clusterizados. A hipótese é avaliada por **não-detecção** (ver 3.5), não por "confirmação" de nulidade.
- **H3 (metas e ganho):** (a) os municípios cumprem as metas projetadas pelo INEP no **mesmo ano de referência** (IDEB observado em *t* ≥ meta em *t*, para *t* ∈ {2011, 2013, 2015, 2017, 2019, 2021}); (b) o ganho educacional 2007→2025 (anos iniciais) não se associa à renda municipal. São proposições separadas e testadas independentemente.

### 3.4 Procedimentos de validação

A inferência estatística deste estudo adota, deliberadamente, procedimentos adequados a um pequeno número de unidades (G = 9). Em primeiro lugar, todos os intervalos e valores-p reportados para a dimensão transversal e para o painel da microrregião usam **bootstrap por cluster**, reamostrando municípios (e não observações individuais), com 5.000 réplicas e seed fixa 42 para reprodutibilidade: cada réplica sorteia G municípios com reposição e recalcula a estatística sobre a amostra sorteada; o intervalo é obtido pelos percentis 2,5 e 97,5 da distribuição bootstrap, e o valor-p, pela proporção de réplicas em que o sinal da estatística se inverte em relação ao observado. Esse procedimento preserva a correlação intracluster do painel, que o bootstrap ingênuo por observação ignoraria (Cameron; Gelbach; Miller, 2008).

Em segundo lugar, o coeficiente de efeitos fixos é inferido com **erros padrão clusterizados por município** (CRVE, "sandwich"), corrigidos para pequena amostra e comparados à distribuição t com **G−1 = 8 graus de liberdade**, em lugar da aproximação assintótica em número de observações (n = 108). Com tão poucos clusters, essa aproximação t é necessária, mas ainda pode super-rejeitar; por isso, o valor-p decisivo é o do **wild cluster bootstrap sob H0** (Rademacher, 9.999 réplicas), que impõe a restrição nula ao reamostrar os sinais dos resíduos restritos por cluster e recalcular o coeficiente em cada réplica, fornecendo um valor-p exato por permutação aproximada (MacKinnon; Webb, 2017). Os erros padrão homocedásticos são reportados apenas como transparência, não como base de decisão.

Em terceiro lugar, o poder do estudo é dimensionado de forma explícita: o **mínimo efeito detectável** (MDES; Bloom, 1995) é derivado do erro padrão clusterizado com poder de 80% e α = 5%, e o **teste de equivalência** (TOST) compara a estimativa a uma margem substantiva (SESOI) de ±0,5 ponto de IDEB, realizando dois testes unicaudais com as hipóteses trocadas e exigindo que ambos rejeitem para declarar equivalência (Lakens; Scheel; Isager, 2018). Esse protocolo impede que a ausência de significância seja lida como prova de nulidade: sem poder e sem equivalência, o resultado é classificado como precisão insuficiente. As etapas aplicadas a cada estimador são:

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

Substantivamente, esse resultado indica que, dentro de um conjunto de municípios semelhantes quanto a pobreza, localização e política estadual, o nível de renda não discrimina o desempenho: há municípios pobres com IDEB muito acima da média nacional e municípios relativamente mais ricos da região sem desempenho superior. A associação nacional, embora real, parece refletir principalmente a comparação entre unidades muito heterogêneas — um fenômeno de composição (ecológico) mais do que um mecanismo individual transposto para a escala municipal. Esse é um ponto central para a interpretação: a escala de análise muda a leitura da relação renda–desempenho.

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

O cumprimento quase universal das metas projetadas — em uma região de pobreza estrutural — é um resultado substantivo em si. As metas do INEP foram desenhadas como projeções de convergência (Soares; Xavier, 2013): cada unidade deveria progredir de seu ponto de partida em direção à média dos países da OCDE. Que nove municípios pequenos do Semiárido tenham superado sistematicamente suas próprias projeções indica um ritmo de melhora acima do programado institucionalmente, e não apenas "cumprimento de tabela". O ganho médio de 5,93 pontos em 18 anos equivale a mais de um terço da escala do IDEB (0–10), o que situa a microrregião entre as trajetórias mais aceleradas do país — sem associação com a renda local, como mostra a correlação nula do ganho com a renda do responsável.

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

A leitura em duas dimensões ajuda a conciliar resultados que, isolados, pareceriam contraditórios. A associação transversal no Brasil (r = 0,49) reproduz o que a literatura documenta há décadas: municípios e estados mais ricos tendem a ter melhor desempenho médio (Duarte, 2013; Andrews; Vries, 2012). Mas esse padrão, quando observado no interior de um único estado pobre, desaparece: no Ceará o between foi r = 0,03, e na microrregião, r = −0,24. Isso indica que a associação nacional é, em grande parte, um artefato de comparação entre contextos muito heterogêneos (estados ricos do Sul e Sudeste versus municípios pobres do Semiárido), e não uma regularidade que se mantenha quando se compara apenas unidades semelhantes. A ausência de associação temporal dentro das unidades reforça a mesma conclusão: mesmo quando o PIB municipal varia, o IDEB não acompanha — o que é consistente com a hipótese de que os determinantes do desempenho estão mais próximos da política educacional (formação, materiais, gestão, avaliação) do que do ciclo econômico local.

### 5.3 Limitações e agenda de pesquisa

As limitações são explícitas e determinam o alcance das conclusões. (i) **Poder estatístico:** n municipal de 9 e 108 observações implica poder baixo (MDES ≈ 6,0 com erro clusterizado), de modo que a ausência de associação temporal e transversal é uma **não-detecção** e não uma prova de ausência; a única afirmação segura é a de precisão insuficiente para efeitos plausíveis. (ii) **Número de clusters:** com G = 9, o teste t cluster pode super-rejeitar — daí o wild cluster bootstrap como robustez (MacKinnon; Webb, 2017); ainda assim, a distribuição bootstrap é discreta e o valor-p tem granularidade própria desse contexto. (iii) **Proxies de desenvolvimento:** o PIB municipal e a renda do responsável são proxies imperfeitas do desenvolvimento local; o IPCE (Índice de Pobreza, Ceará) original não é auditável publicamente, o que motivou a escolha de fontes oficiais verificáveis. (iv) **Causalidade:** não há pretensão causal; os efeitos fixos controlam fatores invariantes no tempo e choques comuns por ano, mas não outros confundidores variáveis no tempo (mudanças de gestão, transferências federais, oferta de creches). (v) **Metas do INEP:** a comparação com as metas é descritiva e não controla por tendências subjacentes nem por comportamento estratégico de municípios. (vi) **Generalização:** os resultados se referem a uma microrregião de 9 municípios; sua validade externa para o Semiárido ou o país deve ser estabelecida por replicação. Para a agenda de pesquisa, recomenda-se ampliar o painel para todas as microrregiões cearenses e estaduais (aumentando o número efetivo de unidades e, portanto, o poder), incorporar controles de política (PAIC, ICMS educacional, FUNDEB per capita) e utilizar estratégias quase-experimentais — descontinuidades nas regras de repasse ou no sorteio de programas — para testar mecanismos causais específicos.

## 6. Considerações finais

Este estudo responde à pergunta de pesquisa com evidência associativa subnacional: no Sertão de Crateús, a relação entre renda e desempenho escolar **não é discernível nem entre nem dentro dos municípios** — a associação transversal observada no agregado nacional não se reproduz na microrregião, e a variação temporal da renda não acompanha a variação do desempenho. Adicionalmente, os dados oficiais mostram que os nove municípios atingiram ou superaram as metas projetadas pelo INEP na grande maioria das 108 comparações município-etapa-ano (99,1%; único desvio em Ipaporanga, 2013) — e, em 2021, todos os 18 pares cumpriram a meta —, com ganhos médios de cerca de seis pontos no período 2007–2025 e IDEB 2025 elevado mesmo em municípios de baixa renda. A ausência de associação entre ganho educacional e renda sugere que fatores de política educacional — e não a variação econômica — estão associados à trajetória observada, em linha com a literatura do Ceará. Recomenda-se, para estudos futuros, ampliar o painel para todas as microrregiões cearenses e estaduais (aumentando o número efetivo de unidades), incorporar controles de política (PAIC, ICMS educacional) e utilizar estratégias quase-experimentais para testar mecanismos causais específicos.

As implicações práticas decorrentes são diretamente utilizáveis por gestores municipais e estaduais. Primeiro, o nível de renda municipal não deve ser tratado como destino: a trajetória da microrregião mostra que municípios pobres podem sustentar ganhos educacionais acelerados e cumprir metas institucionais quando há coordenação de política (formação, materiais, avaliação, regime de colaboração). Segundo, indicadores de desempenho baseados exclusivamente em proficiência e fluxo, embora necessários, são insuficientes para diagnosticar desigualdades de contexto; a leitura conjunta com indicadores socioeconômicos (como aqui feito com o PIB e a renda do responsável) evita atribuições equivocadas de sucesso ou fracasso. Terceiro, a distinção entre associação transversal e temporal deve orientar o monitoramento: metas de convergência fazem sentido porque o avanço temporal é alcançável mesmo onde o nível socioeconômico é adverso — desde que a política educacional atue de forma contínua e coordenada, como no caso cearense (Costa; Carnoy, 2015; Carnoy et al., 2017).

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
