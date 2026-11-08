# Aprofundamento quântico: estados, canais, algoritmos e correção {#aprofundamento}

> **Para quem este apêndice existe.** O corpo do livro prioriza a ponte entre
> ideia, circuito, código e hardware. Este apêndice acrescenta a camada formal
> que falta para ler Nielsen & Chuang e Preskill com menos atrito. Ele **não**
> substitui essas obras: cobre definições, derivações curtas, teoremas com
> esboço e exercícios, não todos os detalhes técnicos.

## 1. Álgebra linear e estados {#ap-1-algebra}

Um estado puro de `n` qubits é um vetor unitário em `ℂ^{2^n}`:

```text
|ψ⟩ = Σ_{x∈{0,1}^n} α_x |x⟩,   Σ_x |α_x|² = 1.
```

O produto interno é `⟨φ|ψ⟩ = Σ_x φ_x* ψ_x`. Um operador `A` age como
`A|ψ⟩`; seu adjunto `A†` satisfaz `⟨φ|Aψ⟩ = ⟨A†φ|ψ⟩`. O comutador é
`[A,B] = AB − BA` e o anticomutador `{A,B} = AB + BA`.

Um estado misto é uma matriz densidade:

```text
ρ = Σ_i p_i |ψ_i⟩⟨ψ_i|,   p_i ≥ 0, Σ_i p_i = 1.
```

Propriedades: `ρ† = ρ`, `ρ ≥ 0`, `Tr ρ = 1`. Um estado é puro se e somente se
`Tr ρ² = 1`; caso contrário, `Tr ρ² < 1`. A pureza é `Tr ρ²`.

A decomposição espectral escreve `ρ = Σ_i λ_i |i⟩⟨i|`, com `λ_i ≥ 0` e
`Σ_i λ_i = 1`. O suporte é o espaço gerado pelos autovetores com `λ_i > 0`.

Para dois sistemas `A` e `B`, o traço parcial sobre `B` produz

```text
ρ_A = Tr_B ρ,   (ρ_A)_{ij} = Σ_k ρ_{ik,jk}.
```

O estado global é separável se `ρ = Σ_i p_i ρ_A^i ⊗ ρ_B^i`; caso contrário,
é emaranhado. A decomposição de Schmidt de um vetor puro é

```text
|ψ⟩_{AB} = Σ_i λ_i |a_i⟩_A |b_i⟩_B,   λ_i ≥ 0, Σ_i λ_i² = 1.
```

O número de Schmidt (quantidade de `λ_i > 0`) mede o emaranhamento do estado
puro. Qualquer estado `ρ_A` admite purificação: existe `|Ψ⟩_{RA}` tal que
`Tr_R |Ψ⟩⟨Ψ| = ρ_A`.

### Exercícios

1. Mostre que `Tr ρ² ≤ 1` e que a igualdade vale apenas para estado puro.
2. Calcule `ρ_A` para `|Φ⁺⟩ = (|00⟩ + |11⟩)/√2`.
3. Escreva a decomposição de Schmidt de `|Φ⁺⟩`.

## 2. Medição {#ap-2-medicao}

Uma medida projetiva é uma família de projetores `{P_i}` com `P_i² = P_i`,
`P_i† = P_i`, `Σ_i P_i = I`. A probabilidade e o estado posterior são

```text
p_i = Tr(P_i ρ),   ρ_i = P_i ρ P_i / p_i.
```

O valor esperado de um observável `A = Σ_i a_i P_i` é `⟨A⟩ = Tr(Aρ)`. A
variância é `Var(A) = ⟨A²⟩ − ⟨A⟩²`. Para observáveis `A` e `B`, a relação de
incerteza de Robertson é

```text
ΔA ΔB ≥ |⟨[A,B]⟩| / 2.
```

Uma medida generalizada (POVM) é uma família `{E_i}` com `E_i ≥ 0` e
`Σ_i E_i = I`; a probabilidade é `p_i = Tr(E_i ρ)`. POVMs não especificam
necessariamente o estado posterior. Toda POVM pode ser realizada como medida
projetiva em um espaço auxiliar (dilatação de Naimark).

### Exercícios

1. Verifique `P(0)+P(1)=1` para `ρ` de um qubit.
2. Mostre que `⟨X⟩² + ⟨Z⟩² ≤ 1` para um estado puro de qubit.
3. Construa uma POVM de três resultados para o qubit e interprete.

## 3. Canais quânticos {#ap-3-canais}

Um canal quântico é um mapa completamente positivo que preserva traço (CPTP):

```text
Φ(ρ) = Σ_k E_k ρ E_k†,   Σ_k E_k† E_k = I.
```

Os `E_k` são operadores de Kraus. A representação de Choi usa
`J(Φ) = Σ_{ij} |i⟩⟨j| ⊗ Φ(|i⟩⟨j|)`; `Φ` é completamente positivo se e somente
se `J(Φ) ≥ 0`.

