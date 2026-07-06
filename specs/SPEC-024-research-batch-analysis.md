# SPEC-024 — Análise Estatística de Batch Research + Relatório Final Integrado

```yaml
spec_id: SPEC-024
title: Port de analyze_research_batch + template final de relatório de pesquisa
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-017, SPEC-021, SPEC-023]
origin: INSPIRAÇÕES/research_pipelines_analyze_research_batch.py + research_results_reports_final_report_template.md
```

## 1. Objetivo

Portar para o Core o analisador estatístico de lotes de pesquisa e o template final consolidado de relatório, fechando as lacunas identificadas na auditoria de inspirações (SPEC-023) para:

- `research_analyze_batch`
- `research_final_report_template`

## 2. Escopo

### 2.1 Dentro do escopo

- módulo `research/pipelines/analyze_research_batch.py`
- cálculo de IC 95%, tamanho de efeito e comparação com baseline
- scorecard de maturidade (`MaturityScorecard`)
- geração de relatório analítico em Markdown
- template final em `research/results/reports/final_report_template.md`
- gerador de relatório final preenchido a partir de raw/summary/análise
- atualização da auditoria de inspirações para refletir o novo estado

### 2.2 Fora do escopo

- dashboard visual
- comparação automática contra benchmark humano externo
- integração CI com cobertura/lint/typecheck obrigatórios

## 3. Requisitos

| ID | Requisito | Critério de aceitação |
|---|---|---|
| REQ-024.1 | O módulo `analyze_research_batch.py` DEVE carregar resultados JSONL de `run_research_batch.py` | `load_raw_results()` retorna lista de dicts |
| REQ-024.2 | O módulo DEVE calcular IC 95% para métricas OQS/VSEE/EGS/pipeline | `mean_ci_95()` retorna `mean/std/lower/upper` coerentes |
| REQ-024.3 | O módulo DEVE comparar baseline vs pipeline completo | `compute_baseline_comparison()` retorna comparações com ganho e significância |
| REQ-024.4 | O módulo DEVE produzir um `MaturityScorecard` com blockers, warnings e readiness | `evaluate_maturity()` retorna scorecard consistente |
| REQ-024.5 | O módulo DEVE gerar relatório analítico em Markdown | `generate_analysis_report()` escreve arquivo com seções OQS/VSEE/EGS/Pipeline |
| REQ-024.6 | O repositório DEVE conter o template final em `research/results/reports/final_report_template.md` | arquivo existe e contém seções da inspiração |
| REQ-024.7 | O módulo DEVE preencher um relatório final consolidado a partir do template | `generate_final_report()` produz Markdown com seções preenchidas |
| REQ-024.8 | Após a implementação, a auditoria de inspirações DEVE classificar `research_analyze_batch` como `implemented` | teste de auditoria verde |
| REQ-024.9 | Após a implementação, a auditoria DEVE classificar `research_final_report_template` como `implemented` | teste de auditoria verde |

## 4. Invariantes

- INV-024.1: O analisador funciona com stdlib; dependências externas são opcionais.
- INV-024.2: Relatórios gerados são determinísticos para a mesma entrada.
- INV-024.3: `overall_ready=False` sempre que houver blocker crítico.
- INV-024.4: O template final preserva as seções essenciais da inspiração (Resumo, Método, Resultados, Robustez, Limitações, Conclusão, Release).

## 5. Critérios de Aceitação

- [ ] `research/pipelines/analyze_research_batch.py` existe e é importável
- [ ] `research/results/reports/final_report_template.md` existe
- [ ] `tests/test_analyze_research_batch.py` passa 100%
- [ ] `tests/test_inspiration_audit.py` passa com `research_analyze_batch == implemented`
- [ ] `tests/test_inspiration_audit.py` passa com `research_final_report_template == implemented`

## 6. TDD

- RED: criar/atualizar `tests/test_analyze_research_batch.py` e `tests/test_inspiration_audit.py`
- GREEN: implementar módulo + template
- REFACTOR: melhorar renderização do relatório final sem quebrar contratos
