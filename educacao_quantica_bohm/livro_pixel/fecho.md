# Glossário de bolso {#glossario}

| Termo | Definição mínima |
|---|---|
| **Bit** | menor diferença clássica: 0 ou 1 |
| **Qubit** | estado descrito por duas amplitudes; a medição produz um resultado |
| **Amplitude** | número que dá peso a um estado de base; probabilidade = módulo ao quadrado |
| **Medição** | processo que produz um resultado e atualiza o estado |
| **Base** | conjunto de estados em relação ao qual medimos |
| **Fase** | relação entre amplitudes; invisível na medição isolada, visível na interferência |
| **Emaranhamento** | correlação quântica não separável entre partes |
| **Bell** | estado maximalmente emaranhado de dois qubits |
| **GHZ** | generalização do Bell para três ou mais qubits |
| **Onda piloto** | interpretação de Bohm: a função de onda guia partículas com posição definida |
| **Não localidade** | dependência entre partes separadas; não permite signaling |
| **Ordem implicada** | proposta filosófica de totalidade; analogia, não teoria testável |
| **QASM 2.0** | linguagem textual para circuitos quânticos |
| **Transpilação** | adaptação do circuito às portas e conexões do hardware |
| **PennyLane** | biblioteca de circuitos quânticos diferenciáveis |
| **Cirq** | biblioteca do Google com linhas de qubits |
| **Qiskit** | biblioteca da IBM para circuitos, estados e visualização |
| **gjq-client** | SDK Python da nuvem Guoji/Tiangong |
| **MCP** | protocolo que expõe ferramentas de nuvem a agentes |
| **API key** | credencial secreta de acesso; trate como senha |
| **Fidelidade proxy** | fração de resultados ideais observada; não prova emaranhamento |
| **QBER** | taxa de erro quântica em uma chave peneirada |

# Referências e créditos {#referencias}

## Como as citações funcionam

Cada conceito tem uma **ficha de evidência** (`F001`–`F100`). A ficha traz a
fonte primária, o que foi medido, o que não prova, uma prática, uma leitura
complementar e o DOI. No rodapé de cada lauda, o link `[Fxxx]` leva à ficha; o
link `[Gxxx]` leva ao gabarito. A lista completa de verificação, com **49
referências** e **44 DOIs ativos**, está em **Verificação de DOIs**, antes deste
glossário. As obras abaixo são as fontes estruturantes do livro.

## Referências estruturantes

SHANNON, C. E. A Mathematical Theory of Communication. *Bell System Technical
Journal*, v. 27, n. 3, p. 379–423, 1948.
DOI: <https://doi.org/10.1002/j.1538-7305.1948.tb01338.x>.

BELL, J. S. On the Einstein Podolsky Rosen paradox. *Physics Physique Fizika*,
v. 1, n. 3, p. 195–200, 1964.
DOI: <https://doi.org/10.1103/PhysicsPhysiqueFizika.1.195>.

BOHM, D. A Suggested Interpretation of the Quantum Theory in Terms of “Hidden”
Variables. I. *Physical Review*, v. 85, n. 2, p. 166–179, 1952.
DOI: <https://doi.org/10.1103/PhysRev.85.166>.

BOHM, D. *Wholeness and the Implicate Order*. London: Routledge, 1980.

BOHM, D. *On Dialogue*. London: Routledge, 1996.

BOHM, D.; HILEY, B. J. *The Undivided Universe*. London: Routledge, 1993.

CLAUSER, J. F.; HORNE, M. A.; SHIMONY, A.; HOLT, R. A. Proposed Experiment to
Test Local Hidden-Variable Theories. *Physical Review Letters*, v. 23, n. 15,
p. 880–884, 1969. DOI: <https://doi.org/10.1103/PhysRevLett.23.880>.

ASPECT, A.; GRANGIER, P.; ROGER, G. Experimental Test of Bell's Inequalities
Using Time-Varying Analyzers. *Physical Review Letters*, v. 49, n. 25,
p. 1804–1807, 1982. DOI: <https://doi.org/10.1103/PhysRevLett.49.1804>.

HENSEN, B. et al. Loophole-free Bell inequality violation using electron spins
separated by 1.3 kilometres. *Nature*, v. 526, p. 682–686, 2015.
DOI: <https://doi.org/10.1038/nature15759>.

NIELSEN, M. A.; CHUANG, I. L. *Quantum Computation and Quantum Information*.
Cambridge: Cambridge University Press, 2000.
DOI: <https://doi.org/10.1017/CBO9780511976667>.

PRESKILL, J. Quantum Computing in the NISQ era and beyond. *Quantum*, v. 2,
p. 79, 2018. DOI: <https://doi.org/10.22331/q-2018-08-06-79>.

