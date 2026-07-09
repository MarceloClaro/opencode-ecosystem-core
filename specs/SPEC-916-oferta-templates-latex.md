# SPEC-916: Oferta de Templates LaTeX no Ecossistema

**STATUS**: IMPLEMENTADO — EXPANDIDO
**DATA**: 2026-07-08 (v1.0) | 2026-07-09 (v2.0 — expansão completa)
**AUTOR**: marceloclaro
**VERSÃO**: 2.0

## 1. Objetivo

Integrar ao ecossistema OpenCode uma oferta formal e abrangente de templates LaTeX para produção acadêmica, técnica e editorial, orquestrada pelo agente `marceloclaro`.

A oferta foi expandida de 2 famílias (v1.0) para **5 categorias com 44+ templates** (v2.0):

| Categoria | Templates | Arquivos .tex |
|-----------|:---------:|:-------------:|
| 🇧🇷 Acadêmicos Brasileiros | 11 | 72 |
| 🌍 Internacionais | 11 | 137 |
| 📖 Livros | 6 | 145 |
| 📄 Currículos | 2 | 24 |
| 🏗️ Projetos Autorais | 14 | 541 |
| **Total** | **44** | **~919** |

## 2. Critérios de Aceitação (v2.0)

- [x] Templates baixados do Windows e organizados em `templates/`
- [x] Estrutura classificada em 5 categorias semânticas
- [x] Agentes `marceloclaro` e `ws-scribe` atualizados com todas as opções
- [x] Compatibilidade retroativa mantida via symlinks
- [x] README.md com catálogo completo e instruções de uso
- [x] SPEC atualizada para v2.0

## 3. Modelos Disponíveis

### 🇧🇷 Acadêmicos Brasileiros — `templates/academic-br/`

| Template | .tex | Descrição | Caminho |
|----------|:----:|-----------|---------|
| abnTeX2 ↑ | 8 | 8 modelos ABNT (artigo, tese, livro, relatório, projeto, slides) | `templates/abntex2/` |
| abnt2025 ↑ | 7 | 4 modelos ABNT 2024/2025 | `templates/abnt2025/` |
| unb-monografia | 12 | Monografia DCC/CIC-UnB | `templates/academic-br/unb-monografia/` |
| usp | 1 | Modelo USP | `templates/academic-br/usp/` |
| ipleiria | 20 | Tese IPLeiria Portugal | `templates/academic-br/ipleiria/` |
| icmc | 17 | ICMC-USP | `templates/academic-br/icmc/` |
| dissertacao | 1 | Modelo clássico ABNT | `templates/academic-br/dissertacao/` |
| artigo-qualis-a1 | 1 | Artigo Qualis A1 | `templates/academic-br/artigo-qualis-a1/` |
| ensaio-fichamento | 3 | Ensaio, fichamento, resenha | `templates/academic-br/ensaio-fichamento/` |
| capes | 1 | Modelo CAPES | `templates/academic-br/capes/` |
| zrm | 1 | ZRM Zermelo | `templates/academic-br/zrm/` |

> ↑ abnTeX2 e abnt2025 estão na raiz de `templates/` por compatibilidade retroativa.

### 🌍 Internacionais — `templates/international/`

| Template | .tex | Editora/Instituição |
|----------|:----:|---------------------|
| acm | 16 | Association for Computing Machinery |
| elsevier | 4 | Elsevier |
| elsevier-cas | 6 | Elsevier CAS |
| ieee | 2 | IEEE |
| mdpi | 2 | MDPI |
| nature | 3 | Nature Portfolio |
| springer | 1 | Springer Nature |
| tandf | 3 | Taylor & Francis |
| koma-script | 98 | KOMA-Script |
| sbc | 1 | Sociedade Brasileira de Computação |
| arxiv | 1 | arXiv |

### 📖 Livros — `templates/books/`

| Template | .tex | Estilo |
|----------|:----:|--------|
| victoria-regia | 9 | E-book clássico Victoria Regia |
| book-simple | 16 | Livro clássico (capa, TOC, capítulos) |
| lathex-dark | 41 | Dark theme |
| springer-volume | 12 | Springer Nature edited volume |
| unb-editora | 22 | Editora UnB |
| generic-templates | 45 | forta, apehex, resume e outros |

### 📄 Currículos — `templates/cv/`

| Template | .tex | Estilos |
|----------|:----:|---------|
| latexcv | 23 | 10 estilos (classic, infographics, modern, sidebar, rows...) |
| my-resume | 1 | Currículo infográfico |

### 🏗️ Projetos Autorais — `templates/projects/`

