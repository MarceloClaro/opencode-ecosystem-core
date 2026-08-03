---
spec_id: SPEC-935-R384
title: Estende regeneração Molambudos a CONT-03, MEM-27 e LUC-Escolha preservando notas editoriais exclusivas do .tex
component: projetos/molambudos/Molambudos_VictoriaRegia/fragmentos
status: verified
test_file: tests/test_r384_molambudos_extended_regen_editorial_notes.py
---

# SPEC-935-R384 — Estende Regeneração a CONT-03/MEM-27/LUC-Escolha

**Data:** 2026-08-03
**Motivação:** achado do R383 (fora de escopo naquele momento): o mesmo bug
de `extract_fragment_content()` (corrigido no R383) já tinha apagado
silenciosamente o epílogo de `CONT-03`, `MEM-27` e `LUC-Escolha` no `.tex`
publicado. O usuário pediu para prosseguir.

## 1. Achado real antes de executar (mais sério que o esperado)

Comparando em memória (sem sobrescrever nada) a saída fresca de
`fragment_to_tex()` contra os 3 fragmentos commitados, a divergência era
**muito maior** que "só o epílogo cortado":

- `CONT-03`: 8 palavras (≥6 caracteres) perdidas / 65 novas — o `.tex`
  publicado estava desatualizado em relação a uma revisão mais extensa do
  `molambudos.md` (faltavam passagens inteiras de interação com o leitor
  e a tabela "ESCALA DE CONTAMINAÇÃO --- ATUALIZAÇÃO 2").
- `MEM-27`: 43→61 linhas.
- `LUC-Escolha`: 69→86 linhas.

Isso não é o mesmo escopo mecânico do R383 (uma única linha cortada) —
é uma divergência editorial maior, reportada ao usuário antes de agir
(critério do projeto: nunca fabricar/descartar conteúdo sem confirmação
quando a mudança é maior que o comunicado inicialmente).

**Achado adicional, oposto ao anterior:** o `.tex` publicado tinha
conteúdo que **não existe em `molambudos.md`**:
- `CONT-03`: nota `\NE{Nota do Editor --- ...}` sobre a natureza
  simulada da "contaminação".
- `MEM-27`: nota `\NE{O editor registra: ...}` sobre a análise
  espectrográfica da tinta do diário.
- `LUC-Escolha`: parágrafo narrativo inteiro ("--- Mas havia uma quarta
  opção. [...] a diferença entre afogar-se e mergulhar.") — não é nota
  editorial, é conteúdo de história que nunca foi escrito de volta no
  `.md`.

Confirmado via `grep` no `molambudos.md`: nenhum desses 3 trechos existe
lá, em nenhuma forma.

## 2. Decisão do usuário

Perguntado explicitamente (3 opções: regenerar preservando as notas,
regenerar sem se preocupar, ou só documentar) — usuário escolheu
**regenerar preservando as notas/parágrafo**.

## 3. Execução

1. Backup manual criado antes de escrever:
   `projetos/molambudos/Molambudos_VictoriaRegia/_archive/backup_R384_pre_extend_regen/`
   (cópia dos 3 arquivos, árvores VictoriaRegia e canônica).
2. Regeneração via `fragment_to_tex()` (já com o fix do R383) para os 3
   IDs.
3. Reinserção manual, na posição textual original exata, dos 2 `\NE{...}`
   e do parágrafo da "quarta opção" — âncoras de texto verificadas
   (`assert marker in tex`) antes da inserção, para nunca inserir "no
   lugar errado" silenciosamente.
4. Verificação de conjunto de palavras (≥6 caracteres) contra o backup:
   `CONT-03` e `MEM-27` — zero palavras reais perdidas (só `rotasep`,
   artefato do antigo macro `\rota{}`/`\rotasep`, harmonizado para o
   estilo "↪ Links:" já adotado em `CONT-05..13` desde o R376).
   `LUC-Escolha` — zero palavras reais perdidas após a reinserção do
   parágrafo (só `rotasep`/`textquotedblleft`/`textquotedblright`,
   artefatos de macro, mesma categoria).

## 4. Verificação de proveniência

Reexecutada a verificação programática das 3 cadeias
(R360 reviews → R361 drift → R362 change manifest) sobre o novo estado:
**zero problemas**. `tests/test_r360_cultural_episteme_pilot.py` e
`tests/test_r361_molambudos_cultural_decision_matrix.py`: 19/19 verdes.
Conjunto de falhas Molambudos idêntico ao baseline (R382/R383).

## 5. Critérios de aceitação

1. `CONT-03.tex` e `MEM-27.tex` preservam seus respectivos `\NE{...}`
   na posição textual original.
2. `LUC-Escolha.tex` preserva o parágrafo da "quarta opção" na posição
   original.
3. Os 3 fragmentos recuperam o conteúdo real ausente (tabelas de escala,
   passagens de interação) presente em `molambudos.md`.
4. Árvore canônica (`projetos/molambudos/fragmentos/`) espelha
   exatamente a árvore VictoriaRegia para os 3 arquivos.
5. Zero problema nas 3 cadeias de proveniência (R360/R361/R362),
   verificado programaticamente.
6. Zero regressão no conjunto de testes Molambudos (idêntico ao
   baseline).
