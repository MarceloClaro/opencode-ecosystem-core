# Profundidade científica: o que o livro cobre e o que fica fora {#profundidade}

> Este apêndice existe para responder a uma pergunta justa: **este livro
> substitui Nielsen & Chuang, Preskill, Bohm & Hiley ou Eisberg & Resnick?**
> Não. Ele cobre a ponte entre a ideia, o circuito e o hardware; não cobre toda
> a matemática nem toda a pesquisa. O que segue é o mapa do que está dentro e do
> que está fora.

## 1. Postulados mínimos

### 1.1 Estado

Um qubit puro é um vetor unitário em `ℂ²`:

```text
|ψ⟩ = α|0⟩ + β|1⟩,   |α|² + |β|² = 1
```

Para `n` qubits, o espaço é `(ℂ²)^⊗n`, de dimensão `2^n`. Um estado misto é uma
matriz densidade `ρ` em `ℂ^{2^n × 2^n}`, com `ρ† = ρ`, `ρ ≥ 0` e `Tr(ρ)=1`.

### 1.2 Evolução

A evolução fechada é unitária:

```text
ρ' = U ρ U†,   U†U = I
```

### 1.3 Medição

Uma medida projetiva `{P_i}` produz o resultado `i` com probabilidade:

```text
p_i = Tr(P_i ρ)
```

e atualiza o estado para `P_i ρ P_i / p_i`. A soma das probabilidades é 1.

### 1.4 Composição

O estado conjunto de dois sistemas é `ρ_A ⊗ ρ_B` se forem independentes. Se não
forem separáveis, o estado é emaranhado.

## 2. Portas e álgebra

```text
X = [[0,1],[1,0]]
Z = [[1,0],[0,-1]]
H = (1/√2)[[1,1],[1,-1]]
CNOT = [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]]
```

Identidades verificadas no Lean 4 (`QuantumTrails.lean`):

- `H² = I`, `X² = I`, `Z² = I`;
- `H Z H = X`;
- `(1/√2)² = 1/2`, `(√2)² = 2`, `(2√2)² = 8`;
- `P(0)+P(1)=1`;
- CHSH clássico `S ≤ 2`;
- tabela-verdade do CNOT.

O Lean prova a álgebra; não prova a execução física.

## 3. Emaranhamento e Bell

O estado de Bell:

```text
|Φ⁺⟩ = (|00⟩ + |11⟩)/√2
```

A correlação de Bell para escolhas `a` e `b` é:

```text
E(a,b) = P(00) + P(11) − P(01) − P(10)
```

Para um modelo local determinístico, `|S| ≤ 2`, com

```text
S = E(a0,b0) + E(a0,b1) + E(a1,b0) − E(a1,b1)
```

A mecânica quântica permite `S = 2√2 ≈ 2,828` (limite de Tsirelson). O livro
mede `S = 2,383` no Guoji08; o valor é compatível com a violação, mas uma
execução não é prova estatística definitiva.

## 4. QFT

A transformada de Fourier quântica em `N = 2^n` dimensões:

```text
QFT|j⟩ = (1/√N) Σ_k e^{2πijk/N} |k⟩
```

Para `N=4`, a matriz é:

```text
(1/2) [[1,1,1,1],[1,i,−1,−i],[1,−1,1,−1],[1,−i,−1,i]]
```

A QFT é unitária; não é a FFT clássica. O livro usa a QFT de 3 qubits para
mostrar uniformização e fase, não para ensinar implementação eficiente.

## 5. Complexidade e algoritmos

| Classe | Ideia | Exemplo |
|---|---|---|
| **BPP** | probabilístico clássico com erro limitado | Monte Carlo |
| **BQP** | quântico com erro limitado | Shor, simulação |
| **NP** | verificação clássica eficiente | SAT |

O livro apresenta Deutsch–Jozsa, Grover e Shor como **panorama**, não como
implementação completa. A vantagem quântica depende de modelo de custo,
tamanho, ruído e comparação justa.

## 6. VQC e barren plateaus

Um classificador variacional usa um circuito parametrizado `U(θ)`, mede um
observável e minimiza uma perda:

```text
L(θ) = (1/M) Σ_i ℓ(⟨O⟩_i(θ), y_i)
```

