# SPEC-935-R254 — PDF de miolo sem capa e contracapa

## Objetivo

Gerar uma cópia em PDF contendo somente o miolo de `Molambudos — O Diário do Paciente 1.260`, removendo a capa frontal e a contracapa do PDF principal.

## Escopo

- Fonte de entrada: `projetos/molambudos/Molambudos_VictoriaRegia/main.pdf`.
- Remover a página de capa full-bleed criada por `frontmatter/titlepage.tex` antes da folha de rosto.
- Remover a página final de contracapa criada por `frontmatter/backpage.tex`.
- Preservar folha de rosto, front matter, passaporte, sumário, navegação, fragmentos, epílogo e nota histórica.

## Critérios de aceitação

1. O arquivo de saída existe e é um PDF válido.
2. O PDF de saída tem menos páginas que `main.pdf`.
3. A primeira página do PDF de saída não é a capa full-bleed; deve começar pela folha de rosto tipográfica ou página interna.
4. A última página do PDF de saída não é a contracapa full-bleed.
5. O miolo preserva trechos críticos:
   - `Molambudos`
   - `Passaporte de Leitura`
   - `MEM-07`
   - `A Mãe Levada`
   - `Nota Histórica`
6. O ISBN real `9798189170492` permanece presente no miolo.

## Artefato esperado

`Molambudos_O-Diario-do-Paciente-1260_miolo_sem-capa_v1.5_2026-07-26.pdf`

## Resultado verificado

- Entrada: `main.pdf`, 371 páginas.
- Corte aplicado: páginas 3–370.
- Páginas removidas:
  - 1–2: capa full-bleed e verso/folha em branco associada.
  - 371: contracapa full-bleed.
- Saídas geradas:
  - `Molambudos_O-Diario-do-Paciente-1260_miolo_sem-capa_v1.5_2026-07-26.pdf`
  - `main_miolo_sem_capa.pdf`
- Saída: 368 páginas, 2.277.966 bytes.
- Primeira página validada como folha de rosto tipográfica.
- Última página validada como nota histórica, não contracapa.
- Trechos críticos preservados:
  - `Molambudos`
  - `Passaporte de Leitura`
  - `MEM-07`
  - `A Mãe Levada`
  - `Nota Histórica`
  - `9798189170492`
- ISBN antigo ausente no miolo extraído.
