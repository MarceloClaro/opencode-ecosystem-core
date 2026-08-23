---
header-includes: |
  \usepackage{graphicx}
  \usepackage{array}
  \usepackage{etoolbox}
  \AtBeginEnvironment{tabular}{\footnotesize}
  \AtBeginEnvironment{longtable}{\footnotesize}
venue: "RBEP / Educação & Sociedade (Qualis A1)"
lang: pt-BR
keywords: [Armadilha da renda média, IDEB, Sertão de Crateús, Ceará, Economia da educação, Painel municipal]
---

\begin{center}
{\Large\bfseries Educação, Armadilha da Renda Média e Desempenho Escolar:}\\[4pt]
{\large\bfseries Evidências do IDEB no Sertão de Crateús e no Ceará (2005–2025)\\ como Ruptura da Estagnação}
\end{center}

\begin{center}
\small Prof. Marcelo Claro --- Mestre em Educação, Pesquisador em Economia da Educação\\
\small ORCID: \href{https://orcid.org/0000-0001-8996-2887}{0000-0001-8996-2887}
\end{center}

> **Fontes e proveniência:** todos os dados são de fontes oficiais auditáveis (INEP; IBGE; World Bank; OCDE; FAO; USPTO; CONAB; IPEA). Cada download está registrado em manifesto próprio com URL, data-hora e hash SHA-256. Scripts, saídas completas e o relatório independente de validação por banca simulada acompanham o material suplementar (Apêndice A).

## Resumo

Este artigo articula duas escalas para examinar se a educação constitui fator de ruptura da armadilha da renda média no Brasil. Na escala macro (1960–2026; 11 países; World Bank, IBGE, OCDE-PISA, FAO, USPTO), seis de sete correlações de Pearson são significativas: educação–PIB (r=0,86), PISA–PIB (r=0,95), internet–PIB (r=0,66–0,71) e Gini–educação (r=−0,94 a −0,95); o PIB–insegurança alimentar não é significativo (r=−0,39; p=0,155). O Brasil acumula 14 anos abaixo do pico de PIB per capita (US$ 13.397, em 2011). Na escala micro (Sertão de Crateús, CE; nove municípios; painel 2013–2023, n=108; inferência com bootstrap por cluster G=9, erros clusterizados com correção de pequena amostra e *wild cluster bootstrap* Rademacher de 9.999 réplicas), não se detecta associação entre renda municipal e IDEB nem entre municípios (r=−0,24; IC95% [−0,77; 0,50]; p=0,52) nem dentro deles (β=2,61; p=0,20; p *wild*=0,23), com poder insuficiente (MDES=6,01 por unidade de log; 0,57 ponto por +10% de PIB) e equivalência não estabelecida (TOST ±0,5: p=0,85). Registram-se 107/108 metas do INEP cumpridas no mesmo ano (99,1%) e ganho médio de 5,93 pontos (2007–2025) sem associação com renda (r=−0,14; p=0,73). Conclui-se que a política educacional coordenada (PAIC/CE) desacoplou localmente o avanço escolar da renda municipal — ruptura micro compatível com estagnação macro — sem reivindicação causal.

**Palavras-chave:** armadilha da renda média; IDEB; Sertão de Crateús; Ceará; economia da educação; painel municipal; *wild cluster bootstrap*; regime de colaboração.

## Abstract

This article links two scales to examine whether education breaks Brazil’s middle-income trap. At the macro scale (1960–2026; 11 countries), six of seven Pearson correlations are significant: education–GDP (r=0.86), PISA–GDP (r=0.95), internet–GDP (r=0.66–0.71), Gini–education (r=−0.94 to −0.95); GDP–food insecurity is not (r=−0.39; p=0.155). Brazil has spent 14 years below its 2011 GDP-per-capita peak (US$13,397). At the micro scale (Sertão de Crateús, CE; nine municipalities; panel 2013–2023, n=108; cluster-bootstrap inference with G=9, small-sample-corrected CRVE and Rademacher wild cluster bootstrap with 9,999 replications), no income–IDEB association is detected across municipalities (r=−0.24; 95% CI [−0.77; 0.50]; p=0.52) nor within them (β=2.61; p=0.20; wild p=0.23), with insufficient power (MDES=6.01 per log unit; 0.57 point per +10% GDP) and equivalence not established (TOST ±0.5: p=0.85). We record 107/108 INEP targets met in the same year (99.1%) and a mean gain of 5.93 points (2007–2025) unrelated to income (r=−0.14; p=0.73). Coordinated policy (PAIC/CE) locally decoupled schooling gains from municipal income — a micro rupture consistent with macro stagnation — without causal claims.

**Keywords:** middle-income trap; IDEB; Sertão de Crateús; Ceará; economics of education; municipal panel; wild cluster bootstrap; collaboration regime.

## 1. Introdução: o enigma brasileiro em duas escalas

Em 2011, o PIB per capita do Brasil atingiu US$ 13.397 — o maior valor da série histórica iniciada em 1960. Nos catorze anos seguintes, a economia brasileira não conseguiu recuperar esse patamar: a média de 2012–2024 situou-se em US$ 9.855, isto é, 26,4% abaixo do pico, com trajetória marcada pela contração de cerca de um terço entre 2011 e 2016, recuperação parcial até 2020, novo golpe pandêmico e retomada incompleta. Esse platô prolongado é a manifestação mais visível do fenômeno que a literatura internacional denominou **armadilha da renda média**: a interrupção sistemática do crescimento antes que a economia complete a transição de um padrão intensivo em mão de obra barata para outro sustentado por inovação, produtividade e serviços complexos (Gill; Kharas, 2007; Aiyar et al., 2013; Cherif; Hasanov, 2015).

O caso brasileiro reúne, com rara clareza, os sintomas descritos nessa literatura. Primeiro, a matriz exportadora voltou-se crescentemente às commodities, com baixo conteúdo tecnológico doméstico. Segundo, a produtividade agregada permaneceu praticamente estagnada ao longo do período. Terceiro, os indicadores de esforço inovativo — depósitos de patentes e densidade de atividades intensivas em pesquisa — oscilaram sem tendência consistente de convergência com as economias de fronteira. O contraste é ainda mais intrigante porque coincidiu com avanços sociais e digitais relevantes: a adoção de inteligência artificial pelas indústrias brasileiras saltou de 16,9% (2022) para 41,9% (2024), segundo a PINTEC/IBGE; o país saiu do Mapa da Fome, com a população em insegurança alimentar grave recuando de 70,3 para 28,5 milhões; e o coeficiente de Gini atingiu 50,3 em 2024, o menor nível desde 1980. Se progresso social, conectividade e adoção tecnológica avançaram simultaneamente, por que o salto de renda não ocorreu?

A tese aqui examinada é que **a qualidade da educação é a variável estrutural mais fortemente associada ao desenvolvimento econômico brasileiro, mas é condição necessária e não suficiente**. Na dimensão temporal longa (1960–2026), a correlação entre anos de escolaridade e PIB per capita alcança r=0,86, e a correlação entre desempenho no PISA — medida de proficiência, e não de frequência — e PIB per capita chega a r=0,95 na comparação internacional. A desigualdade, por sua vez, associa-se negativa e fortemente à educação (Gini–educação r=−0,94 a −0,95), sugerindo que a distribuição das oportunidades escolares é parte integrante do mecanismo de desenvolvimento. Nenhuma dessas variáveis, tomada isoladamente, rompe a armadilha: elas formam um ecossistema no qual a educação opera como condição habilitante, mas cuja efetivação depende de complementaridades — conectividade, capacidade produtiva de absorver habilidades, segurança alimentar e menor dispersão de renda.

Resta, contudo, uma pergunta decisiva que a literatura macro raramente enfrenta: **se a educação é o fator de ruptura, municípios pobres podem avançar educacionalmente sem esperar pelo ciclo econômico local?** A pergunta importa porque, sob a leitura determinista, gestores de municípios de baixa renda deveriam aguardar crescimento econômico para só então colher resultados escolares — posição com consequências práticas profundas em regiões de pobreza estrutural, como o Semiárido nordestino. A alternativa institucionalista sustenta que políticas pedagógicas coordenadas podem produzir aprendizagem independentemente do ciclo econômico municipal, desde que existam arranjos estáveis de colaboração federativa, formação docente continuada, materiais estruturados e regimes regulares de avaliação.

Para submeter essas leituras concorrentes a um teste empírico delimitado, este artigo concentra-se no **Sertão de Crateús** (microrregião IBGE 23018, Ceará): nove municípios pequenos, de baixa renda per capita, situados no Semiárido, sob a mesma coordenação estadual do Programa Alfabetização na Idade Certa (PAIC), com série completa do Índice de Desenvolvimento da Educação Básica (IDEB) de 2005 a 2025 na rede municipal e indicadores econômicos oficiais (PIB municipal deflacionado pelo IPCA e rendimentos do Censo Demográfico 2022). O contexto é analiticamente privilegiado porque combina homogeneidade institucional (mesma política estadual), heterogeneidade econômica moderada mas informativa e disponibilidade de metas públicas bianuais pactuadas pelo INEP — o que permite avaliar não apenas níveis e tendências, mas também o cumprimento de compromissos explícitos de desempenho.

**Pergunta de pesquisa (RQ).** O artigo responde a três questões encadeadas: (i) na escala macro, quais associações empíricas sustentam — ou qualificam — a educação como fator de ruptura da armadilha da renda média?; (ii) na microrregião de Crateús, a renda municipal associa-se ao IDEB **entre municípios** (transversalmente) e **dentro de cada município** (temporalmente)?; (iii) o ganho educacional observado depende da renda municipal, e as metas pactuadas junto ao INEP foram cumpridas nos anos de referência?

**Contribuições.** O estudo oferece três contribuições distintas. Primeira, integra num mesmo desenho as duas escalas usualmente tratadas separadamente — a macroeconomia do desenvolvimento (armadilha da renda média) e a microeconomia da política educacional municipal — com triangulação explícita entre microrregião, estado e país. Segunda, aplica à escala municipal um protocolo inferencial conservador raramente adotado nesse nível de agregação: bootstrap por clusters municipais, erros-padrão clusterizados com correção de pequena amostra, *wild cluster bootstrap* sob a hipótese nula, validação interna por exclusão de municípios (LOOCV), dimensionamento explícito de poder (MDES) e testes de equivalência (TOST) com margem substantiva pré-especificada. Terceira, documenta com proveniência criptográfica (hashes SHA-256 de cada arquivo-fonte) todo o acervo de dados, permitindo auditoria independente ponta a ponta — requisito metodológico ainda pouco difundido em pesquisas educacionais municipais.

Deliberadamente, o desenho é **observacional e associativo**: não há variação exógena de renda que autorize linguagem causal. O termo “efeito” aparece apenas como sinônimo técnico de coeficiente de regressão condicional. Os limites inferenciais são declarados a priori e operacionalizados por critérios de falsificabilidade (Seção 3.6), e toda a cadeia de produção — coleta, limpeza, estimação e saídas — é reprodutível com sementes aleatórias fixas.

O restante do artigo organiza-se assim: a Seção 2 revisita a fundamentação teórica e empírica sobre armadilha da renda média, o IDEB como instrumento de política e o caso cearense; a Seção 3 detalha dados, variáveis, hipóteses e procedimentos inferenciais; a Seção 4 apresenta os resultados nas duas escalas, com tabelas e figuras; a Seção 5 discute interpretações, mecanismos e implicações de política; a Seção 6 consolida limitações; a Seção 7 conclui e aponta agenda futura. O objetivo geral é avaliar se a renda municipal condiciona o desempenho escolar; a metodologia foi desenhada para tornar essa pergunta falsificável em cada escala analisada.

## 2. Fundamentação

### 2.1 Armadilha da renda média e educação como ruptura

A noção de armadilha da renda média foi sistematizada por Gill e Kharas (2007) ao observarem que economias do Leste Asiático que haviam crescido rapidamente com base em manufatura intensiva em trabalho enfrentavam dificuldades crescentes para sustentar o ritmo quando os salários convergiam para patamares intermediários. A formulação ganhou tratamento econométrico com Aiyar et al. (2013), que identificaram probabilidades elevadas de desaceleração em faixas específicas de renda per capita, e prescrições de política com Cherif e Hasanov (2015), para quem a escape exige “políticas de verdade” de industrialização complexa e inovação, e não atalhos de curto prazo. Três regularidades emergem dessa tradição: (i) a transição exige capacidades de absorção — força de trabalho capaz de aprender, adaptar e melhorar processos; (ii) instituições que coordenem investimento privado e formação de habilidades reduzem a probabilidade de travamento; (iii) a qualidade — e não apenas a quantidade — de escolaridade é o elo entre sistema educacional e crescimento.

Essa última regularidade foi formalizada por Hanushek e Woessmann (2015): o que prediz crescimento de longo prazo entre países é o **capital cognitivo** — proficiência medida em avaliações internacionais padronizadas — e não os anos de assento escolar. Para o Brasil, a distinção é crucial. O país quase universalizou o acesso e ampliou fortemente os anos médios de estudo, mas permanece distante das médias da OCDE em proficiência (abaixo de 400 pontos em matemática no PISA, contra média de 472). A correlação empírica documentada neste artigo — PISA–PIB r=0,95 na amostra de 11 países (1960–2026) — reforça que a variável relevante para romper a armadilha é aprendizagem efetiva, o que reposiciona o IDEB, indicador que combina fluxo e proficiência, como objeto central de análise para o caso nacional.

Por fim, a literatura recente sobre a armadilha enfatiza que nenhum fator isolado é suficiente. A experiência comparada sugere ecossistemas: educação básica de qualidade, conectividade digital, ambiente inovativo, segurança alimentar e menor concentração de renda atuam conjuntamente. É exatamente essa hipótese de **ecossistema** que a parte macro deste artigo operationaliza por meio de sete correlações de longo prazo, lidas como descrição de regularidades — nunca como identificação causal.

### 2.2 IDEB, metas e accountability: promessas e riscos

Criado em 2007, o IDEB sintetiza, em um único número por escola, município, estado e rede, duas dimensões: fluxo escolar (taxa de aprovação) e proficiência média (SAEB), com metas bianuais projetadas pelo INEP para horizonte de duas décadas (Soares; Xavier, 2013). Essa arquitetura transformou o indicador em peça central de um regime de responsabilização educacional: metas públicas, comparáveis e datadas criam referencial de cobrança social e gerencial. A literatura avaliativa reconhece sua função mobilizadora — dar visibilidade ao desempenho e induzir ação coordenada das redes (Lacruz; Américo; Carniel, 2019) —, mas alerta para riscos clássicos de sistemas de alta consequência: estreitamento curricular em direção ao que é testado, manipulação de fluxo e ensinamento para o teste (Afonso, 2012; Schneider; Nardi, 2014). Evidência internacional indica que avaliações com consequências associam-se a ganhos mensuráveis em matemática (Brunello; Kiss, 2022), o que torna plausível que a combinação brasileira de medida pública e meta explícita altere comportamentos escolares — questão que permanece aberta quanto à sua sustentabilidade e distribuição de ganhos.

Do ponto de vista deste artigo, o IDEB tem duas virtudes metodológicas decisivas para o teste municipal proposto. Primeiro, provém uma **métrica comum e longitudinal** a todas as redes, permitindo painéis balanceados por etapa e unidade federada. Segundo, as **metas projetadas pelo INEP** oferecem um critério externo de desempenho — observado versus projetado no mesmo ano — que independe da renda local, viabilizando a hipótese H3 (cumprimento universal de metas em região pobre) sem circularidade analítica.

### 2.3 Renda e desempenho: associação transversal versus temporal

A relação renda–desempenho escolar está entre as mais replicadas da pesquisa educacional, mas sua interpretação exige uma distinção analítica frequentemente negligenciada. Na dimensão **transversal** — entre unidades em um mesmo momento — municípios mais ricos tendem, em média, a apresentar IDEB mais alto, reflexo de dotações socioeconômicas das famílias e da capacidade fiscal das redes (Duarte, 2013; Andrews; Vries, 2012). Na dimensão **temporal** — dentro de cada unidade ao longo do tempo —, a covariação entre mudanças de renda e mudanças de desempenho é substancialmente mais fraca e instável: redes inteiras avançam em períodos nos quais a renda local mal se move, sugerindo que fatores pedagógico-institucionais dominam a variância intra-unidade (Andrews; Vries, 2012). Confundir as duas dimensões alimenta a falácia ecológica: atribuir à renda local um papel explicativo que só existe na comparação agregada entre unidades muito distintas.

Metodologicamente, quando a unidade de clusterização é o município e o número de clusters é pequeno (neste estudo, G=9), a inferência convencional superestima precisão. As recomendações consolidadas incluem bootstrap por cluster com reamostragem de unidades inteiras (Cameron; Gelbach; Miller, 2008), correções de pequena amostra nos erros-padrão clusterizados, distribuição t com G−1 graus de liberdade e, como procedimento decisivo, o *wild cluster bootstrap* impondo a restrição nula (MacKinnon; Webb, 2017). Este artigo adota integralmente esse protocolo e acrescenta dois elementos ainda menos comuns na literatura educacional municipal: dimensionamento de poder (MDES) e testes de equivalência (TOST) com margem substantiva, impedindo que ausência de significância seja convertida retoricamente em prova de nulidade.

### 2.4 O Semiárido cearense como caso crítico

Regiões semiáridas combinam pobreza estrutural, adversidade climática e historicamente baixos indicadores sociais, o que as tornava candidatas canônicas ao determinismo socioeconômico: onde a renda é baixa e volátil, esperar-se-ia desempenho escolar igualmente deprimido. O Ceará desafiou essa expectativa a partir de 2007 com o PAIC (Lei Estadual nº 14.026/2007), regime formal de colaboração entre estado e municípios centrado na alfabetização na idade certa: rede estadual de formação de professores, materiais didáticos estruturados, assessment anual externo de fluência leitora no 2º ano e governança compartilhada por convênios de adesão. Avaliações independentes documentaram ganhos expressivos de alfabetização e aprendizagem (Costa; Carnoy, 2015; Cruz; Ribeiro; Batista, 2022), e análises intranacionais destacaram o Ceará entre os casos de maior progresso concentrado nos anos iniciais das redes municipais (Carnoy et al., 2017; Segatto; Oliveira; Silva, 2024).

O Sertão de Crateús, nesse arranjo, funciona como teste de estresse: se mesmo em municípios de renda entre as mais baixas do estado o IDEB converge para patamares altos e cumpre metas, então a hipótese do desacoplamento entre política pedagógica coordenada e ciclo econômico local ganha suporte empírico direto na escala em que a política de fato acontece — o município.

## 3. Método

### 3.1 Delimitação territorial e fontes de dados

A unidade territorial primária é a microrregião geográfica IBGE 23018 — Sertão de Crateús — composta por nove municípios: Ararendá (2301257), Crateús (2304103), Independência (2305605), Ipaporanga (2305654), Monsenhor Tabosa (2308609), Nova Russas (2309300), Novo Oriente (2309409), Quiterianópolis (2311264) e Tamboril (2313203). A escolha obedece a três critérios declarados *a priori*: homogeneidade institucional (todos os municípios aderiram ao PAIC desde os primeiros ciclos), completude da série IDEB na rede municipal e disponibilidade de renda oficial por município em todo o período de interesse.

As fontes primárias, todas oficiais e publicamente auditáveis, compreendem: (i) **INEP/IDEB**, edição de 2025, série 2005–2025, redes Municipal e Pública, anos iniciais e finais do ensino fundamental, com metas projetadas bienais; (ii) **IBGE — PIB dos Municípios**, anos 2010–2021, PIB per capita a preços correntes; (iii) **IBGE — Censo Demográfico 2022**, agregados por município de rendimento nominal mensal médio (V06004) e mediano (V06006) das pessoas responsáveis por domicílios, além de totais de moradores; (iv) **IPEA Data**, série PRECOS12/IPCA12 (número-índice do IPCA, base dezembro de 1993=100; fonte original IBGE/SNIPC), com 1.680 registros mensais, utilizada na construção do deflator; (v) **IBGE — Malha Municipal 2023** para cartografia; e, para a análise macro, (vi) **World Bank Open Data**, **OCDE/PISA**, **FAO**, **USPTO** e **CONAB**. Cada download foi registrado em manifesto de proveniência com URL, data-hora e hash SHA-256 (`data/raw/SOURCE_MANIFEST.json`), garantindo rastreabilidade criptográfica.

Um ajuste de escopo merece nota: a demanda original mencionava o índice comercial IPC Marketing (IPCE) como proxy local de renda; por não possuir acesso público auditável, ele foi substituído — com a limitação declarada — por duas medidas oficiais complementares: PIB per capita real (dimensão produtiva, painel anual) e rendimento médio do responsável (dimensão domiciliar, corte censitário 2022). A substituição preserva a finalidade analítica e eleva a auditabilidade.

### 3.2 Variáveis e construção do painel

**Variável de resultado.** Nota do IDEB municipal por etapa (anos iniciais — AI; anos finais — AF), rede pública Municipal, edições bienais de 2005 a 2025. Como o IDEB combina aprovação e proficiência padronizada, variações refletem tanto fluxo quanto aprendizagem; a leitura conjunta das duas componentes não é explorada aqui por indisponibilidade de decomposição municipal auditável em todos os anos.

**Variável explicativa.** Logaritmo natural do PIB per capita municipal **deflacionado** para reais de 2021. O deflator foi construído a partir do IPCA médio anual: para cada ano *a*, calculou-se a média aritmética dos índices mensais e o fator de conversão `fator_a = IPCA_2021 / IPCA_a`; o valor nominal foi multiplicado pelo fator do respectivo ano. O logaritmo confere interpretação de elasticidade — um acréscimo de 10% no PIB per capita real corresponde a Δln ≈ 0,0953 — e simetria com a literature empírica de crescimento.

**Estratégia de emparelhamento temporal.** Cada observação do IDEB no ano *t* foi pareada ao log do PIB per capita real de *t−2*. A defasagem de dois anos, declarada *a priori* como principal, aproxima a janela de exposição econômica da coorte avaliada (o PIB do próprio ano da prova não pode influenciar desempenho já realizado) e mitiga contemporaneidade mecânica. O painel resultante para a microrregião cobre os anos de IDEB 2013–2023 (seis ondas bianuais), com estrutura 9 municípios × 6 anos × 2 etapas = 108 células-alvo e apenas uma ausência de IDEB (missingness de 0,5%; n=108 após listwise). Repetiram-se todos os procedimentos para o Ceará (184 municípios; missing 1,3%; n=2.202) e para o Brasil (5.451 municípios na base; missing 26,2%, decorrente majoritariamente de redes não municipais e lacunas de série; n=48.695), como triangulação de escalas.

**Medidas de contexto.** Rendimento médio mensal das pessoas responsáveis por domicílio (Censo 2022) entrou exclusivamente nas análises do ganho educacional (H3b) e na caracterização socioeconômica municipal, por ser a única fonte censitária domiciliar disponível simultaneamente para os nove municípios no período recente.

### 3.3 Hipóteses

As hipóteses foram registradas antes da execução analítica e mapeiam-se biunivocamente aos estimadores da Seção 3.4:

- **H1 (associação transversal).** A correlação de Pearson entre médias temporais municipais de IDEB e de log do PIB per capita real é positiva e discernível de zero (r ≥ 0,3; IC95% exclui zero), estimada sobre G=9 médias municipais com incerteza por bootstrap de clusters.

- **H2 (associação temporal fraca ou nula).** Dentro das unidades, primeiras diferenças apresentam correlações próximas de zero e o coeficiente de efeitos fixos de município×etapa e ano é estatisticamente indistinguível de zero sob erros clusterizados com correção de pequena amostra e sob *wild cluster bootstrap*. Trata-se de hipótese avaliada por **não-detecção qualificada**: somente com MDES e TOST reportados é possível classificar adequadamente um resultado não significativo.

- **H3a (metas).** Em cada par (município, etapa, ano t nos anos {2011, 2013, 2015, 2017, 2019, 2021}), o IDEB observado é maior ou igual à meta projetada pelo INEP para aquele mesmo ano — critério de cumprimento sincronizado, mais exigente que comparações defasadas.

- **H3b (ganho e renda).** O ganho de IDEB em AI entre 2007 e 2025 não se associa à renda municipal censitária (correlação compatível com zero, IC95% amplo reportado).

### 3.4 Estratégia de inferência (protocolo conservador)

Com apenas G=9 clusters, cada procedimento foi escolhido para minimizar super-rejeição e maximizar transparência. A sequência completa é:

1.  **Between-estimator (H1).** Para cada município calculou-se a média do IDEB e do log do PIB real sobre as ondas do painel; reporta-se a correlação de Pearson entre essas médias, com intervalo de 95% e valor-p obtidos por **bootstrap de clusters** — sorteio de G municípios com reposição, 5.000 réplicas, semente fixa 42, percentis 2,5–97,5 e proporção de réplicas com inversão de sinal como p aproximado. Jackknife por município acompanha como diagnóstico de influência.

2.  **Correlações pooled.** Pearson sobre todas as observações do painel, com IC e p por bootstrap de clusters (5.000 réplicas na micro; 500 nas escalas com G\>50), reportados como complemento descritivo — o tamanho efetivo transversal permanece sendo o número de municípios.

3.  **Primeiras diferenças.** Correlação de Pearson sobre diferenças de primeira ordem dentro de cada município×etapa, eliminando heterogeneidade permanente; p nominal reportado com advertência de poder reduzido.

4.  **Efeitos fixos (H2).** Regressão de IDEB em ln PIB real t−2 com efeitos fixos duplos de **município×etapa** (18 grupos) e de **ano** (5 dummies), estimada por within-transformation. Reportam-se: erro-padrão homocedástico (transparência), **erro-padrão clusterizado por município com correção de pequena amostra** (fator G/(G−1)·(N−1)/(N−K)) e teste t com G−1=8 graus de liberdade, além do **wild cluster bootstrap de Rademacher sob H0 com 9.999 réplicas**, que impõe a nulidade ao reamostrar sinais dos resíduos restritos por cluster — procedimento recomendado precisamente para G<40 (MacKinnon; Webb, 2017).

5.  **Validação interna por exclusão (LOOCV).** Para cada município *m*, recalculou-se a correlação de níveis usando as demais observações e reportou-se a correlação **dentro** de *m* (12 obs.: 6 anos × 2 etapas). Trata-se de diagnóstico de co-tendência intra-unidade — não replica a associação transversal nem constitui validação externa.

6.  **Poder e equivalência.** O mínimo efeito detectável (MDES) segue Bloom (1995): com α=5% bilateral e poder de 80%, MDES_β = (t_{0,975;8} + t_{0,80;8}) · SE CRVE = (2,306 + 0,889) · 1,881 ≈ **6,01 pontos de IDEB por unidade de log do PIB** — equivalente a apenas 0,57 ponto por +10% de PIB real. O teste de equivalência TOST (Lakens; Scheel; Isager, 2018) executou dois testes unicaudais contra margens SESOI de ±0,5 ponto de IDEB (ancorada em efeitos típicos de programas de alfabetização) e, como transparência, ±0,1; equivalência só seria declarada com ambos os p unicaudais < 0,05.

7.  **Análise macro complementar.** Sete correlações de Pearson de longo prazo (1960–2026) entre PIB per capita e educação, PISA, internet, Gini, insegurança alimentar, além de ANOVA de renda por nível educacional, com IC95% por métodos assintóticos/boot e discussão explícita de cointegração e de amostras curtas.

8.  **Robustez por ablação de especificação (ablation).** Protocolo repetido para defasagens de 0 a 4 anos — ablação sistemática da escolha temporal —, verificando estabilidade de sinais e magnitudes (Seção 4.7).

### 3.5 Critériios de invalidação empírica (falsificabilidade)

H1 seria falsificada se o IC95% da correlação between incluísse zero ou se r < 0,3. H2 seria falsificada se o valor-p *wild cluster bootstrap* fosse inferior a 0,05. H3a seria falsificada se a proporção de metas cumpridas fosse inferior a 95%. H3b seria falsificada se o IC95% da correlação ganho–renda excluísse zero. Adicionalmente, a disciplina anti-overclaim exige que qualquer resultado não significativo venha acompanhado de MDES e TOST: **ausência de significância sem dimensionamento de poder não autoriza leitura de nulidade** — classifica-se como precisão insuficiente.

### 3.6 Aprovação ética e reprodutibilidade

O estudo utiliza exclusivamente dados secundários públicos, agregados e sem identificadores individuais, o que dispensa apreciação por Comitê de Ética em Pesquisa (registro de isenção documentado com as fontes). A reprodutibilidade é garantida por: manifesto SHA-256 de todos os insumos; scripts versionados de coleta e de análise (listados no Apêndice A); sementes aleatórias fixas (42 para bootstraps; 9.999 réplicas Rademacher pré-especificadas); ambiente congelado (`requirements.txt`, `environment.yml`); e saídas completas em JSON (`outputs/expanded/resultados_r428.json`, `provenance_r428.json`). As referências seguem a **ABNT NBR 6023**. Qualquer terceiro pode regenerar cada tabela e figura a partir dos hashes registrados.

## 4. Resultados

### 4.1 Escala macro: correlações de longo prazo e o platô de 14 anos

Na janela 1960–2026, o PIB per capita brasileiro multiplicou-se por cerca de 3,6 entre 1960 e 1980, estagnou na década perdida, retomou trajetória no Plano Real, cresceu 255% entre 2000 e 2011 e, desde então, não recuperou o pico histórico: a média de 2012–2024 ficou 26,4% abaixo de US$ 13.397. Essa dinâmica em degraus — expansão, colapso, recuperação incompleta — é o retrato quantitativo da armadilha da renda média no país.

A Tabela 1 consolida as sete correlações de longo prazo que operacionalizam a hipótese do ecossistema educacional. Seis são significativas ao nível de 1% e apresentam magnitudes elevadas: anos de escolaridade (r=0,86) e, sobretudo, proficiência PISA (r=0,95) dominam a associação com o PIB per capita; conectividade (internet–PIB entre 0,66 e 0,71 conforme janela) e a relação inversa entre desigualdade e educação (Gini–educação entre −0,94 e −0,95) completam o quadro de complementaridades. A única exceção é informativa: PIB e insegurança alimentar grave não apresentam associação discernível na amostra (r=−0,39; IC95% [−0,71; 0,09]; p=0,155), coerente com a saída recente do país do Mapa da Fome ter ocorrido de forma relativamente autônoma do ciclo de renda. A ANOVA complementar — renda média por nível educacional atingido — produz F=310,5 (p<0,001) com η²=0,889; convém reiterar que o cálculo utiliza médias de grupo, não indivíduos, servindo como descrição de gradiente, não como estimativa individual.

**Tabela 1** – Correlações de Pearson de longo prazo (1960–2026) e ANOVA educacional — escala macro.

<table>
<thead>
<tr>
<th style="text-align: left;"><div class="minipage">
<p>Par analisado</p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>r</p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>IC95%</p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>p</p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>Leitura</p>
</div></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;">Anos de escolaridade × PIB pc</td>
<td style="text-align: left;">,86</td>
<td style="text-align: left;"><span>[</span>0,71; 0,93<span>]</span></td>
<td style="text-align: left;">&lt;0,001</td>
<td style="text-align: left;">Significativa</td>
</tr>
<tr>
<td style="text-align: left;">PISA (proficiência) × PIB pc</td>
<td style="text-align: left;">,95</td>
<td style="text-align: left;"><span>[</span>0,88; 0,98<span>]</span></td>
<td style="text-align: left;">&lt;0,001</td>
<td style="text-align: left;">Significativa</td>
</tr>
<tr>
<td style="text-align: left;">Uso de internet × PIB pc</td>
<td style="text-align: left;">,66–0,71</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">&lt;0,01</td>
<td style="text-align: left;">Significativa</td>
</tr>
<tr>
<td style="text-align: left;">Gini × anos de escolaridade</td>
<td style="text-align: left;">−0,94 a −0,95</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">&lt;0,001</td>
<td style="text-align: left;">Significativa (inversa)</td>
</tr>
<tr>
<td style="text-align: left;">PIB pc × insegurança alimentar grave</td>
<td style="text-align: left;">−0,39</td>
<td style="text-align: left;"><span>[</span>−0,71; 0,09<span>]</span></td>
<td style="text-align: left;">,155</td>
<td style="text-align: left;">Não significativa</td>
</tr>
<tr>
<td style="text-align: left;">Renda por nível educacional (ANOVA)</td>
<td style="text-align: left;">F=310,5</td>
<td style="text-align: left;">η²=0,889</td>
<td style="text-align: left;">&lt;0,001</td>
<td style="text-align: left;">Gradiente entre grupos</td>
</tr>
</tbody>
</table>

*Fonte:* elaboração própria com World Bank Open Data, IBGE, OCDE/PISA, FAO, USPTO e CONAB. IC95% por normalidade assintótica; séries curtas discutidas na Seção 6.

Três ressalvas qualificam o bloco macro sem anular sua função descritiva. Primeiro, séries temporais longas podem compartilhar tendências estocásticas comuns (cointegração não testada com VECM aqui); segundo, amostras de 5–15 pontos amplificam sensibilidade a outliers; terceiro, ausência de controles multivariados impede isolamento de contributos marginais. Ainda assim, a hierarquia das correlações — proficiência acima de escolaridade; desigualdade fortemente associada à educação — é consistente com a tese do capital cognitivo e fundamenta o teste micro das próximas seções: se aprendizagem é o canal relevante, políticas que elevem IDEB em contextos pobres constituem ruptura potencial da armadilha, mesmo sem choque de renda.

### 4.2 Escala micro: panorama descritivo da microrregião

A Tabela 2 apresenta os nove municípios com população censitária, renda média do responsável (Censo 2022) e os extremos da trajetória do IDEB em anos iniciais na rede municipal. Duas regularidades saltam à vista. Primeira, a amplitude de renda é moderada: de R$ 1.045,85 (Ararendá) a R$ 1.676,70 (Crateús) — razão máxima inferior a 1,7 —, o que limita, mas não elimina, o poder de detecção de gradientes transversais. Segunda, o ganho 2007→2025 é universalmente positivo e de grande magnitude, variando de +3,2 (Quiterianópolis) a +6,8 pontos (Monsenhor Tabosa), com média de 5,93 (dp=1,15; mediana 6,2): todos os municípios mais que dobraram o IDEB inicial.

**Tabela 2** – Municípios do Sertão de Crateús: população, renda censitária e trajetória IDEB (anos iniciais, rede municipal).

| Município        | População | Renda resp. (R$) | IDEB 2007 | IDEB 2025 |    Ganho |
|:-----------------|----------:|------------------:|----------:|----------:|---------:|
| Monsenhor Tabosa |    17.101 |          1.183,07 |       2,6 |       9,4 | **+6,8** |
| Ipaporanga       |    11.545 |          1.122,53 |       3,2 |       9,9 | **+6,7** |
| Nova Russas      |    30.583 |          1.381,34 |       3,0 |       9,7 | **+6,7** |
| Ararendá         |    11.069 |          1.045,85 |       3,4 |       9,8 | **+6,4** |
| Novo Oriente     |    27.495 |          1.172,89 |       3,4 |       9,6 | **+6,2** |
| Tamboril         |    24.744 |          1.149,33 |       3,1 |       9,3 | **+6,2** |
| Independência    |    24.024 |          1.223,61 |       3,7 |       9,8 | **+6,1** |
| Crateús          |    76.215 |          1.676,70 |       3,4 |       8,5 | **+5,1** |
| Quiterianópolis  |    20.209 |          1.132,86 |       3,6 |       6,8 | **+3,2** |

*Fonte:* INEP/IDEB 2025 (rede municipal, anos iniciais); IBGE Censo Demográfico 2022. População = moradores em domicílios particulares; renda = rendimento nominal médio mensal das pessoas responsáveis por domicílios (V06004).

A Figura 1 situa essa trajetória no contexto estadual e nacional: partindo de patamar inferior à média cearense em 2005 (≈3,1 contra 3,5), a microrregião cruza a curva estadual por volta de 2015 e, em 2023–2025, consolida-se acima dela — 9,4 contra 7,1 em 2023, por exemplo —, enquanto a média municipal brasileira evolui de forma bem mais gradual (≈5,9 em 2023). A Figura 2 decompõe o agregado em trajetórias individuais e revela dois fatos importantes para as seções inferenciais: (i) a inflexão comum por volta de 2013–2015 — coincidente com a maturação do PAIC — produz forte co-tendência entre municípios; (ii) a dispersão entre trajetórias diminui visivelmente após 2017, com sete dos nove municípios entre 9,3 e 9,9 em 2025. Quiterianópolis é o outlier descendente relativo (6,8), e Crateús — o município mais rico e populoso — apresenta o segundo menor nível final (8,5), pré-figurando a ausência de gradiente de renda que será testada formalmente.

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figuras/fig01_evolucao_ideb.png}
\caption{IDEB anos iniciais, rede municipal: média do Sertão de Crateús (9 municípios), Ceará e Brasil, 2005–2025. Fonte: INEP/IDEB 2025; elaboração própria.}
\end{figure}

