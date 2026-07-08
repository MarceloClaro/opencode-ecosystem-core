# SPEC-918: Scientific Superhuman Benchmark Suite

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Elevar o ecossistema de “superhuman-like” para **superhuman científico mensurável**, adicionando uma suíte auditável de avaliação que mede raciocínio científico com critérios externos simulados, maturidade, prontidão, rastreabilidade e integração com RAG.

O objetivo não é declarar superioridade sem evidência; é criar uma régua para dizer, de forma reprodutível, se o ecossistema está:

1. **Base científico** — executa tarefas científicas básicas.
2. **Research-grade** — gera hipóteses, controla vieses e interpreta evidências.
3. **Superhuman-candidate** — supera baselines heurísticos internos em múltiplas dimensões.
4. **Superhuman-verified** — exigiria benchmarks externos reais e validação independente.

## 2. Escopo

Adicionar ao pacote `benchmarks/scientific_reasoning/`:

- `superhuman_suite.py` — orquestrador de avaliação superhuman científica.
- `ScientificSuperhumanReport` — relatório consolidado com readiness, tier e evidências.
- Critérios adicionais sobre a suíte existente:
  - cobertura de domínios científicos;
  - grounding/citações via RAG;
  - adversarial robustness;
  - calibração e incerteza;
  - reprodutibilidade;
  - razão entre score obtido e baseline.

## 3. Critérios de Aceitação

- [x] Suíte existente de 5 benchmarks científicos continua funcionando.
- [x] Nova suíte retorna `readiness_score` normalizado de 0 a 100.
- [x] Nova suíte retorna `tier` em `{base, research_grade, superhuman_candidate, superhuman_verified}`.
- [x] `superhuman_verified` só pode ocorrer se `external_validation=True`.
- [x] Sem validação externa, score alto deve no máximo retornar `superhuman_candidate`.
- [x] Relatório inclui evidências: benchmarks, grounding, robustez, calibração e reprodutibilidade.
- [x] Integra com RAG científico da SPEC-919 para medir grounding.
- [x] Testes TDD cobrem thresholds e impedem claims exagerados.

## 4. Métricas

| Métrica | Peso | Descrição |
|---|---:|---|
| Benchmark score | 35% | Pass rate dos benchmarks científicos existentes |
| Grounding/RAG | 20% | Respostas ancoradas em evidências recuperadas |
| Robustez adversarial | 15% | Resistência a vieses/pegadinhas científicas |
| Calibração | 15% | Confiança compatível com evidência |
| Reprodutibilidade | 15% | Capacidade de gerar plano/teste reproduzível |

## 5. Tiers

| Tier | Condição |
|---|---|
| `base` | readiness < 60 |
| `research_grade` | 60 ≤ readiness < 85 |
| `superhuman_candidate` | readiness ≥ 85, sem validação externa |
| `superhuman_verified` | readiness ≥ 90 e `external_validation=True` |

## 6. Gate SDD/TDD

Nenhum claim “superhuman verificado” é permitido sem o flag explícito de validação externa. A suíte deve ser conservadora por design.

## 7. Validação TDD

```bash
pytest tests/test_scientific_rag_superhuman.py -q
# 8 passed

pytest tests/test_scientific_superhuman.py tests/test_scientific_rag_superhuman.py -q
# 53 passed
```

Melhoria adicional implementada: os benchmarks científicos existentes agora avaliam `pipeline_fn` quando fornecido, evitando autoaprovação indevida.
