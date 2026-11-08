# Trilhas por nível: do fundamental ao PhD {#trilhas}

> Um livro não ensina sozinho. Uma sequência ensina. A diferença entre os dois
> é o que este capítulo tenta construir.

## 1. O princípio: manual → simulação → hardware → síntese

Toda trilha deste capítulo usa o mesmo ciclo de quatro passos. O ciclo é o
mesmo no fundamental e no doutorado; o que muda é a profundidade.

| Passo | O que o leitor faz | Por que existe |
|---|---|---|
| **1. Manual** | Prever, desenhar, contar com cartões, moedas, dados e papel | O corpo e a mão criam uma âncora concreta antes do símbolo |
| **2. Simulação** | Rodar o mesmo experimento em Python, com 1024 tiros | Comparar a previsão manual com uma máquina ideal |
| **3. Hardware** | Enviar ao backend, ler counts, task ID e ruído | Confrontar o ideal com a matéria |
| **4. Síntese** | Escrever o que provou, o que não provou e qual é a próxima pergunta | Transformar resultado em evidência e evidência em crítica |

Em cada passo há um **contraste clássico**: um modelo clássico que tenta
explicar o mesmo fenômeno. O contraste não é enfeite; é o que impede que o
leitor confunda “quântico” com “misterioso”.

