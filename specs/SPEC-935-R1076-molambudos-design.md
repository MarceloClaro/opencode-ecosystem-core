# SPEC-935-R1076 — Direção visual e tipográfica do Molambudos

**Status:** implementado na edição revista; PDF e EPUB gerados localmente.  
**Objetivo:** dar identidade visual legível aos quatro códigos do romance,
instalar uma capitular de família em cada fragmento e acrescentar um caderno
iconográfico ético.

## 1. Requisitos

| ID | Requisito | Critério |
|---|---|---|
| R1 | Paleta legível | Cores de leitura com contraste ≥4,5:1 sobre `#F8F0D7`; dourado/olho só em fundo escuro |
| R2 | Cor por código | MEM cobre, DOC teal, LUC violeta, CONT carmim aplicados a inicial, filete e rótulo |
| R3 | Capitular em cada fragmento | 84/84 com inicial da família (M/D/L/C) e rótulo “Memória/Documento/Lucidez/Contaminação” |
| R4 | Legenda | Página “Legenda dos Códigos” com quatro famílias, cores e contraste |
| R5 | Caderno iconográfico | 6 pranchas do arquivo existente, legendas de ficção documental e aviso de não prova histórica |
| R6 | PDF/EPUB | PDF 160×230 mm com fontes embutidas; EPUB com 84 seções e 13 imagens |
| R7 | Não overclaim | Nenhuma nota 10/10, validação profissional ou prova histórica declarada |
| R8 | Gate | `tests/test_r1076_molambudos_design.py` |

## 2. Decisões de design

- A capitular é a **inicial da família**, não uma segunda capitular textual:
  evita duas iniciais concorrentes e mantém os 84 fragmentos coerentes.
- O código é redundante em cor, letra e nome; isso protege leitores com
  daltonismo.
- O caderno usa imagens já existentes; a geração de novas imagens estava
  indisponível e não se inventaram imagens de vítimas.
- O dourado e o amarelo do olho ficam restritos a fundos escuros.

## 3. Entregáveis

| Caminho | Papel |
|---|---|
| `main.tex` | macros `\fragtitle`, `\fragfamily`, `\fragcode`, `\fragcap` e paleta |
| `fragmentos/**/*.tex` | 84 aberturas com capitular de família |
| `frontmatter/legenda_codigos.tex` | legenda visual |
| `frontmatter/caderno_iconografico.tex` | 6 pranchas e nota ética |
| `figures/immersao/placa_00..05.png` | imagens recortadas e legendadas |
| `reports/r1076/design_manifest.json` | paleta, contraste, tipografia, hashes |
| `tests/test_r1076_molambudos_design.py` | gate |

## 4. Aceitação

1. 84/84 fragmentos com `\fragtitle` e inicial de família.
2. Contraste ≥4,5:1 para MEM/DOC/LUC/CONT/EPI.
3. Legenda e caderno presentes no PDF e no EPUB.
4. PDF 421 pp, fontes embutidas; EPUB 84 seções, 13 imagens, 0 links quebrados.
5. Nenhuma imagem apresentada como prova histórica.
6. Relatório declara limites: capa/lombada a recalcular, sem nova ISBN, sem
   validação externa, sem 10/10.

## 5. Fora de escopo

- Redesenhar a capa em 300 DPI ou recalcular a lombada.
- Gerar novas imagens de pessoas ou vítimas.
- Atualizar traduções EN/ZH/TRI.
- Produzir PDF/UA.
- Certificar qualidade estética ou nota de banca.
