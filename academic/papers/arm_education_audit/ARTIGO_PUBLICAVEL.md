# Educação terciária e trajetórias de renda: evidência associativa de painel com validação cruzada agrupada por país (Argentina, Brasil, Chile, China, Coreia do Sul, Singapura e Vietnã, 1960–2023)

> **Status: versão candidata a submissão** — manuscrito em preparação, sujeito a
> revisão por pares. Nenhuma alegação de aceite, classificação de periódico ou
> prontidão editorial é feita neste documento. Todas as tabelas e números foram
> gerados por script a partir de dados oficiais do Banco Mundial (WDI) com cache
> auditável (SHA-256). Repositório de auditoria: `academic/papers/arm_education_audit/`.

---

## Resumo

Este estudo examina a associação entre educação terciária e nível de renda per
capita em sete economias — Argentina, Brasil, Chile, China, Coreia do Sul,
Singapura e Vietnã — entre 1960 e 2023, a partir de dados oficiais do World
Development Indicators (Banco Mundial). A matrícula terciária bruta correlaciona
0,934 com o logaritmo do PIB per capita em níveis (n = 198), mas a associação
cai para 0,181 quando se consideram primeiras diferenças por país (n = 180),
indicando que grande parte da correlação reflete tendências comuns. A
estabilidade da correlação em níveis é verificada por leave-one-country-out
(ρ entre 0,888 e 0,968; excluindo Singapura, 0,935). Em painel com efeitos
fixos de país e defasagem de cinco anos, cada ponto percentual de matrícula
terciária associa-se a um log-PIB per capita 0,022 mais alto
(IC95% 0,017–0,026). Um exercício de aprendizado de máquina (florestas
aleatórias) classifica crescimento acima da mediana com área sob a curva ROC de
0,796 quando o conjunto de treino compartilha países com o de teste, mas de
apenas 0,591 sob validação cruzada leave-one-country-out — evidência de que, com
sete países, a capacidade preditiva não generaliza para economias não vistas. Os
resultados sustentam a associação positiva entre escolaridade terciária e renda,
mas não identificam relação de determinação; a generalização entre países permanece uma
limitação estrutural do desenho.

**Palavras-chave:** educação terciária; renda per capita; países de renda média;
validação cruzada por país; dados de painel; aprendizado de máquina.

## Abstract

This study examines the association between tertiary education and income per
capita in seven economies — Argentina, Brazil, Chile, China, South Korea,
Singapore and Vietnam — between 1960 and 2023, using official World Development
Indicators (World Bank) data. Gross tertiary enrollment correlates 0.934 with
log income per capita in levels (n = 198), but the association drops to 0.181
under country-specific first differences (n = 180), indicating that much of the
level correlation reflects common trends. Level-correlation stability is
veriﬁed by leave-one-country-out (ρ ranging from 0.888 to 0.968; excluding
Singapore, 0.935). In a country-fixed-effects panel with a five-year lag, each
percentage point of tertiary enrollment is associated with log income per
capita 0.022 higher (95% CI 0.017–0.026). A machine-learning exercise
(random forests) classifies above-median growth with a ROC area of 0.796 when
training and test sets share countries, but only 0.591 under
leave-one-country-out cross-validation — evidence that, with seven countries,
predictive capacity does not generalize to unseen economies. The results support
a positive association between tertiary schooling and income, but do not
identify a directional relationship; cross-country generalization remains a structural
limitation of the design.

**Keywords:** tertiary education; income per capita; middle-income economies;
cross-validation by country; panel data; machine learning.

---

## 1. Introdução

A relação entre escolaridade e crescimento econômico é um dos temas mais
persistentes da economia do desenvolvimento. Desde os modelos de capital humano
de Lucas (1988) e Romer (1990), a educação superior ocupa lugar central nas
narrativas de convergência e de diferenciação entre economias. Trabalhos
empíricos de longo prazo documentam associações positivas entre anos de
escolaridade da população adulta e nível de renda (Barro e Lee, 2013;
Mankiw; Romer; Weil, 1992), enquanto revisões do retorno privado e social da
educação apontam ganhos substanciais, embora declinantes nos níveis mais altos
de escolaridade (Psacharopoulos; Patrinos, 2018). Em contrapartida, análises
que consideram a qualidade do aprendizado e o contexto institucional moderam a
magnitude dessas associações (Hanushek; Woessmann, 2010; Pritchett, 2001).

