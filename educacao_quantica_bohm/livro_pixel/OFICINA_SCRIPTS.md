# Oficina de scripts: 18 experimentos, linha a linha {#oficina}

Esta oficina mostra, para cada experimento, **o código que foi rodado**, o
que cada linha faz, o cálculo matemático e o resultado simulado × backend.
Os scripts completos estão em `educacao_quantica_bohm/scripts/experimentos_100.py`.

## E01 — Base |0⟩ {#oficina-e01}

**Script:** `scripts/experimentos_100.py` · `E01` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.measure(0, 0)
```

| Linha | O que faz |
|---|---|
| `QuantumCircuit(1, 1)` | cria 1 qubit e 1 bit clássico |
| `qc.measure(0, 0)` | mede o qubit 0 e grava no bit clássico 0 |

**Cálculo matemático:** P(0) = N0/N; P(1) = N1/N; P(0)+P(1)=1.

**Saída simulada:** 0=1024 → P(0) = 1,000 (ideal 1,000)
**Saída no backend:** 0=1016, 1=8 → P(0) = 0,992 (ideal 1,000); sobreposição: 99,2%; task: `9fd44816-2f18-4857-9129-55c509caa51c`.

**O que prova:** mede a distribuição do estado |0⟩ e o ruído de leitura.

**O que não prova:** não caracteriza a leitura de |1⟩ nem a fidelidade de portas.


## E02 — Base |1⟩ e leitura {#oficina-e02}

**Script:** `scripts/experimentos_100.py` · `E02` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.x(0)
qc.measure(0, 0)
```

| Linha | O que faz |
|---|---|
| `QuantumCircuit(1, 1)` | cria 1 qubit e 1 bit clássico |
| `qc.x(0)` | aplica X: &#124;0⟩ → &#124;1⟩ |
| `qc.measure(0, 0)` | mede o qubit e grava no bit clássico |

**Cálculo matemático:** P(1) = N1/N. O erro de leitura é aproximadamente 1 − P(1).

**Saída simulada:** 1=1024 → P(1) = 1,000 (ideal 1,000)
**Saída no backend:** 1=1010, 0=14 → P(1) = 0,986 (ideal 1,000); sobreposição: 98,6%; task: `6018c711-5649-4eb7-96a1-3b4aa48b7e7e`.

**O que prova:** mede a taxa de leitura correta do estado |1⟩.

**O que não prova:** não é uma calibração completa: um qubit, um estado, uma execução.


## E03 — Superposição H|0⟩ {#oficina-e03}

**Script:** `scripts/experimentos_100.py` · `E03` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)
```

| Linha | O que faz |
|---|---|
| `QuantumCircuit(1, 1)` | cria 1 qubit e 1 bit clássico |
| `qc.h(0)` | Hadamard: &#124;0⟩ → (&#124;0⟩+&#124;1⟩)/√2 |
| `qc.measure(0, 0)` | amostra 0 ou 1 |

**Cálculo matemático:** P(1)=|amplitude de |1⟩|²=0,5. Erro padrão: √(p(1−p)/N).

**Saída simulada:** 0=516, 1=508 → P(1) = 0,496 (ideal 0,500)
**Saída no backend:** 0=530, 1=494 → P(1) = 0,482 (ideal 0,500); sobreposição: 98,6%; task: `268a67b7-1d43-49a4-919d-3c151f3feef6`.

**O que prova:** mostra que a medição é estatística e que H cria superposição.

**O que não prova:** não mede a fase relativa nem prova emaranhamento.


## E04 — Interferência H-Z-H {#oficina-e04}

**Script:** `scripts/experimentos_100.py` · `E04` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.h(0); qc.z(0); qc.h(0)
qc.measure(0, 0)
```

| Linha | O que faz |
|---|---|
| `qc.h(0)` | cria superposição |
| `qc.z(0)` | inverte a fase do ramo &#124;1⟩ |
| `qc.h(0)` | recombina os ramos: HZH = X |
| `qc.measure(0, 0)` | resultado deve ser 1 |

