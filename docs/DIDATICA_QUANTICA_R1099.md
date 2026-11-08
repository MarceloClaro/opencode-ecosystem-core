# Didática quântica — fontes e atribuição (R1099)

**Data:** 2026-11-08
**Objetivo:** registrar como o livro usa o Qiskit Textbook, o qmlcourse e a documentação Tiangong para conferir sequência, exercícios e linguagem, sem copiar assets e sem alegar eficácia pedagógica.

## 1. Fontes

| Fonte | Licença | Uso |
|---|---|---|
| <https://github.com/Qiskit/textbook> | Apache-2.0 | sequência de circuitos, algoritmos e exercícios |
| <https://github.com/quantum-ods/qmlcourse> | CC BY 4.0 | trilha de QML, notebooks e progressão |
| <https://tiangongqs.com/docs/quantum/ProgrammingQuantumCircuits.html> | documentação oficial | exemplos de Bell, GHZ, Hadamard/SWAP e CHSH |
| <https://tiangongqs.com/docs/quantum/QuantumProgrammingFramework.html> | documentação oficial | SDK GJQ, backends, Sampler/Estimator, MPS e sessões |
| <https://tiangongqs.com/docs/quantum/JupyterNotebookUserGuide.html> | documentação oficial | ambiente Jupyter/MindQuantum |

## 2. Como usar

- Conferir ordem conceitual: bit → porta → emaranhamento → medida → ruído → algoritmo.
- Comparar exercícios e notação, não copiar texto.
- Usar os exemplos Tiangong para validar QASM e leitura de counts.
- Usar o qmlcourse para a trilha de aprendizado de máquina quântico.
- Atribuir a fonte em cada seção que dependa dela.

## 3. O que não fazer

- Não copiar figuras, notebooks ou texto sem verificar a licença do asset.
- Não tratar a existência de um curso como prova de aprendizagem.
- Não declarar “Qualis A1”, “10/10” ou “eficácia comprovada”.
- Não misturar o Qiskit Textbook com o livro sem citar a versão consultada.
- Não usar a documentação Tiangong como peer review.

## 4. Mapa para as trilhas do livro

| Trilha | Fonte de conferência | Exercício |
|---|---|---|
| Bit e portas | Qiskit Textbook | circuitos de 1 qubit |
| Emaranhamento | Tiangong (Bell/GHZ) | QASM com H + CNOT |
| Medida | Qiskit Textbook | bases e probabilidades |
| Ruído | Tiangong/GJQ | modelos depolarizante e térmico |
| Algoritmos | Qiskit Textbook | Grover, QFT, VQE |
| QML | qmlcourse | VQC e classificação |
| Pesquisa | GJQ docs | sampling, estimativa e MPS |

## 5. Atribuição

Formato sugerido:

> Sequência didática conferida com [fonte], versão/commit [x], licença [y]. Exercícios e figuras do livro são originais; a fonte não endossa o texto.

Para o qmlcourse, preservar a atribuição CC BY 4.0 e indicar modificações.
Para o Qiskit Textbook, preservar o aviso Apache-2.0.

## 6. Limites

- Não houve estudo de eficácia com estudantes.
- Não há pré-registro, grupo de controle ou medida de retenção.
- A comparação com cursos é editorial, não experimental.
- A documentação Tiangong pode mudar; cite a data de consulta.
