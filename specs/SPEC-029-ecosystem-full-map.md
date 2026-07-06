# SPEC-029 — Mapa Completo do Ecossistema (Nós + Vetores)

```yaml
spec_id: SPEC-029
title: Geração de mapa completo e minucioso do ecossistema em JSON + Markdown
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-005, SPEC-023, SPEC-028]
origin: pedido do usuário para criar um mapa completo e minucioso com todos os vetores e nós
```

## 1. Objetivo

Gerar um mapa auditável do ecossistema contendo:

- todos os nós relevantes do Core (módulos, specs, schemas, testes, agentes do catálogo, docs)
- todos os vetores relevantes (containment, imports, documentação, dependência de specs e fluxo arquitetural)
- artefatos persistidos em **JSON** e **Markdown**

## 2. Requisitos

| ID | Requisito | Critério de aceitação |
|---|---|---|
| REQ-029.1 | O sistema DEVE gerar um inventário completo de nós | `build_ecosystem_map()` retorna `nodes[]` não vazio |
| REQ-029.2 | O sistema DEVE gerar vetores entre nós | `build_ecosystem_map()` retorna `vectors[]` não vazio |
| REQ-029.3 | O mapa DEVE incluir agentes do catálogo, specs, schemas e testes | nós desses tipos presentes |
| REQ-029.4 | O mapa DEVE ser persistido em JSON | `maps/ecosystem_map_2026-07-06.json` existe |
| REQ-029.5 | O mapa DEVE ser persistido em Markdown | `MAPA_ECOSSISTEMA_COMPLETO_2026-07-06.md` existe |
| REQ-029.6 | O artefato Markdown DEVE resumir contagens e taxonomia de vetores | headings e métricas presentes |

## 3. Invariantes

- INV-029.1: Todo nó possui `id`, `label`, `kind` e `path` ou `logical_group`.
- INV-029.2: Todo vetor possui `source`, `target` e `kind`.
- INV-029.3: Os artefatos são determinísticos para a mesma árvore de arquivos.

## 4. Critérios de Aceitação

- [ ] `tests/test_ecosystem_full_map.py` passa
- [ ] JSON e Markdown do mapa existem no repositório

## 5. TDD

- RED: criar testes para contagem, nós-chave, vetores-chave e artefatos
- GREEN: implementar gerador e persistir artefatos
- REFACTOR: enriquecer metadados sem quebrar o formato