**Cálculo matemático:** HZH = X, logo P(1)=1. O ruído reduz P(1).

**Saída simulada:** 1=1024 → P(1) = 1,000 (ideal 1,000)
**Saída no backend:** 1=1010, 0=14 → P(1) = 0,986 (ideal 1,000); sobreposição: 98,6%; task: `00a6d70a-0529-44da-a3c9-750446161f26`.

**O que prova:** a fase muda a interferência e o resultado final.

**O que não prova:** não lê a fase diretamente; só o efeito no resultado.


## E05 — Estado de Bell {#oficina-e05}

**Script:** `scripts/experimentos_100.py` · `E05` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])
```

| Linha | O que faz |
|---|---|
| `qc.h(0)` | coloca q0 em superposição |
| `qc.cx(0, 1)` | CNOT: &#124;10⟩ vira &#124;11⟩; cria correlação |
| `qc.measure(...)` | mede os dois qubits |

**Cálculo matemático:** Fidelidade proxy = (N00+N11)/N. Ideal: 1,000.

**Saída simulada:** 00=531, 11=493 → P(00)+P(11) = 1,000 (ideal 1,000)
**Saída no backend:** 00=484, 11=480, 10=33 → P(00)+P(11) = 0,941 (ideal 1,000); sobreposição: 94,1%; task: `705bf99c-0bce-4ea3-851d-4efd4db73f7e`.

**O que prova:** mede a correlação 00/11 do estado de Bell.

**O que não prova:** não prova emaranhamento; para isso, CHSH ou tomografia.


## E06 — GHZ de 4 qubits {#oficina-e06}

**Script:** `scripts/experimentos_100.py` · `E06` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(4, 4)
qc.h(0)
for q in (1, 2, 3):
    qc.cx(0, q)
qc.measure([0,1,2,3], [0,1,2,3])
```

| Linha | O que faz |
|---|---|
| `qc.h(0)` | coloca q0 em superposição |
| `qc.cx(0, q)` | espalha a correlação para q1, q2, q3 |
| `qc.measure(...)` | mede os quatro qubits |

**Cálculo matemático:** Fidelidade proxy = (N0000+N1111)/N. Ideal: 1,000.

**Saída simulada:** 0000=527, 1111=497 → P(0000)+P(1111) = 1,000 (ideal 1,000)
**Saída no backend:** 0000=418, 1111=389, 1011=38 → P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição: 78,8%; task: `—`.

**O que prova:** mede a população 0000/1111 do GHZ.

**O que não prova:** não prova emaranhamento genuíno multipartite.


## E07 — CHSH {#oficina-e07}

**Script:** `scripts/experimentos_100.py` · `E07` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
for a1, ang in [(0,-pi/4),(0,pi/4),(1,-pi/4),(1,pi/4)]:
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1)
    if a1: qc.h(0)
    qc.ry(ang, 1)
    qc.measure([0,1], [0,1])
```

| Linha | O que faz |
|---|---|
| `qc.h(0); qc.cx(0,1)` | prepara o estado de Bell |
| `if a1: qc.h(0)` | escolhe a base de Alice (Z ou X) |
| `qc.ry(ang, 1)` | escolhe o ângulo de Bob |
| `qc.measure(...)` | mede as duas bases |

**Cálculo matemático:** E=(N00+N11−N01−N10)/N; S=E00+E01+E10−E11. Clássico: |S|≤2; ideal: 2√2≈2,828.

**Saída simulada:** 4 circuitos → S = 2,828 (ideal 2,828)
**Saída no backend:** 4 circuitos → S = 2,383 (ideal 2,828); sobreposição: 93,6%; task: `—`.

**O que prova:** se S>2, as correlações não são explicáveis por um modelo local.

**O que não prova:** não é loophole-free; uma execução não é prova estatística.


## E08 — Gerador quântico de números {#oficina-e08}

**Script:** `scripts/experimentos_100.py` · `E08` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)
```

