# Engenharia de loop para GJQ — R1112

**Status:** implementação local + loop real no Baihua
**Spec:** `specs/SPEC-935-R1112-gjq-loop-engineering.md`
**Módulos:** `gjq_hardware_opt/loop.py`, `gjq_hardware_opt/simulation.py`
**Runner:** `harnesses/gjq-hardware-optimizers/loop_runner.py`
**Agente:** `gjq-readout-mitigation` (via `agent_readout.py`)

## 1. O que o loop faz

O loop transforma a comparação isolada em um ciclo auditável:

```text
plan → SDD → TDD → simulate → hardware → mitigate → score → report
```

Cada etapa grava estado e evidência:

| Etapa | Arquivo | O que prova |
|---|---|---|
| `plan` | `plan/plano_comparacao.json` | QASM2/QASM3, calibração, hash, nenhum job |
| SDD | `loop_state.json` | specs e testes existem |
| TDD | `simulacao.json` | pytest passou |
| simulação | `simulacao.json` | equivalência ideal e TVD ruidosa |
| hardware | `comparacao/comparacao.json` | task IDs, counts, auditoria |
| mitigação | `comparacao/` | matriz, leakage, TVD mitigada |
| score | `loop_state.json` | proxy vs raw vs mitigado, lição, próxima ação |

## 2. Gates

- **SDD:** specs R1112 e R1110 existem e têm critérios de aceitação; testes
  existem.
- **TDD:** `pytest` nos testes indicados retorna 0.
- **Simulação:** remapeia qubits físicos para locais, monta modelo
  depolarizante por porta/leitura, exige equivalência ideal `TVD <= 1e-9` e
  registra a TVD ruidosa.
- **Hardware:** só roda com SDD, TDD e simulação aprovados, `--confirm` e
  `--allow-hardware`. Usa `runner.py compare` com `transpile=False`.
- **Mitigação:** matriz 00/11 por calibração |00>/|11>, inversão, clipping e
  renormalização.

A simulação **não** é previsão de hardware. No teste local, o modelo
depolarizante favoreceu o layout otimizado, mas o hardware anterior favoreceu
o baseline. O loop registra a divergência em vez de escondê-la.

## 3. Comandos

```bash
# plano + SDD + TDD + simulação (sem hardware)
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/loop_runner.py run \
  --backend Baihua --circuit E05 --shots 2048 --quick \
  --use-cached-account \
  --out resultados/E05_loop

# plano + gates + hardware + score
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/loop_runner.py run \
  --backend Baihua --circuit E05 --shots 2048 --quick \
  --confirm --allow-hardware --use-cached-account \
  --out resultados/E05_loop

# etapas separadas
loop_runner.py plan --profile perfil.json --circuit E05 --shots 2048 --quick --out resultados/E05_loop
loop_runner.py simulate --state resultados/E05_loop/loop_state.json
loop_runner.py execute --state resultados/E05_loop/loop_state.json --confirm --allow-hardware --use-cached-account
loop_runner.py score --state resultados/E05_loop/loop_state.json
loop_runner.py status --state resultados/E05_loop/loop_state.json
loop_runner.py report --state resultados/E05_loop/loop_state.json
```

## 4. Agente dedicado

O agente `gjq-readout-mitigation` pode rodar o loop via wrapper:

```bash
agent_readout.py loop-plan ...
agent_readout.py loop-simulate ...
agent_readout.py loop-execute ...
agent_readout.py loop-score ...
agent_readout.py loop-run ...
agent_readout.py loop-status ...
agent_readout.py loop-report ...
```

O wrapper mapeia para `loop_runner.py` e rejeita `runner.py run`, `compare`
direto e qualquer outro comando. O hardware só é chamado pelo `loop-execute`/
`loop-run` com `--confirm --allow-hardware` e gates aprovados.

## 5. Estado e orçamento

`loop_state.json` registra:

- backend, perfil, circuito, shots, iteração;
- gates SDD/TDD/simulação/hardware;
- caminhos de plano, simulação, comparação e relatório;
- histórico, melhor resultado, lições;
- submissões estimadas e usadas;
- timestamps.

O `loop_log.jsonl` é append-only. O `RELATORIO_LOOP.md` é regenerável.

## 6. Score e reflexão

O score usa a TVD mitigada do otimizado:

```text
score = 1 - TVD_mitigada_otimizado
```

A reflexão compara:

- proxy: erro menor previsto;
- raw: vencedor pela TVD raw;
- mitigado: vencedor pela TVD mitigada.

Se o proxy não confirmar, o loop registra a lição e propõe:

- usar o baseline como referência;
- testar um candidato alternativo;
- repetir com mais shots;
- calibrar os 4 estados para corrigir leakage 01/10.

## 7. Resultado do loop real

Loop `gjq-loop-20261109T122129`, Baihua, E05/Bell, **2048 shots** por circuito.
Os gates SDD, TDD e simulação passaram; o hardware foi executado com
`--confirm` e `--allow-hardware`.

### 7.1 Gates e simulação

| Item | Resultado |
|---|---|
| SDD | True |
| TDD | True |
| Simulação | True |
| Equivalência ideal (TVD) | 0,000 |
| TVD ruidosa baseline | 0,0176 |
| TVD ruidosa otimizado | 0,0078 |
| Vencedor simulado | otimizado |

### 7.2 Hardware

| Caso | Qubits | Counts 00/11/10/01 | Raw 00/11 | TVD raw | TVD mitigada | Leakage \|11> | Task ID |
|---|---|---:|---:|---:|---:|---:|---|
| Baseline | 0, 1 | 996/922/59/71 | 0,9365 | 0,0635 | **0,0150** | 11,18% | `f36d0036-1994-4281-a42e-e7fcbf332bc0` |
| Otimizado | 106, 107 | 980/915/76/77 | 0,9253 | 0,0747 | **0,0141** | 13,38% | `25fab68e-27d6-4ca2-9bb2-71908fc07d4c` |

Diferença `otimizado − baseline`:

| Métrica | Δ |
|---|---:|
| Correlação raw 00/11 | −0,0112 |
| TVD raw | +0,0112 |
| TVD mitigada | **−0,0009** |

### 7.3 Score

- Proxy: baseline 0,0338; otimizado 0,0060; vencedor **otimizado**.
- Raw: vencedor **baseline**.
- Mitigado: vencedor **otimizado** por 0,0009.
- Proxy confirmado no raw: **False**.
- Proxy confirmado no mitigado: **True**.
- Lição: proxy e mitigado concordam no otimizado; o raw favoreceu o baseline.
  A diferença mitigada é minúscula; repetir com mais shots e calibrar os 4
  estados antes de qualquer conclusão.

### 7.4 Instabilidade entre execuções

A comparação anterior, com **4096 shots**, teve TVD mitigada baseline 0,0249 e
otimizado 0,0277 (baseline melhor). Nesta execução de **2048 shots**, a TVD
mitigada foi 0,0150 e 0,0141 (otimizado melhor por 0,0009). O vencedor mitigado
**inverteu** entre as duas execuções. A diferença é menor que a variação
observada e não sustenta vantagem.

O loop é útil justamente por registrar a contradição: proxy e simulação
favoreceram o otimizado, o raw favoreceu o baseline e o mitigado ficou quase
empatado. Nenhuma dessas leituras autoriza declarar superioridade.

Ver `resultados/baihua/E05_loop/RELATORIO_LOOP.md`.

## 8. Limites

- Simulação não é hardware; modelo depolarizante não prevê fidelidade.
- Uma execução por caso não é estudo estatístico.
- A calibração |11> usa `rx(pi)` e inclui preparação do |1>.
- A inversão 00/11 não corrige leakage para 01/10.
- Não há ZNE, PEC, DD ou correção quântica de erro.
- Custo, fila e calibração podem mudar.
- O loop não promove confiança automaticamente.