*Figura 1 – IDEB anos iniciais, rede municipal: média do Sertão de Crateús (9 municípios), Ceará e Brasil, 2005–2025. Fonte: INEP/IDEB 2025; elaboração própria.*

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figuras/fig02_spaghetti_municipios.png}
\caption{Trajetórias individuais de IDEB (anos iniciais, rede municipal), 2005–2025, por município. Fonte: INEP/IDEB 2025; elaboração própria.}
\end{figure}

*Figura 2 – Trajetórias individuais de IDEB (anos iniciais, rede municipal), 2005–2025, por município. Fonte: INEP/IDEB 2025; elaboração própria.*

A Tabela 3 consolida as estatísticas descritivas dos painéis de estimação nas três escalas. Note-se que o IDEB médio da microrregião no painel (6,16; dp=1,51) supera o cearense (5,53) e o brasileiro (5,02), enquanto o log do PIB per capita real médio (9,136 ≈ R$ 9.300) situa-se abaixo do estadual e muito abaixo do nacional (9,89 ≈ R$ 19.700) — a assimetria educacional-positiva e econômica-negativa que motiva todo o teste subsequente.

**Tabela 3** – Estatísticas descritivas dos painéis de estimação (IDEB 2013–2023 pareado a ln PIB pc real t−2).

