# Benchmark Cultural Medido — R367

Gerado em 2026-08-02T09:26:03.084101+00:00 sobre corpus interno rotulado de 18 casos.

> Números medidos em corpus interno rotulado, pequeno e construído pela própria equipe; NÃO constituem validação externa, benchmark independente nem promessa de desempenho em obras reais. Servem para acompanhar a evolução das regras e documentar limitações conhecidas.

Este relatório NÃO constitui validação externa. Qualquer uso comercial
destes números deve citá-los como medição descritiva em corpus interno,
com data e tamanho do corpus.

## Métricas por código

| Código | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|
| ANACHRONISM | 1 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| CULTURAL_LOSS | 2 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| PRAGMATIC_FAILURE | 2 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| REGISTER_SHIFT | 1 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| SYMBOL_DRIFT | 1 | 0 | 0 | 1.00 | 1.00 | 1.00 |
| TERM_CONFLICT | 3 | 0 | 1 | 1.00 | 0.75 | 0.86 |
| VOICE_SHIFT | 2 | 0 | 1 | 1.00 | 0.67 | 0.80 |

**Agregado (micro):** precisão 1.00, recall 0.86.

## Limitações conhecidas evidenciadas pelo corpus

- `T5-inflected-plural-miss` (terminology): esperado ['TERM_CONFLICT'], detectado [] — limitação conhecida das regras atuais.
- `V6-colloquial-intensity-miss` (voice): esperado ['VOICE_SHIFT'], detectado [] — limitação conhecida das regras atuais.
