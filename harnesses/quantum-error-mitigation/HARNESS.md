# HARNESS — Mitigação e correção de erro quântico (R1114)

**Objetivo:** planejar, simular e auditar ZNE, PEC, DD, QEC, SPAM, crosstalk,
drift e incerteza.

**Não faz:** não executa hardware, não instala dependências, não acessa rede,
não declara threshold, fidelidade ou vantagem.

## Comandos

| Comando | O que faz |
|---|---|
| `zne` | folding e extrapolação ZNE em simulação |
| `dd` | plano DD circuit-level com verificação de identidade |
| `pec` | planejador PEC 1q com overhead |
| `qec` | repetição de 3 qubits com síndrome e decodificador |
| `spam` | ajuste \|0>/\\|1> |
| `crosstalk` | métrica isolado vs simultâneo |
| `drift` | tendência linear e CUSUM |
| `uncertainty` | Wilson/bootstrap |
| `lessons` | extrai lições do `loop_state.json` |
| `audit` | auditoria lexical de overclaim |

## Exemplos

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py zne \
  --profile perfil.json --circuit E05 --scales 1 3 5 --shots 2048 --out resultados/zne

.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py qec \
  --p 0.01 --shots 20000 --out resultados/qec

.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py lessons \
  --loop-state loop_state.json --out resultados/lessons
```

## Agentes

| Agente | Comandos |
|---|---|
| `quantum-error-mitigation` | `zne*`, `dd*`, `pec*`, `audit*`, `lessons*` |
| `quantum-error-correction` | `qec*`, `audit*`, `lessons*` |
| `quantum-noise-characterization` | `spam*`, `crosstalk*`, `drift*`, `uncertainty*`, `audit*`, `lessons*` |

O wrapper é `agent_qem.py`. Nenhum agente executa hardware.

## Gates

- [ ] ZNE declara folding e método de extrapolação;
- [ ] PEC 2q é explicitamente não implementado;
- [ ] DD é circuit-level;
- [ ] QEC é repetição bit-flip, não superfície;
- [ ] SPAM declara `rx(pi)` e preparação do |1>;
- [ ] crosstalk/drift são descritivos;
- [ ] bootstrap/Wilson não são significância universal;
- [ ] nenhuma chave em arquivo.

## Calibração Rabi da preparação

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/hardware_rabi_calibration.py \
  --qubit 1 --shots 4096 --confirm --allow-hardware --use-cached-account
.venv-quantum/bin/python harnesses/quantum-error-mitigation/hardware_rabi_calibration.py \
  --qubit 1 --analyze
```

16 jobs (8 ângulos × 2 eixos). Em q1: ε(rx) = −0,0006 ± 0,0091 rad;
ε(ry) = +0,0012 ± 0,0129 rad; eixo preferido `none`; r1 0,0695–0,0786.
Nenhum desvio coerente acima de 2σ; o erro dominante é leitura. O comando não
declara melhora sem validação.

## Scorecard híbrido

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py resilience \
  --readout comparacao.json --zne zne.json \
  --tomography-q0 comparison.json --tomography-q1 comparison.json \
  --comparison comparison_q0_q1.json \
  --rabi rabi_q1.json \
  --pec pec.json --surface --pulse-dd
```

Combina técnicas e aponta bloqueios/recomendações. Não executa hardware.

## Validação de hardware R1115

No Baihua (q0/q1, 4096 shots, 9 jobs):

- ZNE escalas 1/3/5: TVD 0,0706 / 0,1003 / 0,0671; não monotônica; extrapolações
  linear 0,0819 e quadrática 0,0320 divergem; sem ganho.
- SPAM por pulsos π repetidos: P1≈0,93 constante; ajuste não identificável.
- Tomografia multi-base (16 jobs, 4096 shots): fidelidades 0,9875 / 0,9292 /
  0,9824 / 0,9839; r0=0,0125 e r1=0,0708.
- ZNE 4 escalas: TVD 0,0645 / 0,0747 / 0,0735 / 0,0967; ainda não monotônica.
- Tomografia q1 (2 conjuntos): |1> 0,9163 [0,9100; 0,9221]; r1 0,0837
  [0,0779; 0,0900].
- Tomografia q0 (2 conjuntos): |1> 0,9235 [0,9178; 0,9290]; r1 0,0765
  [0,0710; 0,0822].
- Δ q1−q0: r1 +0,0072; ICs se sobrepõem e Δ < spread entre conjuntos; não
  conclusivo. `prep |0>/|1>` e `r0/r1` são a mesma contagem Z.
- PEC 2q, superfície e DD pulse-level não foram executados.

## Limites

- ZNE não é QEC; PEC 2q não está implementado.
- DD não é schedule pulse-level.
- QEC de repetição não protege fase.
- Nenhuma técnica elimina state preparation, crosstalk ou deriva.
- O loop registra lições; não promove confiança automaticamente.