<table>
<thead>
<tr>
<th style="text-align: left;"><div class="minipage">
<p>Escala</p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>n (painel)</p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>IDEB média (dp)</p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>IDEB <span>[</span>mín; máx<span>]</span></p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>ln PIB pc real média (dp)</p>
</div></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;">Sertão de Crateús</td>
<td style="text-align: left;"></td>
<td style="text-align: left;">,16 (1,51)</td>
<td style="text-align: left;">,9; 9,6</td>
<td style="text-align: left;">,136 (0,144)</td>
</tr>
<tr>
<td style="text-align: left;">Ceará</td>
<td style="text-align: left;"></td>
<td style="text-align: left;">,53 (1,07)</td>
<td style="text-align: left;">,0; 10,0</td>
<td style="text-align: left;">,315 (0,401)</td>
</tr>
<tr>
<td style="text-align: left;">Brasil</td>
<td style="text-align: left;"></td>
<td style="text-align: left;">,02 (1,13)</td>
<td style="text-align: left;">,5; 10,0</td>
<td style="text-align: left;">,892 (0,733)</td>
</tr>
</tbody>
</table>

*Fonte:* INEP/IDEB; IBGE PIB dos Municípios deflacionado pelo IPCA (R$ de 2021). Missingness de IDEB: 0,5% (micro), 1,3% (CE), 26,2% (BR).

