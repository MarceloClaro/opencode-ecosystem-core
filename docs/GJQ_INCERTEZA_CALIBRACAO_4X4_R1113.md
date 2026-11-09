# Incerteza e calibração 4×4 no GJQ — R1113

**Status:** implementação local + execução real no Baihua
**Spec:** `specs/SPEC-935-R1113-gjq-uncertainty-full-calibration.md`
**Depende de:** R1110 (mitigação), R1112 (loop)

## 1. O que mudou

O R1112 usava calibração |00>/|11> e uma submatriz 2×2. Isso corrigia flips
00↔11, mas não a população que saía para 01/10. O R1113 adiciona:

- calibração dos **4 estados**: |00>, |01>, |10>, |11>;
- matriz **4×4** completa;
- `N` repetições do Bell por caso, com counts agregados;
- estatística por repetição: média, desvio, mínimo e máximo;
- score baseado na TVD mitigada 4×4.

## 2. Matriz 4×4

Para cada estado preparado `s`, a coluna `s` da matriz é a distribuição medida:

```text
A[medido, preparado] = P(medido | preparado)
p_mit = A^{-1} p_obs
```

Massas negativas são clipadas e o vetor é renormalizado. A condição da matriz é
registrada; se estiver mal condicionada, usa-se pseudoinversa.

## 3. Repetições e incerteza

Com `N=3` e 8192 shots por circuito:

```text
baseline: 4 cal + 3 Bell = 7 jobs
otimizado: 4 cal + 3 Bell = 7 jobs
total: 14 jobs
```

Para cada repetição, o relatório registra:

- raw 00/11;
- TVD raw;
- TVD mitigada 4×4;
- correlação mitigada.

A incerteza é a dispersão entre repetições (`média ± desvio`), não uma prova
estatística definitiva.

## 4. Comandos

```bash
# loop com 3 repetições, 8192 shots, calibração 4x4
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/agent_readout.py loop-run \
  --backend Baihua --circuit E05 --shots 8192 --repetitions 3 --full-calibration \
  --confirm --allow-hardware --use-cached-account \
  --out harnesses/gjq-hardware-optimizers/resultados/baihua/E05_loop_uncertainty

# plano apenas
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py compare \
  --plan --profile perfil.json --circuit E05 --shots 8192 \
  --repetitions 3 --full-calibration --quick --out resultados/plano_4x4
```

Saídas:

- `plan/plano_comparacao.json` com `submissions_estimated=14`;
- `comparacao/comparacao.json` com counts agregados, matriz 4×4 e
  `repetition_stats`;
- `RELATORIO_COMPARACAO.md` com tabela por repetição;
- `RELATORIO_LOOP.md` com gates, hardware, score e incerteza.

## 5. Resultado real

Loop `gjq-loop-20261109T125854`, Baihua, E05/Bell, **8192 shots × 3
repetições** e calibração completa dos 4 estados. Gates SDD, TDD, simulação e
hardware aprovados.

### 5.1 Resultado agregado

| Caso | Raw 00/11 | Raw TVD | TVD mitigada 4×4 | Correlação mitigada |
|---|---:|---:|---:|---:|
| Baseline 0/1 | **0,9268** | **0,0732** | **0,0092** | 0,9999 |
| Otimizado 106/107 | 0,9152 | 0,0848 | 0,0168 | 0,9832 |

Diferença `otimizado − baseline`:

| Métrica | Δ |
|---|---:|
| Correlação raw 00/11 | −0,0117 |
| TVD raw | +0,0117 |
| TVD mitigada 4×4 | **+0,0077** |

### 5.2 Incerteza por repetição

| Caso | TVD mitigada média | Desvio | Mín. | Máx. |
|---|---:|---:|---:|---:|
| Baseline | 0,0092 | 0,0029 | 0,0058 | 0,0109 |
| Otimizado | 0,0168 | 0,0019 | 0,0147 | 0,0183 |

As faixas **não se sobrepõem**: o máximo do baseline (0,0109) é menor que o
mínimo do otimizado (0,0147). O baseline venceu nas três repetições.

### 5.3 Efeito da matriz 4×4

| Caso | Mitigado 00 | Mitigado 01 | Mitigado 10 | Mitigado 11 |
|---|---:|---:|---:|---:|
| Baseline | 0,4909 | 0,0001 | 0,0000 | 0,5090 |
| Otimizado | 0,4956 | 0,0000 | 0,0168 | 0,4876 |

A matriz 4×4 corrigiu a maior parte de 01/10. O resíduo 10 do otimizado
(0,0168) é o próprio TVD mitigado; ele não é explicado por readout e aponta
para erro de porta, preparação ou crosstalk no par 106/107.

### 5.4 Proxy, simulação e hardware

- Proxy: baseline 0,0338; otimizado 0,0060; vencedor **otimizado**.
- Simulação: baseline 0,0190; otimizado 0,0073; vencedor **otimizado**.
- Hardware raw: vencedor **baseline**.
- Hardware mitigado 4×4: vencedor **baseline** (0,0092 vs 0,0168).

Proxy e simulação favoreceram o otimizado; o hardware não confirmou. A
calibração declarada e o modelo depolarizante não previram o Bell.

### 5.5 Task IDs

| Caso | Repetição | Task ID |
|---|---|---|
| Baseline | 1 | `b95a5e17-68da-4e17-b17f-7aaaa7cc506b` |
| Baseline | 2 | `a40d4960-fd2e-4068-bb5b-c49fc58c5c20` |
| Baseline | 3 | `a796e707-e17a-4e8a-988d-1bf1ef24a1fa` |
| Otimizado | 1 | `20ae794b-9a3c-4e61-b344-1956fd3fdeec` |
| Otimizado | 2 | `5bd84a46-f602-4ecc-9861-02a838387f41` |
| Otimizado | 3 | `b5c74bb0-48bd-464b-8f3f-6eac6d5607c2` |

As calibrações 4×4 têm task IDs em `comparacao/comparacao.json`.

### 5.6 Jobs órfãos

Foram 20 submissões no total:

- **14 usadas** na comparação final (4 calibrações + 3 Bell por caso);
- **5 órfãs** da primeira tentativa, que falhou por `NameError: correlation`;
- **1 órfã** (`760869c6-b768-400e-8f63-b91ad2d7f2c1`) que ficou em `RUNNING` e
  foi substituída por três repetições novas.

Os jobs órfãos não entram no resultado final. O `loop_state.json` e o
`loop_log.jsonl` registram a ocorrência.

Ver `resultados/baihua/E05_loop_uncertainty/RELATORIO_LOOP.md` e
`comparacao/RELATORIO_COMPARACAO.md`.

## 6. Limites

- A matriz 4×4 corrige 01/10, mas não state preparation, crosstalk ou deriva.
- A calibração |11> usa `rx(pi)` e inclui preparação do |1>.
- Três repetições estimam dispersão; não provam significância.
- A TVD mitigada não é fidelidade de estado.
- Não há ZNE, PEC, DD ou correção quântica de erro.
- Custo, fila e calibração podem mudar.
- O loop registra lições; não promove confiança automaticamente.
