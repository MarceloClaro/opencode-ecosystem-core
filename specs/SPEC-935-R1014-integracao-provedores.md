# SPEC-935-R1014 — Integração com Mais Provedores de Embedding e LLM

## 1. Introdução

Esta especificação define o framework para integração com provedores adicionais de embedding e LLM beyond os provedores atualmente suportados, operando sob o protocolo SDD/TDD do ecossistema OpenCode Core. O foco é extensibilidade mantendo postura anti-overclaim.

## 2. Provedores Atualmente Suportados

### 2.1. Provedores Primários
- **OpenAI**: embeddings e chat completions (padrão de referência)
- **Anthropic**: modelos Claude para comparação e diversidade
- **Google Gemini**: suporte via CLI e MCP

### 2.2. Provedores Secundários / Em Desenvolvimento
- **Ollama**: modelos locais via HTTP OpenAI-compatível
- **Colibri**: GLM-5.2 via interface integrada
- **DeepSeek Reasonix**: raciocínio avançado via CLI

## 3. Protocolo de Integração de Novos Provedores

### 3.1. Etapa A: Registro de Capacidades
Cada novo provedor deve ser registrado com:
- Nome identificador único
- Tipo de serviço (embedding, chat, completions)
- Endpoint HTTP/OpenAI-compatível
- Autenticação requerida (API key, token, etc)
- Modelos disponíveis
- Limites de taxa e custo

### 3.2. Etapa B: Teste de Conectividade
- Verificar disponibilidade do endpoint
- Validar autenticação com chave de teste
- Medir latência de resposta
- Confirmar formatos de request/response

### 3.3. Etapa C: Mapeamento de Capabilities
Mapear capacidades do provedor para o framework do Core:
- Tipo de embedding (dense, sparse, hybrid)
- Tamanho de contexto máximo
- Janela de contexto suportada
- Formatos de resposta compatíveis

## 4. Design de Interface Unificada

### 4.1. Adapter Pattern
Cada provedor deve implementar um adapter seguindo o padrão:
- `embed(texts: List[str]) -> List[List[float]]`
- `chat(messages: List[Dict]) -> Dict`
- `health_check() -> Dict`

### 4.2. Feature Flags
- Provedores podem ser ativados/desativados via flags de configuração
- Fallback automático entre provedores quando um falha
- Prioridade configurável para cada provedor

## 5. Critérios de Aceitação

A1: Pelo menos 3 provedores além dos primários estão registrados e testados
A2: Cada provedor registrado passa em health_check com status "healthy"
A3: Adapters seguem interface padronizada (embed, chat, health_check)
A4: Feature flags funcionais para ativar/desativar provedores
A5: Nenhum provedor é declarado "melhor" ou "padrão ouro" sem benchmarking

## 6. Limites e Responsabilidades

L1: Integração de provedores não demonstra preferência por um provedor em relação outros. Apenas expandia as opções disponíveis.

L2: Custos e taxas de cada provedor são de responsabilidade do operador.

L3: Chaves de autenticação e segredos nunca são armazenados no código-fonte.

L4: Oorchestador marceloclaro permanece responsável pelo ciclo SDD/TDD.

L5: Novos provedores são adicionados via configuração, não via código hardcoded.

## 7. Plano de Implementação

1. **RED**: Documentar framework de integração (SPEC-935-R1014) e testes de infraestrutura.

2. **GREEN**: Implementar suporte a provedores adicionais (Ollama, Colibri, DeepSeek); conectar ao orquestrador marceloclaro; validar health checks.

3. **REFACTOR**: Otimizar cadência de integração; garantir que adapters seguem interface padronizada; validar hashes de configurações e health check results.

4. **VERIFY**: Executar health checks em todos os provedores registrados; gerar relatório de integração de provedores.

5. **REFLECT**: Registrar lições no MetaBus; atualizar confidence ledger apenas para falhas operacionais; registrar ciclo de evolução R1014.

## 6. Evidência Esperada

- `tests/test_r1014_integracao_provedores.py` com testes RED/GREEN
- `docs/evidence/R1014_*/` com resultados de health_check por provedor
- `specs/SPEC-935-R1014.md` (este documento) com status final
- Relatórios de health_check e capacidades de cada provedor
- Registro de evolução no EvolutionRegistry

## 7. Referências Internas

- SPEC-935-R1013 — Hipóteses H9-H10 de propriedades emergentes avançadas em RAG
- SPEC-935-R1012 — Hipóteses H6-H8 de propriedades emergentes avançadas em RAG
- SPEC-935-R112 — Goal Drift Detection no Trust Engine
- SPEC-935-R886 — Ciclo metacognitivo integrado
- CORRIGENDUM.md — Histórico de alegações corrigidas

---

*Esta spec foi desenvolvida seguindo protocolo SDD rigoroso. Integração de provedores expande opções disponíveis sem declarar preferência ou qualidade superior. Todos os resultados ficam restritos ao escopo local até validação externa independente.*