CEREZO, M. et al. Variational quantum algorithms. *Nature Reviews Physics*,
v. 3, p. 625–644, 2021. DOI: <https://doi.org/10.1038/s42254-021-00348-9>.

HAVLÍČEK, V. et al. Supervised learning with quantum-enhanced feature spaces.
*Nature*, v. 567, p. 209–212, 2019.
DOI: <https://doi.org/10.1038/s41586-019-0980-2>.

SCHULD, M.; BERGHOLM, V.; GOGOLIN, C.; GROSS, D.; KILLORAN, N. Evaluating
analytic gradients on quantum hardware. *Physical Review A*, v. 99, p. 032331,
2019. DOI: <https://doi.org/10.1103/PhysRevA.99.032331>.

ZUREK, W. H. Decoherence, einselection, and the quantum origins of the
classical. *Reviews of Modern Physics*, v. 75, p. 715, 2003.
DOI: <https://doi.org/10.1103/RevModPhys.75.715>.

ARUTE, F. et al. Quantum supremacy using a programmable superconducting
processor. *Nature*, v. 574, p. 505–510, 2019.
DOI: <https://doi.org/10.1038/s41586-019-1666-5>.

IBM QUANTUM. Evidence for the utility of quantum computing before fault
tolerance. *Nature*, v. 618, p. 500–505, 2023.
DOI: <https://doi.org/10.1038/s41586-023-06096-3>.

FOWLER, A. G.; MARIANTONI, M.; MARTINIS, J. M.; CLELAND, A. N. Surface codes:
Towards practical large-scale quantum computation. *Physical Review A*, v. 86,
p. 032324, 2012. DOI: <https://doi.org/10.1103/PhysRevA.86.032324>.

BENNETT, C. H. et al. Teleporting an unknown quantum state via dual classical
and Einstein-Podolsky-Rosen channels. *Physical Review Letters*, v. 70, n. 13,
p. 1895–1899, 1993. DOI: <https://doi.org/10.1103/PhysRevLett.70.1895>.

BENNETT, C. H.; WIESNER, S. J. Communication via one- and two-particle
operators on Einstein-Podolsky-Rosen states. *Physical Review Letters*, v. 69,
n. 20, p. 2881–2884, 1992. DOI: <https://doi.org/10.1103/PhysRevLett.69.2881>.

GROVER, L. K. A fast quantum mechanical algorithm for database search.
In: *Proceedings of the 28th Annual ACM Symposium on Theory of Computing*,
1996. p. 212–219. DOI: <https://doi.org/10.1145/237814.237866>.

SHOR, P. W. Polynomial-Time Algorithms for Prime Factorization and Discrete
Logarithms on a Quantum Computer. *SIAM Journal on Computing*, v. 26, n. 5,
p. 1484–1509, 1997. DOI: <https://doi.org/10.1137/S0097539795293172>.

LLOYD, S. Universal Quantum Simulators. *Science*, v. 273, n. 5278,
p. 1073–1077, 1996. DOI: <https://doi.org/10.1126/science.273.5278.1073>.

RAUSSENDORF, R.; BROWNE, D. E. A One-Way Quantum Computer. *Physical Review
Letters*, v. 86, n. 22, p. 5188–5191, 2001.
DOI: <https://doi.org/10.1103/PhysRevLett.86.5188>.

BIAMONTE, J. et al. Quantum machine learning. *Nature*, v. 549, p. 195–202,
2017. DOI: <https://doi.org/10.1038/nature23474>.

GIOVANNETTI, V.; LLOYD, S.; MACCONE, L. Advances in quantum metrology.
*Nature Photonics*, v. 5, p. 222–229, 2011.
DOI: <https://doi.org/10.1038/nphoton.2011.35>.

GISIN, N.; RIBORDY, G.; TITTEL, W.; ZBINDEN, H. Quantum cryptography.
*Reviews of Modern Physics*, v. 74, p. 145, 2002.
DOI: <https://doi.org/10.1103/RevModPhys.74.145>.

FEYNMAN, R. P. Simulating physics with computers. *International Journal of
Theoretical Physics*, v. 21, p. 467–488, 1982.
DOI: <https://doi.org/10.1007/BF02650179>.

MCCLEAN, J. R.; BOIXO, S.; SMELYANSKIY, V. N.; BABBUSH, R.; NEVEN, H. Barren
plateaus in quantum neural network training landscapes. *Nature Communications*,
v. 9, p. 4812, 2018. DOI: <https://doi.org/10.1038/s41467-018-07090-4>.

WANG, S. et al. Noise-induced barren plateaus in variational quantum algorithms.
*Nature Communications*, v. 12, p. 6961, 2021.
DOI: <https://doi.org/10.1038/s41467-021-27045-6>.

