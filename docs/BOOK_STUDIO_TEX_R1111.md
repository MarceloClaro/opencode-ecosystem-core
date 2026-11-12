# Book Studio TeX — guia operacional (R1111)

O Book Studio agora compila livros em LaTeX com **memoir + LuaLaTeX**, valida o
PDF sem depender de poppler e revisa o manuscrito em PT-BR com regras nativas e
LanguageTool local. Nada aqui publica, certifica PDF/UA ou aprova qualidade
literária.

## Toolchain instalado

| Item | Caminho / versão |
|---|---|
| TinyTeX | `~/.TinyTeX` (TeX Live 2026) |
| LuaLaTeX | `~/.local/bin/lualatex` (LuaHBTeX 1.24.0) |
| latexmk | `~/.local/bin/latexmk` (4.89) |
| biber | `~/.local/bin/biber` (2.22) |
| Fontes | Libertinus Serif/Sans/Mono OTF |
| JRE | `~/.local/share/opencode-core/jre` (Temurin 21) |
| LanguageTool | `~/.local/share/opencode-core/languagetool` (6.6) |

O Core não embute TeX Live nem LanguageTool: apenas invoca os binários externos.

## Fluxo mínimo

```bash
cd /home/marceloclaro/opencode-ecosystem-core

# 1. Criar o projeto LaTeX (160x230 mm por padrão)
.venv/bin/python -m marceloclaro.book_studio design /tmp/meu-livro \
  --title "Título do Livro" --author "Autor" --trim 160x230mm

# 2. Editar os capítulos
$EDITOR /tmp/meu-livro/chapters/01.tex

# 3. Compilar com LuaLaTeX e rodar QA
.venv/bin/python -m marceloclaro.book_studio tex /tmp/meu-livro --clean

# 4. QA avulso
.venv/bin/python -m marceloclaro.book_studio qa \
  /tmp/meu-livro/build/book.pdf --trim 160x230mm
```

O PDF fica em `build/book.pdf`; `book.json` e `book-design.json` registram
manifesto e tokens.

## Padrões de design

- Trim 160 × 230 mm, bleed 3 mm, margens espelhadas (interna 22 mm, externa
  18 mm, superior 20 mm, inferior 25 mm).
- Corpo 11 pt, entrelinha 14,5 pt, `\flushbottom`, viúvas/órfãs bloqueadas.
- Libertinus Serif no corpo (números oldstyle), Libertinus Sans nos títulos,
  Libertinus Mono no código.
- `memoir` com `\chapterstyle{veelo}`, running heads e folios externos.
- `microtype`, `babel` pt-BR, `fontspec`, `hyperref`, `bookmark`, `booktabs`,
  `caption`, `enumitem`, `graphicx`; `biblatex`/`biber` e índice são opcionais.

Para habilitar bibliografia/índice:

```bash
.venv/bin/python -m marceloclaro.book_studio design /tmp/meu-livro \
  --title "Título" --author "Autor" --bibliography --index
```

Adicione entradas em `references.bib` e `\index{...}` no texto; sem entradas, o
índice vazio pode fazer o `makeindex` falhar. O caminho padrão (sem as flags)
evita esse caso.

## Revisão literária

```bash
# Regras nativas apenas
.venv/bin/python -m marceloclaro.book_studio review manuscrito.txt

# Nativo + LanguageTool local
.venv/bin/python -m marceloclaro.book_studio review manuscrito.txt --languagetool
```

Regras nativas: aspas retas, reticências, travessão, espaço antes de pontuação,
muletas, clichês, repetição próxima, frase/parágrafo longo, advérbios em
`-mente` e aspas desbalanceadas. O relatório traz trecho, posição, severidade,
confiança e sugestões; sempre com `human_review_required=true`.

### Servidor LanguageTool

```bash
~/.local/share/opencode-core/jre/bin/java \
  -cp ~/.local/share/opencode-core/languagetool/languagetool-server.jar \
  org.languagetool.server.HTTPServer --port 8081
```

Teste:

```bash
curl -s -X POST http://127.0.0.1:8081/v2/check \
  --data-urlencode 'language=pt-BR' \
  --data-urlencode 'text=Ele disse "olá"... basicamente, foi -- muito bom , com  duplo espaço.'
```

A primeira requisição carrega as regras de pt-BR e pode demorar ~30 s; as
seguintes levam cerca de 1 s. Sem o servidor, `review` declara
`available=false` e mantém o gate nativo.

## QA e limites

- `qa` usa `pypdf` quando `pdfinfo`/`pdffonts` não existem; verifica páginas,
  trim, metadados, fontes embutidas (inclusive Type0/descendentes) e texto.
- O log TeX é varrido em busca de `Overfull/Underfull \hbox`, referências e
  citações indefinidas, fontes ausentes e erros de `biblatex`.
- QA técnico **não** avalia estética, voz, ritmo, verossimilhança ou adequação
  editorial.
- PDF/UA, PDF/X, TAC e sangria exigem validação externa.
- Nenhum relatório usa "aprovado", "10/10", "publicável" ou "Qualis".

## Testes

```bash
.venv/bin/python -m pytest tests/test_r1111_book_design.py -q
.venv/bin/python -m pytest tests/test_r1071_book_studio.py \
  tests/test_r1078_bookstudio_contracts.py \
  tests/test_r1078_book_studio_landscape.py -q
```

O teste de integração compila um livro de 3 capítulos quando `latexmk` e
`lualatex` existem; caso contrário, é `skip` explícito.

## Evidência desta instalação

- Demo de fumaça: 10 páginas, 160×230 mm, 2 fontes embutidas, QA sem issues.
- Demo via CLI: 6 páginas, 160×230 mm, fontes embutidas, QA sem issues.
- R1111: 15/15 testes; regressão R1071/R1078: 36 passed, 3 skipped.
- LanguageTool 6.6 pt-BR: amostra com 1 erro, 6 avisos e 7 informativos.
