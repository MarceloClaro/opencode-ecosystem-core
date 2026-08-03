# Changelog

Todas as mudanças notáveis no **OpenCode Ecosystem Core** serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [2.5.0] - 2026-08-03

### Adicionado
- **Motor de Validação Empírica Rigorosa (SPEC-935-R370)**: `mci/rigorous_validation.py` — computa estatística a partir de dados brutos (não só valida números já fornecidos): contraprova por permutação (seed fixo, determinística), duas lentes independentes (Welch-t + Mann-Whitney), validação cruzada k-fold genérica, validade convergente, e gate real no R103 (`OrchestratorReviewer.verify_statistical_claim()`).
- **Triangulação Multidisciplinar (SPEC-935-R371)**: `mci/multidisciplinary_triangulation.py` — uma alegação só é `triangulated=True` com ≥2 domínios independentes concordantes **e** nenhum domínio contestando (contestação de qualquer domínio bloqueia, nunca resolvida por maioria de votos); gate real no R103.
- **Protocolo de Pré-registro (SPEC-935-R372)**: `mci/preregistration_protocol.py` — `register_protocol()`/`verify_protocol()`; corrige um overclaim real em `mci/experiment_designer.py` (`pre_registered` defaultava para `True` sem qualquer verificação).
- **Enriquecimento do Catálogo MASWOS (SPEC-935-R380)**: 46 agent cards (00–53) com `description` placeholder e corpo apontando para caminho externo inexistente substituídos por conteúdo real (missão, entradas, saídas, workflow) portado de repositório-fonte confirmado, nunca fabricado.
- **Integração do Gate de Rigor ao Pipeline Principal (SPEC-935-R381)**: `scientific_discovery_pipeline()` agora chama de verdade `audit_scientific_manuscript()` (R369) sobre as seções reais compostas pelo R105 — antes uma função de biblioteca testada mas sem chamador. Novo estágio consultivo `stages["r381"]` (nunca bloqueia) e resumo `result["manuscript_rigor_gate"]`. R370–R372 permanecem deliberadamente opt-in (exigem dados brutos do chamador).

### Corrigido
- **Validação fim-a-fim com manuscrito real (SPEC-935-R373)**: os gates R369–R372 rodados sobre um manuscrito USP real revelaram e corrigiram 2 problemas genuínos — falso positivo de novidade em `production_scaffolds.py` ("primeiras diferenças" disparava `UNSUPPORTED_NOVELTY_CLAIM`) e gap de significância estatística para manuscritos que só reportam resumo (r, p, n), fechado com `pearson_naive_significance()` + `crosscheck_reported_correlation()` assimétrico.
- **Colisão de nomenclatura no R381**: a chave de estágio inicial (`r106_rigor`) colidia com `specs/SPEC-935-R106.md` (CI/CD Pipeline + Quality Gates, spec real não relacionado); renomeada para `r381`.

### Documentado
- README.md: novo Ato VII (rigor estatístico + unificação real do pipeline), nova Seção 15 (integração R381), diagrama de arquitetura completo com a aresta real `Composer → ProductionScaffolds` (antes ausente), números atualizados (198 ciclos, 2.695 testes, 222 specs, 129/205 agentes com episteme).

## [2.4.0] - 2026-08-02

### Adicionado
- **Camada Epistêmica de Roteamento (SPEC-935-R363)**: `transformer/episteme.py` com 6 regimes epistemológicos, léxico determinístico pt/en, matriz de afinidade e inferência que nunca chuta; `SkillHandbook.match()` aplica afinidade tarefa↔agente como peso brando (±10% máx., fail-open); frontmatter opcional `episteme:` nos agent cards.
- **Guardas de Tradução Cultural (SPEC-935-R364/R365/R366)** — os três agentes que eram só interface no R359:
  - `translation/terminology_graph.py`: grafo terminológico trilíngue versionado, idempotente, com aprovação humana obrigatória por termo, detecção de `TERM_CONFLICT`/`SYMBOL_DRIFT` e gate de release fail-closed;
  - `translation/author_voice.py`: perfil de voz autoral contratual (preserve/gloss/adapt, modernismos proibidos) com `VOICE_SHIFT`/`ANACHRONISM`/`REGISTER_SHIFT`;
  - `translation/back_translation.py`: 6 verificações determinísticas de retrotradução; nunca aprova equivalência.
