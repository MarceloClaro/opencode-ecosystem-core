# SPEC-935-R1148 — Metacognição subjetiva, lógica e quântica

**Status:** implementação local; dados sintéticos; sem hardware
**Data:** 2026-11-10
**Depende de:** R1146, R1147, `mci/evidence_graph.py`,
`mci/confidence_calibrator.py`, `trust/trust_engine.py`
**Fontes de método:** EMA, N-of-1/SCED (NAP, PEM, Tau-U), Brier/ECE,
PROV-like provenance, circuit breaker.

## 1. Objetivo

Melhorar a metacognição do Core em cinco camadas correlacionadas:

1. **EMA** com agenda, compliance, faltantes, transferência e psicometria;
2. **N-of-1** com randomização, lock, adesão, eventos adversos e SCED;
3. **Grafo de claims** com proveniência, evidência real/complexa/irreal,
   prova/contraprova formal e contradições;
4. **Trust warrant** separando coordenação de warrant epistêmico, com
   Brier/ECE e abstenção;
5. **Contrato de runtime** com classes de ação, hooks, circuit breaker e
   escalada humana.

## 2. Requisitos

- **R1.** `mci.ema`: `build_schedule`, `record_responses`,
  `validate_psychometrics`, `paired_transfer_test`, `ema_report`.
- **R2.** `mci.n_of_1`: `generate_sequence`, `lock_preregistration`,
  `verify_lock`, `nap`, `pem`, `tau_u`, `lag1_autocorrelation`,
  `permutation_test_nap`, `run_n_of_1`.
- **R3.** `mci.claims_graph`: nós claim/source/excerpt/test/evidence/theorem/
  counterproof; arestas supports/contradicts/insufficient/derived_from/tests/
  proves/counterproves; `add_formal_link` com certificado kernel-checked;
  `add_psychometric`; `detect_contradictions`; `warrant`.
- **R4.** `mci.trust_warrant`: `brier_score`, `expected_calibration_error`,
  `coordination_score`, `epistemic_warrant`, `trust_report`; abstenção sem
  histórico.
- **R5.** `mci.runtime_contract`: classes `read_only`, `reversible`,
  `irreversible`, `high_risk`; hooks `before`/`after`; circuit breaker;
  escalada humana; auditoria JSONL.
- **R6.** Metadados psicométricos obrigatórios; lock de pré-registro;
  aprovação explícita para ações irreversíveis.
- **R7.** Nenhum hardware, rede, submissão ou alegação de verdade clínica.

## 3. Regras de warrant

| Tipo | Regra |
|---|---|
| `axiom` | hipótese declarada; warrant ≤ 0,5; abstenção |
| `lemma`/`law`/`theory` | exige teorema **e** contraprova kernel-checked; sem isso, `insufficient_formal` |
| `hypothesis` | suportada/contradita por evidência; conflito → abstenção |
| `empirical` | evidência real/complexa peso 1,0; irreal peso 0,3 |
| `subjective` | metadados psicométricos obrigatórios; warrant ≤ 0,6; abstenção |

Evidência **irreal** é sintética/contrafactual: só pode gerar
`simulation_only`, nunca `supported`.

## 4. Critérios de aceitação

- EMA: compliance conta prompts ausentes; metadados inválidos bloqueiam;
  transferência separa dependente de autônomo.
- N-of-1: hash de lock determinístico; lock errado bloqueia; evento grave
  interrompe; NAP/PEM/Tau-U/permutação calculados; autocorrelação sinalizada.
- Claims: claim real suportada; irreal descontada; subjetiva sem psicometria
  bloqueada; axioma declarado; formal exige kernel-checked; contradição
  detectada.
- Trust: histórico calibrado aceito; superconfiante abstém; sem histórico
  `calibration_insufficient_data`.
- Runtime: `read_only` executa; `irreversible` sem aprovação escala; hook
  nega; breaker abre e recupera; auditoria grava JSONL.

## 5. Limites

Dados sintéticos; EMA e N-of-1 não substituem ética, consentimento,
participante ou supervisão clínica. Brier/ECE não provam verdade. O grafo liga
evidência; não a inventa. O contrato de runtime não prova segurança jurídica ou
ausência de efeitos colaterais. Nenhuma vantagem quântica ou clínica é alegada.