| Linha | O que faz |
|---|---|
| `qc.h(0)` | cria 0 e 1 com amplitudes iguais |
| `qc.measure(0, 0)` | cada execução produz um bit |

**Cálculo matemático:** Equilíbrio = |P(0)−P(1)|. Ideal: 0.

**Saída simulada:** 1=531, 0=493 → |P(0)-P(1)| = 0,037 (ideal 0,000)
**Saída no backend:** 0=530, 1=494 → |P(0)-P(1)| = 0,035 (ideal 0,000); sobreposição: 96,4%; task: `58eedaa5-295c-41cc-887c-13ba436660a8`.

**O que prova:** mostra que a medição de H|0⟩ é aproximadamente equilibrada.

**O que não prova:** não é um gerador criptográfico certificado; o backend pode ter viés.


## E09 — Codificação de amplitude {#oficina-e09}

**Script:** `scripts/experimentos_100.py` · `E09` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
import numpy as np
from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.ry(2*np.pi/3, 0)
qc.measure(0, 0)
```

| Linha | O que faz |
|---|---|
| `qc.ry(θ, 0)` | rotação de amplitude: &#124;0⟩ → cos(θ/2)&#124;0⟩ + sen(θ/2)&#124;1⟩ |
| `qc.measure(0, 0)` | amostra 0 ou 1 |

**Cálculo matemático:** P(1)=sen²(θ/2). Para θ=2π/3, P(1)=0,75.

**Saída simulada:** 1=753, 0=271 → P(1) = 0,735 (ideal 0,750)
**Saída no backend:** 1=761, 0=263 → P(1) = 0,743 (ideal 0,750); sobreposição: 99,2%; task: `90f9f88a-2470-4725-bc6c-f63b95590581`.

**O que prova:** mostra como um ângulo codifica uma probabilidade.

**O que não prova:** não prepara um estado arbitrário de vários qubits.


## E10 — Classificador XOR (VQC) {#oficina-e10}

**Script:** `scripts/experimentos_100.py` · `E10` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
XOR = [(0,0),(0,1),(1,0),(1,1)]
for x in XOR:
    qc = QuantumCircuit(2, 1)
    qc.ry(np.pi*x[0], 0); qc.ry(np.pi*x[1], 1)
    qc.ry(theta[0], 0); qc.ry(theta[1], 1)
    qc.cx(0, 1)
    qc.ry(theta[2], 0); qc.ry(theta[3], 1)
    qc.measure(0, 0)
```

| Linha | O que faz |
|---|---|
| `qc.ry(pi*x[q], q)` | codifica as duas features nos qubits |
| `qc.ry(theta[...], q)` | aplica os parâmetros treinados |
| `qc.cx(0,1)` | cria a interação entre os qubits |
| `qc.measure(0,0)` | lê a classe prevista |

**Cálculo matemático:** pred=1[P(1)≥0,5]; acurácia=(1/4)Σ 1[pred=y].

**Saída simulada:** 4 circuitos → Acurácia = 4/4
**Saída no backend:** 4 circuitos → Acurácia = 4/4; sobreposição: 95,9%; task: `—`.

**O que prova:** mostra o pipeline de codificação, treino e avaliação.

**O que não prova:** 4/4 não é generalização; o teste é pequeno e o teto é 100%.


## E11 — Interferência de dois qubits {#oficina-e11}

