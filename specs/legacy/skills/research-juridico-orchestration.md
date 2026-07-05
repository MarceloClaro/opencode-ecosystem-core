# Specs: Skills — Research, Juridico e Demais Categorias

**Total:** 26 skills | **Revisao:** 2026-05-27

---

## Research (3 skills)

### academic-export-abnt (v1.0.0)
Exportacao multi-formato ABNT: PDF (LaTeX), DOCX (python-docx), HTML standalone. Normas NBR 14724/6023/6028.
- [ ] PDF gerado com margens ABNT (3cm/2cm), Times 12pt, 1.5 espacamento
- [ ] DOCX com template ABNT
- [ ] HTML standalone funcional

### academic-ml-pipeline (v1.1.0)
Pipeline ML 6 etapas: correcao bootstrap, classificacao ARM, deteccao de anomalias, clusterizacao, feature importance.
- [ ] 6 etapas executam sequencialmente
- [ ] 11 features + 262 observacoes
- [ ] AUC >= 0.70, RF >= 85%

### editais-br (v7.2)
Busca inteligente de editais brasileiros. 25 sub-dimensoes, scoring por perfil, 52 editais curados (CNPq/CAPES/FINEP).
- [ ] Busca em 4 categorias: pesquisa/mestrado/doutorado/startup
- [ ] Extracao profunda (contrapartida, prazos, docs)
- [ ] Cache versionado com fallback de curadoria

---

## Juridico (7 skills)

### edicao-cirurgica
Edicao que retorna APENAS blocos modificados, nunca o artefato inteiro.
- [ ] Retorna apenas diffs, nao arquivo completo
- [ ] Cobre todas as linguagens e formatos

### followup-advocacia
Rotina de follow-up: lembretes de prazos, cadencia de contatos, pipeline de demandas.
- [ ] Lembretes configurados por prazo processual
- [ ] Pipeline com estados: contato→consulta→contrato→andamento→concluido

### gerador-contratos
Contratos juridicos em HTML otimizado para PDF, identidade visual profissional.
- [ ] HTML gerado com CSS para impressao
- [ ] Dados preenchidos via wizard ou JSON

### overview-juridico
Visao geral das skills juridicas. Roteamento de demanda para skill correta.
- [ ] Classifica demanda por area do direito
- [ ] Recomenda skill apropriada

### pecas-juridicas-html
Pecas juridicas em HTML para exportacao PDF. Identidade visual customizavel.
- [ ] Formatos: peticao inicial, contestacao, recurso, parecer
- [ ] Exportacao PDF via browser

### pesquisa-jurisprudencia
Pesquisa em bases brasileiras: STJ, STF, TJSP, TRTs.
- [ ] Busca por termo, numero de processo, relator
- [ ] Resultados formatados com ementa e link

### triagem-juridica
Triagem de leads: classifica area do direito, avalia urgencia, identifica dados essenciais.
- [ ] Classificacao em < 5 areas simultaneas
- [ ] Score de urgencia (0-10)

---

## Orchestration / MiroFish (18 skills)

### agent-forum
Debate multiagente com moderador LLM. 4 estagios: OPEN→DISCUSS→SYNTHESIZE→CONCLUDE.
- [ ] Moderador controla fluxo de debate
- [ ] Buffer de N speeches por agente

### agent-node-pipeline (v1.1.0)
Framework para construir agentes como pipelines de nos tipados. 7 middlewares pre-construidos (DeerFlow).
- [ ] Nos composables com estado rastreavel
- [ ] Pipeline: busca → sumarizacao → reflexao → formatacao

### antigravity-integration (v1.0.0)
Ponte OpenCode ↔ Antigravity. Delegacao de imagem, browser, busca web, subagentes.
- [ ] Delegacao de tarefas para Antigravity
- [ ] Resposta integrada ao fluxo OpenCode

### code-graphrag (v1.0.0)
Grafo de conhecimento via GraphRAG + Zep Cloud. Busca semantica e estrutural.
- [ ] "O que depende de X?" → grafo de dependencias
- [ ] SQLite como backend de consulta

### config-generator (v1.0.0)
Geracao de configuracoes complexas com LLM multi-etapa + fallback heuristico.
- [ ] 4 etapas: tempo → eventos → agentes → plataforma
- [ ] Retry com temperatura decrescente
- [ ] Reparo de JSON truncado

### cora-debate (v1.0.0)
Debate multiagente com verificacao simbolica. Q-Score UCB1, 6 verificadores V1-V6, self-consistency K=7.
- [ ] Q-Score seleciona debatedores
- [ ] 6 verificadores independentes
- [ ] Calibracao Platt

### decisionnode
CLI + MCP para memoria de decisoes entre ferramentas IA.
- [ ] CRUD de decisoes com busca semantica
- [ ] Versionamento de decisoes (active/deprecated)

