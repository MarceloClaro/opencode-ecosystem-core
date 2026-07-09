# Catálogo de Templates LaTeX — OpenCode Ecosystem Core

> **Orquestrado pelo agente `marceloclaro`**
> SPEC-916 — Atualizado em 2026-07-09 — 50+ templates organizados em 5 categorias

Este diretório contém a oferta completa de templates LaTeX para produção acadêmica, técnica e editorial, integrada ao ecossistema OpenCode.

---

## 📂 Estrutura

```
templates/
├── academic-br/          # Templates acadêmicos brasileiros (ABNT, USP, UnB, etc.)
├── international/         # Templates internacionais (ACM, IEEE, Elsevier, Nature, etc.)
├── books/                # Templates de livros (Victoria Regia, Springer, UnB, etc.)
├── cv/                   # Templates de currículos LaTeX (10 estilos)
└── projects/             # Projetos autorais completos (dissertação, livros, artigos)
```

---

## 🇧🇷 Acadêmicos Brasileiros — `templates/academic-br/`

| Template | .tex | .bib | .cls | .sty | Tamanho | Descrição |
|----------|:----:|:----:|:----:|:----:|:-------:|-----------|
| **abntex2** ↑ | 8 | 2 | 1 | 2 | 320K | abnTeX2 (v1.9.7) — Padrão ABNT oficial (artigo, TCC, livro, relatório, slides) |
| **abnt2025** ↑ | 7 | 0 | 1 | 1 | 24K | ABNT 2025 — Normas atualizadas (NBR 14724:2024, 10520:2023) |
| **unb-monografia** | 12 | 1 | 1 | 0 | 328K | Monografia DCC/CIC — Universidade de Brasília |
| **usp** | 1 | 1 | 0 | 0 | 20K | Modelo USP — Universidade de São Paulo |
| **ipleiria** | 20 | 1 | 1 | 12 | 3.6M | Tese/Dissertação — Instituto Politécnico de Leiria, Portugal |
| **icmc** | 17 | 1 | 1 | 0 | 5.4M | ICMC-USP — Instituto de Ciências Matemáticas e de Computação |
| **dissertacao** | 1 | 1 | 0 | 0 | 20K | Modelo clássico de dissertação ABNT |
| **artigo-qualis-a1** | 1 | 1 | 0 | 0 | 20K | Modelo de artigo para periódico Qualis A1 |
| **ensaio-fichamento** | 3 | 3 | 0 | 0 | 32K | Modelos de ensaio, fichamento e resenha acadêmica |
| **capes** | 1 | 0 | 0 | 0 | 36K | Modelo CAPES — Coordenação de Aperfeiçoamento de Pessoal de Nível Superior |
| **zrm** | 1 | 0 | 0 | 3 | 424K | ZRM — Modelo Zermelo para artigos |

> ↑ `abntex2` e `abnt2025` estão na raiz de `templates/` por compatibilidade, mas fazem parte desta categoria.

---

## 🌍 Internacionais — `templates/international/`

| Template | .tex | .bib | .cls | .sty | Tamanho | Descrição |
|----------|:----:|:----:|:----:|:----:|:-------:|-----------|
| **acm** | 16 | 2 | 2 | 0 | 1.3M | Association for Computing Machinery — artigos e proceedings |
| **elsevier** | 4 | 0 | 1 | 2 | 320K | Elsevier — artigos para periódicos Elsevier |
| **elsevier-cas** | 6 | 1 | 2 | 3 | 1.2M | Elsevier CAS — Organized Elsevier CAS template |
| **ieee** | 2 | 0 | 1 | 0 | 332K | IEEE — artigos, conferências e transactions |
| **mdpi** | 2 | 1 | 1 | 0 | 1.8M | MDPI — Multidisciplinary Digital Publishing Institute |
| **nature** | 3 | 1 | 3 | 0 | 620K | Nature — revista Nature e Nature Portfolio |
| **springer** | 1 | 1 | 1 | 0 | 700K | Springer — SN Journal style |
| **tandf** | 3 | 2 | 1 | 0 | 168K | Taylor & Francis — Interactive APA/Chicago |
| **koma-script** | 98 | 1 | 1 | 0 | 5.8M | KOMA-Script — pacote completo de classes LaTeX alemãs |
| **sbc** | 1 | 1 | 0 | 2 | 204K | SBC — Sociedade Brasileira de Computação |
| **arxiv** | 1 | 0 | 0 | 0 | 24K | arXiv — modelo para preprint |

---

## 📖 Livros — `templates/books/`

| Template | .tex | .cls | .sty | Tamanho | Descrição |
|----------|:----:|:----:|:----:|:-------:|-----------|
| **victoria-regia** | 9 | 0 | 1 | 76K | Victoria Regia — Template clássico de e-book LaTeX |
| **book-simple** | 16 | 0 | 0 | 604K | Template de livro simples (cover, TOC, capítulos, bibliografia) |
| **lathex-dark** | 41 | 0 | 0 | 4.7M | LatHex Dark — Template de livro com tema escuro |
| **springer-volume** | 12 | 1 | 0 | 1.6M | Springer Nature — Template para edited volumes |
| **unb-editora** | 22 | 0 | 0 | 1.3M | Editora UnB — Modelo de livro para Editora Universidade de Brasília |
| **generic-templates** | 45 | 0 | 0 | 500K | Templates genéricos (book, forta, generic, resume) |

