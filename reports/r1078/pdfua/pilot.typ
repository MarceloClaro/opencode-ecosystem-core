#set document(title: "Piloto PDF/UA — Book Studio", author: "OpenCode Core")
#set page(width: 6in, height: 9in, margin: 0.75in)
#set text(font: "Liberation Serif", size: 11pt, lang: "pt", fill: rgb("#2B2117"))
#set par(justify: true, leading: 0.65em)
#set heading(numbering: none)

= Piloto de acessibilidade

Este documento testa estrutura tagged, #link("https://example.org")[link externo], tabela com cabeçalho e nota de rodapé.#footnote[Nota de rodapé: a acessibilidade exige estrutura, não apenas texto extraível.]

== Tabela de contraste

#figure(
  table(
    columns: 3,
    align: left,
    stroke: 0.5pt + rgb("#2B2117"),
    [*Cor*], [*Hexadecimal*], [*Contraste*],
    [Memória], [\#8A3B1F], [6,32:1],
    [Documento], [\#1F5C57], [6,31:1],
    [Cuidado], [\#FF4D4D], [6,42:1 sobre preto],
  ),
  caption: [Contraste da paleta sobre papel sépia],
)

== Figura com texto alternativo

#figure(
  image("pilot.png", width: 100%, alt: "Retângulo sépia com moldura cobre e a palavra CUIDADO em vermelho sobre fundo preto."),
  caption: [Figura 1 — teste de texto alternativo e legenda.],
)
