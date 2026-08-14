# SPEC-935-R411 — Versão LaTeX/PDF de submissão do artigo RBEP (R410)

- **Ciclo**: R411
- **Data**: 2026-08-12
- **Status**: em implementação
- **Dependência**: R410 (ARTIGO_RBEP_SUBMISSAO.md aprovado pelos testes) e R409 (números/proveniência)

## Objetivo

Produzir a versão **LaTeX** do manuscrito de submissão RBEP
(`ARTIGO_RBEP_SUBMISSAO.md`) e compilar o **PDF** correspondente, mantendo
conformidade editorial (trilinguismo, ABNT, anti-overclaim) e **fidelidade
numérica integral** ao R409/R410 — nenhum número alterado na transcrição.

## Requisitos funcionais

1. `academic/papers/arm_education_audit/latex/ARTIGO_RBEP_SUBMISSAO.tex`
   compilável com pdflatex (TeX Live), documento A4, 12pt, margens ABNT
   (esq/sup 3 cm, dir/inf 2 cm), espaçamento 1,5, fonte Times (newtxtext).
2. Conteúdo idêntico em substância ao MD do R410: título PT/EN/ES,
   resumo/abstract/resumen, 3–5 palavras-chave por idioma, 6 seções, 6
   tabelas (booktabs), 16 referências ABNT em ordem alfabética com DOI.
3. **Corpo sem avisos editoriais** e **sem termos bloqueados** (mesmos
   critérios dos testes R410).
4. Números e tabelas idênticos aos do MD (proveniência R409).
5. Compilação determinística: `pdflatex` duas passadas, sem erros, gerando
   `latex/ARTIGO_RBEP_SUBMISSAO.pdf` não vazio.
6. Avisos de candidatura permanecem apenas em `CARTA_AO_EDITOR.md`.

## Critérios de aceitação

- `tests/test_r411_artigo_rbep_latex.py` verde (RED → GREEN).
- PDF gerado e não vazio; suíte acumulada R408–R411 verde.
- Ciclo R411 registrado no `evolution/cycles.json`; PROGRESS.md atualizado.

## Entregáveis

- `academic/papers/arm_education_audit/latex/ARTIGO_RBEP_SUBMISSAO.tex`
- `academic/papers/arm_education_audit/latex/ARTIGO_RBEP_SUBMISSAO.pdf`
- `tests/test_r411_artigo_rbep_latex.py`

## Não escopo

- Não altera números, dados, método ou conteúdo científico (R409/R410).
- Não declara "Qualis A1" nem prontidão editorial (anti-overclaim R142).
- Não instala abntex2 (ausente no ambiente); usa article.cls com formatação
  ABNT equivalente — as normas ABNT exigidas pela RBEP são de citação
  (NBR 10520) e referência (NBR 6023), já atendidas no conteúdo.
- Não submete o artigo à RBEP (ação humana).