- **Benchmark Cultural Medido (SPEC-935-R367)**: corpus interno rotulado de 18 casos (com limitações conhecidas deliberadas) + runner determinístico; resultado datado: precisão micro 1.00, recall micro 0.86; relatórios versionados com disclaimer de não-validação-externa.
- **Cobertura Epistêmica (SPEC-935-R368)**: léxico ampliado em 2 rodadas curadas (32%→65% do catálogo de 205 agentes), invariante de sinais disjuntos, `catalog_episteme_coverage()` e 12º check do doctor (`episteme_coverage`).
- **Andaimes de Raciocínio Produtivo (SPEC-935-R369)**: `reasoning/production_scaffolds.py` — 8 movimentos científicos auditáveis com `engine_hints` (SPEC-917/ARCHE), auditoria de novidade (`UNSUPPORTED_NOVELTY_CLAIM` sem citação/comparação na mesma frase), plano literário contratual (voz/conflito/símbolos/estranhamento), relatório medido de distintividade (22 clichês pt) e `select_scaffold()` via episteme.
- 122 testes novos (TDD estrito, RED verificado antes de cada implementação).

### Corrigido
- **Higiene SDD**: 6 specs (R264–R266, R277–R279) apontavam para "validações inline" ou arquivos de teste que nunca existiram no git; agora referenciam testes de regressão reais dos entregáveis (`test_sdd_tdd` de volta a 12/12).
- 15 diretórios `mci_test_state_*` órfãos removidos e ignorados no `.gitignore`.

### Documentado
- Falhas pré-existentes da frente literária (R272–R276) confirmadas também no HEAD e registradas como pendência nominal em `PROGRESS.md` (não corrigidas às cegas para não misturar frentes).

## [2.3.0] - 2026-07-08

### Adicionado
- **Inteligência Jurídica Integrada (SPEC-921 → SPEC-928)**:
  - Novo subsistema `legal/` com raciocínio jurídico brasileiro, integração Datajud, agentes AuxJuris, knowledge base com RAG por keywords, sumarização jurídica e especialização por 7 ramos do direito.
  - Novo `scanners/legal_impact_scanner.py` com avaliação de impacto jurídico e ganho metacognitivo jurídico.
  - Nova suíte de benchmarks jurídicos por ramo em `legal/benchmarks.py` com tiers conservadores (`base`, `specialist`, `specialist_advanced`, `phd_candidate`, `phd_validated`).
  - Nova aba `⚖️ Jurídico` na interface Streamlit para operação dedicada do scanner jurídico.
  - Novos Agent Cards jurídicos em `agents/catalog/` e roteamento por domínio em `legal/specializations.py`.
- **Knowledge Bases Segmentadas por Ramo Jurídico (SPEC-931)**:
  - Base de conhecimento segmentada nos 7 ramos do direito (penal, trabalhista, tributário, empresarial, administrativo, ambiental, digital/LGPD).
  - Roteamento automático por domínio e seleção manual/automática na webapp.
- **Integração Webapp com Knowledge Bases (SPEC-932)**:
  - Aba jurídica exibe base de conhecimento ativa, switch manual de ramo e preview de estatutos/principles/keywords.
- **Refinamento Jurídico via MetaBus (SPEC-933)**:
  - Ciclo de refinamento contínuo: busca → recuperação → síntese → atualização de confiança no MetaBus.
- **Orquestração Transversal no MetaBus (SPEC-934)**:
  - OQS, VSEE, EGS, RAG, Superhuman Suite, MiroFish, Game Theory, Publishing, Research e SDD publicam eventos de subsistema no MetaBus.
  - MetaBus com `publish_subsystem_event`, `search_memory`, `update_topic_confidence`, `upser_semantic_topic`.
  - Eventos de raciocínio, predição MiroFish, Nash equilibria, produção científica e ciclo SDD rastreáveis.
- **Universidade Sintética Transversal (SPEC-935)**:
  - Novo subsistema `synthetic_university/` com 10 faculdades (humanas, sociais, engenharia, letras, história, quântica, exatas, estatística, programação, interdisciplinar).
  - Motor combinatorial MiroFish-powered que testa 10.000+ combinações de conceitos entre faculdades.
  - Correlator Interdisciplinar que descobre e classifica correlações (causal, analógica, emergente, dialética, etc.).
  - Gerador de Teses PhD-level com 5 níveis acadêmicos (especulação → hipótese → teoria → paradigma → descoberta).
  - Grafo de Conhecimento da universidade com nós e arestas navegáveis.
  - 40+ professores especialistas distribuídos por todas as faculdades.
  - Currículo base com 20+ disciplinas gerado automaticamente.
  - Integração com MetaBus (eventos `synthetic_university.*`) e orquestrador (`orchestrator.synthetic_university()`).
  - 59 novos testes TDD (total: 422 passed).

