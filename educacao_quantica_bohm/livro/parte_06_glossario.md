# Glossário {#glossario}

**Amplitude.** Número (real ou complexo) que descreve o peso de um estado de base.
A probabilidade é o quadrado do módulo.

**Bohm, David (1917–1992).** Físico teórico britânico-brasileiro. Propôs a
interpretação de onda piloto e uma filosofia de totalidade e diálogo.

**Bohmian mechanics.** Interpretação não local da mecânica quântica em que
partículas têm posições definidas e são guiadas pela função de onda.

**Cirq.** Biblioteca open source do Google para circuitos quânticos, com ênfase em
linhas de qubits e simulação.

**Colapso efetivo.** Na teoria de Bohm, o fato de a partícula terminar em uma das
componentes da função de onda após a interação com o aparelho, sem postular um
colapso fundamental.

**Configuração (espaço de).** Espaço de \(3N\) dimensões que descreve as posições
de \(N\) partículas. A função de onda de Bohm vive nesse espaço.

**Diálogo (bohminiano).** Prática coletiva de investigar suposições por meio de
escuta, suspensão de julgamento e desaceleração, sem buscar consenso forçado.

**Equivariância.** Propriedade pela qual a distribuição \(|\psi|^2\) é preservada
pela dinâmica de Bohm. É a base da regra de Born na teoria.

**Emaranhamento.** Correlação quântica entre partes de um sistema, descrita por um
estado conjunto não separável.

**Esfera de Bloch.** Representação geométrica do estado de um qubit.

**Estado de Bell.** Estado maximalmente emaranhado de dois qubits, como
\((|00\rangle+|11\rangle)/\sqrt{2}\).

**Explicate order.** Ordem explícita: o mundo das coisas separadas e localizadas.

**Holomovimento.** Termo de Bohm para o fluxo dinâmico do qual emergem as formas
explícitas.

**Implicate order.** Ordem implicada: a totalidade de relações que se desdobra no
mundo explícito.

**Interpretação.** Leitura filosófica de uma teoria física que preserva as
previsões experimentais.

**Não localidade.** Dependência instantânea entre partes separadas no espaço. Em
Bohm, é explícita na equação do guia.

**Onda piloto.** Função de onda que guia o movimento das partículas na teoria de
Bohm.

**PennyLane.** Biblioteca open source para computação quântica diferenciável.

**Qiskit.** Biblioteca open source da IBM para circuitos, estados e visualização.

**Qubit.** Unidade de informação quântica descrita por duas amplitudes.

**Regra de Born.** \(P(0)=|\alpha|^2\), \(P(1)=|\beta|^2\).

**Suspensão de suposições.** Gesto de colocar uma crença entre parênteses para
examiná-la, sem necessariamente abandoná-la.

**Totalidade.** Ideia de que o todo não se reduz à soma de partes independentes.

# Referências {#referencias}

BELL, J. S. On the Einstein Podolsky Rosen paradox. *Physics*, v. 1, n. 3,
p. 195–200, 1964.

BLACK, P.; WILIAM, D. Assessment and classroom learning. *Assessment in
Education*, v. 5, n. 1, p. 7–74, 1998.

BLOOM, B. S. Learning for mastery. *Evaluation Comment*, v. 1, n. 2, 1968.

BOHM, D. *Quantum Theory*. New York: Prentice-Hall, 1951.

BOHM, D. *Causality and Chance in Modern Physics*. London: Routledge, 1957.

BOHM, D. *Wholeness and the Implicate Order*. London: Routledge, 1980.

BOHM, D. *Thought as a System*. London: Routledge, 1992.

BOHM, D. *On Dialogue*. Edited by Lee Nichol. London: Routledge, 1996.

BOHM, D.; HILEY, B. J. *The Undivided Universe: An Ontological Interpretation of
Quantum Theory*. London: Routledge, 1993.

BOHM, D.; PEAT, F. D. *Science, Order, and Creativity*. New York: Bantam, 1987.

BRASIL. Ministério da Educação. *Base Nacional Comum Curricular*. Brasília:
MEC, 2018.

