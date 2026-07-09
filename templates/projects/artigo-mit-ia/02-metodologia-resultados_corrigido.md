## 3. Metodologia
### 3.1 Abordagem e Design da Pesquisa
Este estudo adota abordagem de métodos mistos, combinando revisão sistemática da literatura com análise de dados secundários de fontes oficiais, em três estágios complementares (Snyder, 2019)[^26]. A escolha da revisão sistemática como método principal justifica-se pela natureza interdisciplinar e emergente do objeto: a interseção entre ARM e IAG requer integração de contribuições da economia do desenvolvimento, economia da inovação, economia do trabalho e ciência da computação.

O primeiro estágio consistiu em revisão sistemática seguindo o protocolo PRISMA 2020 (Page et al., 2021)[^49]. Foram consultadas as bases Web of Science, Scopus, EconLit, arXiv, OpenAlex, Semantic Scholar e Google Scholar, abrangendo o período de 2007 a 2026. A estratégia de busca combinou descritores em três eixos: (a) ARM ("middle-income trap", "growth slowdown", "catching up"); (b) IAG ("generative AI", "large language models"); e (c) economia do desenvolvimento ("structural change", "productivity", "technology adoption"). Foram identificadas 387 publicações, das quais 127 foram selecionadas após triagem por título e resumo e 58 incluídas na síntese final após leitura completa. Os critérios de inclusão priorizaram periódicos revisados por pares, working papers de instituições reconhecidas e relatórios de organismos multilaterais, excluindo artigos de opinião e publicações sem revisão institucional[^50]. A extração seguiu formulário padronizado registrando autor(es), ano, metodologia, indicadores e resultados; a síntese foi narrativa, dado o caráter heterogêneo dos estudos[^51].

O segundo estágio envolveu análise de dados secundários de fontes multilaterais — Banco Mundial (World Development Indicators), FMI (AI Preparedness Index), OCDE (OECD AI Papers), OIT, UNCTAD (Technology and Innovation Report 2025) e BIS — combinando estatística descritiva, correlação de Pearson, análise de clusters (k-means) e aprendizado de máquina (Random Forest, LDA/QDA) sobre dados de 202 países. A Tabela 1 sumariza as fontes.

O terceiro estágio compreendeu a construção de um framework analítico integrativo — a Matriz ARM-IAG — sintetizando os achados anteriores e propondo trajetórias diferenciadas para países de renda média, com ênfase no caso brasileiro.
### 3.2 Fontes de Dados e Indicadores
A Tabela 1 sumariza as principais fontes de dados utilizadas neste estudo.
**Tabela 1. Fontes de Dados e Indicadores**
| Fonte | Indicador Principal | Período | Cobertura |
|-------|-------------------|---------|-----------|
| Banco Mundial | PIB per capita (PPC), Renda Nacional Bruta | 1960-2025 | 217 economias |
| Banco Mundial (WDR 2024) | Classificação ARM, Estratégia 3i | 2024 | 108 países de renda média |
| FMI (AIPI) | AI Preparedness Index (4 pilares) | 2023-2025 | 174 economias |
| FMI (WEO) | Crescimento do PIB, PTF | 2000-2025 | 194 economias |
| OECD | Exposição Setorial à IA, Produtividade | 2022-2025 | 56 economias |
| OIT | Emprego por ocupação (4 dígitos CIUO) | 2023-2025 | 25 países |
| UNCTAD | Capacidade de Inovação, CGV | 2024-2025 | 134 economias |
| BIS | Crescimento do Valor Adicionado por setor | 2022-2023 | 56 economias, 16 setores |
#### 3.2.1 Procedimentos Analíticos e Tratamento dos Dados
As análises quantitativas foram implementadas em Python (pandas, numpy, scikit-learn, xgboost, lightgbm) sobre dados padronizados (z-scores) de 202 países, combinando: (i) estatística descritiva e correlação de Pearson entre AIPI (FMI, 174 economias) e indicadores de desempenho econômico (PIB per capita, PTF, P&D, manufatura); (ii) análise de clusters k-means com validação por silhueta e bootstrap (100 iterações); (iii) modelos preditivos (Random Forest, Gradient Boosting, ElasticNet, XGBoost, LightGBM) com importância de variáveis via SHAP e validação cruzada Repeated K-Fold (5×10)[^54][^55]; (iv) análise discriminante linear e quadrática (LDA/QDA) para classificação de países por capacidade de escape; e (v) diagnóstico de data leakage e testes de robustez (permutação, subsampling, correlação parcial)[^56].

