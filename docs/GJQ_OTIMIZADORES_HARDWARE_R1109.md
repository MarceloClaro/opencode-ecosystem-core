# Otimizadores para hardware GJQ — R1109

**Status:** implementação local + execução real no Baihua

**Spec:** `specs/SPEC-935-R1109-gjq-hardware-optimizers.md`

**Skill:** `.opencode/skills/gjq-hardware-optimizers/SKILL.md`

**Agente:** `agents/catalog/gjq-hardware-optimizer.md`

**Harness:** `harnesses/gjq-hardware-optimizers/`

## 1. O que foi executado

Em 2026-11-09, o runtime GJQ listou 7 backends ao vivo. O **Baihua** apareceu
como hardware supercondutor, 156 qubits, 154 disponíveis, 0 tarefas pendentes,
`credits_required=False`. O perfil foi extraído do `backend.target` e das
`backend.properties` ao vivo:

| Campo | Valor |
|---|---|
| Backend | Baihua |
| Qubits | 156 |
| Qubits operacionais | 154 (80 e 155 excluídos por erro 1q de 5%) |
| Arestas físicas | 128 (256 direções após simetrizar `cz`) |
| Portas 1q | `h`, `rx`, `ry`, `rz` |
| Portas 2q | `cz` |
| Calibração | 2026-11-09 17:23:30-03:00 |
| Fingerprint | `f79a19730b1c5cc0…` |

O target do Baihua usa `error=1.0` como sentinela de aresta indisponível.
O parser remove essas arestas, exclui os qubits degradados e simetriza `cz`,
que é uma porta simétrica. Sem esse filtro, o layout poderia escolher uma
aresta inexistente.

## 2. Circuito e layout

Circuito: E05/Bell, 2 qubits, 1024 shots, `transpile=False`.

O layout noise-aware escolheu os qubits físicos **106 e 107**:

| Métrica | Baseline (trivial) | Escolhido |
|---|---:|---:|
| Layout | 0, 1 | 106, 107 |
| Erro proxy | 0,03379 | **0,005985** |
| Sucesso proxy | 0,9662 | **0,9940** |
| 2q | 1 | 1 |
| Profundidade | 4 | 4 |

O QASM final tem `qreg q[108]` e gates em `q[106]`/`q[107]`; a numeração física
é preservada para o backend.

## 3. Execução real

| Campo | Valor |
|---|---|
| Task ID | `1aeb1d6b-4d5b-4ecf-a434-789c579635d1` |
| Backend | Baihua |
| Shots | 1024 |
| Submissão | 2026-11-09T11:25:17-03:00 (local); 2026-11-09T22:25:18Z (backend) |
| Status | DONE |
| Soma dos counts | 1024 |

| Bitstring | Counts | Probabilidade | Erro padrão |
|---|---:|---:|---:|
| `00` | 489 | 0,477539 | 0,015609 |
| `11` | 449 | 0,438477 | 0,015506 |
| `10` | 48 | 0,046875 | 0,006605 |
| `01` | 38 | 0,037109 | 0,005907 |

Métricas descritivas:

- Fração de outcomes correlacionados `00`/`11`: **0,9160 ± 0,0087** (1σ).
- TVD observada vs distribuição ideal de Bell: **0,0840**.
- Erro proxy do otimizador: **0,005985**.

O proxy foi **otimista** por um fator de aproximadamente 14 em relação à TVD
observada. Isso não significa que o layout escolhido seja inválido: os valores
de `h`, `rx`, `ry`, `rz`, `cz(106,107)` e leitura em 106/107 são os reportados
pela calibração do backend (todos em torno de `1e-3`). Significa que o produto
de `(1 - erro)` por porta não captura state preparation, crosstalk, deriva,
leakage ou correlação. O proxy não é fidelidade e não deve ser apresentado como
previsão do resultado.

## 4. O que o otimizador faz

1. **Perfil**: lê `backend.configuration()`, `backend.properties()` e
   `backend.target`; registra largura, acoplamentos, portas base, erros e
   durações.
2. **Filtro**: remove arestas com erro sentinela (`>= 0.999`), qubits com erro
   1q `>= 0.05` e arestas fora do `coupling_map` operacional.
3. **Simetrização**: adiciona as duas direções para `cz`, `swap` e `iswap`.
4. **Layout noise-aware**: pondera 1q, medição e arestas 2q; calcula caminhos
   mínimos com erro como peso; escolhe uma região física conectada.
