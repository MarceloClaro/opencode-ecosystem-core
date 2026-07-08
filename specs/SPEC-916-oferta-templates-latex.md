# SPEC-916: Oferta de Templates LaTeX no Ecossistema

**STATUS**: IMPLEMENTADO
**DATA**: 2026-07-08
**AUTOR**: marceloclaro
**VERSÃO**: 1.0

## 1. Objetivo

Integrar ao ecossistema OpenCode uma oferta formal de templates LaTeX para produção acadêmica, orquestrada pelo agente `marceloclaro`. A oferta cobre duas famílias de templates brasileiros:

- **abnTeX2** (v1.9.7, 2018) — padrão ABNT consolidado no Brasil
- **abnt2025** (2025) — normas ABNT atualizadas (NBR 14724:2024, NBR 10520:2023)

## 2. Critérios de Aceitação

- [x] Templates baixados e armazenados em `templates/abntex2/` e `templates/abnt2025/`
- [x] Modelos canônicos disponíveis para: artigo, monografia/tese, relatório técnico, projeto de pesquisa, livro, slides
- [x] Agente `marceloclaro` atualizado para consultar usuário sobre qual template usar
- [x] SPEC registrada como oferta formal do ecossistema

## 3. Modelos Disponíveis por Pacote

### abnTeX2 (8 modelos)

| Modelo | Arquivo | Norma ABNT |
|---|---|---|
| Artigo científico | `abntex2-modelo-artigo.tex` | NBR 6022:2003 |
| Trabalho acadêmico (tese/dissertação) | `abntex2-modelo-trabalho-academico.tex` | NBR 14724:2011 |
| Livro | `abntex2-modelo-livro.tex` | NBR 6029:2006 |
| Relatório técnico/científico | `abntex2-modelo-relatorio-tecnico.tex` | NBR 10719:2015 |
| Projeto de pesquisa | `abntex2-modelo-projeto-pesquisa.tex` | NBR 15287:2011 |
| Glossários | `abntex2-modelo-glossarios.tex` | — |
| Slides (Beamer) | `abntex2-modelo-slides.tex` | — |
| Include comandos | `abntex2-modelo-include-comandos.tex` | — |

### abnt2025 (4 modelos)

| Modelo | Arquivo | Norma ABNT |
|---|---|---|
| Artigo acadêmico | `artigo_academico.tex` | NBR 6022, 10520:2023 |
| Monografia (TCC/dissertação/tese) | `monografia.tex` | NBR 14724:2024 |
| Projeto de Iniciação Científica | `projeto_ic.tex` | NBR 15287 |
| Relatório técnico | `relatorio_tecnico.tex` | NBR 10719 |

## 4. Arquitetura da Oferta

```
templates/
├── abntex2/          # abnTeX2 — 8 modelos (2018)
│   ├── abntex2.cls
│   ├── abntex2-modelo-artigo.tex
│   ├── abntex2-modelo-trabalho-academico.tex
│   ├── abntex2-modelo-livro.tex
│   ├── abntex2-modelo-relatorio-tecnico.tex
│   ├── abntex2-modelo-projeto-pesquisa.tex
│   ├── abntex2-modelo-glossarios.tex
│   ├── abntex2-modelo-slides.tex
│   └── abntex2-modelo-include-comandos.tex
│
├── abnt2025/         # abnt2025 — 4 modelos (2025)
│   ├── abnt2025.cls
│   ├── abnt2025.sty
│   ├── config/
│   │   ├── margens.tex
│   │   ├── fontes.tex
│   │   └── cores.tex
│   └── exemplos/
│       ├── artigo_academico.tex
│       ├── monografia.tex
│       ├── projeto_ic.tex
│       └── relatorio_tecnico.tex
│
└── README.md         # Guia de uso da oferta
```

## 5. Integração com a Orquestração

O agente `marceloclaro` (catalogado em `agents/catalog/marceloclaro.md`) é o ponto de entrada. Quando um usuário solicitar a criação de um documento acadêmico, o orquestrador:

1. Consulta o usuário sobre o tipo de documento (artigo, tese, relatório, etc.)
2. Apresenta as duas opções de template (abnTeX2 ou abnt2025)
3. Cria o diretório de trabalho e copia os arquivos necessários
4. Delega a escrita para os agentes apropriados do pipeline MASWOS

## 6. Instalação

Os templates estão disponíveis localmente em `templates/`. Para usar:

```bash
# abnTeX2 precisa ser instalado no TeX Live:
sudo apt install texlive-latex-extra texlive-publishers texlive-lang-portuguese

# abnt2025 já está completo no diretório (cls + sty + config)
```

## 7. Referências

- [abnTeX2 — Site oficial](https://www.abntex.net.br/)
- [abnTeX2 — CTAN](https://ctan.org/pkg/abntex2)
- [abnt2025 — GitHub](https://github.com/lucas-cirilo/abnt2025-latex)
- `SPEC-916` → esta especificação
