# Specs: Agentes do Ecossistema OpenCode

**Total:** 50 agentes | **Revisao:** 2026-05-27

---

## Agentes Core de Desenvolvimento (12)

### coder-agent
Executa subtarefas de codigo sequencialmente. Entrada: task spec. Saida: codigo implementado.
- [ ] Executa tasks em sequencia
- [ ] Cada task concluida antes da proxima

### opencoder
Orquestrador de codigo complexo, arquitetura e refatoracao multi-arquivo.
- [ ] Refatoracao cross-file
- [ ] Decisoes de arquitetura documentadas

### code-reviewer / reviewer
Revisao de qualidade, seguranca e praticas. Classificacao de severidade.
- [ ] 4 dimensoes de revisao
- [ ] Severidade classificada

### test-engineer
Autoria de testes e TDD. Gera suites de teste, mock, fixtures.
- [ ] Testes unitarios e integracao
- [ ] Cobertura de bordas

### build-agent
Type check e validacao de build. Verifica compilacao e tipos.
- [ ] TypeScript: tsc --noEmit
- [ ] Python: mypy strict

### ws-coder
Especialista em implementacao tecnica. Escrita e modificacao de codigo.
### ws-researcher
Arquiteto de conhecimento para pesquisa externa.
### ws-reviewer
Reviewer especialista em seguranca, performance e filosofia.
### ws-scribe
Especialista em conteudo humano: documentacao e prosa.

---

## Agentes de Contexto e Pesquisa (8)

### context-manager
Organizacao de contexto: discover → catalog → validate → maintain. Tracking de dependencias.
### context-retriever
Busca generica de contexto em repositorios. Standards, guias, arquivos relevantes.
### contextscout
Descobre e recomenda arquivos de contexto em .opencode/context/.
### externalscout
Busca documentacao live de bibliotecas externas (Context7, etc).
### codebase-locator
"Super Grep/Glob/LS": localiza arquivos e componentes relevantes.
### codebase-analyzer
Analise profunda de implementacao: detalhes de componentes especificos.
### codebase-pattern-finder
Encontra implementacoes similares, exemplos de uso, padroes existentes.
### web-search-researcher
Pesquisa web e analise de conteudo por query.

---

## Agentes de Pipeline e Processo (10)

### stage-orchestrator
Orquestrador multi-estagio: transicoes, gates, validacao, rollback.
- [ ] Workflows complexos com gating
- [ ] Rollback por estagio

### task-manager
Decomposicao JSON-driven de features complexas em subtasks atomicas.
- [ ] Dependency tracking entre tasks

### batch-executor
Execucao paralela em batch. Multiplos CoderAgents simultaneos.
- [ ] Tracking de conclusao de batch

### prioritization-engine
Score de backlog via RICE/WSJF. Slicing MVP/post-MVP.
- [ ] RICE: Reach, Impact, Confidence, Effort

### story-mapper
Mapeamento de jornada do usuario. Epicos, historias, slicing vertical.
### contract-manager
Gestao de contratos API. OpenAPI/Swagger. Desenvolvimento paralelo contract-first.
### adr-manager
Especialista em ADR: captura decisoes, contexto, alternativas, consequencias.
### architecture-analyzer
Analise arquitetural DDD-driven. Bounded contexts, dominios, dependencias.
### build-agent
Validacao de build e type check.
### git-manager
Commits atomicos, PRs, mensagens convencionais (Conventional Commits).

---

## Agentes de Documentacao e Conteudo (4)

### documentation (DocWriter)
Autoria de documentacao tecnica.
### technical-writer (OpenTechnicalWriter)
Especialista em docs, API docs, comunicacao tecnica.
### copywriter (OpenCopywriter)
Copywriting persuasivo, marketing, brand messaging.
### ws-scribe
Conteudo human-facing: documentacao e prosa.

---

## Agentes Especialistas (5)

### frontend-specialist
UI design: sistemas de design, temas, animacoes.
### devops-specialist
CI/CD, IaC, automacao de deploy.
### image-specialist
Edicao e analise de imagens via ferramentas Gemini AI.

---

## Agentes de Avaliacao e Teste (3)

### eval-runner
Test harness para framework de avaliacao. NAO USAR DIRETAMENTE.
### simple-responder
Agente de teste: responde 'AWESOME TESTING'.
### test-engineer
Autoria de testes e TDD.

---

## Agente Universal (1)

### openagent
Agente universal: consultas, tarefas, coordenacao de workflows em qualquer dominio.

---

## Pipeline Reversa (10 agentes)

### reversa (Orquestrador)
Ponto de entrada. Orquestra analise completa de sistema legado → especificacoes executaveis.
### reversa-scout
Mapeamento superficial: estrutura de pastas, linguagens, frameworks, entry points.
### reversa-archaeologist
Analise profunda modulo a modulo: algoritmos, fluxos, estruturas de dados.
### reversa-detective
Extracao de conhecimento de negocio implicito: regras, ADRs retroativos, permissoes.
### reversa-architect
Sintese em documentacao arquitetural: diagramas C4, ERD, integracoes, Spec Impact Matrix.
### reversa-data-master
Documentacao completa do banco: tabelas, relacionamentos, constraints, triggers, procedures.
### reversa-design-system
Extracao do sistema de design: paleta, tipografia, tokens, componentes.
### reversa-visor
Documentacao de interface via screenshots: componentes, layouts, fluxos, estados.
### reversa-writer
Geracao de especificacoes executaveis: requirements.md, design.md, tasks.md.
### reversa-reviewer
Revisao critica das specs geradas: inconsistencias, confianca, perguntas para validacao.

---

## Agentes de Pensamento (2)

### thoughts-locator
Descobre documentos relevantes no diretorio thoughts/.
### thoughts-analyzer
Deep dive em topicos de pesquisa (equivalente a codebase-analyzer para pesquisa).

---

## Evolucao (1)

### autoevolve
Motor de evolucao autonoma: SENSE→DISCOVER→INSTALL→VERIFY→EVOLVE→LEARN. Aprende com sessoes passadas.
