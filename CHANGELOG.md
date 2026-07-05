# Changelog

Todas as mudanças notáveis no **OpenCode Ecosystem Core** serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

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