Um debate paralelo concentra-se na chamada "armadilha da renda média": a
observação de que economias de renda média tendem a desacelerar antes de
alcançar o grupo de alta renda (Eichengreen; Park; Shin, 2012; Aiyar et al.,
2018; Felipe; Abdon; Kumar, 2012; Im; Rosenblatt, 2015). Nesse debate, a
educação terciária aparece com frequência como condicionante da capacidade de
inovar e de absorver tecnologia (Acemoglu; Gallego; Robinson, 2014; Rodrik,
2016). O Brasil, em particular, combina alta desigualdade educacional com
crescimento modesto, o que torna o tema relevante para a política pública
(World Bank, 2024).

Este artigo contribui com um exercício empírico transparente e auditável: a
partir de dados oficiais do Banco Mundial, examinamos a associação entre
matrícula terciária bruta, gasto educacional e dispêndio em pesquisa e
desenvolvimento, de um lado, e nível de renda per capita, de outro, em um
painel de sete países ao longo de 64 anos. A contribuição não é a novidade
metodológica, mas o rigor de reprodutibilidade: toda a cadeia de dados, código
e resultados está disponível, e as inferências são submetidas a validações
cruzadas por país e por tempo.

A seguir, apresentamos a literatura (seção 2), os dados e o método, com ênfase
nas decisões de validação (seção 3), os resultados (seção 4) e a discussão, com
as limitações e a conclusão (seções 5 e 6).

## 2. Revisão da literatura

A literatura empírica sobre educação e crescimento divide-se em duas tradições.
A primeira estima regressões de crescimento com estoques de capital humano e
encontra associações positivas, porém sensíveis à especificação (Mankiw; Romer;
Weil, 1992). A segunda enfatiza a qualidade e o uso do capital humano: países
com baixa qualidade educacional podem acumular anos de estudo sem que isso se
traduza em crescimento (Pritchett, 2001; Hanushek; Woessmann, 2010). No plano
da educação terciária especificamente, a literatura sobre mudança estrutural
sugere que a capacidade de produzir e absorver tecnologia depende de formação
avançada (Acemoglu; Gallego; Robinson, 2014; Rodrik, 2016), mas a evidência
empírica direta em painéis de países em desenvolvimento é limitada.

No debate sobre a armadilha da renda média, o papel da educação aparece de
forma indireta. Eichengreen, Park e Shin (2012) documentam desacelerações
frequentes em economias de renda média e associam a probabilidade de
desaceleração a fatores como câmbio, demografia e escolaridade. Aiyar et al.
(2018) estimam que a probabilidade de desaceleração cresce com a proximidade da
fronteira tecnológica. Felipe, Abdon e Kumar (2012) e Im e Rosenblatt (2015)
questionam, por sua vez, a própria existência de um limiar empírico estável de
renda média, apontando a heterogeneidade das trajetórias.

Dessa literatura emergem duas lições metodológicas. A primeira é que correlações
de níveis entre países são dominadas por diferenças permanentes de
desenvolvimento, o que torna indispensável o uso de variações no tempo dentro
dos países. A segunda é que o número reduzido de países em qualquer amostra de
renda média limita a validade externa de exercícios preditivos; validações
cruzadas que separam países de treino e de teste são recomendáveis para
caracterizar essa limitação, em vez de ocultá-la.

## 3. Dados e método

### 3.1 Dados

Os dados provêm da API do World Development Indicators do Banco Mundial
(World Bank, 2024), com download em 12 de agosto de 2026 e cache local
imutável (URL, timestamp UTC, status HTTP e hash SHA-256 de cada arquivo). A
amostra compreende sete países: Argentina, Brasil, Chile, China, Coreia do Sul,
Singapura e Vietnã (1960–2023), selecionados por seu protagonismo no debate
brasileiro sobre a renda média e por sua diversidade de trajetórias.

As variáveis utilizadas são: PIB per capita em US$ constantes de 2015
(NY.GDP.PCAP.KD); crescimento anual do PIB per capita (NY.GDP.PCAP.KD.ZG);
matrícula terciária bruta como proporção do grupo etário correspondente
(SE.TER.ENRR); gasto público em educação como proporção do PIB
(SE.XPD.TOTL.GD.ZS); dispêndio em pesquisa e desenvolvimento como proporção do
PIB (GB.XPD.RSDV.GD.ZS); e população urbana como proporção do total
(SP.URB.TOTL.IN.ZS). O painel completo tem 448 observações país-ano, com
cobertura parcial das variáveis educacionais (a matrícula terciária tem 204
observações; o gasto educacional, 219; e o dispêndio em P&D, 159). Nenhuma
observação ausente foi preenchida por imputação ou tratada como zero.

