# Eficiência de código quântico — R1108

**Status:** implementação local<br>
**Skill:** `eficiencia-codigo-quantico`<br>
**Agentes:** `quantum-code-efficiency` e `quantum-benchmark-audit`<br>
**Harness:** `harnesses/quantum-code-efficiency/`<br>
**Spec:** `specs/SPEC-935-R1108-quantum-code-efficiency.md`

## 1. O que é eficiência

Eficiência de código quântico não é uma coisa só. É um conjunto de métricas:

| Métrica | O que mede | Por que importa |
|---|---|---|
| qubits | largura | define se o circuito cabe no backend |
| portas 1q | rotações e bases | custa tempo e erro |
| portas 2q | CX/ECR | principal fonte de erro em supercondutores |
| profundidade | camadas dependentes | sofre decoerência |
| tamanho | operações totais | custa compilação e execução |
| tempo de transpilação | custo de build | importa em pipelines |
| TVD | diferença de distribuição | verifica se a otimização mudou o resultado |

A pergunta correta é: **“o circuito ficou menor e/ou mais raso sem mudar a
distribuição que ele calcula?”** Não é: “o código ficou mais rápido?”.

## 2. Protocolo

1. Fixar o circuito, a seed, as portas base e o coupling map.
2. Transpilar com `optimization_level=0` (baseline).
3. Transpilar com `optimization_level=3` (otimizado).
4. Calcular a distribuição ideal dos dois circuitos por statevector,
   marginalizada nos bits clássicos medidos.
5. Exigir `TVD ≤ 1e-9`.
6. Medir 2q, depth, size, 1q e tempo.
7. Reportar redução relativa, versão, seed e limites.
8. Auditar com `quantum-benchmark-audit`.

Sem o passo 5, a comparação é inválida.

## 3. Benchmarks

| Benchmark | O que exercita |
|---|---|
| `bell` | emaranhamento mínimo |
| `ghz4` | fan-out de CNOT |
| `qft4` | decomposição de QFT |
| `vqe2` | ansatz variacional curto |
| `layered4` | camadas de rotação e CNOT |
| `redundant` | cancelamento de portas |
| `nonadjacent` | roteamento com coupling map linear |

## 4. Resultado local

Execução de referência com Qiskit 2.3.0, seed 42, portas base `u/cx`:

| Métrica | Valor |
|---|---:|
| Benchmarks | 7 |
| Pass | 7 |
| Fail | 0 |
| TVD médio | 9,02 × 10⁻¹⁷ |
| Redução média de 2q | 31,3% |
| Redução média de profundidade | 25,6% |

Esses números são **locais e condicionais**. Eles não são uma promessa de
ganho em hardware, nem uma medida de vantagem quântica. O QFT-4, por exemplo,
caiu de 18 para 12 portas de dois qubits e de 28 para 22 de profundidade; o
circuito redundante caiu de 2 para 0 portas de dois qubits; o CNOT não
adjacente caiu de 7 para 1 porta de dois qubits com roteamento.

### 4.1 Experimentos do livro (E01–E18)

O harness também importa os circuitos reais do livro: **25 circuitos em 18
experimentos**. Resultado local com níveis 0–3, seed 42:

| Métrica | Valor |
|---|---:|
| Circuitos | 25 |
| Experimentos | 18 |
| Pass | 25 |
| Fail | 0 |
| Redução média de 2q | 1,3% |
| Redução média de profundidade | 12,9% |
| TVD médio do melhor nível | 1,69 × 10⁻¹⁷ |

O caso mais visível é o E12 (QFT): 9 → 6 portas de dois qubits e 20 → 14 de
profundidade. A maioria dos circuitos pequenos não tem 2q para reduzir; o
ganho aparece em profundidade e tamanho.

Varredura de ruído depolarizante (2048 tiros):

| p | TVD baseline | TVD melhor nível | Δ |
|---:|---:|---:|---:|
| 0 | 0,0068 | 0,0077 | +0,0009 |
| 0,001 | 0,0061 | 0,0063 | +0,0002 |
| 0,005 | 0,0094 | 0,0073 | −0,0021 |
| 0,01 | 0,0142 | 0,0094 | −0,0048 |

Em `p = 0`, a TVD é apenas ruído de amostragem (2048 tiros); não é erro de
porta. A diferença positiva em p = 0 e p = 0,001 é compatível com esse ruído
de amostragem. A varredura é descritiva: não prova fidelidade de backend nem
vantagem quântica.

Comando:

```bash
.venv-quantum/bin/python harnesses/quantum-code-efficiency/runner.py --mode experiments
```

## 5. Técnicas que o agente pode propor

- cancelamento de portas inversas;
- comutação e template matching;
- otimização de um qubit;
- consolidação de blocos;
- layout e roteamento (Sabre, lookahead);
- parameter binding;
- execução em lote;
- escolha de simulador (statevector, MPS, density matrix);
- mitigação de erro (ZNE, PEC, DD) com custo declarado;
- QEC, quando o circuito justificar.

Cada técnica deve vir com uma métrica e um gate. “Otimizar” sem medir é
propaganda.

## 6. Comando

```bash
.venv-quantum/bin/python harnesses/quantum-code-efficiency/runner.py --quick
```

Saída:

- `harnesses/quantum-code-efficiency/resultados/resultados.json`;
- `harnesses/quantum-code-efficiency/resultados/RELATORIO.md`.

## 7. Gates

- [ ] TVD ≤ `1e-9`;
- [ ] 2q otimizado ≤ baseline;
- [ ] depth otimizado ≤ baseline;
- [ ] `hardware=False`;
- [ ] `network=False`;
- [ ] seed e versão registradas.

## 8. Limites

- Métricas de transpilação e distribuição ideal; não é hardware.
- Não mede fidelidade de estado, calibração, fila ou custo real.
- Depende da versão do Qiskit, do seed e do conjunto de portas.
- Redução de portas não é vantagem quântica.
- Comparar circuitos de tarefas diferentes é inválido.
- Auditoria local não é peer review.

## 9. Rotas no Core

| Necessidade | Agente |
|---|---|
| Otimizar circuito/código | `quantum-code-efficiency` |
| Auditar benchmark e claim | `quantum-benchmark-audit` |
| Algoritmos e teoria | `27_agente_computacao_quantica_aplicada` |
| Auditoria de experimento | `quantum-experiment-auditor` |
| Verificação formal | `quantum-lean-verifier` |

## 10. Referências de apoio

QISKIT. **Transpiler documentation**. Versão 2.3.0. Disponível em:
https://docs.quantum.ibm.com/transpile. Acesso em: 9 nov. 2026.

QISKIT. **AerSimulator documentation**. Versão 0.18.2. Disponível em:
https://qiskit.github.io/qiskit-aer/. Acesso em: 9 nov. 2026.

LARANJEIRA, M. C. **Experimentos reproduzidos E01–E18 + E19**. [S. l.]:
OpenCode Ecosystem Core, 2026b. Relatório técnico.
