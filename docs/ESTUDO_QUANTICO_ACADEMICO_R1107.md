# Estudo acadêmico quântico — R1107

**Status:** implementação local<br>
**Skill:** `estudo-quantico-academico`<br>
**Agente:** `quantum-academic-study`<br>
**Spec:** `specs/SPEC-935-R1107-quantum-academic-study.md`

## 1. Objetivo

Transformar o material existente — 3000 laudas, 600 laudas de curso, 100
fichas, 400 notas, E01–E19, Lean e artigo — em um **programa de estudo
verificável**. O foco não é ler mais; é executar tarefas de alto nível:
demonstrar, calcular, replicar, avaliar e escrever.

## 2. Diagnóstico em seis eixos

| Eixo | O que diagnosticar | Saída mínima |
|---|---|---|
| Matemática | complexos, álgebra linear, Hilbert, operadores, espectro, produto tensorial, traço parcial | 12 módulos, 120 problemas |
| Física | postulados, medida, evolução, composição, emaranhamento, decoerência, interpretações | 20 problemas conceituais, 5 experimentos |
| Computação | circuitos, universalidade, algoritmos, complexidade, ruído, QEC | 8 replicações |
| Método | hipótese, pré-registro, seeds, IC95%, sensibilidade, replicação | protocolo + caderno |
| Avaliação | diagnóstico, formativa, somativa, oral, portfólio | pré/pós + rubrica |
| Pesquisa | leitura, replicação, escrita, parecer, banca | artigo + parecer |

O diagnóstico deve ser aplicado **antes** da trilha. Sem diagnóstico, a trilha
é um catálogo de desejos.

## 3. Trilha de 16 semanas

### Fase 1 — Matemática e postulados (semanas 1–4)

| Semana | Conteúdo | Entregável |
|---|---|---|
| 1 | complexos, espaços vetoriais, produto interno | 20 problemas |
| 2 | operadores, adjunto, Hermitianos, unitários | 20 problemas + verificação numérica |
| 3 | espectro, medida, probabilidade, regra de Born | 20 problemas + simulação |
| 4 | produto tensorial, estados compostos, postulados | 20 problemas + prova |

**Critério de passagem:** 80 problemas corrigidos, prova com ≥ 70%, capacidade
de refazer uma derivação sem consulta.

### Fase 2 — Dois qubits e emaranhamento (semanas 5–8)

| Semana | Conteúdo | Entregável |
|---|---|---|
| 5 | qubit, Bloch, portas, circuitos | replicação E03 |
| 6 | Bell, CNOT, correlações | replicação E05 |
| 7 | CHSH, não-sinalização, interpretações | replicação E07 + relatório |
| 8 | matriz densidade, ruído, decoerência | replicação E14 + relatório |

**Critério de passagem:** duas replicações com pré-registro, seeds, IC95% e
explicação do que o resultado não prova.

### Fase 3 — Algoritmos e ruído (semanas 9–12)

| Semana | Conteúdo | Entregável |
|---|---|---|
| 9 | QFT, QPE, mudança de base | replicação E12 |
| 10 | Grover, limite de consultas | problema de prova + simulação |
| 11 | VQE/QAOA, variacionais | replicação E10 |
| 12 | ruído, mitigação, QEC | replicação E19 + artigo curto |

**Critério de passagem:** artigo curto com método, resultados, IC95%, limites e
referências verificadas.

### Fase 4 — Lean, QEC e pesquisa (semanas 13–16)

| Semana | Conteúdo | Entregável |
|---|---|---|
| 13 | Lean 4, proposições, táticas | 5 teoremas |
| 14 | Mathlib, álgebra, probabilidade | 5 teoremas + auditoria |
| 15 | QEC, estabilizadores, surface code | problema de prova + leitura |
| 16 | paper, replicação, banca | artigo + parecer + banca |

**Critério de passagem:** 5 teoremas `machine_checked` (sem `sorry`/`admit`),
artigo revisável, parecer de colega e banca com réplica.

## 4. Artefatos

### 4.1 Caderno matemático

12 módulos:

1. complexos e álgebra linear;
2. espaços vetoriais complexos;
3. operadores e adjuntos;
4. espectro e decomposição;
5. probabilidade e regra de Born;
6. produto tensorial;
7. matriz densidade e traço parcial;
8. evolução e Schrödinger;
9. medida, POVM e canais;
10. Fourier e QFT;
11. Pauli, Clifford e estabilizadores;
12. métodos numéricos e complexidade.

Cada módulo: 10 problemas, 1 exemplo resolvido, 1 problema de prova, 1
verificação computacional, 1 erro comum e gabarito comentado.

### 4.2 Provas e demonstrações

60 problemas de prova, com critérios de correção. Não basta a resposta: o
estudante deve declarar hipóteses, justificar passos e apontar limites.

### 4.3 Laboratório de replicação

