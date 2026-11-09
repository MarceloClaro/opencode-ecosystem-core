# Relatório de reprodução dos experimentos E01–E18

Gerado em 2026-11-09T00:49:58-0300.

## Protocolo

- Simulador: `AerSimulator`.
- Sementes por experimento: **20**.
- Tiros por semente: **4096**.
- Total por experimento: **81920** tiros.
- Métrica principal: distância de variação total (TVD) contra a distribuição ideal; TVD menor é melhor.

## Resultados

| Exp. | Nome | Leitura agregada | TVD ideal | IC95 TVD | TVD arquivo simulado | TVD arquivo real |
|---|---|---|---:|---:|---:|---:|
| E01 | Base |0⟩ | P(0) = 1.000 (ideal 1,000) | 0.0000 | [0.0000, 0.0000] | 0.0000 | 0.0078 |
| E02 | Base |1⟩ e leitura | P(1) = 1.000 (ideal 1,000) | 0.0000 | [0.0000, 0.0000] | 0.0000 | 0.0137 |
| E03 | Superposição H|0⟩ | P(1) = 0.501 (ideal 0,500) | 0.0060 | [0.0041, 0.0080] | 0.0039 | 0.0176 |
| E04 | Interferência H-Z-H | P(1) = 1.000 (ideal 1,000) | 0.0000 | [0.0000, 0.0000] | 0.0000 | 0.0137 |
| E05 | Estado de Bell | P(00)+P(11) = 1.000 (ideal 1,000) | 0.0050 | [0.0029, 0.0070] | 0.0186 | 0.0586 |
| E06 | GHZ de 4 qubits | P(0000)+P(1111) = 1.000 (ideal 1,000) | 0.0047 | [0.0032, 0.0061] | 0.0146 | 0.2119 |
| E07 | CHSH | S = 2.829 (ideal 2,828) | 0.0095 | [0.0086, 0.0104] | 0.0176 | 0.0557 |
| E08 | Gerador quântico de números | |P(0)-P(1)| = 0.001 (ideal 0,000) | 0.0060 | [0.0041, 0.0080] | 0.0186 | 0.0176 |
| E09 | Codificação de amplitude | P(1) = 0.750 (ideal 0,750) | 0.0043 | [0.0029, 0.0056] | 0.0146 | 0.0068 |
| E10 | Classificador XOR (VQC) | Acurácia = 4/4 | 0.0000 | [0.0000, 0.0000] | 0.0000 | 0.0413 |
| E11 | Interferência de dois qubits | P(00) = 0.499 (ideal 0,500) | 0.0050 | [0.0029, 0.0070] | 0.0117 | 0.0566 |
| E12 | QFT de 3 qubits | P(000) = 0.124 (ideal 0,125) | 0.0167 | [0.0140, 0.0194] | 0.0225 | 0.0410 |
| E13 | Produto tensorial |01⟩ | P(01) = 1.000 (ideal 1,000) | 0.0000 | [0.0000, 0.0000] | 0.0000 | 0.0430 |
| E14 | Ruído de fase | P(0) = 1.000 (ideal 1,000) | 0.0000 | [0.0000, 0.0000] | 0.0000 | 0.0078 |
| E15 | GHZ via QASM 2.0 | P(0000)+P(1111) = 1.000 (ideal 1,000) | 0.0047 | [0.0032, 0.0061] | 0.0273 | 0.2119 |
| E16 | Esfera de Bloch | ⟨Z⟩ = -0.001, ⟨X⟩ = +1.000 (ideal 0, +1) | 0.0030 | [0.0021, 0.0040] | 0.0020 | 0.0127 |
| E17 | Interferência de três qubits | P(000) = 0.248 (ideal 0,250) | 0.0090 | [0.0066, 0.0113] | 0.0166 | 0.0918 |
| E18 | Amostragem binomial | P(1) = 0.501 (ideal 0,500) | 0.0060 | [0.0041, 0.0080] | 0.0166 | 0.0176 |

## Leitura

- A TVD contra o ideal mede o erro de amostragem e a distância do circuito ao estado preparado; ela não mede fidelidade de estado.
- O arquivo simulado original tem 1024 tiros em uma execução; a reprodução usa 81.920 tiros, então a TVD tende a ser menor apenas pelo tamanho da amostra.
- O arquivo real foi coletado em hardware e não foi reproduzido em hardware nesta rodada; a coluna serve como referência, não como prova.
- Nenhum job foi enviado ao GJQ/Tiangong.

## Limites

- Simulação clássica de circuitos pequenos; não há vantagem quântica.
- O protocolo controla seed e shots, mas não corrige erros de calibração do hardware original.
- A comparação com o JSON real é descritiva; não é replicação experimental nem teste de hipótese sobre o hardware.
