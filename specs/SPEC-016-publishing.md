# SPEC-016 — Pipeline de Produção Científica (Pasta Única)

```yaml
spec_id: SPEC-016
title: Templates LaTeX e Pasta Única de Produção Científica
status: implemented
component: publishing/
source: OpenCode_Ecosystem/templates (portado)
```

## Objetivo

Padronizar toda produção acadêmica (artigo Qualis A1, dissertação ABNT,
trabalho abnTeX2, livro/e-book) em uma **pasta única autocontida** com fonte
LaTeX (a partir dos templates oficiais), fonte Markdown canônica e compilados
em **PDF, DOCX, MD e ODT** (extensão aceita no Amazon KDP), acompanhados de
manifesto auditável com checksums SHA-256.

## Estrutura canônica da pasta

```
producao_cientifica/<slug>-<timestamp>/
├── latex/               # fonte LaTeX (template + main.tex)
├── manuscrito.md        # fonte canônica
├── manuscrito.pdf       # compilado PDF
├── manuscrito.docx      # compilado Word
├── manuscrito.odt       # compilado OpenDocument (Amazon KDP)
└── MANIFEST.json        # metadados + checksums SHA-256
```

## Templates disponíveis

| Nome | Arquivo principal | Uso |
|------|-------------------|-----|
| `artigo` | `artigo_modelo_qualis_a1.tex` | Artigos Qualis A1 (ABNT) |
| `dissertacao` | `dissertacao_modelo_abnt.tex` | Dissertações e teses ABNT |
| `abntex2` | `abntex2-modelo-trabalho-academico.tex` | Trabalhos acadêmicos abnTeX2 |
| `livro` | `victoria_regia/` | E-books clássicos (KDP-ready) |
| `livro-book` | `book/` | Livros genéricos LaTeX |

## Requisitos

| ID | Requisito | Critério de aceitação |
|----|-----------|----------------------|
| R-016.1 | Pasta única | `build()` cria pasta com `latex/`, `manuscrito.md` e `MANIFEST.json` |
| R-016.2 | Quatro formatos | Com pandoc disponível, gera PDF, DOCX, MD e ODT |
| R-016.3 | KDP-ready | `manifest["kdp_ready"] is True` quando ODT foi gerado |
| R-016.4 | Auditabilidade | Cada formato gerado tem `sha256` e `bytes` no manifesto |
| R-016.5 | Degradação graciosa | Sem pandoc/latex, o build não falha: registra ausências no log do manifesto |
| R-016.6 | Templates íntegros | `list_templates()` aponta para arquivos/pastas existentes |
| R-016.7 | Integração orquestrador | `orch.produce_scientific_work()` retorna manifesto e registra reflexão |

## Invariantes

- INV-016.1: A fonte Markdown é canônica — todos os compilados derivam dela
  (ou do main.tex gerado a partir dela).
- INV-016.2: Nenhum build sobrescreve pasta anterior (slug com timestamp).
- INV-016.3: O manifesto lista TODOS os formatos, inclusive os não gerados (null).