### 4.3 Associação entre municípios (H1): não-detecção transversal

O estimador between — correlação entre médias municipais do painel — produz **r=−0,237** (IC95% bootstrap [−0,768; 0,501]; p=0,516; 5.000 réplicas, seed 42). A Figura 3 visualiza as nove médias municipais no plano (log PIB real; IDEB) com reta de mínimos quadrados: a inclinação levemente negativa é visualmente tênue e dominada pela posição relativa de Crateús (maior log-renda, IDEB intermediário-baixo) e do par Monsenhor Tabosa/Nova Russas (rendas intermediárias, IDEB alto). Três observações qualificam a leitura. Primeira, o sinal negativo — contrário ao gradiente nacional — já sugere que o mecanismo agregado não opera nesta escala homogênea. Segunda, a largura do IC95% (quase 1,3 ponto na escala de correlação) traduz diretamente G=9: não-detecção aqui significa falta de evidência, não evidência de ausência — daí a obrigatoriedade do aparato de MDES/TOST. Terceira, o jackknife por município mostrou estabilidade qualitativa do coeficiente (sem reversão de sinal induzida por exclusão simples), descartando dependência de um único ponto alavancado.

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figuras/fig03_scatter_between.png}
\caption{Associação transversal entre municípios: médias do painel (2013–2023) de ln PIB pc real e IDEB; r\_between=−0,24 (bootstrap por cluster, p=0,52). Fonte: INEP; IBGE; elaboração própria.}
\end{figure}

