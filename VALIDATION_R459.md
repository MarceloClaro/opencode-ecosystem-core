# VALIDATION_R459 — Artigo científico de publicação (Recamán vs MMR)

**Status:** GREEN · **Compilação:** PDF de 10 páginas (pdflatex+bibtex) sem erros fatais.

## Artefatos entregues (`publications/r459_article/`)
- `main.tex` — manuscrito completo (resumo PT + abstract EN, sumário, 6 seções,
  apêndice de reprodutibilidade).
- `sections/01..06` — introdução, trabalhos relacionados, metodologia, resultados,
  discussão, conclusão.
- `figures/cohort_results.png` — figura de evidência (matplotlib), dados reais.
- `referencias.bib` — 13 referências reais/verificadas.
- `main.pdf` — 10 páginas compiladas.

## Critérios executáveis verificados
| Critério | Situação |
|---|---|
| manuscrito main.tex compilável → PDF | ✅ (10 págs, exit 0) |
| resumo PT + abstract EN | ✅ |
| seções 1–3 (intro, relacionados, metodologia) | ✅ |
| Quadro 1 com valores REAIS do R458 | ✅ (0.500/0.750/0.4561/0.4256/0.667/0.917) |
| discussão com limitações explícitas | ✅ |
| referências resolvidas (10 na bibliografia) | ✅ sem citação indefinida |
| nenhum número inventado | ✅ (todos do cohort_report.json) |
| escopo anti-overclaim presente | ✅ ("corpus-piloto, não generaliza") |
| veredito refuta_H2 declarado | ✅ (4 ocorrências no PDF) |
| QA de rigor | SRI 60/100, falsifiability 75, sem falácias |

## QA de qualidade (scanners)
- `scientific_reasoning_scan` (metodologia completa): **SRI 60**, falsifiability 75,
  methodology 50, **sem falácias detectadas**, status "moderate_rigor" —
  compatível com estudo de benchmark de corpus-piloto.
- `super_rigor_audit`: sem ressalvas de sobre-alegação (testes locais ≠ certificação
  externa, declarado).

## Limites (anti-overclaim)
- Valores são de **corpus-piloto controlado**; artigo declara que **não generaliza
  para produção**.
- **Sem embeddings externos** (similaridade por tokens); **sem geração de texto LLM**.
- **Não** alega superioridade da proposta sobre MMR (observado: MMR supera).
- QA interno não equivale a revisão por pares/periódico.