### 3.2 Estratégia empírica

A estratégia combina quatro níveis de análise, do mais descritivo ao mais
estruturado.

**(a) Correlações em níveis e em primeiras diferenças.** Para cada par de
variáveis, reportamos o coeficiente de correlação de Spearman em níveis e a
correlação das primeiras diferenças por país. As primeiras diferenças removem a
tendência comum de longo prazo e aproximam a variação dentro do país, reduzindo
o risco de correlação espúria por co-movimento de tendências.

**(b) Validação cruzada leave-one-country-out (LOOCV) das correlações em
níveis.** Reestimamos a correlação matrícula terciária × log(PIB per capita)
sete vezes, excluindo um país de cada vez, para verificar se o resultado depende
de uma economia específica. Os conjuntos de treino e de teste são disjuntos por
construção (Tabela 3).

**(c) Painel com efeitos fixos.** Estimamos uma regressão de log(PIB per
capita) sobre a matrícula terciária defasada em cinco anos, com efeitos fixos de
país (transformação within), e uma especificação adicional com efeitos fixos de
país e de ano. Os erros padrão são homocedásticos e o número de países (sete) é
pequeno, o que recomenda leitura cautelosa dos intervalos.

**(d) Exercício preditivo com validação agrupada.** Treinamos florestas
aleatórias (Breiman, 2001) para classificar anos de crescimento do PIB per
capita acima da mediana do período, usando matrícula terciária, gasto
educacional, dispêndio em P&D e urbanização como características. Comparamos
duas formas de partição: (i) partição aleatória por linha, em que o mesmo país
aparece no treino e no teste; e (ii) leave-one-country-out, em que o país de
teste é inteiramente ausente do treino. A diferença entre as duas áreas sob a
curva ROC caracteriza o grau de identificabilidade entre países: se a
classificação depende de características específicas dos países de treino, o
modelo não generaliza.

### 3.3 Reproducibilidade

Todos os resultados são produzidos pelo script
`scripts/analyze_publishable.py`, que lê exclusivamente o painel auditado e
escreve tabelas e um arquivo de proveniência (`outputs/publishable_tables/`).
Cada número citado neste artigo tem entrada correspondente em
`provenance.json`. A execução é offline e determinística (sementes fixas).

## 4. Resultados

### 4.1 Descritivos

Os dados por país no período 2010–2023 estão resumidos na Tabela 1. A heterogeneidade é
marcante: o PIB per capita de 2023 varia de cerca de US$ 3,5 mil (Vietnã) a
mais de US$ 60 mil (Singapura), e a matrícula terciária média varia de
aproximadamente 28% (Vietnã) a 82% (Coreia do Sul). A cobertura temporal da
matrícula terciária é mais completa para os países asiáticos, sobretudo a
partir dos anos 1990.

| País | PIB pc 2023 (US$ const.) | Matrícula terciária média 2010–23 (%) | Gasto educacional médio (% PIB) | Dispêndio P&D médio (% PIB) |
|---|---|---|---|---|
| Argentina | 12.993 | 89,73 | 5,19 | 0,56 |
| Brasil | 9.288 | 51,39 | 5,91 | 1,18 |
| Chile | 14.295 | 86,69 | 4,99 | 0,36 |
| China | 12.484 | 49,28 | 3,90 | 2,11 |
| Coreia do Sul | 36.348 | 97,64 | 4,45 | 4,08 |
| Singapura | 65.977 | 93,23 | 2,82 | 1,97 |
| Vietnã | 3.772 | 30,59 | 3,54 | 0,35 |

*Fonte: elaboração própria a partir de World Development Indicators (2024).
Valores completos em `outputs/publishable_tables/tabela1_descr_paises.csv`.
Marcadores "—" indicam indisponibilidade no painel auditado.*

### 4.2 Associações em níveis e em primeiras diferenças

As correlações centrais estão na Tabela 2. Em níveis, a matrícula terciária
correlaciona 0,934 com o log do PIB per capita (n = 198), resultado de
magnitude elevada, mas típico de comparações entre países em estágios muito
diferentes de desenvolvimento. Em primeiras diferenças por país, a correlação
cai para 0,181 (n = 180). A queda não elimina a associação, mas a reduz a uma
ordem de grandeza compatível com efeitos modestos e com a presença de ciclos.

