# SPEC-019 — Automated Cover Designer

```yaml
spec_id: SPEC-019
title: Automated Cover Designer + Internal Illustrator (Paleta, Tipografia e Prompts)
status: ACTIVE
version: 1.1.0
depends_on: [SPEC-016]
modules:
  - publishing/cover_designer.py
```

## 1. Requisitos

| ID | Requisito |
|---|---|
| REQ-019.1 | O `CoverDesigner` DEVE analisar o título e o conteúdo do livro para classificar o estilo em uma de 4 categorias: `tecnologia`, `academico`, `ficcao` ou `didatico`. |
| REQ-019.2 | O sistema DEVE gerar um arquivo `DESIGN_STUDY.md` contendo a paleta de cores (psicologia das cores), tipografia e prompts de ilustração para Midjourney/DALL-E/MIRA. |
| REQ-019.3 | O sistema DEVE gerar os arquivos `capa.tex` e `contracapa.tex` aplicando as cores da paleta (fundo e texto) e reservando espaço para as ilustrações geradas. |
| REQ-019.4 | O pipeline `ScientificProduction` DEVE acionar o `CoverDesigner` automaticamente sempre que o template escolhido começar com `livro` (ex: `livro`, `livro-book`). |
| REQ-019.5 | O `CoverDesigner.illustrate_internals()` DEVE analisar os parágrafos do manuscrito e injetar blocos de prompt de ilustração didática após parágrafos complexos (>150 caracteres), no estilo vibrante/didático ('jovem gênio'). |
| REQ-019.6 | Os prompts internos DEVEM usar a mesma paleta de cores da capa, garantindo consistência visual em toda a obra, e proporção `--ar 16:9`. |
| REQ-019.7 | Quando houver prompts internos injetados, o pipeline DEVE gravar `manuscrito_ilustrado.md` na pasta única e registrar `internal_prompts` no manifesto (`cover_design`). |

## 2. Invariantes (contratos)

| ID | Invariante |
|---|---|
| INV-019.1 | A paleta de cores DEVE conter 5 cores hexadecimais: `primary`, `secondary`, `accent`, `bg` e `text`. |
| INV-019.2 | O prompt de ilustração da capa DEVE incluir a paleta de cores exata e a proporção `--ar 2:3`. |
| INV-019.3 | O arquivo `capa.tex` DEVE usar o comando `\pagecolor` com a cor primária ou de fundo da paleta. |
| INV-019.4 | `illustrate_internals()` NÃO DEVE alterar o texto original dos parágrafos — apenas injetar blocos de citação (blockquote) adicionais. |
| INV-019.5 | Cabeçalhos, listas, blocos de código e blockquotes NÃO DEVEM receber prompts de ilustração. |

## 3. Critérios de aceitação

1. `CoverDesigner.design_cover("Manual de Python", "Autor", "código e algoritmos")` retorna estilo `tecnologia`.
2. `CoverDesigner.design_cover("Tese de Doutorado", "Autor", "pesquisa e teorema")` retorna estilo `academico`.
3. O arquivo `DESIGN_STUDY.md` gerado contém a string `--ar 2:3` e os códigos hexadecimais da paleta.
4. O manifesto gerado por `ScientificProduction(template="livro").build()` contém a chave `cover_design` não nula.
5. `illustrate_internals(md, "didatico")` injeta pelo menos 1 bloco `[ILUSTRAÇÃO DIDÁTICA SUGERIDA]` em um manuscrito com parágrafos longos.
6. O manuscrito ilustrado preserva 100% das linhas originais do manuscrito fonte.
7. Para um livro com parágrafos complexos, a pasta única contém `manuscrito_ilustrado.md` e o manifesto registra `internal_prompts >= 1`.
