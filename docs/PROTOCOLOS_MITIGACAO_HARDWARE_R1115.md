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

## 6. Resultado 16 jobs — ZNE 4 escalas + tomografia

Backend Baihua, 4096 shots, gates SDD/TDD/simulação aprovados.

### 6.1 ZNE

| Escala | TVD vs Bell | Task ID |
|---:|---:|---|
| 1 | 0,0645 | `52b8c44d-f322-468e-b75a-eb9140b2d7cc` |
| 3 | 0,0747 | `52268fb6-bb0d-4680-8cb5-06a672ecb71c` |
| 5 | 0,0735 | `e947cb8c-7442-4f16-9dc2-e72d82ed53cd` |
| 7 | 0,0967 | `a605ab51-66dd-4c80-972c-acc70b0d9327` |

A curva continua **não monotônica**. Linear 0,0582 e quadrática 0,0671; não
há extrapolação válida nem ganho. O randomized compiling completo (Pauli-frame
twirling) não foi executado; apenas o plano foi preparado.

### 6.2 Tomografia SPAM

| Estado | Fidelidade de preparação | Comprimento de Bloch |
|---|---:|---:|
| 0 | 0,9875 | 0,9768 |
| 1 | 0,9292 | 0,8603 |
| + | 0,9824 | 0,9682 |
| +i | 0,9839 | 0,9697 |

Leitura: `r0 = P(1|prep0) = 0,0125` e `r1 = P(0|prep1) = 0,0708`.

A tomografia multi-base separou preparação e leitura sob a hipótese de
rotações de base ideais. O |1> tem a menor fidelidade/comprimento, compatível
com erro de preparação do `rx(pi)`. Não é GST completa: crosstalk e erros
coerentes nas rotações não são modelados.

### 6.3 Pré-registro

A execução foi pré-registrada com 4096 shots, confiança 95% e método Wilson
para as probabilidades; o `n` não foi ajustado após ver os dados. O ZNE não foi
usado para comparar layouts.

### 6.4 Conclusão

- Tomografia SPAM: **funcionou** como caracterização, com limites declarados.
- ZNE: **não aplicável** nesta curva; sem ganho.
- PEC 2q, superfície e DD pulse-level: planejamento, não executados.
- Nenhuma vantagem quântica é declarada.

## 7. Limites

- PEC 2q é planejamento; o perfil escalar assume depolarização uniforme.
- Superfície não é simulada; o orçamento não prova threshold.
- DD pulse-level não é executável na API atual.
- SPAM separation depende do modelo de pulsos independentes.
- ZNE extrapola TVD; não é fidelidade.
- Nenhuma técnica elimina state preparation, crosstalk ou deriva.
- Não há vantagem quântica demonstrada.
