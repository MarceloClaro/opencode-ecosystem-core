# SPEC-924: Scanner de Visão Jurídica de Impacto para Pesquisas e Produções

```yaml
spec_id: SPEC-924
title: Scanner jurídico de impacto para pesquisa, produção científica e artefatos do ecossistema
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-921, SPEC-922, SPEC-923, SPEC-009, SPEC-022]
origin: pedido do usuário para avaliar ganho metacognitivo com conhecimento jurídico e criar scanner de visão jurídica
```

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Criar um **Legal Impact Scanner** para avaliar pesquisas, produções e artefatos do ecossistema sob uma ótica jurídica de impacto, conformidade e defensibilidade. O scanner deve também medir se a incorporação do conhecimento jurídico amplia o **desempenho metacognitivo** do ecossistema.

## 2. Hipótese de Valor

A adição de conhecimento jurídico especializado melhora a metacognição do ecossistema porque adiciona:

- **awareness normativa** — percepção de LGPD, licenças, responsabilidade, ética, precedentes e compliance;
- **detecção de conflito normativo** — capacidade de perceber tensões entre abertura científica, privacidade, propriedade intelectual e risco regulatório;
- **antecipação de risco** — identificação de riscos antes da publicação/produção;
- **humildade epistêmica aplicada** — reconhecer quando um output precisa de abstenção, revisão jurídica ou escalonamento.

## 3. Escopo

### 3.1 Dimensões avaliadas

1. **Proteção de dados e LGPD**
2. **Propriedade intelectual e licenciamento**
3. **Conformidade regulatória e ética**
4. **Grounding jurisprudencial/normativo**
5. **Responsabilidade contratual e risco litigioso**
6. **Defensibilidade de publicação/produção**

### 3.2 Dimensões metacognitivas jurídicas

1. **compliance_awareness**
2. **normative_conflict_detection**
3. **risk_anticipation**
4. **epistemic_humility_legal**

## 4. Integração

- novo módulo: `scanners/legal_impact_scanner.py`
- integração opcional ao `DiagnosticPipeline.run(..., include_legal_impact=True)`
- atualização do `README.md` e `diagram.mmd`

## 5. Critérios de Aceitação (TDD)

1. `LegalImpactScanner.analyze_research_paper()` retorna relatório estruturado
2. `LegalImpactScanner.analyze_production_artifact()` retorna relatório estruturado
3. `overall_score` e `metacognitive_gain_score` ficam em `[0,100]`
4. um corpus juridicamente consciente tem `metacognitive_gain_score` maior que um corpus neutro
5. o scanner detecta sinais de LGPD, licenciamento e jurisprudência
6. `DiagnosticPipeline.run(..., include_legal_impact=True)` inclui seção `legal_impact`
7. `DiagnosticPipeline.run(..., include_legal_impact=False)` preserva retrocompatibilidade

## 6. Resultado Esperado

O ecossistema deve passar a avaliar não apenas lacunas epistemológicas e impacto social, mas também **defensibilidade jurídica e maturidade metacognitiva jurídica** de pesquisas e produções.