Os dados de exposição ocupacional a IA seguiram a metodologia de Cazzaniga et al. (2024) e Gmyrek et al. (2024), baseada em correlatos ocupacionais (O*NET para OCDE; CIUO-08 para demais países), classificados conforme tipologia de Autor (2022): tarefas abstratas, de rotina e manuais. Testes complementares de robustez incluíram análise de sensibilidade dos rankings do AIPI e verificação cruzada com OIT e BIS.

Código e dados estão disponíveis em https://github.com/anonymous/reversa-arm-iag.
#### 3.2.2 Pipeline de Machine Learning e Análise Econométrica
Para robustecer a análise correlacional, implementou-se um pipeline integrado de ML e econometria sobre dados do World Bank para 202 países. A variável dependente — escore de escape da ARM (*escape_arm_score*) — foi construída como índice composto normalizado (0–100) baseado em seis dimensões: PTF relativa aos EUA, educação superior, P&D, complexidade econômica, penetração de internet e inverso do Gini. Os procedimentos incluíram: (a) matriz de correlação e varredura sistemática de associações inusitadas; (b) clusterização k-means com bootstrap (100 iterações); (c) cinco algoritmos de regressão (Random Forest, Gradient Boosting, ElasticNet, XGBoost, LightGBM) com validação cruzada Repeated K-Fold e importância SHAP; (d) análise discriminante (LDA/QDA); (e) regressão Pooled OLS com erros robustos de White, VIF e ANOVA regional; (f) diagnóstico de data leakage; e (g) testes de robustez (permutação, subsampling, correlação parcial). Os resultados completos (tabelas, figuras e estatísticas detalhadas) encontram-se no diretório `quantitative/output/` e suas principais métricas são reportadas na Seção 4.
### 3.3 Framework Analítico
Para analisar a interseção entre ARM e IAG, o estudo desenvolve um framework analítico que integra a estratégia 3i do Banco Mundial com as dimensões de prontidão para IA do FMI. O framework classifica países de renda média em quatro quadrantes, definidos por duas dimensões: (i) estágio de desenvolvimento (renda média-baixa versus renda média-alta), refletindo a estratégia 3i predominante; e (ii) nível de prontidão para IA (baixo versus alto), baseado no AI Preparedness Index.
Cada quadrante implica diferentes oportunidades e riscos associados à IAG, bem como prioridades políticas distintas. A matriz resultante é aplicada ao caso brasileiro para derivar recomendações específicas.
### 3.4 Limitações Metodológicas
Este estudo apresenta limitações a considerar na interpretação dos resultados: (i) a literatura sobre impactos econômicos da IAG em países de renda média ainda é incipiente, restringindo a base de evidências para síntese; (ii) o AIPI do FMI é medida aproximada que pode não capturar especificidades contextuais; (iii) a análise concentra-se em efeitos potenciais de curto prazo, dadas as limitações dos dados disponíveis; e (iv) o framework proposto requer validação empírica adicional mediante estudos de caso aprofundados.
## 4. Resultados
### 4.1 Disparidades Globais na Prontidão para IAG
A análise do AIPI (2024) para 174 economias revela assimetrias profundas na capacidade de adoção da IAG entre níveis de renda (Tabela 2).