8 protocolos:

1. E03 — superposição;
2. E05 — Bell;
3. E07 — CHSH;
4. E10 — VQC XOR;
5. E12 — QFT;
6. E14 — ruído de fase;
7. E19 — Mermin;
8. um experimento novo proposto pelo estudante.

Cada protocolo exige pré-registro, seeds, shots, IC95%, sensibilidade e
replicação independente.

### 4.4 Avaliação

- diagnóstico de 30 questões;
- pré/pós-teste;
- prova oral de 20 minutos;
- projeto final;
- portfólio;
- rubrica 0–4.

### 4.5 Lean

20 teoremas progressivos:

- 5 de álgebra de portas;
- 5 de probabilidade e normalização;
- 5 de emaranhamento/CHSH;
- 5 de canais/QEC ou tópico escolhido.

Cada teorema deve ter enunciado em português, código, imports, status e limite.

### 4.6 Pesquisa e escrita

- 20 papers com fichamento;
- 3 replicações;
- 1 artigo curto em ABNT;
- 1 parecer de colega;
- 1 banca simulada.

## 5. Rubrica de avaliação

| Nível | Descrição | Evidência |
|---|---|---|
| 0 | não executou | nenhuma |
| 1 | executou com consulta | problema resolvido com gabarito |
| 2 | executou sem consulta | problema novo |
| 3 | replicou e explicou limites | relatório com IC95% |
| 4 | formalizou e escreveu | Lean + artigo revisável |
| 5 | passou por revisão externa | parecer + replicação independente |

A nota final não é autoavaliação. É a soma de evidências externas.

## 6. Critérios de sucesso

- pré/pós-teste com instrumento validado e grupo de comparação;
- ganho com IC95% e tamanho de efeito;
- retenção após 3–6 meses;
- resolução de problema novo;
- replicação independente;
- revisão por pares externa;
- adoção curricular documentada.

## 7. Rotas no Core

| Necessidade | Agente |
|---|---|
| Derivação e modelagem formal | `21_agente_matematica_aplicada_modelagem_formal` |
| Computação quântica | `27_agente_computacao_quantica_aplicada` |
| Auditoria de experimento | `quantum-experiment-auditor` |
| Lean | `quantum-lean-verifier` / `49_agente_lean_verificacao_total` |
| Redação | `academic_writer` |
| LaTeX ABNT | `abnt-latex-modular` |
| DOI | `bibtex-crossref-auditor` |
| Lacuna | `tdah-gap-hunter` |
| Livro/curso | `livro-quantico-orchestrator` |

## 8. Base local

- Obra: `educacao_quantica_bohm/livro_pixel/` — 3000 laudas.
- Curso: `educacao_quantica_bohm/livro_pixel/build_curso.py` — 600 laudas.
- Experimentos: `educacao_quantica_bohm/experimentos_reproduzidos/` — E01–E19.
- Artigo: `educacao_quantica_bohm/artigo_educacao_quantica/ARTIGO.pdf`.
- Lean: `livro-core/lean/QuantumTrails.lean`.

## 9. Limites

A trilha organiza o estudo; não garante aprendizagem. Precisa de mediação
humana, correção de problemas e revisão externa. Simulação não é hardware;
Lean não é medida física; build verde não é peer review.

## 10. Referências de apoio

KRIJTENBURG-LEWERISSA, K.; POL, H. J.; BRINKMAN, A.; VAN JOOLINGEN, W. R.
Insights into teaching quantum mechanics in secondary and lower undergraduate
education. **Physical Review Physics Education Research**, v. 13, n. 1, 2017.
DOI: 10.1103/PhysRevPhysEducRes.13.010109.

YUSUF, A.; ROMÁN-GONZÁLEZ, M.; BEHERA, S. K. Quantum computing in K-12
education: an early systematic review. **Computer Science Education**, v. 36,
n. 3, p. 461-493, 2025. DOI: 10.1080/08993408.2025.2545915.

KAUR, M.; VENEGAS-GOMEZ, A. Defining the quantum workforce landscape: a review
of global quantum education initiatives. **Optical Engineering**, v. 61, n. 8,
p. 081806, 2022. DOI: 10.1117/1.OE.61.8.081806.

LARANJEIRA, M. C. **3000 laudas de física quântica: do bit ao todo**. [S. l.]:
OpenCode Ecosystem Core, 2026a. Disponível em:
https://marceloclaro.github.io/opencode-ecosystem-core/livro-quantico/.

LARANJEIRA, M. C. **Experimentos reproduzidos E01–E18 + E19**. [S. l.]:
OpenCode Ecosystem Core, 2026b. Relatório técnico.

LARANJEIRA, M. C. **Educação em computação quântica desde a educação básica:
revisão de literatura, cenários internacionais e a armadilha da renda média**.
[S. l.]: OpenCode Ecosystem Core, 2026c. Artigo.