5. **Candidatos**: baseline trivial, noise-aware, Sabre e Dense; níveis 1–3;
   seeds declaradas.
6. **Seleção**: `balanced`, `min_error`, `min_depth`, `min_two_qubit` ou
   `noise_aware`; o baseline não participa da seleção.
7. **Compactação**: remove qubits ociosos preservando os índices físicos.
8. **Exportação**: QASM 2.0, QASM 3.0, JSON, Markdown e SHA-256.
9. **Submissão**: `Sampler(backend=backend).run(circuit, shots=shots)`, com o
   circuito já otimizado; `transpile=False` evita dupla transpilação.
10. **Proveniência**: task ID, backend, shots, timestamps, hashes, counts e
    auditoria da soma.

## 5. Como usar

### 5.1 Com `GJQ_API_KEY` no ambiente

```bash
export GJQ_API_KEY="sua-chave"

# 1. perfil ao vivo
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py profile \
  --backend Baihua --out resultados/baihua

# 2. otimizar sem submeter
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py optimize \
  --backend Baihua --circuit E05 --strategy balanced --quick \
  --out resultados/baihua/E05

# 3. executar no hardware real (Bell, 1024 shots)
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py run \
  --backend Baihua --circuit E05 --shots 1024 --quick --strategy balanced \
  --confirm --allow-hardware --wait --timeout 600 --poll 5 \
  --out resultados/baihua/E05_execucao

# 4. reler o resultado sem reenviar
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py result \
  --backend Baihua --task-id <TASK_ID> --shots 1024 \
  --out resultados/baihua/E05_execucao
```

### 5.2 Com a conta já cacheada pelo SDK

O SDK grava a conta em `~/.gjq_client/gjq_client_account.json` com permissão
`600`. O flag `--use-cached-account` usa esse arquivo sem ler nem imprimir a
chave:

```bash
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py run \
  --backend Baihua --circuit E05 --shots 1024 --quick \
  --confirm --allow-hardware --wait --timeout 600 --poll 5 \
  --use-cached-account --out resultados/baihua/E05_execucao
```

O flag é explícito: sem ele, o harness exige `GJQ_API_KEY` no ambiente.

### 5.3 Perfil offline a partir do MCP

Salve os campos `configuration` e `properties` de `gjq_backend_config` e
`gjq_backend_properties` e rode:

```bash
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py profile \
  --config config.json --properties properties.json --out resultados/perfil_offline
```

## 6. Gates

- `GJQ_API_KEY` no ambiente ou `--use-cached-account` explícito;
- `confirm=True` (`--confirm`);
- `allow_hardware=True` (`--allow-hardware`) para Baihua, Guoji01/04/07/08 e
  Yudu;
- `1 <= shots <= 100000`;
- pelo menos uma medição;
- `transpile=False` na submissão;
- task ID e auditoria da soma dos counts;
- nenhuma chave em arquivo, log ou relatório.

## 7. Limites

- Uma execução de 1024 shots não prova fidelidade, emaranhamento, vantagem
  quântica ou interpretação de Bohm.
- A fração `00`/`11` é uma taxa de outcomes correlacionados, não fidelidade de
  estado.
- O proxy de erro não é calibração nem previsão do resultado; ele foi otimista
  nesta execução.
- A calibração muda; o perfil vale para a janela registrada.
- Não há mitigação de erro (ZNE/PEC/DD) nesta versão.
- Custo, fila e disponibilidade podem mudar; `credits_required=False` e
  0 tarefas pendentes são o estado observado em 2026-11-09, não uma garantia.
- O harness não substitui o `gjq-runtime` nem o `gjq-experiments`.

## 8. Artefatos

- `harnesses/gjq-hardware-optimizers/resultados/baihua/perfil.json` — perfil
  real do Baihua (154 qubits operacionais, 256 direções).
- `.../baihua/E05/` — otimização offline, QASM2/QASM3, relatório.
- `.../baihua/E05_execucao/` — execução real, counts, auditoria, task ID e
  `RESULTADO_REAL.md`.

## 9. Referências de apoio

QISKIT. **Transpiler documentation**. Versão 2.3.0. Disponível em:
https://docs.quantum.ibm.com/transpile. Acesso em: 9 nov. 2026.

GJQ. **Tiangong Quantum Cloud — server list**. Disponível em:
https://www.tiangongqs.com/cloud/server. Acesso em: 9 nov. 2026.

GJQ. **gjq-client 0.2.1**. Disponível em:
https://github.com/guoji-quantum/gjq_client. Acesso em: 9 nov. 2026.
