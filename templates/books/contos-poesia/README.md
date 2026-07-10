# Contos & Poesia

Template LaTeX para coletânea de contos e/ou poemas — cada texto é
autocontido (sem dependência narrativa entre capítulos), organizado em
partes ("Contos" e "Poemas").

## Estrutura

```
contos-poesia/
├── main.tex                     # documento principal (edite os metadados no topo)
├── misc/opcoes.sty              # estilo tipográfico (sem numeração "Capítulo N")
├── frontmatter/
│   ├── folhaderosto.tex         # página de título
│   └── apresentacao.tex         # apresentação da coletânea
├── content/
│   ├── conto-01.tex             # conto de exemplo (dropcap)
│   └── poema-01.tex             # poema de exemplo (ambiente poema)
└── backmatter/
    └── sobre-o-autor.tex
```

## Como usar

1. Copie a pasta inteira para o seu diretório de trabalho.
2. Edite os metadados no topo de `main.tex` (`\autornome`, `\titulolivro`, etc.).
3. Cada conto/poema vira um `\chapter{Título}` em seu próprio arquivo
   `content/conto-NN.tex` ou `content/poema-NN.tex`, incluído em `main.tex`.
4. Use `\letracapitular{Primeira letra}{resto da palavra}` na primeira
   palavra de um conto; use o ambiente `poema` para poemas.
5. Compile com `latexmk -pdf main.tex` (ou `pdflatex` em 2 passagens para
   o sumário).

Formato de página: 5.5in × 8.5in (trade paperback, compatível com Amazon KDP).
