# SPEC-900 — Livro "Tritemo: O Elixir e o Tempo"

```yaml
spec_id: SPEC-900
title: Livro Tritemo com Ilustrações MIRA
status: ACTIVE
version: 1.0.0
author: Marcelo Dias de Carvalho Filho
adapted_by: MarceloClaro OpenCode Ecosystem
template: livro
depends_on: [SPEC-018, SPEC-019, SPEC-026]
```

## 1. Objetivo

Produzir um livro ilustrado completo (PDF + DOCX + ODT) a partir do conto **"Tritemo"** de Marcelo Dias de Carvalho Filho, utilizando o **template Victoria Regia** para formatação de livro e o **MIRA Engine** para geração de ilustrações metafóricas animadas por capítulo.

## 2. Estrutura do Livro

| Capítulo | Título | Palavras-chave MIRA |
|---|---|---|
| 1 | O Alquimista Moderno | alquimia, ciência, descoberta |
| 2 | O Elixir da Vida | elixir, transmutação, experimento |
| 3 | O Despertar em Camelot | despertar, magia, reino |
| 4 | Merlin e os Druidas | orquestração, coordenação, sabedoria |
| 5 | Jéssica | encontro, amor, contexto |
| 6 | A Invasão Saxã | batalha, conflito, invasão |
| 7 | O Resgate Heróico | resgate, coragem, pipeline |
| 8 | O Adeus e o Retorno | despedida, dívida, retorno |

## 3. Requisitos

| ID | Requisito |
|---|---|
| REQ-900.1 | O conteúdo do livro DEVE ser o texto integral do conto "Tritemo" de Marcelo Dias de Carvalho Filho |
| REQ-900.2 | O livro DEVE ser dividido em 8 capítulos com títulos temáticos |
| REQ-900.3 | Cada capítulo DEVE ter uma ilustração MIRA (card HTML animado) |
| REQ-900.4 | A capa DEVE usar o template Victoria Regia com paleta de ficção |
| REQ-900.5 | O livro DEVE ser compilado em PDF, DOCX e ODT |
| REQ-900.6 | Metadados do livro (título, autor, subtítulo) DEVEM constar no MANIFEST |

## 4. Personagens Principais

- **Lucas Tritemo** — Estudante de Química, alquimista moderno
- **Merlin** — Mago druida, senhor de Avalon
- **Jéssica** — Bisneta de Merlin, interesse amoroso de Lucas
- **Cavaleiros de Camelot** — Nobres guerreiros do reino
- **Saxões** — Invasores do reino de Camelot

## 5. Critérios de Aceitação

1. [ ] O texto integral do conto está presente no livro
2. [ ] O livro está dividido em 8 capítulos claramente nomeados
3. [ ] Cada capítulo possui um card MIRA animado correspondente
4. [ ] A capa segue o design do template Victoria Regia
5. [ ] O PDF é gerado sem erros de compilação
6. [ ] O DOCX é gerado via pandoc
7. [ ] O MANIFEST.json contém todos os metadados e checksums
8. [ ] O livro pode ser publicado no Amazon KDP (formato ODT)