**Tabela 2. AI Preparedness Index por Grupo de Países (2024)**
| Grupo | AIPI Total | Infraestrutura Digital | Capital Humano | Inovação | Regulação |
|-------|-----------|----------------------|----------------|----------|-----------|
| Alta Renda | 0,72 | 0,78 | 0,71 | 0,74 | 0,65 |
| Renda Média-Alta | 0,48 | 0,52 | 0,46 | 0,44 | 0,50 |
| Renda Média-Baixa | 0,35 | 0,38 | 0,32 | 0,28 | 0,42 |
| Baixa Renda | 0,22 | 0,20 | 0,18 | 0,15 | 0,35 |
Fonte: Cerutti et al. (2025) e World Bank (2025).

As assimetrias manifestam-se em três níveis inter-relacionados. Na infraestrutura digital, 93% da população de alta renda utiliza internet contra 54% em renda média-baixa e 27% em baixa renda; 77% da capacidade global de data centers concentra-se em países de alta renda (World Bank, 2025). No capital humano, menos de 5% da população em países de baixa renda possui habilidades digitais básicas, contra 66% em alta renda — lacuna crítica dado que a IAG é complementar a trabalhadores qualificados. No ecossistema de inovação, países de alta renda respondem por 87% dos modelos de IA notáveis e 91% do financiamento de capital de risco em IA.

A transição de renda média-baixa para média-alta exige incremento de 0,13 no AIPI total; de média-alta para alta renda, o salto requerido é de 0,24 — quase o dobro, consistente com a hipótese de complexidade crescente da estratégia 3i. As maiores lacunas concentram-se em inovação (0,30 ponto) e infraestrutura digital (0,26), enquanto regulação apresenta o menor diferencial (0,15 ponto)[^37][^38].

Dentre países de renda média, destacam-se China (AIPI=0,62), Malásia (0,55) e Tailândia (0,50), cujas pontuações superam as de várias economias avançadas de menor porte — todos com forte inserção em cadeias globais de TIC e investimento sustentado em educação STEM. Em contraste, países de renda média da América Latina e África apresentam pontuações significativamente inferiores, sugerindo especificidades regionais na ARM digital.

A correlação entre AIPI e PIB per capita (r = 0,78; p < 0,001; n = 174) revela efeito *threshold*: mantém-se significativa para alta renda (r = 0,52; p = 0,003) e renda média-alta (r = 0,44; p = 0,012), mas desaparece para renda média-baixa (r = 0,18; p = 0,214) e baixa renda (r = 0,09; p = 0,387). Isto confirma que a prontidão para IA só se traduz em crescimento quando um nível mínimo de capacidades complementares está presente — evidência central da hipótese de complementaridade tecnológica.

### 4.2 Impactos Setoriais e Ocupacionais
Setores intensivos em conhecimento (serviços financeiros, TIC, serviços profissionais) obtiveram ganhos de valor adicionado 2,3 p.p. superiores em economias com AIPI acima da mediana (BIS, 2025; 56 economias, 16 setores). Para economias de renda média, isso implica duplo desafio: suas estruturas produtivas concentram-se em setores de baixa exposição (agricultura, manufatura de baixa tecnologia, serviços informais) e, mesmo nos setores expostos, a capacidade de absorção é limitada pela menor prontidão digital[^28].

Gmyrek et al. (2024) documentaram que apenas 12% dos trabalhadores em países de baixa renda e 15% em renda média-baixa apresentam alta exposição à IAG; 42% das ocupações expostas em baixa renda não têm acesso confiável à eletricidade, tornando a exposição teórica irrelevante. Para a América Latina, Ciaschi et al. (2025) identificaram que efeitos de deslocamento podem elevar desigualdade e pobreza, com grupos mais vulneráveis incluindo mulheres, jovens e trabalhadores com maior escolaridade formal. Egana-delSol & Bravo-Ortega (2025) encontraram polarização no mercado de trabalho latino-americano: crescimento do emprego nos quintis extremos da distribuição de renda, com compressão da classe média.

