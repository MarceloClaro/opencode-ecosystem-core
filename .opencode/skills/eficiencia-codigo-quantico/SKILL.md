---
name: eficiencia-codigo-quantico
description: Mede e melhora eficiência de circuitos e código quântico com baseline, otimização, gate de correção distribucional, métricas de portas/profundidade e relatório reproduzível. Use para analisar gate count, depth, transpilação, roteamento e benchmarks; não declara speedup ou vantagem quântica sem tarefa completa e hardware.
metadata:
  version: "1"
  origem: "R1108 — eficiência de código quântico"
---

# Eficiência de código quântico

## Quando usar

Use quando o pedido for **medir ou melhorar** um circuito, um script Qiskit,
um pipeline de transpilação ou um benchmark quântico. Não use para afirmar
“meu código é mais rápido” sem baseline, tarefa e medição.

## Contrato

1. **Mesmo circuito.** Baseline e otimizado devem calcular a mesma coisa.
2. **Mesma seed e mesmas restrições.** Portas base, coupling map e versão
   declarados.
3. **Correção antes de performance.** Se a TVD entre as distribuições ideais
   for maior que `1e-9`, a otimização é inválida.
4. **Métrica declarada.** Não misture gate count, depth, tempo de parede e
   custo de backend como se fossem a mesma coisa.
5. **Sem hardware.** Simulação não é execução física.
6. **Sem overclaim.** Redução de 2q não é vantagem quântica; transpilação mais
   curta não é speedup de algoritmo.

## Workflow

```bash
# 1. baseline e otimizado
.venv-quantum/bin/python harnesses/quantum-code-efficiency/runner.py --quick

# 2. relatório
cat harnesses/quantum-code-efficiency/resultados/RELATORIO.md

# 3. teste
.venv-quantum/bin/python -m pytest tests/test_r1108_quantum_code_efficiency.py -q
```

## Métricas

| Métrica | Pergunta | Cuidado |
|---|---|---|
| `num_qubits` | o circuito cabe no backend? | largura não é custo |
| `num_1q` | quantas rotações? | depende da decomposição |
| `num_2q` | quantos CX/ECR? | principal custo em supercondutor |
| `depth` | qual a profundidade? | depende do alinhamento |
| `size` | quantas operações? | inclui medidas |
| `transpile_seconds` | quanto custa compilar? | depende da máquina |
| `tvd` | a distribuição mudou? | não é fidelidade de estado |

## Técnicas de otimização

- cancelamento de portas inversas;
- comutação e template matching;
- otimização de um qubit;
- consolidação de blocos;
- layout e roteamento (Sabre, lookahead);
- escolha de nível de otimização;
- ligação de parâmetros (`parameter_bind`);
- execução em lote;
- escolha de simulador (statevector, MPS, density matrix);
- mitigação de erro (ZNE, PEC, DD) — sempre com custo e limite declarados;
- QEC — fora do escopo de circuitos NISQ curtos.

## Gates

- [ ] TVD ≤ `1e-9`;
- [ ] `2q_otimizado ≤ 2q_baseline`;
- [ ] `depth_otimizado ≤ depth_baseline`;
- [ ] `hardware=False`;
- [ ] `network=False`;
- [ ] seed e versão registradas.

## Rotas no Core

| Necessidade | Agente |
|---|---|
| Otimização de circuito/código | `quantum-code-efficiency` |
| Auditoria de benchmark e claim | `quantum-benchmark-audit` |
| Algoritmos e teoria | `27_agente_computacao_quantica_aplicada` |
| Auditoria de experimento | `quantum-experiment-auditor` |
| Verificação formal | `quantum-lean-verifier` |

## Limites

- Métricas de transpilação e distribuição ideal; não é hardware.
- Não mede fidelidade de estado, calibração ou custo de fila.
- O resultado depende da versão do Qiskit, do seed e do conjunto de portas.
- Comparar circuitos de tarefas diferentes é inválido.
- Redução de portas não é, por si só, vantagem quântica.
