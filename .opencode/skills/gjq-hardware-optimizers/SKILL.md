---
name: gjq-hardware-optimizers
description: Otimiza circuitos para o hardware real da GJQ (Baihua e aliases) usando o Target e a calibração ao vivo, layout noise-aware, QASM2/QASM3, comparação baseline vs otimizado, mitigação de leitura e engenharia de loop SDD/TDD/simulação/hardware. Use para perfil, otimização, benchmark, comparação, mitigação, loop e execução real; não declara fidelidade, vantagem quântica ou emaranhamento como provados.
metadata:
  version: "1"
  origem: "R1109 — otimizadores para hardware GJQ"
---

# Otimizadores para hardware GJQ

## Quando usar

Use quando o pedido envolver **executar ou otimizar um circuito para hardware
real da GJQ**, em especial o Baihua. Para E01–E18, combine com
`gjq-experimentos-quanticos`; para pesquisa geral, combine com
`gjq-pesquisa-quantica`.

Não use para declarar fidelidade, emaranhamento, vantagem quântica ou
interpretação de Bohm a partir de counts.

## Contrato

1. **Perfil real.** Ler `backend.configuration()`, `backend.properties()` e
   `backend.target`. Não inventar acoplamentos, portas base ou erros.
2. **Filtro.** Remover arestas com erro sentinela `>= 0.999`, qubits com erro
   1q `>= 0.05` e arestas fora do `coupling_map` operacional.
3. **Simetria.** `cz`, `swap` e `iswap` recebem as duas direções.
4. **Layout.** O layout noise-aware pondera 1q, medição e arestas 2q; escolhe
   uma região física conectada; o baseline é trivial-operacional.
5. **Correção.** O circuito escolhido usa apenas portas base e arestas do
   perfil; a numeração física é preservada.
6. **Submissão.** `confirm=True`, `allow_hardware=True` para hardware e
   `transpile=False`. Sem dupla transpilação.
7. **Proveniência.** Salvar task ID, backend, shots, timestamps, hashes,
   counts e auditoria da soma.
8. **Sem overclaim.** `success_proxy` é produto de `(1 - erro)` por porta e
   leitura, não fidelidade.

## Comandos

```bash
# perfil ao vivo
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py profile \
  --backend Baihua --out resultados/baihua

# otimizar sem submeter
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py optimize \
  --backend Baihua --circuit E05 --strategy balanced --quick --out resultados/E05

# benchmark sem submeter
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py benchmark \
  --backend Baihua --set experiments --only E05 E06 E12 --quick --out resultados/bench

# executar no hardware real
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py run \
  --backend Baihua --circuit E05 --shots 1024 --quick --strategy balanced \
  --confirm --allow-hardware --wait --timeout 600 --poll 5 \
  --out resultados/E05_execucao

# comparar baseline vs otimizado + calibrar |00>/|11> + mitigar leitura
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py compare \
  --backend Baihua --circuit E05 --shots 4096 --quick \
  --confirm --allow-hardware --calibrate \
  --out resultados/E05_comparacao

# reler o resultado sem reenviar
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py result \
  --backend Baihua --task-id <TASK_ID> --shots 1024 --out resultados/E05_execucao

# auditar counts locais
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py audit \
  --counts counts.json --shots 1024
```

Sem `GJQ_API_KEY`, use `--use-cached-account` para a conta que o SDK já
cacheou em `~/.gjq_client/gjq_client_account.json`. O flag é explícito e não
lê nem imprime a chave.

## Agente dedicado

O agente `gjq-readout-mitigation` é `managed-v1` e tem permissão apenas para
`doctor`, o próprio teste e o wrapper:

```bash
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py compare-plan ...
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py mitigate ...
```

Ele não executa `runner.py run` nem `runner.py compare` direto. O wrapper
rejeita esses comandos. A submissão de hardware permanece no primário, com
`--confirm` e `--allow-hardware`.

## Loop

```bash
# plano + SDD + TDD + simulação (sem hardware)
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/loop_runner.py run \
  --backend Baihua --circuit E05 --shots 8192 --repetitions 3 --full-calibration \
  --quick --use-cached-account --out resultados/E05_loop

# ciclo completo com hardware após os gates
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/loop_runner.py run \
  --backend Baihua --circuit E05 --shots 8192 --repetitions 3 --full-calibration \
  --confirm --allow-hardware --use-cached-account \
  --out resultados/E05_loop
```

O `loop-run` sem `--confirm` para depois da simulação. O `loop-execute`
bloqueia sem SDD, TDD, simulação, `--confirm` e `--allow-hardware`. A simulação
usa modelo depolarizante do perfil e **não** prevê o hardware.

## Mitigação de leitura

O comando `compare` mede |00> e |11> nos mesmos qubits do baseline e do
otimizado, constrói a submatriz 00/11 e inverte:

```text
p_mit = A^{-1} p_obs
```

Massas negativas são clipadas e o vetor é renormalizado. A matriz 00/11 não
corrige a população que sai para 01/10: o leakage é reportado separadamente.
No Baihua, o leakage de |11> ficou em 14–15%, muito acima do `readout_error`
reportado (0,1–0,2%). A TVD mitigada não é fidelidade.

## Gates

- [ ] credencial disponível (ambiente ou cache explícito);
- [ ] `confirm=True`;
- [ ] `allow_hardware=True` para Baihua/Guoji/Yudu;
- [ ] `1 <= shots <= 100000`;
- [ ] circuito com medição;
- [ ] `transpile=False`;
- [ ] task ID e auditoria;
- [ ] nenhuma chave em arquivo, log ou relatório.

## Limites

- Uma execução não prova fidelidade, emaranhamento, vantagem quântica ou
  interpretação de Bohm.
- A fração `00`/`11` é taxa de outcomes correlacionados, não fidelidade.
- O proxy de erro não é calibração; no Baihua ele foi otimista frente à TVD
  observada e o ranking baseline vs otimizado não se confirmou no hardware.
- A mitigação 00/11 não corrige leakage para 01/10; a TVD mitigada não é
  fidelidade de estado.
- A calibração muda; releia as propriedades antes de comparar execuções.
- Não há mitigação de erro (ZNE/PEC/DD) nesta versão.
- Custo, fila e disponibilidade mudam; o snapshot não é garantia.