---

## 📄 Currículos — `templates/cv/`

| Template | .tex | .cls | Tamanho | Estilos |
|----------|:----:|:----:|:-------:|---------|
| **latexcv** | 23 | 0 | 6.9M | classic, infographics, infographics2 (en/fr), minimalistic, modern, rows, sidebar, sidebarleft, two_column |
| **my-resume** | 1 | 1 | 336K | Modelo de currículo personalizado |

---

## 🏗️ Projetos Autorais — `templates/projects/`

Projetos completos de produção acadêmica e editorial do ecossistema.

| Projeto | .tex | .bib | Tamanho | Descrição |
|---------|:----:|:----:|:-------:|-----------|
| **dissertacao-opencode** | 62 | 0 | 6.5M | Dissertação completa sobre o ecossistema OpenCode (capítulos ABNT) |
| **livro-opencode** | 146 | 1 | 40M | Livro principal do ecossistema OpenCode |
| **livro-volume2** | 79 | 2 | 16M | Segundo volume do livro OpenCode |
| **livro-gemeos-odontologia** | 187 | 2 | 15M | Livro sobre odontologia (gêmeos) |
| **artigo-mit-ia** | 1 | 0 | 63M | Artigo sobre IA — estilo MIT |
| **artigos** | 1 | 1 | 184K | Artigos diversos do ecossistema |
| **criador-artigo** | 2 | 0 | 2.6M | Ferramenta de criação de artigos Qualis A1 |
| **evolucao-artigos** | 5 | 0 | 1.6M | Artigos sobre evolução do ecossistema |
| **dados-entrada-mestrado** | 2 | 0 | 1.8M | Dados de entrada do mestrado (análise taxonômica) |
| **md-dissertacao-latex** | 32 | 1 | 166M | Dissertação em LaTeX (MD) |
| **docs-dissertacao** | 18 | 0 | 364K | Documentos auxiliares de dissertação |
| **documentos** | 1 | 0 | 12M | Documentos diversos |
| **nano** | 4 | 0 | 4.1M | Artigos nano |
| **orchestration** | 1 | 0 | 160K | Modelo de orquestração |

---

## 🚀 Como usar

### Pelo agente `marceloclaro`

Solicite a criação de um documento acadêmico. O agente irá:

1. **Perguntar** o tipo de documento desejado
2. **Apresentar** as opções de template disponíveis por categoria
3. **Copiar** os arquivos para o diretório de trabalho
4. **Orquestrar** a escrita via agentes especializados (academic_writer, ws-scribe, etc.)

### Manualmente

```bash
# Listar templates disponíveis por categoria
ls templates/academic-br/
ls templates/international/
ls templates/books/

# Copiar um template para o diretório de trabalho
cp -r templates/academic-br/unb-monografia ./meu-tcc/
cd meu-tcc && latexmk -pdf main.tex
```

### Via agente `ws-scribe`

O agente `ws-scribe` possui atalhos para templates específicos:
- `🇧🇷` ABNT → `templates/abntex2/` ou `templates/abnt2025/`
- `📖` Livros → `templates/books/`
- `📄` Currículos → `templates/cv/latexcv/`

---

## 🔗 Compatibilidade retroativa

Os seguintes caminhos legados foram mantidos como **symlinks** para a nova estrutura:

| Caminho antigo | → | Caminho novo |
|----------------|---|-------------|
| `publishing/templates/abntex2/` | → | `templates/abntex2/` |
| `publishing/templates/artigo/` | → | `templates/academic-br/artigo-qualis-a1/` |
| `publishing/templates/dissertacao/` | → | `templates/academic-br/dissertacao/` |
| `publishing/templates/livro/book/` | → | `templates/books/book-simple/` |
| `publishing/templates/livro/victoria_regia/` | → | `templates/books/victoria-regia/` |
| `template/Victoria_Regia/` | → | `templates/books/victoria-regia/` |

---

## 📊 Estatísticas

| Categoria | Templates | Arquivos .tex |
|-----------|:---------:|:-------------:|
| Acadêmicos BR | 11 | 72 |
| Internacionais | 11 | 137 |
| Livros | 6 | 145 |
| Currículos | 2 | 24 |
| Projetos | 14 | 541 |
| **Total** | **44** | **~919** |

**Tamanho total:** ~380 MB
**Última atualização:** 2026-07-09

---

## Referências

- [abnTeX2 — Site oficial](https://www.abntex.net.br/)
- [abnTeX2 — CTAN](https://ctan.org/pkg/abntex2)
- [abnt2025 — GitHub](https://github.com/lucas-cirilo/abnt2025-latex)
- [ACM Template](https://www.acm.org/publications/proceedings-template)
- [Elsevier CAS](https://www.elsevier.com/researcher/author/packages/elsevier-cas-template)
- [IEEE Template](https://www.ieee.org/conferences/publishing/templates.html)
- [MDPI Template](https://www.mdpi.com/authors/latex)
- `SPEC-916` — Especificação formal original da oferta de templates