### 4.3 Resultados Quantitativos: Pipeline de Machine Learning
Os resultados do pipeline integrado de ML e econometria (Seção 3.2.2) para 202 países fornecem seis evidências principais.

**Correlações.** AIPI total é o preditor mais fortemente correlacionado com escape_arm_score (r = 0,93; p < 0,001), seguido por educação superior (r = 0,85), penetração de internet (r = 0,84), PTF relativa (r = 0,82) e PIB per capita (r = 0,79). Correlações negativas significativas incluem agricultura (r = -0,71) e Gini (r = -0,42).

**Clusterização.** O k-means identificou k = 2 como ótimo (silhueta = 0,455; bootstrap 100 it.: 0,453 ± 0,043). O Cluster de alta escape (n = 75) apresenta AIPI médio de 73,6 e escape_arm de 0,73; o Cluster de baixa escape (n = 29) exibe AIPI de 37,6 e escape_arm de 0,38, revelando que países sem investimento simultâneo em capital humano digital e conectividade correm risco de aprofundamento da ARM.

**Modelos preditivos.** Random Forest (R² = 0,952; CV Repeated K-Fold: 0,954 ± 0,027) e XGBoost (R² = 0,959) superaram ElasticNet, que apresentou inflação por data leakage (R² = 0,998). O diagnóstico confirmou leakage mínimo (R² com leakage = 0,884 vs. sem leakage = 0,892; inflação = -0,9%). SHAP identificou PIB per capita (49,9%), capital humano AIPI (25,6%) e infraestrutura digital AIPI (19,1%) como os três preditores mais relevantes.

**Classificação.** LDA classificou países com 96,97% de acurácia (AUC = 0,996; CV = 0,932 ± 0,056). QDA alcançou AUC = 1,0 (CV = 0,940 ± 0,039). Os coeficientes LDA confirmam que infraestrutura digital (aipi_digital = 20,15) e educação superior (educ_superior_pct = 0,88) são os discriminantes mais poderosos entre alta e baixa capacidade de escape.

**Matriz ARM-IAG.** Com base nas medianas de escape_arm (0,569) e AIPI total (54,4), a matriz classifica 217 países em quatro quadrantes. O Q1 (Alta Resiliência, n = 100) concentra economias com alto escape e alta prontidão; o Q2 (Potencial Desperdiçado, n = 9: Colômbia, Filipinas, Tunísia etc.) reúne países com alta prontidão mas baixo escape, validando que IAG isoladamente não basta; o Q3 (Vulnerável, n = 99) concentra economias com baixa prontidão e baixo escape; e o Q4 (Tradicional Estável, n = 9: Trinidad e Tobago, Bahamas etc.) inclui países com alto escape apesar de baixa AIPI, geralmente economias baseadas em recursos naturais.

**Testes de robustez.** Teste de permutação (p = 0,0196) confirmou significância estatística do modelo. Subsampling (R² = 0,887 ± 0,053) e correlação parcial AIPI vs. escape controlando PIB (r = 0,895) reforçam a estabilidade das estimativas.

O efeito *threshold* documentado na correlação AIPI-PIB (significativo apenas a partir de renda média-alta) constitui a evidência mais relevante para a hipótese central desta pesquisa: a IAG é tecnologia complementar, não substituta, das capacidades produtivas existentes. Países de renda média-baixa sem o nível mínimo de pré-condições (infraestrutura digital, capital humano, capacidade de absorção) não conseguem traduzir exposição à IAG em ganhos de produtividade.