### Modificado
- **README / ARCHITECTURE / diagram.mmd** sincronizados com a expansão jurídica, transversal e universitária completa.
- **Mapas do ecossistema** regenerados com a nova camada `synthetic_university` (10 faculdades, 40+ professores, motor combinatorial).
- **Orquestrador MarceloClaro** estendido com método `synthetic_university()`.
- **Evolução** registrada nos ciclos `R56` a `R68`.

### Validação
- Full test suite: `pytest tests -q` → 422 passed, 2 skipped.

## [2.2.0] - 2026-07-08

### Adicionado
- **Metacognitive Superhuman Refinement Suite (SPEC-920)**:
  - Novo `mci/metacognitive_evaluator.py` com `MetacognitiveTrace`, `MetacognitiveEvaluator`, `MetacognitiveBenchmarkSuite`, `classify_metacognitive_tier()` e `run_metacognitive_superhuman_suite()`.
  - Avaliação das dimensões `awareness`, `reflection`, `adaptation`, `memory_quality`, `error_causality` e `epistemic_humility`.
  - Política conservadora: `metacognitive_superhuman_verified` exige `external_validation=True`.
  - Nova suíte `tests/test_metacognitive_superhuman.py` com 8 testes RED→GREEN.

### Validação
- `pytest tests/test_metacognitive_superhuman.py -q` → 8 passed.
- `pytest tests -q` → 263 passed, 2 skipped, 1 warning.

## [2.1.0] - 2026-07-08

### Adicionado
- **Scientific RAG (SPEC-919)**:
  - Novo pacote `rag/` com `ScientificDocument`, `ScientificRAG`, `RetrievedEvidence` e `GroundingEvaluator`.
  - Recuperação híbrida lexical + semantic-lite, chunking citável, reranking científico e citações auditáveis (`Autor (Ano), doc_id#chunk`).
  - Política epistêmica conservadora: abstenção automática quando não há evidência suficiente.
- **Scientific Superhuman Benchmark Suite (SPEC-918)**:
  - Novo `benchmarks/scientific_reasoning/superhuman_suite.py` com `readiness_score` (0–100) e tiers `base`, `research_grade`, `superhuman_candidate`, `superhuman_verified`.
  - `superhuman_verified` exige `external_validation=True`, impedindo claim exagerado sem validação externa.
- **Testes TDD**:
  - Nova suíte `tests/test_scientific_rag_superhuman.py` cobrindo recuperação RAG, citações, abstenção, grounding e readiness superhuman.

### Modificado
- **Benchmarks científicos existentes** agora avaliam `pipeline_fn` quando fornecido; pipelines incorretos deixam de passar automaticamente.
- **Documentação** atualizada em `README.md`, `ARCHITECTURE.md` e `RELEASE_NOTES.md` para refletir RAG científico, readiness conservador e 255 testes operacionais.
- **EvolutionRegistry** atualizado com o ciclo `R55`.

### Validação
- `pytest tests/test_scientific_rag_superhuman.py -q` → 8 passed.
- `pytest tests -q` → 255 passed, 2 skipped, 1 warning.

## [1.0.2] - 2026-07-05

