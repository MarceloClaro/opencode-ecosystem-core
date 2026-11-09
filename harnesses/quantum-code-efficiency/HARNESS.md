# HARNESS — Eficiência de código quântico (R1108)

**Objetivo:** medir, comparar e verificar a eficiência de circuitos quânticos
antes e depois de otimização, com gate de correção distribucional.

**Não faz:** não executa hardware, não acessa rede, não instala dependências,
não declara vantagem quântica e não compara circuitos de tarefas diferentes
como se fossem equivalentes.

## Entradas

- circuito ou benchmark nomeado;
- conjunto de portas base (`u`, `cx` por padrão);
- coupling map, quando houver restrição de conectividade;
- seed do transpilador;
- níveis de otimização: baseline `0`, otimizado `3`;
- tolerância de TVD (padrão `1e-9`).

## Métricas

| Métrica | O que mede | Limite |
|---|---|---|
| `num_qubits` | largura do circuito | não mede custo |
| `num_1q` | portas de um qubit | depende da decomposição |
| `num_2q` | portas de dois qubits | principal custo em hardware supercondutor |
| `depth` | profundidade | depende do alinhamento e do backend |
| `size` | número de operações | inclui medidas |
| `transpile_seconds` | tempo de transpilação | depende da máquina |
| `tvd` | distância entre distribuições ideais | não mede fidelidade de estado |

## Etapas

### 1. Baseline

Transpilar com `optimization_level=0`, seed fixa e portas base declaradas.

### 2. Otimizar

Transpilar com `optimization_level=3`, mesma seed e mesmas restrições.

### 3. Verificar correção

Calcular a distribuição ideal dos dois circuitos por statevector,
marginalizada nos bits clássicos medidos. Exigir `TVD ≤ 1e-9`.

Se a TVD falhar, o circuito otimizado **não** é equivalente ao baseline para
a distribuição medida. Não reporte redução de portas.

### 4. Medir

Comparar `num_2q`, `depth`, `size`, `num_1q` e tempo de transpilação.
Reportar redução relativa, não apenas valores absolutos.

### 5. Gates

- [ ] TVD ≤ `1e-9`;
- [ ] `num_2q` otimizado ≤ baseline;
- [ ] `depth` otimizado ≤ baseline;
- [ ] `hardware=False`;
- [ ] `network=False`;
- [ ] versão do Qiskit e seed registradas.

### 6. Relatório

Gerar `resultados.json` e `RELATORIO.md` com:

- protocolo;
- tabela por benchmark;
- resumo;
- limites;
- versão e seed.

## Benchmarks atuais

| Benchmark | O que exercita |
|---|---|
| `bell` | circuito mínimo com emaranhamento |
| `ghz4` | fan-out de CNOT |
| `qft4` | decomposição de QFT |
| `vqe2` | ansatz variacional curto |
| `layered4` | camadas de rotação e CNOT |
| `redundant` | cancelamento de portas |
| `nonadjacent` | roteamento com coupling map linear |

## Comando

```bash
.venv-quantum/bin/python harnesses/quantum-code-efficiency/runner.py --quick
```

Saída esperada: 7 benchmarks, todos `pass`, TVD próxima de zero.

## Limites

- Métricas de transpilação e distribuição ideal; não é hardware.
- Não mede fidelidade de estado, calibração, tempo de fila ou custo real.
- O resultado depende da versão do Qiskit, do seed e do conjunto de portas.
- Redução de portas não é, por si só, vantagem quântica.
- Comparar circuitos de tarefas diferentes é inválido; o harness só compara
  baseline e otimizado do mesmo circuito.