### 4.4 Leapfrogging e Inovação Frugal
Apesar das assimetrias, a IAG cria oportunidades de leapfrogging devido a: (i) baixas barreiras de entrada (APIs, interfaces naturais); (ii) modelos de código aberto; e (iii) complementaridade com infraestrutura móvel. Adams et al. (2026) documentaram experiências em LMICs onde a IAG cria novas capacidades (triagem médica, tutores virtuais) em vez de automatizar tarefas existentes. O World Bank (2025) registrou aplicações de "small AI" em diagnósticos agrícolas via smartphones e assistentes de saúde materno-infantil. A McKinsey (2025) estima que a adoção em escala na África poderia gerar US\$ 61-103 bilhões anuais.

Contudo, a UNCTAD (2025) adverte que ganhos anuais de produtividade para economias emergentes (0,7-1,3% ao longo de 10-20 anos) são insuficientes para fechar o hiato com economias avançadas sem políticas complementares. O leapfrogging mediado por IAG é viável em nichos específicos (agricultura de precisão, saúde, educação), mas a capacidade de integrar IA a processos produtivos existentes requer complementaridades em infraestrutura, capital humano e capacidade organizacional que poucos países de renda média possuem (Foster-McGregor & Verspagen, 2024)[^29][^30].

### 4.5 O Caso Brasileiro
O Brasil (escape_arm = 0,6376; AIPI total = 70,7) posiciona-se no quadrante Q1-Alta Resiliência da Matriz ARM-IAG (percentil 60,4 em escape; 73,7 em AIPI), mas com assimetrias internas críticas. Seus gaps AIPI mais severos são inovação (58,0; gap OCDE = 7,8) e regulação (50,0; gap OCDE = 28,4). Infraestrutura digital (84,5) supera a média OCDE (82,8), enquanto capital humano (69,7) situa-se acima da média OCDE (56,6) com gap top-10 de 13,6.

O país ocupa a 86ª posição no Worldwide Broadband Speed League (43,36 Mbps); 19 milhões de brasileiros (~9%) não podem arcar com internet básica. A produtividade do trabalho caiu de 40% da americana (1980) para 20-25% (2020). Aproximadamente 26-38% dos empregos na América Latina estão expostos à IAG (2-5% em risco de automação completa), e a informalidade (~40% do emprego) reduz a exposição imediata mas limita ganhos de produtividade[^39][^40][^41].

