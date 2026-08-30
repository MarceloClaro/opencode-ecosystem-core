---
spec_id: SPEC-935-R456
title: Manual técnico (formato banca de doutorado) da arquitetura RAG e da proposta pós-Recamán
component: docs/r456_manual_tecnico_rag, rag/*
status: red
round_id: R456
test_file: tests/test_r456_manual_tecnico_rag.py
---

# SPEC-935-R456 — Manual técnico da arquitetura RAG e da proposta pós-Recamán

## Objetivo

Produzir um manual técnico completo, no formato de banca de doutorado, compilado
 em PDF, documentando (i) o estado atual da arquitetura RAG do ecossistema e
 (ii) a arquitetura-alvo **proposta** após a implementação do diversificador de
 Recamán. O manual deve deixar **explícito** que a arquitetura "pós-Recamán" é
 uma proposta (não implementada), preservando a riqueza informativa dos mapas de
 dados existentes e oferecendo legendas, cálculos, especificações técnicas e
 referências reais validadas.

## Critérios de Aceitação Executáveis

- `spec_exists` — existe `specs/SPEC-935-R456-manual-tecnico-rag-recaman.md`.
- `manual_source_exists` — existe o fonte LaTeX do manual em
  `docs/r456_manual_tecnico_rag/manual_rag_recaman.tex`.
- `bibliography_exists` — existe `docs/r456_manual_tecnico_rag/referencias.bib`
  com entradas de fontes reais verificadas.
- `build_script_exists` — existe um script reproduzível de compilação
  (`build.sh` ou `Makefile`) em `docs/r456_manual_tecnico_rag/`.
- `manual_is_compilable` — o fonte LaTeX compila para PDF sem erro fatal com a
  toolchain local (`pdflatex` + `bibtex`/`biber` + `latexmk`).
- `pdf_produced` — a compilação gera `manual_rag_recaman.pdf`.
- `pdf_is_readable` — `pdftotext` extrai texto não trivial do PDF (manual legível).
- `distinguishes_current_from_proposal` — o manual rotula explicitamente a
  arquitetura "pós-Recamán" como **proposta/futura**, não como estado atual.
- `references_real_and_validated` — as referências citadas no manual correspondem
  a fontes reais previamente validadas (DOIs/arXiv verificados), sem fabricação.
- `cites_current_components` — o manual referencia os componentes RAG
  implementados (`rag/evolved.py`, `rag/enhanced_search_rag.py`).
- `no_external_certification_claim` — o manual não alega certificação externa ou
  segurança absoluta.
- `legends_and_calculations_present` — o manual contém legendas para diagramas e
  cálculos/equações com especificações técnicas.

## Estratégia TDD

1. Escrever testes documentais (RED) que validem a existência dos fontes, a
   distinção atual/proposta e a ausência de alegações indevidas.
2. Redigir o manual LaTeX e a bibliografia com referências reais.
3. Compilar o PDF e validar com `pdftotext`/`pdfinfo`.
4. Executar os testes documentais e registrar recibo local da rodada.

## Não objetivos

- Não implementar o diversificador de Recamán neste round — apenas documentar a
  proposta.
- Não prometer disponibilidade universal de serviços ou modelos.
- Não fabricar DOIs, autores, páginas ou datas.