BRASIL. Conselho Nacional de Educação. *Normas sobre Computação na Educação
Básica — Complemento à BNCC*. Brasília: CNE, 2022.

BRUNER, J. S. *Toward a Theory of Instruction*. Cambridge: Harvard University
Press, 1966.

CIRQ DEVELOPERS. *Cirq Documentation*. Disponível em:
https://quantumai.google/cirq. Acesso em: 6 nov. 2026.

FEYNMAN, R. P. Simulating physics with computers. *International Journal of
Theoretical Physics*, v. 21, n. 6–7, p. 467–488, 1982.

HOLLAND, P. R. *The Quantum Theory of Motion: An Account of the de Broglie–Bohm
Causal Interpretation of Quantum Mechanics*. Cambridge: Cambridge University
Press, 1993.

MAYER, R. E. *Multimedia Learning*. 2. ed. Cambridge: Cambridge University Press,
2009.

NIELSEN, M. A.; CHUANG, I. L. *Quantum Computation and Quantum Information*.
Cambridge: Cambridge University Press, 2000.

NIST. *FIPS 203, 204 e 205*: padrões de criptografia pós-quântica. Gaithersburg:
NIST, 2024.

PENNYLANE DEVELOPERS. *PennyLane Documentation*. Disponível em:
https://docs.pennylane.ai. Acesso em: 6 nov. 2026.

PRESKILL, J. Quantum computing in the NISQ era and beyond. *Quantum*, v. 2,
p. 79, 2018.

QISKIT DEVELOPERS. *Qiskit Documentation*. Disponível em:
https://docs.quantum.ibm.com. Acesso em: 6 nov. 2026.

ROEDIGER, H. L.; KARPICKE, J. D. Test-enhanced learning: taking memory tests
improves long-term retention. *Psychological Science*, v. 17, n. 3, p. 249–255,
2006.

SWELLER, J. Cognitive load during problem solving: effects on learning.
*Cognitive Science*, v. 12, n. 2, p. 257–285, 1988.

VYGOTSKY, L. S. *Mind in Society: The Development of Higher Psychological
Processes*. Cambridge: Harvard University Press, 1978.

# Anexo: instalação e Colab {#anexo}

## 1. Abrir o notebook

1. Acesse `colab.research.google.com`.
2. **Arquivo → Fazer upload de notebook**.
3. Selecione `AULA_BOHM_LABORATORIO.ipynb`.
4. Execute a primeira célula para checar as bibliotecas.
5. Se faltar alguma, rode no início:

```bash
!pip install -q pennylane qiskit cirq pylatexenc
```

6. **Ambiente de execução → Executar tudo**.

## 2. Versões testadas

| Biblioteca | Versão testada |
|---|---|
| PennyLane | 0.45.1 |
| Cirq | 1.7.0 |
| Qiskit | 2.6.2 |
| pylatexenc | 2.11 |
| Python | 3.14 |

Versões diferentes podem mudar detalhes de desenho, mas não os conceitos.

## 3. Se algo der errado

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ModuleNotFoundError: pennylane` | biblioteca ausente | rode o `pip install` acima |
| `ModuleNotFoundError: cirq` | biblioteca ausente | rode o `pip install` acima |
| `ModuleNotFoundError: qiskit` | biblioteca ausente | rode o `pip install` acima |
| desenho do circuito estranho | versão diferente | use o diagrama textual ou atualize |
| figura não aparece | célula não executada | rode a célula de ambiente e a célula da figura |
| resultado diferente de 0,5 | convenção de ordem ou amostragem | confira a ordem dos qubits e o número de tiros |

## 4. Licenças

PennyLane, Cirq e Qiskit são projetos open source com licenças próprias. Consulte
os repositórios oficiais antes de redistribuir código. Este livro é material
didático; as figuras foram geradas por código e podem ser reutilizadas em sala
com atribuição.

## 5. Como citar

> OPENCODE ECOSYSTEM CORE. *Bohm na Escola: onda piloto, diálogo e totalidade no
> ensino de informação quântica — edição black*. 1. ed. 2026. Material didático.

Para redistribuição, mantenha a atribuição, a seção de limites e a nota de que
Bohm é apresentado como uma interpretação entre várias.