### docling-pdf-extraction (v2.0.0)
Extracao de documentos via Docling (IBM Research). 23 backends testados.
- [ ] PDF, DOCX, PPTX, HTML, CSV, Markdown
- [ ] OCR integrado
- [ ] Metadados extraidos

### document-ir
Pipeline de documentacao 7 estagios, 16 tipos de bloco. Inspirado no ReportEngine do BettaFish.
- [ ] Template → layout → budget → geracao → QC → composicao → render
- [ ] Output: MD + JSON

### entity-ner-reader (v1.0.0)
Leitura de entidades nomeadas em grafos. Filtro por tipo, enriquecimento com arestas.
- [ ] Extracao de entidades por tipo
- [ ] Contexto completo (arestas + nos relacionados)

### file-ipc (v1.0.0) + fs-ipc (v1.1.0)
Comunicacao entre processos via filesystem. Diretorios commands/ + responses/ com JSON.
- [ ] Polling com timeout configuravel
- [ ] Batch operations
- [ ] Limpeza automatica

### graph-builder-pipeline (v1.0.0)
Construcao de grafos a partir de texto. Chunking → NER → persistencia SQLite/Neo4j.
- [ ] Processamento assincrono
- [ ] Progresso rastreavel via TaskManager

### graph-memory-updater (v2.0.0)
Atualizacao de grafos em tempo real com atividade de agentes. Buffer por plataforma.
- [ ] Monitoramento de logs de acoes (postar, curtir, comentar, seguir)
- [ ] Envio em lote com buffer

### hybrid-graph-retrieval (v1.0.0)
3 estrategias: InsightForge (profundo), PanoramaSearch (amplo), QuickSearch (rapido).
- [ ] InsightForge: decomposicao de perguntas
- [ ] PanoramaSearch: contexto historico
- [ ] QuickSearch: palavra-chave

### machine-states (v2.0.0)
Maquina de estados para pipeline Reversa. 14 estados, 20+ transicoes.
- [ ] Transicoes validadas
- [ ] Persistencia automatica

### maswos-v5-nexus
Framework MASWOS V5: 130+ agentes, 9 estrategias RAG, pipeline Qualis A1.
- [ ] Orquestracao multiagente
- [ ] Transformer Network para roteamento

### mirofish-sync
Sincronizacao MiroFish/BettaFish ↔ OpenCode. Monitora repos upstream, extrai padroes.
- [ ] Deteccao de novos padroes
- [ ] Integracao automatica como P19+

### oasis-profile-gen (v2.0.0)
Geracao de personas IA a partir de nos de grafo. Bio, MBTI, topicos, estilo de fala.
- [ ] Entrada: nos do grafo
- [ ] Saida: perfil estruturado com 6 dimensoes

### ontology-generator (v1.0.0)
Geracao de ontologias para grafos de conhecimento social. Entidades + relacionamentos.
- [ ] Analise de texto para definicao de tipos
- [ ] Schema validavel

### plan-generator (v1.0.0)
Planos incrementais para engenharia reversa. Scope → Modules → Tasks → Dependencies.
- [ ] 5 estagios de planejamento
- [ ] Dependencias resolvidas automaticamente

### process-lifecycle (v1.0.0)
Ciclo de vida de processos background cross-platform (Windows taskkill + Unix SIGTERM).
- [ ] Iniciar, monitorar, pausar, retomar, finalizar
- [ ] Tracking dual-platform
- [ ] Ingestao de logs em tempo real

### report-agent-react (v1.0.0)
Relatorios com cadeia ReACT multi-turno. Reflexao em 3 dimensoes pos-geracao.
- [ ] Ciclo think→act→observe→reflect por secao
- [ ] Sumario planejado antes da geracao

### swarm-review (v1.0.0)
Revisao por enxame: 3+ agentes especializados em paralelo. Debatem divergencias, consolidam relatorio.
- [ ] Seguranca, performance, arquitetura em paralelo
- [ ] Consenso ou dissenso documentado

### synthesis-agent (v1.0.0)
Meta-agente: coleta outputs de multiplos agentes, cruza referencias, resolve contradicoes.
- [ ] Input: N outputs de agentes
- [ ] Output: documentacao consolidada e rastreavel

---

## Frontend (1 skill)

### frontend-philosophy (v2.1.0)
5 Pilares da UI Intencional: filosofia visual e de UI para agentes de frontend.
- [ ] Componentes seguem os 5 pilares
- [ ] Consistencia visual跨 componentes

---

## Workflows (1 skill)

### plan-protocol (v2.1.0)
Criacao de planos com YAML frontmatter, fases hierarquicas, tasks com citacoes.
- [ ] YAML frontmatter valido
- [ ] Tasks com criterios de aceitacao
- [ ] Rastreabilidade de citacoes
