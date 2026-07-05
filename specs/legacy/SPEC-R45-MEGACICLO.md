# SPEC-R45 — Megaciclo: Raciocínio Formal + Descoberta + Cobertura + Academia + Refino

**Ciclo:** R45  
**Versao:** 1.0.0  
**Status:** SDD (Spec-Driven Development)  
**CTs Planejados:** 60  
**Total Ecossistema apos R45:** 537 CTs (477 + 60)

---

## Sumario Executivo

Este megaciclo executa **5 fases sequenciais** para completar todos os rascunhos pendentes
do ecossistema e ampliar a cobertura noológica para 60%+:

```
Fase A (ARCHE+OQS) → Fase B (ASDE) → Fase C (Cobertura 60%+) 
    → Fase D (Acadêmico) → Fase E (Refino+Fechamento)
```

Cada fase segue SDD → TDD → Implementação → Validação.

---

## Fase A: ARCHE RLT (SPEC-057) + OQS (SPEC-056)

### A.1 ARCHE RLT — Reasoning Logic Tree

Implementar os 6 tipos de inferência de Peirce como motores de raciocínio formais:

| Tipo | Sigla | Motor | 
|:----:|:-----:|-------|
| Deduction-Rule | DR | Z3 (∀x(P(x)→Q(x)), P(a) ⊢ Q(a)) |
| Deduction-Case | DC | Probabilístico (∀x(P(x)→Q(x)), Q(a) ⊢ P(a)) |
| Induction-Common | IC | Indutivo (P(a₁)∧Q(a₁)... ⊢ ∀x(P(x)→Q(x))) |
| Induction-Case | IH | Teste de hipótese |
| Abduction-Knowledge | AK | Ontologia (Q(a), ∀x(P(x)→Q(x)) ⊢ P(a)) |
| Abduction-Phenomenon | AP | Descoberta (Q(a), ∃x(R(x)→Q(x)) ⊢ R(a)) |

### A.2 OQS — Optimal Question Scanner

Implementar o pipeline:

```
UncertaintyScanner → QuestionVectorizer → ConvergenceScore
    → QuestionSelector → FeedbackLoop
```

### CTs Fase A: 12

| CT | Nome | Descrição |
|:--:|------|-----------|
| A01 | arche_imports | Módulo ARCHE importa sem erros |
| A02 | arche_rlt_node | RLTNode com todos os campos |
| A03 | arche_rlt_tree | Árvore RLT com 3+ níveis |
| A04 | arche_all_6_types | Todos os 6 tipos de Peirce funcionam |
| A05 | arche_type_mapping | Mapeamento 212+ tipos → 6 Peirce |
| A06 | oqs_imports | Módulo OQS importa sem erros |
| A07 | oqs_uncertainty_scan | UncertaintyScanner retorna estrutura |
| A08 | oqs_question_vectorize | QuestionVectorizer funciona |
| A09 | oqs_convergence_score | CS calculado corretamente |
| A10 | oqs_select_best | Melhor pergunta selecionada |
| A11 | arche_oqs_integration | ARCHE + OQS integrados |
| A12 | arche_full_pipeline | Pipeline completo executa |

---

## Fase B: ASDE Pipeline (SPEC-058)

### B.1 Componentes

| Componente | Função | Input | Output |
|------------|--------|-------|--------|
| IdeaGenerator | Gera ideias de pesquisa | OQS + RUMI | Ideias rankeadas |
| OntologyGraph | Grafo científico | Ideias | Ontologia |
| MultiAgentCritic | Revisão multi-agente | Hipóteses | Críticas |
| ExperimentPlanner | Plano experimental | Hipóteses aprovadas | Plano |
| ResultSynthesizer | Relatório IMRaD | Resultados | Relatório |

### CTs Fase B: 12

| CT | Nome | Descrição |
|:--:|------|-----------|
| B01 | asde_imports | Módulo ASDE importa sem erros |
| B02 | idea_generator | Geração de ideias funciona |
| B03 | ontology_graph | Grafo ontológico cria nós |
| B04 | multi_agent_critic | Crítica multi-agente avalia |
| B05 | experiment_planner | Plano experimental gerado |
| B06 | result_synthesizer | Relatório IMRaD gerado |
| B07 | asde_full_pipeline | Pipeline completo executa |
| B08 | asde_report_structure | Relatório tem seções ABNT |
| B09 | asde_ontology_persistence | Ontologia persiste |
| B10 | asde_idea_scoring | Ideias têm score replicável |
| B11 | asde_critic_diversity | Críticas de agentes diferentes |
| B12 | asde_end_to_end | Problema → Relatório completo |

---

## Fase C: Cobertura Noológica 60%+

### C.1 Dimensões Alvo

