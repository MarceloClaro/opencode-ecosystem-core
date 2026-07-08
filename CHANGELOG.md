# Changelog

Todas as mudanças notáveis no **OpenCode Ecosystem Core** serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

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
