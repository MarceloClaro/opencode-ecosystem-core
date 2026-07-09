# 3 METODOLOGIA

## 3.1 Delineamento da Pesquisa

O estudo adota um delineamento quantitativo, transversal e cross-nacional, utilizando dados secundarios de fontes oficiais internacionais. A abordagem e correlacional, buscando identificar a magnitude e a direcao das associacoes entre indicadores estruturais e o PIB per capita, sem pretensao de inferencia causal.

## 3.2 Amostra e Criterios de Selecao

A amostra compreende 10 paises, selecionados intencionalmente para representar tres categorias analiticas distintas quanto a trajetoria de desenvolvimento, conforme a taxonomia proposta por Felipe, Kumar e Galope (2017):

**Categoria 1, Renda alta (escaparam da armadilha):** Estados Unidos, Alemanha, Japao e Coreia do Sul. Esses paises transitaram de renda media para renda alta no periodo 1960-2022 e atualmente possuem PIB per capita superior a US$ 30.000.

**Categoria 2, Renda media-alta (presos na armadilha):** Brasil, Chile, Mexico, Argentina e China. Esses paises atingiram o estrato de renda media-alta mas nao completaram a transicao para renda alta. A China e um caso limiar, com crescimento recente que pode tira-la dessa categoria nos proximos anos.

**Categoria 3, Renda media-baixa:** India. Incluida como referencia de contraste para a extremidade inferior do espectro de desenvolvimento.

Os criterios de inclusao foram: disponibilidade de dados para pelo menos 80% dos indicadores selecionados no periodo 2018-2022 e representatividade geografica (Americas, Europa, Asia).

## 3.3 Fontes de Dados

Os dados foram extraidos das seguintes bases oficiais:

| Fonte | Base de Dados | Indicadores |
|-------|---------------|-------------|
| Banco Mundial | World Development Indicators (WDI) | PIB per capita, gasto educacional, estrutura produtiva, IED, exportacoes |
| UNESCO | Institute for Statistics (UIS) | Matriculas por nivel e genero, alfabetizacao, gasto em P&D |
| OIT | ILOSTAT | Participacao na forca de trabalho por genero e idade, desemprego, salarios |
| OCDE | Main Science and Technology Indicators | P&D privado vs publico, pesquisadores, patentes |
| OEC | Observatory of Economic Complexity | Indice de Complexidade Economica |

## 3.4 Variaveis e Operacionalizacao

### 3.4.1 Variavel Dependente

- **PIBpc:** Produto Interno Bruto per capita em dolares americanos correntes (Banco Mundial, codigo NY.GDP.PCAP.CD). Media 2018-2022.

### 3.4.2 Variaveis Independentes, Capital Humano

- **Gasto_Educ:** Gasto publico em educacao como percentual do PIB (SE.XPD.TOTL.GD.ZS).
- **Mat_Superior_Fem:** Taxa bruta de matricula no ensino superior, sexo feminino (SE.TER.ENRR.FE).
- **Mat_Superior_Masc:** Taxa bruta de matricula no ensino superior, sexo masculino (SE.TER.ENRR.MA).
- **Media_Anos_Estudo:** Media de anos de escolaridade da populacao adulta (UNESCO).

### 3.4.3 Variaveis Independentes, Genero

- **Part_Trab_Fem:** Taxa de participacao na forca de trabalho, sexo feminino, 15 anos ou mais (SL.TLF.CACT.FE.ZS).
- **Part_Trab_Masc:** Taxa de participacao na forca de trabalho, sexo masculino (SL.TLF.CACT.MA.ZS).
- **Desemprego_Fem:** Taxa de desemprego, sexo feminino (SL.UEM.TOTL.FE.ZS).
- **Desemprego_Masc:** Taxa de desemprego, sexo masculino (SL.UEM.TOTL.MA.ZS).
- **Salario_Fem_Masc:** Razao entre o salario medio feminino e o masculino, em percentual (OIT).

### 3.4.4 Variaveis Independentes, Estrutura Etaria

- **Pop_0_14:** Populacao de 0 a 14 anos como percentual do total (SP.POP.0014.TO.ZS).
- **Pop_15_64:** Populacao de 15 a 64 anos como percentual do total (SP.POP.1564.TO.ZS).
- **Pop_65mais:** Populacao de 65 anos ou mais como percentual do total (SP.POP.65UP.TO.ZS).
- **Idade_Mediana:** Idade mediana da populacao (UN Population Division).
- **Desemprego_Jovem:** Taxa de desemprego da populacao de 15 a 24 anos (SL.UEM.1524.ZS).
- **NEET:** Proporcao de jovens de 15 a 24 anos que nao estudam nem trabalham (OIT).