A escolha do ciclo não é arbitrária. Ela combina evidências sobre aprendizagem
ativa (FREEMAN et al., 2014, DOI:
<https://doi.org/10.1073/pnas.1319030111>), prática distribuída (CEPEDA et al.,
2006, DOI: <https://doi.org/10.1037/0033-2909.132.3.354>), teste com feedback
(ROEDIGER; KARPICKE, 2006, DOI:
<https://doi.org/10.1111/j.1467-9280.2006.01693.x>) e feedback orientado a
critérios (HATTIE; TIMPERLEY, 2007, DOI:
<https://doi.org/10.3102/003465430298487>). A literatura sobre ensino de
mecânica quântica mostra que a intuição clássica não desaparece com uma
definição: ela precisa ser confrontada por experimento e por contraste
(KRIJTENBURG et al., 2017, DOI:
<https://doi.org/10.1103/PhysRevPhysEducRes.13.010109>).

O princípio pedagógico é simples: **primeiro a previsão, depois o resultado**.
Quem prevê erra com informação; quem só vê o resultado aprende a repetir.

## 2. Mapa das trilhas

| Trilha | Para quem | Duração | Nível do livro | Entrada | Saída |
|---|---|---|---|---|---|
| **A — Despertar** | 10–14 anos, fundamental | 12 semanas | N0 | frações, porcentagens, leitura fluente | caderno de 12 experimentos |
| **B — Fundamentos** | 14–17 anos, médio | 6 meses | N0→N1 | álgebra, funções, probabilidade básica | relatório de 1 experimento |
| **C — Graduação** | 18+, universidade | 1 ano | N1→N2 | cálculo, álgebra linear, probabilidade | replicação de 1 experimento |
| **D — Mestrado** | pós-graduação | 1 ano | N2 | mecânica quântica, estatística, programação | protocolo de pesquisa |
| **E — Doutorado/PhD** | doutorado | 2–3 anos | N2→PhD | mestrado, pergunta própria | artigo + pacote de replicação |
| **P — Professor** | docentes e divulgadores | 8 semanas | N0–N2 | prática de sala | kit de 30 dias + rubrica |

As trilhas não são idades rígidas. São **compromissos**: cada uma exige um
tempo, um artefato e um critério. Um leitor de 12 anos pode começar na A; um
adulto curioso também. Um estudante de graduação pode começar na C, mas só
avança se cumprir os critérios da B que faltarem.

### 2.0 Ferramentas por trilha {#ferramentas-por-trilha-niveis}

| Trilha | Ferramentas mínimas | O que o leitor aprende |
|---|---|---|
| **A** | papel, moeda, cartão; Python com adulto | prever, contar, comparar |
| **B** | Qiskit, NumPy | montar circuito, ler counts |
| **C** | Qiskit, PennyLane, Cirq, Matplotlib | comparar três APIs |
| **D** | Qiskit Aer, SciPy, Optuna | ruído, otimização, estatística |
| **E** | stack completa + Git + Lean 4 | replicar e auditar |
| **P** | Qiskit, projetor, resultados documentados | ensinar sem depender de hardware |

A instalação, o acesso à plataforma GJQ, a execução dos scripts, a leitura dos
resultados e a auditoria estão no capítulo **Trilhas de ferramentas**
(`#trilhas-ferramentas`). Ele foi escrito para quem nunca abriu um terminal.

## 2.1 Verificação formal com Lean 4

As identidades matemáticas usadas nas trilhas foram formalizadas em Lean 4 +
Mathlib no arquivo:

```text
livro-core/lean/QuantumTrails.lean
```

Verificação:

```bash
cd livro-core/lean
lake env lean QuantumTrails.lean
```

O arquivo compila sem `sorry` e sem `admit` no ambiente desta edição
(Lean 4.35.0; Mathlib no commit `d13f23b723b8a846827a245b89c10fc7d3f11612`).

| Teorema | O que prova | Onde é usado |
|---|---|---|
| `H_mul_H` | `H² = I` | Circuitos, interferência |
| `X_mul_X` | `X² = I` | Porta X, NOT quântico |
| `Z_mul_Z` | `Z² = I` | Fase, H-Z-H |
| `H_mul_Z_mul_H` | `H Z H = X` | Interferência e base X |
| `sqrt2_sq` | `(√2)² = 2` | Normalização, CHSH |
| `inv_sqrt2_sq` | `(1/√2)² = 1/2` | Hadamard |
| `quantum_chsh_sq` | `(2√2)² = 8` | Limite quântico de CHSH |
| `prob_sum` | `P(0)+P(1)=1` | Medição |
| `chsh_classical` | `S ≤ 2` para modelo local determinístico | Contraste clássico |
| `cnot` | Tabela-verdade do CNOT | Circuitos |

O teorema `chsh_classical` é o contraste mais importante da trilha B: ele
percorre as 16 combinações de escolhas de Alice e Bob e verifica que
`a0·b0 + a0·b1 + a1·b0 − a1·b1 ≤ 2`. O valor quântico `2√2` é formalizado no
caso do estado de Bell e das escolhas de observáveis usadas no livro:
`chsh_bell_eigen` prova que `|Φ+⟩` é autovetor de `CHSH` com autovalor `2√2`, e
`chsh_bell_expectation` prova o valor esperado. O limite de Tsirelson geral não
é formalizado; o caso específico é.

O arquivo também formaliza modelos **fenomenológicos** de ruído:
`phaseDamping_p0`, `phaseDamping_coh` e `phaseDamping_coh_abs_le` provam que o
phase damping preserva a população e não aumenta a coerência;
`depolarizing_p0`, `depolarizing_zero`, `depolarizing_one_p0`,
`depolarizing_p0_nonneg` e `depolarizing_p0_le_one` provam a fórmula e a
normalização do depolarizing. Não é uma formalização completa de canais CPTP:
é o modelo de população e coerência real que o livro usa.

> **O que o Lean não prova:** counts de hardware, calibração, fidelidade,
> ruído, interpretação de Bohm ou vantagem quântica. Essas afirmações são
> empíricas e dependem de dados, task IDs e desenho experimental. O Lean prova
> a matemática; o experimento prova (ou não) a física.

## 3. Trilha A — Despertar (N0, fundamental)

### 3.1 Para quem

Leitor de 10 a 14 anos, com leitura fluente, frações, porcentagens e noção de
probabilidade. Não precisa de álgebra, vetores ou programação. Precisa de um
adulto por perto para a parte de Python e hardware.

### 3.2 Duração e ritmo

- **12 semanas**, 3 sessões por semana, 30–40 minutos.
- 1 conceito por semana, com 3 lentes: ideia, prática e checkpoint.
- 1 experimento manual por semana; 1 simulação por quinzena; 1 demonstração de
  hardware no final.

### 3.3 Sequência

| Fase | Semanas | Conceitos | Laudas | Experimento |
|---|---|---|---|---|
| 1. Diferença e medida | 1–2 | C001–C005 | L0001–L0050 | E01, E02, E03 |
| 2. Amplitude e probabilidade | 3–4 | C003–C006 | L0021–L0060 | E03, E18 |
| 3. Fase e interferência | 5–6 | C007–C008 | L0061–L0080 | E04 |
| 4. Emaranhamento e Bell | 7–8 | C009–C010 | L0081–L0100 | E05, E07 |
| 5. Portas e circuitos | 9–10 | C021–C026 | L0201–L0260 | E05, E11 |
| 6. Hardware e ética | 11–12 | C041–C046, C081–C090 | L0401–L0460, L0801–L0900 | E14 + demonstração |

### 3.4 Prática manual

- **E01:** um cartão com “0” e outro com “1”; 1024 sorteios com reposição.
  Contar, tabelar, calcular `P(0)=N0/1024`.
- **E03:** uma moeda honesta, 1024 lançamentos; comparar com `H|0⟩` simulado.
  A moeda tem lado definido; o qubit não tem valor escondido.
- **E18:** 10 séries de 10 lançamentos; calcular a dispersão; comparar com
  `EP=√(p(1−p)/N)`.
- **E05:** dois cartões correlacionados (00 e 11) vs duas moedas independentes;
  medir a correlação e ver a diferença.
- **E07:** tabela de quatro configurações; contar `00`, `11`, `01`, `10`;
  calcular `E` e `S` com a fórmula da lauda.

#### Cálculo da trilha A

| Conta | Fórmula | Exemplo |
|---|---|---|
| Frequência | `p = N_evento/N` | `530/1024 = 0,5176` |
| Erro padrão | `EP = √(p(1−p)/N)` | `√(0,5176×0,4824/1024) = 0,0156` |
| Intervalo de 95% | `p ± 1,96·EP` | `0,5176 ± 0,0306` |
| Diferença para 50% | `|p−0,5|/EP` | `|0,5176−0,5|/0,0156 = 1,13` |

A diferença de 1,13 erro padrão não é evidência forte contra 50%. É assim que
se aprende a distinguir “número” de “evidência”.

### 3.5 Python (com adulto)

```bash
python 08_experimentos_18.py --sim --only E03
python 08_experimentos_18.py --sim --only E09
python 08_experimentos_18.py --report
```

O adulto ajuda a abrir o terminal, ativar o `.venv` e ler `dados/E03.json`.
O leitor não precisa escrever código; precisa **prever** o resultado antes de
rodar e **comparar** com a previsão.

### 3.6 Hardware (demonstração supervisionada)

Um único job no Guoji08, 1024 tiros, com a conta de um adulto. Se não houver
acesso, usar os resultados registrados no livro (com data e task ID) e tratar
como “hardware documentado”, não como “hardware ao vivo”.

### 3.7 Contraste clássico

| Modelo clássico | Modelo quântico | Contraste teórico | Prática |
|---|---|---|---|
| Interruptor (0/1) | Qubit (α, β) | O bit tem um valor; o qubit tem amplitudes | Cartão vs moeda girando |
| Moeda honesta | H\|0⟩ | 50% clássico vs 50% quântico; a diferença aparece na fase | 1024 lançamentos vs 1024 tiros |
| Duas moedas independentes | Estado de Bell | Correlação clássica vs correlação não separável | Dois cartões vs pares 00/11 |
| Sorteio clássico | QRNG | A origem da aleatoriedade | Dado vs H\|0⟩ |

### 3.8 Checkpoints

1. Qual é a diferença entre um bit e um qubit?
2. O que significa `P(0)=0,5` antes de medir?
3. Por que a moeda não é um qubit?
4. O que a fase muda na interferência?
5. O que o estado de Bell tem que duas moedas não têm?
6. O que `S=2,383` prova e o que não prova?
7. Por que 1024 tiros não são uma prova definitiva?
8. Onde está o erro de leitura no E01?
9. O que você faria para testar se o backend é estável?
10. Qual pergunta você ainda não sabe responder?

### 3.9 Critério de passagem

| Critério | Evidência | Limiar |
|---|---|---|
| Checkpoints | 10 respostas escritas | ≥ 8 com critério |
| Manual | E01, E03, E18 no caderno | contas conferidas |
| Python | E03 e E09 rodados | JSON + previsão escrita |
| Hardware | demonstração ou resultado documentado | task ID anotado |
| Síntese | 1 página | pergunta, resultado, limite |
| Diálogo | apresentar a um adulto | responder 1 contrapergunta |

### 3.10 Artefato

**Caderno do despertar:** 12 experimentos, cada um com previsão, counts,
cálculo, resultado e uma frase de limite. É o passaporte para a Trilha B.

### 3.11 O que não fazer

- Decorar o gabarito sem fazer a conta.
- Rodar o script sem prever o resultado.
- Usar hardware sem adulto.
- Dizer “entendi” quando só viu o número.

## 4. Trilha B — Fundamentos (N0→N1, médio)

### 4.1 Para quem

Leitor de 14 a 17 anos, com álgebra, funções, probabilidade básica e noção de
gráfico. Ainda não precisa de números complexos, matrizes ou cálculo.

### 4.2 Duração e ritmo

- **6 meses**, 2 sessões por semana, 60 minutos.
- 1 parte por mês; 1 experimento por quinzena; 1 relatório por mês.

### 4.3 Sequência

| Fase | Meses | Conceitos | Laudas | Experimento |
|---|---|---|---|---|
| 1. Revisão de informação | 1 | C001–C010 | L1001–L1100 | E05, E07 |
| 2. Portas e circuitos | 2 | C021–C030 | L1201–L1300 | E11, E15 |
| 3. Ferramentas | 3 | C031–C040 | L1301–L1400 | E09, E16 |
| 4. Hardware e ruído | 4 | C041–C050 | L1401–L1500 | E02, E14 |
| 5. Experimentos | 5 | C051–C060 | L1501–L1600 | E06, E10 |
| 6. Ética e projeto | 6 | C081–C090, C091–C100 | L1801–L2000 | E07 + projeto |

### 4.4 Prática manual

- Tabela-verdade de X, H, Z, CNOT; multiplicação de matrizes 2×2.
- Diagrama do circuito de Bell no papel; conferir com o desenho do Qiskit.
- Tabela CHSH completa; calcular `E` e `S` à mão.
- Construir um “meio-somador” clássico com portas lógicas e comparar com o
  circuito quântico reversível.
- Calcular `2^n` amplitudes para n=2, 3, 4 e estimar a memória.

#### Cálculo da trilha B: CHSH

| Configuração | `00` | `11` | `01` | `10` | `E` |
|---|---:|---:|---:|---:|---:|
| E00 | 401 | 405 | 106 | 112 | +0,5742 |
| E01 | 401 | 406 | 105 | 112 | +0,5762 |
| E10 | 399 | 403 | 111 | 111 | +0,5664 |
| E11 | 77 | 94 | 434 | 419 | −0,6660 |

`E = (N00 + N11 − N01 − N10)/1024`.

`S = E00 + E01 + E10 − E11 = 0,5742 + 0,5762 + 0,5664 + 0,6660 = 2,3828`.

O limite clássico é `|S| ≤ 2`; o ideal quântico é `2√2 ≈ 2,828`. A demonstração
do limite clássico e a identidade `(2√2)² = 8` estão no arquivo Lean
`livro-core/lean/QuantumTrails.lean` (teoremas `chsh_classical` e
`quantum_chsh_sq`).

### 4.5 Python

```bash
python 08_experimentos_18.py --sim --only E05
python 08_experimentos_18.py --sim --only E07
python 08_experimentos_18.py --sim --only E09
python 08_experimentos_18.py --sim --only E16
```

Depois, no caderno: mudar `--shots` para 2048 e `--seed` para 7; comparar a
dispersão. O leitor começa a escrever pequenos circuitos no Qiskit:

```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.h(0); qc.cx(0, 1); qc.measure([0, 1], [0, 1])
```

### 4.6 Hardware

Um job no Guoji08 ou Baihua (E05 ou E07), 1024 tiros. Comparar com o simulado:
`P(00)+P(11)`, `S`, task ID, data. Se o job falhar, registrar o erro e repetir.

### 4.7 Contraste clássico

| Modelo clássico | Modelo quântico | Contraste teórico | Prática |
|---|---|---|---|
| NOT clássico | Porta X | X é unitária e reversível; NOT é clássico | Tabela-verdade vs matriz |
| AND/OR | CNOT | CNOT é reversível; AND não é | Meio-somador vs circuito |
| Correlação clássica | Bell/CHSH | Limite clássico 2; quântico 2√2 | Tabela CHSH |
| DFT | QFT | DFT clássica vs transformada quântica | Matriz 4×4 vs circuito |
| Simulação clássica | Statevector | 2^n amplitudes; memória exponencial | Conta de 2^n |

### 4.8 Checkpoints

1. Qual é a matriz de X, H e Z?
2. Por que `H Z H = X`?
3. O que o CNOT faz com `|10⟩`?
4. Qual é a diferença entre correlação clássica e violação de CHSH?
5. Por que o limite clássico de S é 2?
6. O que a QFT faz com `|000⟩`?
7. Quantas amplitudes tem um estado de 4 qubits?
8. O que é erro de leitura?
9. O que o hardware mudou em relação ao simulador?
10. O que você faria para melhorar a estimativa de S?
11. Qual é o limite da analogia do meio-somador?
12. Qual pergunta você levaria para a Trilha C?

### 4.9 Critério de passagem

| Critério | Evidência | Limiar |
|---|---|---|
| Checkpoints | 12 respostas | ≥ 9 com critério |
| Manual | matrizes, circuito, CHSH | contas conferidas |
| Python | 4 experimentos | JSON + comparação |
| Hardware | 1 job | task ID + counts |
| Relatório | 2 páginas | pergunta, método, resultado, limite |
| Diálogo | apresentar a 2 colegas | responder 2 contraperguntas |

### 4.10 Artefato

**Relatório de fundamentos:** 2 páginas com circuito, counts, S, incerteza e
limite. É o passaporte para a Trilha C.

## 5. Trilha C — Graduação (N1→N2)

### 5.1 Para quem

Estudante de graduação com cálculo, álgebra linear, probabilidade e alguma
programação. Já sabe o que é vetor, matriz e derivada.

### 5.2 Duração e ritmo

- **1 ano**, 2 semestres, 4–6 horas por semana.
- 1 parte por mês; 1 experimento por mês; 1 replicação no final.

### 5.3 Sequência

| Fase | Meses | Conceitos | Laudas | Experimento |
|---|---|---|---|---|
| 1. Informação e medida | 1 | C001–C010 | L1001–L1100 | E05, E07 |
| 2. Bohm e interpretação | 2 | C011–C020 | L1101–L1200 | E04, E17 |
| 3. Circuitos e ferramentas | 3–4 | C021–C040 | L1201–L1400 | E06, E10 |
| 4. Hardware e ruído | 5 | C041–C050 | L1401–L1500 | E14, E16 |
| 5. Experimentos | 6 | C051–C060 | L1501–L1600 | E10, E12 |
| 6. Matemática | 7–8 | C061–C070 | L1601–L1700 | E12, E16 |
| 7. Ética e projeto | 9–12 | C081–C100 | L1801–L2000 | projeto |

### 5.4 Prática manual

- Matriz densidade 2×2; calcular `Tr(ρ)`, `Tr(ρ²)`, autovalores.
- Produto tensorial de dois qubits; ordem dos fatores.
- QFT de 3 qubits: matriz 8×8 e padrão de probabilidades.
- Entropia de Shannon vs von Neumann; comparar estados puros e mistos.
- Propagação de incerteza; intervalo de confiança para uma proporção.

#### Cálculo da trilha C: densidade, entropia e QFT

| Objeto | Conta | Resultado |
|---|---|---|
| Estado puro \|+⟩ | `ρ = ½[[1,1],[1,1]]`; `Tr(ρ)=1`; `Tr(ρ²)=1` | puro |
| Estado misto | `ρ = ½ I`; `Tr(ρ²)=0,5` | misto |
| Entropia | `S = −Tr(ρ log₂ ρ)`; para `½I`, `S=1` bit | 1 bit |
| QFT de 3 qubits | `P(000)=1/8=0,125`; medido `123/1024=0,1201` | 12,01% |
| GHZ | `(418+389)/1024 = 807/1024` | 78,81% |

A comparação entre `Tr(ρ²)=1` e `Tr(ρ²)=0,5` é o contraste clássico-quântico
mais direto desta trilha: um estado puro tem uma descrição probabilística; um
estado misto tem uma mistura que não se reduz a um vetor.

### 5.5 Python

- Qiskit: circuitos, statevector, density matrix, transpilação.
- PennyLane: QNode e gradiente.
- Cirq: momentos e circuitos.
- Simulador ruidoso; leitura de calibração; mitigação de leitura.
- VQC com Optuna; múltiplas seeds.

### 5.6 Hardware

Dois backends (Guoji08 e Baihua), GHZ, CHSH e VQC. Comparar fidelidade proxy,
erro de leitura, fila e calibração. Guardar task IDs e datas.

### 5.7 Contraste clássico

| Modelo clássico | Modelo quântico | Contraste teórico | Prática |
|---|---|---|---|
| Entropia de Shannon | Entropia de von Neumann | Distribuição vs matriz densidade | Calcular as duas |
| Probabilidade vetorial | Matriz densidade | Estado puro vs misto | `Tr(ρ²)` |
| Lógica clássica | Lógica quântica | Distributividade e contexto | CHSH |
| Algoritmo clássico | Deutsch–Jozsa/Grover/Shor | Complexidade e oráculo | Simular 2–3 qubits |
| Simulação clássica | Simulação quântica | Custo exponencial | 2^n |

### 5.8 Checkpoints

1. Qual é a diferença entre estado puro e misto?
2. O que `Tr(ρ²)=1` diz sobre o estado?
3. Como se calcula a entropia de von Neumann?
4. O que a QFT faz com um estado de base?
5. Por que o VQC pode ter barren plateau?
6. O que a mitigação de leitura corrige e o que não corrige?
7. Por que o GHZ é frágil?
8. O que a fidelidade proxy não mede?
9. Como comparar dois backends de forma justa?
10. O que um intervalo de confiança acrescenta a um count?
11. O que Bohm explica e o que ele não explica?
12. Qual é o limite do seu experimento?
13. O que você replicaria em outra seed?
14. O que você faria com 10× mais shots?
15. Qual pergunta você levaria para o mestrado?

### 5.9 Critério de passagem

| Critério | Evidência | Limiar |
|---|---|---|
| Checkpoints | 15 respostas | ≥ 12 com critério |
| Manual | densidade, QFT, entropia | contas conferidas |
| Python | 5 experimentos | código + JSON |
| Hardware | 2 backends | task IDs + comparação |
| Replicação | 1 experimento | 5 páginas + código + dados |
| Diálogo | seminário de 15 min | responder 3 contraperguntas |

### 5.10 Artefato

**Replicação de graduação:** 5 páginas, código, dados, incerteza e limites.
É o passaporte para a Trilha D.

## 6. Trilha D — Mestrado (N2)

### 6.1 Para quem

Mestrando com mecânica quântica, estatística e programação. Já sabe ler um
artigo e reproduzir um experimento simples.

### 6.2 Duração e ritmo

- **1 ano**, 10–15 horas por semana.
- 1 protocolo, 1 piloto, 1 experimento, 1 relatório.

### 6.3 Sequência

| Fase | Meses | Conceitos | Laudas | Experimento |
|---|---|---|---|---|
| 1. Ruído e canais | 1–2 | C041–C050 | L2401–L2500 | E14 |
| 2. Experimentos | 3–4 | C051–C060 | L2501–L2600 | E06, E10 |
| 3. Matemática | 5–6 | C061–C070 | L2601–L2700 | E12, E16 |
| 4. Ética e projeto | 7–12 | C081–C100 | L2801–L3000 | projeto |

### 6.4 Prática manual

- Modelos de ruído: bit flip, phase flip, depolarizing, amplitude damping.
- Código de repetição de 3 qubits; syndrome e correção.
- Tomografia de 1 qubit; máxima verossimilhança.
- Bootstrap; intervalo de confiança; poder estatístico.
- Randomização de benchmarking; curvas de decaimento.

#### Cálculo da trilha D: ruído e incerteza

| Conta | Fórmula | Exemplo |
|---|---|---|
| Fidelidade total | `F_total ≈ F^k` | `0,9754¹⁰ ≈ 0,779` |
| Decaimento T1 | `P(t)=e^{−t/T1}` | em `t=T1`, `P=1/e≈0,368` |
| Erro de leitura | `(P(1|0)+P(0|1))/2` | `(0,008+0,008)/2=0,008` |
| Intervalo de 95% | `p ± 1,96√(p(1−p)/N)` | `0,5 ± 0,0306` com N=1024 |
| Sobreposição | `Σ_b min(p_sim[b],p_real[b])` | 0,941 no Bell |

O ponto central é que `F_total` cai exponencialmente com o número de portas.
Dez portas de dois qubits a 97,54% já reduzem a fidelidade para ~78%; isso
explica por que “mais qubits” não é sinônimo de “melhor resultado”.

### 6.5 Python

- Qiskit Aer com modelos de ruído.
- Mitigação de leitura; zero-noise extrapolation.
- Tomografia; `qiskit-experiments` quando disponível.
- VQC com ruído; curvas de acurácia; múltiplas seeds.
- Empacotamento: `requirements.txt`, seed, ambiente, dados.

### 6.6 Hardware

Caracterizar um backend: T1, T2, erro de leitura, fidelidade de porta.
Rodar GHZ/CHSH/VQC; comparar com simulação ruidosa; repetir em outra data.
Registrar calibração, fila e task IDs.

### 6.7 Contraste clássico

| Modelo clássico | Modelo quântico | Contraste teórico | Prática |
|---|---|---|---|
| Ruído clássico | Canal quântico | Bit flip vs phase flip | Simular canais |
| Código de repetição clássico | Código quântico | Cópia vs no-cloning | Circuito de 3 qubits |
| Tomografia clássica | Tomografia quântica | Amostra vs matriz densidade | Medir 3 bases |
| Otimização clássica | VQE/QAOA | Paisagem e barren plateau | Curva de custo |
| Monte Carlo clássico | Amostragem quântica | Distribuição vs amplitude | Comparar histogramas |

### 6.8 Checkpoints

1. Qual é a diferença entre bit flip e phase flip?
2. O que o código de repetição corrige e o que não corrige?
3. Por que não se pode copiar um qubit?
4. O que a tomografia de 1 qubit exige?
5. O que a mitigação de leitura corrige?
6. O que a extrapolação de ruído assume?
7. O que um intervalo de confiança bootstrap acrescenta?
8. O que é um barren plateau?
9. O que a calibração do backend muda entre duas datas?
10. Qual é o limite estatístico do seu experimento?

### 6.9 Critério de passagem

| Critério | Evidência | Limiar |
|---|---|---|
| Protocolo | 3 páginas | pergunta, hipótese, método, análise |
| Piloto | 1 experimento | dados + código |
| Checkpoints | 10 respostas | ≥ 8 com critério |
| Hardware | caracterização | T1/T2/leitura + task IDs |
| Relatório | 10 páginas | resultado, incerteza, limite, próximo passo |
| Diálogo | apresentação de 20 min | responder 5 contraperguntas |

### 6.10 Artefato

**Protocolo de mestrado:** pergunta, hipótese, método, análise, limites e
próximo passo. É o passaporte para a Trilha E.

## 7. Trilha E — Doutorado/PhD (N2→PhD)

### 7.1 Para quem

Doutorando com pergunta própria, método e capacidade de replicar. Já passou
pela Trilha D ou tem equivalente.

### 7.2 Duração e ritmo

- **2–3 anos**, 20–30 horas por semana.
- 1 pergunta original, 1 experimento, 1 artigo, 1 replicação.

### 7.3 Sequência

| Fase | Meses | Foco | Produto |
|---|---|---|---|
| 1. Pergunta | 1–3 | lacuna, hipótese, falsificabilidade | proposta |
| 2. Método | 4–6 | desenho, poder, pré-registro | protocolo |
| 3. Piloto | 7–9 | viabilidade, ruído, calibração | dados piloto |
| 4. Experimento | 10–18 | coleta, análise, robustez | resultados |
| 5. Artigo | 19–24 | escrita, revisão, replicação | manuscrito |
| 6. Defesa | 25–36 | banca, correções, depósito | tese |

### 7.4 Prática manual

- Derivações e provas; contas de ordem de grandeza.
- Análise de poder; tamanho de amostra; erro tipo I e II.
- Pré-registro; critérios de exclusão; plano de análise.
- Revisão por pares simulada; resposta a parecer.

#### Cálculo da trilha E: tamanho de amostra e poder

| Conta | Fórmula | Exemplo |
|---|---|---|
| Amostra para proporção | `n ≈ 1,96² p(1−p)/d²` | `p=0,5`, `d=0,05` → `384,16` |
| Erro padrão | `EP = √(p(1−p)/n)` | `√(0,25/385) = 0,0255` |
| Intervalo de 95% | `p ± 1,96·EP` | `0,5 ± 0,050` |
| Efeito mínimo detectável | `d ≈ 1,96·EP` | `d ≈ 0,050` |

O `p`-valor não mede a probabilidade de a hipótese ser verdadeira; ele mede a
probabilidade de um resultado tão extremo quanto o observado, supondo a
hipótese nula. A discussão completa está em Wasserstein e Lazar (2016, DOI:
<https://doi.org/10.1080/00031305.2016.1154108>) e Ioannidis (2005, DOI:
<https://doi.org/10.1371/journal.pmed.0020124>).

### 7.5 Python

- Código de pesquisa reprodutível; ambiente fixo; seeds.
- Estatística: bootstrap, Bayes, intervalos, testes.
- Mitigação de erro; tomografia; caracterização.
- Pacote de dados: JSON/CSV, metadados, hashes, DOI.

### 7.6 Hardware

Experimento original em hardware, ou simulação de alto nível com validação
experimental. Múltiplos backends, múltiplas datas, replicação independente.
Registrar calibração, fila, task IDs e limites.

### 7.7 Contraste clássico

| Modelo clássico | Modelo quântico | Contraste teórico | Prática |
|---|---|---|---|
| Complexidade BPP | BQP | O que “vantagem” significa | Comparar algoritmos |
| Estatística clássica | Inferência quântica | Amostra vs estado | Intervalos |
| Simulação clássica | Simulação quântica | Tensor network vs circuito | Custo |
| ML clássico | QML | Barren plateau, generalização | Curva de aprendizado |
| Replicação clássica | Replicação quântica | Ruído e calibração | Réplica |

### 7.8 Checkpoints

1. Qual é a lacuna que sua pergunta preenche?
2. Qual é a hipótese rival?
3. O que falsificaria sua hipótese?
4. Qual é o tamanho de efeito que você espera?
5. Qual é o poder estatístico do seu desenho?
6. O que o ruído do backend faz com sua conclusão?
7. O que você replicaria em outro backend?
8. O que seu resultado não prova?

### 7.9 Critério de passagem

| Critério | Evidência | Limiar |
|---|---|---|
| Proposta | 10 páginas | pergunta, hipótese, método, impacto |
| Piloto | dados + código | viabilidade demonstrada |
| Artigo | manuscrito | submetível, com limites |
| Replicação | pacote | código + dados + DOI |
| Banca | defesa | aprovação |
| Ética | declaração | consentimento, dados, conflitos |

### 7.10 Artefato

**Artigo de doutorado + pacote de replicação.** O artigo sem o pacote é uma
promessa; o pacote sem o artigo é um depósito. A tese é a ponte entre os dois.

## 8. Trilha P — Professor

### 8.1 Para quem

Professores, divulgadores e monitores que querem usar o livro em sala ou em
oficinas.

### 8.2 Duração e ritmo

- **8 semanas**, 1 encontro por semana, 90 minutos.
- 1 plano de aula por semana; 1 rubrica; 1 demonstração de hardware.

### 8.3 Sequência

| Semana | Tema | Produto |
|---|---|---|
| 1 | O contrato de leitura | plano de 30 dias |
| 2 | N0 e prática manual | 3 experimentos de papel |
| 3 | N1 e circuitos | 1 circuito no Qiskit |
| 4 | Hardware e ruído | 1 job demonstrativo |
| 5 | Ética e LGPD | plano de segurança |
| 6 | Rubrica e avaliação | rubrica de 5 critérios |
| 7 | Roda de diálogo | roteiro de 9 minutos |
| 8 | Oficina piloto | aula de 90 minutos + feedback |

### 8.4 Prática manual

- Montar os experimentos de papel da Trilha A.
- Construir a tabela CHSH e o circuito de Bell no papel.
- Calcular a conta de um count e de um erro padrão.
- Escrever um plano de aula de 7 minutos por lauda.

#### Cálculo da trilha P: tempo e rubrica

| Conta | Fórmula | Resultado |
|---|---|---|
| Trilha de 30 dias | `30 × 7 min` | 210 min = 3,5 h |
| Um conceito | `10 lentes × 7 min` | 70 min |
| Um nível | `100 conceitos × 70 min` | 7000 min ≈ 117 h |
| Rubrica | `5 critérios × 4 níveis` | 20 células |
| Oficina | `90 min = 10 laudas × 7 min + 20 min` | 10 laudas + síntese |

O professor não precisa ensinar as 3000 laudas: precisa escolher 10 laudas, um
experimento manual e uma pergunta de saída. O resto é o aluno que faz.

### 8.5 Python e hardware

- Rodar `08_experimentos_18.py --sim` em sala.
- Demonstrar um job no Guoji08; se não houver acesso, usar os resultados
  documentados.
- Ensinar o aluno a ler o JSON, o task ID e o limite.

### 8.6 Contraste clássico

Usar as mesmas tabelas das Trilhas A–E, adaptadas à turma. O contraste é o
mesmo; muda a linguagem.

### 8.7 Checkpoints

1. Qual é a pergunta motriz da sua aula?
2. Qual experimento manual abre a aula?
3. Qual conceito o aluno pode confundir?
4. Qual é o critério de passagem?
5. O que você faz se não houver hardware?
6. Como você avalia sem overclaim?
7. Como você protege dados e chaves?
8. O que o aluno leva para a próxima aula?

### 8.8 Critério de passagem

| Critério | Evidência | Limiar |
|---|---|---|
| Plano | 30 dias | 30 laudas + 4 experimentos |
| Oficina | 90 minutos | participação + feedback |
| Rubrica | 5 critérios | aplicável e transparente |
| Segurança | plano | chave, dados, consentimento |
| Diálogo | roda de 9 min | roteiro cumprido |

### 8.9 Artefato

**Kit do professor:** planos, rubricas, scripts, demonstração de hardware e
roteiro de diálogo.

## 9. Critérios de passagem: o que vale em qualquer trilha

| Evidência | O que mostra | Limiar |
|---|---|---|
| Checkpoints | compreensão conceitual | ≥ 80% com critério |
| Conta manual | domínio do número | reproduzir sem script |
| Experimento | prática e previsão | previsão + resultado + limite |
| Relatório | síntese | pergunta, método, resultado, incerteza, limite |
| Código | reprodutibilidade | roda do zero, com seed |
| Hardware | contato com a matéria | task ID + comparação |
| Diálogo | crítica e escuta | responder contrapergunta |
| Ética | responsabilidade | sem chave, sem dado pessoal, sem overclaim |

**Regra:** se o leitor não consegue explicar o que o resultado **não** prova,
ele ainda não passou. A nota sozinha não é critério.

## 10. Comparações clássicas: o fio transversal

| Nível | Modelo clássico | Modelo quântico | Contraste teórico | Prática |
|---|---|---|---|---|
| A | Bit, moeda, dois cartões | Qubit, medição, Bell | Valor definido vs amplitude; correlação vs emaranhamento | 1024 lançamentos vs 1024 tiros |
| B | Portas lógicas, CHSH clássico, DFT | X/H/CNOT, CHSH quântico, QFT | Reversibilidade; limite 2 vs 2√2 | Tabela-verdade, S, QFT 3 qubits |
| C | Shannon, probabilidade, algoritmo clássico | Von Neumann, densidade, Deutsch–Jozsa | Entropia; estado puro vs misto; complexidade | `Tr(ρ²)`, QFT, simulador |
| D | Ruído clássico, repetição, tomografia | Canal quântico, QEC, tomografia quântica | No-cloning; síndrome; máxima verossimilhança | Canais, código de 3 qubits, 3 bases |
| E | BPP, estatística clássica, ML clássico | BQP, inferência quântica, QML | Vantagem; generalização; replicação | Artigo + pacote |
| P | O mesmo, adaptado | O mesmo, adaptado | O mesmo | Aula + demonstração |

## 11. Segurança, ética e limites

- **Hardware** só com conta autorizada e, para menores, com adulto responsável.
- **API key** nunca no código, no caderno ou no PDF; rotacione se vazar.
- **Dados pessoais** não entram no experimento; LGPD e consentimento.
- **Overclaim:** não diga “vantagem quântica”, “ruído benéfico” ou “prova de
  emaranhamento” sem o desenho que sustente.
- **Bohm** é uma interpretação entre várias; a ordem implicada é uma proposta
  filosófica, não uma teoria confirmada.
- **Hardware** tem ruído, fila e calibração; um resultado não é uma curva.

## 12. Adaptações

- **Sem computador:** faça o manual, use os resultados documentados e deixe o
  Python para depois. O livro foi escrito para o PDF bastar.
- **Sem hardware:** simule, compare com os resultados registrados e trate o
  hardware como etapa opcional nas Trilhas A e B.
- **Neurodivergência:** use as 10 lentes como portas de entrada, sessões curtas,
  apoio visual e escolha de ordem. O contrato dos 7 minutos ajuda; a nota de
  cálculo é opcional.
- **Leitor adiantado:** faça o diagnóstico da trilha seguinte; se passar nos
  critérios, avance. Não pule o manual: ele é o que sustenta a intuição.
- **Turma heterogênea:** use a Trilha A como base e a Trilha B como extensão;
  o mesmo experimento serve a níveis diferentes com lentes diferentes.

## 13. O fio condutor entre as trilhas

| De → para | O que o leitor leva | O que muda |
|---|---|---|
| A → B | Previsão, contagem, limite | Do gesto para a matriz |
| B → C | Circuito, CHSH, QFT | Da matriz para a densidade |
| C → D | Replicação, ruído, estatística | Do resultado para o protocolo |
| D → E | Protocolo, análise, ética | Do protocolo para a pergunta original |
| E → P | Artigo, pacote, banca | Da pesquisa para o ensino |

A sequência não é uma escada de idades; é uma escada de compromissos. Cada
degrau tem um artefato, um critério e uma pergunta que só o leitor pode
responder. O livro oferece o mapa; o tempo e a prática fazem o resto.

## 14. Referências das trilhas

As fontes conceituais de cada experimento estão nas fichas `F001`–`F100`. A
lista completa, com 44 DOIs ativos, está na **Verificação de DOIs**. As
referências abaixo sustentam as escolhas pedagógicas e metodológicas das
trilhas.

### Pedagogia e aprendizagem

FREEMAN, S. et al. Active learning increases student performance in science,
engineering, and mathematics. *PNAS*, v. 111, n. 23, p. 8410–8415, 2014.
DOI: <https://doi.org/10.1073/pnas.1319030111>.

DESLAURIERS, L. et al. Measuring actual learning versus feeling of learning in
response to being actively engaged in the classroom. *PNAS*, v. 116, n. 39,
p. 19251–19257, 2019. DOI: <https://doi.org/10.1073/pnas.1821936116>.

ROEDIGER, H. L.; KARPICKE, J. D. Test-Enhanced Learning. *Psychological
Science*, v. 17, n. 3, p. 249–255, 2006.
DOI: <https://doi.org/10.1111/j.1467-9280.2006.01693.x>.

CEPEDA, N. J. et al. Distributed practice in verbal recall tasks: A review and
quantitative synthesis. *Psychological Bulletin*, v. 132, n. 3, p. 354–380,
2006. DOI: <https://doi.org/10.1037/0033-2909.132.3.354>.

HATTIE, J.; TIMPERLEY, H. The Power of Feedback. *Review of Educational
Research*, v. 77, n. 1, p. 81–112, 2007.
DOI: <https://doi.org/10.3102/003465430298487>.

KRIJTENBURG, H. K. E.; DEPREZ, E. van den B.; VAN DER VEEN, J. T. Insights into
teaching quantum mechanics in secondary and lower undergraduate education.
*Physical Review Physics Education Research*, v. 13, p. 010109, 2017.
DOI: <https://doi.org/10.1103/PhysRevPhysEducRes.13.010109>.

### Quântica

NIELSEN, M. A.; CHUANG, I. L. *Quantum Computation and Quantum Information*.
Cambridge: Cambridge University Press, 2000.
DOI: <https://doi.org/10.1017/CBO9780511976667>.

PRESKILL, J. Quantum Computing in the NISQ era and beyond. *Quantum*, v. 2,
p. 79, 2018. DOI: <https://doi.org/10.22331/q-2018-08-06-79>.

BELL, J. S. On the Einstein Podolsky Rosen paradox. *Physics Physique Fizika*,
v. 1, n. 3, p. 195–200, 1964.
DOI: <https://doi.org/10.1103/PhysicsPhysiqueFizika.1.195>.

CLAUSER, J. F.; HORNE, M. A.; SHIMONY, A.; HOLT, R. A. Proposed Experiment to
Test Local Hidden-Variable Theories. *Physical Review Letters*, v. 23, n. 15,
p. 880–884, 1969. DOI: <https://doi.org/10.1103/PhysRevLett.23.880>.

ASPECT, A.; GRANGIER, P.; ROGER, G. Experimental Test of Bell's Inequalities
Using Time-Varying Analyzers. *Physical Review Letters*, v. 49, n. 25,
p. 1804–1807, 1982. DOI: <https://doi.org/10.1103/PhysRevLett.49.1804>.

HENSEN, B. et al. Loophole-free Bell inequality violation using electron spins
separated by 1.3 kilometres. *Nature*, v. 526, p. 682–686, 2015.
DOI: <https://doi.org/10.1038/nature15759>.

ZUREK, W. H. Decoherence, einselection, and the quantum origins of the
classical. *Reviews of Modern Physics*, v. 75, p. 715, 2003.
DOI: <https://doi.org/10.1103/RevModPhys.75.715>.

CEREZO, M. et al. Variational quantum algorithms. *Nature Reviews Physics*,
v. 3, p. 625–644, 2021. DOI: <https://doi.org/10.1038/s42254-021-00348-9>.

HAVLÍČEK, V. et al. Supervised learning with quantum-enhanced feature spaces.
*Nature*, v. 567, p. 209–212, 2019.
DOI: <https://doi.org/10.1038/s41586-019-0980-2>.

SCHULD, M.; BERGHOLM, V.; GOGOLIN, C.; GROSS, D.; KILLORAN, N. Evaluating
analytic gradients on quantum hardware. *Physical Review A*, v. 99, p. 032331,
2019. DOI: <https://doi.org/10.1103/PhysRevA.99.032331>.

MCCLEAN, J. R.; BOIXO, S.; SMELYANSKIY, V. N.; BABBUSH, R.; NEVEN, H. Barren
plateaus in quantum neural network training landscapes. *Nature Communications*,
v. 9, p. 4812, 2018. DOI: <https://doi.org/10.1038/s41467-018-07090-4>.

WANG, S. et al. Noise-induced barren plateaus in variational quantum algorithms.
*Nature Communications*, v. 12, p. 6961, 2021.
DOI: <https://doi.org/10.1038/s41467-021-27045-6>.

TEMME, K.; BRAVYI, S.; GAMBETTA, J. M. Error Mitigation for Short-Depth Quantum
Circuits. *Physical Review Letters*, v. 119, p. 180509, 2017.
DOI: <https://doi.org/10.1103/PhysRevLett.119.180509>.

FOWLER, A. G.; MARIANTONI, M.; MARTINIS, J. M.; CLELAND, A. N. Surface codes:
Towards practical large-scale quantum computation. *Physical Review A*, v. 86,
p. 032324, 2012. DOI: <https://doi.org/10.1103/PhysRevA.86.032324>.

ARUTE, F. et al. Quantum supremacy using a programmable superconducting
processor. *Nature*, v. 574, p. 505–510, 2019.
DOI: <https://doi.org/10.1038/s41586-019-1666-5>.

IBM QUANTUM. Evidence for the utility of quantum computing before fault
tolerance. *Nature*, v. 618, p. 500–505, 2023.
DOI: <https://doi.org/10.1038/s41586-023-06096-3>.

GIOVANNETTI, V.; LLOYD, S.; MACCONE, L. Advances in quantum metrology.
*Nature Photonics*, v. 5, p. 222–229, 2011.
DOI: <https://doi.org/10.1038/nphoton.2011.35>.

### Método, reprodutibilidade e ética

OPEN SCIENCE COLLABORATION. Estimating the reproducibility of psychological
science. *Science*, v. 349, n. 6251, aac4716, 2015.
DOI: <https://doi.org/10.1126/science.aac4716>.

WASSERSTEIN, R. L.; LAZAR, N. A. The ASA Statement on p-Values: Context,
Process, and Purpose. *The American Statistician*, v. 70, n. 2, p. 129–133,
2016. DOI: <https://doi.org/10.1080/00031305.2016.1154108>.

IOANNIDIS, J. P. A. Why Most Published Research Findings Are False. *PLoS
Medicine*, v. 2, n. 8, e124, 2005.
DOI: <https://doi.org/10.1371/journal.pmed.0020124>.

WILKINSON, M. D. et al. The FAIR Guiding Principles for scientific data
management and stewardship. *Scientific Data*, v. 3, p. 160018, 2016.
DOI: <https://doi.org/10.1038/sdata.2016.18>.

BRASIL. *Lei nº 13.709, de 14 de agosto de 2018* — Lei Geral de Proteção de
Dados Pessoais (LGPD). Brasília, 2018. Disponível em:
<http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm>.

### Bohm

BOHM, D. A Suggested Interpretation of the Quantum Theory in Terms of “Hidden”
Variables. I. *Physical Review*, v. 85, n. 2, p. 166–179, 1952.
DOI: <https://doi.org/10.1103/PhysRev.85.166>.

BOHM, D.; HILEY, B. J. *The Undivided Universe: An Ontological Interpretation
of Quantum Theory*. London: Routledge, 1993.

PEAT, F. David. *Infinite Potential: The Life and Times of David Bohm*.
Reading, MA: Addison-Wesley, 1997.
