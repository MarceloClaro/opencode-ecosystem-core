# SPEC-935-R1134 — Gauge, funções de corte e rota para PEC 2q

**Status:** auditoria offline, sem hardware
**Depende de:** R1128, R1129
**Fontes:**
Chen et al., PRX Quantum 7, 010305 (2026), DOI `10.1103/1pnv-t9px`;
Calzona et al., Phys. Rev. Research 8, 013111 (2026), DOI `10.1103/4hbl-hpl3`;
Chen et al., PRX Quantum 7, 033045 (2026), DOI `10.1103/69wc-gzl6`.

## 1. Contexto

O desenho de 13 funções deixa 2 funções de corte não aprendíveis. Tentar
identificá-las diretamente no CB padrão é o caminho errado. A literatura de
2026 mostra que:

- GSPN caracteriza o gate set inteiro (SPAM, 1q, CZ) de forma autoconsistente;
- MLCB reduz graus não aprendíveis em até 75%;
- com aprendizagem autoconsistente, o gauge não deve bloquear observáveis
  mitigados; a escolha de gauge afeta o overhead de amostragem.

## 2. Auditoria

- adicionar um vetor de corte às taxas muda as 15 fidelidades;
- as 13 funções do desenho permanecem invariantes;
- portanto, as 2 funções de corte são gauge para o desenho, mas não se deve
  concluir que PEC está resolvido sem o modelo autoconsistente.

## 3. Requisitos

- **R1.** `cut_invariance` com `learnable_change < 1e-12` e
  `fidelity_change > 1e-12`.
- **R2.** `pec_readiness` com `direct_15_rate_pec_allowed=False`.
- **R3.** Rota GSPN/MLCB, requisitos e `not_claimed`.
- **R4.** Nenhum hardware, rede ou submissão.
- **R5.** Não declarar as 2 funções medidas nem PEC desbloqueado.

## 4. Critérios

- 13 funções invariantes; fidelidades completas mudam;
- 2 funções de corte declaradas como gauge;
- rota e fontes registradas;
- testes e relatório.

## 5. Limites

A invariância das 13 funções não é uma prova de invariância de PEC para todo
observável. GSPN/MLCB exigem implementação, dados e validação; nenhum foi
executado no Baihua.
