# SPEC-935-R1112 — Engenharia de loop para GJQ

**Status:** implementação local + loop real no Baihua
**Data:** 2026-11-09
**Depende de:** R1109 (otimizador), R1110 (comparação/mitigação), R1111 (agente dedicado)

## 1. Contexto

O R1110 mostrou que o proxy de erro não confirmou o ranking no hardware e que a
mitigação 00/11 reduziu a TVD, mas não separou completamente readout de
preparação. O operador autorizou transformar o fluxo em um **loop
auditável**: SDD → TDD → simulação → hardware → mitigação → score/reflexão,
com estado durável e próxima ação explícita.

## 2. Requisitos

- **R1.** Criar `gjq_hardware_opt/loop.py` com estado, gates, score, relatório
  e log.
- **R2.** Criar `gjq_hardware_opt/simulation.py` para simular o plano com
  modelo depolarizante derivado do perfil.
- **R3.** Criar `harnesses/gjq-hardware-optimizers/loop_runner.py` com
  `plan`, `simulate`, `execute`, `score`, `run`, `status` e `report`.
- **R4.** `plan` deve chamar `compare --plan` e não submeter job.
- **R5.** O gate SDD confere specs e testes; o gate TDD executa `pytest`.
- **R6.** O gate de simulação remapeia qubits físicos para locais, monta modelo
  de ruído, confere equivalência ideal (`TVD <= 1e-9`) e registra a TVD
  ruidosa; não pode ser usado como previsão de hardware.
- **R7.** `execute` só roda com SDD, TDD e simulação aprovados, `--confirm` e
  `--allow-hardware`; usa `runner.py compare` com `transpile=False`.
- **R8.** `score` compara proxy, raw e mitigado; registra lição e próxima ação;
  não promove confiança automaticamente.
- **R9.** O loop salva `loop_state.json`, `loop_log.jsonl`,
  `simulacao.json`, `comparacao/` e `RELATORIO_LOOP.md`.
- **R10.** O agente `gjq-readout-mitigation` pode rodar o loop via wrapper
  `agent_readout.py loop-plan*`, `loop-simulate*`, `loop-execute*`,
  `loop-score*`, `loop-run*`, `loop-status*` e `loop-report*`.
- **R11.** Testes R1112 sem rede e sem submissão; o gate TDD do teste usa um
  teste temporário para evitar recursão.
- **R12.** Não declarar fidelidade, vantagem quântica, superioridade do layout
  ou execução autônoma sem gates.

## 3. Fluxo

```text
plan -> SDD -> TDD -> simulate -> [hardware: confirm+allow] -> score -> report
```

- `plan`: gera baseline, otimizado, calibração |00>/|11> em QASM2/QASM3.
- `SDD`: specs e testes existem e têm conteúdo mínimo.
- `TDD`: pytest passa.
- `simulate`: equivalência ideal e TVD ruidosa com modelo do perfil.
- `hardware`: `runner.py compare` com `--confirm --allow-hardware`.
- `score`: proxy vs raw vs mitigado; lição e próxima ação.

## 4. Estado e orçamento

O estado contém:

- `loop_id`, backend, perfil, circuito, shots, iteração;
- gates SDD/TDD/simulação/hardware;
- caminhos de plano, simulação, comparação e relatório;
- histórico, melhor resultado, lições;
- submissões estimadas e usadas;
- timestamps.

O orçamento de submissões é registrado; o loop não reenvia o mesmo circuito
sem necessidade. O `execute` usa o `compare` que já contém os gates de
`confirm` e `allow_hardware`.

## 5. Critérios de aceitação

- `loop plan --profile` gera plano sem job;
- `loop simulate` executa SDD, TDD e simulação;
- `loop execute` bloqueia sem gates ou sem confirmação;
- `loop run` sem `--confirm` para após a simulação;
- `loop score` gera lição e próxima ação;
- `RELATORIO_LOOP.md` contém gates, simulação, hardware, score e limites;
- testes R1112 passam sem rede;
- agente tem permissão para os comandos do loop via wrapper;
- nenhuma chave em arquivo;
- nenhuma alegação de fidelidade ou vantagem.

## 6. Não objetivos

- Submissão de hardware sem gates.
- Previsão de fidelidade por simulação.
- Estudo estatístico com uma execução.
- ZNE, PEC, DD ou correção quântica de erro.
- Promover confiança automaticamente.

## 7. Riscos

- **Simulação não preditiva:** o modelo depolarizante pode favorecer um layout
  que o hardware não confirma.
- **Calibração instável:** |11> tem leakage alto e inclui `rx(pi)`.
- **Amostra pequena:** uma execução por caso.
- **Permissão:** o wrapper é a barreira; o agente não chama `runner.py run`.
- **Custo:** 6 submissões por iteração com calibração.

## 8. Testes

`tests/test_r1112_gjq_loop_engineering.py` verifica:

- gates SDD/TDD com teste temporário;
- simulação com plano real e perfil real;
- plano offline sem jobs;
- `loop run` sem confirmação para na simulação;
- `loop execute` bloqueado sem gates/confirm;
- score e relatório;
- permissões do agente e wrapper;
- ausência de segredos e overclaim.