| Dimensão | Cobertura Atual | Alvo | Artefatos Necessários |
|----------|:--------------:|:----:|:---------------------:|
| dominios | 100% | 100% | 0 |
| metodos | 87.5% | 100% | 1 |
| paradigmas | 66.7% | 100% | 2 |
| raciocinio | 80% | 100% | 1 |
| dados | 50% | 80% | 3 |
| niveis_analise | 0% | 60% | 4 |
| temporalidade | 0% | 60% | 4 |
| populacao | 0% | 60% | 8 |
| teorias | 0% | 60% | 7 |
| teoria_jogos | 0% | 100% | 1 |

### CTs Fase C: 12

| CT | Nome | Descrição |
|:--:|------|-----------|
| C01 | coverage_baseline | Medir cobertura atual |
| C02 | inject_niveis_analise | Injetar 4 categorias |
| C03 | inject_temporalidade | Injetar 4 categorias |
| C04 | inject_populacao | Injetar 8 categorias |
| C05 | inject_teorias | Injetar 7 categorias |
| C06 | inject_teoria_jogos | Injetar 1 categoria |
| C07 | fill_remaining_gaps | Completar dimensões parciais |
| C08 | coverage_60_pct | Verificar cobertura ≥ 60% |
| C09 | hi_below_025 | HI < 0.25 |
| C10 | rpi_above_75 | RPI > 75 |
| C11 | topology_no_islands | 0 ilhas topológicas |
| C12 | bridge_strength | Pontes ≥ 0.70 |

---

## Fase D: Pipeline Acadêmico Completo

### D.1 Arquitetura

```
Problema/Pergunta
    → SEEKER (pesquisa profunda, 10+ fontes)
    → MASWOS (49 agentes acadêmicos, 8 fases)
    → PeerReview (5 revisores simulados)
    → Corretor TSAC (87 padrões anti-IA)
    → Qualis A1 Auditor (10 critérios)
    → Export (LaTeX/PDF/DOCX)
    → Manus Evolve (aprendizado do ciclo)
```

### CTs Fase D: 12

| CT | Nome | Descrição |
|:--:|------|-----------|
| D01 | pipeline_imports | Orquestrador importa sem erros |
| D02 | seeker_trigger | SEEKER é acionado |
| D03 | maswos_orchestration | MASWOS orquestrado |
| D04 | peer_review | Revisão simulada |
| D05 | tsac_correction | Correção TSAC aplicada |
| D06 | qualis_audit | Auditoria Qualis A1 |
| D07 | export_latex | Exportação LaTeX |
| D08 | export_pdf | Exportação PDF |
| D09 | manus_evolve_learn | Aprendizado do ciclo |
| D10 | full_pipeline_short | Pipeline completo (problema → rascunho) |
| D11 | citation_validation | Validação ABNT das citações |
| D12 | reproducibility_check | Verificação de reprodutibilidade |

---

## Fase E: Refino + Fechamento

### E.1 Ações

1. Revisar todos os SPECs R25-R44 e marcar status correto
2. Verificar cobertura de testes para todos os módulos nexus/
3. Validar que tools do ecosystem-capabilities têm testes correspondentes
4. Gerar relatório de completude do ecossistema
5. Atualizar ecosystem-state.json com todos os ciclos

### CTs Fase E: 12

| CT | Nome | Descrição |
|:--:|------|-----------|
| E01 | spec_coverage | Todos SPECs têm testes correspondentes |
| E02 | nexus_coverage | Todos módulos nexus/ têm testes |
| E03 | tool_test_mapping | Tools MCP mapeadas para testes |
| E04 | spec_status_audit | Status de todos SPECs auditado |
| E05 | duplicate_spec_check | Sem SPECs duplicados |
| E06 | completeness_report | Relatório gerado |
| E07 | ecosystem_state_valid | State.json válido |
| E08 | ct_count_verified | Contagem total de CTs conferida |
| E09 | backward_compat | Testes R25-R44 ainda passam |
| E10 | no_draft_specs | Todos os SPECs têm status final |
| E11 | readme_updated | README reflete estado atual |
| E12 | final_validation | Todas as suítes verdes |

---

## Arquivos do Ciclo

| Arquivo | Fase |
|---------|:----:|
| `specs/SPEC-R45-MEGACICLO.md` | Este documento |
| `tests/test_r45a_arche_oqs.py` | A — 12 CTs |
| `tests/test_r45b_asde_pipeline.py` | B — 12 CTs |
| `tests/test_r45c_coverage_expansion.py` | C — 12 CTs |
| `tests/test_r45d_academic_pipeline.py` | D — 12 CTs |
| `tests/test_r45e_refine_close.py` | E — 12 CTs |
| `nexus/arche_rlt.py` | A — ARCHE RLT |
| `nexus/oqs_scanner.py` | A — OQS |
| `nexus/asde_pipeline.py` | B — ASDE |
| `nexus/academic_pipeline.py` | D — Orquestrador |
| `ecosystem-state.json` | Atualização |
