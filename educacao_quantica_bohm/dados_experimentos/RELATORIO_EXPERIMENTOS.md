# Relatório dos experimentos: 100 conceitos, 18 circuitos

Cada conceito aponta para um circuito-base. A coluna **sobreposição**
compara a distribuição simulada com a do backend; não é fidelidade de
estado nem prova de emaranhamento.

## Experimentos-base

| ID | Experimento | Simulado | Backend | Sobreposição |
|---|---|---|---|---:|
| E01 | Base &#124;0⟩ | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| E02 | Base &#124;1⟩ e leitura | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| E03 | Superposição H&#124;0⟩ | P(1) = 0,496 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 98,6% |
| E04 | Interferência H-Z-H | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| E05 | Estado de Bell | P(00)+P(11) = 1,000 (ideal 1,000) | P(00)+P(11) = 0,941 (ideal 1,000) | 94,1% |
| E06 | GHZ de 4 qubits | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| E07 | CHSH | S = 2,828 (ideal 2,828) | S = 2,383 (ideal 2,828) | 93,6% |
| E08 | Gerador quântico de números | &#124;P(0)-P(1)&#124; = 0,037 (ideal 0,000) | &#124;P(0)-P(1)&#124; = 0,035 (ideal 0,000) | 96,4% |
| E09 | Codificação de amplitude | P(1) = 0,735 (ideal 0,750) | P(1) = 0,743 (ideal 0,750) | 99,2% |
| E10 | Classificador XOR (VQC) | Acurácia = 4/4 | Acurácia = 4/4 | 95,9% |
| E11 | Interferência de dois qubits | P(00) = 0,488 (ideal 0,500) | P(00) = 0,474 (ideal 0,500) | 94,3% |
| E12 | QFT de 3 qubits | P(000) = 0,117 (ideal 0,125) | P(000) = 0,120 (ideal 0,125) | 95,7% |
| E13 | Produto tensorial &#124;01⟩ | P(01) = 1,000 (ideal 1,000) | P(01) = 0,957 (ideal 1,000) | 95,7% |
| E14 | Ruído de fase | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| E15 | GHZ via QASM 2.0 | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| E16 | Esfera de Bloch | ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) | ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) | 98,9% |
| E17 | Interferência de três qubits | P(000) = 0,258 (ideal 0,250) | P(000) = 0,229 (ideal 0,250) | 90,8% |
| E18 | Amostragem binomial | P(1) = 0,483 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 99,9% |

## Cobertura dos 100 conceitos

::: {.tabela-longa}

