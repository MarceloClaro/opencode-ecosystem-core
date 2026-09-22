---
spec_id: SPEC-935-R504
component: reversa_feynman.*
title: ReversaFeynman Bridge — Evidence & Calibration Layer (port Python do ReversaFeynman)
version: 1.0.0
status: green
test_file: tests/test_r504_feynman_bridge.py
---

# SPEC-935-R504 — ReversaFeynman Bridge no OpenCode Ecosystem Core

## Meta
- **Ciclo**: R504
- **Origem**: `MarceloClaro/reversa` (ReversaFeynman — linha independente derivada do Reversa original de Macedo & Costa, arXiv:2605.18684). Port Python dos contratos/gates; **não** é sync automático (independência preservada), não incorpora runtime Node.
- **Motivação**: o achado R503 (mimo 0.987 → 0.44 sob validação cruzada) expôs que o Trust Engine e o roteamento R500 atualizam scores **sem calibração formal** (Brier/ECE existem apenas heuristicamente em `mci/confidence_calibrator` para ScientificClaims, sem decide→observe, holdout, drift, IC95, readiness) e sem auditoria criptográfica. R504 fecha essa lacuna.
- **Reuso**: `mci/confidence_calibrator.py` (Brier/ECE) mantém-se para claims; este módulo adiciona a camada de *avaliação offline de política* e *governança epistemológica*.

## Arquitetura

```
reversa_feynman/
├── __init__.py
├── evidence_guard.py   # OBSERVED / INFERRED / UNVERIFIED / BLOCKED + apply_evidence_proposal
├── feynman_gates.py    # FEG-01..07 (score 0..12; FEG-07 humano fora do score)
├── offline_eval.py     # OfflinePolicyEvaluator v3: decide→observe, holdout, Brier/ECE,
│                       #   reward/regret, IC95 bootstrap (seed determinística), drift, readiness
├── ledger.py           # AuditLedger: hash-chain SHA-256, dedupe, verify, snapshot, JSONL
└── router_calibration.py  # CalibratedRoutingAdvisor: consome eval e recomenda (nunca impõe)
```

## Critérios de aceitação (testes)

1. **EvidenceGuard** — `apply_evidence_proposal`:
   - recoje origem `learned-policy`/`memory` (direct=False) promovendo a `OBSERVED`;
   - aceita origem direta rastreável (`kind=test`, `ref=tests/...:linha`);
   - memória/confiança/skill-confidence **nunca** produzem `OBSERVED`.
2. **FeynmanGates** — FEG-01..06 pontuam 0..12; 0 quando sem evidência/proveniência; FEG-07 (teach-back) só via humano e não entra no score.
3. **OfflinePolicyEvaluator**:
   - separa `decide(d)` de `observe(d, decision)`; `ingest()` não permite look-ahead (outcome do evento não entra no histórico usado pela decisão do mesmo evento);
   - holdout temporal `trainFraction=0.70` (registros ordenados por `decided_at`); política avaliada no holdout não usado para estimar;
   - Brier e ECE calculados em `shadow-matched-only`;
   - contrafactual quando `shadow_action != executed_action`: **não inventa outcome**; reward/regret estimados rotulados `observational/model-based` e `not causal`;
   - IC95% bootstrap determinístico (PRNG por seed → mesmo resultado para mesma seed);
   - DriftDetector: janela referência vs recente → `insufficient_data | stable | drift`; drift bloqueia readiness;
   - PromotionReadiness com thresholds default (minRecords 30, minMatchedShadow 12, minShadowCoverage 0.20, maxBrier 0.25, maxEce 0.20, maxEstimatedShadowRegret 0.10, minEstimatedRewardDelta 0.00); **auto_activate = False sempre**; elegível produz only `requestPolicyActivation()`.
4. **AuditLedger** — hash-chain SHA-256: dedupe por `event_id`; payload canonicalizado; verificação integral; detecção de adulteração; snapshot somente leitura; export JSONL.
5. **router_calibration** — com dados do R503 (mimo 4/9 conf. 0.987; big-pickle 1/9 conf. 0.923), o conselho recomenda redução do score calibrado do big-pickle abaixo do mimo; **não** altera `FREE_BENCHMARK` sozinho (requer ativação explícita).

## Não-escopo / anti-overclaim
- Não promete melhoria de acurácia de modelos; melhoria é de **governança/calibração**.
- Não substitui `mci/confidence_calibrator.py` nem `trust/trust_engine.py` — integra-se a eles.
- Nenhum score é alterado sem ativação explícita.