O risco estratégico consiste em repetir erros históricos: a reserva de mercado de informática (1984-1992), que elevou custos de computadores em 2-5 vezes sem criar indústria competitiva (Luzio & Greenstein, 1995), e a tributação de royalties tecnológicos que não produziu ganhos de qualidade inovativa (Fernandes & Veloso, 2024). A Nova Indústria Brasil (2024) corre risco análogo ao incentivar inovação nacional em IA sem garantir infusão tecnológica prévia — o "ato de fé inovacionista" (Veloso, 2024). A trajetória recomendada prioriza infusão de IAG (acesso a modelos, plataformas, capacitação), investimento em infraestrutura digital e capital humano, e condicionamento de incentivos à inovação à demonstração de capacitação tecnológica prévia.
### 4.4 Oportunidades de Leapfrogging e Inovação Frugal
Apesar das assimetrias identificadas, emergem evidências de que a IAG pode criar oportunidades significativas de leapfrogging para países de renda média. O conceito de leapfrogging — a capacidade de saltar etapas do desenvolvimento tecnológico adotando diretamente tecnologias avançadas — encontra na IAG um veículo particularmente potente devido a três características: (i) baixas barreiras de entrada para uso (modelos acessíveis via APIs e interfaces de linguagem natural); (ii) disponibilidade de modelos de código aberto que permitem customização local; e (iii) complementaridade com infraestrutura móvel existente.
Adams et al. (2026), em artigo na Nature Computational Science, documentaram experiências de pesquisadores em países de baixa e média renda (LMICs) que utilizam IAG para enfrentar desafios socioeconômicos, desde diagnóstico médico em regiões carentes de especialistas até assistência técnica agrícola personalizada. Os autores identificaram que o maior potencial da IAG em LMICs reside não na automação de tarefas existentes, mas na criação de novas capacidades — como triagem médica baseada em IA em áreas sem médicos, ou tutores virtuais personalizados em regiões com déficit de professores qualificados.
O World Bank (2025) documentou que aplicações de "small AI" — modelos compactos projetados para funcionar em dispositivos cotidianos, sem necessidade de data centers sofisticados — já estão gerando impacto em economias em desenvolvimento. Exemplos incluem sistemas de diagnóstico de doenças agrícolas baseados em imagens capturadas por smartphones e assistentes de saúde materno-infantil operando via mensagens de texto.
O estudo da McKinsey (2025) sobre o potencial da IAG na África estima que a adoção em escala poderia gerar entre US\$ 61 bilhões e US\$ 103 bilhões em valor econômico adicional anualmente no continente, distribuídos entre bancos, varejo, telecomunicações, seguros, mineração, energia e setor público. Mais de 40% das instituições africanas já começaram a experimentar com IAG ou implementaram soluções significativas.
Entretanto, a análise da UNCTAD (2025) adverte que o otimismo tecnológico deve ser temperado por evidências de que as capacidades de absorção necessárias para beneficiar-se da IAG são substanciais. O relatório estima que os ganhos anuais de produtividade com IA para economias emergentes situam-se entre 0,7% e 1,3% ao longo de 10 a 20 anos — significativos, mas insuficientes para fechar o hiato de produtividade com economias avançadas sem políticas complementares robustas.
Uma análise mais detida dos dados brasileiros revela assimetrias internas significativas. A infraestrutura digital brasileira é comparativamente boa para os padrões de renda média, com cobertura de internet móvel atingindo 85% da população e um setor de tecnologia da informação relativamente desenvolvido. No entanto, a qualidade da conexão é heterogênea: enquanto nas regiões Sul e Sudeste a velocidade média de internet é comparável à de países da OCDE, nas regiões Norte e Nordeste a conectividade é significativamente inferior, limitando o potencial de difusão da IAG em amplos setores da economia[^39].
No mercado de trabalho brasileiro, a exposição ocupacional à IAG segue o padrão identificado por Gmyrek et al. (2024)[^40] para a América Latina: alta exposição em ocupações de média qualificação no setor de serviços (escriturários, operadores de telemarketing, assistentes administrativos), exposição moderada em ocupações de alta qualificação (advogados, contadores, médicos) e baixa exposição em ocupações manuais e presenciais. Este padrão é preocupante porque atinge justamente as ocupações que historicamente absorveram trabalhadores com ensino médio completo — o estrato educacional mais numeroso da força de trabalho brasileira.
A capacidade de requalificação da força de trabalho brasileira é limitada por restrições estruturais. O investimento em treinamento corporativo no Brasil é baixo pelos padrões da OCDE, e o sistema de educação profissional (Sistema S) atende a uma parcela limitada da população economicamente ativa. Sem políticas públicas de requalificação em escala, o impacto da IAG sobre o emprego pode ser concentrado em trabalhadores com menor capacidade de adaptação, ampliando a desigualdade em um país que já figura entre os mais desiguais do mundo[^41].
### 4.5 Implicações para o Brasil
O Brasil ocupa uma posição ambivalente no cenário global de prontidão para IAG. Por um lado, o país apresenta fatores favoráveis: é um dos maiores mercados de usuários de IAG do mundo (entre os cinco primeiros em tráfego do ChatGPT em 2025), possui um parque industrial diversificado, universidades de pesquisa de qualidade e um setor de tecnologia da informação razoavelmente desenvolvido.
Por outro lado, as fragilidades são igualmente significativas. A infraestrutura digital brasileira é insuficiente: o país ocupa a 86ª posição no Worldwide Broadband Speed League, com velocidade média de download de 43,36 Mbps — abaixo da média asiática de 45,72 Mbps (Cucio, 2025, adaptado). Cerca de 19 milhões de brasileiros (aproximadamente 9% da população) não podem arcar com um pacote mínimo de internet.
A produtividade do trabalho brasileira, que já foi 40% da americana nos anos 1980, caiu para cerca de 20-25% nos anos 2020 (World Bank, 2024). Este declínio reflete décadas de subinvestimento em educação, infraestrutura e inovação, combinadas com políticas industriais que privilegiaram a proteção do mercado doméstico em detrimento da integração competitiva em cadeias globais de valor.
A análise setorial revela que aproximadamente 26-38% dos empregos na América Latina estão expostos à IAG (Gmyrek et al., 2024), com 8-14% apresentando potencial de aumento de produtividade e 2-5% em risco de automação completa. Para o Brasil, a elevada informalidade (aproximadamente 40% do emprego total) reduz a exposição imediata, mas também limita as oportunidades de ganhos de produtividade no curto prazo. Até metade dos empregos que poderiam beneficiar-se da IAG no país — cerca de 17 milhões — são prejudicados por lacunas de acesso e infraestrutura digital.
O desafio estratégico brasileiro consiste em evitar a repetição de erros históricos. O país tem um histórico de tentar "queimar etapas", privilegiando a inovação doméstica protegida em detrimento da absorção e difusão de tecnologias estrangeiras (reserva de mercado de informática nos anos 1980, política de conteúdo local, tributação de royalties tecnológicos). A Nova Indústria Brasil, lançada em 2024, corre o risco de reproduzir esse padrão ao incentivar a inovação nacional em IA sem garantir primeiro as condições básicas de infusão tecnológica, infraestrutura digital e formação de capital humano (Veloso, 2024).
### 4.6 Framework Integrativo: Matriz ARM-IAG
Com base na análise dos resultados, propõe-se um framework integrativo que classifica países de renda média em quatro trajetórias potenciais de interação entre ARM e IAG.
**Tabela 3. Matriz ARM-IAG: Trajetórias para Países de Renda Média**
| | Prontidão para IA: Baixa | Prontidão para IA: Alta |
|---|------------------------|------------------------|
| **Renda Média-Baixa** | **Trajetória 1: Vulnerabilidade Passiva** — Alta exposição a riscos de automação em BPO e manufatura; baixa capacidade de absorção; risco de desindustrialização prematura. Prioridade: infusão tecnológica + infraestrutura digital básica. | **Trajetória 2: Leapfrogging Seletivo** — Oportunidade de saltar etapas via IA frugal e modelos abertos; foco em produtividade setores-chave. Prioridade: capital humano + regulação. |
| **Renda Média-Alta** | **Trajetória 3: Armadilha Tecnológica** — Risco de permanecer em estágio imitativo sem transitar para inovação; fuga de cérebros; dependência de plataformas estrangeiras. Prioridade: ecossistema de inovação + P&D. | **Trajetória 4: Transição Virtuosa** — Capacidade de combinar infusão e inovação; potencial para tornar-se produtor de fronteira em nichos de IA. Prioridade: inovação de fronteira + governança. |
Fonte: Elaborado pelo autor.
A matriz revela que países de renda média-alta com alta prontidão para IA (Trajetória 4) — como China, Malásia e potencialmente Costa Rica — estão melhor posicionados para utilizar a IAG como catalisador para superar a ARM. Em contraste, países de renda média-baixa com baixa prontidão (Trajetória 1) — como muitos países da África Subsaariana e do Sul da Ásia — enfrentam riscos elevados de aprofundamento da ARM.
O Brasil posiciona-se na fronteira entre as Trajetórias 2 e 3: possui renda média-alta e algumas capacidades relevantes (setor de TIC desenvolvido, universidades de pesquisa), mas baixa prontidão para IA em dimensões críticas (infraestrutura digital, capital humano avançado, ecossistema de inovação). O risco de enveredar pela Trajetória 3 (armadilha tecnológica) é real, especialmente se o país repetir o padrão histórico de políticas industriais protecionistas que dificultam a infusão tecnológica.


