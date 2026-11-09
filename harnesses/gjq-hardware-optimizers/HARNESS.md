# HARNESS — Otimizadores para hardware GJQ (R1109)

**Objetivo:** preparar, comparar e executar circuitos no hardware real da GJQ
com perfil ao vivo, layout noise-aware, gates de segurança e proveniência.

**Não faz:** não inventa calibração, não submete hardware sem `confirm=True` e
`allow_hardware=True`, não retranspila na submissão (`transpile=False`) e não
declara fidelidade, emaranhamento ou vantagem quântica a partir de counts.

## Entradas

- backend GJQ: `Baihua`, `Guoji08` ou simulador;
- perfil JSON offline, se não houver rede;
- circuito nomeado (`E01`–`E18`, `bell`, `ghz4`, `qft4`, `vqe2`, `layered4`,
  `redundant`, `nonadjacent`) ou arquivo QASM;
- estratégia: `balanced`, `min_error`, `min_depth`, `min_two_qubit`,
  `noise_aware`;
- seed, modo rápido/completo;
- shots, quando houver submissão;
- autorização explícita e revisão de custo.

## Perfil do backend

O perfil é extraído de `backend.configuration()`, `backend.properties()` e
`backend.target`:

- largura e `operational_qubits`;
- `coupling_map` operacional;
- portas 1q/2q;
- erros e durações por porta/qubit/aresta;
- erro de leitura;
- fingerprint SHA-256.

O target do Baihua usa `error=1.0` como sentinela de aresta indisponível. O
harness remove arestas com erro `>= 0.999`, exclui qubits com erro 1q `>= 0.05`
e simetriza `cz`, `swap` e `iswap`.

## Layout

1. Contar operações 1q, medições e arestas 2q do circuito.
2. Calcular custo de cada qubit físico e de cada aresta.
3. Calcular caminhos mínimos com erro como peso.
4. Atribuir qubits lógicos por grau de interação.
5. Refinar com 2-opt e conectar a região física.
6. Cair para o layout trivial-operacional se o custo não melhorar.

## Candidatos

| Candidato | Layout | Roteamento |
|---|---|---|
| `trivial` | trivial-operacional | basic |
| `noise_aware` | noise-aware | sabre |
| `sabre` | sabre | sabre |
| `dense` | dense | sabre |

Níveis: `1, 3` no modo rápido; `1, 2, 3` no completo. Seeds: `42` no rápido;
`42, 43` no completo. O baseline não participa da seleção.

## Gates

- [ ] credencial disponível: `GJQ_API_KEY` ou `--use-cached-account`;
- [ ] `confirm=True`;
- [ ] `allow_hardware=True` para Baihua/Guoji/Yudu;
- [ ] `1 <= shots <= 100000`;
- [ ] circuito com medição;
- [ ] `transpile=False`;
- [ ] task ID, hashes e auditoria da soma;
- [ ] nenhuma chave em arquivo, log ou relatório.

## Comandos

```bash
# perfil ao vivo
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py profile \
  --backend Baihua --out resultados/baihua

# perfil offline
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py profile \
  --config config.json --properties properties.json --out resultados/offline

# otimizar sem submeter
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py optimize \
  --backend Baihua --circuit E05 --strategy balanced --quick --out resultados/E05

# benchmark sem submeter
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py benchmark \
  --backend Baihua --set experiments --only E05 E06 E12 --quick --out resultados/bench

# executar hardware real
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py run \
  --backend Baihua --circuit E05 --shots 1024 --quick --strategy balanced \
  --confirm --allow-hardware --wait --timeout 600 --poll 5 \
  --out resultados/E05_execucao

# reler o resultado sem reenviar
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py result \
  --backend Baihua --task-id <TASK_ID> --shots 1024 --out resultados/E05_execucao

# auditar counts locais
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py audit \
  --counts counts.json --shots 1024

# diagnóstico local
.venv-quantum/bin/python harnesses/gjq-hardware-optimizers/runner.py doctor
```

## Execução real de referência

| Campo | Valor |
|---|---|
| Backend | Baihua |
| Circuito | E05/Bell |
| Shots | 1024 |
| Task ID | `1aeb1d6b-4d5b-4ecf-a434-789c579635d1` |
| Status | DONE |
| `00` / `11` | 489 / 449 |
| `10` / `01` | 48 / 38 |
| Fração 00/11 | 0,9160 ± 0,0087 |
| TVD vs ideal | 0,0840 |
| Proxy de erro | 0,005985 |

O proxy foi otimista. Ele é um produto de `(1 - erro)` por porta e leitura e
não modela state preparation, crosstalk, deriva, leakage ou correlação. Não é
fidelidade.

## Artefatos

- `resultados/baihua/perfil.json`;
- `resultados/baihua/configuracao.json`;
- `resultados/baihua/propriedades.json`;
- `resultados/baihua/E05/` — otimização offline;
- `resultados/baihua/E05_execucao/` — execução real, counts, auditoria,
  `RESULTADO_REAL.md`.

## Limites

- Uma execução não prova fidelidade, emaranhamento, vantagem quântica ou
  interpretação de Bohm.
- A calibração muda; o perfil vale para a janela registrada.
- Não há mitigação de erro (ZNE/PEC/DD) nesta versão.
- Custo, fila e disponibilidade mudam; o snapshot não é garantia.
- O harness não substitui o `gjq-runtime` nem o `gjq-experiments`.
