# SPEC-935-R1114 — Mitigação e correção de erro quântico

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1110 (leitura), R1113 (4×4/incerteza)

## 1. Contexto

O R1113 mostrou que a matriz 4×4 corrige 01/10, mas não state preparation,
crosstalk ou deriva; que |11> é preparado com `rx(pi)` e inclui preparação do
|1>; e que três repetições estimam dispersão, não são prova estatística
universal. O operador pediu agentes para ZNE, PEC, DD e QEC, além de
caracterização de SPAM, crosstalk, deriva e incerteza, mantendo o loop de
lições.

## 2. Requisitos

- **R1.** Criar o pacote `quantum_mitigation/` com ZNE, DD, PEC, QEC e
  caracterização.
- **R2.** ZNE: folding global, extrapolação linear/quadrática/exponencial e
  simulação com modelo depolarizante.
- **R3.** DD: sequências XY4/CPMG/echo, inserção circuit-level e verificação de
  identidade.
- **R4.** PEC: quasi-probabilidades do canal depolarizante 1q, overhead de
  amostragem e plano; 2q é explicitamente não implementado.
- **R5.** QEC: código de repetição de 3 qubits para bit-flip, síndrome,
  decodificador e taxa de erro lógica; não é código de superfície.
- **R6.** SPAM: ajuste |0>/|1>, separação declarada entre preparação e leitura.
- **R7.** Crosstalk: métrica isolado vs simultâneo.
- **R8.** Drift: tendência linear e CUSUM.
- **R9.** Incerteza: Wilson e bootstrap.
- **R10.** Harness `harnesses/quantum-error-mitigation/` com comandos
  `zne`, `dd`, `pec`, `qec`, `spam`, `crosstalk`, `drift`, `uncertainty`,
  `lessons`.
- **R11.** Criar três agentes `managed-v1`: `quantum-error-mitigation`,
  `quantum-error-correction` e `quantum-noise-characterization`, com wrapper
  `agent_qem.py` e permissões específicas.
- **R12.** Criar skill `mitigacao-e-correcao-quantica`.
- **R13.** Testes sem hardware, sem rede e sem submissão.
- **R14.** Não declarar vantagem, threshold de QEC, fidelidade ou execução
  física sem evidência.

## 3. Métodos

| Técnica | O que faz | Limite |
|---|---|---|
| ZNE | fold U → U(U†U)^k, extrapola para escala zero | assume relação monotônica; não é QEC |
| PEC | quasi-probabilidades do canal depolarizante 1q | 2q não implementado; overhead cresce com γ² |
| DD | sequências de identidade em qubits ociosos | circuit-level, não pulse-level |
| QEC | repetição 3 qubits para bit-flip | não protege fase; não é superfície |
| SPAM | |0> e |1> com rx(pi) | separa prep/readout apenas parcialmente |
| Crosstalk | erro isolado vs simultâneo | não identifica mecanismo |
| Drift | tendência e CUSUM | não corrige calibração |
| Incerteza | Wilson/bootstrap | dispersão, não significância universal |

## 4. Critérios de aceitação

- ZNE preserva a unitariedade ideal e extrapola um caso linear;
- DD verifica identidade;
- PEC retorna coeficientes e overhead > 1; 2q é marcado como não implementado;
- QEC reduz a taxa de erro lógica para p pequeno e reporta teoria;
- SPAM, crosstalk, drift e incerteza geram JSON/Markdown;
- agentes validados por lifecycle; permissões restritas ao wrapper;
- `opencode.json` contém os três agentes;
- testes R1114 passam;
- nenhuma chave ou overclaim.

## 5. Não objetivos

- PEC em hardware ou 2q completo.
- Código de superfície ou fault tolerance.
- DD pulse-level.
- Corrigir state preparation, crosstalk ou deriva.
- Provar vantagem quântica.

## 6. Riscos

- **ZNE:** extrapolação instável se a curva não for monotônica.
- **PEC:** overhead exponencial no número de gates; 2q ausente.
- **DD:** inserção no fim não é schedule ideal.
- **QEC:** repetição não protege fase; sem threshold de superfície.
- **SPAM:** |11> com rx(pi) confunde preparação e leitura.
- **Overclaim:** técnicas de mitigação não são correção total.
