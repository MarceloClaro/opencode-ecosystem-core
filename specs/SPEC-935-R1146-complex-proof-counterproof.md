# SPEC-935-R1146 — Prova e contraprova com números complexos em Lean 4 + Mathlib

**Status:** implementação local; compilação verificada
**Data:** 2026-11-10
**Depende de:** R1131, R1136, R747
**Fonte de método:** Lean 4 v4.34.1 + Mathlib (rev `d13f23b7`).

## 1. Objetivo

Dar ao Core uma habilidade de verificação formal para **inovações com
amplitudes complexas**, não apenas inteiros/racionais:

- provar identidades algébricas de números complexos usadas em mitigação;
- exigir uma **contraprova** para cada alegação;
- compilar de verdade e classificar axiomas;
- bloquear `sorry`, `admit`, `axiom`, `sorryAx` e axiomas nativos;
- emitir certificado com SHA-256 do `.lean` e do log.

## 2. Requisitos

- **R1.** `lean/quantum-cb/ComplexProofs.lean` com teoremas complexos:
  fase global, conjugação, Born não negativo, Born ≤ 1, interferência,
  porta de fase unitária.
- **R2.** Contraprovas explícitas: fase relativa observável, escala de
  amplitude altera `normSq`, probabilidade negativa impossível.
- **R3.** Sem `sorry`, `admit`, `axiom` ou `native_decide`.
- **R4.** `quantum_mitigation.complex_proof_gate` verifica fonte, compila,
  lê `#print axioms` e classifica cada teorema.
- **R5.** O gate aceita somente se todos os teoremas obrigatórios forem
  `kernel_checked` e cada alegação tiver contraprova nomeada.
- **R6.** Certificado JSON com hashes, status e limites.

## 3. Critérios de aceitação

- compilação retorna 0 e log sem `error`;
- todos os 9 teoremas reportados;
- axiomas ⊆ `{propext, Classical.choice, Quot.sound}`;
- `sorryAx` → `blocked`; `Lean.ofReduceBool` → `native`;
- alegação sem contraprova → `accepted=False`;
- teorema ausente → `accepted=False`;
- `hardware_executed=False`, `externally_validated=False`,
  `confidence_promoted=False`.

## 4. Limites

Prova algébrica, não hardware/calibração/ruído/canal/vantagem. O pareamento
alegação↔contraprova é editorial. O gate não substitui revisão humana nem
autoriza execução.
