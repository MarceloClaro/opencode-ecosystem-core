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

## Resultado R1115

No Baihua, ZNE não foi monotônica e o SPAM separation por pulsos π repetidos
não foi identificável. Não use a extrapolação ZNE como ganho nem os valores
e/r0/r1 como físicos. PEC 2q, superfície e DD pulse-level não foram executados.

## Limites

- Nenhum comando executa hardware.
- ZNE não é QEC; PEC 2q não está implementado.
- DD é circuit-level, não pulse-level.
- QEC de repetição não protege fase.
- SPAM |11> usa `rx(pi)` e inclui preparação do |1>.
- Crosstalk e drift são descritivos.
- Bootstrap/Wilson não provam significância universal.
- Nenhuma técnica elimina state preparation, crosstalk ou deriva.
