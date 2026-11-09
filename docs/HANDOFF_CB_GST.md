# Handoff — cycle benchmarking e GST

**Status:** bloqueado por protocolo/dependência
**Data:** 2026-11-09
**Relacionado:** R1121 (literatura), R1122 (plano CB), R1123 (RC), R1124 (leitura)

Este documento registra por que as 15 taxas Pauli-Lindblad e a GST de q1
**não foram executadas** nesta rodada, apesar da autorização de hardware.

## 1. Cycle benchmarking

### O que já existe

- Plano de 150 jobs: 15 Paulis × 5 profundidades × 2 conjuntos.
- 8 processos de 20 jobs.
- 4.096 shots por job; 614.400 shots no total.
- Referências: Erhard et al. 2019; Harper et al. 2020; Flammia & Wallman 2020.

### O que falta

1. Gerador de circuitos:
   - preparar autoestados dos 15 Paulis;
   - aplicar `d` ciclos do CZ com twirls de Pauli;
   - medir na base do Pauli;
   - rastrear a fase/frame ideal.
2. Modelo de análise:
   - ajustar decaimento exponencial por Pauli;
   - separar fidelidade de Pauli de SPAM;
   - converter para taxas Pauli-Lindblad;
   - bootstrap/IC por profundidade.
3. Validação em simulador:
   - injetar um canal de Pauli conhecido;
   - recuperar as 15 taxas dentro da tolerância;
   - só então rodar hardware.

### Por que não rodar os 150 jobs agora

Sem o gerador e o ajuste validados, os counts não seriam interpretáveis. Rodar
150 jobs e “extrair taxas” por um ajuste não validado seria overclaim. O plano
está pronto; a execução fica condicionada ao pipeline.

### Próximo passo

Implementar `quantum_mitigation/cycle_benchmarking.py` com:

- `prepare_pauli_eigenstate(pauli)`;
- `cycle_benchmarking_circuit(pauli, depth, seed)`;
- `fit_pauli_decay(counts_by_depth)`;
- `pauli_lindblad_rates(fidelities)`;
- teste sintético com canal de Pauli conhecido.

## 2. GST de q1

### O que já existe

- Referências: Blume-Kohout et al. 2017; Brieger et al. 2023; Gu et al. 2021;
  Greenbaum 2015.
- Calibração Rabi de q1: ε ≈ 0; r1 0,0695–0,0786.
- Tomografia de 2 conjuntos: prep coerente 0,9823.

### O que falta

- `pyGSTi` não está instalado no `.venv-quantum`.
- Definição do gate set de 1 qubit e dos fiduciais/germs.
- Conversão dos circuitos GST para Qiskit/GJQ.
- Orçamento de ~100 circuitos (múltiplos processos).
- Análise de diamond norm e SPAM autoconsistente.

### Por que não instalar/rodar agora

GST não é um script de 10 linhas: exige gate set, fiduciais, germs, potências,
conversão de circuitos e análise. Instalar `pyGSTi` e rodar sem esse contrato
produziria um número não auditável. A dependência e o protocolo ficam para uma
rodada dedicada.

### Próximo passo

```bash
.venv-quantum/bin/python -m pip install pygsti
```

Depois:

1. definir gate set `Gi, Gx(pi/2), Gy(pi/2)`;
2. gerar `StandardGST` com `target_model='TP'`;
3. converter circuitos para Qiskit;
4. rodar em q1 com `confirm=True` e `allow_hardware=True`;
5. analisar diamond norm e SPAM;
6. comparar com Rabi/tomografia.

## 3. Gates que continuam fechados

| Etapa | Gate |
|---|---|
| PEC 2q | 15 taxas com IC |
| ZNE | curva monotônica |
| Comparação de layouts | prep coerente ≥ 0,99; r1 ≤ 0,05; drift resolvido; efeito ≥ 0,01 |
| Superfície | decoder em tempo real no Baihua |

## 4. O que não fazer

- Não rodar 150 jobs e chamar o resultado de “15 taxas” sem ajuste validado.
- Não instalar pyGSTi e declarar diamond norm sem protocolo.
- Não usar RC + ZNE + PEC como se fossem independentes.
- Não prometer “10/10”.
