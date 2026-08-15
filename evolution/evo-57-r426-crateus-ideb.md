# evo-57 — R426: Estudo Crateús-IDEB (padrão associativo renda × IDEB na microrregião do Sertão de Cratéus)

## Objetivo

Produzir novo paper RBEP testando se o padrão associativo nacional
(forte em níveis, nulo dentro das unidades) se reproduz na microrregião
do Sertão de Cratéus (CE, IBGE 23018, 9 municípios), com dados oficiais
auditáveis (INEP 2005–2025; IBGE PIB 2010–2021 e Censo 2022), mapas
com proxies oficiais do IPCE, manuscrito MD→TeX→PDF (0 Overfull)→DOCX,
testes (17), registro evolutivo e commit.

## Mudanças

1. `specs/SPEC-935-R426-crateus-ideb.md` — especificação com H1/H2/H3,
   fontes oficiais, método espelhado (bootstrap por cluster, 1ª dif,
   FE, LOOCV, MDES/TOST), anti-overclaim e critérios ≥12 testes.
2. `scripts/baixar_dados.py` — download INEP (IDEB AI/AF), IBGE (PIB
   municipal, Censo 2022 renda) com manifesto `SOURCE_MANIFEST.json`
   (URL+sha256), reutilização de downloads já existentes, conversão de
   CSV com vírgula decimal e normalização numérica.
3. `scripts/analise_crateus.py` — painel defasado (PIB t−2), correlações
   com bootstrap por cluster, primeiras diferenças, FE (município+ano),
   LOOCV por município (9 folds), MDES (6,05) e TOST; saídas em
   `outputs/expanded/resultados_r426.json` + `provenance_r426.json`.
4. `scripts/mapa_crateus.py` — mapas coropléticos (renda do responsável
   Censo 2022 e PIB per capita 2021) com geopandas em venv isolado;
   `outputs/mapas/` + `mapas_manifest.json`.
5. `docs/ARTIGO_CRATEUS_RBEP.md` — manuscrito completo (resumo/abstract,
   6 seções, 13 referências com DOI ativos validados via Crossref,
   Apêndice A de proveniência e declaração de limites).
6. `latex/ARTIGO_CRATEUS_RBEP.tex` — versão LaTeX compilada com
   **0 Overfull** (uso de `xurl`/`\path` para URLs e paths longos);
   PDF de 8 páginas.
7. `scripts/export_docx_rbep.py` (adaptado de R421) — DOCX ABNT com
   margens 3/2 cm, Times 12, 1,5 espaço; `outputs/docx/` + manifest.
8. `tests/test_r426_crateus_ideb.py` — **17 testes** (dados processados,
   contagens, painel n=108, resultados H1/H2/H3, LOOCV, MDES/TOST,
   proveniência, mapas, manuscrito anti-overclaim e DOIs).
9. `evolution/evo-57-r426-*.md` + `cycles.json` (ciclo 244).

## Verificação

- Suíte R426: **17 passed** (test_r426_crateus_ideb.py).
- PDF: 8 páginas, **0 Overfull**, sem undefined refs/errors.
- DOCX: gerado com manifest SHA-256; MD canônico.
- Doctor pré-edição: 10/12 pass, 0 failed.

## Lições

- A premissa de estagnação foi **refutada pelos dados oficiais**: os 9
  municípios da micro atingiram a meta 2021 e ganharam em média 5,93
  pontos (AI, 2007–2025) — a análise deve relatar a refutação com
  clareza, não forçar a hipótese original.
- n=9 municipal exige declarar **não-detecção** (MDES 6,05; TOST
  p=0,88), nunca equivalência nem ausência.
- IPCE comercial não auditável → proxies oficiais (renda do responsável
  e PIB per capita) com limitação declarada no manuscrito.
- LaTeX: `\texttt` não quebra em `_`; usar `xurl` + `\path{}` para
  atingir 0 Overfull em referências com DOI e paths longos.
- Validação de DOI via Crossref descarta falsos positivos (ex.:
  `10.1590/1981-3821202300010003` não é Ponne).
