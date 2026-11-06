# Preflight KDP local — Molambudos

**Status: FAIL.** O pacote de impressão ainda não está pronto para upload.

## Falhas

1. **Resolução da capa**: arte principal a ~163 DPI; KDP exige mínimo de 300 DPI.
2. **Área de barras**: reserva 2,15×0,95 in; requerido 2,0×1,2 in.
3. **Posição da área de barras**: reserva no canto inferior esquerdo; para LTR, o KDP posiciona no canto inferior direito.

## Avisos

- Capa/contracapa contêm código e ISBN fictício (`978-65-01-23456-7`) na arte; remover da fonte.
- Páginas 1 e 435 usam imagem de página inteira sem BleedBox; confirmar sangria.
- 12 imagens do miolo abaixo de 300 DPI (páginas 1, 37, 79, 145, 257, 286, 287, 288, 299, 339, 361, 435).
- PDF não é tagged (`Tagged: no`); gap de acessibilidade digital.
- Página 435 é branca; confirmar no previewer.

## Passes

- Trim personalizado 160×230 mm aceito pela KDP (faixa 4–8,5 × 6–11,69 in).
- 435 páginas; margens mínimas ≥19,34 pt; 0 violações de 18 pt.
- Fontes do miolo e da capa embutidas; PDF 1.7 sem criptografia.
- Capa 13,8706×9,3051 in; lombada 1,0222 in; sangria 0,125 in.
- ISBN 9798189170492 consistente entre capa e miolo.

## Limite

Preflight local; não substitui o previewer oficial da KDP nem a prova física.