### Adicionado
- **Pipeline Científico com Governança (OQS + MCI + VSEE + EGS)**:
  - Adicionado suporte a schemas JSON formais em `/schemas` para validação de dados em todas as etapas: [optimal_question.schema.json](file:///home/marceloclaro/opencode-ecosystem-core/schemas/optimal_question.schema.json), [vector_execution_decision.schema.json](file:///home/marceloclaro/opencode-ecosystem-core/schemas/vector_execution_decision.schema.json), [ethical_assessment.schema.json](file:///home/marceloclaro/opencode-ecosystem-core/schemas/ethical_assessment.schema.json) e [scientific_claim.schema.json](file:///home/marceloclaro/opencode-ecosystem-core/schemas/scientific_claim.schema.json).
  - Implementado o módulo **OQS (Optimal Question Scanner)** (`mci/oqs/`) que avalia o poder de convergência de perguntas candidatas, mapeando lacunas conceituais e ambiguidades.
  - Implementado o **VSEE (Vector Shortcut Execution Engine)** (`mci/vsee/`) para desviar execuções custosas para caminhos vetoriais otimizados pré-validados com fallback automático.
  - Implementado o **EGS (Ethical Governance Scanner)** (`mci/egs/`) integrado ao TDD para triar a conformidade ética e aplicar hard-blocks em saídas sensíveis.
  - Integrado o fluxo científico na classe `MarceloClaroOrchestrator` (`marceloclaro/orchestrator.py`) com o método `run_scientific_governance()`, gerando relatórios em LaTeX e gravando as reflexões na memória global (`metabus`).
  - Adicionado o executável de lote em [run_research_batch.py](file:///home/marceloclaro/opencode-ecosystem-core/research/pipelines/run_research_batch.py) e o arquivo de cenários estruturados [scenario_matrix_v1.json](file:///home/marceloclaro/opencode-ecosystem-core/research/experiments/scenario_matrix_v1.json).
  - Adicionadas suítes completas de testes automatizados unitários e de integração em [test_run_research_batch.py](file:///home/marceloclaro/opencode-ecosystem-core/tests/test_run_research_batch.py) e [test_scientific_governance_pipeline.py](file:///home/marceloclaro/opencode-ecosystem-core/tests/test_scientific_governance_pipeline.py).
- **Utilitários do Ambiente WSL**:
  - Instalados pacotes `xclip` e `wl-clipboard` no ambiente WSL via gerenciador de pacotes `apt-get` para dar suporte à integração transparente da área de trabalho compartilhada com comandos da CLI do OpenCode.

## [1.0.1] - 2026-07-05

### Adicionado
- **Atalho automático na Área de Trabalho**: `publishing/production.py` agora mantém um symlink persistente `~/Desktop/Produção Científica - OpenCode` → `producao_cientifica/`. Detecta automaticamente `Desktop`, `Área de Trabalho` ou `Escritorio` (Linux/macOS/Windows). O atalho é garantido a cada inicialização de `ScientificProduction`, sem duplicação.

### Corrigido
- **MCP `metacognitive-interconnect`**: removido código morto (`_ = blackboard`, `_ = reflexion_engine`) e import não utilizado (`reflexion_engine`) do `mci/mcp_server.py` que não tinham efeito real — os singletons já são inicializados via import.
- **Tratamento de erros no MCP server**: o `except Exception: pass` no loop `run_stdio()` suprimia silenciosamente qualquer falha de parsing JSON ou erro de runtime. Substituído por `print(..., file=sys.stderr)` com mensagens descritivas, garantindo rastreabilidade.
- **Inconsistência `antigravity-bridge`**: `integrations/opencode_cli.py` (builder) gerava `enabled: False` enquanto o `opencode.json` no disco tinha `enabled: True`. Sincronizado para `True` em ambas as fontes e JSON regenerado.

## [1.0.0] - 2026-07-05

### Adicionado
- **Tabela Comparativa de Maturidade**: adicionado comparativo detalhado no `README.md` contra AutoGen, MetaGPT, Superhuman, LangGraph, CrewAI e OpenDevin, avaliando 7 critérios arquiteturais (Roteamento, Metacognição, QA, Economia, Ciência, Enxame, Diagnóstico) com avaliações em estrelas (⭐⭐⭐⭐⭐).
- **Notebooks de Demonstração End-to-End**: 3 notebooks interativos (executados com saídas reais) em `notebooks/` demonstrando o ciclo de vida do orquestrador, pipeline acadêmico Qualis A1 completo e algoritmos de enxame/teoria dos jogos.
- **Interface Web Streamlit**: painel de controle interativo (`webapp/app.py`) com 6 abas (Dashboard, Delegação, Pesquisa Acadêmica, Enxame & Jogos, Diagnóstico, Raciocínio & Quântico) para interação visual com o orquestrador `marceloclaro`.
- **Suporte a Modelos Locais via Ollama**: integração nativa (`research/llm_client.py`) para enriquecimento de resenhas críticas e fichamentos usando modelos locais (ex: llama3.2, qwen2.5), garantindo privacidade total e custo zero, com fallback para APIs OpenAI-compatíveis.

### Modificado
- **Pesquisa Acadêmica (`research/`)**: `hub.py` e `fichamento.py` refatorados para aceitar os parâmetros `use_llm`, `llm_provider` e `llm_model`, repassando o suporte Ollama de ponta a ponta.
- **Orquestrador (`marceloclaro/orchestrator.py`)**: método `research()` atualizado para expor as opções de provedor LLM.
- **Testes Unitários**: adicionados testes offline robustos para o `LLMClient` usando mock server (`test_llm_client.py`).

### Segurança
- **Privacidade Local**: o suporte ao Ollama garante que PDFs e dados de pesquisa não sejam enviados para APIs de terceiros durante o enriquecimento das resenhas críticas, operando em `localhost:11434`.
