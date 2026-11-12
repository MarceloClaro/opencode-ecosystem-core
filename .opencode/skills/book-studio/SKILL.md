---
name: book-studio
description: >
  Estúdio editorial do Core para livros: manifesto, build PDF/EPUB e QA técnico.
  Use para diagramar manuscritos Markdown com Typst/Pandoc/WeasyPrint, compilar
  projetos LaTeX com TinyTeX/LuaLaTeX (memoir, fontspec, microtype) e revisar
  PDF (páginas, trim, fontes embutidas, metadados, texto) e manuscritos
  (norma PT-BR, consistência, repetições, clichês). LanguageTool local é
  opcional. Scribus, Vivliostyle e CaSILE são engines externas: o Core verifica
  presença e prepara handoff, sem copiar código GPL/AGPL. Não publica, não
  declara qualidade editorial sem revisão humana e não substitui leitura
  crítica.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R1111
spec: SPEC-935-R1111-book-studio-tex.md
---

# Book Studio (R1071/R1111)

Base: R1071/R1078; esta revisão acrescenta TeX/LuaLaTeX e revisão literária (R1111).

O Core deixa de apenas gerar manuscritos: passa a manter um **projeto de livro**
com manifesto, capítulos, build e QA físico do PDF.

## Comandos

| Comando | Ação |
|---|---|
| `/book status [root]` | Motores disponíveis, projeto e capítulos |
| `/book init <root> --title ... --author ... [--trim 6x9in] [--engine typst\|latex] [--source main.tex]` | Cria `book.json` e capítulo de exemplo |
| `/book design <root> --title ... --author ... [--trim 160x230mm] [--chapter-count N] [--bibliography] [--index]` | Cria projeto LaTeX `memoir`/LuaLaTeX com design tokens |
| `/book tex <root> [--clean] [--timeout 600]` | Compila `main.tex` com `latexmk -lualatex` e roda QA |
| `/book build <root> [--engine typst\|pandoc\|weasyprint\|latex] [--format pdf\|epub]` | Compila e roda QA |
| `/book qa <pdf> [--trim 160x230mm]` | Metadados, páginas, trim, fontes e texto |
| `/book review <texto> [--languagetool] [--endpoint URL]` | Gate literário nativo PT-BR + LanguageTool |

## Motores

| Motor | Uso | Licença |
|---|---|---|
| Typst | padrão automatizado; Markdown→Typst→PDF | Apache-2.0 |
| Pandoc/LaTeX | manuscritos Markdown ou `main.tex` existente | GPL/BSD (ferramenta externa) |
| WeasyPrint | HTML/CSS paged media | BSD |
| Scribus | diagramação visual/print externa | GPL-2.0+ |
| Vivliostyle | HTML/CSS→PDF/EPUB externo | AGPL-3.0 |
| CaSILE | automação editorial externa | AGPL-3.0 |

O Core **não copia** código GPL/AGPL. Scribus/Vivliostyle/CaSILE ficam no
registro como engines externas.

## Toolchain TeX (R1111)

- TinyTeX em `~/.TinyTeX`; binários ligados em `~/.local/bin` (`latexmk` 4.89,
  LuaHBTeX 1.24.0, `biber` 2.22).
- Fontes Libertinus em
  `~/.TinyTeX/texmf-dist/fonts/opentype/public/libertinus-fonts`.
- O Core não embute TeX Live: `book tex` invoca `latexmk -lualatex` externo.
- `book build --engine latex` é o caminho legado (`latexmk -pdf`);
  `book tex` é o caminho `memoir` + LuaLaTeX + `fontspec` + `microtype`.
- Sem `shell-escape`; o build não usa rede.

## Revisão literária (R1111)

- `book review` aplica regras nativas: aspas retas, reticências, travessão,
  espaço antes de pontuação, muletas, clichês, repetição próxima, frase ou
  parágrafo longo, advérbios em `-mente` e aspas desbalanceadas.
- `--languagetool` consulta `http://127.0.0.1:8081/v2/check` em `pt-BR`. Se o
  servidor não estiver ativo, o relatório declara a indisponibilidade e mantém
  o gate nativo.
- Iniciar o servidor:

  ```bash
  ~/.local/share/opencode-core/jre/bin/java \
    -cp ~/.local/share/opencode-core/languagetool/languagetool-server.jar \
    org.languagetool.server.HTTPServer --port 8081
  ```

- Todo relatório tem `human_review_required=true` e
  `external_validation=false`; nenhum achado aprova o texto.

## Projeto Molambudos

```bash
python3 -m marceloclaro.book_studio status \
  projetos/molambudos/Molambudos_VictoriaRegia
python3 -m marceloclaro.book_studio build \
  projetos/molambudos/Molambudos_VictoriaRegia --engine latex --timeout 300
```

Manifesto: `book.json` no projeto, `engine=latex`,
`source=main_kdp_pt_160x230mm.tex`, `trim=160x230mm`.

## Gates

1. Toda entrega tem manifesto e QA; build não é aprovação editorial.
2. Fontes precisam estar embutidas; trim e página precisam bater.
3. Metadados Title/Author/Subject/Keywords são obrigatórios.
4. Não publicar, não enviar à KDP e não declarar PDF/X sem inspeção externa.
5. Scribus/Vivliostyle/CaSILE exigem decisão e instalação externas.
6. Nenhuma validação externa é inferida de QA técnico.
7. `book tex` não usa `shell-escape` e não declara PDF/UA ou PDF/X.
8. `book review` é heurístico: não aprova, não atribui nota e não substitui
   revisão humana; LanguageTool pode estar indisponível ou errar.
9. Nenhum relatório pode usar "aprovado", "10/10", "publicável" ou
   "Qualis" sem validação externa explícita.

## Limites

- QA não avalia estética, voz, ritmo, verossimilhança ou adequação editorial.
- Não substitui revisão humana, prova de página, leitura de galerada ou parecer.
- EPUB gerado por Pandoc não preserva necessariamente o layout do PDF.
- LanguageTool é externo e opcional; a indisponibilidade é declarada no relatório.
- Regras nativas de revisão produzem falsos positivos e falsos negativos.