| Projeto | .tex | Descrição |
|---------|:----:|-----------|
| dissertacao-opencode | 62 | Dissertação completa do ecossistema |
| livro-opencode | 146 | Livro principal |
| livro-volume2 | 79 | Segundo volume |
| livro-gemeos-odontologia | 187 | Odontologia |
| artigo-mit-ia | 1 | Artigo MIT IA (63MB) |
| artigos | 1 | Artigos diversos |
| criador-artigo | 2 | Ferramenta de criação |
| dados-entrada-mestrado | 2 | Dados de mestrado |
| evolucao-artigos | 5 | Evolução do ecossistema |
| md-dissertacao-latex | 32 | MD dissertação |
| docs-dissertacao | 18 | Documentos auxiliares |
| documentos | 1 | Documentos diversos |
| nano | 4 | Artigos nano |
| orchestration | 1 | Orquestração |

## 4. Arquitetura da Oferta

```
templates/
├── README.md                     # Catálogo completo
├── abntex2/                      # abnTeX2 (legado, 8 modelos)
├── abnt2025/                     # abnt2025 (legado, 4 modelos)
├── academic-br/                  # Acadêmicos brasileiros
│   ├── unb-monografia/
│   ├── usp/
│   ├── ipleiria/
│   ├── icmc/
│   ├── dissertacao/
│   ├── artigo-qualis-a1/
│   ├── ensaio-fichamento/
│   ├── capes/
│   └── zrm/
├── international/                # Internacionais
│   ├── acm/
│   ├── elsevier/
│   ├── elsevier-cas/
│   ├── ieee/
│   ├── mdpi/
│   ├── nature/
│   ├── springer/
│   ├── tandf/
│   ├── koma-script/
│   ├── sbc/
│   └── arxiv/
├── books/                        # Livros
│   ├── victoria-regia/
│   ├── book-simple/
│   ├── lathex-dark/
│   ├── springer-volume/
│   ├── unb-editora/
│   └── generic-templates/
├── cv/                           # Currículos
│   ├── latexcv/
│   └── my-resume/
└── projects/                     # Projetos autorais
    ├── dissertacao-opencode/
    ├── livro-opencode/
    ├── livro-volume2/
    ├── livro-gemeos-odontologia/
    ├── artigo-mit-ia/
    ├── artigos/
    ├── criador-artigo/
    ├── dados-entrada-mestrado/
    ├── evolucao-artigos/
    ├── md-dissertacao-latex/
    ├── docs-dissertacao/
    ├── documentos/
    ├── nano/
    └── orchestration/
```

## 5. Compatibilidade Retroativa

Os seguintes caminhos antigos foram preservados como **symlinks** para a nova estrutura:

| Caminho antigo | → | Caminho novo |
|----------------|---|-------------|
| `publishing/templates/abntex2/` | → | `templates/abntex2/` |
| `publishing/templates/artigo/` | → | `templates/academic-br/artigo-qualis-a1/` |
| `publishing/templates/dissertacao/` | → | `templates/academic-br/dissertacao/` |
| `publishing/templates/livro/book/` | → | `templates/books/book-simple/` |
| `publishing/templates/livro/victoria_regia/` | → | `templates/books/victoria-regia/` |
| `template/Victoria_Regia/` | → | `templates/books/victoria-regia/` |

## 6. Integração com a Orquestração

O agente `marceloclaro` é o ponto de entrada. Quando um usuário solicitar a criação de um documento:

1. Pergunta ao usuário a categoria e o template desejado
2. Copia os arquivos do template para o diretório de trabalho
3. Delega a escrita para agentes especializados (academic_writer, ws-scribe, etc.)

Os agentes `marceloclaro` e `ws-scribe` foram atualizados para refletir a oferta completa de templates.

## 7. Instalação

```bash
# abnTeX2 (necessita TeX Live):
sudo apt install texlive-latex-extra texlive-publishers texlive-lang-portuguese

# abnt2025 e demais templates: já completos (cls + sty + config inclusos)
```

## 8. Origem dos Templates

Os templates foram extraídos do diretório Windows:
`C:\Users\marce\Downloads\OpenCode_Ecosystem-main\OpenCode_Ecosystem-main`

E organizados na estrutura padronizada do ecossistema em `/home/marceloclaro/opencode-ecosystem-core/templates/`.

## 9. Referências

- [abnTeX2 — Site oficial](https://www.abntex.net.br/)
- [abnTeX2 — CTAN](https://ctan.org/pkg/abntex2)
- [abnt2025 — GitHub](https://github.com/lucas-cirilo/abnt2025-latex)
- [ACM Template](https://www.acm.org/publications/proceedings-template)
- [IEEE Template](https://www.ieee.org/conferences/publishing/templates.html)
- [MDPI Template](https://www.mdpi.com/authors/latex)
- `SPEC-916` → esta especificação (v2.0)
