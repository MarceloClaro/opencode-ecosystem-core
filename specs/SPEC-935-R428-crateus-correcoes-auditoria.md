# SPEC-935-R428 — Correções da Auditoria Qualis A1 do artigo Crateús-IDEB (R426)

- **Ciclo**: R428 | **Estado**: Em execução | **Responsável**: marceloclaro
- **Relacionada**: SPEC-935-R426 (artigo RBEP), SPEC-935-R427 (diagnóstico de indicadores)
- **Gatilho**: auditoria externa (QA MASWOS 6,5/10; blind peer review MAJOR REVISION com risco de REJECT; honestidade 8,0/10) apontou falhas P0/P1/P2 no manuscrito.

## Critérios de aceitação (gate SDD)

1. **CA-1 — Correção da dimensão transversal**: reportar o between-estimator (médias municipais, n=9) com IC95 e p por bootstrap por cluster; rotular LOOCV como validação INTERNA (co-tendência), nunca "validação externa" nem "replicada fora da amostra 9/9".
2. **CA-2 — Inferência cluster-robusta**: p-valores de H1 reportados com bootstrap por cluster (níveis) e CRVE com t(G−1) + wild cluster bootstrap Rademacher (G=9) no FE; declarar limitação de G=9 (MacKinnon & Webb, 2017).
3. **CA-3 — H3 corrigida**: comparar IDEB observado vs projeção INEP do MESMO ano (2011–2021); ganho 2007–2025 e associação com renda como proposição separada, com linguagem de não-detecção.
4. **CA-4 — Deflação**: PIB per capita real (IPCA médio anual, IPEA Data `PRECOS12_IPCA12`; R$ de 2021), registrado em `data/processed/ipca_medias_anuais.json` com URL de proveniência.
5. **CA-5 — TOST e MDES substantivos**: TOST com SESOI ±0,5 ponto de IDEB (não apenas ±0,10) e MDES traduzido em pontos por +10% do PIB real; linguagem "precisão insuficiente" (não "equivale a zero").
6. **CA-6 — Grafia e consistência**: "Crateús" em todo o documento (título, resumo, abstract, corpo); figuras corretas na Discussão; 100% dos números do manuscrito reproduzem de `resultados_r428.json`.
7. **CA-7 — Referências e formalidades**: paginação real pesquisada (não inventada); PAIC uniformizado ("Aprendizagem"); sem "pactuated target"; seções formais RBEP; `requirements.txt` do paper.

## Correções mapeadas (auditoria → implementação)

| # | Achado | Severidade | Implementação |
|---|---|---|---|
| 1 | LOOCV = dimensão errada | P0 | `loocv_interno` rotulado validação interna; between-estimator como dimensão transversal |
| 2 | p nominal H1 | P0 | bootstrap por cluster (níveis) + CRVE t(G−1) + wild (FE) |
| 3 | H3 logicamente invertida | P0 | metas por ano-mesmo-ano (2011–2021) |
| 4 | H2 "se confirma"/"nula" | P0 | linguagem de não-detecção + MDES traduzido |
| 5 | Meta 2021 vs IDEB 2025 | P0 | IDEB observado 2021 vs projeção 2021 |
| 6 | "Cratéus" | P0 | uniformização Crateús |
| 7 | Figuras trocadas | P0 | verificação da Discussão |
| 8 | PIB nominal | P1 | deflator IPCA (IPEA Data) |
| 9 | Lag arbitrário | P1 | perfil lags 0–4 |
| 10 | FE sem etapa / G pequeno | P1 | FE município×etapa + ano; nota G=9; wild bootstrap |
| 11 | TOST ±0,10 trivial | P1 | SESOI ±0,5 ponto |
| 12 | MDES não interpretável | P1 | pontos de IDEB por +10% PIB real |
| 13 | Missingness não discutida | P1 | bloco `missingness` por escala |
| 14 | "Média nacional da rede municipal" sem fonte | P1 | remover/substituir por fonte |
| 15 | Espantalho da estagnação sem fonte | P1 | ancorar em fonte |
| 16 | Citações metodológicas | P2 | Cameron et al. 2008; MacKinnon & Webb 2017; Lakens et al. 2018; Bloom 1995 |
| 17 | PAIC Alfabetização vs Aprendizagem | P2 | uniformizar título real (Cruz; Ribeiro; Batista, 2022) |
| 18 | "pactuated target" | P2 | "agreed target" |
| 19 | Paginação ausente | P2 | web search (Carnoy 2017; Cito & Marôco 2026; Lacruz et al. 2019) |
| 20 | requirements.txt | P2 | criar |

## Entregáveis

- `scripts/analise_crateus_r428.py` + `outputs/expanded/resultados_r428.json` + `provenance_r428.json` ✓
- `data/processed/ipca_medias_anuais.json` (IPEA Data PRECOS12_IPCA12) ✓
- Artigo reescrito: `docs/ARTIGO_CRATEUS_RBEP.md` + `latex/ARTIGO_CRATEUS_RBEP.tex` + PDF + DOCX
- `tests/test_r428_*.py`; `requirements.txt`
- Re-auditoria (honest-critic + consistência interna)
- `evolution/evo-59-r428-*.md`; `evolution/cycles.json` (ciclo 246); commit + push

## Decisões registradas

- **Definição de X**: log do PIB per capita real deflacionado pelo IPCA médio anual (fator 2021/ano), defasagem principal de 2 anos, robustez 0–4.
- **Dimensões de associação**: (a) entre municípios (n=9, média temporal por município); (b) pooled níveis (IC cluster); (c) temporal dentro (1ª diferenças e FE município×etapa+ano).
- **Não é estudo causal**: limitação explícita; correlação não implica causalidade.
- **Anti-overclaim**: nenhuma alegação de "Qualis A1 verificado" sem validação externa; scanners MCP são calibrados para RCT e não reconhecem estudo observacional — registrado como limitação da ferramenta.