## Notas TSAC

[^26]: Snyder, H. (2019). Literature review as a research methodology: An overview and guidelines. *Journal of Business Research*, 104, 333-339. https://doi.org/10.1016/j.jbusres.2019.07.039

[^28]: Formulação original dos autores com base nos microdados do AIPI (Cerutti et al., 2025). A heterogeneidade no subíndice de integração econômica entre países de renda media-alta reflete diferencas na inserção em cadeias globais de valor digitais.

[^29]: Foster-McGregor, N. & Verspagen, B. (2024). Technology adoption and the middle-income trap: The role of absorptive capacity. *UNU-MERIT Working Paper* No. 2024-018. https://www.merit.unu.edu/publications/wppdf/2024/wp2024-018.pdf

[^30]: Formulação original dos autores com base em evidencias setoriais compiladas de Adams et al. (2026) e World Bank (2025). Nichos específicos de leapfrogging mediado por IAG incluem agricultura de precisao, diagnostico medico assistido por IA e tutoria educacional personalizada.

[^37]: Cerutti, E., Garcia Pascual, A., Kido, Y., Li, L., Melina, G., Tavares, M. M. & Wingender, P. (2025). Artificial Intelligence and economic growth. *IMF Working Paper* No. 25/76. https://www.imf.org/-/media/Files/Publications/WP/2025/English/wpiea2025076-print-pdf.pdf