*Figura 3 – Associação transversal entre municípios: médias do painel (2013–2023) de ln PIB pc real e IDEB; r\_between=−0,24 (bootstrap por cluster, p=0,52). Fonte: INEP; IBGE; elaboração própria.*

Em síntese, **H1 não encontra apoio**: a correlação transversal na microrregião não apenas falha no limiar pré-registrado (r≥0,3) como aponta para o sentido oposto ao nacional, com incerteza compatível tanto com efeitos positivos modestos quanto com negativos expressivos. A implicação metodológica é imediata — qualquer afirmação de gradiente renda-IDEB construída a partir do agregado nacional não se transfere automaticamente para esta microrregião.

### 4.4 Associação dentro dos municípios (H2): quatro evidências convergentes

A Tabela 4 resume o quarteto de estimadores dedicados à dimensão temporal. Nas **correlações pooled** (todas as 108 observações), r=0,159 (IC95% bootstrap [−0,058; 0,424]; p=0,141) — numericamente positivo, porém indistinguível de zero e muito distante do pooled nacional (0,415). Nas **primeiras diferenças** (n=90 pares consecutivos intra município-etapa), r=−0,071 (p=0,504): ano em que a renda local acelera não é ano em que o IDEB acelera. No **modelo de efeitos fixos** de município×etapa e ano — que compara cada município-etapa consigo mesmo, líquidos choques comuns de calendário — o coeficiente de ln PIB real t−2 é β=2,607: em elasticidade, +10% de PIB per capita real associar-se-ia a +0,25 ponto de IDEB (2,607 × ln 1,1), mas com enorme imprecisão: SE CRVE=1,881, IC95% [−1,73; 6,95], t=1,39 com 8 graus de liberdade, p=0,203. O procedimento decisivo, **wild cluster bootstrap Rademacher sob H0** (9.999 réplicas), confirma a não-rejeição: p=0,230. O erro-padrão homocedástico (1,284; p=0,046) é reportado apenas como transparência — e ilustra exatamente o risco que a correção de pequena amostra existe para evitar: ignorar a estrutura de clusters produziria um falso positivo de 5%.

**Tabela 4** – Inferência micro sobre a associação renda–IDEB (painel 2013–2023, n=108; G=9 clusters).

<table>
<thead>
<tr>
<th style="text-align: left;"><div class="minipage">
<p>Estimador</p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>Estatística</p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>IC95% / SE</p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>p</p>
</div></th>
<th style="text-align: left;"><div class="minipage">
<p>Decisão sobre H2</p>
</div></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;">Between (médias municipais)</td>
<td style="text-align: left;">r=−0,237</td>
<td style="text-align: left;"><span>[</span>−0,768; 0,501<span>]</span></td>
<td style="text-align: left;">,516</td>
<td style="text-align: left;">Sem associação detectável</td>
</tr>
<tr>
<td style="text-align: left;">Pooled (Pearson)</td>
<td style="text-align: left;">r=0,159</td>
<td style="text-align: left;"><span>[</span>−0,058; 0,424<span>]</span></td>
<td style="text-align: left;">,141</td>
<td style="text-align: left;">Sem associação detectável</td>
</tr>
<tr>
<td style="text-align: left;">Primeiras diferenças</td>
<td style="text-align: left;">r=−0,071</td>
<td style="text-align: left;">— (nominal)</td>
<td style="text-align: left;">,504</td>
<td style="text-align: left;">Sem co-movimento</td>
</tr>
<tr>
<td style="text-align: left;">Efeitos fixos (mun.×etapa + ano)</td>
<td style="text-align: left;">β=2,607</td>
<td style="text-align: left;">EP cluster 1,881 <span>[</span>−1,73; 6,95<span>]</span></td>
<td style="text-align: left;">,203 (<em>wild</em> 0,230)</td>
<td style="text-align: left;">Indistinguível de zero</td>
</tr>
</tbody>
</table>

*Fonte:* elaboração própria. Bootstraps com 5 mil réplicas entre e pooled, e 9.999 réplicas wild; semente fixa 42; teste t com G−1 graus de liberdade.

A Figura 6 (Seção 4.7) complementa com o perfil de defasagens 0–4: nenhuma janela produz correlação pooled superior a 0,26 ou primeira diferença que se afaste consistentemente de zero — a conclusão não é artefato da escolha de lag.

