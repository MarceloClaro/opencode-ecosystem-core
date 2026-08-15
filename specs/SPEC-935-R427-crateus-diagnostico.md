# SPEC-935-R427-crateus-diagnostico.md — Diagnóstico de indicadores correlacionados com o IDEB (foco Crateús)

## Contexto

O ciclo R426 (artigo RBEP "Crateús-IDEB") mostrou que, no Sertão de Cratéus, a associação
renda × desempenho é transversal (entre municípios), não temporal (dentro das unidades).
O município-sede **Crateús (2304103)** — maior e mais rico da microrregião — teve IDEB
anos iniciais 2025 de 8,5 (ganho 2007–2025 de 5,1 pontos), ainda abaixo do melhor
desempenho da região (Ipaporanga 9,9) e abaixo da própria trajetória de municípios vizinhos.

A gestão municipal precisa de um **diagnóstico exploratório**: dentre os indicadores
municipais oficiais disponíveis, **quais se correlacionam mais (positivamente) e quais
menos com o desempenho escolar** — para orientar prioridades de política e evitar gastar
esforço em fatores sem associação observável na região.

## Pergunta de pesquisa (RQ-R427)

Entre indicadores municipais oficiais (Censo Demográfico 2022 do IBGE e IDEB do INEP),
quais apresentam **maior** e **menor** correlação com o IDEB (2025, anos iniciais e finais)
e com o ganho de IDEB (2007–2025) nos nove municípios do Sertão de Cratéus? E onde
Crateús se posiciona nos indicadores de maior correlação (para orientar prioridades)?

## Hipóteses operacionais

- **H1 (mais correlacionados):** indicadores de **capital humano e saneamento básico**
  (alfabetização de adultos, água encanada, esgoto, banheiro) devem apresentar correlação
  positiva mais forte com o IDEB do que indicadores de **renda e desigualdade**.
- **H2 (menos correlacionados):** renda (PIB per capita, renda do responsável) e Gini
  devem apresentar correlação **fraca ou nula** com o **ganho** de IDEB (replicando o R426),
  e correlação apenas moderada com o IDEB em níveis.
- **H3 (posição de Crateús):** Crateús deve estar **acima da mediana** em renda/PIB,
  mas **abaixo da mediana** em pelo menos um indicador de alto capital humano/saneamento —
  candidato a prioridade de política.

## Fontes de dados (oficiais e auditáveis)

| Indicador | Fonte | Tabela SIDRA / arquivo |
|---|---|---|
| Taxa de alfabetização 15+ (%) | IBGE Censo 2022 | SIDRA 9543 (var 2513) |
| % domicílios com água da rede geral | IBGE Censo 2022 | SIDRA 6803 (var 1000381, cat 72144) |
| % domicílios com esgoto rede geral/pluvial | IBGE Censo 2022 | SIDRA 6805 (var 1000381, cat 72110) |
| % domicílios com lixo coletado | IBGE Censo 2022 | SIDRA 6892 (var 1000381, cat 2520) |
| % domicílios com internet | IBGE Censo 2022 | SIDRA 9936 (var 1000381, cat 77585) |
| % domicílios com banheiro exclusivo | IBGE Censo 2022 | SIDRA 6806 (var 1000381, cat 12032) |
| Gini (rendimento domiciliar) | IBGE Censo 2022 | SIDRA 3568 (var 881) |
| Renda média do responsável (R$) | IBGE Censo 2022 | já coletado (R426) |
| PIB per capita (R$) | IBGE 2021 | já coletado (R426) |
| IDEB 2025 AI/AF; ganho AI 2007–2025 | INEP | já coletado (R426) |

Unidades: 9 municípios da microrregião IBGE 23018 (Ararendá, Crateús, Independência,
Ipaporanga, Monsenhor Tabosa, Nova Russas, Novo Oriente, Quiterianópolis, Tamboril).

## Método

1. Coleta via API SIDRA v3 (`/metadados` + consulta por `localidades=N6[...]`),
   classificação "Total" onde aplicável, variável percentual do total geral quando
   disponível; manifest de coleta com timestamp e código de tabela.
2. Fusão com `resultados_r426.json` (IDEB 2025 AI/AF, ganho AI 2007–2025),
   `renda_microrregiao.json` e PIB per capita.
3. Correlações **Pearson e Spearman** entre cada indicador e cada desfecho (n=9);
   intervalo de confiança 95% por **bootstrap não paramétrico** (seed 42, 5.000
   reamostragens, percentis 2,5/97,5). Relatórios: `r`, `rho`, IC95, sinal e
   estabilidade (fração de reamostragens com o mesmo sinal).
4. Ranking por |r| médio (Pearson e Spearman) para os 3 desfechos; top-3 e bottom-3.
5. Perfil de Crateús: valor do município vs. mediana da microrregião em cada
   indicador; matriz prioridade = (força da correlação) × (posição de Crateús
   abaixo da mediana).
6. Gráficos: heatmap de correlações (indicador × desfecho), scatter top-3 por
   desfecho, ranking horizontal.

## Critérios de aceitação

- CA1: ≥ 9 indicadores coletados para os 9 municípios (sem NA).
- CA2: `resultados_r427.json` com `ranking_pearson`, `ranking_spearman`, `perfil_crateus`
  e `matriz_prioridade`.
- CA3: heatmap + scatter top-3 gerados em `outputs/figuras_r427/`.
- CA4: nota técnica `docs/NOTA_TECNICA_CRATEUS_INDICADORES.md` com ranking e
  recomendações, **sem overclaim** (n=9; associação ≠ causalidade; IC95 amplos).
- CA5: ≥ 12 testes em `tests/test_r427_crateus_diagnostico.py`.
- CA6: registro evolutivo (evo-58) e commit.

## Anti-overclaim

- Declarar sempre: n=9, poder estatístico baixo, correlação ≠ causalidade.
- Não usar termos "prova", "causa", "efeito"; usar "associação", "candidato a prioridade",
  "não se observa associação".
- Distinguir sinal estável (≥ 90% das reamostragens com o mesmo sinal) de instável.

## Riscos

- API SIDRA instável (500 em `/variaveis`) → mitigado usando `/metadados` e consulta
  direta de dados; retry com backoff.
- Finanças municipais (FINBRA/SICONFI) indisponíveis no momento (404/0 items) →
  registrado como limitação e sugestão de extensão futura.
- Colinearidade entre indicadores (água×banheiro×esgoto) → tratar como famílias:
  capital humano, saneamento, conectividade, renda/desigualdade.
