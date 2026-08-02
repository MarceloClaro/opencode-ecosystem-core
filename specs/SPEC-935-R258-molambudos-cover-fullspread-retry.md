# SPEC-935-R258 — Nova tentativa da capa KDP usando spread completo

## Objetivo

Refazer a capa completa KDP de `Molambudos — O Diário do Paciente 1.260` usando diretamente a imagem full-spread fornecida, sem recortes de painéis e sem sobrepor caixa adicional de barcode.

## Diagnóstico da tentativa anterior

A tentativa R257 recortou painéis a partir de imagens interpretadas como `capa`, `lombada` e `contracapa`. Após nova inspeção, o arquivo mais adequado encontrado é:

`capa contracapa lombada.png`

Esse arquivo é um spread completo de `2996 × 2100 px`, já contendo contracapa, lombada e capa frontal alinhadas.

## Estratégia nova

- Usar `capa contracapa lombada.png` como imagem única de fundo.
- Ajustar a imagem para preencher exatamente o full cover KDP:
  - `14.635in × 10.417in`.
- Não aplicar recortes.
- Não adicionar barcode/ISBN sobre a arte, para não cobrir elementos gráficos.

## Artefatos esperados

- `capa_kdp_371_fullspread_final.tex`
- `capa_kdp_371_fullspread_final.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_capa-completa_Amazon-KDP_371p_FULLSPREAD_v1.5_2026-07-26.pdf`

## Critérios de aceitação

1. O TeX referencia explicitamente `capa contracapa lombada.png`.
2. O PDF compila sem erro.
3. O PDF final tem 1 página.
4. O tamanho de página é `14.635in × 10.417in`.
5. O PDF contém a imagem full-spread incorporada.
6. O PDF não contém guias técnicas nem overlays adicionais.

## Resultado verificado

Arquivos gerados:

- `capa_kdp_371_fullspread_final.tex`
- `capa_kdp_371_fullspread_final.pdf`
- `Molambudos_O-Diario-do-Paciente-1260_capa-completa_Amazon-KDP_371p_FULLSPREAD_v1.5_2026-07-26.pdf`

Validação:

- Imagem fonte: `capa contracapa lombada.png` (`2996 × 2100 px`).
- PDF final: `1` página.
- Tamanho: `14.635in × 10.417in`.
- Criptografia: `no`.
- Imagens incorporadas: `1` imagem full-spread.
- Guias/placeholder ausentes.
- Sem overlay extra de barcode/ISBN.
- Tamanho do PDF final: `8.883.066` bytes.

Observação: esta é a versão correta para preservar integralmente a arte fornecida pelo usuário. A tentativa anterior com recortes foi descartada como interpretação inadequada para esta imagem full-spread.
