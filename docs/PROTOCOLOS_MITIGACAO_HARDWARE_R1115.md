# Protocolos de mitigação para hardware — R1115

**Status:** implementação local + validação de hardware no subconjunto viável
**Spec:** `specs/SPEC-935-R1115-hardware-mitigation-protocols.md`
**Harness:** `harnesses/quantum-error-mitigation/runner.py`
**Agentes:** `quantum-error-mitigation`, `quantum-error-correction`, `quantum-noise-characterization`

## 1. Matriz de viabilidade

| Item | Implementação | Baihua |
|---|---|---|
| ZNE no Bell | folding + extrapolação | **executável** |
| DD circuit-level | XY4/CPMG/echo | executável, mas sem janela ociosa longa |
| PEC 2q Pauli-Lindblad | inversão de canal Pauli | **planejamento**; não executado |
| QEC de superfície | orçamento + interface MWPM | **planejamento**; sem decodificador em tempo real |
| DD pulse-level | plano de timing | **bloqueado**; API sem pulso |
| SPAM separation | pulsos π repetidos | **executável** |
| Incerteza pré-registrada | Wilson/bootstrap | executável na análise |

## 2. Protocolo de hardware viável

### 2.1 Gates

1. SDD: spec R1115 e testes existem.
2. TDD: `pytest` R1114/R1115 passa.
3. Simulação: circuitos ZNE/SPAM simulam em Aer e preservam a distribuição
   ideal.
4. Hardware: `confirm=True`, `allow_hardware=True`, backend Baihua.

### 2.2 ZNE no Bell

- Circuito E05/Bell em q0/q1.
- Folding global: escalas **1, 3, 5**.
- 4096 shots por escala.
- Análise: TVD vs ideal por escala; extrapolação linear/quadrática para
  escala zero.
- 3 jobs.

### 2.3 SPAM separation

- Qubits q0 e q1.
- k = **1, 3, 5** pulsos `rx(pi)`; medir o qubit.
- 4096 shots por circuito.
- Ajuste do modelo:
  `P(1|k) = (1-r1) + p0(k)(r0-(1-r1))`,
  `p0(k) = (1+(1-2e)^k)/2`.
- 6 jobs.
- O modelo separa erro de pulso `e` de leitura `r0/r1` sob hipóteses
  declaradas; não separa crosstalk/drift.

### 2.4 Incerteza pré-registrada

```bash
runner.py preregister --p 0.92 --half-width 0.01
```

Retorna `n` para meia-largura Wilson. O número deve ser fixado antes da
execução; não ajustar depois de ver os dados.

## 3. O que não foi executado

- **PEC 2q:** o plano usa inversão de canal Pauli, mas a execução exige taxas
  por operador (Pauli-Lindblad) e amostragem alta; não foi submetida.
- **Superfície:** orçamento e interface de decodificador; o Baihua não oferece
  decodificador em tempo real.
- **DD pulse-level:** o runtime GJQ não expõe controle de pulso; o plano de
  timing é apenas planejamento.

## 4. Comandos

```bash
# ZNE
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py zne \
  --profile perfil.json --circuit E05 --scales 1 3 5 --shots 4096 --out resultados/zne

# SPAM plan + separation
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py spam-plan \
  --qubits 0 1 --ks 1 3 5 --out resultados/spam_plan
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py spam-separation \
  --counts counts_ks.json --out resultados/spam_sep

# PEC 1q/2q
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py pec \
  --profile perfil.json --circuit E05 --out resultados/pec

# superfície
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py surface \
  --distance 3 --rounds 3 --p 0.001 --out resultados/surface

# DD pulse-level
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py dd-pulse \
  --t1-us 70 --t2-us 20 --idle-us 10 --sequence cpmg --out resultados/dd_pulse

# pré-registro
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py preregister \
  --p 0.92 --half-width 0.01 --out resultados/prereg
```

## 5. Resultado de hardware — Baihua, 9 jobs

Gates SDD/TDD/simulação aprovados. 4096 shots por circuito.

### 5.1 ZNE

| Escala | TVD vs Bell | Task ID |
|---:|---:|---|
| 1 | 0,0706 | `cfff51d4-072a-45e6-9fbd-4ba62d4c4527` |
| 3 | 0,1003 | `bdb63435-5517-427a-ab6b-3d4cf4758738` |
| 5 | 0,0671 | `08f5e45e-fba4-44ad-b030-79b29cdf9f24` |

A curva **não é monotônica**. A extrapolação linear deu 0,0819 e a quadrática
0,0320; elas divergem. Não há extrapolação válida nem ganho de mitigação.

### 5.2 SPAM separation

| Qubit | P1(k=1) | P1(k=3) | P1(k=5) | Identificado? |
|---|---:|---:|---:|---|
| q0 | 0,9331 | 0,9233 | 0,9248 | **False** |
| q1 | 0,9255 | 0,9248 | 0,9302 | **False** |

O ajuste caiu em um limite (e≈0,5, r0≈0,5, r1≈0) e o resíduo foi alto. Os
valores de e/r0/r1 **não são físicos** e não devem ser usados. O protocolo de
pulsos π repetidos não separa preparação de leitura neste hardware.

### 5.3 Task IDs SPAM

| Qubit | k | Task ID |
|---|---:|---|
| q0 | 1 | `0488c599-9d5b-47ab-9858-e8c4a44da4af` |
| q0 | 3 | `3ea01899-2ed6-46e6-bf93-8d69692d4ec6` |
| q0 | 5 | `68316e94-b256-4823-83df-08ebf76f542f` |
| q1 | 1 | `a147c708-e903-49ae-808f-c22876b4bc70` |
| q1 | 3 | `b4dea322-d531-446a-86fd-e69a4c2895a5` |
| q1 | 5 | `78835f36-9c5e-4b2b-9a8b-c98e598123e6` |

### 5.4 Conclusão

O protocolo foi executado, mas os modelos simples falharam. Isso é evidência
negativa, não ganho. Para separar state preparation de readout, o próximo
passo é tomografia/GST com bases múltiplas. PEC 2q, superfície e DD
pulse-level permanecem em planejamento.

## 6. Limites

- PEC 2q é planejamento; o perfil escalar assume depolarização uniforme.
- Superfície não é simulada; o orçamento não prova threshold.
- DD pulse-level não é executável na API atual.
- SPAM separation depende do modelo de pulsos independentes.
- ZNE extrapola TVD; não é fidelidade.
- Nenhuma técnica elimina state preparation, crosstalk ou deriva.
- Não há vantagem quântica demonstrada.