| Par | Correlação | p-valor | n |
|---|---|---|---|
| Matrícula terciária × log PIB pc (níveis) | 0,934 | 1,20e-89 | 198 |
| Δ Matrícula terciária × Δ PIB pc (primeiras diferenças) | 0,181 | 1,53e-02 | 180 |
| P&D % PIB × log PIB pc (níveis) | 0,505 | 1,09e-11 | 159 |
| Δ P&D % PIB × Δ PIB pc (primeiras diferenças) | 0,072 | 3,92e-01 | 145 |
| Gasto educacional % PIB × PIB pc (Pearson, níveis) | 0,026 | 7,00e-01 | 219 |
| Gasto educacional % PIB × PIB pc (Spearman, níveis) | 0,290 | 1,27e-05 | 219 |
| Δ Gasto educacional % PIB × Δ PIB pc (primeiras diferenças) | -0,065 | 3,71e-01 | 190 |

*Fonte: elaboração própria. "Δ" indica primeira diferença por país.*

Dois pontos merecem destaque. A discrepância entre o coeficiente de
Pearson (0,026; p = 0,700) e o de Spearman (0,290; p = 1,27e-05) para a
associação gasto educacional × renda em níveis indica sensibilidade a
observações extremas; relatar apenas uma das medidas subestima ou superestima a
relação. Além disso, o dispêndio em P&D, fortemente correlacionado em níveis
(0,505), não apresenta associação discernível em primeiras diferenças (0,072;
p = 0,392).

### 4.3 Estabilidade entre países (LOOCV)

A estabilidade entre países aparece na Tabela 3, com a correlação em níveis
reestimada pela exclusão de um país por vez. A correlação permanece entre 0,888
e 0,968 em todos os cenários, e a
exclusão de Singapura — a economia de maior renda — produz 0,935. A exclusão da
China produz o menor valor (0,888), ainda elevada. A associação em níveis é,
portanto, robusta à exclusão de qualquer economia individual.

| País excluído | ρ (níveis) | n |
|---|---|---|
| Argentina | 0,968 | 152 |
| Brasil | 0,942 | 187 |
| Chile | 0,929 | 175 |
| China | 0,888 | 148 |
| Coreia do Sul | 0,927 | 174 |
| Singapura | 0,935 | 187 |
| Vietnã | 0,918 | 165 |

*Fonte: elaboração própria. Valores completos em
`outputs/publishable_tables/tabela3_loocv.csv`. Os folds de treino e teste são
disjuntos (`loocv_folds.json`).*

### 4.4 Subperíodos

Os subperíodos 1960–1989 e 1990–2023 são comparados na Tabela 4. A correlação em níveis
é elevada em ambos (0,843 no primeiro; 0,943 no segundo). Em primeiras
diferenças, a correlação é modesta nos dois subperíodos (0,102 e 0,176), sem
evidência de tendência clara de fortalecimento.

| Subperíodo | ρ (níveis) | ρ (primeiras diferenças) |
|---|---|---|
| 1960–1989 | 0,843 | 0,102 |
| 1990–2023 | 0,943 | 0,176 |

*Fonte: elaboração própria. Valores completos em
`outputs/publishable_tables/tabela4_subperiodos.csv`.*

### 4.5 Painel com efeitos fixos

O painel com efeitos fixos de país (within) e matrícula
terciária defasada em cinco anos está na Tabela 5. Cada ponto percentual adicional de matrícula
terciária associa-se a um log-PIB per capita aproximadamente 0,022 maior
(IC95% 0,017–0,026; n = 168; 7 países). Na especificação com efeitos fixos de
país e de ano, o coeficiente é 0,025 (IC95% 0,0004–0,0498). A magnitude é
modesta, mas o intervalo não contém zero na especificação principal. Trata-se de
associação dentro do país ao longo do tempo, e não estabelece determinação.

| Especificação | Coeficiente (lag 5 anos) | IC95% | n | Países |
|---|---|---|---|---|
| Efeitos fixos de país (within) | 0,022 | [0,017; 0,026] | 168 | 7 |
| Efeitos fixos de país e ano | 0,025 | [0,0004; 0,0498] | 168 | 7 |

*Fonte: elaboração própria. `painel_efeitos_fixos.json`. Os intervalos são
homocedásticos e o número de clusters é pequeno (sete), o que recomenda
cautela.*

### 4.6 Exercício preditivo com validação agrupada

