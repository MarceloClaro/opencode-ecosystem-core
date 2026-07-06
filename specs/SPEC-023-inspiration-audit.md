# SPEC-023 — Auditoria de Inspirações do Ecossistema

```yaml
spec_id: SPEC-023
title: Auditoria Determinística de Inspirações → Implementações
version: 1.2.0
status: active
owner: marceloclaro
depends_on: [SPEC-005, SPEC-021, SPEC-022, SPEC-024]
origin: Diretório INSPIRAÇÕES + pedido de validação integral do usuário
```

## 1. Objetivo

Fornecer uma auditoria **reprodutível, evidenciável e não subjetiva** que compare os artefatos de `INSPIRAÇÕES/` com a codebase real do `opencode-ecosystem-core`, classificando cada inspiração como:

- `implemented`
- `partial`
- `absent`

A auditoria deve servir como base de governança SDD/TDD para responder, com evidências, se uma inspiração já foi portada para o Core.

## 2. Escopo

### 2.1 Dentro do escopo

- Catálogo canônico de inspirações auditáveis.
- Deduplicação de artefatos auxiliares (`:Zone.Identifier`, cópias redundantes).
- Classificação baseada em evidências de arquivos reais do repositório.
- Relatório estruturado e renderização Markdown.
- Integração com o orquestrador via `audit_inspirations()`.

### 2.2 Fora do escopo

- Interpretar PDFs/livros completos como OCR semântico.
- Julgar qualidade funcional profunda de cada módulo além da presença auditável.
- Autoimplementação de inspirações ausentes sem nova spec específica.

## 3. Requisitos

| ID | Requisito | Critério de aceitação |
|---|---|---|
| REQ-023.1 | O sistema DEVE manter um catálogo canônico de inspirações auditáveis | `audit_inspirations()` retorna itens estáveis com `item_id` único |
| REQ-023.2 | A auditoria DEVE ignorar arquivos auxiliares não implementacionais (`:Zone.Identifier`) | nenhum item usa `Zone.Identifier` como evidência |
| REQ-023.3 | Cada item auditado DEVE listar `source_files`, `mandatory_paths`, `evidence_paths` e `missing_paths` | relatório contém esses campos |
| REQ-023.4 | O status `implemented` SÓ PODE ser atribuído quando 100% dos caminhos mandatórios existirem | teste de item implementado passa apenas com cobertura mandatória total |
| REQ-023.5 | O status `partial` DEVE indicar cobertura incompleta, porém com evidência real de port | itens parciais têm `evidence_paths` não vazios e `missing_paths` não vazios |
| REQ-023.6 | O status `absent` DEVE indicar ausência de implementação correspondente no Core | item ausente tem `evidence_paths` vazios para os caminhos mandatórios |
| REQ-023.7 | O orquestrador DEVE expor `audit_inspirations()` e registrar reflexão no MetaBus | memória episódica cresce após auditoria |
| REQ-023.8 | A auditoria DEVE gerar relatório Markdown consumível por humanos | `render_inspiration_audit_markdown()` retorna tabela/resumo |

## 4. Catálogo Canônico Validado

| item_id | inspiração | status validado atual |
|---|---|---|
| `superhuman_scientific_core` | Blueprint de `INSPIRAÇÃO 1.txt` para núcleo científico superhuman-like | `implemented` |
| `scientific_governance_pipeline_architecture` | SDD do pipeline OQS→MCI→VSEE→EGS | `implemented` |
| `scientific_governance_tdd_plan` | Plano TDD detalhado do pipeline científico | `implemented` |
| `research_run_batch` | `research_pipelines_run_research_batch.py` | `implemented` |
| `research_analyze_batch` | `research_pipelines_analyze_research_batch.py` | `implemented` |
| `research_final_report_template` | `research_results_reports_final_report_template.md` | `implemented` |
| `research_scenario_matrix` | `research_experiments_scenario_matrix_v1.json` | `implemented` |
| `mira_presentation_system` | Livro/engine MIRA e superfície de comandos | `implemented` |

## 5. Invariantes

- INV-023.1: O relatório usa caminhos relativos ao repositório, nunca absolutos na saída final.
- INV-023.2: `implemented`, `partial` e `absent` são os únicos status válidos.
- INV-023.3: Itens duplicados no diretório de inspiração são consolidados num único item canônico.
- INV-023.4: A classificação deve ser determinística para a mesma árvore de arquivos.

## 6. Critérios de Aceitação

- [x] `audit_inspirations()` retorna pelo menos 8 itens canônicos.
- [x] `research_analyze_batch` é classificado como `implemented` na árvore atual.
- [x] `research_final_report_template` é classificado como `implemented` na árvore atual.
- [x] `mira_presentation_system` é classificado como `implemented` na árvore atual.
- [x] `scientific_governance_pipeline_architecture` é classificado como `implemented`.
- [x] `research_run_batch` é classificado como `implemented`.
- [x] `render_inspiration_audit_markdown()` contém resumo e tabela de itens.
- [x] `MarceloClaroOrchestrator.audit_inspirations()` registra reflexão.

## 7. TDD

- RED: `tests/test_inspiration_audit.py`
- GREEN: `marceloclaro/inspiration_audit.py` + integração no orquestrador
- REFACTOR: ajuste de catálogo, notas e renderização Markdown sem quebrar os testes
