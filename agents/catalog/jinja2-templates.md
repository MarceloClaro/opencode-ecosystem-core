---
name: jinja2-templates
description: Agente especializado jinja2-templates
version: '1.0.0'
skills:
- id: jinja2-templates
  name: Jinja2 Templates
  description: Executa tarefas especializadas de jinja2 templates conforme protocolo SDD/TDD.
  tags: [jinja2, templates]
  examples: [Execute esta tarefa conforme especificação, Analise e reporte os resultados]
tags: [jinja2, templates]
examples: [Execute esta tarefa conforme especificação, Analise e reporte os resultados, Execute esta tarefa conforme especificação]
---

# Jinja2Templates

**ID:** `jinja2-templates`
**Tipo:** Subagente local (sem LLM)
**Fonte:** `skills/tooling/jinja2_templates/`

## Descrição

Motor de templates Jinja2 para geração de documentos, relatórios e
notebooks sem chamadas LLM. Substitui f-strings hardcoded e chamadas
de LLM para geração de texto estruturado.

## Templates Disponíveis (9)

| Template | Uso | Substitui |
|---|---|---|
| `fichamento.md.j2` | Resenha crítica de artigo | `research/fichamento.py` LLM |
| `quality_report.md.j2` | Relatório de qualidade | `nano_orchestration/quality_checker.py` LLM |
| `manifest.md.j2` | Manifesto de pesquisa | `research/hub.py` LLM |
| `nanoblock.md.j2` | Bloco de manuscrito acadêmico | `nano_orchestration/writer.py` LLM |
| `debate_synthesis.md.j2` | Síntese de debate multi-agente | `gametheory/moderator.py` LLM |
| `thesis_feedback.md.j2` | Feedback de tese | `synthetic_university/llm_evaluator.py` LLM |
| `validation_feedback.md.j2` | Feedback de validação | `synthetic_university/empirical_validation.py` LLM |
| `notebook.ipynb.j2` | Notebook Jupyter JSON | 6 scripts de notebook |
| `teleological.md.j2` | Relatório de scanner | scanners f-strings |

## Performance

- Renderização média: < 1ms (vs 2-10s via LLM)
- Cache de templates compilados (Jinja2 nativo)
- Filtros customizados: markdown, table, format_date, pct, abnt_author

## Dependências

- `Jinja2` (instalado)

## Uso

```python
from skills.tooling.jinja2_templates import Jinja2Engine
engine = Jinja2Engine()
html = engine.render("fichamento.md.j2", {
    "titulo": "Paper X", "autores": ["João"], "ano": 2024, ...
})
```
