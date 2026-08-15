# evo-57 — R426: Estudo Crateús-IDEB (associação renda × IDEB na microrregião do Sertão de Cratéus)

## Objetivo

Produzir novo paper RBEP (pesquisa original, sem citar/espelhar estudo
anterior) testando, na microrregião do Sertão de Cratéus (CE, IBGE
23018, 9 municípios), a associação entre renda municipal e desempenho
escolar no IDEB em duas dimensões — transversal (entre municípios) e
temporal (dentro dos municípios) —, com pergunta de pesquisa (RQ)
explícita, dados oficiais auditáveis (INEP 2005–2025; IBGE PIB 2010–2021
e Censo 2022), mapas, 4 gráficos e 4 tabelas, manuscrito
MD→TeX→PDF (0 Overfull)→DOCX (6 figuras), testes (23), registro
evolutivo e commit.

## Mudanças

1. `specs/SPEC-935-R426-crateus-ideb.md` — especificação com RQ, H1/H2/H3,
   fontes oficiais, método (bootstrap por cluster, 1ª dif, FE com SE
   clusterizado, LOOCV, MDES/TOST), anti-overclaim e critérios ≥12 testes.
2. `scripts/baixar_dados.py` — download INEP (IDEB AI/AF), IBGE (PIB
   municipal, Censo 2022 renda) com manifesto `SOURCE_MANIFEST.json`
   (URL+sha256), reutilização de downloads já existentes, conversão de
   CSV com vírgula decimal e normalização numérica.
3. `scripts/analise_crateus.py` — painel defasado (PIB t−2), correlações
   com bootstrap por cluster, primeiras diferenças, FE (município+ano)
   com **erros padrão clusterizados CRVE por município (t com G−1=8)**,
   LOOCV por município (9 folds), MDES (5,71 cluster) e TOST; saídas em
   `outputs/expanded/resultados_r426.json` + `provenance_r426.json`.
4. `scripts/mapa_crateus.py` — mapas coropléticos (renda do responsável
   Censo 2022 e PIB per capita 2021) com geopandas em venv isolado;
   `outputs/mapas/` + `mapas_manifest.json`.
5. `scripts/graficos_crateus.py` — 4 gráficos (scatter de níveis, séries
   temporais IDEB, LOOCV r de teste, ganho×renda) em `outputs/figuras/`
   + `figuras_manifest.json`.
6. `docs/ARTIGO_CRATEUS_RBEP.md` — manuscrito completo (resumo/abstract,
   6 seções, pergunta de pesquisa, seção de falsificabilidade, 13
   referências com DOI ativos validados via Crossref, 4 tabelas, 6
   figuras incorporadas, Apêndice A de proveniência e declaração de
   limites).
6. `latex/ARTIGO_CRATEUS_RBEP.tex` — versão LaTeX compilada com
   **0 Overfull** (uso de `xurl`/`\path` para URLs e paths longos);
   **PDF de 13 páginas com as 6 figuras**.
7. `scripts/export_docx_rbep.py` (adaptado de R421) — DOCX ABNT com
   margens 3/2 cm, Times 12, 1,5 espaço; **6 imagens + 4 tabelas com
   bordas**; `outputs/docx/` + manifest.
8. `tests/test_r426_crateus_ideb.py` — **23 testes** (dados processados,
   contagens, painel n=108, resultados H1/H2/H3 com SE clusterizado,
   LOOCV, MDES/TOST, proveniência, mapas, figuras, RQ, ausência de
   referência a estudo anterior, manuscrito anti-overclaim e DOIs).
9. `evolution/evo-57-r426-*.md` + `cycles.json` (ciclo 244).

## Verificação

- Suíte R426: **23 passed** (test_r426_crateus_ideb.py).
- PDF: 13 páginas, **0 Overfull**, sem undefined refs/errors.
- DOCX: 6 imagens (4 gráficos + 2 mapas) e 4 tabelas com bordas;
  manifest SHA-256; MD canônico.
- Auditoria estatística: FE com SE homocedástico → **SE clusterizado
  CRVE por município** (t com G−1=8); IC95 cluster [−1,51; 6,73],
  p=0,18; MDES cluster 5,71; TOST p=0,90.
- Doctor pré-edição: 10/12 pass, 0 failed.

## Lições

- A premissa de estagnação foi **refutada pelos dados oficiais**: os 9
  municípios da micro atingiram a meta 2021 e ganharam em média 5,93
  pontos (AI, 2007–2025) — a análise deve relatar a refutação com
  clareza, não forçar a hipótese original.
- n=9 municipal exige declarar **não-detecção** (MDES 5,71 cluster;
  TOST p=0,90), nunca equivalência nem ausência.
- IPCE comercial não auditável → proxies oficiais (renda do responsável
  e PIB per capita) com limitação declarada no manuscrito.
- LaTeX: `\texttt` não quebra em `_`; usar `xurl` + `\path{}` para
  atingir 0 Overfull em referências com DOI e paths longos.
- Validação de DOI via Crossref descarta falsos positivos (ex.:
  `10.1590/1981-3821202300010003` não é Ponne).
- **Erros padrão homocedásticos subestimam a incerteza com poucos
  clusters (G=9)**; reportar CRVE por município com correção de pequena
  amostra (t com G−1 graus de liberdade).
- Pandoc incorpora imagens markdown ao DOCX automaticamente quando o
  cwd é a pasta do paper (caminhos relativos resolvidos).
