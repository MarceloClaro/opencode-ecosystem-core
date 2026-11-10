# Metacognição subjetiva, lógica e quântica — R1148

**Data:** 2026-11-10
**Módulos:** `mci/ema.py`, `mci/n_of_1.py`, `mci/claims_graph.py`,
`mci/trust_warrant.py`, `mci/runtime_contract.py`
**Relatório:** `harnesses/metacognition/r1148/`
**Dados:** sintéticos; nenhum hardware ou participante real.

## 1. Arquitetura em cinco camadas

```
EMA (subjetivo) ─┐
N-of-1 (caso)  ──┼─→ Claims graph ─→ Trust warrant ─→ Runtime contract
Lean/complexos ──┘     (prova/contraprova)   (abstenção)     (hooks/breaker)
Correlação   ────┘
```

### 1.1 EMA

Agenda determinística, compliance, faltantes sem imputação, metadados
psicométricos obrigatórios e teste de transferência pré/pós.

Resultado do relatório:

| Métrica | Valor |
|---|---:|
| Status | `ready_for_review` |
| Compliance | 0,778 |
| Transferência | `autonomous` |
| Validação clínica | `False` |

O teste distingue:

- **dependente**: offloading sobe e autonomia cai;
- **autônomo**: offloading cai/estabiliza e autonomia sobe.

### 1.2 N-of-1

Runner com fases randomizadas por bloco, lock SHA-256, adesão, eventos
adversos e análise SCED.

| Métrica | Valor |
|---|---:|
| Status | `analyzed` |
| NAP | 1,000 |
| PEM | 1,000 |
| Tau-U | 0,800 |
| p (permutação) | 0,0005 |
| Adesão | 1,000 |

Evento adverso grave interrompe a análise; lock divergente bloqueia.

### 1.3 Claims graph

Nós de claim, fonte, trecho, teste, evidência, teorema e contraprova.
Arestas `supports`, `contradicts`, `insufficient`, `derived_from`, `tests`,
`proves`, `counterproves`. Proveniência PROV-like e detecção de contradições.

Resultado:

| Claim | Tipo | Status | Warrant | Abstenção |
|---|---|---|---:|---|
| `formal_complex` | lemma | `formal_only` | 0,300 | não |
| `formal_correlation` | lemma | `formal_only` | 0,300 | não |
| `empirical_real` | empirical | `supported` | 0,700 | não |
| `empirical_complex` | empirical | `supported` | 0,700 | não |
| `subjective` | subjective | `subjective_review` | 0,600 | sim |
| `irreal` | empirical | `simulation_only` | 0,500 | sim |
| `affirm`/`deny` | empirical | `supported` | 0,700 | não |

Contradições detectadas: **1** (par affirm/deny com suporte dos dois lados).

Os vínculos formais usam os certificados reais de R1146 e R1147:
`interference` ↔ `relative_phase_not_one` e
`marginals_do_not_determine_joint` ↔ `joints_differ`, ambos
`kernel_checked`.

### 1.4 Trust warrant

Separa coordenação de warrant:

| Histórico | Status | Warrant | Abstenção |
|---|---|---:|---|
| Calibrado (n=40, p=0,7) | `calibrated` | 0,853 | não |
| Superconfiante (n=30, p=0,9, 70%) | `overconfident` | 0,765 | **sim** |
| Vazio | `calibration_insufficient_data` | — | sim |

Coordenação alta não implica warrant alto. Sem outcomes, o Core abstém.

### 1.5 Runtime contract

| Ação | Resultado |
|---|---|
| `read_only` | `executed` |
| `irreversible` sem aprovação | `escalated` |
| 2 falhas consecutivas | breaker `open` |
| Após cooldown | `half_open` e recuperação |
| Auditoria | JSONL com uma linha por execução |

## 2. Números reais, complexos e irreais

O grafo aceita três domínios de evidência:

- **real**: número real com unidade/incerteza (peso 1,0);
- **complexo**: `{real, imag}` (peso 1,0) — ligado aos teoremas complexos;
- **irreal**: cenário sintético/contrafactual, `synthetic=True` (peso 0,3;
  status `simulation_only`).

“Irreal” nunca é tratado como observação. Ele informa hipóteses e simulações,
mas não sustenta alegação empírica.

## 3. Axiomas, lemas, leis, teorias e hipóteses

| Tipo | Tratamento |
|---|---|
| axioma | declarado, não provado; warrant ≤ 0,5 |
| lema/lei/teoria | exige teorema **e** contraprova kernel-checked |
| hipótese | evidência a favor/contra; conflito → abstenção |
| empírico | evidência real/complexa; irreal descontada |
| subjetivo | psicometria obrigatória; warrant ≤ 0,6 |

O grafo **liga e contrapõe** evidência; não inventa resultado.

## 4. Limites

- Dados sintéticos; nenhum participante, hardware ou calibração real.
- EMA e N-of-1 não substituem ética, consentimento, supervisão ou validação
  clínica.
- Brier/ECE medem calibração observada; não provam verdade ou causalidade.
- O pareamento claim↔prova/contraprova é editorial e exige revisão humana.
- O contrato de runtime não prova segurança jurídica nem ausência de efeitos.
- Nenhuma vantagem quântica, clínica ou epistêmica é declarada.

## 5. Reprodução

```bash
.venv-quantum/bin/python -m pytest tests/test_r1148_ema.py \
  tests/test_r1148_n_of_1.py tests/test_r1148_claims_graph.py \
  tests/test_r1148_trust_warrant.py tests/test_r1148_runtime_contract.py \
  tests/test_r1148_integration.py -q
```

Relatório: `harnesses/metacognition/r1148/summary.json`.
