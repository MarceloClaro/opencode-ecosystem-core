# SPEC-935-R413 — Canais associativos da educação terciária: saúde, desigualdade, inovação e moderação institucional

- **Ciclo**: R413
- **Data**: 2026-08-13
- **Status**: em implementação
- **Dependência**: R412 (painel expandido de 135 países, controles WGI, erros clusterizados)

## Contexto

O usuário solicitou melhorias cobrindo **gaps reais e relevantes** com
resultados **auditáveis e validados**: "encontrar algo que ainda não foi
correlacionado ou ainda não combinado nos estudos". A varredura exploratória
no painel expandido (R412) e o cruzamento com a literatura identificaram
combinações que a literatura trata separadamente mas raramente junta:

1. **Canal saúde**: matrícula terciária × expectativa de vida (correlação
   parcial controlando PIB = +0,64) e o colapso da associação matrícula×PIB
   quando se controla por saúde (0,751 → 0,104). A literatura estuda
   saúde→crescimento e educação→crescimento separadamente (ex.: ACEMOGLU;
   JOHNSON, 2007; CERVALLATI; SUNDE, 2009); o uso de matrícula **terciária**
   com expectativa de vida e governança no mesmo painel é escasso, e um
   estudo de determinantes da longevidade sugere explicitamente essa
   combinação como pesquisa futura.
2. **Canal desigualdade**: matrícula terciária × Gini (parcial = −0,26);
   relevante para o Brasil (inclusão educacional e desigualdade).
3. **Canal inovação**: P&D × exportação de alta tecnologia (parcial = +0,45)
   e a "cadeia ciência→tecnologia" com governança.
4. **Moderação institucional**: interações matrícula×WGI e matrícula×P&D no
   painel FE (exploratório, com cluster por país).

## Princípios (real, relevante, auditável, validado)

- **Real**: números vêm do painel auditado R412 (dados oficiais, cache SHA-256).
- **Relevante**: os canais saúde/desigualdade/inovação são centrais para a
  política educacional brasileira e para o debate da renda média.
- **Auditável**: scripts + proveniência fechada (`provenance_r413.json`),
  bootstrap por país com sementes fixas, LOOCV.
- **Validado**: testes RED→GREEN; sem causalidade — linguagem associativa;
  resultados negativos reportados (a mediação é descritiva, não estrutural).

## Requisitos funcionais

1. `scripts/analyze_channels.py` (reusa `data/processed/panel_wdi_expandido_1960_2023.csv`):
   - Matriz de **correlações parciais** (níveis, controlando ln PIB) entre as
     variáveis do painel; e correlações de **primeiras diferenças**.
   - **Análise em etapas** do par matrícula×PIB: sem controle → +WGI →
     +estrutura → +saúde (cada rho parcial com n e IC bootstrap por país).
   - **Canal saúde**: parcial matrícula×expectativa de vida (ctrl PIB) +
     painel FE matrícula defasada→expectativa de vida (cluster por país).
   - **Canal desigualdade**: parcial matrícula×Gini + painel FE
     matrícula defasada→Gini (cluster).
   - **Canal inovação**: parcial P&D×alta tecnologia + painel FE
     P&D defasado→alta tecnologia (cluster).
   - **Moderação institucional** (exploratória): interações matrícula×WGI e
     matrícula×P&D no painel FE (cluster), reportadas como exploratórias.
   - **Bootstrap por país** (500 replicações, seed 42) para ICs das
     correlações parciais centrais.
   - Persiste `outputs/channels/provenance_r413.json` + tabelas CSV.
2. `NOTA_CANAIS_ASSOCIATIVOS.md`: nota de pesquisa (PT, com resumo EN/ES)
   reportando os canais com anti-overclaim; números com proveniência fechada;
   referências ABNT.
3. `latex/NOTA_CANAIS_ASSOCIATIVOS.tex` + PDF compilável.
4. `tests/test_r413_canais_associativos.py` (RED→GREEN).

## Critérios de aceitação

- provenance_r413.json com: parciais da matriz, etapas da análise
  (rho inicial e final com IC bootstrap), canais (saúde/desigualdade/
  inovação) com coef FE cluster, interações exploratórias.
- LOOCV das parciais centrais (≥ 20 folds).
- Nota MD: sem termos bloqueados; sem causalidade; números do resumo na
  provenance_r413.json; trilinguismo dos resumos.
- PDF compilado sem erros; suíte R408–R413 verde.

## Entregáveis

- `specs/SPEC-935-R413-canais-associativos.md`
- `scripts/analyze_channels.py`
- `outputs/channels/*` (tabelas + provenance_r413.json + folds)
- `NOTA_CANAIS_ASSOCIATIVOS.md` + `latex/NOTA_CANAIS_ASSOCIATIVOS.tex/.pdf`
- `tests/test_r413_canais_associativos.py`

## Não escopo

- Não altera ARTIGO_RBEP_SUBMISSAO.md nem seus testes (R410–R412) — a nota
  é um produto complementar (candidato a apêndice ou segundo artigo).
- Não declara mediação causal nem efeito identificado; não usa variação
  exógena; não alega Qualis.
