# SPEC-913 — Molambudos Fase 1B: voz documental fria em DOC-04 a DOC-07

## Objetivo
Revisar `DOC-04`, `DOC-05`, `DOC-06` e `DOC-07` para reduzir prosa literária e tornar os documentos clínicos mais frios, burocráticos e verossímeis, preservando apenas sinais sutis de contaminação narrativa.

## Escopo
- Fragmentos-alvo: `fragmentos/doc/DOC-04.tex` a `DOC-07.tex` no projeto `Molambudos_VictoriaRegia`.
- Manter a sequência factual das sessões com Dr. Heitor Oliveira.
- Preservar links de leitura no final dos fragmentos.
- Reduzir conclusões explícitas sobre criatura/possessão.
- Manter tensão por contraste: linguagem institucional seca diante de conteúdo perturbador.

## Critérios de aceitação
1. Os documentos devem soar como registros clínicos/administrativos, não como narração literária.
2. A primeira pessoa do médico deve ser contida e funcional; adjetivos atmosféricos devem ser reduzidos.
3. A “contaminação” pode aparecer como anomalia documental, rasura, adendo, lacuna, mudança de termo ou nota marginal — não como explicação sobrenatural direta.
4. `DOC-07` deve apresentar diagnóstico de época e risco institucional sem transformar o laudo em discurso de vilão.
5. Links finais de leitura devem permanecer presentes.
6. O PDF deve compilar em duas passagens sem erro fatal.

## Verificação
- Leitura manual dos quatro fragmentos.
- Busca por expressões explícitas a reduzir: `criatura existe`, `possessão`, `monstro`, `não sou maluco`, `isso é real`.
- Compilação dupla de `main.tex`.