TEMME, K.; BRAVYI, S.; GAMBETTA, J. M. Error Mitigation for Short-Depth Quantum
Circuits. *Physical Review Letters*, v. 119, p. 180509, 2017.
DOI: <https://doi.org/10.1103/PhysRevLett.119.180509>.

EMERSON, J.; ALICKI, R.; ZYCZKOWSKI, K. Scalable noise estimation with random
unitary operators. *Journal of Optics B*, v. 7, p. S347, 2005.
DOI: <https://doi.org/10.1088/1464-4266/7/10/021>.

FREEMAN, S. et al. Active learning increases student performance in science,
engineering, and mathematics. *PNAS*, v. 111, n. 23, p. 8410–8415, 2014.
DOI: <https://doi.org/10.1073/pnas.1319030111>.

DESLAURIERS, L. et al. Measuring actual learning versus feeling of learning in
response to being actively engaged in the classroom. *PNAS*, v. 116, n. 39,
p. 19251–19257, 2019. DOI: <https://doi.org/10.1073/pnas.1821936116>.

KRIJTENBURG, H. K. E.; DEPREZ, E. van den B.; VAN DER VEEN, J. T. Insights into
teaching quantum mechanics in secondary and lower undergraduate education.
*Physical Review Physics Education Research*, v. 13, p. 010109, 2017.
DOI: <https://doi.org/10.1103/PhysRevPhysEducRes.13.010109>.

FAIR. The FAIR Guiding Principles for scientific data management and
stewardship. *Scientific Data*, v. 3, p. 160018, 2016.
DOI: <https://doi.org/10.1038/sdata.2016.18>.

BRASIL. Ministério da Educação. *Base Nacional Comum Curricular*. Brasília, 2018.

BRASIL. Conselho Nacional de Educação. *Normas sobre Computação na Educação
Básica — Complemento à BNCC*. Brasília, 2022.

BRASIL. *Lei nº 13.709, de 14 de agosto de 2018* — Lei Geral de Proteção de
Dados Pessoais (LGPD). Brasília, 2018.

PENNYLANE. *PennyLane: Automatic differentiation of hybrid quantum-classical
computations*. Documentação oficial, consultada em novembro de 2026.
Disponível em: <https://docs.pennylane.ai>.

CIRQ. *Cirq: A Python framework for creating, editing, and invoking quantum
circuits*. Documentação oficial, consultada em novembro de 2026.
Disponível em: <https://quantumai.google/cirq>.

QISKIT. *Qiskit 0.44.0*. Zenodo, 2020.
DOI: <https://doi.org/10.5281/zenodo.2573505>.

CIQUANTA. *Portal do Centro Internacional de Computação e Tecnologias Quânticas
do Estado da Paraíba*. Disponível em: <https://ciquanta.secties.pb.gov.br>.
Acesso em: 6 nov. 2026.

TIANGONG / CETC-ICQ. *Quantum Computing Platform User Guide* e *Quantum
Programming Framework User Guide*. Disponível em:
<https://tiangongqs.com/docs/quantum/>. Acesso em: 6 nov. 2026.

GUOJI QUANTUM. *gjq-client* e *gjq-runtime-mcp-server*. Repositórios públicos,
Apache 2.0. Acesso em: 6 nov. 2026.

MARCELO CLARO. *Beneficial Quantum Noise in Variational Quantum Classifiers*.
Repositório público usado como **inspiração** para a pergunta sobre ruído; os
resultados deste livro não replicam o estudo e não devem ser apresentados como
confirmação da hipótese.

> **Créditos de fontes:** Atkinson Hyperlegible, Press Start 2P, VT323 e Noto
> Serif CJK SC (SIL Open Font License 1.1); DejaVu Sans (Bitstream Vera).
> Qiskit, PennyLane, Cirq e `gjq-client` (Apache 2.0); NumPy e SciPy (BSD);
> Matplotlib (PSF); Optuna (MIT). Arte pixel gerada por código. Figuras de
> resultados reais geradas a partir dos JSONs em `dados_hardware/`.
> Tiangong/CETC-ICQ, CIQuanta, Guoji08 e Baihua pertencem aos seus respectivos
> operadores; as menções são informativas e não implicam endosso, patrocínio ou
> vínculo institucional.

# Como citar {#como-citar}

> LARANJEIRA, Marcelo Claro. *3000 laudas de física quântica: do bit ao todo —
> Bohm, onda piloto e informação quântica do fundamental ao PhD*. 1. ed.
> Brasil: Edição do autor, 2026.

Projeto e infraestrutura editorial: **OpenCode Ecosystem Core**.

Para redistribuição, mantenha a atribuição, a licença CC BY-NC-SA 4.0, a seção
de limites e a nota de que Bohm é uma interpretação entre várias; resultados de
backend têm ruído e não generalizam automaticamente.