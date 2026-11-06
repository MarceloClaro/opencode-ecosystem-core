# SPEC-935-R1077 — Variante print-safe do Molambudos

**Status:** implementado como candidato de impressão; não publicado.  
**Objetivo:** manter a identidade sensorial do R1076 e reduzir o custo/risco de
impressão, trocando fundo e páginas pretas por papel cream, tipografia e imagens
com resolução suficiente.

## 1. Requisitos

| ID | Requisito | Critério |
|---|---|---|
| R1 | Sem fundo impresso | Nenhum `\pagecolor` sépia no PDF print-safe; papel cream assume a temperatura |
| R2 | Aberturas de parte tipográficas | Numeral romano + título + filete + ícone; sem página preta |
| R3 | Rosto/colofão/Cuidado tipográficos | Sem arte de baixa resolução e sem fundo preto |
| R4 | Imagens ≥300 DPI | Todas as imagens colocadas a ≥300 DPI |
| R5 | CMYK controlado | Cores vetoriais em CMYK; TAC dos textos ≤205% |
| R6 | Cobertura de tinta | TAC médio <50%; TAC máximo <300% |
| R7 | PDF íntegro | 160×230 mm; fontes embutidas; sem referências indefinidas |
| R8 | Gate | `tests/test_r1077_molambudos_print.py` |

## 2. Entregáveis

| Caminho | Papel |
|---|---|
| `literatura/molambudos/Molambudos_Print_R1077/` | fonte e PDF print-safe |
| `main_kdp_print_r1077.pdf` | PDF 418 pp |
| `frontmatter/titlepage_print.tex` | rosto tipográfico |
| `frontmatter/backpage_print.tex` | colofão tipográfico |
| `frontmatter/cuidado_print.tex` | advertência tipográfica |
| `reports/r1077/print_manifest.json` | TAC, imagens, CMYK e hash |
| `tests/test_r1077_molambudos_print.py` | gate |

## 3. Aceitação

1. PDF 418 pp; 160×230 mm; fontes embutidas.
2. 20 imagens; mínimo 305 DPI; nenhuma abaixo de 300.
3. TAC médio 11,4%; máximo 173,4%.
4. Cores CMYK com TAC ≤205% nos elementos de texto.
5. R1076 digital permanece intacta.
6. Relatório declara: capa 300 DPI pendente, lombada a recalcular, sem nova
   ISBN, sem validação externa, sem 10/10.

## 4. Fora de escopo

- Corrigir a capa exterior em 300 DPI.
- Publicar, enviar à KDP ou distribuir.
- Atualizar traduções.
- Produzir PDF/UA.
- Certificar qualidade estética.
