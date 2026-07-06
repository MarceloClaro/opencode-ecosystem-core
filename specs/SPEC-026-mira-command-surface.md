# SPEC-026 — Superfície de Comandos MIRA no Catálogo

```yaml
spec_id: SPEC-026
title: Port do command surface MIRA para agents/catalog
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-018, SPEC-023]
origin: Livro/guia MIRA em INSPIRAÇÕES/mira.md
```

## 1. Objetivo

Completar a superfície de comandos/agentes do MIRA no `agents/catalog/`, portando os comandos descritos no material de inspiração para artefatos reais do Core.

## 2. Requisitos

| ID | Requisito | Critério de aceitação |
|---|---|---|
| REQ-026.1 | O catálogo DEVE expor `mira-new` e `mira-references` | arquivos existem e são carregados pelo `catalog_loader` |
| REQ-026.2 | O catálogo DEVE expor os agentes centrais de animação e metáfora | `mira-animator`, `mira-animated-metaphor`, `mira-size-animator` |
| REQ-026.3 | O catálogo DEVE expor os agentes de pipeline | `mira-extract`, `mira-planner`, `mira-copywriter`, `mira-builder`, `mira-validator` |
| REQ-026.4 | O catálogo DEVE expor os agentes visuais/dados | `mira-visuals`, `mira-chart`, `mira-chart-race`, `mira-qrcode`, `mira-3d`, `mira-image-template` |
| REQ-026.5 | O catálogo DEVE expor os agentes de mídia e interatividade | `mira-image`, `mira-get-videos`, `mira-survey` |
| REQ-026.6 | O catálogo DEVE expor os agentes responsivos | `mira-squared`, `mira-vertical`, `mira-thirds` |
| REQ-026.7 | Todos os agentes MIRA DEVEM possuir frontmatter válido e descrição não vazia | `load_catalog_definitions()` encontra todos |
| REQ-026.8 | A auditoria de inspirações DEVE classificar `mira_presentation_system` como `implemented` | teste de auditoria verde |

## 3. Invariantes

- INV-026.1: Cada arquivo MIRA no catálogo usa `mode: subagent`.
- INV-026.2: Cada arquivo possui `name:` compatível com o nome do arquivo.
- INV-026.3: Os agentes MIRA são descritos como superfícies do ecossistema, não como executáveis mágicos autônomos.

## 4. Critérios de Aceitação

- [x] `tests/test_mira_catalog.py` passa
- [x] `tests/test_inspiration_audit.py` passa com `mira_presentation_system == implemented`
- [x] `load_catalog_definitions()` contém todos os agentes MIRA esperados

## 5. TDD

- RED: criar teste de catálogo MIRA + atualizar auditoria
- GREEN: adicionar arquivos em `agents/catalog/`
- REFACTOR: uniformizar descrições e categorias sem quebrar a carga do catálogo