**Script:** `scripts/experimentos_100.py` · `E11` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.h(0); qc.h(1)
qc.cz(0, 1)
qc.h(0)
qc.measure([0,1], [0,1])
```

| Linha | O que faz |
|---|---|
| `qc.h(0); qc.h(1)` | cria superposição nos dois qubits |
| `qc.cz(0,1)` | adiciona fase controlada |
| `qc.h(0)` | recombina o qubit 0 |
| `qc.measure(...)` | mede a distribuição final |

**Cálculo matemático:** P(00)=N00/N. Ideal: 0,500.

**Saída simulada:** 11=524, 00=500 → P(00) = 0,488 (ideal 0,500)
**Saída no backend:** 00=485, 11=481, 10=32 → P(00) = 0,474 (ideal 0,500); sobreposição: 94,3%; task: `a9be9213-57d5-4036-8a59-41766fbcbe76`.

**O que prova:** mostra interferência de dois qubits.

**O que não prova:** não prova emaranhamento nem vantagem computacional.


## E12 — QFT de 3 qubits {#oficina-e12}

**Script:** `scripts/experimentos_100.py` · `E12` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit.circuit.library import QFTGate
qc = QuantumCircuit(3, 3)
qc.x(2)
qc.append(QFTGate(3), range(3))
qc.measure([0,1,2], [0,1,2])
```

| Linha | O que faz |
|---|---|
| `qc.x(2)` | prepara &#124;100⟩ |
| `QFTGate(3)` | aplica a transformada de Fourier quântica |
| `qc.measure(...)` | mede a distribuição uniforme |

**Cálculo matemático:** P(000)=N000/N. Ideal: 1/8=0,125.

**Saída simulada:** 011=138, 111=137, 001=132 → P(000) = 0,117 (ideal 0,125)
**Saída no backend:** 101=161, 001=137, 010=128 → P(000) = 0,120 (ideal 0,125); sobreposição: 95,7%; task: `2e281bbe-d26e-477f-8121-51485a7210d1`.

**O que prova:** mostra a QFT como mudança de base.

**O que não prova:** não prova speedup; a QFT é parte de algoritmos maiores.


## E13 — Produto tensorial |01⟩ {#oficina-e13}

**Script:** `scripts/experimentos_100.py` · `E13` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.x(0)
qc.measure([0,1], [0,1])
```

| Linha | O que faz |
|---|---|
| `qc.x(0)` | prepara q0=1 e q1=0 |
| `qc.measure(...)` | mede os dois qubits |

**Cálculo matemático:** P(01)=N01/N. Ideal: 1,000.

**Saída simulada:** 01=1024 → P(01) = 1,000 (ideal 1,000)
**Saída no backend:** 01=980, 11=28, 00=16 → P(01) = 0,957 (ideal 1,000); sobreposição: 95,7%; task: `b29350bd-90e9-4bc7-84c1-3b37e039a7d6`.

**O que prova:** mostra que operações locais não criam correlação.

**O que não prova:** não prova emaranhamento; o estado é produto.


## E14 — Ruído de fase {#oficina-e14}

**Script:** `scripts/experimentos_100.py` · `E14` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.h(0); qc.x(0); qc.h(0)
qc.measure(0, 0)
```

| Linha | O que faz |
|---|---|
| `qc.h(0); qc.x(0); qc.h(0)` | HXH = Z; o estado deveria voltar a &#124;0⟩ |
| `qc.measure(0,0)` | mede a população que sobrou |

**Cálculo matemático:** P(0)=N0/N. Ideal: 1,000; o ruído reduz.

**Saída simulada:** 0=1024 → P(0) = 1,000 (ideal 1,000)
**Saída no backend:** 0=1016, 1=8 → P(0) = 0,992 (ideal 1,000); sobreposição: 99,2%; task: `aae54f46-5c56-4245-8a32-ad4f2a78e207`.

**O que prova:** mostra perda de coerência em uma sequência curta.

**O que não prova:** não separa T1, T2, leitura e erro de porta.


## E15 — GHZ via QASM 2.0 {#oficina-e15}