O exercício preditivo está resumido na Tabela 6. Com partição aleatória
por linha — que permite ao modelo "memorizar" países — a área sob a curva ROC é
0,796. Sob leave-one-country-out, em que cada país de teste esteve totalmente
ausente do treino, a área cai para 0,591, próxima do acaso (0,500). A queda de
aproximadamente 0,21 ponto indica que a capacidade preditiva aparente depende
de características específicas dos países do treino: com sete países, o modelo
não identifica um padrão transferível entre economias não vistas.

| Partição | Área sob a curva ROC | n avaliado | Países |
|---|---|---|---|
| Aleatória por linha (mesmo país no treino e no teste) | 0,796 | 24 | 7 |
| Leave-one-country-out (país de teste ausente do treino) | 0,591 | 76 | 7 |

*Fonte: elaboração própria. `ml_resultados.json`. Alvo: crescimento do PIB per
capita acima da mediana do período.*

## 5. Discussão

Os resultados são coerentes com o padrão já documentado na literatura, em dados
oficiais e auditáveis: a escolaridade terciária e o nível de renda
correlacionam-se fortemente entre países, mas a associação enfraquece de forma
acentuada quando se considera a variação dentro dos países ao longo do
tempo (Mankiw; Romer; Weil, 1992; Pritchett, 2001; Hanushek; Woessmann, 2010).
A queda de 0,934 para 0,181 em primeiras diferenças é o achado central: a
correlação de níveis decorre majoritariamente da co-evolução secular de
escolaridade e renda, não de uma relação contemporânea estável dentro de cada
país.

O painel com efeitos fixos contextualiza esse resultado. A defasagem de cinco anos
mitiga a simultaneidade, e o coeficiente positivo com intervalo de confiança
excluindo zero é consistente com a hipótese de que a expansão terciária
acompanha — e possivelmente precede — o crescimento da renda dentro do país.
Contudo, com sete países, o desenho não permite distinguir entre escolaridade
que precede o crescimento e escolaridade que cresce com o desenvolvimento
(relação inversa), nem controlar adequadamente por choques comuns. A
literatura que utiliza variações exógenas em escolaridade encontra efeitos
menores do que os sugeridos por correlações simples (Acemoglu; Gallego;
Robinson, 2014), consistente com nossa leitura cautelosa.

O exercício preditivo ilustra um ponto metodológico pouco frequente em
estudos de renda média: a validação por linha superestima a capacidade preditiva
quando há poucos países. A queda da área sob a curva ROC de 0,796 para 0,591
sob leave-one-country-out mostra que modelos treinados em um conjunto de países
não se transferem automaticamente a outros (Breiman, 2001). Esse limite é
próprio de amostras com poucos países e não decorre da sofisticação do
algoritmo; vale, ao menos, para os métodos aqui testados. Esse resultado
negativo é, em si, uma contribuição: exercícios preditivos sobre a armadilha da
renda média deveriam reportar validação agrupada por país.

As principais limitações do estudo são: (i) sete países, com consequente perda
de poder e de generalização; (ii) cobertura parcial das variáveis educacionais,
sobretudo nas décadas iniciais; (iii) ausência de controles de qualidade
educacional e de instituições, que a literatura aponta como moderadores
(Hanushek; Woessmann, 2010); (iv) erros padrão que não ajustam para
correlação serial; e (v) o caráter associativo de todas as estimativas. A
replicabilidade integral dos resultados mitiga, mas não elimina, essas
limitações.

## 6. Conclusão

Este artigo oferece uma análise associativa, reprodutível e auditável da
relação entre educação terciária e renda em sete economias, entre 1960 e 2023.
O primeiro resultado diz respeito aos níveis: a correlação entre
matrícula terciária e renda é elevada (0,934) e estável à exclusão de qualquer
país (LOOCV entre 0,888 e 0,968; seção 4.3). O segundo refere-se à variação
dentro do país: a associação, embora positiva e defasada (coeficiente 0,022;
IC95% 0,017–0,026), é de magnitude modesta em comparação com a correlação de
níveis, o que reforça a necessidade de distinguir co-movimento secular de
relação contemporânea (seções 4.2 e 4.5). Por fim, a validação cruzada agrupada
por país indica que a capacidade preditiva não generaliza entre economias não
vistas (área sob a curva ROC de 0,591; seção 4.6), um alerta metodológico para
a literatura de renda média.

