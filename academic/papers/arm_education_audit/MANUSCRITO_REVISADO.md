# EDUCAÇÃO E TRAJETÓRIAS DE RENDA EM SETE PAÍSES (1960–2023): UMA ANÁLISE EXPLORATÓRIA ASSOCIATIVA

**Versão candidata à revisão humana — SPEC-935-R408 (12/08/2026)**

> **Rótulo de status:** este documento é uma *versão candidata à revisão
> humana*. Não é um artigo publicado, não carrega classificação de mérito de
> periódico e não foi submetido a avaliação por pares. Os resultados foram
> recalculados a partir de fonte oficial (World Bank WDI, cache com hash)
> e refletem apenas associações exploratórias.

**Marcelo Claro**
Área: Desenvolvimento Econômico | Economia da Educação | Análise Comparativa Longitudinal
Dados: World Bank WDI API (cache R408, 12/08/2026)

---

## Resumo

A Armadilha da Renda Média (ARM) descreve a tendência observada em economias
de renda média de perder dinamismo após estágios intermediários de
desenvolvimento. Este estudo examina, de forma **exploratória e associativa**,
a relação entre indicadores educacionais e PIB per capita em sete países
(Argentina, Brasil, Chile, China, Coreia do Sul, Singapura e Vietnã) entre
1960 e 2023, com grade teórica de 448 células país-ano (7 países × 64 anos) e
dados oficiais do World Bank WDI.

Três achados descritivos merecem destaque: (1) em valores de nível, a
matrícula terciária e o PIB per capita apresentam correlação de Spearman de
0,934 (n = 198), mas essa associação cai para 0,174 quando se calculam as
primeiras diferenças dentro de cada país (n = 191) — o que indica que grande
parte da associação em níveis acompanha tendências comuns e **não constitui
evidência de relação causal**; (2) o gasto público em educação como proporção
do PIB mostra associação próxima de zero em primeiras diferenças (0,014,
n = 212); (3) os perfis descritivos de 2010–2023 revelam heterogeneidade
marcante, com o Vietnã exibindo PIB per capita muito inferior (US$ 2.832) e
desempenho educacional relativo acima do esperado para sua renda — padrão que
merece investigação específica, não generalização causal.

Palavras-chave: Armadilha da Renda Média. Capital Humano. Educação. Análise
Longitudinal. Economia Comparada.

---

## 1. Introdução

A literatura sobre desenvolvimento econômico debate há décadas o papel da
educação nas trajetórias de renda dos países. Autores como Hanushek e
Woessmann (2010) enfatizam a qualidade educacional medida por testes
internacionais; outros, como Pritchett (2001) e Easterly (2001), questionam se
a escolaridade é causa ou consequência do desenvolvimento. Este estudo não
pretende arbitrar o debate causal: seu objetivo é documentar, com dados
oficiais reproduzíveis, as associações empíricas entre indicadores
educacionais e renda nos sete países selecionados, ao longo de 64 anos.

O desenho é **observacional e exploratório**, com sete clusters nacionais —
número pequeno para inferência causal ou para alegações sobre condições
estruturais. As conclusões são limitadas à descrição de padrões associativos.

## 2. Dados e método

- **Fonte:** World Bank WDI, API oficial (`api.worldbank.org/v2/`), 11
  indicadores, 7 países, 1960–2023; respostas brutas cacheadas com URL,
  timestamp UTC, status HTTP e SHA-256.
- **Painel:** 448 linhas país-ano (grade teórica), uma por par país-ano; sem
  conversão de ausência em zero; sem interpolação silenciosa.
- **Associações:** correlação de Spearman em níveis (diagnóstico, vulnerável
  a tendência) e em primeiras diferenças por país (análise principal, remove
  tendência comum); com sete clusters, a inferência é declarada frágil.
- **Validação cruzada:** qualquer modelo preditivo exigiria split agrupado
  por país (*leave-one-country-out*); divisão aleatória por linha **não** é
  validade externa.

## 3. Resultados

### 3.1 Perfis descritivos (médias 2010–2023, World Bank WDI)

