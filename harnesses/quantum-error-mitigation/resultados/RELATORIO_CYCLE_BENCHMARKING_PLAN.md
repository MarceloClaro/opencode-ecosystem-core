# Plano de cycle benchmarking — 15 taxas Pauli-Lindblad

Gerado em 2026-11-10T13:12:12-03:00.

## Plano

- Porta: `cz` em [0, 1].
- Paulis: 15.
- Profundidades: [1, 2, 4, 8, 16].
- Conjuntos: 2.
- Jobs: **150**.
- Processos (limite 20): 8.
- Shots por job: 4,096.
- Shots totais: 614,400.

## Análise

- Ajuste exponencial da sobrevivência por Pauli; converter fidelidades em taxas Pauli-Lindblad; reportar IC.

## Pré-requisitos

- passe de Pauli-frame R1119
- mitigação de leitura
- n por profundidade pré-registrado
- GST ou Rabi para separar SPAM

## Limites

- Nenhuma taxa foi medida.
- O plano não executa hardware.
- Plano de jobs; nenhuma taxa foi medida. 150 jobs é piso de planejamento, não garantia de poder estatístico.