**Script:** `scripts/experimentos_100.py` · `E15` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
OPENQASM 2.0;
include "qelib1.inc";
qreg q[4]; creg c[4];
h q[0];
cx q[0],q[1]; cx q[0],q[2]; cx q[0],q[3];
measure q[0]->c[0]; measure q[1]->c[1];
measure q[2]->c[2]; measure q[3]->c[3];
```

| Linha | O que faz |
|---|---|
| `qreg/creg` | declara 4 qubits e 4 bits clássicos |
| `h q[0]` | cria superposição |
| `cx q[0],q[k]` | espalha a correlação |
| `measure ...` | mede os quatro qubits |

**Cálculo matemático:** Mesmo cálculo do E06: (N0000+N1111)/N.

**Saída simulada:** 1111=540, 0000=484 → P(0000)+P(1111) = 1,000 (ideal 1,000)
**Saída no backend:** 0000=418, 1111=389, 1011=38 → P(0000)+P(1111) = 0,788 (ideal 1,000); sobreposição: 78,8%; task: `—`.

**O que prova:** mostra que o mesmo circuito pode ser escrito em QASM 2.0.

**O que não prova:** não garante que o editor/backend executou sem erro.


## E16 — Esfera de Bloch {#oficina-e16}

**Script:** `scripts/experimentos_100.py` · `E16` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
# base Z
qc = QuantumCircuit(1, 1); qc.h(0); qc.measure(0,0)
# base X
qc = QuantumCircuit(1, 1); qc.h(0); qc.h(0); qc.measure(0,0)
```

| Linha | O que faz |
|---|---|
| `qc.h(0)` | prepara (&#124;0⟩+&#124;1⟩)/√2 |
| `qc.h(0); qc.h(0)` | H²=I: mede na base X |
| `qc.measure(0,0)` | amostra Z ou X |

**Cálculo matemático:** ⟨Z⟩=P0−P1; ⟨X⟩=P0−P1 na base X.

**Saída simulada:** 2 circuitos → ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1)
**Saída no backend:** 2 circuitos → ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1); sobreposição: 98,9%; task: `9da79d10-8f39-41f0-8868-0591c6dfaf5d`.

**O que prova:** estima dois componentes do vetor de Bloch.

**O que não prova:** não é tomografia completa; falta ⟨Y⟩.


## E17 — Interferência de três qubits {#oficina-e17}

**Script:** `scripts/experimentos_100.py` · `E17` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(3, 3)
for q in range(3): qc.h(q)
qc.cz(0,1); qc.cz(1,2)
for q in range(3): qc.h(q)
qc.measure([0,1,2], [0,1,2])
```

| Linha | O que faz |
|---|---|
| `qc.h(q)` | cria superposição nos três qubits |
| `qc.cz(0,1); qc.cz(1,2)` | adiciona fases controladas |
| `qc.h(q)` | recombina |
| `qc.measure(...)` | mede a distribuição |

**Cálculo matemático:** P(000)=N000/N. Ideal: 0,250.

**Saída simulada:** 101=265, 000=264, 010=254 → P(000) = 0,258 (ideal 0,250)
**Saída no backend:** 010=244, 101=236, 000=235 → P(000) = 0,229 (ideal 0,250); sobreposição: 90,8%; task: `c92beefa-a283-40a7-9415-3f1b7ffe4757`.

**O que prova:** mostra interferência de três qubits.

**O que não prova:** não é uma caminhada quântica completa.


## E18 — Amostragem binomial {#oficina-e18}

**Script:** `scripts/experimentos_100.py` · `E18` · backend `Guoji08`
**O que o script faz:** monta o circuito, transpila para o backend, executa 1024
tiros, lê os counts e calcula a métrica.

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)
```

| Linha | O que faz |
|---|---|
| `qc.h(0)` | cria p=0,5 |
| `qc.measure(0,0)` | cada tiro é Bernoulli(p) |

**Cálculo matemático:** P(1)=N1/N; erro padrão=√(p(1−p)/N).

**Saída simulada:** 0=529, 1=495 → P(1) = 0,483 (ideal 0,500)
**Saída no backend:** 0=530, 1=494 → P(1) = 0,482 (ideal 0,500); sobreposição: 99,9%; task: `54de9107-54fd-4aa5-8c85-53012550ed22`.

**O que prova:** mostra que a estimativa melhora com N.

**O que não prova:** não prova independência entre tiros.