Exemplos:

- **bit flip:** `E_0 = √(1−p) I`, `E_1 = √p X`;
- **phase flip:** `E_0 = √(1−p) I`, `E_1 = √p Z`;
- **depolarizing:** `Φ(ρ) = (1−p)ρ + p I/2`;
- **phase damping:** `Φ(ρ) = (1−p)ρ + p ZρZ`;
- **amplitude damping:** com `γ ∈ [0,1]`,

```text
E_0 = [[1, 0], [0, √(1−γ)]],   E_1 = [[0, √γ], [0, 0]].
```

A fidelidade entre `ρ` e `σ` é

```text
F(ρ,σ) = Tr √(√ρ σ √ρ),
```

com `F ∈ [0,1]`; para `ρ = |ψ⟩⟨ψ|`, `F = ⟨ψ|σ|ψ⟩`. A distância de traço é
`D(ρ,σ) = ½ Tr|ρ−σ|`. A distância de diamante mede a distinguibilidade de
canais; não é calculada neste livro.

### Exercícios

1. Verifique `Σ_k E_k†E_k = I` para amplitude damping.
2. Mostre que depolarizing em `p=1` leva qualquer qubit a `I/2`.
3. Compare phase damping e depolarizing para a população `Z`.

## 4. Emaranhamento e Bell {#ap-4-emaranhamento}

Para o estado de Bell `|Φ⁺⟩ = (|00⟩ + |11⟩)/√2`, medidas no plano `X–Z` com
ângulos `a` e `b` produzem

```text
E(a,b) = cos(a−b).
```

Com `a0=0`, `a1=π/2`, `b0=π/4`, `b1=−π/4`, o parâmetro CHSH é

```text
S = E(a0,b0) + E(a0,b1) + E(a1,b0) − E(a1,b1) = 2√2.
```

O limite clássico é `|S| ≤ 2`; o limite de Tsirelson é `2√2`. O resultado GJQ
no FAS-GPU, `S = 2,871094 ± 0,043506`, é consistente com `2√2` dentro de cerca
de um erro padrão e não excede Tsirelson de forma significativa.

O emaranhamento não permite sinalização mais rápida que a luz: as marginais
locais não dependem da escolha de medida do outro lado. A monogamia do
emaranhamento limita a partilha entre múltiplos sistemas; para estados puros,
`E(A:BC) ≥ E(A:B) + E(A:C)`.

### Exercícios

1. Deduza `E(a,b)=cos(a−b)` para `|Φ⁺⟩`.
2. Calcule `S` para os quatro pares de ângulos acima.
3. Explique por que `S>2` não permite comunicação superlumínica.

## 5. Algoritmos e complexidade {#ap-5-algoritmos}

### Deutsch–Jozsa

Dada `f:{0,1}^n→{0,1}` prometida constante ou balanceada, o algoritmo usa
`n` qubits de consulta e um ancilla:

```text
|0⟩|1⟩ → H^{⊗n} → U_f → H^{⊗n} → medida.
```

Se `f` é constante, a medida é `0^n` com probabilidade 1; se é balanceada, o
resultado é diferente de `0^n` com probabilidade 1. Uma consulta quântica
resolve o problema; classicamente, no pior caso, são necessárias `2^{n−1}+1`.

### Bernstein–Vazirani

Para `f(x) = a·x mod 2`, o algoritmo recupera `a` com uma consulta e `n`
qubits, contra `n` consultas clássicas no modelo de consulta.

### Grover

Com `N=2^n` itens e `M` soluções, seja `θ = arcsin(√(M/N))`. Após `k`
iterações, a probabilidade de sucesso é `sin²((2k+1)θ)`. O número ótimo é
`k ≈ (π/4)√(N/M)`. Grover oferece aceleração quadrática no modelo de consulta;
não é exponencial.

### QFT, fase e Shor

A QFT em `N=2^n` é

```text
QFT|j⟩ = (1/√N) Σ_{k=0}^{N−1} e^{2πijk/N} |k⟩.
```

A estimativa de fase, com `U|u⟩ = e^{2πiφ}|u⟩`, escreve `φ` nos qubits de
controle com precisão `2^{−m}`. O algoritmo de Shor reduz a fatoração à
determinação da ordem `r` de `a` módulo `N`; com `r` par e `a^{r/2} ≠ −1`,
`gcd(a^{r/2}±1,N)` fornece fatores. A implementação completa exige aritmética
modular reversível e correção de erro.

### Complexidade

| Classe | Ideia |
|---|---|
| **BPP** | probabilístico clássico, erro limitado |
| **BQP** | quântico, erro limitado |
| **NP** | verificação clássica eficiente |
| **QMA** | verificação quântica com testemunha |

