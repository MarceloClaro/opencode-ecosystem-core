# SPEC-935-R1115 — Protocolos de mitigação para hardware

**Status:** implementação local + validação de hardware no subconjunto viável
**Data:** 2026-11-09
**Depende de:** R1113 (4×4/incerteza), R1114 (QEM/QEC)

## 1. Contexto

O operador pediu para levar ao hardware: ZNE/DD em Bell; PEC 2q via
Pauli-Lindblad; QEC de superfície com decodificador e orçamento; DD
pulse-level com timing; separação de state preparation e readout; e
repetições suficientes para um intervalo pré-registrado.

Nem todas as técnicas são executáveis no runtime GJQ atual. Esta spec separa
**pronto para hardware**, **planejamento/simulação** e **bloqueado por
capacidade da API**.

## 2. Requisitos

- **R1.** PEC 2q por inversão de canal Pauli, com quasi-probabilidades e γ.
- **R2.** Orçamento de código de superfície (dados, ancillas, síndrome) e
  interface de decodificador, sem simular o código.
- **R3.** Plano DD pulse-level a partir de T1/T2, janela ociosa e espaçamento.
- **R4.** Plano e ajuste de SPAM por pulsos π repetidos (k=1,3,5), separando
  erro de preparação e leitura em modelo declarado.
- **R5.** Pré-registro de `n` para meia-largura Wilson.
- **R6.** Protocolo de hardware para ZNE no Bell e SPAM separation, com gates
  SDD/TDD/simulação.
- **R7.** Declarar explicitamente o que não é executável no Baihua:
  PEC 2q em hardware, superfície com decodificador em tempo real, DD
  pulse-level.
- **R8.** Testes sem submissão.
- **R9.** Nenhum overclaim de threshold, fidelidade ou vantagem.

## 3. Matriz de viabilidade

| Item | Implementação | Hardware Baihua |
|---|---|---|
| ZNE no Bell | módulo + protocolo | **executável** (folding 1,3,5) |
| DD circuit-level | módulo + protocolo | executável, mas sem janela ociosa longa no Bell |
| PEC 2q Pauli-Lindblad | inversão de canal Pauli | **não executado**; exige taxas por Pauli e sampling alto |
| QEC de superfície | orçamento + interface MWPM | **não executado**; sem decodificador em tempo real |
| DD pulse-level | plano de timing | **bloqueado**; API GJQ não expõe pulso |
| SPAM separation | plano + ajuste | **executável** (k=1,3,5) |
| Incerteza pré-registrada | Wilson/bootstrap | executável na análise |

## 4. Critérios de aceitação

- PEC 1q e 2q retornam γ > 1 e labels Pauli;
- orçamento d=3 tem 17 qubits e 24 bits de síndrome;
- DD pulse-level retorna pulsos e timings;
- SPAM separation recupera e/r0/r1 de dados sintéticos;
- pré-registro retorna n com meia-largura <= alvo;
- testes R1115 passam;
- agentes com permissões para os novos comandos;
- nenhuma chave ou overclaim.

## 5. Não objetivos

- Simular o código de superfície completo.
- Executar PEC 2q ou superfície no Baihua.
- Implementar DD pulse-level no runtime atual.
- Declarar threshold ou fault tolerance.
- Provar vantagem quântica.
