# SPEC-935-R1107 — Estudo acadêmico quântico no Core

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1099 (livro quântico), R1104/R1105 (GJQ), R1106 (runtime GJQ)

## 1. Contexto

O projeto já tem uma obra de referência com 3000 laudas, uma edição de curso
com 600 laudas, 100 fichas de evidência, 400 notas de cálculo, uma suíte de
reprodução E01–E19 e um artigo de revisão sobre educação quântica e armadilha
da renda média. O que falta é uma camada **de estudo acadêmico** que organize
esse material em uma progressão verificável: matemática, física, computação,
método científico, avaliação e pesquisa.

Essa camada não deve ser um novo livro nem um novo agente genérico. Deve ser
uma **skill de orquestração curricular** e um **agente especializado** que:

- diagnostica lacunas;
- monta uma trilha de 16 semanas;
- gera caderno de problemas, provas e rubricas;
- encaminha tarefas aos agentes existentes;
- exige evidência externa antes de declarar domínio.

## 2. Requisitos

- **R1.** Criar a skill `estudo-quantico-academico` com contrato, seis eixos,
  trilha de 16 semanas, artefatos e critérios de aceitação.
- **R2.** Criar o agente `quantum-academic-study` no catálogo, com frontmatter
  válido, modo `subagent`, ferramentas de leitura/escrita limitadas e
  roteamento explícito para agentes existentes.
- **R3.** O agente deve encaminhar matemática, experimentos, Lean, redação e
  auditoria bibliográfica aos agentes já existentes, sem duplicar suas
  funções.
- **R4.** A skill deve distinguir diagnóstico, formação, avaliação e pesquisa;
  nenhuma etapa pode ser declarada concluída por autoavaliação.
- **R5.** Todo protocolo de laboratório deve exigir pergunta falsificável,
  pré-registro, seeds, IC95%, análise de sensibilidade e replicação.
- **R6.** O material deve declarar que simulação não é hardware e que Lean
  prova afirmações matemáticas, não medidas físicas.
- **R7.** Nenhuma saída pode declarar Qualis, aceite editorial, eficácia
  pedagógica comprovada ou peer review concluído sem parecer externo.
- **R8.** Criar documento `docs/ESTUDO_QUANTICO_ACADEMICO_R1107.md` com a
  trilha completa, artefatos e critérios de sucesso.
- **R9.** Criar testes que validem arquivos, frontmatter, seis eixos, trilha,
  rotas, ausência de segredos e ausência de overclaim.
- **R10.** Não adicionar dependência Python nova; a camada é documental e
  usa os agentes, skills e ferramentas já instalados.

## 3. Seis eixos

1. **Matemática:** álgebra linear sobre ℂ, espaços de Hilbert, operadores,
   espectro, produto tensorial, traço parcial, probabilidade e métodos
   numéricos.
2. **Física:** postulados, medida, evolução, composição, emaranhamento, Bell,
   decoerência, sistemas abertos e interpretações.
3. **Computação:** circuitos, universalidade, algoritmos, complexidade, ruído,
   mitigação e correção de erros.
4. **Método:** estatística, incerteza, pré-registro, replicação, revisão por
   pares e ética.
5. **Avaliação:** diagnóstico, formativa, somativa, prova oral, portfólio e
   inventário conceitual.
6. **Pesquisa:** leitura de papers, replicação, escrita ABNT, Lean e banca.

## 4. Trilha de 16 semanas

| Fase | Semanas | Foco | Entregável |
|---|---|---|---|
| 1 | 1–4 | matemática e postulados | 80 problemas + prova |
| 2 | 5–8 | 2 qubits, Bell/CHSH, matriz densidade | replicação E05/E07 + relatório |
| 3 | 9–12 | QFT, QPE, Grover, VQE/QAOA, ruído | replicação E10/E12 + artigo curto |
| 4 | 13–16 | Lean, QEC, papers, projeto | 5 teoremas + artigo + banca |

Carga: 8–10 h/semana. Para trabalhadores, 24 semanas.

## 5. Rotas para agentes existentes

| Necessidade | Agente |
|---|---|
| Fundamento matemático e derivações | `21_agente_matematica_aplicada_modelagem_formal` |
| Computação quântica e algoritmos | `27_agente_computacao_quantica_aplicada` |
| Auditoria de experimento e counts | `quantum-experiment-auditor` |
| Verificação Lean | `quantum-lean-verifier` / `49_agente_lean_verificacao_total` |
| Redação acadêmica | `academic_writer` |
| LaTeX ABNT | `abnt-latex-modular` |
| DOI e citações | `bibtex-crossref-auditor` |
| Lacuna de pesquisa | `tdah-gap-hunter` |
| Livro e curso | `livro-quantico-orchestrator` |

## 6. Critérios de sucesso

- pré/pós-teste com instrumento validado e grupo de comparação;
- ganho com IC95% e tamanho de efeito;
- retenção após 3–6 meses;
- resolução de problema novo;
- replicação independente;
- revisão por pares externa;
- adoção curricular documentada.

Nenhum desses critérios pode ser substituído por “li tudo” ou “o build passou”.

## 7. Não objetivos

- Criar novo livro, novo PDF ou novo curso completo nesta rodada.
- Executar hardware quântico.
- Declarar eficácia pedagógica.
- Substituir graduação, orientação ou banca.
- Instalar dependências ou agentes de terceiros.

## 8. Testes

`tests/test_r1107_quantum_academic_study.py` verifica:

- spec, skill, agente e documento existem;
- frontmatter do agente é válido;
- skill contém seis eixos, trilha e critérios;
- rotas para agentes existentes;
- ausência de segredos;
- ausência de overclaim;
- documentação cita pré-registro, IC95%, replicação e Lean.
