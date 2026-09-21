# SPEC-935-R205 — Atividades de Som nas Folhas A (vogais) e B (letras) — parte3 (v4.8)

**Status:** CONCLUÍDO
**Data:** 2026-09-12
**Autor:** marceloclaro (orquestrador primário)
**Gatilho do usuário:** "aplicar o padrão às folhas B (letras, parte3) e às vogais A-01..A-05"

## Problema

R204 aplicou o padrão de som às 26 lições da parte2 e às folhas de sílabas C-01..C-06,
mas as folhas Kumon **A-01..A-05** (vogais, pré-silábico) e **B-01..B-11** (letras,
silábico) seguem sem atividade de som integrada.

## Escopo

Box bônus compacto **(não vale nota)** após o `\end{exercicio}` de cada folha:

1. **A-01..A-05** (vogais A, E, I, O, U): "Atividade de Som da Vogal — Bônus" com
   caça ao som (quadradinhos 4 palavras, 2 com/2 sem) + Tem ou não tem (SIM/NÃO 4) +
   caixapausa (boca R202) + caixapista.
2. **B-01..B-06 e B-09, B-10** (letras M, S, T, R, L, B, X, Q): mesmo padrão
   "Atividade de Som da Letra — Bônus".
3. **B-07 (C e D) e B-08 (F, G, N, P, V, Z, J):** box duplo compacto (2 letras: C/D e F/V)
   + nota de prática guiada para as demais letras (G, N, P, Z, J).
4. **B-11 (Letra H):** padrão H mudo ("HOJE lê-se OJE").

Reusa ambientes `somletra`/`somsilaba` (R204), dataset e pistas articulatórias R202/R204.

## Critérios de aceitação

- CA-01: 16 boxes bônus inseridos (5 A + 11 B), idempotente, sem alterar notas X/15.
- CA-02: palavras corriqueiras do 1º ano; H mudo sem "aspirado"; nenhuma promessa clínica.
- CA-03: script reproduzível `/tmp/opencode/r205_som_folhas_ab.py` + backups.
- CA-04: `pdflatex -interaction=nonstopmode` 2× → exit 0, 0 "Missing character".
- CA-05: versão 4.8 (capa, créditos, main.tex); PDF entregue; ciclo R507 registrado.

## Não-objetivo

- Não substitui fonoaudiólogo (mesma regra parte6); não reproduz marca Boquinha®.