# R1074 — EPUB, preflight KDP e PDF acessível do Molambudos

**Data:** 2026-11-05  
**Status:** EPUB concluído e validado localmente; impressão **não KDP-ready**;
PDF tagged **bloqueado pelo toolchain**.

## 1. EPUB

Fonte: `main.tex` + 84 fragmentos + epílogo + frontmatter/backmatter canônicos.
Gerado com Pandoc 3.7; nenhum texto foi importado de `v2` ou do Diário
(excluídos).

| Item | Resultado |
|---|---|
| Arquivo | `literatura/molambudos/release/2026-11-05/epub/Molambudos_PT.epub` |
| Tamanho | 6.653.683 bytes |
| SHA-256 | `9f7a5ea58f6c1c72cc870e423412843173f004d374644f068a6e1d11b898aabe` |
| Partes | 5 |
| Seções de fragmento | 84 |
| Links de fragmento no TOC | 84 |
| Links totais no TOC | 105 |
| Links quebrados | 0 |
| Imagens | 7 |
| Imagens ausentes | 0 |
| LaTeX cru | 0 |
| Referências não resolvidas | 0 |
| Palavras | 54.663 |
| PDF canônico (palavras) | 56.439 |
| Razão | 0,969 |

Validação estrutural: ZIP, `container.xml`, OPF, `nav.xhtml`, spine, metadados,
links do TOC, imagens e seções com corpo. **EPUBCheck não está instalado**; não
há declaração de conformidade EPUB 3.

Gerador reproduzível: `scripts/build_molambudos_epub.py`.
Manifesto: `reports/r1074/epub_manifest.json`.

## 2. Preflight KDP local

Relatório: `reports/r1074/preflight_kdp.json`.  
**Status: FAIL — 13 passes, 5 avisos, 3 falhas.**

### Falhas

| ID | Evidência |
|---|---|
| `cover_resolution` | Arte principal da capa a ~163 DPI; KDP exige mínimo de 300 DPI. |
| `barcode_area_size` | Reserva 2,15×0,95 in; requisito adotado 2,0×1,2 in. |
| `barcode_position` | Reserva no canto inferior esquerdo; LTR pede o canto inferior direito. |

### Avisos

- `barcode_fake_art`: a contracapa contém código/ISBN fictício
  (`978-65-01-23456-7`); a caixa branca o cobre, mas o elemento deve sair da
  arte de origem.
- `interior_bleed`: páginas 1 e 435 têm imagem de página inteira; sem
  `BleedBox`, a sangria não está garantida.
- `interior_images_300dpi`: 12 imagens abaixo de 300 DPI (páginas 1, 37, 79,
  145, 257, 286, 287, 288, 299, 339, 361, 435).
- `interior_tagged`: `Tagged: no`; gap de acessibilidade digital.
- `last_page_blank`: página 435 branca; confirmar no previewer.

### Passes relevantes

- Trim personalizado 160×230 mm aceito pela KDP (faixa 4–8,5 × 6–11,69 in).
- 435 páginas; margens mínimas ≥19,34 pt; 0 violações de 18 pt.
- Fontes do miolo e da capa embutidas; PDF 1.7 sem criptografia.
- Capa 13,8706×9,3051 in; lombada 1,0222 in; sangria 0,125 in.
- ISBN 9798189170492 consistente entre capa e miolo.

## 3. PDF tagged

**Nenhum PDF tagged foi produzido.** Duas vias foram testadas:

| Via | Erro |
|---|---|
| LuaLaTeX + `accessibility` | `module 'luaotfload-main' not found`; fontes OpenType não carregam. |
| pdfLaTeX + `tagpdf`/`accessibility` | `Package tagpdf Error: The PDF version has changed after the loading of tagpdf from 2.0 to 2.6`. |

Evidências: `reports/r1074/evidence/tagged_lualatex.log` e
`tagged_pdflatex.log`. Estado: `reports/r1074/tagged_pdf_status.json`.

O EPUB é a entrega de acessibilidade digital desta rodada. Um PDF/UA exige
corrigir o TeX Live (`luaotfload`) ou usar um pipeline dedicado de tagging.

## 4. Caminho de correção

1. Reexportar capa e contracapa a 300 DPI (ou vetor).
2. Remover o código/ISBN fictício da arte.
3. Reservar 2,0×1,2 in no canto inferior direito da contracapa, a 0,25 in do
   corte.
4. Recompilar a capa e rodar novamente o preflight.
5. Conferir no previewer KDP, solicitar prova digital e prova física.
6. Para o miolo: garantir sangria nas páginas 1/435 ou inserir a arte dentro da
   área segura; substituir ícones de 105 DPI por fontes maiores/vetoriais.

## 5. Limites

- Preflight local; não substitui o previewer oficial da KDP.
- Nenhuma publicação, upload ou distribuição.
- Nenhuma validação editorial externa, banca ou leitura beta.
- O EPUB não passou por EPUBCheck.
- O PDF canônico segue como referência de impressão; a capa ainda precisa de
  correção antes de qualquer upload.
