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

## Referências

- [abnTeX2 — Site oficial](https://www.abntex.net.br/)
- [abnTeX2 — CTAN](https://ctan.org/pkg/abntex2)
- [abnt2025 — GitHub](https://github.com/lucas-cirilo/abnt2025-latex)
- `SPEC-916` — Especificação formal desta oferta
