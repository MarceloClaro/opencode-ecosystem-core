---
spec_id: SPEC-935-R440
component: producao_cientifica.armadilha_renda_media_ideb
title: Artigo Qualis A1 expandido (26 páginas) — sem seção interna de banca, tabelas/figuras nas margens
version: 1.0.0
status: green
test_file: tests/test_r439_rigorous_board.py
---

# SPEC-935-R440 — Artigo Armadilha da Renda Média × IDEB Crateús/Ceará: expansão editorial

## Objetivo
Expandir o manuscrito para formato de periódico (alvo ~25 páginas A4), aprofundando Método e Resultados parágrafo a parágrafo, com tabelas e figuras geradas dos dados oficiais processados, todos os elementos dentro das margens, e a validação por banca rigorosa deslocada para documento separado — com score de banca > 95/100.

## Critérios de aceitação
1. Seção "8. Validação por Banca Rigorosa" ausente do corpo; relatório separado (`RELATORIO_BANCA_R439.md`) presente.
2. Artigo final com 25–27 páginas A4, fonte 10 pt DejaVu Serif, margens 2,2 cm, Sumário.
3. **0 overfull boxes** no LaTeX (verificado via compilação intermediária com log).
4. 7 tabelas e 6 figuras; figuras geradas por `scripts/gerar_figuras_tabelas.py` diretamente dos JSONs oficiais (INEP/IBGE) — zero dados fabricados.
5. Números idênticos ao `outputs/expanded/resultados_r428.json` autoritativo (between −0,237; FE β=2,607/wild 0,230; MDES 6,01; TOST p=0,852; metas 107/108; ganho 5,93).
6. `RigorousBoard` ≥ 9,5/10 (≥95/100) em todos os venues; orquestrador `approved=True`.
7. Regressão: suíte R433–R439 permanece GREEN.