| País | PIB pc (US$ 2015) | n | Matr. terc. (%) | n | Gasto educ. (% PIB) | n | P&D (% PIB) | n |
|---|---|---|---|---|---|---|---|---|
| ARG | 13.216 | 14 | 89,73 | 14 | 5,19 | 14 | 0,56 | 14 |
| BRA | 8.923 | 14 | 51,39 | 11 | 5,91 | 13 | 1,18 | 14 |
| CHL | 13.312 | 14 | 86,69 | 14 | 4,99 | 12 | 0,36 | 13 |
| CHN | 9.017 | 14 | 49,28 | 14 | 3,90 | 1 | 2,11 | 14 |
| KOR | 31.417 | 14 | 97,64 | 14 | 4,45 | 8 | 4,08 | 14 |
| SGP | 58.195 | 14 | 93,23 | 11 | 2,82 | 14 | 1,97 | 13 |
| VNM | 2.832 | 14 | 30,59 | 12 | 3,54 | 13 | 0,35 | 7 |

Fonte: painel WDI (cache R408), médias por país no período; n = valores
realmente observados. Valores monetários em US$ constantes de 2015.

### 3.2 Associações com PIB per capita

| Indicador | ρ Spearman em níveis (n) | ρ Spearman em primeiras diferenças (n) |
|---|---|---|
| Matrícula terciária | 0,934 (198) | 0,174 (191) |
| Gasto público em educação (% PIB) | 0,29 (219) | 0,014 (212) |
| P&D (% PIB) | 0,505 (159) | 0,063 (152) |

Leitura: em níveis, a matrícula terciária acompanha fortemente o PIB per
capita; em primeiras diferenças, a associação cai drasticamente. Esse padrão
é o esperado quando duas séries crescentes co-movem por tendência comum. A
interpretação adequada é descritiva: **não há aqui evidência de que expandir
a matrícula terciária produza crescimento da renda**.

## 4. Discussão e limites

- **Causalidade:** não identificada neste desenho; a relação pode ser
  inversa ou bidirecional.
- **Generalização:** sete países intencionalmente selecionados; inferências
  externas restritas.
- **Cobertura:** contagens de observações variam por indicador (ex.: gasto
  educacional da China com n = 1 em 2010–2023); células ausentes permanecem
  ausentes.
- **Comparabilidade:** a China subnacional do PISA não é representada como
  média nacional; dados de qualidade educacional (PISA, Barro–Lee) não foram
  incluídos nesta versão por ausência de fonte oficial com hash verificável.
- **Validade externa:** nenhum resultado de validação cruzada por linha é
  apresentado como validade externa.

## 5. Conclusão

Os dados oficiais do World Bank WDI mostram associações positivas entre
indicadores educacionais e renda em níveis, que se reduzem substancialmente
quando se remove a tendência temporal por país. A comparação descritiva dos
sete países evidencia heterogeneidade relevante — em especial o contraste
entre gasto educacional relativamente alto e resultados educacionais
moderados no Brasil, e a eficiência educacional relativa do Vietnã com renda
muito inferior. Esses padrões são insumos para hipóteses futuras, não
resultados conclusivos. A pergunta "que tipo de educação, de que qualidade,
para quais demandas produtivas" permanece em aberto e exige dados
adicionais, identificação causal e revisão por pares.

---

## Referências (obras únicas — auditoria R408)