Para a política pública brasileira, o resultado mais defensável é o mais
modesto: a expansão da educação terciária associa-se positivamente ao nível de
renda dentro do país, mas a magnitude dessa associação é incerta e dependente
de condições institucionais e de qualidade que este desenho não observa. A
recomendação de priorizar a expansão do ensino superior com qualidade e a
articulação com a inovação (Acemoglu; Gallego; Robinson, 2014; Rodrik, 2016;
World Bank, 2024) é compatível com os resultados, mas não decorre deles como
conclusão de determinação.

## Referências

ACEMOGLU, D.; GALLEGO, F. A.; ROBINSON, J. A. Institutions, human capital, and development. **Annual Review of Economics**, v. 6, p. 875-912, 2014. DOI: 10.1146/annurev-economics-080213-041119.

AIYAR, S. et al. Growth slowdowns and the middle-income trap. **Japan and the World Economy**, v. 48, p. 22-37, 2018. DOI: 10.1016/j.japwor.2018.07.001.

BARRO, R. J.; LEE, J. W. A new data set of educational attainment in the world, 1950–2010. **Journal of Development Economics**, v. 104, p. 184-198, 2013. DOI: 10.1016/j.jdeveco.2012.10.001.

BREIMAN, L. Random forests. **Machine Learning**, v. 45, n. 1, p. 5-32, 2001. DOI: 10.1023/A:1010933404324.

EICHENGREEN, B.; PARK, D.; SHIN, K. When fast-growing economies slow down: international evidence and implications for China. **Asian Economic Papers**, v. 11, n. 1, p. 42-87, 2012. DOI: 10.1162/ASEP_a_00118.

FELIPE, J.; ABDON, A.; KUMAR, U. Tracking the middle-income trap: what is it, who is in it, and why? **Asian Development Review**, v. 29, n. 1, 2012. DOI: 10.2139/ssrn.2049330.

HANUSHEK, E. A.; WOESSMANN, L. Education and economic growth. In: PETERSON, P.; BAKER, E.; McGAW, B. (Ed.). **International Encyclopedia of Education**. 3. ed. Oxford: Elsevier, 2010. v. 2, p. 245-252. [DOI: 10.1016/B978-0-08-044894-7.01227-6](https://doi.org/10.1016/B978-0-08-044894-7.01227-6).

IM, F. G.; ROSENBLATT, D. Middle-income traps: a conceptual and empirical survey. **Journal of International Commerce, Economics and Policy**, v. 6, n. 3, 2015. DOI: 10.1142/S1793993315500131.

LUCAS, R. E. On the mechanics of economic development. **Journal of Monetary Economics**, v. 22, n. 1, p. 3-42, 1988. DOI: 10.1016/0304-3932(88)90168-7.

MANKIW, N. G.; ROMER, D.; WEIL, D. N. A contribution to the empirics of economic growth. **Quarterly Journal of Economics**, v. 107, n. 2, p. 407-437, 1992. DOI: 10.2307/2118477.

PRITCHETT, L. Where has all the education gone? **World Bank Economic Review**, v. 15, n. 3, p. 367-391, 2001. DOI: 10.1093/wber/15.3.367.

PSACHAROPOULOS, G.; PATRINOS, H. A. Returns to investment in education: a decennial review of the global literature. **Education Economics**, v. 26, n. 5, p. 445-458, 2018. DOI: 10.1080/09645292.2018.1484426.

RODRIK, D. Premature deindustrialization. **Journal of Economic Growth**, v. 21, n. 1, p. 1-33, 2016. DOI: 10.1007/s10887-015-9122-3.

ROMER, P. M. Endogenous technological change. **Journal of Political Economy**, v. 98, n. 5, p. S71-S102, 1990. DOI: 10.1086/261725.

VANDENBUSSCHE, J.; AGHION, P.; MEGHIR, C. Growth, distance to frontier and composition of human capital. **Journal of Economic Growth**, v. 11, n. 2, p. 97-127, 2006. DOI: 10.1007/s10887-006-9002-y.

WORLD BANK. **World Development Report 2024: The Middle-Income Trap**. Washington, DC: World Bank, 2024. [DOI: 10.1596/978-1-4648-2078-6](https://doi.org/10.1596/978-1-4648-2078-6).

---

*Manuscrito gerado em 12 de agosto de 2026. Fonte de dados: World Development
Indicators (World Bank, API oficial, cache com SHA-256). Scripts, tabelas e
proveniência numérica completos em
`academic/papers/arm_education_audit/outputs/publishable_tables/`.*
