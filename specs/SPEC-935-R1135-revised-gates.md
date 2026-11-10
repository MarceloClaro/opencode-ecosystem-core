# SPEC-935-R1135 — Gates revisados e fail-closed

**Status:** política offline, sem hardware
**Depende de:** R1130–R1134

## 1. Objetivo

Substituir gates heurísticos por critérios explícitos, testáveis e
fail-closed, sem declarar desbloqueio por planejamento.

## 2. Gates

### PEC 2q

- modelo GSPN do gate set validado;
- erro em held-out ≤ 0,01;
- overhead de amostragem ≤ 10;
- as 2 funções de corte **não** precisam ser identificadas diretamente;
- rota: GSPN/MLCB + gauge optimization.

### ZNE

- configurações LRE ≥ 9;
- resíduo do modelo ≤ 0,005;
- estimativa estável em held-out;
- monotonicidade global **não** é exigida.

### Layouts

- `n_pairs ≥ n_required`;
- pares diferentes exigem randomização;
- r1 ≤ 0,05 (ou reportado como limitação/covariável);
- drift resolvido;
- efeito ≥ 0,01.

### 2 funções de corte

- tratadas como gauge;
- exigem GSPN autoconsistente + MLCB;
- `identified=False` mesmo quando a rota é aprovada.

## 3. Requisitos

- **R1.** `gate_policy.py` com as quatro funções e `evaluate`.
- **R2.** Default fail-closed com evidência vazia.
- **R3.** Testes de passe e falha por critério.
- **R4.** Nenhum hardware, rede ou submissão.
- **R5.** Nenhuma taxa medida; nenhum gate declarado desbloqueado.

## 4. Critérios

- evidência vazia bloqueia os quatro gates;
- PEC passa com GSPN validado, erro 0,005 e overhead 5;
- ZNE passa com 27 configurações, resíduo 0,002 e held-out estável;
- layout passa com n=32, randomização, r1=0,04, drift resolvido e efeito 0,02;
- layout falha com r1=0,08;
- cortes passam como gauge, mas `identified=False`;
- testes e relatório.

## 5. Limites

A aprovação de um gate é condição **necessária**, não suficiente: dados,
revisão humana e validação independente continuam obrigatórios.