1. ABRUCIO, F. L.; SEGGATTO, C. I.; PEREIRA, M. C. O modelo cearense de educação. In: ABRUCIO; RAMOS (org.). *Regime de colaboração e associativismo territorial*. São Paulo: Santillana, 2016.
2. ACEMOGLU, D.; GALLEGO, F. A.; ROBINSON, J. A. Institutions, human capital, and development. *Annual Review of Economics*, v. 6, 2014. DOI: 10.1146/annurev-economics-080213-041119.
3. ACEMOGLU, D.; ROBINSON, J. A. *Why nations fail*. New York: Crown Business, 2012.
4. AIYAR, S. et al. Growth slowdowns and the middle-income trap. *Japan and the World Economy*, v. 48, 2018. DOI: 10.1016/j.japwor.2018.07.001.
5. BARRO, R. J.; LEE, J. W. A new data set of educational attainment in the world, 1950-2010. *Journal of Development Economics*, v. 104, 2013. DOI: 10.1016/j.jdeveco.2012.10.001.
6. BREIMAN, L. Random forests. *Machine Learning*, v. 45, 2001. DOI: 10.1023/A:1010933404324.
7. CEPAL. *Development traps in Latin America and the Caribbean*. Santiago: CEPAL, 2024.
8. COHEN, J. *Statistical power analysis for the behavioral sciences*. 2. ed. Hillsdale: Lawrence Erlbaum, 1988.
9. EASTERLY, W. The middle class consensus and economic development. *Journal of Economic Growth*, v. 6, 2001. DOI: 10.1023/A:1012786330095.
10. EICHENGREEN, B.; PARK, D.; SHIN, K. When fast growing economies slow down. *Asian Economic Papers*, v. 11, 2012. DOI: 10.1162/ASEP_a_00118.
11. EICHENGREEN, B.; PARK, D.; SHIN, K. Growth slowdowns redux. NBER WP 18673, 2013. DOI: 10.3386/w18673.
12. FAUL, F. et al. G*Power 3. *Behavior Research Methods*, v. 39, 2007. DOI: 10.3758/BF03193146.
13. FELIPE, J.; ABDON, A.; KUMAR, U. Tracking the middle-income trap. Levy Institute WP 715, 2012. DOI: 10.2139/ssrn.2049330.
14. FIELD, A. *Discovering statistics using IBM SPSS Statistics*. 5. ed. London: SAGE, 2018.
15. GILL, I.; KHARAS, H. *An East Asian renaissance*. Washington: World Bank, 2007.
16. GLEWWE, P. et al. *What explains Vietnam's exceptional performance in education?* Working Paper. Minneapolis: Univ. of Minnesota, 2023.
17. GRINDLE, M. S. *Despite the odds*. Princeton: Princeton University Press, 2004.
18. HANUSHEK, E. A.; WOESSMANN, L. Education and economic growth. In: *International Encyclopedia of Education*. 3. ed. Oxford: Elsevier, 2010. v. 2, p. 245-252. DOI: 10.1016/B978-0-08-044894-7.01227-6.
19. IM, F. G.; ROSENBLATT, D. Middle-income traps: a conceptual and empirical survey. *Journal of International Commerce, Economics and Policy*, v. 6, 2015. DOI: 10.1142/S1793993315500131.
20. LEE, K. *Schumpeterian analysis of economic catch-up*. Cambridge: Cambridge University Press, 2013.
21. LUCAS, R. E. On the mechanics of economic development. *Journal of Monetary Economics*, v. 22, 1988. DOI: 10.1016/0304-3932(88)90168-7.
22. MANKIW, N. G.; ROMER, D.; WEIL, D. N. A contribution to the empirics of economic growth. *Quarterly Journal of Economics*, v. 107, 1992. DOI: 10.2307/2118477.
23. OECD. *PISA 2022 Results — Volume I*. Paris: OECD Publishing, 2023. DOI: 10.1787/53f23881-en.
24. PRITCHETT, L. Where has all the education gone? *World Bank Economic Review*, v. 15, 2001. DOI: 10.1093/wber/15.3.367.
25. PSACHAROPOULOS, G.; PATRINOS, H. A. Returns to investment in education. *Education Economics*, v. 26, 2018. DOI: 10.1080/09645292.2018.1484426.
26. RODRIK, D. Premature deindustrialization. *Journal of Economic Growth*, v. 21, 2016. DOI: 10.1007/s10887-015-9122-3.
27. ROMER, P. M. Endogenous technological change. *Journal of Political Economy*, v. 98, 1990. DOI: 10.1086/261725.
28. STROBL, C. et al. Bias in random forest variable importance measures. *BMC Bioinformatics*, v. 8, 2007. DOI: 10.1186/1471-2105-8-25.
29. TAN, P. N.; STEINBACH, M.; KUMAR, V. *Introduction to data mining*. 2. ed. New York: Pearson, 2018.
30. VANDENBUSSCHE, J.; AGHION, P.; MEGHIR, C. Growth, distance to frontier and composition of human capital. *Journal of Economic Growth*, v. 11, 2006. DOI: 10.1007/s10887-006-9002-y.
31. VIRTANEN, P. et al. SciPy 1.0. *Nature Methods*, v. 17, 2020. DOI: 10.1038/s41592-019-0686-2.
32. WORLD BANK. *World Development Report 2024: The Middle-Income Trap*. Washington: World Bank, 2024. DOI: 10.1596/978-1-4648-2078-6.
33. WORLD BANK. *World Development Indicators 2024*. Washington: World Bank, 2024.
