# Oferta de Templates LaTeX — OpenCode Ecosystem Core

> **Parte da orquestração do agente `marceloclaro`**
> SPEC-916 — Integrado ao ecossistema em 2026-07-08

Este diretório contém a oferta formal de templates LaTeX para produção acadêmica brasileira, orquestrada pelo agente central do ecossistema.

## Como usar

Quando você solicitar a criação de um documento acadêmico ao agente `marceloclaro`, ele:

1. **Perguntará** o tipo de documento (artigo, tese, relatório, etc.)
2. **Apresentará** as duas opções de template ABNT disponíveis
3. **Copiará** os arquivos para o diretório de trabalho
4. **Orquestrará** a escrita via agentes especializados

## Templates disponíveis

### abnTeX2 (v1.9.7, 2018) — `templates/abntex2/`

| Modelo | Arquivo | Norma |
|---|---|---|
| Artigo científico | `abntex2-modelo-artigo.tex` | NBR 6022 |
| Trabalho acadêmico | `abntex2-modelo-trabalho-academico.tex` | NBR 14724 |
| Livro | `abntex2-modelo-livro.tex` | NBR 6029 |
| Relatório técnico | `abntex2-modelo-relatorio-tecnico.tex` | NBR 10719 |
| Projeto de pesquisa | `abntex2-modelo-projeto-pesquisa.tex` | NBR 15287 |
| Glossários | `abntex2-modelo-glossarios.tex` | — |
| Slides (Beamer) | `abntex2-modelo-slides.tex` | — |
| Include comandos | `abntex2-modelo-include-comandos.tex` | — |

**Instalação necessária:** `sudo apt install texlive-latex-extra texlive-publishers texlive-lang-portuguese`

### abnt2025 (2025) — `templates/abnt2025/`

| Modelo | Arquivo | Norma |
|---|---|---|
| Artigo acadêmico | `exemplos/artigo_academico.tex` | NBR 6022, 10520:2023 |
| Monografia (TCC/dissertação/tese) | `exemplos/monografia.tex` | NBR 14724:2024 |
| Projeto IC | `exemplos/projeto_ic.tex` | NBR 15287 |
| Relatório técnico | `exemplos/relatorio_tecnico.tex` | NBR 10719 |

**Instalação:** Já completo (cls + sty + config inclusos)

## Comparação rápida

| Característica | abnTeX2 | abnt2025 |
|---|---|---|
| Versão | 2018 | 2025 |
| Modelos | 8 | 4 |
| Normas recentes | Até 2018 | NBR 14724:2024, 10520:2023 |
| Instalação | TeX Live | Já incluso |
| Base | memoir | Própria |
| Comunidade | Grande | Emergente |

## Banco de opções por gênero (Book Editor)

O catálogo [`templates/books/catalogo-generos.json`](books/catalogo-generos.json)
registra classes, pacotes e templates por gênero editorial. Ele é um artefato
de dados: **listar não é instalar, instalar não é compilar e compilar não é
aprovar**.

| Gênero | Destaques | Observação |
|---|---|---|
| Bíblicos | `scripture`, `bibletext`, `bibleref` | Citação e passagem; Bíblia completa exige classe de livro + texto licenciado. |
| Romances e ficção | `novel`, `ElegantBook` | `novel` é focado em print-on-demand, mas não é mais mantido. |
| Infantis | `photobook`, `book-two`, `medievalMurderMistery` | Livro ilustrado/álbum; não há classe infantil dedicada madura no CTAN. |
| Científicos | `kaobook`, `nature-tex`, `elsarticle`, `RevTeX` | Separa livro, relatório e artigo de periódico. |
| Artísticos | `pagelayout`, `bookcover`, `VividBook` | Página, capa e estética ilustrada; não é curadoria de arte. |
| Matemáticos | `amsbook`, `Tufte-LaTeX` | Classe AMS e margens para teoremas, provas e figuras. |
| Históricos | `memoir`, `biblatex-chicago`, `chronology` | Miolo, citação Chicago e linha do tempo. |
| RPG | `rpgtex`, `DND-5e-LaTeX-Template` | Caixas, tabelas, statblocks e temas. |
| Mangá | `laboticgate`, `jlreq`, `pxrubrica`, `gentombow` | Tipografia japonesa, B5 com sangria e furigana; não desenha painéis. |
| HQs | `comictex`, `GraphicNovel`, `hqfamiliar` | Roteiro e estrutura de quadrinhos; não desenha arte final. |
| Livros didáticos | `livro-aberto`, `tex-book-template` | Referência brasileira e estrutura genérica. |
| Livros-jogo | `gamebook`, `gamebooklib` | Seções numeradas e escolhas. |

**Política de licença:** itens `reference_only: true` não têm licença
explícita, são GPL/AGPL ou têm licença incerta; eles não são vendorizados e
não têm instalação automática. Os demais registram `tlmgr install ...` ou
`git clone ...` apenas como instrução declarativa.

**Verificação:** o campo `verified.compile_tested` distingue o que foi
compilado nesta máquina do que foi apenas documentado. Antes de oferecer uma
opção no Book Editor, rode o smoke test no ambiente de destino.

- `SPEC-1072` — Especificação formal deste banco de opções.

## Referências

- [abnTeX2 — Site oficial](https://www.abntex.net.br/)
- [abnTeX2 — CTAN](https://ctan.org/pkg/abntex2)
- [abnt2025 — GitHub](https://github.com/lucas-cirilo/abnt2025-latex)
- `SPEC-916` — Especificação formal desta oferta