O gradiente pode decair exponencialmente com o número de qubits — o **barren
plateau**. O livro mede acurácia em 2 e 4 qubits, mas não faz curva de
escalabilidade. A conclusão correta é limitada: “não observamos ruído benéfico
neste teste”, não “ruído benéfico não existe”.

## 7. Ruído e correção

Um canal quântico é um mapa completamente positivo que preserva traço (CPTP):

```text
ρ' = Σ_k E_k ρ E_k†,   Σ_k E_k†E_k = I
```

Exemplos:

- **bit flip:** `ρ' = (1−p)ρ + p XρX`;
- **phase flip:** `ρ' = (1−p)ρ + p ZρZ`;
- **depolarizing:** `ρ' = (1−p)ρ + p I/2`;
- **amplitude damping:** modelo de relaxação.

O livro cobre ruído de forma experimental e pedagógica; não cobre teoria
completa de canais, códigos estabilizadores ou surface codes em profundidade.
Para isso, a referência é Nielsen & Chuang e Fowler et al. (2012).

## 8. O que o livro cobre bem

- ponte entre ideia, circuito, código e hardware;
- leitura de counts e incerteza;
- comparação simulado × backend;
- interpretação de Bohm como lente;
- trilhas N0–N2 com prática manual;
- cálculo manual e notas de rodapé;
- limites explícitos e ledger de afirmações;
- verificação formal de identidades algébricas.

## 9. O que fica fora

| Tema | Onde estudar |
|---|---|
| Álgebra linear e postulados completos | Nielsen & Chuang (2000) |
| Algoritmos e complexidade | Nielsen & Chuang; Preskill (2018) |
| Canais, códigos e QEC | Nielsen & Chuang; Fowler et al. (2012) |
| Bohmian mechanics técnica | Bohm & Hiley (1993) |
| Filosofia da física | Bohm (1980); Peat (1997) |
| Física quântica geral | Eisberg & Resnick |
| Machine learning quântico | Cerezo et al. (2021); Havlíček et al. (2019) |

## 10. Comparação honesta

| Obra | Força | O que este livro não substitui |
|---|---|---|
| Nielsen & Chuang | referência completa de computação quântica | profundidade matemática e algoritmos |
| Preskill (2018) | panorama NISQ e complexidade | análise de fronteira |
| Bohm & Hiley | ontologia bohmiana técnica | fundamentação filosófica |
| Eisberg & Resnick | física quântica geral | curso completo de mecânica quântica |
| Qiskit Textbook | prática de código | tutoriais de framework |
| Este livro | integração didática em PT-BR | nenhuma das obras acima |

## 11. Referências {#profundidade-referencias}

NIELSEN, M. A.; CHUANG, I. L. *Quantum Computation and Quantum Information*.
Cambridge: Cambridge University Press, 2000.
DOI: <https://doi.org/10.1017/CBO9780511976667>.

PRESKILL, J. Quantum Computing in the NISQ era and beyond. *Quantum*, v. 2,
p. 79, 2018. DOI: <https://doi.org/10.22331/q-2018-08-06-79>.

BOHM, D.; HILEY, B. J. *The Undivided Universe*. London: Routledge, 1993.

BOHM, D. *Wholeness and the Implicate Order*. London: Routledge, 1980.

CEREZO, M. et al. Variational quantum algorithms. *Nature Reviews Physics*,
v. 3, p. 625–644, 2021. DOI: <https://doi.org/10.1038/s42254-021-00348-9>.

HAVLÍČEK, V. et al. Supervised learning with quantum-enhanced feature spaces.
*Nature*, v. 567, p. 209–212, 2019.
DOI: <https://doi.org/10.1038/s41586-019-0980-2>.

FOWLER, A. G.; MARIANTONI, M.; MARTINIS, J. M.; CLELAND, A. N. Surface codes:
Towards practical large-scale quantum computation. *Physical Review A*, v. 86,
p. 032324, 2012. DOI: <https://doi.org/10.1103/PhysRevA.86.032324>.

TEMME, K.; BRAVYI, S.; GAMBETTA, J. M. Error Mitigation for Short-Depth Quantum
Circuits. *Physical Review Letters*, v. 119, p. 180509, 2017.
DOI: <https://doi.org/10.1103/PhysRevLett.119.180509>.
