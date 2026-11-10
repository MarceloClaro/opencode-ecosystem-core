# R1147 — Correlações, arranjos e contraprovas

**Status:** implementação local; nenhum hardware executado.
**Artefatos:** `harnesses/quantum-error-mitigation/resultados/r1147_correlation_layout/`.

## 1. A correlação nova

Além da marginal `p_i`, o Core mede a co-ocorrência `p_ij` e o coeficiente

```
phi_ij = (p_ij - p_i p_j) / sqrt(p_i(1-p_i) p_j(1-p_j))
```

Duas tabelas com **as mesmas marginais** (0,15 em cada qubit) podem ter juntas
opostas:

| Tabela | `p00` | `p01` | `p10` | `p11` | `phi` | `P(0 erro)` | `P(≥1)` |
|---|---:|---:|---:|---:|---:|---:|---:|
| A correlacionada | 0,8000 | 0,0500 | 0,0500 | 0,1000 | **0,608** | **0,8000** | **0,2000** |
| B independente | 0,7225 | 0,1275 | 0,1275 | 0,0225 | 0,000 | 0,7225 | 0,2775 |

Consequência: o modelo independente **subestima** a fidelidade e o erro duplo,
mas **superestima** a união de erros. A direção do erro depende do estatístico.
Nenhuma decisão de mitigação ou layout deve usar apenas marginais.

## 2. Simulação com correlação latente

4 qubits, 50.000 shots, marginais 0,08:

| Modelo | `max |phi|` | `P(≥1 erro)` | delta vs independente |
|---|---:|---:|---:|
| `rho = 0,6` | 0,304 | 0,1964 | **−0,0831** |
| `rho = 0,0` | 0,008 | 0,2824 | ≈ 0 |

O estimador recupera a correlação positiva e mostra a inversão do sinal.

## 3. Arranjos: trade-off entre porta e correlação

Dispositivo de 6 qubits (anel + cordas), leitura 0,03, interações com pesos
3, 2, 1, 1, 1. Pares com `phi = 0,5` em (0,1), (2,3), (4,5).

| Arranjo | Custo total | Porta | Leitura | Correlação |
|---|---:|---:|---:|---:|
| Só marginais (`marginal_only`) | **1,780** | 0,100 | 0,180 | **1,500** |
| Ciente da correlação | **1,320** | 0,140 | 0,180 | **1,000** |

O arranjo ciente aceita **+0,040 de custo de porta** para remover **0,500 de
penalidade de correlação**; líquido **−0,460**. O arranjo ótimo não é universal:
depende do modelo de ruído.

Contraprova limpa: dispositivo completo com portas iguais; layout cego paga
**1,522** e o ciente **0,322** (delta **1,200**), com porta e leitura idênticas.

## 4. Contraprovas de otimização

| Contraprova | Resultado |
|---|---|
| Greedy vs. exaustão (5 qubits) | greedy **3,0087** pior que o ótimo |
| Reversão de regime (A ótimo em A) | **0,441** pior em B; **4,01×** o custo do ótimo de B |
| Layout cego à correlação | **+1,200** de custo de correlação |
| Marginais iguais | juntas diferentes; `phi` 0,608 vs 0 |

## 5. Contraprova formal (Lean 4 + Mathlib)

`lean/quantum-cb/CorrelationCounterproof.lean` — **10 teoremas
kernel-checked**, apenas `propext`, `Classical.choice`, `Quot.sound`.

| Teorema | Conteúdo |
|---|---|
| `marginals_equal` | as duas tabelas têm marginais iguais |
| `joints_differ` | as juntas diferem |
| `covariance_A_positive` | covariância positiva em A |
| `covariance_B_not_positive` | covariância não positiva em B |
| `no_error_A_gt_B` | correlação aumenta `P(0 erro)` |
| `double_error_A_gt_B` | correlação aumenta `P(2 erros)` |
| `any_error_A_lt_B` | correlação diminui `P(≥1 erro)` |
| `any_error_direction_reverses` | a direção se inverte |
| `union_bound_not_tight` | cota de união 0,7 < 0,8 |
| `marginals_do_not_determine_joint` | síntese |

Gate: **4/4 alegações aceitas**, 0 bloqueadas. Certificado:
`harnesses/quantum-error-mitigation/resultados/r1147_correlation_layout/certificate.json`
SHA-256 `182cc5f1a86a3f1c87d3259ea95b6e4d51598a9e483d3a191ec1c84fcf6f6273`.

## 6. Limites

- Counts sintéticos; nenhuma calibração real, crosstalk medido ou hardware.
- Só correlação de pares (`phi`); ordem superior não é modelada.
- Custo de layout é proxy; não prevê fidelidade.
- O pareamento alegação↔contraprova é editorial.
- Nenhuma vantagem quântica é alegada; aceitar o gate não promove confiança.

## 7. Reprodução

```bash
.venv-quantum/bin/python -m pytest tests/test_r1147_correlation_layout.py -q
.venv-quantum/bin/python -m quantum_mitigation.correlation_gate
RUN_LEAN_CORRELATION=1 .venv-quantum/bin/python \
  -m pytest tests/test_r1147_correlation_gate.py -q
```
