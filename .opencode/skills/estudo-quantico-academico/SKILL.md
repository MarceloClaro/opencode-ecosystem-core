---
name: estudo-quantico-academico
description: Estrutura um programa de estudo acadêmico de mecânica quântica e computação quântica com espinha dorsal matemática, laboratórios reproduzíveis, avaliação e pesquisa. Use para diagnosticar lacunas, montar trilha de 16 semanas, gerar caderno de problemas, rubricas e protocolos de replicação; não declara eficácia, peer review ou domínio sem evidência externa.
metadata:
  version: "1"
  origem: "R1107 — estudo acadêmico quântico"
---

# Estudo acadêmico quântico

## Quando usar

Use quando o pedido for **estudar, ensinar ou avaliar** mecânica quântica e
computação quântica com profundidade acadêmica: montar trilha, diagnosticar
lacunas, criar problemas e provas, organizar laboratório de replicação, preparar
banca ou escrever artigo. Não use para uma curiosidade isolada nem para
substituir orientação, graduação ou peer review.

## Contrato

1. **Spec primeiro.** A trilha nasce de `specs/SPEC-935-R1107-quantum-academic-study.md`.
2. **Matemática não é opcional.** Toda afirmação física precisa de definição,
   hipótese e limite; toda derivação precisa de contas conferíveis.
3. **Laboratório com pré-registro.** Pergunta falsificável, seeds, shots,
   IC95%, análise de sensibilidade e replicação.
4. **Simulação não é hardware.** `AerSimulator`, statevector e nuvem são
   simulação, salvo recibo de execução física.
5. **Lean não é físico.** Lean 4/Mathlib prova afirmações matemáticas; não
   prova calibração, fidelidade ou hardware.
6. **Avaliação externa.** Nenhuma etapa é concluída por autoavaliação; use
   pré/pós-teste, prova oral, projeto e revisão por pares.
7. **Anti-overclaim.** Não declare Qualis, aceite, eficácia pedagógica ou
   “domínio” sem parecer externo e dados.

## Diagnóstico em seis eixos

| Eixo | Pergunta de diagnóstico | Saída mínima |
|---|---|---|
| Matemática | Sei operar em ℂ, espaços de Hilbert, operadores e produto tensorial? | 12 módulos + 120 problemas |
| Física | Sei distinguir estado, medida, evolução, composição e interpretação? | 20 problemas conceituais + 5 experimentos |
| Computação | Sei ler um circuito, um algoritmo e um resultado com ruído? | 8 replicações + relatórios |
| Método | Sei formular hipótese, pré-registrar, estimar incerteza e replicar? | protocolo + caderno |
| Avaliação | Sei medir aprendizagem sem confundir com exposição? | pré/pós + rubrica |
| Pesquisa | Sei ler paper, replicar, escrever e revisar? | 1 artigo + 1 parecer |

## Trilha de 16 semanas

| Fase | Semanas | Foco | Entregável |
|---|---|---|---|
| 1 | 1–4 | complexos, álgebra linear, probabilidade, postulados | 80 problemas + prova |
| 2 | 5–8 | 2 qubits, Bell/CHSH, matriz densidade | replicação E05/E07 + relatório |
| 3 | 9–12 | QFT, QPE, Grover, VQE/QAOA, ruído | replicação E10/E12 + artigo curto |
| 4 | 13–16 | Lean, QEC, papers, projeto | 5 teoremas + artigo + banca |

Carga realista: 8–10 h/semana. Para quem trabalha, 24 semanas.

## Artefatos a gerar

- `CADERNO_MATEMATICO.md` — 12 módulos, 120 problemas, gabarito comentado.
- `PROVAS_E_DEMONSTRACOES.md` — 60 problemas de prova e critérios.
- `LABORATORIO_REPLICACAO.md` — 8 protocolos com pré-registro, seeds e IC95%.
- `AVALIACAO_E_RUBRICAS.md` — diagnóstico, pré/pós, prova oral e portfólio.
- `LEAN_TRILHA.md` — 20 teoremas progressivos.
- `PESQUISA_E_ESCRITA.md` — leitura de papers, replicação, ABNT e parecer.

## Rotas no Core

| Necessidade | Agente |
|---|---|
| Derivação e modelagem formal | `21_agente_matematica_aplicada_modelagem_formal` |
| Computação quântica e algoritmos | `27_agente_computacao_quantica_aplicada` |
| Auditoria de experimento | `quantum-experiment-auditor` |
| Verificação Lean | `quantum-lean-verifier` |
| Redação acadêmica | `academic_writer` |
| LaTeX ABNT | `abnt-latex-modular` |
| DOI e citações | `bibtex-crossref-auditor` |
| Lacuna de pesquisa | `tdah-gap-hunter` |
| Livro e curso | `livro-quantico-orchestrator` |

## Base local

- Obra: `educacao_quantica_bohm/livro_pixel/` — 100 conceitos, 3 níveis,
  100 fichas, 400 notas.
- Curso: `educacao_quantica_bohm/livro_pixel/build_curso.py` — 600 laudas.
- Experimentos: `educacao_quantica_bohm/experimentos_reproduzidos/` — E01–E19.
- Artigo: `educacao_quantica_bohm/artigo_educacao_quantica/ARTIGO.pdf`.
- Lean: `livro-core/lean/QuantumTrails.lean`.

## Critérios de aceitação

- diagnóstico aplicado antes e depois;
- 80 problemas corrigidos na fase 1;
- 2 replicações com relatório e IC95%;
- 5 teoremas Lean sem `sorry`/`admit`;
- 1 artigo curto com fontes verificadas;
- 1 parecer de colega;
- banca simulada com réplica;
- nenhum segredo em arquivo;
- nenhuma alegação de eficácia sem dados externos.

## Limites

A skill organiza o estudo; não garante aprendizagem. Um build verde, um PDF
bonito ou uma simulação perfeita não substituem avaliação com estudantes,
orientação humana e revisão por pares. Quando não houver evidência, escreva
`protocol` ou `não medido`.
