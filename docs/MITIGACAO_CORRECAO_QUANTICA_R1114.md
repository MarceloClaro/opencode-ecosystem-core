# Mitigação e correção de erro quântico — R1114

**Status:** implementação local, offline/simulada
**Spec:** `specs/SPEC-935-R1114-quantum-error-mitigation-correction.md`
**Skill:** `.opencode/skills/mitigacao-e-correcao-quantica/SKILL.md`
**Harness:** `harnesses/quantum-error-mitigation/`
**Agentes:** `quantum-error-mitigation`, `quantum-error-correction`, `quantum-noise-characterization`

## 1. O que foi criado

| Técnica | Módulo | O que faz | Limite |
|---|---|---|---|
| ZNE | `quantum_mitigation/zne.py` | folding global e extrapolação linear/quadrática/exponencial | assume monotonicidade; não é QEC |
| PEC | `quantum_mitigation/pec.py` | quasi-probabilidades do canal depolarizante 1q e overhead γ² | 2q não implementado |
| DD | `quantum_mitigation/dd.py` | XY4/CPMG/echo circuit-level e verificação de identidade | não é schedule pulse-level |
| QEC | `quantum_mitigation/qec.py` | repetição de 3 qubits, síndrome e decodificador bit-flip | não protege fase; não é superfície |
| SPAM | `quantum_mitigation/characterization.py` | ajuste \|0>/\\|1> com `rx(pi)` | preparação e leitura parcialmente confundidas |
| Crosstalk | idem | erro isolado vs simultâneo | descritivo; não identifica mecanismo |
| Drift | idem | tendência linear e CUSUM | não corrige calibração |
| Incerteza | idem | Wilson e bootstrap | dispersão; não é significância universal |

## 2. O que cada agente pode fazer

| Agente | Comandos permitidos |
|---|---|
| `quantum-error-mitigation` | `zne*`, `dd*`, `pec*`, `audit*`, `lessons*` |
| `quantum-error-correction` | `qec*`, `audit*`, `lessons*` |
| `quantum-noise-characterization` | `spam*`, `crosstalk*`, `drift*`, `uncertainty*`, `audit*`, `lessons*` |

Todos usam o wrapper `harnesses/quantum-error-mitigation/agent_qem.py`. Eles
**não** executam hardware e não chamam `runner.py` diretamente. O hardware
permanece sob o primário, com gates e confirmação.

## 3. Comandos

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

## 4. Como isso responde às limitações do R1113

| Limitação R1113 | Resposta R1114 |
|---|---|
| \|11> usa `rx(pi)` e inclui preparação do \|1> | SPAM declara a confusão e planeja \|0>/\\|1>; não finge separar |
| Matriz 4×4 corrige 01/10, mas não state prep/crosstalk/deriva | DD, crosstalk e drift entram como caracterização/planejamento; ninguém promete correção total |
| Três repetições estimam dispersão | Wilson/bootstrap documentam a incerteza; não há prova universal |
| Loop registra lições | comando `lessons` lê `loop_state.json` e `loop_log.jsonl` |
| ZNE/PEC/DD/QEC ausentes | módulos, harness, skill e três agentes dedicados |

## 5. Limites

- Nenhum comando executa hardware.
- ZNE não é QEC; PEC 2q não está implementado.
- DD é circuit-level; não é schedule pulse-level.
- QEC de repetição não protege fase; não é superfície e não demonstra threshold.
- SPAM |11> inclui preparação do |1>.
- Crosstalk e drift são descritivos.
- Bootstrap/Wilson não provam significância universal.
- Nenhuma técnica elimina state preparation, crosstalk ou deriva.
- O loop registra lições; não promove confiança automaticamente.

## 6. Verificação

`tests/test_r1114_quantum_error_mitigation.py` cobre ZNE, DD, PEC, QEC, SPAM,
crosstalk, drift, incerteza, permissões dos agentes, wrapper, skill e
anti-overclaim. Nenhum teste executa hardware ou acessa rede.