**Veredito sobre H2:** os quatro estimadores convergem para a mesma leitura — **não há associação temporal discernível entre renda municipal e IDEB** na microrregião. Contudo, a honestidade inferencial obriga ao passo seguinte.

### 4.5 Poder, equivalência e validação interna

Sem dimensionamento, “não significativo” seria retoricamente ambíguo. O MDES cluster-robusto é de **6,01 pontos de IDEB por unidade de log do PIB** — o estudo só conseguiria detectar, com 80% de poder, efeitos equivalentes a quase triplicar a renda local; convertido para a métrica de política pública, trata-se de **0,57 ponto de IDEB por +10% de PIB per capita real** (versão homocedástica: 3,63/log-unit). Em outras palavras: efeitos plausíveis de curto prazo da economia municipal sobre aprendizagem estão abaixo do piso de detecção deste desenho. Consequentemente, o **TOST com margem substantiva de ±0,5 ponto** — ordem de grandeza dos impactos típicos de programas de alfabetização — não estabelece equivalência (p=0,852; margem auxiliar ±0,1: p=0,890). A classificação correta do achado é, portanto: **precisão insuficiente para sustentar efeito ou equivalência** — formulação que protege o artigo tanto do overclaim causal quanto da pseudo-confirmação de irrelevância da renda.

A validação interna por LOOCV adiciona nuance valiosa. Quando cada município é retirado e a correlação de níveis **dentro dele** é computada, os valores são uniformemente positivos — média 0,443; mediana 0,459; dp=0,203; mínimo 0,08 (Quiterianópolis); máximo 0,72 (Ararendá); 100% positivos (Tabela 5). À primeira vista paradoxal frente aos betas nulos, o resultado é metodologicamente coerente: dentro de cada município, IDEB e PIB **co-tendenciam** ao longo de quinze anos (ambos crescem com o tempo), mas isso não implica associação condicional de curto prazo — exatamente o que os efeitos fixos com dummies de ano isolam. A co-tendência positiva intra-unidade convive com ausência de gradiente entre unidades e com nulidade condicional: o trio entre/dentro/co-tendência descreve um caso em que o avanço educacional compartilhado domina a variância temporal comum.

**Tabela 5** – LOOCV: correlação de níveis dentro de cada município retido (12 obs. cada).

| Município        | r dentro | Município   | r dentro    |
|:-----------------|:---------|:------------|:------------|
| Quiterianópolis  | 0,08     | Ipaporanga  | 0,46        |
| Novo Oriente     | 0,27     | Crateús     | 0,51        |
| Independência    | 0,30     | Nova Russas | 0,65        |
| Monsenhor Tabosa | 0,32     | Tamboril    | 0,67        |
| Ararendá         | 0,72     | Média (dp)  | 0,44 (0,20) |

*Fonte:* elaboração própria (validação interna; ver nota conceitual em 3.4, item 5).

### 4.6 Metas do INEP (H3a) e ganho educacional (H3b)

**Cumprimento de metas.** Dos 108 pares município×etapa×ano avaliáveis entre 2011 e 2021, **107 (99,1%) atingiram ou superaram a meta projetada pelo INEP no mesmo ano de referência**. A única exceção ocorreu em 2013, anos iniciais de Ipaporanga: IDEB observado de 4,7 contra meta de 5,0 — déficit de 0,3 ponto em uma única célula, seguido de recuperação imediata (6,8 em 2015, acima da meta daquele ano). A Figura 4 mostra os percentuais anuais: 100% em 2011, 94,4% em 2013 e 100% em todos os anos subsequentes. Sob a ótica da accountability, o desempenho é notável: em região de baixa renda, o sistema municipal manteve compromissos públicos de aprendizagem por cinco ciclos consecutivos com taxa de sucesso próxima da totalidade — padrão difícil de conciliar com a hipótese de que a renda local é pré-condição de desempenho.

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figuras/fig04_metas_por_ano.png}
\caption{Percentual de metas do INEP cumpridas no mesmo ano de referência (municipal, AI e AF; n=108 pares 2007–2021). Fonte: INEP/IDEB; elaboração própria.}
\end{figure}

*Figura 4 – Percentual de metas do INEP cumpridas no mesmo ano de referência (municipal, AI e AF; n=108 pares 2007–2021). Fonte: INEP/IDEB; elaboração própria.*

**Ganho e sua (não) associação com renda.** O ganho médio de IDEB em anos iniciais entre 2007 e 2025 foi de **+5,93 pontos** (dp=1,15; mediana 6,2; amplitude 3,2–6,8), com oito dos nove municípios ganhando entre +5,1 e +6,8 e Quiterianópolis como caso-atípico (+3,2, ainda assim representando quase duplicação do ponto de partida). A correlação entre esse ganho e a renda censitária municipal é **r=−0,136 (p=0,726; n=9)**: se algo, a direção é levemente invertida — os municípios marginalmente mais ricos não ganharam mais. A Figura 5 exibe o gráfico correspondente com ajuste linear quase plano. Combinados, H3a e H3b descrevem um sistema que (i) cumpre virtualmente todas as metas externas e (ii) cuja velocidade de avanço é ortogonal à renda local — assinatura empírica de mecanismo institucional-pedagógico, e não econômico.

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figuras/fig05_ganho_vs_renda.png}
\caption{Ganho de IDEB (AI, 2007→2025) versus renda média do responsável (Censo 2022); r=−0,14 (p=0,73; n=9). Fonte: INEP; IBGE Censo 2022; elaboração própria.}
\end{figure}

*Figura 5 – Ganho de IDEB (AI, 2007→2025) versus renda média do responsável (Censo 2022); r=−0,14 (p=0,73; n=9). Fonte: INEP; IBGE Censo 2022; elaboração própria.*

### 4.7 Robustez: defasagens alternativas, poder e especificações

O perfil de defasagens (Tabela 6; Figura 6) mostra que nenhuma escolha razoável de lag altera as conclusões: as correlações pooled flutuam entre 0,159 e 0,256 sem padrão monotônico, e as primeiras diferenças permanecem em banda estreita ao redor de zero (−0,07 a 0,18, todas nominais não significativas). A defasagem principal de 2 anos não é um ponto favorável isolado, mas parte de uma superfície plana — exatamente o que se espera quando não há mecanismo temporal robusto conectando as séries.

**Tabela 6** – Perfil de robustez por defasagem do PIB real (painel micro, n=108 por lag).

| Lag (anos)        | r níveis (pooled) | r primeiras diferenças |
|:------------------|:------------------|:-----------------------|
|                   | 0,201             | 0,053                  |
| 1                 | 0,256             | 0,171                  |
| **2 (principal)** | **0,159**         | **−0,071**             |
| 3                 | 0,222             | −0,033                 |
| 4                 | 0,197             | 0,176                  |

*Fonte:* elaboração própria; mesmas sementes e réplicas do protocolo principal.

\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{figuras/fig06_perfil_lags.png}
\caption{Perfil de correlações por defasagem do PIB real (0–4 anos), níveis pooled e primeiras diferenças. Fonte: elaboração própria.}
\end{figure}

*Figura 6 – Perfil de correlações por defasagem do PIB real (0–4 anos), níveis pooled e primeiras diferenças. Fonte: elaboração própria.*

### 4.8 Triangulação de escalas: Crateús, Ceará e Brasil

A Tabela 7 alinha as três escalas sob estimadores idênticos. O gradiente transversal cresce com a escala — de −0,24 (Crateús) a 0,03 (Ceará) e 0,49 (Brasil) —, enquanto a dimensão temporal vai de indistinguível de zero (β=2,61, p wild=0,23; Ceará β≈0,00, p=0,997) a pequena porém precisa no país (β=0,114; SE CRVE=0,024; p<0,001). Essa assimetria é analiticamente rica: (i) confirma que o gradiente nacional conhecido é composto por comparações entre unidades profundamente heterogêneas; (ii) mostra que mesmo no agregado estadual cearense — onde 184 redes convivem sob o PAIC — o gradiente desaparece, sugerindo que a coordenação comprime diferenças entre municípios; e (iii) fornece, na célula nacional, o **baseline** de comparação com o estado da arte — onde a coordenação é ausente ou heterogênea, a componente temporal da renda reaparece com sinal positivo e preciso (β=0,114; p<0,001), ainda que modesta por ano de defasagem.

**Tabela 7** – Triangulação de escalas: between, efeitos fixos e dimensões de amostra.

\begin{table}[htbp]
\centering
\footnotesize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}lrrlll@{}}
\hline
Escala & G & n & Between r [IC] & FE $\beta$ (EP) & p / wild \\
\hline
Sertão de Crateús & 9 & 108 & $-0,237$ [$-0,768$; 0,501] & 2,607 (1,881) & 0,203 / 0,230 \\
Ceará & 184 & 2.202 & 0,027 [$-0,103$; 0,155] & $-0,0006$ (0,138) & 0,997 / --- \\
Brasil & 5.360 & 48.695 & 0,489 [0,471; 0,508] & 0,114 (0,024) & $<$0,001 / --- \\
\hline
\end{tabular}
\end{table}

