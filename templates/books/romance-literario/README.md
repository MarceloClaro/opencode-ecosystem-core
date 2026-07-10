# Romance Literário

Template LaTeX para romance, novela ou narrativa longa de ficção — sem
aparato acadêmico (sem abstract, sem numeração de seção, sem bibliografia
obrigatória).

## Estrutura

```
romance-literario/
├── main.tex                    # documento principal (edite os metadados no topo)
├── misc/opcoes.sty             # estilo tipográfico (dropcap, quebra de cena, cabeçalhos)
├── frontmatter/
│   ├── folhaderosto.tex        # página de título
│   ├── dedicatoria.tex         # dedicatória
│   └── epigrafe.tex            # epígrafe de abertura
├── content/
│   ├── capitulo01.tex          # capítulo de exemplo (dropcap + quebra de cena)
│   └── capitulo02.tex
└── backmatter/
    ├── sobre-o-autor.tex
    └── colofao.tex             # página de créditos/ISBN
```

## Como usar

1. Copie a pasta inteira para o seu diretório de trabalho.
2. Edite os metadados no topo de `main.tex` (`\autornome`, `\titulolivro`, etc.).
3. Escreva cada capítulo em `content/capituloNN.tex` e inclua-o em `main.tex`
   com `\input{content/capituloNN}`.
4. Use `\letracapitular{Primeira letra}{resto da palavra}` na primeira
   palavra de cada capítulo e `\cenaseguinte` para marcar uma quebra de cena.
5. Compile com `latexmk -pdf main.tex` (ou `pdflatex` em 2 passagens para
   o sumário).

Formato de página: 5.5in × 8.5in (trade paperback, compatível com Amazon KDP).
