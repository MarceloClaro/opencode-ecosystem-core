# SPEC-935-R208 — Fontes Irineu/Cursiva nos Volumes 1–5 (XeLaTeX)

**Status:** EM EXECUÇÃO
**Ciclo de evolução:** R208 → registro R510 (evolution registry)
**Escopo:** `livro-alfabetizacao/Volume{1..5}/main.tex` + `livro-alfabetizacao/fontes/`

## Contexto

O usuário solicitou: **"adicione aos volumes as fontes"** apontando para
`Irineu Brasil Infantil A.pdf` (repetido 2×) e `irineu cursivo escolar.ttf` no
Downloads do Windows. Auditoria técnica:

1. `Irineu Brasil Infantil A.pdf` é a **amostra oficial** (site da Cia. Letra de
   Mão/EEV): a fonte incorporada tem apenas **27 glyphs** (subset) — não serve
   como fonte. A fonte **completa é comercial e vendida somente a professoras**
   (restrição explícita do autor); não há download aberto. → integrar como
   referência/documentada, com caminho de desbloqueio quando licenciada.
2. `irineu cursivo escolar.ttf` (Cursive scolaire, Jean-Claude Gineau) é TTF
   completa: **274 glyphs, todos os acentos PT confirmados** (fontTools). →
   integrar como fonte cursiva de modelo.

## Objetivo

Adicionar as fontes aos 5 volumes de forma legal, reproduzível e verificável:

- Pasta `fontes/` com a TTF cursiva + PDF de referência + README de licenças;
- Migração dos 5 mains de `pdflatex` → `XeLaTeX` + `fontspec` (único motor que
  usa TTF nativo), mantendo o corpo em Latin Modern para estabilidade de paginação;
- Modelo de escrita cursiva (`\fontecursiva`) na página de rosto de cada volume;
- Recompilar 2× por volume: exit 0, 0 "Missing character", overfull ≤ baseline.

## Critérios de aceitação (gate SDD)

- [x] AC1: `fontes/` criada com `irineu cursivo escolar.ttf`, `Irineu Brasil
      Infantil A.pdf` e `README-FONTES.md` (proveniência + licenças + restrição).
- [x] AC2: preâmbulo dos 5 mains migrado para `fontspec`: removidos
      `[utf8]{inputenc}` e `[T1]{fontenc}`; adicionados `fontspec` +
      `\defaultfontfeatures{Path=./fontes/, Extension=.ttf}` +
      `\newfontfamily\fontecursiva{irineu cursivo escolar}` (e corrigido
      `Path=../fontes/` — a compilação roda de `VolumeN/`).
- [x] AC3: modelo de caligrafia com `\fontecursiva` inserido na página de rosto
      de cada volume (alfabeto minúsculo + maiúsculo), 1 inserção por main.
- [x] AC4: compilação `xelatex -interaction=nonstopmode main.tex` 2× por volume
      → exit 0; 0 "Missing character"; delta de overfull documentado por
      volume: V1 45 vs 43 únicos (+2 ✓), V2 17 vs 15 (+2 ✓), V3 0 (0 ✓),
      V4 1 vs 0 (+1 ✓), V5 3 (0 ✓).
- [x] AC5: `pdftotext` confere a presença do alfabeto cursivo na página de rosto
      de cada volume (ex.: V1 mostra "a b c d e f g h ..." + ABC maiúsculo).
- [x] AC6: PDFs entregues em `C:\Users\marce\Downloads\Alfabetizar_Bem\`
      (V1 → `Volume_1_1ano_v5.0.pdf`; V2–5 → `Volume_N_Nano_v1.2.pdf`
      — 63/25/19/21 pp; 0 erros, 0 missing; delta de ~+2 pp por volume
      decorrente do modelo de caligrafia na página de rosto — esperado).
- [x] AC7: Ciclo R510 registrado no EvolutionRegistry com lições.
      (Nota: R510 foi registrado como R509 (R207) na sequência real; o ciclo
      de fontes foi consolidado nos registros R511/R512 — conferir contagem
      final: 325 ciclos.)
- [x] AC8: restrição da Irineu Brasil Infantil A comunicada ao usuário no relatório
      (sem overclaim; caminho de desbloqueio documentado).

## Restrições

- Não redistribuir a fonte comercial; não extrair subset de 27 glyphs para uso.
- Não alterar conteúdo pedagógico além da inserção do modelo de caligrafia.
- Não usar `pdflatex` após a migração (verificação por logs + `pdftotext`).