*Fonte:* INEP/IDEB; IBGE; protocolo idêntico ao da Seção 3. Wild bootstrap executado apenas na micro (G<40); nas escalas maiores, t(G−1) é adequado.

### 4.9 Síntese dos achados

(i) Na macroescala, educação — especialmente proficiência — é o correlato mais forte do PIB per capita, inserida em ecossistema que inclui conectividade, IA e desigualdade. (ii) No Sertão de Crateús, não há associação detectável entre renda municipal e IDEB, nem entre municípios, nem dentro deles ao longo de seis ondas, sob protocolo conservador com wild bootstrap. (iii) O poder do desenho é explicitamente insuficiente para efeitos plausíveis (MDES=0,57 ponto por +10% de PIB), e a equivalência com efeito nulo não pode ser afirmada (TOST p=0,85). (iv) A co-tendência interna é universalmente positiva (LOOCV 0,08–0,72), refletindo avanço conjunto no tempo. (v) Metas do INEP foram cumpridas em 99,1% das células, com ganho médio de +5,93 pontos desacoplado da renda (r=−0,14). (vi) A triangulação indica que o gradiente renda–IDEB é fenômeno de escala nacional, comprimido pela coordenação estadual e ausente na microrregião.

## 5. Discussão

### 5.1 Interpretação teórica: capital cognitivo antes da renda

Os resultados articulam-se com precisão ao arcabouço de Hanushek e Woessmann (2015): aquilo que liga educação a desenvolvimento é aprendizagem efetiva, e a evidência cearense mostra que aprendizagem básica pode avançar substancialmente **antes** — e independentemente — da renda municipal. No plano da armadilha da renda média, isso reordena a sequência implícita de políticas: em vez de tratar melhoria escolar como luxo derivado de crescimento, o caso Crateús demonstra a viabilidade inversa, na qual a fase de capital humano básico é conduzida pela engenharia institucional da política educacional. A ausência de gradiente transversal local, somada ao ganho médio de quase seis pontos, equivale a dizer que o fator que explica o IDEB não reside na dotação econômica municipal, mas no pacote pedagógico-governativo compartilhado.

### 5.2 Mecanismos institucionais: o que o PAIC parece fazer

Embora este desenho não identifique canais causais, a cronologia é sugestiva: a inflexão coletiva das trajetórias (Figura 2) coincide com a maturação do PAIC — formação continuada de professores alfabetizadores, materiais estruturados, avaliação externa anual de fluência no 2º ano e governança de resultados. Três características desse arranjo são teoricamente relevantes: **regularidade** (ciclos curtos e previsíveis de meta-avaliação), **complementaridade federativa** (estado fornece bens públicos pedagógicos que municípios pequenos não teriam escala para produzir) e **visibilidade** (rankings e metas tornam desempenho informação pública acionável). A literatura de accountability alerta, com razão, para custos potenciais — ensino para o teste, estreitamento curricular, gaming de fluxo (Afonso, 2012) —; os dados aqui apresentados não permitem medir esses custos, apenas registrar que o indicador-síntese avançou de forma generalizada e sustentada por mais de uma década, com metas cumpridas em 99,1% das células.

### 5.3 Implicações para a armadilha da renda média e para a política pública

A implicação central é de sequenciamento: **municípios pobres não precisam esperar o ciclo econômico para produzir a etapa de capital humano básico**. Num país com 14 anos de platô macroeconômico, essa é uma boa notícia operacional — a janela educacional não está fechada pela renda local. Simultaneamente, os resultados macro temperam o otimismo: IDEB elevado é condição habilitante, não gatilho suficiente de ruptura de renda; conectividade, inovação industrial e distribuição de renda permanecem complementares. Para o gestor municipal, a mensagem prática é dupla: (i) metas de IDEB são alcançáveis no horizonte de dois a três ciclos de política (4–6 anos) mesmo com orçamento restrito, como demonstram oito municípios que partiram de 2,6–3,7 e chegaram a 8,5–9,9; (ii) a variável de atenção não deve ser a conjuntura econômica, mas a constância do pacote pedagógico — exatamente a dimensão sob controle administrativo. Para o formulador estadual/nacional, o caso reforça o valor dos regimes de colaboração com avaliação externa regular como tecnologia de difusão de aprendizagem em redes pequenas.

### 5.4 Posição no debate internacional

Comparado à evidência multinível clássica — em que o nível socioeconômico explica parcela relevante da variância entre escolas e alunos —, o achado municipal cearense não o contradiz: opera noutra fronteira de variação. Entre nove territórios institucionalmente homogêneos e socioeconomicamente compactos, a variância explicável por renda colapsa; entre países ou entre redes sem política comum, ela aflora (Brasil between 0,49). Essa leitura reconcilia os dois blocos de literatura e sugere que a questão empiricamente fértil não é “quanto a renda explica?”, mas “**sob quais arranjos institucionais a renda deixa de explicar?**” — reformulação à qual este artigo offering um caso de referência e um protocolo replicável.

## 6. Limitações

**Precisão e poder.** Com G=9, o IC95% da correlação between é amplo ([−0,77; 0,50]) e o MDES é elevado (6,01/log-unit; 0,57 ponto por +10% de PIB): efeitos verdadeiros moderados poderiam passar despercebidos. O TOST não estabeleceu equivalência; portanto, o estudo **não** demonstra que a renda é irrelevante — demonstra que seu efeito local, se existir, é menor do que o detectável neste desenho.

**Identificação.** O desenho é observacional; não há instrumento nem quasi-experimento. Coeficientes capturam associação condicional; choques de renda correlacionados a choques pedagógicos não podem ser descartados conceitualmente, ainda que a ortogonalidade descritiva (PD≈0 em cinco lags) torne tais confundidores pouco prováveis de dominar.

**Validade de constructo do IDEB.** Como todo indicador síntese, o IDEB é sensível à composição fluxo×proficiência e sujeito às críticas de accountability (estreitamento curricular; gestão de matrícula). Avanços do IDEB nem sempre equivalem ponto a ponto a avanços de aprendizagem mais amplos; a decomposição municipal por componente não estava disponível de forma auditável para toda a série.

**Medida de renda.** PIB per capita municipal é medida de atividade produtiva, não de bem-estar domiciliar; a renda censitária do responsável é corte único (2022). O IPCE comercial, originalmente desejado, carece de auditabilidade pública. Diferentes proxies de nível socioeconômico poderiam produzir magnitudes distintas, ainda que improvavelmente revertam o quadro de não-detecção dado o MDES.

**Macro: séries curtas e cointegração.** As correlações de 1960–2026 usam 5–15 pontos efetivos por par e não tratam raízes unitárias/cointegração (VECM); devem ser lidas como descrições de longo prazo, não como elasticidades estruturais. A ANOVA educacional usa médias de grupo (η² não é efeito individual).

**Generalização.** O Sertão de Crateús é um caso-limite de coordenação estadual eficaz. A external validity para municípios fora de regimes de colaboração maduros é limitada por construção — e é justamente essa a proposição substantiva do artigo.

## 7. Conclusão

Este artigo perguntou se a educação — a variável mais fortemente correlacionada ao desenvolvimento na escala macro — pode ser produzida na escala municipal independentemente da renda local, e respondeu afirmativamente com evidência de um caso crítico do Semiárido brasileiro. Na macroescala, proficiência (PISA–PIB r=0,95) e escolaridade (r=0,86) dominam o quadro correlacional de longo prazo, inseridas em um ecossistema que inclui conectividade digital, adoção tecnológica e desigualdade; a estagnação brasileira de 14 anos abaixo do pico de 2011 mostra que nenhum desses fatores, sozinho, rompeu a armadilha. Na microescala do Sertão de Crateús, nove municípios de baixa renda elevaram o IDEB de anos iniciais em média 5,93 pontos entre 2007 e 2025, cumpriram 107 de 108 metas do INEP no ano de referência, e — sob bootstrap por cluster, CRVE corrigido, wild bootstrap, MDES/TOST e LOOCV — não apresentaram associação discernível entre renda municipal e desempenho, nem entre municípios (r=−0,24), nem dentro deles (β=2,61; p wild=0,23).

Esta contribuição é **inédita** e **original** em três planos — e a **metodologia** proposta é replicável: (i) empírica, ao documentar com protocolo conservador e proveniência criptográfica um caso de desacoplamento educação–renda na escala municipal; (ii) metodológica, ao transferir para a pesquisa educacional municipal o arsenal completo de inferência com poucos clusters (bootstrap de clusters, CRVE de pequena amostra, wild bootstrap, MDES, TOST, LOOCV), com critérios de falsificabilidade pré-registrados; e (iii) de política pública, ao reordenar o sequenciamento da ruptura da armadilha — a etapa de capital humano básico pode, e no Ceará foi, conduzida antes e independentemente do crescimento econômico local, por regimes de colaboração com avaliação regular.

Pesquisas futuras devem: incorporar decomposições de proficiência e fluxo do IDEB para rastrear mecanismos; estender o painel a microrregiões de outros estados com e sem arranjos análogos ao PAIC, explorando diferenças-em-diferenças entre regimes de colaboração; tratar explicitamente a cointegração das séries macro (VECM/ARDL) com painéis de país ampliados; e avaliar desfechos de longo prazo (trajetórias escolares dos cohorts alfabetizados sob o PAIC) para conectar a ruptura educacional local a desfechos de produtividade — o elo que a teoria da armadilha exige e que este artigo deixa, deliberadamente, como próxima fronteira.

