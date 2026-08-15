# SPEC-935-R426 — Estagnação educacional e renda municipal no Sertão de Cratéus (CE)

**Estado:** Em implementação
**Data:** 2026-08-15
**Autor:** Marcelo Claro Laranjeira (ORCID 0000-0001-8996-2887)

## Contexto e lacuna (gap)

O estudo ARM (`arm_education_audit`, R410–R425) mostrou que, entre 135
economias (1960–2023), a correlação em níveis entre educação terciária e
renda é forte (0,751) mas cai para 0,146 em primeiras diferenças por país;
no painel com efeitos fixos, o coeficiente é 0,073 (IC95% −0,169 a 0,314),
não discernível de zero. **Lacuna**: essa estrutura associativa — forte
entre unidades, fraca dentro das unidades ao longo do tempo — é testada
quase exclusivamente em escala de países ou estados; não há evidência
municipal para a microrregião do Sertão de Cratéus (CE), uma das regiões
mais pobres do Semiárido, com estagnação relativa do IDEB.

**Pergunta de pesquisa:** a estagnação do IDEB na microrregião do Sertão
de Cratéus (CE) reproduz o padrão associativo nacional da ARM — correlação
transversal positiva entre renda municipal e resultado educacional, mas
associação dentro do município ao longo do tempo fraca ou nula?

## Hipóteses falsificáveis

- **H1 (níveis/transversal):** a correlação transversal entre IDEB e PIB
  per capita municipal (e renda do responsável) entre os municípios do CE
  é positiva e forte (espelho do ρ_níveis ≈ 0,751 da ARM). Rejeitável se
  ρ < 0,3 ou IC95% contendo 0.
- **H2 (primeiras diferenças/dentro):** a correlação em primeiras
  diferenças (IDEB × PIB per capita, dentro do município) é fraca ou nula
  (espelho do ρ_1ªdif ≈ 0,146 e coef FE ≈ 0,073 da ARM). Rejeitável se a
  correlação for forte e significativa (ρ > 0,3 com p < 0,05).
- **H3 (estagnação operacional):** o crescimento do IDEB 2007–2023 dos
  municípios da microrregião é inferior às metas projetadas pelo INEP
  (estagnação relativa) e a variação não é associada à variação da renda
  municipal (não-detecção, não equivalência).

## Dados (reais, oficiais, auditáveis)

| Fonte | Indicador | Período | URL de acesso |
|---|---|---|---|
| INEP | IDEB observado por município (anos iniciais e finais) | 2005–2023 (2025 se disponível) | https://download.inep.gov.br/ideb/resultados/divulgacao_anos_iniciais_municipios_2023.zip |
| IBGE | PIB per capita municipal | 2010–2021 | https://ftp.ibge.gov.br/Pib_Municipios/2021/base/base_de_dados_2010_2021_xlsx.zip |
| IBGE/Censo 2022 | Renda nominal média/mediana mensal do responsável por município (proxy do IPCE) | 2022 | https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel/Agregados_por_municipios_renda_responsavel_BR_20260508_csv.zip |
| IBGE | Malha municipal CE (shapefile) | 2023 | https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2023/UFs/CE/CE_Municipios_2023.zip |

- **Unidades:** 9 municípios da microrregião oficial do Sertão de Cratéus
  (IBGE código 23018): Ararendá, Crateús, Independência, Ipaporanga,
  Monsenhor Tabosa, Nova Russas, Novo Oriente, Quiterianópolis, Tamboril.
- **Contexto de robustez:** Ceará (184 municípios) e Brasil (5.570) para
  potência e generalização.
- **IPCE:** índice comercial (IPC Marketing Editora) **não auditável** —
  não usado como dado; citado como referência conceitual. O mapa usa
  proxies oficiais: renda média do responsável (Censo 2022) e PIB per
  capita municipal (IBGE).

## Método

1. Coleta com proveniência (URL, timestamp, sha256) em `data/raw/`.
2. Processamento em `data/processed/` (tabela município × ano; rede
   municipal, com robustez na rede pública).
3. Análises:
   - Correlações transversais (Pearson/Spearman + bootstrap IC95, seed 42).
   - Correlações em primeiras diferenças (dentro do município).
   - Painel com efeitos fixos de município e ano (statsmodels) — espelho do
     modelo ARM.
   - LOOCV por município (9 folds) para correlação de níveis.
   - MDES/TOST para o coeficiente (poder 80%, α 5%; equivalência ±0,10).
   - Comparação de escalas: microrregião × CE × BR (mesmas métricas).
   - H3: ganho IDEB vs meta projetada (INEP) e associação com renda.
4. Mapa choropleth (geopandas/matplotlib): PIB per capita e renda média do
   responsável (proxy IPCE) por município.
5. Manuscrito MD → TeX → PDF → DOCX (normas ABNT/RBEP), mesmo pipeline do
   ARM.

## Anti-overclaim (obrigatório)

- Texto dirá "evidência associativa", "não-detecção" e "não se identifica
  relação direcional"; nunca "prova", "causa", "efeito causal",
  "validado", "AUC/ROC como preditor", "Qualis A1".
- A pequena amostra (n = 9) é declarada como limitação e tratada com
  bootstrap, LOOCV e MDES; nenhuma inferência causal é feita.

## Critérios de aceitação

1. `data/raw/` com arquivos-fonte + `SOURCE_MANIFEST.json` (URL, data,
   sha256) — reexecutável por `scripts/baixar_dados.py`.
2. `data/processed/painel_municipios.csv` reproduzível.
3. `scripts/analise_crateus.py` gera todos os números e tabelas em
   `outputs/expanded/` + `provenance_r426.json`.
4. `outputs/mapas/` com 2 mapas (PIB per capita e renda do responsável).
5. Manuscrito `ARTIGO_CRATEUS_RBEP.md` com referências reais com DOI
   ativos (Crossref validados) e links auditáveis.
6. Testes `tests/test_r426_*.py` (≥ 12) na suíte R408–R426; PDF sem
   Overfull/Underfull; DOCX gerado.
7. EvolutionRegistry: ciclo R426; evo-57.

## Fora de escopo

- Dados primários de campo (entrevistas, escolas).
- Estimação causal (propensity score, RDD etc.).
- Dados do IPCE comercial (não auditáveis).
