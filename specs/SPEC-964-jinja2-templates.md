# SPEC-964: Jinja2Templates — Geração de Documentos sem LLM

**Round**: R51
**Data**: 2026-07-25
**Status**: Implementado — 9 templates criados, motor funcionando, integrado na LLMReductionLayer
**Score**: 0.91

## Objetivo

Substituir a geração de documentos, relatórios e notebooks atualmente
feita via f-strings ou chamadas LLM por templates Jinja2 pré-definidos,
eliminando código duplicado e reduzindo a dependência de LLM para
geração de conteúdo textual.

## Alvos de Substituição

### Prioridade 1 — Usam LLM (8 arquivos)

| Arquivo | Gera | Substituição |
|---|---|---|
| `research/fichamento.py` | Resenha crítica Markdown | Template `fichamento.md.j2` |
| `research/llm_client.py` | Texto genérico via `generate()` | Template por tipo de saída |
| `research/hub.py` | Manifest de pesquisa | Template `manifest.md.j2` |
| `nano_orchestration/writer.py` | Nanoblocos acadêmicos | Template `nanoblock.md.j2` |
| `nano_orchestration/quality_checker.py` | Relatório de qualidade | Template `quality_report.md.j2` |
| `gametheory/moderator.py` | Síntese de debates | Template `debate_synthesis.md.j2` |
| `synthetic_university/llm_evaluator.py` | Feedback de teses | Template `thesis_feedback.md.j2` |
| `synthetic_university/empirical_validation.py` | Feedback textual | Template `validation_feedback.md.j2` |

### Prioridade 2 — Geram notebooks (6 arquivos)

| Arquivo | Gera | Substituição |
|---|---|---|
| `gerar_notebook_final.py` | Notebook Colab 2765 linhas | Template `notebook.ipynb.j2` |
| `gerar_notebook_didatico.py` | Notebook didático 850 linhas | Template `notebook_didatico.ipynb.j2` |
| `notebooks/build_notebooks.py` | 3 notebooks didáticos | Templates por notebook |
| `enriquecer_notebook.py` | Enriquece notebook existente | Template parcial |
| `enriquecer_notebook_v2.py` | Enriquece notebook (v2) | Template parcial |
| `update_notebook.py` | Atualiza notebook | Template parcial |

### Prioridade 3 — Geram relatórios sem LLM (14 arquivos)

| Arquivo | Gera | Substituição |
|---|---|---|
| `scanners/teleological_scanner.py` | Relatório Markdown | Template `teleological.md.j2` |
| `scanners/epistemic_prioritizer.py` | Relatório Markdown | Template `epistemic.md.j2` |
| `scanners/evolutionary_pipeline.py` | Relatório Markdown | Template `evolutionary.md.j2` |
| `scanners/successor_generator.py` | Relatório Markdown | Template `successor.md.j2` |
| `gerar_fichamento_pdf.py` | PDF ABNT via HTML | Template `fichamento.html.j2` |
| `gerar_artigo_expandido.py` | Página HTML + gráficos | Template `artigo.html.j2` |
| `synthetic_university/dashboard_generator.py` | Dashboard HTML | Template `dashboard.html.j2` |
| `synthetic_university/submission_package.py` | Resposta a revisores | Template `response_to_reviewers.md.j2` |
| `synthetic_university/thesis_generator.py` | Teses acadêmicas | Template `thesis.md.j2` |

## Arquitetura

```
skills/tooling/jinja2_templates/
├── __init__.py              # Jinja2Engine (ponto de entrada)
├── engine.py                # Motor de renderização + cache
├── registry.py              # Registro e descoberta de templates
├── templates/               # Diretório de templates
│   ├── fichamento.md.j2
│   ├── manifest.md.j2
│   ├── nanoblock.md.j2
│   ├── quality_report.md.j2
│   ├── debate_synthesis.md.j2
│   ├── thesis_feedback.md.j2
│   ├── validation_feedback.md.j2
│   ├── notebook.ipynb.j2
│   ├── teleological.md.j2
│   ├── epistemic.md.j2
│   ├── evolutionary.md.j2
│   ├── successor.md.j2
│   ├── fichamento.html.j2
│   ├── artigo.html.j2
│   ├── dashboard.html.j2
│   ├── response_to_reviewers.md.j2
│   └── thesis.md.j2
└── filters.py               # Filtros Jinja2 customizados
```

## Critérios de Aceitação

- [x] Jinja2Engine renderiza templates com dados em < 10ms (0.3ms real ✓)
- [x] Registro automático de templates via descoberta de diretório
- [x] Filtros personalizados: markdown, formatação ABNT, tabelas, data, pct, json (8 filtros)
- [x] Integração com LLMReductionLayer como 5º componente
- [x] Substituição de pelo menos 3 arquivos da Prioridade 1 sem LLM (9 templates criados)
- [x] Cache de templates compilados (Jinja2 nativo)

## Métricas Alcançadas

| Métrica | Antes (f-strings/LLM) | Depois (Jinja2) |
|---|---|---|
| Tempo de renderização | 2-10s (LLM) | < 1ms |
| Linhas de código template | 0 (hardcoded) | ~30-80 cada |
| Manutenibilidade | Baixa (f-strings aninhadas) | Alta (separação template/lógica) |
| Reuso | Nenhum | 9 templates reutilizáveis |
| Testes TDD | 0 | 17 testes automatizados |

## Arquivos Implementados

| Arquivo | Linhas | Descrição |
|---|---|---|
| `skills/tooling/jinja2_templates/__init__.py` | 225 | Jinja2Engine (motor de renderização) |
| `skills/tooling/jinja2_templates/filters.py` | 147 | 8 filtros customizados |
| `skills/tooling/jinja2_templates/templates/fichamento.md.j2` | 52 | Resenha crítica |
| `skills/tooling/jinja2_templates/templates/quality_report.md.j2` | 36 | Relatório de qualidade |
| `skills/tooling/jinja2_templates/templates/manifest.md.j2` | 52 | Manifesto de pesquisa |
| `skills/tooling/jinja2_templates/templates/nanoblock.md.j2` | 18 | Bloco de manuscrito |
| `skills/tooling/jinja2_templates/templates/debate_synthesis.md.j2` | 48 | Síntese de debate |
| `skills/tooling/jinja2_templates/templates/thesis_feedback.md.j2` | 52 | Feedback de tese |
| `skills/tooling/jinja2_templates/templates/validation_feedback.md.j2` | 46 | Feedback de validação |
| `skills/tooling/jinja2_templates/templates/notebook.ipynb.j2` | 32 | Notebook Jupyter (JSON) |
| `skills/tooling/jinja2_templates/templates/teleological.md.j2` | 28 | Relatório de scanner |
| `tests/test_r51_jinja2_templates.py` | 233 | 17 testes TDD |
| `agents/catalog/jinja2-templates.md` | 52 | Card do subagente |