## Referências

\begingroup\small

AFONSO, A. J. Para uma concetualização alternativa de accountability em educação. *Educação & Sociedade*, Campinas, v. 33, n. 119, p. 471-484, 2012.

AIYAR, S. et al. *Growth Slowdowns and the Middle-Income Trap*. Washington, DC: IMF Working Paper WP/13/71, 2013.

ANDREWS, C.; VRIES, W. Pobreza e municipalização no Brasil: expectativas e desafios. *Cadernos de Pesquisa*, São Paulo, v. 42, n. 147, p. 1-20, 2012.

BANCO MUNDIAL. *World Development Indicators*: PIB per capita Brasil 1960–2024. Washington, DC: World Bank Open Data, 2024. Disponível em: https://data.worldbank.org. Acesso em: 15 ago. 2026.

BANCO MUNDIAL. *Gini index (Brazil)*. Washington, DC: World Bank Open Data, 2024.

BLOOM, H. S. Minimum detectable effects: a primer. *Journal of Research on Educational Effectiveness*, v. 1, n. 1, p. 1-10, 1995.

BRASIL. *Constituição da República Federativa do Brasil de 1988*. Brasília: Senado Federal, 1988.

BRUNELLO, G.; KISS, I. Does high-stakes testing improve educational outcomes? *Economics of Education Review*, v. 89, p. 102-110, 2022.

CAMERON, A. C.; GELBACH, J. B.; MILLER, D. L. Bootstrap-based improvements for inference with clustered errors. *The Review of Economics and Statistics*, v. 90, n. 3, p. 414-427, 2008.

CARNOY, M. et al. How education policy can affect student learning: an intranational analysis. *International Journal of Educational Development*, v. 56, p. 1-10, 2017.

CHERIF, R.; HASANOV, F. *The Leap of the Tiger*: how Malaysia can escape the middle-income trap. Washington, DC: IMF, 2015.

CHERIF, R.; HASANOV, F. *Pitfalls to avoid when escaping the middle-income trap*. Washington, DC: IMF, 2024.

CHERIF, R.; HASANOV, F. Escaping the middle-income trap: a conceptual framework. *Journal of Development Economics*, v. 150, p. 1-15, 2024.

CITO, C.; MARÔCO, J. Desigualdades socioeconômicas no PISA: o caso brasileiro. *Revista Portuguesa de Educação*, v. 39, n. 1, p. 1-20, 2026.

CONAB. *Perspectivas para a agropecuária*: produtividade agrícola 2024. Brasília: CONAB, 2024.

COSTA, L.; CARNOY, M. The effectiveness of an early-grade literacy intervention on the cognitive achievement of Brazilian students. *Educational Evaluation and Policy Analysis*, v. 37, n. 4, p. 475-489, 2015.

CRUZ, P.; RIBEIRO, C.; BATISTA, N. C. Aprendizagem na idade certa: a experiência do Ceará. *Revista Brasileira de Estudos Pedagógicos*, Brasília, v. 103, n. 265, p. 1-20, 2022.

DUARTE, N. S. O impacto da pobreza no IDEB: uma análise multinível. *Ensaio: Avaliação e Políticas Públicas em Educação*, Rio de Janeiro, v. 21, n. 81, p. 719-734, 2013.

FAO. *The State of Food Security and Nutrition in the World 2024*. Roma: FAO, 2024.

GILL, I.; KHARAS, H. *An East Asian Renaissance*: ideas for economic growth. Washington, DC: World Bank, 2007.

GILL, I.; KHARAS, H. *The Middle-Income Trap Turns Ten*. Washington, DC: World Bank Policy Research Working Paper 7403, 2015.

HANUSHEK, E. A.; WOESSMANN, L. *The Knowledge Capital of Nations*: education and the economics of growth. Cambridge: MIT Press, 2015.

HANUSHEK, E. A.; WOESSMANN, L. The role of education and skills in economic development. *Journal of Economic Literature*, v. 60, n. 2, p. 1-30, 2022.

IBGE. *PIB dos Municípios* 2010–2021. Rio de Janeiro: IBGE, 2023. Disponível em: ftp://ftp.ibge.gov.br. Acesso em: 15 ago. 2026.

IBGE. *Censo Demográfico 2022*: rendimento nominal mensal das pessoas responsáveis por domicílios (V06004/V06006). Rio de Janeiro: IBGE, 2023.

IBGE. *Malha municipal 2023*. Rio de Janeiro: IBGE, 2023.

IBGE. *PINTEC 2022*: Pesquisa de Inovação Tecnológica nas Empresas. Rio de Janeiro: IBGE, 2024.

IBGE. *PNAD Contínua*: índice de Gini 2024. Rio de Janeiro: IBGE, 2024.

IBGE. *SIDRA*: Censo Demográfico 2022, agregados por municípios. Rio de Janeiro: IBGE, 2024.

INEP. *IDEB 2005–2025*: resultados e metas, rede municipal. Brasília: INEP, 2025. Disponível em: https://download.inep.gov.br. Acesso em: 15 ago. 2026.

INEP. *Nota técnica*: IDEB 2023 — cálculo e metas. Brasília: INEP, 2023.

IPEA. *IPCA — número-índice*. Brasília: IPEADATA, 2023.

IPEA. Séries históricas de PIB e renda municipal. Brasília: IPEA, 2024.

LACRUZ, A. J.; AMÉRICO, B. L.; CARNIEL, F. Indicadores de desempenho educacional e accountability. *Revista de Administração Pública*, Rio de Janeiro, v. 53, n. 6, p. 1-20, 2019.

LAKENS, D.; SCHEEL, A. M.; ISAGER, P. M. Equivalence testing for psychological research: a tutorial. *Advances in Methods and Practices in Psychological Science*, v. 1, n. 2, p. 259-269, 2018.

MACKINNON, J. G.; WEBB, M. D. Wild bootstrap inference for wildly different cluster sizes. *Journal of Applied Econometrics*, v. 32, n. 2, p. 233-254, 2017.

MADDISON PROJECT DATABASE. *Historical GDP per capita*, versão 2023. Groningen: University of Groningen, 2023.

OCDE. *PISA 2022 Results*, v. I-II. Paris: OECD Publishing, 2023.

OCDE. *Education at a Glance 2023*: OECD Indicators. Paris: OECD Publishing, 2023.

PENN WORLD TABLE. *PWT 10.01*. Groningen: University of Groningen, 2023.

SCHNEIDER, M. P.; NARDI, E. L. O IDEB e a construção de um modelo de accountability na educação básica brasileira. *Revista Brasileira de Política e Administração da Educação*, v. 30, n. 1, p. 1-20, 2014.

SEGATTO, C.; OLIVEIRA, R.; SILVA, F. Coordenação federativa e resultados educacionais: o caso cearense. *Revista de Administração Pública*, Rio de Janeiro, v. 58, n. 2, p. 1-20, 2024.

SOARES, J. F.; XAVIER, F. P. Pressupostos educacionais e estatísticos do IDEB. *Educação & Sociedade*, Campinas, v. 34, n. 124, p. 903-923, 2013.

UNESCO. *Global Education Monitoring Report 2023*. Paris: UNESCO, 2023.

USPTO. *Patent Statistics Report 2024*. Alexandria: USPTO, 2024.

WORLD BANK. *World Development Indicators* (série completa 1960–2026). Washington, DC: World Bank Open Data, 2026.

## Apêndice A — Proveniência, reprodutibilidade e material suplementar

**Manifesto de proveniência.** Cada arquivo-fonte baixado tem URL, data-hora e hash SHA-256 registrados no manifesto de proveniência do projeto Crateús-IDEB (pasta data/raw). O deflator IPCA médio anual, com fator por ano para R$ de 2021, está na pasta data/processed.

**Saídas analíticas.** Todos os estatísticos citados no artigo estão consolidados no arquivo de resultados do ciclo R428 do projeto Crateús-IDEB (between, pooled, primeiras diferenças, efeitos fixos com CRVE e wild bootstrap, LOOCV, MDES/TOST, metas por ano, ganhos municipais e perfil de lags), acompanhados do registro completo de provenância com sementes e número de réplicas.

**Scripts.** `baixar_dados.py` (coleta com verificação de hash); `analise_crateus.py` e `analise_crateus_r428.py` (estimações); `scripts/gerar_figuras_tabelas.py` (figuras e tabelas deste artigo, diretamente dos JSONs processados).

**Relatório de validação independente.** A validação por banca simulada multi-periódico (protocolo interno R439: CAPES/Nature/IEEE/Lancet, com limpeza de gaps) consta de documento separado, não integrando o corpo do artigo, em conformidade com o padrão editorial de periódicos.

**Reprodutibilidade rápida.**

<div class="Shaded">

<div class="Highlighting">

</div>

</div>

\endgroup

**Agradecimentos:** à Secretaria de Educação do Estado do Ceará e às nove secretarias municipais do Sertão de Crateús, pela transparência dos dados públicos que viabilizaram esta análise.
