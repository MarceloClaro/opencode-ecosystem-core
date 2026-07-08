# SPEC-928: Benchmarks Jurídicos por Ramo

```yaml
spec_id: SPEC-928
title: Suíte conservadora de benchmarks jurídicos por domínio
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-927, SPEC-923, SPEC-921]
origin: pedido do usuário para avançar da especialização jurídica para benchmarks que sustentem a ideia de comportamento especialista por ramo
```

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Criar uma suíte de benchmarks jurídicos por ramo que permita medir, de forma **conservadora e auditável**, o quão bem o ecossistema se comporta em cada domínio jurídico especializado.

## 2. Escopo

### 2.1 Ramos cobertos

- penal
- trabalhista
- tributário
- empresarial
- administrativo
- ambiental
- digital/LGPD

### 2.2 Métricas

1. **router_accuracy** — acerto do roteamento por domínio
2. **answer_score** — qualidade jurídica da resposta por caso
3. **domain_coverage_score** — cobertura do domínio inferida a partir do perfil
4. **overall_score** — score consolidado da suíte
5. **expertise_tier** — classificação conservadora por faixa

### 2.3 Política anti-overclaim

Mesmo scores altos **não** autorizam afirmar “PhD validado” sem validação externa.

Classificação proposta:

- `base`
- `specialist`
- `specialist_advanced`
- `phd_candidate`
- `phd_validated` (**somente com `external_validation=True`**)

## 3. Critérios de Aceitação (TDD)

1. a suíte contém casos para os 7 ramos
2. `benchmark_router()` mede acurácia do roteamento
3. `evaluate_domain_answer()` retorna score entre 0 e 100
4. respostas com estatutos, princípios e cautela jurídica pontuam mais do que respostas rasas
5. `run_domain_benchmark_suite()` retorna relatório consolidado
6. `classify_domain_expertise_tier()` nunca retorna `phd_validated` sem validação externa

## 4. Resultado Esperado

O ecossistema passa a ter um instrumento objetivo para dizer:

- em quais ramos está mais forte;
- onde a especialização é apenas inicial;
- quando a linguagem de “quase especialista / phd_candidate por domínio” é defensável internamente;
- e quando isso ainda seria overclaim.
