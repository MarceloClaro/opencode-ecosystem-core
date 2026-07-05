# SPEC-020 — Diagnóstico Profundo (Deep Diagnose)

```yaml
spec_id: SPEC-020
title: Diagnóstico Profundo — Roadmap Evolutivo + Priorização Epistemológica + Sucessores Plausíveis
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-009, SPEC-012]
origin: Anexos 3-8 (propostas do usuário) + academic-audit do OpenCode_Ecosystem original
```

## 1. Contexto

Os anexos 3–8 propuseram seis capacidades de metacognição estrutural:

1. **Scanner Noológico com potencial epistemológico** (anexo 3) — não só
   detectar ausências, mas estimar o *valor* de preencher cada ausência.
2. **Trajetórias evolutivas M1–M5** (anexo 4) — mapear rotas de aquisição
   de capacidades (quick wins, foundations, frontiers, convergents).
3. **Scanner Reverso + Sequenciamento** (anexo 5) — inferir a ordem lógica
   de construção de capacidades a partir de metas.
4. **Composição Unitária** (anexo 6) — decompor capacidades em unidades
   mínimas (CapabilityUnit) com custo de construção.
5. **Potentiality Scanner / DNA estrutural** (anexo 7) — extrair os "genes"
   do ecossistema e seus potenciais latentes.
6. **Successor Generator** (anexo 8) — gerar hipóteses de capacidades
   emergentes plausíveis por recombinação de genes do DNA.

## 2. Requisitos

| ID | Requisito | Verificação |
|----|-----------|-------------|
| R1 | `DiagnosticPipeline.run(..., deep=True)` DEVE executar o roadmap M1–M5 completo quando houver metas | test_deep_roadmap |
| R2 | O modo deep DEVE produzir `epistemic_opportunities` com tiers (breakthrough/promissora/marginal) e score composto de 4 fatores | test_prioritizer |
| R3 | O modo deep DEVE produzir `successors` com tiers (imediato/próximo-horizonte/especulativo) a partir do DNA estrutural | test_successors |
| R4 | O score de oportunidade DEVE combinar centralidade, raridade, interdisciplinaridade e viabilidade (pesos 0.30/0.20/0.25/0.25) | test_opportunity_score |
| R5 | O score de sucessor DEVE combinar sinergia, viabilidade, aderência ao tema e emergência (pesos 0.30/0.30/0.20/0.20) | test_successor_score |
| R6 | Ambos os geradores DEVEM emitir relatórios Markdown auditáveis (`generate_report`) | test_reports_md |
| R7 | `orch.diagnose(corpus, deep=True)` DEVE registrar reflexão metacognitiva com síntese da camada profunda | test_orchestrator_deep |
| R8 | O modo deep NÃO PODE derrubar o pipeline em caso de erro de um módulo (isolamento por try/except) | test_isolation |

## 3. Invariantes

- INV1: `0.0 <= opportunity_score <= 1.0` e `0.0 <= successor_score <= 1.0`.
- INV2: `deep=False` (padrão) mantém o comportamento anterior do pipeline
  (retrocompatibilidade total — nenhuma chave nova obrigatória).
- INV3: Sucessores são recombinações de genes existentes no DNA — nunca
  inventam genes ausentes.
- INV4: Oportunidades derivam exclusivamente de dimensões medidas pelo
  Scanner Noológico (rastreabilidade: cada oportunidade cita a dimensão).

## 4. Arquitetura

```
orch.diagnose(corpus, goals, deep=True)
    └── DiagnosticPipeline.run(deep=True)
          ├── [1-6] scanners padrão (noológico, teleológico, potentiality,
          │         social, evolutivo-síntese, reversa)
          └── _run_deep()
                ├── EvolutionaryScannerPipeline.scan()   # M1–M5 + composição
                │     ├── M1 NoologicalScanner
                │     ├── M2 TeleologicalReverseScanner
                │     ├── M3 CrossValidationEngine
                │     ├── M3.5 CapabilityComposer (SPEC-033 legado)
                │     ├── M4 PolymathicConvergence
                │     ├── M5 TrajectoryMapper
                │     └── M3.8 Sequenciamento evolutivo
                ├── EpistemicPrioritizer.prioritize()    # erro→ausência→oportunidade
                └── SuccessorGenerator.generate()        # DNA → sucessores
```

## 5. Critérios de Aceitação

- [x] Demo `examples/demo_deep_diagnose.py` executa sem erros.
- [x] Roadmap produz gaps classificados e sequência lógica de construção.
- [x] Priorização emite ao menos 1 oportunidade para corpus não trivial.
- [x] Sucessores emitem ao menos 1 hipótese com DNA de ≥ 2 genes.
- [x] Bateria `tests/test_deep_diagnose.py` 100% verde.
