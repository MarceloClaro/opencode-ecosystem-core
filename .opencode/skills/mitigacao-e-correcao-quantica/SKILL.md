---
name: mitigacao-e-correcao-quantica
description: Integra ZNE, PEC, DD, QEC, SPAM, crosstalk, drift e incerteza ao Core com planejamento, simulação e auditoria; não executa hardware, não declara threshold, fidelidade ou vantagem sem evidência.
metadata:
  version: "1"
  origem: "R1114 — mitigação e correção de erro quântico"
---

# Mitigação e correção de erro quântico

## Quando usar

Use para **planejar, simular e auditar** ZNE, PEC, DD, QEC, SPAM, crosstalk,
drift e incerteza. Para executar em hardware, o primário precisa de gates,
`confirm=True` e `allow_hardware=True`; esta skill não executa hardware.

## Contrato

1. **Declare a técnica e o modelo.** ZNE assume relação monotônica; PEC exige
   quasi-probabilidades; DD circuit-level não é pulse-level.
2. **Separe mitigação de correção.** ZNE/PEC/DD mitigam; QEC codifica. Nenhum
   deles garante fault tolerance.
3. **Registre overhead.** PEC cresce com `γ²`; DD adiciona portas; QEC adiciona
   qubits e síndromes.
4. **Não declare threshold.** O código de repetição 3 qubits não é superfície
   nem prova de threshold.
5. **Não declare fidelidade.** Métricas de TVD, erro lógico e SPAM não são
   fidelidade de estado.
6. **Incerteza é dispersão.** Três repetições não são prova estatística
   universal.

## Técnicas

| Técnica | Implementação | Limite |
|---|---|---|
| ZNE | folding global + extrapolação linear/quadrática/exponencial | assume monotonicidade; não é QEC |
| PEC | quasi-probabilidades do canal depolarizante 1q | 2q não implementado; overhead γ² |
| DD | XY4/CPMG/echo circuit-level | não é schedule pulse-level |
| QEC | repetição 3 qubits para bit-flip | não protege fase; não é superfície |
| SPAM | \|0> e \|1> com rx(pi) | preparação e leitura parcialmente confundidas |
| Crosstalk | erro isolado vs simultâneo | descritivo; não identifica mecanismo |
| Drift | tendência e CUSUM | não corrige calibração |
| Incerteza | Wilson/bootstrap | dispersão, não significância universal |

## Comandos

```bash
# ZNE
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py zne \
  --profile perfil.json --circuit E05 --scales 1 3 5 --shots 2048 --out resultados/zne

# DD
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py dd \
  --circuit E05 --qubits 0 1 --sequence xy4 --out resultados/dd

# PEC 1q
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py pec \
  --profile perfil.json --circuit E05 --out resultados/pec

# QEC repetição
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py qec \
  --p 0.01 --shots 20000 --out resultados/qec

# SPAM
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py spam \
  --counts0 counts0.json --counts1 counts1.json --out resultados/spam

# crosstalk, drift, incerteza
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py crosstalk \
  --isolated 0.01 --simultaneous 0.02 --out resultados/crosstalk
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py drift \
  --values 0.010 0.011 0.013 0.016 0.020 --out resultados/drift
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py uncertainty \
  --values 0.020 0.025 0.022 0.024 --out resultados/uncertainty

# lições do loop
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py lessons \
  --loop-state loop_state.json --out resultados/lessons
```

## Agentes

| Necessidade | Agente |
|---|---|
| ZNE, PEC, DD | `quantum-error-mitigation` |
| QEC e síndromes | `quantum-error-correction` |
| SPAM, crosstalk, drift, incerteza | `quantum-noise-characterization` |
| Auditoria de claim | `quantum-benchmark-audit` |

## Calibração Rabi

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/hardware_rabi_calibration.py \
  --qubit 1 --shots 4096 --confirm --allow-hardware --use-cached-account
```

16 jobs (8 ângulos × 2 eixos) ajustam `p1(θ) = r0 + A·sin²((θ+ε)/2)` e separam
leitura de desvio coerente. Em q1: ε(rx) = −0,0006 ± 0,0091 rad;
ε(ry) = +0,0012 ± 0,0129 rad; nenhum desvio acima de 2σ; r1 0,0695–0,0786.
Não corrigir o ângulo do π; priorizar leitura.

## Scorecard híbrido

O comando `resilience` combina readout 4x4, tomografia q0/q1, ZNE, PEC e
incerteza para recomendar o próximo passo e listar técnicas bloqueadas:

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py resilience \
  --readout comparacao.json --zne zne.json \
  --tomography-q0 comparison.json --tomography-q1 comparison.json \
  --comparison comparison_q0_q1.json \
  --rabi rabi_q1.json \
  --pec pec.json --surface --pulse-dd
```

No run simétrico (2 conjuntos por qubit): ZNE bloqueado por não monotonicidade;
Δ r1 q1−q0 = +0,0072, mas ICs se sobrepõem e o Δ é menor que o spread entre
conjuntos, então a diferença não é conclusiva. `prep |0>/|1>` e `r0/r1` são a
mesma contagem Z; a preparação independente de readout é medida por `|+>` e
`|+i>`. Superfície e DD pulse-level bloqueados; PEC 2q com 15 taxas não
caracterizadas.

## Resultado R1115

No Baihua, ZNE continuou não monotônica mesmo com 4 escalas; não use a
extrapolação como ganho. O SPAM por pulsos π repetidos falhou, mas a
tomografia multi-base (4 estados x 3 bases) separou preparação e leitura sob
hipóteses declaradas. PEC 2q, superfície e DD pulse-level não foram executados.

## Limites

- Nenhum comando executa hardware.
- ZNE não é QEC; PEC 2q não está implementado.
- DD é circuit-level, não pulse-level.
- QEC de repetição não protege fase.
- SPAM |11> usa `rx(pi)` e inclui preparação do |1>.
- Crosstalk e drift são descritivos.
- Bootstrap/Wilson não provam significância universal.
- Nenhuma técnica elimina state preparation, crosstalk ou deriva.
