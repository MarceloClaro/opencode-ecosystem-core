# SPEC-935-R496 — Integração IVA/SNS/SCE no DiagnosticPipeline

Status: **implementado** (R496)
Data: 2026-09-13
Requer: R493 (InertiaVectorAnalyzer), R494 (StructuralNoiseScanner),
R495 (StructuralCompressionEngine), pipeline SPEC-020/022.

## 1. Contexto

A camada profunda do `DiagnosticPipeline._run_deep` produz roadmap, priorização
epistemológica e sucessores. As 3 novas camadas (IVA, SNS, SCE) foram
implementadas standalone (R493-R495) mas ainda não fazem parte do diagnóstico:
o usuário pediu integração ao pipeline.

## 2. Objetivos

- **OF1** — `deep=True` passa a incluir `report["inertia"]` (R493): avalia
  SUCCESSOR_BANK (R492) e sucessores legados como candidatas; potential =
  coverage (PotentialityScanner R491); QIV e ranking de barreiras.
- **OF2** — `deep=True` inclui `report["noise"]` (R494): SNS aplicado às
  sentenças do corpus; SPS/NRR/FLI + nível + elementos classificados.
- **OF3** — `deep=True` inclui `report["compression"]` (R495): SCE sobre o
  corpus; CR/CPS/FLI/DG + texto comprimido + delta.
- **OF4** — Backcompat: `deep=False` NÃO ganha as chaves novas (R8 intacto).
- **OF5** — Padrão de erro do pipeline: cada bloco em try/except com
  `{"error": ...}`; anti-overclaim em todas as saídas.

## 3. Modelo

```
_run_deep:
    d) cartografar candidatas = SUCCESSOR_BANK + top sucessores legados
       → PotentialityScanner.scan(candidates)  (coverage = potential)
       → InertiaVectorAnalyzer.analyze(rep)    (QIV = potential − inércia)
       report["inertia"] = {n_assessments, quebra_imediata, quebra_moderada,
                            inercia_dominante, top[8], report_md}
    e) sentenças = split(corpus)  → SNS.scan_text(sentences)
       report["noise"] = {sps, nrr, fli, level, n_elements, removed,
                          classified[20], report_md}
    f) SCE.compress(corpus)
       report["compression"] = {cr, cps, fli, dg, level, tokens_original,
                                tokens_final, tokens_saved, report_md}
```

## 4. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | deep=True → `inertia` com `n_assessments > 0` |
| CA2 | Cada assessment com QIV ∈ [0,1] e componentes em [0,1] |
| CA3 | deep=True → `noise` com sps/nrr/fli/level |
| CA4 | deep=True → `compression` com cr/cps/fli/dg + texto comprimido |
| CA5 | deep=False → sem `inertia`/`noise`/`compression` (backcompat) |
| CA6 | `report_md` presente nos 3 blocos |
| CA7 | Anti-overclaim em todo o relatório deep |
| CA8 | Corpus com repetição/ruído → `compression.cr > 1` |
| CA9 | Bloco com falha → dict `{"error": ...}` (padrão pipeline) |
| CA10 | deep sem metas → inertia/noise/compression ainda rodam (não derruba) |

## 5. Entregáveis

- `scanners/pipeline.py` — imports + lazy properties + bloco d/e/f em `_run_deep`
- `tests/test_r496_pipeline_integration.py`
- ciclo R496 + commit

## 6. Prontidão

- `pytest tests/test_r496_pipeline_integration.py` verde; test_deep_diagnose
  verde; regressões R483-R495 verdes