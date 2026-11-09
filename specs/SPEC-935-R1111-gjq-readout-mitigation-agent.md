# SPEC-935-R1111 — Agente dedicado de mitigação de leitura GJQ

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1109 (otimizador GJQ), R1110 (comparação e mitigação)

## 1. Contexto

O R1110 implementou a comparação baseline vs otimizado e a mitigação de
leitura, mas o agente `gjq-hardware-optimizer` é `managed-v1` e só pode rodar
`doctor` e o próprio teste. O operador autorizou um agente dedicado com
permissão específica para **planejar a comparação** e **mitigar leitura
offline**, mantendo a submissão de hardware sob confirmação do primário.

## 2. Requisitos

- **R1.** Criar o agente `gjq-readout-mitigation` em `managed-v1`.
- **R2.** Permitir no `bash` apenas:
  - `python3 -m marceloclaro.cli doctor`;
  - `python3 -m pytest tests/test_r1111_gjq_readout_mitigation_agent.py -q`;
  - `.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py compare-plan*`;
  - `.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py mitigate*`.
- **R3.** Negar `runner.py run`, `runner.py compare` direto e qualquer
  submissão de hardware.
- **R4.** Criar o wrapper `harnesses/gjq-hardware-optimizers/agent_readout.py`
  que só mapeia `compare-plan` para `runner.py compare --plan` e `mitigate`
  para `runner.py mitigate`; qualquer outro comando retorna bloqueio.
- **R5.** `compare --plan` deve gerar `plano_comparacao.json` com QASM2/QASM3,
  calibração |00>/|11>, hash do plano e `hardware_executed=false`, sem job.
- **R6.** `mitigate` deve aplicar a matriz 2x2 informada ou a matriz do perfil,
  com clipping, renormalização, auditoria e relatório, sem rede.
- **R7.** Criar testes de contrato, permissão, wrapper, plano e mitigação.
- **R8.** Não expor segredo nem declarar fidelidade, vantagem quântica ou
  submissão autônoma.

## 3. Permissão

A política de lifecycle recebe uma exceção explícita para o ID
`gjq-readout-mitigation`:

```text
*: deny
python3 -m marceloclaro.cli doctor: allow
python3 -m pytest tests/test_r1111_gjq_readout_mitigation_agent.py -q: allow
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py compare-plan*: allow
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py mitigate*: allow
```

O wrapper é a segunda barreira: mesmo que a permissão de glob seja ampla, ele
rejeita `run`, `compare` direto e qualquer comando fora de `compare-plan` e
`mitigate`.

## 4. Fluxo

### 4.1 Planejar

```bash
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py compare-plan \
  --profile perfil.json --circuit E05 --shots 4096 --quick --calibrate \
  --out resultados/plano
```

Saída: `plano_comparacao.json` com:

- backend, shots, estratégia, seed e fingerprint;
- baseline e otimizado: QASM2/QASM3, layout, métricas e estimativa;
- calibração |00>/|11> em QASM2;
- `submissions_estimated` (6 com calibração, 2 sem);
- `plan_sha256`;
- `hardware_executed=false`.

### 4.2 Mitigar

```bash
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py mitigate \
  --counts counts.json --profile perfil.json \
  --qubits 107,106 --matrix matriz.json --shots 4096 \
  --out resultados/mitigacao
```

Saída: `mitigacao.json` e `RELATORIO_MITIGACAO.md` com raw, mitigado, matriz,
condição, massa negativa, leakage e auditoria.

## 5. Submissão de hardware

O agente **não** executa:

- `runner.py run`;
- `runner.py compare` sem `--plan`;
- qualquer comando que chame `Sampler.run`.

O primário revisa o plano e executa:

```bash
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py compare \
  --backend Baihua --circuit E05 --shots 4096 --quick \
  --confirm --allow-hardware --calibrate ...
```

## 6. Critérios de aceitação

- agente validado por `validate_managed_card`;
- permissão contém apenas doctor, pytest, `compare-plan*` e `mitigate*`;
- `run` e `compare` direto retornam bloqueio;
- plano não cria counts nem submete job;
- mitigação offline reproduz os valores do R1110;
- testes R1111 passam sem rede;
- `opencode.json` contém o agente;
- nenhum segredo ou overclaim.

## 7. Não objetivos

- Submissão de hardware pelo próprio agente.
- Bypass do primário.
- Mitigação completa de state preparation, crosstalk ou leakage 01/10.
- Declarar fidelidade ou vantagem quântica.

## 8. Riscos

- **Glob excessivo:** mitigado pelo wrapper.
- **Plano obsoleto:** o plano registra fingerprint e data; o primário deve
  reler a calibração antes de executar.
- **Mitigação parcial:** a inversão 00/11 não corrige 01/10; |11> usa `rx(pi)`.
- **Overclaim:** uma execução de 4096 shots não é estudo estatístico.
