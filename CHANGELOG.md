# Changelog

Todas as mudanças notáveis no **OpenCode Ecosystem Core** serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

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
