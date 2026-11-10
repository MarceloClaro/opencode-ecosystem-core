# SPEC-935-R1130 — Twirl/frame, ruído das correções e pré-registro

**Status:** implementação local, sem hardware
**Data:** 2026-11-10
**Depende de:** R1129 (13 funções), R1119 (Pauli-frame)

## 1. Objetivo

Adicionar ao desenho intercalado:

1. twirl de Pauli em cada CZ, com registro dos frames;
2. simulação de depolarização 1q após cada correção;
3. pré-registro local do desenho, sem autorização de hardware.

## 2. Twirl/frame

- Cada CZ pode ser substituído por `P · CZ · P'`, com `P' = CZ P CZ`.
- O circuito ideal é equivalente ao original; os frames ficam registrados.
- O twirl é opcional (`twirl=False` por padrão) e determinístico por seed.
- A simulação usa ruído Pauli **antes** do CZ; o twirl não altera a recuperação
  exata nos testes com taxas uniformes e não uniformes.

## 3. Ruído das correções

- `correction_rate` aplica depolarização 1q após cada gate de correção marcado.
- A taxa 0 recupera 13/13; a taxa 0,005 produz erro absoluto máximo ~1,3×10⁻².
- O modelo é uma **simulação**, não o ruído real do Baihua.

## 4. Pré-registro

- 13 funções × 5 profundidades × 5 seeds de twirl = 325 jobs planejados.
- 4.096 shots por job; 1.331.200 shots no orçamento.
- Regras de decisão, hipótese de ruído, hash e `hardware_submission_allowed=False`.
- Nenhuma submissão, credencial ou rede.

## 5. Requisitos

- **R1.** `cycle_body_framed` com frames de twirl.
- **R2.** `simulate_expectation` com `twirl`, `seed` e `correction_rate`.
- **R3.** `noise_audit` com taxas de correção e twirl.
- **R4.** `build_preregistration` determinístico, hash e validação.
- **R5.** Comandos `interleaved-noise` e `preregister` no harness.
- **R6.** Testes de frames, equivalência ideal, degradação e tamper.
- **R7.** Nenhum hardware, rede, submissão ou credencial.

## 6. Não objetivos

- Executar no Baihua.
- Modelar ruído coerente ou crosstalk.
- Resolver as 2 funções de corte.
- Declarar taxas medidas, PEC 2q ou vantagem.

## 7. Critérios de aceitação

- frames não vazios e expectativa ideal +1;
- twirl preserva 13/13 em simulação;
- ruído 0,005 degrada e mantém ajuste;
- pré-registro com 325 jobs, hash e flags falsas;
- validação rejeita pré-registro alterado;
- comandos do harness funcionam e não sobrescrevem;
- nenhuma string de hardware/segredo;
- relatório e limites registrados.
