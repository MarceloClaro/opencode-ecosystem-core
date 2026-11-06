# R1079 — Preflight dos artefatos existentes

**Status:** parcial. Os critérios de **saída** passam nos artefatos atuais; a
migração completa da cadeia (pdfcpu/qpdf/veraPDF/Quarto) não foi executada.
**Não é upload KDP, não é PDF/UA formal e não é prova física.**

## 1. Escopo

Verificação dos artefatos já produzidos:

- PDF print-safe R1077 (`main_kdp_print_r1077.pdf`);
- EPUB revisado R1075/R1076 (`Molambudos_PT_revisado.epub`).

Não houve rebuild completo do miolo. O objetivo é separar “o arquivo passa nos
critérios” de “o pipeline novo está completo”.

## 2. Resultado

| Verificação | Resultado | Evidência |
|---|---|---|
| Páginas do PDF | **422** | `pdfinfo` |
| Tamanho | **453,543 × 651,968 pt = 160 × 230 mm** | `pdfinfo` |
| Fontes | **15 fontes; 0 não embutidas** | `pdffonts` |
| Imagens | **20; mínimo 300 DPI** | `pdfimages -list` |
| TAC médio | **11,7%** | Ghostscript `inkcov` (manifesto R1077) |
| TAC máximo | **173,4%** | Ghostscript `inkcov` (manifesto R1077) |
| EPUBCheck | **5.4.0: 0 erros, 0 avisos** | execução local |
| Ace | **1.4.6: 26 pass, 0 fail** | execução local |
| `accessibilitySummary` | **presente** | OPF do EPUB |
| Fontes do template de capa | **todas embutidas** | `pdffonts` |
| Capa 300 DPI | frente vetorial re-renderizada em 1890 × 2717 px | prova em `/tmp/opencode` |

## 3. Ferramentas

**Executadas nesta rodada:**

- `pdfinfo`, `pdffonts`, `pdfimages`, `pdftoppm`;
- Ghostscript `inkcov`;
- EPUBCheck 5.4.0;
- Ace 1.4.6;
- WeasyPrint 67.0 e Typst 0.15.1 (piloto PDF/UA).

**Não executadas:**

- `pdfcpu`, `qpdf`, `veraPDF`;
- Quarto e build completo do miolo;
- preflight oficial da KDP.

Nenhuma ferramenta foi embutida no Core; todas rodaram como processos externos
em `/tmp/opencode`.

## 4. O que ainda impede declarar a fase completa

1. **veraPDF** para PDF/UA formal; o piloto tem estrutura tagged, mas não foi
   validado pelo perfil oficial.
2. **pdfcpu/qpdf** para preflight e transformação PDF no CI.
3. **Quarto/Typst** para um build novo do miolo, comparável ao LaTeX.
4. **Capa**: contracapa com proporção incompatível e barcode antigo; precisa de
   re-layout antes de qualquer upload.
5. **Trim 160 × 230 mm**: fora da lista conservadora de trims KDP; confirmar no
   previewer.
6. **ISBN** nova e prova física.

## 5. Próximo passo

1. Instalar pdfcpu/qpdf/veraPDF em `/tmp/opencode` e rodar o preflight.
2. Rodar veraPDF no piloto WeasyPrint e no PDF R1077 (este não é PDF/UA; o teste
   deve documentar a reprovação, não escondê-la).
3. Fazer um build Typst de um capítulo real e comparar páginas, fontes, TAC e
   estrutura com o LaTeX.
4. Só depois decidir migração do miolo.

## 6. Arquivos

| Caminho | Conteúdo |
|---|---|
| `preflight.json` | checks, hashes e ferramentas executadas/não executadas |
