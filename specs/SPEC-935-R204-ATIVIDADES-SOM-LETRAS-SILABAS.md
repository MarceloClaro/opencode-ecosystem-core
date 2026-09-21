# SPEC-935-R204 — Atividades de Som em Cada Letra e por Sílabas (v4.7)

**Status:** CONCLUÍDO
**Data:** 2026-09-12
**Autor:** marceloclaro (orquestrador primário)
**Gatilho do usuário:** "amplie as atividades de som em cada atividade de letra e por sílabas"

## Problema

O R203 criou 38 planchetas de som isoladas (parte7), mas o usuário quer atividades de som
**integradas** ao contexto de cada atividade de letra (parte2: 26 lições A–Z) e **por sílabas**
(parte3: folhas Kumon C-01..C-06, Silábico-Alfabético).

## Escopo

1. **parte2 — cada letra (26):** nova plancheta "Atividade de Som e Sílabas da Letra X" após a
   `familiasilabica` de cada letra, com 4 exercícios compactos:
   - (1) Caça ao som: marcar quadradinhos das palavras que têm o som da letra (3 com / 3 sem);
   - (2) Tem ou não tem?: rondear SIM/NÃO para 4 palavras (2 com / 2 sem);
   - (3) Som das sílabas: bata palmas, escreva quantas sílabas (2 palavras com separação pronta);
   - (4) Qual sílaba tem o som?: sílaba em negrito nas mesmas palavras;
   - caixapausa (dica articulatória/boca R202) + caixapista.
   - Letra H tratada à parte (H mudo: "HOJE lê-se OJE").
2. **parte3 — folhas C-01..C-06:** box bônus "Som das Sílabas" após cada folha (fora do
   `exercicio`, sem alterar a nota): 3 palavras para contar sílabas com palmas + pista.
3. **Classe:** 2 ambientes tcolorbox novos (`somletra`, `somsilaba`) no estilo `sonsdaletra`/`familiasilabica`.

## Critérios de aceitação

- CA-01: 26 planchetas "Atividade de Som e Sílabas" inseridas (uma por letra, idempotente).
- CA-02: 6 boxes bônus "Som das Sílabas" nas folhas C-01..C-06 (não alteram a nota das folhas).
- CA-03: palavras corriqueiras do 1º ano; ausente promessa clínica; H mudo sem "aspirado".
- CA-04: script reproduzível `/tmp/opencode/r204_som_letras_silabas.py`; backups antes da edição.
- CA-05: `pdflatex -interaction=nonstopmode` 2× → exit 0, 0 "Missing character".
- CA-06: versão 4.7 (capa, créditos, main.tex); PDF entregue; ciclo R506 registrado.

## Não-objetivo

- Não substitui fonoaudiólogo; atividades observacionais e lúdicas (mesma regra parte6).
- Não reproduz a marca Boquinha®; bocas usadas são ilustrações originais R202.