Shor está em BQP; Grover é ótimo no modelo de consulta. Complexidade
assintótica não é desempenho no hardware atual: constante, ruído, conectividade
e custo de compilação importam.

### Exercícios

1. Mostre que Deutsch–Jozsa resolve o problema com uma consulta.
2. Deduza o número ótimo de iterações de Grover.
3. Explique por que a QFT não é a FFT clássica.

## 6. Correção de erro {#ap-6-qec}

O código de repetição de 3 qubits codifica `|0⟩→|000⟩` e `|1⟩→|111⟩`. Ele
corrige um bit flip, mas não um phase flip. O código de Shor combina repetição
e rotação de base para corrigir ambos.

O formalismo de estabilizadores descreve códigos por um grupo abeliano gerado
por operadores de Pauli `S_i` que comutam e satisfazem `S_i|ψ⟩ = |ψ⟩`. Um
código `[[n,k,d]]` usa `n` qubits físicos, `k` lógicos e distância `d`; corrige
`t = ⌊(d−1)/2⌋` erros.

O código de superfície é uma família de códigos estabilizadores Locais em 2D,
com limiar de erro da ordem de 1% para certos modelos. O teorema do limiar
afirma que, abaixo do limiar, é possível computar por tempo arbitrariamente
longo com overhead polilogarítmico; a prova e as constantes dependem do modelo
de ruído e do código.

### Exercícios

1. Verifique que o código de repetição corrige um bit flip.
2. Mostre por que ele não corrige um phase flip.
3. Explique a diferença entre distância e número de qubits.

## 7. VQC e barren plateaus {#ap-7-vqc}

Um circuito variacional prepara `|ψ(θ)⟩ = U(θ)|0⟩` e mede um observável `O`.
A perda é `L(θ) = ⟨ψ(θ)|O|ψ(θ)⟩`. Para uma porta `e^{−iθP/2}` com `P` Pauli,
a regra de parameter-shift é

```text
∂_θ L = ½ [L(θ+π/2) − L(θ−π/2)].
```

Em circuitos profundos e aleatórios, a variância do gradiente pode decair
exponencialmente com o número de qubits — o **barren plateau**. O fenômeno
depende da arquitetura, da inicialização, do observável e do ruído; não é uma
lei universal. O livro mede 2 e 4 qubits; isso não é uma curva de
escalabilidade.

### Exercícios

1. Deduza a regra de parameter-shift para uma porta de um qubit.
2. Explique por que a variância do gradiente pode decair com `n`.
3. Proponha um experimento para distinguir barren plateau de ruído.

## 8. Mapa de estudo {#ap-8-mapa}

| Tema | Nielsen & Chuang | Preskill | Neste livro |
|---|---|---|---|
| Postulados e densidade | caps. 2 | notas 1–3 | §1–2 |
| Canais e CPTP | cap. 8 | notas 3 | §3 |
| Emaranhamento/Bell | cap. 2, 12 | notas 2 | §4; cap. GJQ |
| Deutsch–Jozsa/Grover | cap. 6 | notas 6 | §5 |
| Shor/QFT | cap. 5 | notas 6 | §5 |
| QEC | cap. 10 | notas 7 | §6 |
| VQC | — | notas NISQ | §7 |

## 9. Limites deste apêndice {#ap-9-limites}

- Não contém todas as provas; alguns teoremas são enunciados com esboço.
- Não substitui Nielsen & Chuang para álgebra, canais e QEC.
- Não substitui Preskill para complexidade e fronteira NISQ.
- Não cobre hardware, calibração, códigos de superfície em detalhe ou
  tolerância a falhas completa.
- Não prova que o livro ensina melhor; a avaliação de eficácia continua
  sendo um protocolo.

## 10. Referências {#ap-10-referencias}

- NIELSEN, M. A.; CHUANG, I. L. *Quantum Computation and Quantum Information*.
  10th Anniversary ed. Cambridge: Cambridge University Press, 2010.
  DOI: <https://doi.org/10.1017/CBO9780511976667>.
- PRESKILL, J. Quantum Computing in the NISQ era and beyond. *Quantum*, v. 2,
  p. 79, 2018. DOI: <https://doi.org/10.22331/q-2018-08-06-79>.
- GOTTESMAN, D. Stabilizer codes and quantum error correction. Caltech,
  1997. arXiv:quant-ph/9705052.
- FOWLER, A. G. et al. Surface codes: towards practical large-scale quantum
  computation. *Physical Review A*, v. 86, 032324, 2012.
  DOI: <https://doi.org/10.1103/PhysRevA.86.032324>.
- CEREZO, M. et al. Variational quantum algorithms. *Nature Reviews Physics*,
  v. 3, p. 625–644, 2021. DOI: <https://doi.org/10.1038/s42254-021-00348-9>.
