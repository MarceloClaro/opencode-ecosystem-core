# R1091 — Preflight local KDP (equivalente)

**Data:** 6 de novembro de 2026.

**Escopo:** checagem local dos artefatos de produção. **Não substitui** o
Kindle Previewer oficial, o previewer online da KDP, o EPUBCheck/Ace ou a prova
física. O veredito abaixo é `PASS_LOCAL`; o gate oficial da KDP **não foi
executado** neste ambiente.

## 1. Artefatos

| Artefato | Papel | Páginas | SHA-256 |
|---|---|---:|---|
| `main_kdp_pt_160x230mm.pdf` | miolo digital de leitura | 423 | `bd78c8db32db2976e2c087bf342cf909a232c56f3348885ea577d9f82773902a` |
| `main_kdp_print_r1077.pdf` | **miolo de impressão KDP** | 422 | `1490915c06ab5250389090d1a739135bd998629341b30a5c3b33e8502f1b5e5b` |
| `Molambudos_PT_revisado.epub` | edição digital | 84 seções | `70e4216a81564f88cabf7b1f9ef037b43357f568f34b12f7aee3071f3899276c` |
| `molambudos_capa_completa_422p_print_300dpi.pdf` | capa de produção 422p | 1 | `dee30337035b96237c64f3c6d12f835c6cd6474729719892c3ff662f594707da` |

## 2. Miolo de impressão R1077 — o arquivo para a KDP

- **422 páginas**; 453,543 × 651,968 pt = **160 × 230 mm**.
- `TrimBox = MediaBox` (sem sangria; correto para miolo).
- **Fontes:** todas embutidas; nenhuma ausente.
- **Imagens:** 20; menor resolução efetiva **300 DPI**; nenhuma abaixo de 300.
- **Margens:** 5.289 blocos de texto examinados; **nenhum** a menos de 18 pt
  (0,25 in) da borda.
- **Estrutura:** Ghostscript `nullpage` retornou 0, sem erro.
- **Paginação × lombada:** 422 × 0,002347 in = **25,157 mm**; a capa 422p usa
  exatamente essa lombada.

## 3. Miolo digital R1075 — leitura, não KDP

- **423 páginas**; 160 × 230 mm; fontes embutidas; Ghostscript 0.
- **20 imagens**; mínimo de **105 DPI**. As cinco imagens de 300 × 300 px são
  os ícones de abertura de parte, exibidos a 300 pt; as cinco fotos ficam entre
  222 e 296 DPI no tamanho de leitura.
- **Margens:** 5.289 blocos; nenhum a menos de 18 pt da borda.
- **Este PDF não é o arquivo de upload KDP.** O miolo de impressão é o R1077,
  com mínimo de 300 DPI. O digital é a edição de leitura.

## 4. Capa 422p

- **1 página**; 996,4 × 669,97 pt = **351,507 × 236,35 mm**.
- `TrimBox` recuado 9 pt (3,175 mm); `BleedBox = MediaBox`; sangria presente.
- **2 imagens** a **302,4 DPI**; **4 fontes** embutidas.
- Texto contém título, autoria, Joaquim e Lúcia; **não** contém `ISBN`,
  `978-65-01-23456-7` nem “62 anos”.
- **Lombada:** 25,157 mm; textos da lombada com folga superior a 15 pt (5,3 mm)
  das dobras, acima do mínimo de 1,6 mm.
- **Área de código de barras:** 50,8 × 30,48 mm no canto inferior direito da
  contracapa, com 6,35 mm de afastamento; recorte visualmente branco, média
  254,6/255. O mínimo 113 vem de poucos pixels de borda do recorte, não de texto
  ou arte.
- A capa não imprime ISBN; a KDP adiciona o código. O ISBN do miolo é
  `979-8-18-917049-2`, no colofão.

## 5. EPUB

- `unzip -t`: íntegro.
- **84 seções**; **107 links** no TOC; **0 quebrados**; **0 LaTeX cru**;
  **0 imagens ausentes**; **13 imagens**; **53.175 palavras**; razão
  0,952 em relação ao PDF.
- Capa embutida `media/file12.png` em **1890 × 2717 px** (a prancha 300 DPI).
- **EPUBCheck e Ace não estão instalados** neste ambiente; a validação é
  estrutural local. O release anterior declarava EPUBCheck 5.4.0/Ace 1.4.6,
  mas esses resultados **não foram reexecutados** para esta versão.

## 6. O que o preflight local não prova

- O **Kindle Previewer oficial** e o **previewer online da KDP** não estão
  disponíveis; não houve renderização no motor oficial.
- **Prova física** não foi produzida; cor, papel, registro frente/verso e
  lombada só se confirmam em prova.
- **EPUBCheck/Ace** não foram executados.
- **PDF/UA** não foi alcançado (`Tagged: no`).
- Não houve leitura humana independente, revisão de galerada ou validação
  histórica/clínica.

## 7. Comandos usados

```bash
pdfinfo -box <pdf>
pdffonts <pdf>
pdfimages -list <pdf>
pdftotext <pdf> -
gs -q -dNOPAUSE -dBATCH -sDEVICE=nullpage <pdf>
unzip -t <epub>
```

As margens foram medidas com PyMuPDF (`page.get_text("blocks")` e distância
mínima até as bordas). A área de código de barras e a capa foram conferidas com
Pillow/PyMuPDF sobre as pranchas de 300 DPI.

## 8. Conclusão

**PASS_LOCAL** para o miolo de impressão R1077, a capa 422p e a estrutura do
EPUB. **O gate oficial da KDP continua pendente**: não envie o livro sem o
Kindle Previewer/previewer online e a prova física. A branch de código pode ser
publicada; o upload do livro não.