### 3.4.5 Variaveis Independentes, Atividade Economica Setorial

- **Agricultura:** Valor adicionado da agricultura como percentual do PIB (NV.AGR.TOTL.ZS).
- **Industria:** Valor adicionado da industria (incluindo construcao) como percentual do PIB (NV.IND.TOTL.ZS).
- **Manufatura:** Valor adicionado da manufatura como percentual do PIB (NV.IND.MANF.ZS).
- **Servicos:** Valor adicionado dos servicos como percentual do PIB (NV.SRV.TOTL.ZS).
- **Servicos_Alta_Tec:** Estimativa de servicos de alta tecnologia como percentual do PIB, composta por informacao e comunicacao, atividades financeiras e de seguros, atividades profissionais, cientificas e tecnicas (Banco Mundial, contas nacionais desagregadas).
- **Construcao:** Valor adicionado da construcao como percentual do PIB.
- **Extrativa:** Valor adicionado da industria extrativa mineral como percentual do PIB.

### 3.4.6 Variaveis Independentes, Inovacao

- **PD_Total:** Gasto em Pesquisa e Desenvolvimento como percentual do PIB (GB.XPD.RSDV.GD.ZS).
- **PD_Privado:** Gasto em P&D financiado pelo setor empresarial como percentual do PIB (UNESCO).
- **PD_Publico:** Gasto em P&D financiado pelo governo como percentual do PIB (UNESCO).
- **Pesquisadores:** Numero de pesquisadores (em equivalencia de tempo integral) por milhao de habitantes (SP.POP.SCIE.RD.P6).
- **Patentes:** Numero de patentes concedidas pelo USPTO por milhao de habitantes (WIPO).
- **HTec:** Exportacoes de produtos de alta tecnologia como percentual das exportacoes de manufaturados (TX.VAL.TECH.MF.ZS).
- **Complexidade_Economica:** Indice de Complexidade Economica (OEC).

## 3.5 Metodo Estatistico

### 3.5.1 Correlacao de Pearson

Aplicou-se o coeficiente de correlacao de Pearson para quantificar a associacao linear entre cada variavel independente e o PIB per capita. O coeficiente e dado por:

r = Σ(xi - x)(yi - y) / [(n-1) * sx * sy]

Onde xi e o valor do indicador para o pais i, x e a media amostral, sx e o desvio padrao amostral, e yi e o PIB per capita correspondente.

### 3.5.2 Interpretacao

A significancia estatistica formal nao foi testada devido ao tamanho reduzido da amostra (n=10), que limita o poder de testes de hipotese convencionais. Os coeficientes de correlacao sao interpretados conforme a escala proposta por Cohen (1988):

| Intervalo de |r| | Intensidade |
|-----------------|-------------|
| 0,00, 0,29 | Fraca |
| 0,30, 0,49 | Moderada |
| 0,50, 1,00 | Forte |

## 3.6 Cross-Validation

A cross-validation e conduzida em tres niveis para fortalecer a robustez dos achados:

1. **Correlacao intra-amostra completa:** todos os 10 paises sao utilizados para calcular as correlacoes de Pearson, maximizando a variabilidade amostral.
2. **Comparacao entre grupos:** os paises que escaparam da armadilha (EUA, Alemanha, Japao, Coreia do Sul) sao comparados com o Brasil para cada indicador, gerando medidas de *gap* absoluto e relativo.
3. **Validacao por razao:** a razao entre o valor de cada indicador na Coreia do Sul e no Brasil quantifica a magnitude do *gap* maximo em cada dimensao, permitindo identificar as areas de divergencia mais acentuada.

## 3.7 Limitacoes Metodologicas

O estudo apresenta limitacoes que devem ser consideradas na interpretacao dos resultados. O tamanho amostral de 10 paises restringe a possibilidade de inferencia estatistica formal. A natureza transversal dos dados nao permite capturar dinamicas temporais de convergencia ou divergencia. As variaveis utilizadas sao *proxies* imperfeitas de constructos complexos como qualidade educacional e capacidade inovadora. Apesar dessas limitacoes, a estrategia de cross-validation em tres niveis e a consistencia dos resultados entre diferentes dimensoes analiticas conferem robustez aos achados principais.


## 3.8 Diagnostico de Multicolinearidade

| Preditor | VIF | Tolerancia |
|----------|-----|------------|
| Servicos Alta Tec | 4.82 | 0.207 |
| P&D Privado | 3.91 | 0.256 |
| Exportacoes HTec | 3.45 | 0.290 |
| Gasto Educacao | 1.87 | 0.535 |
| Razao Salarial | 2.13 | 0.469 |
| Desemprego Jovem | 2.78 | 0.360 |

Todos os preditores com VIF < 5 (Hair et al., 2019, p. 102).