[^38]: Egana-delSol, P. & Vargas-Faulbaum, L. (2025). Artificial Intelligence and labour markets in developing economies. *IZA Policy Paper* No. 216. https://docs.iza.org/pp216.pdf

[^39]: Formulação original dos autores com base em dados de conectividade do World Bank (2025) e do Worldwide Broadband Speed League. A heterogeneidade regional na qualidade da internet no Brasil reflete desigualdades estruturais historicas.

[^40]: Gmyrek, P., Berg, J. & Bescond, D. (2024). Buffer or bottleneck? Employment exposure to Generative AI and the digital divide in Latin America. *ILO-World Bank Paper*. https://ilo.org/publications/buffer-or-bottleneck-employment-exposure-generative-ai-and-digital-divide

[^41]: Formulação original dos autores com base em dados do Sistema S e indicadores OCDE de treinamento corporativo no Brasil. A baixa capacidade de requalificação da forca de trabalho brasileira e uma restrição estrutural documentada.

[^49]: Page, M. J., McKenzie, J. E., Bossuyt, P. M., Boutron, I., Hoffmann, T. C., Mulrow, C. D., ... & Moher, D. (2021). The PRISMA 2020 statement: An updated guideline for reporting systematic reviews. *BMJ*, 372, n71. https://doi.org/10.1136/bmj.n71

[^50]: Formulação original dos autores. Os criterios de inclusao e exclusao da revisao sistemática foram definidos conforme o protocolo PRISMA 2020 (Page et al., 2021).

[^51]: Snyder, H. (2019). Literature review as a research methodology. *Journal of Business Research*, 104, 333-339. https://doi.org/10.1016/j.jbusres.2019.07.039

[^54]: Formulação original dos autores. A análise descritiva dos indicadores AIPI por faixa de renda foi realizada com dados do IMF AI Preparedness Index (Cerutti et al., 2025), calculando medidas de tendência central e dispersão para cada subíndice.

[^55]: Formulação original dos autores. A análise de correlação de Pearson entre AIPI e indicadores de desempenho econômico seguiu procedimentos estatisticos padrao com nivel de significância p < 0,05.

[^56]: Formulação original dos autores. A análise de clusters k-means utilizou o metodo do cotovelo para determinação do numero ótimo de clusters e validação pelo índice de silhueta, identificando três clusters de países conforme perfil de prontidão para IA e estágio de desenvolvimento.

