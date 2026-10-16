# SPEC-935-R907 — Margens e recursos visuais do livro ampliado

Status: entregue com verificação local; ver manifesto R907.

## Objetivo

Conservar as ampliações didáticas R903–R906 e tornar suas tabelas, equações,
mapas mentais e fluxos legíveis no livro A4 existente. Dar continuidade à
revisão integral R901, sem substituir o documento aberto ou apagar conteúdo
adicionado pelo autor.

## Critérios de aceitação

1. Tabelas de texto usam colunas que permitem quebra dentro da largura local.
2. A seção didática acrescentada ao catálogo passa à fonte autoritativa do
   gerador e permanece após regeneração, com números derivados da configuração.
3. Os novos recursos visuais têm legenda, orientação de leitura, finalidade,
   limite e fonte local. Analogia e mecanismo executado são distinguidos.
4. Hipóteses matemáticas não se convertem em medidas de confiança ou desempenho
   do Core; incoerências numéricas identificadas são corrigidas.
5. O livro existente compila; estouros materiais são corrigidos. A inspeção
   de coordenadas do texto e a leitura de páginas renderizadas complementam o
   log, sem constituir estudo de aprendizagem ou auditoria externa.
6. Gates editoriais aplicáveis passam; o manifesto registra resultados,
   amostragem visual, hashes e limitações.

## Verificação

`tests/test_r907_livro_layout.py`, gates R617–R620/R814/R901, `check.py`,
compilação do `main.tex` existente e inspeção do PDF resultante.

## Fora de escopo

Reescrever o runtime para coincidir com um exemplo matemático, alterar materiais
de outros trabalhos ou declarar validação científica/educacional externa.
