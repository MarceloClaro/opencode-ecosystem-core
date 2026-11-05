# SPEC-935-R1071 — Book Studio e auditoria do Molambudos

**Status:** implementado e validado localmente; nenhuma publicação ou validação
externa.
**Objetivo:** transformar o Core em um estúdio editorial capaz de manter um
projeto de livro, compilar PDF/EPUB, rodar QA físico e integrar manuscritos
LaTeX existentes, começando pelo Molambudos.

## 1. Componentes

| Componente | Papel |
|---|---|
| `marceloclaro/book_studio.py` | manifesto `book.json`, `init`, `build`, `qa`, `status`. |
| `skills/book-studio/SKILL.md` | interface `/book` e política editorial. |
| `.opencode/skills/book-studio/SKILL.md` | skill carregada pelo OpenCode. |
| `integrations/external_skills.py` | adaptador `book-studio` roteável pelo Centro. |
| `tests/test_r1071_book_studio.py` | testes de manifesto, Typst, EPUB, LaTeX, QA e path safety. |

## 2. Motores

| Motor | Uso | Licença | Instalação |
|---|---|---|---|
| Typst 0.15.1 | padrão para Markdown→PDF | Apache-2.0 | binário em `~/.local/share/opencode-core/typst/typst` |
| Pandoc 3.7 | Markdown→Typst/PDF/EPUB | GPL-2.0+ | sistema |
| WeasyPrint 67 | HTML/CSS paged media→PDF | BSD | sistema |
| LaTeX/latexmk | projetos `main.tex` existentes | GPL | sistema |
| Scribus | editor visual/print | GPL-2.0+ | externo, não instalado |
| Vivliostyle | HTML/CSS→PDF/EPUB | AGPL-3.0 | externo, não instalado |
| CaSILE | automação editorial | AGPL-3.0 | externo, não instalado |

Nenhum código GPL/AGPL foi copiado para o Core.

## 3. Manifesto

`book.json` contém título, autor, idioma, edição, editora, trim, engine,
`source` (LaTeX), capítulos, formatos e CSS opcional. `chapters` pode ser vazio
somente no engine `latex`, que usa `source`.

## 4. Build e QA

- PDF: Typst, Pandoc/LaTeX, WeasyPrint ou `latexmk`.
- EPUB: Pandoc `epub3`.
- QA: `pdfinfo`, `pdffonts`, `pdftotext`; páginas, trim, metadados, fontes
  embutidas, texto, criptografia.
- O QA não promove confiança editorial; retorna `human_review_required=True` e
  `external_validation=False`.

## 5. Molambudos

- Projeto: `literatura/molambudos/Molambudos_VictoriaRegia`.
- Manifesto: `book.json`, `engine=latex`,
  `source=main_kdp_pt_160x230mm.tex`, `trim=160x230mm`.
- Build: 435 pp, 160×230 mm, 15 fontes embutidas, metadados preenchidos, zero
  issues técnicos.
- Correções aplicadas: metadados PDF e 12 aspas retas → curly quotes.
- Auditoria detalhada local: `BOOK_STUDIO_AUDIT.md` no projeto (gitignored).
- `REVISAO_MOLAMBUDOS.md` recebeu nota de escopo: o parecer antigo descreve a
  versão incompleta de 4 capítulos, não a edição atual.

## 6. Aceitação

1. `init` cria `book.json` e capítulo de exemplo.
2. Typst compila dois capítulos e o QA vê páginas, texto, trim, metadados e
   fontes embutidas.
3. EPUB é um ZIP válido com `mimetype=application/epub+zip`.
4. Engine LaTeX compila um `main.tex` mínimo e o QA lê Title/Author.
5. Path traversal em capítulos é rejeitado.
6. `book-studio` aparece no registro e o Centro roteia “diagramar um livro”
   para ele com safe check rc=0.
7. Testes verdes.

**Resultado:** **119 passed** no conjunto R1071 + R1069 + R640 + Transformer +
autonomia + metacognição. O Molambudos KDP foi rebuildado com sucesso.

## 7. Limites

- QA técnico não substitui leitura crítica, prova de página, revisão de voz,
  preparação de texto ou parecer profissional independente.
- Não há PDF/X, tagged PDF, EPUB corrente ou aprovação KDP nesta rodada.
- O conteúdo do livro é gitignored e não foi versionado.
- Scribus/Vivliostyle/CaSILE não foram instalados nem executados.
- Nenhuma validação externa ou publicação.