| Conceito | Experimento | Simulado | Backend | Sobreposição |
|---|---|---|---|---:|
| Bit | E01 — Base &#124;0⟩ | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| Qubit | E03 — Superposição H&#124;0⟩ | P(1) = 0,496 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 98,6% |
| Amplitude | E09 — Codificação de amplitude | P(1) = 0,735 (ideal 0,750) | P(1) = 0,743 (ideal 0,750) | 99,2% |
| Probabilidade | E18 — Amostragem binomial | P(1) = 0,483 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 99,9% |
| Medição | E02 — Base &#124;1⟩ e leitura | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| Base | E16 — Esfera de Bloch | ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) | ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) | 98,9% |
| Fase | E04 — Interferência H-Z-H | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| Interferência | E04 — Interferência H-Z-H | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| Emaranhamento | E05 — Estado de Bell | P(00)+P(11) = 1,000 (ideal 1,000) | P(00)+P(11) = 0,941 (ideal 1,000) | 94,1% |
| Estado de Bell | E07 — CHSH | S = 2,828 (ideal 2,828) | S = 2,383 (ideal 2,828) | 93,6% |
| Onda piloto | E03 — Superposição H&#124;0⟩ | P(1) = 0,496 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 98,6% |
| Equação do guia | E04 — Interferência H-Z-H | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| Equilíbrio quântico | E18 — Amostragem binomial | P(1) = 0,483 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 99,9% |
| Não localidade | E07 — CHSH | S = 2,828 (ideal 2,828) | S = 2,383 (ideal 2,828) | 93,6% |
| Colapso efetivo | E02 — Base &#124;1⟩ e leitura | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| Ordem implicada | E11 — Interferência de dois qubits | P(00) = 0,488 (ideal 0,500) | P(00) = 0,474 (ideal 0,500) | 94,3% |
| Holomovimento | E17 — Interferência de três qubits | P(000) = 0,258 (ideal 0,250) | P(000) = 0,229 (ideal 0,250) | 90,8% |
| Diálogo | E08 — Gerador quântico de números | &#124;P(0)-P(1)&#124; = 0,037 (ideal 0,000) | &#124;P(0)-P(1)&#124; = 0,035 (ideal 0,000) | 96,4% |
| Suspensão de suposições | E16 — Esfera de Bloch | ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) | ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) | 98,9% |
| Totalidade | E06 — GHZ de 4 qubits | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| Porta X | E02 — Base &#124;1⟩ e leitura | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| Porta H | E03 — Superposição H&#124;0⟩ | P(1) = 0,496 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 98,6% |
| Porta Z | E04 — Interferência H-Z-H | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| CNOT | E05 — Estado de Bell | P(00)+P(11) = 1,000 (ideal 1,000) | P(00)+P(11) = 0,941 (ideal 1,000) | 94,1% |
| Circuito | E11 — Interferência de dois qubits | P(00) = 0,488 (ideal 0,500) | P(00) = 0,474 (ideal 0,500) | 94,3% |
| Circuito de Bell | E05 — Estado de Bell | P(00)+P(11) = 1,000 (ideal 1,000) | P(00)+P(11) = 0,941 (ideal 1,000) | 94,1% |
| GHZ | E06 — GHZ de 4 qubits | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| QASM 2.0 | E15 — GHZ via QASM 2.0 | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| Transpilação | E15 — GHZ via QASM 2.0 | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| Medição múltipla | E18 — Amostragem binomial | P(1) = 0,483 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 99,9% |
| PennyLane | E03 — Superposição H&#124;0⟩ | P(1) = 0,496 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 98,6% |
| Cirq | E03 — Superposição H&#124;0⟩ | P(1) = 0,496 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 98,6% |
| Qiskit | E03 — Superposição H&#124;0⟩ | P(1) = 0,496 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 98,6% |
| QNode | E11 — Interferência de dois qubits | P(00) = 0,488 (ideal 0,500) | P(00) = 0,474 (ideal 0,500) | 94,3% |
| Cirq Circuit | E05 — Estado de Bell | P(00)+P(11) = 1,000 (ideal 1,000) | P(00)+P(11) = 0,941 (ideal 1,000) | 94,1% |
| QuantumCircuit | E05 — Estado de Bell | P(00)+P(11) = 1,000 (ideal 1,000) | P(00)+P(11) = 0,941 (ideal 1,000) | 94,1% |
| Statevector | E16 — Esfera de Bloch | ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) | ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) | 98,9% |
| Esfera de Bloch | E16 — Esfera de Bloch | ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) | ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) | 98,9% |
| Amostragem | E18 — Amostragem binomial | P(1) = 0,483 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 99,9% |
| gjq-client | E15 — GHZ via QASM 2.0 | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| Supercondutor | E14 — Ruído de fase | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| Qubit físico | E02 — Base &#124;1⟩ e leitura | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| Decoerência | E14 — Ruído de fase | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| T1 e T2 | E14 — Ruído de fase | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| Erro de leitura | E02 — Base &#124;1⟩ e leitura | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| Ruído | E14 — Ruído de fase | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| CIQuanta | E15 — GHZ via QASM 2.0 | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| Tiangong | E15 — GHZ via QASM 2.0 | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| Fila de jobs | E08 — Gerador quântico de números | &#124;P(0)-P(1)&#124; = 0,037 (ideal 0,000) | &#124;P(0)-P(1)&#124; = 0,035 (ideal 0,000) | 96,4% |
| API key | E08 — Gerador quântico de números | &#124;P(0)-P(1)&#124; = 0,037 (ideal 0,000) | &#124;P(0)-P(1)&#124; = 0,035 (ideal 0,000) | 96,4% |
| GHZ real | E06 — GHZ de 4 qubits | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| VQC XOR | E10 — Classificador XOR (VQC) | Acurácia = 4/4 | Acurácia = 4/4 | 95,9% |
| Classificador | E10 — Classificador XOR (VQC) | Acurácia = 4/4 | Acurácia = 4/4 | 95,9% |
| Encoding | E09 — Codificação de amplitude | P(1) = 0,735 (ideal 0,750) | P(1) = 0,743 (ideal 0,750) | 99,2% |
| Ansatz | E11 — Interferência de dois qubits | P(00) = 0,488 (ideal 0,500) | P(00) = 0,474 (ideal 0,500) | 94,3% |
| Treino | E10 — Classificador XOR (VQC) | Acurácia = 4/4 | Acurácia = 4/4 | 95,9% |
| Acurácia | E10 — Classificador XOR (VQC) | Acurácia = 4/4 | Acurácia = 4/4 | 95,9% |
| Phase damping | E14 — Ruído de fase | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| Depolarizing | E14 — Ruído de fase | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| Ruído benéfico? | E10 — Classificador XOR (VQC) | Acurácia = 4/4 | Acurácia = 4/4 | 95,9% |
| Vetor | E16 — Esfera de Bloch | ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) | ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) | 98,9% |
| Matriz | E11 — Interferência de dois qubits | P(00) = 0,488 (ideal 0,500) | P(00) = 0,474 (ideal 0,500) | 94,3% |
| Produto interno | E16 — Esfera de Bloch | ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) | ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) | 98,9% |
| Produto tensorial | E13 — Produto tensorial &#124;01⟩ | P(01) = 1,000 (ideal 1,000) | P(01) = 0,957 (ideal 1,000) | 95,7% |
| Matriz densidade | E05 — Estado de Bell | P(00)+P(11) = 1,000 (ideal 1,000) | P(00)+P(11) = 0,941 (ideal 1,000) | 94,1% |
| Traço | E05 — Estado de Bell | P(00)+P(11) = 1,000 (ideal 1,000) | P(00)+P(11) = 0,941 (ideal 1,000) | 94,1% |
| Autovalor | E16 — Esfera de Bloch | ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) | ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) | 98,9% |
| Fourier | E12 — QFT de 3 qubits | P(000) = 0,117 (ideal 0,125) | P(000) = 0,120 (ideal 0,125) | 95,7% |
| Holograma | E17 — Interferência de três qubits | P(000) = 0,258 (ideal 0,250) | P(000) = 0,229 (ideal 0,250) | 90,8% |
| Fourier quântico | E12 — QFT de 3 qubits | P(000) = 0,117 (ideal 0,125) | P(000) = 0,120 (ideal 0,125) | 95,7% |
| Nanoaula | E18 — Amostragem binomial | P(1) = 0,483 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 99,9% |
| Autodidatismo | E10 — Classificador XOR (VQC) | Acurácia = 4/4 | Acurácia = 4/4 | 95,9% |
| Feedback | E02 — Base &#124;1⟩ e leitura | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| Checkpoint | E16 — Esfera de Bloch | ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) | ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) | 98,9% |
| Erro produtivo | E14 — Ruído de fase | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| Roda de diálogo | E11 — Interferência de dois qubits | P(00) = 0,488 (ideal 0,500) | P(00) = 0,474 (ideal 0,500) | 94,3% |
| Projeto | E11 — Interferência de dois qubits | P(00) = 0,488 (ideal 0,500) | P(00) = 0,474 (ideal 0,500) | 94,3% |
| Rubrica | E10 — Classificador XOR (VQC) | Acurácia = 4/4 | Acurácia = 4/4 | 95,9% |
| Adaptação | E09 — Codificação de amplitude | P(1) = 0,735 (ideal 0,750) | P(1) = 0,743 (ideal 0,750) | 99,2% |
| Acessibilidade | E08 — Gerador quântico de números | &#124;P(0)-P(1)&#124; = 0,037 (ideal 0,000) | &#124;P(0)-P(1)&#124; = 0,035 (ideal 0,000) | 96,4% |
| Acesso | E08 — Gerador quântico de números | &#124;P(0)-P(1)&#124; = 0,037 (ideal 0,000) | &#124;P(0)-P(1)&#124; = 0,035 (ideal 0,000) | 96,4% |
| Dupla finalidade | E07 — CHSH | S = 2,828 (ideal 2,828) | S = 2,383 (ideal 2,828) | 93,6% |
| Privacidade | E08 — Gerador quântico de números | &#124;P(0)-P(1)&#124; = 0,037 (ideal 0,000) | &#124;P(0)-P(1)&#124; = 0,035 (ideal 0,000) | 96,4% |
| LGPD | E08 — Gerador quântico de números | &#124;P(0)-P(1)&#124; = 0,037 (ideal 0,000) | &#124;P(0)-P(1)&#124; = 0,035 (ideal 0,000) | 96,4% |
| Custo | E18 — Amostragem binomial | P(1) = 0,483 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 99,9% |
| Ambiente | E14 — Ruído de fase | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| Trabalho | E11 — Interferência de dois qubits | P(00) = 0,488 (ideal 0,500) | P(00) = 0,474 (ideal 0,500) | 94,3% |
| Desinformação | E07 — CHSH | S = 2,828 (ideal 2,828) | S = 2,383 (ideal 2,828) | 93,6% |
| Consenso | E06 — GHZ de 4 qubits | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| Responsabilidade | E02 — Base &#124;1⟩ e leitura | P(1) = 1,000 (ideal 1,000) | P(1) = 0,986 (ideal 1,000) | 98,6% |
| Pergunta | E03 — Superposição H&#124;0⟩ | P(1) = 0,496 (ideal 0,500) | P(1) = 0,482 (ideal 0,500) | 98,6% |
| Hipótese | E07 — CHSH | S = 2,828 (ideal 2,828) | S = 2,383 (ideal 2,828) | 93,6% |
| Evidência | E16 — Esfera de Bloch | ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) | ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) | 98,9% |
| Limite | E14 — Ruído de fase | P(0) = 1,000 (ideal 1,000) | P(0) = 0,992 (ideal 1,000) | 99,2% |
| Replicação | E06 — GHZ de 4 qubits | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| Narrativa | E17 — Interferência de três qubits | P(000) = 0,258 (ideal 0,250) | P(000) = 0,229 (ideal 0,250) | 90,8% |
| Visualização | E16 — Esfera de Bloch | ⟨Z⟩ = +0,008, ⟨X⟩ = +1,000 (ideal 0, +1) | ⟨Z⟩ = +0,035, ⟨X⟩ = +0,984 (ideal 0, +1) | 98,9% |
| Apresentação | E15 — GHZ via QASM 2.0 | P(0000)+P(1111) = 1,000 (ideal 1,000) | P(0000)+P(1111) = 0,788 (ideal 1,000) | 78,8% |
| Portfólio | E10 — Classificador XOR (VQC) | Acurácia = 4/4 | Acurácia = 4/4 | 95,9% |
| Próximo passo | E10 — Classificador XOR (VQC) | Acurácia = 4/4 | Acurácia = 4/4 | 95,9% |

:::

> **Limite:** a sobreposição mede semelhança entre distribuições de
> counts. Ela cai com ruído e com o tamanho da amostra, mas não prova
> que o estado preparado é puro, emaranhado ou fiel ao ideal.