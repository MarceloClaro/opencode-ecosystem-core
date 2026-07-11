# R128 — Encanamento seguro de chaves LLM (OpenAI) via ambiente + LLM local Ollama

## Objetivo

Habilitar provedores LLM de nuvem (OpenAI e compatíveis) e o LLM local
(Ollama) no ecossistema de forma **segura por construção**: chaves vivem
apenas em variáveis de ambiente / `.env` protegido, nunca versionadas
nem impressas. Corrigir o risco real de `.env` fora do `.gitignore`,
fornecer `.env.example`, um carregador de `.env` (acessibilidade) e dar
visibilidade via `doctor` de qual provedor LLM está disponível.

## Motivação

Pedido do usuário: habilitar a API da OpenAI para "melhorar a gestão de
tokens" e ter um LLM local real via Ollama. A investigação mostrou que o
suporte a OpenAI **já existia** em `research/llm_client.py` (lê
`OPENAI_API_KEY`/`OPENAI_API_BASE`/`OPENAI_MODEL`; `provider="auto"`
prioriza Ollama local e cai para OpenAI). Faltava o **encanamento seguro**
e a ativação prática.

**Risco real encontrado:** `.env` NÃO estava no `.gitignore` — um `.env`
com a chave seria commitável por acidente.

**Restrição de acessibilidade:** o usuário informou não conseguir
digitar/colar a chave (a CLI do OpenCode não aceitava colagem). Isso
justificou (a) escrever a chave no `.env` protegido por ele e (b) um
carregador de `.env` que injeta a chave no ambiente sem exportação manual.

## Mudanças Entregues

1. **`.gitignore`**: passa a ignorar `.env`, `.env.local`, `.env.*.local`,
   `*.pem`, `*.key`, mantendo `.env.example` versionado (negação `!`).
2. **`.env.example` (novo)**: modelo com variáveis vazias/padrão
   (`OPENAI_API_KEY=`, `OPENAI_API_BASE`, `OPENAI_MODEL`, `OLLAMA_HOST`,
   `OLLAMA_MODEL`, `OPENCODE_*`) — sem nenhum segredo, com orientação de
   que Ollama local é a via de custo zero e OpenAI é fallback de nuvem.
3. **`marceloclaro/doctor.py`**: `_ollama_available()` +
   `_check_llm_providers()` — reporta Ollama local e se `OPENAI_API_KEY`
   **está definida** (apenas o booleano, **nunca** o valor); `pass` com
   ≥1 provedor, `warn` (nunca `fail`) se nenhum. Ligado a `run_doctor()`.
4. **`marceloclaro/env_loader.py` (novo)**: carregador de `.env` sem
   dependências, chamado em `cli.main()`. Injeta variáveis do `.env`
   protegido sem sobrescrever o shell e sem imprimir valores — para o
   ecossistema reconhecer a chave sem exportação manual (acessibilidade).
5. **`tests/test_r128_openai_provider.py` (novo)**: 13 testes TDD
   (proteção do `.env`, ausência de segredo no `.env.example`, o check do
   doctor, a não-exposição do valor da chave, e o loader).

**Ações locais (NÃO versionadas):**
- `.env` criado com a chave de teste do usuário (permissão `600`,
  protegido pelo `.gitignore`, ausente do `git status`).
- Ollama já instalado (v0.31.1, servidor ativo); modelo de geração
  `llama3.2` (o padrão do ecossistema em `llm_client.py`) baixado, além do
  `nomic-embed-text` (embeddings do RAG/Graphify) já presente.

## Verificação

- TDD: testes escritos antes → vermelho (8 failed) → verde (13 passed).
- `git check-ignore .env` confirma proteção; `git status` **não** mostra
  `.env` (segredo nunca versionado).
- Prova E2E: `python3 -m marceloclaro.cli doctor` reporta
  `llm_providers: pass` (Ollama local + OpenAI) **sem** vazar o valor da
  chave; `LLMClient(provider='openai')` resolve `openai/gpt-4o-mini` com
  o `.env` carregado.
- `python3 -m pytest tests/ -q` completo.

## Lições

1. Segredo colado em chat/arquivo deve ser tratado como comprometido — a
   chave do usuário foi orientada a rotação e **nunca** foi versionada
   nem impressa de volta; o único lugar dela é o `.env` local (600,
   gitignored). O encanamento seguro (gitignore + loader + check que não
   vaza valor) é o que permite atender o pedido de acessibilidade sem
   abrir mão da segurança.
2. Suporte a um provedor já existir no código (`llm_client`) não é o
   mesmo que estar **ativável**: faltavam a proteção do segredo, o modelo
   de configuração e a visibilidade (doctor). O mesmo padrão de "motor
   existe, falta exposição" já visto no R125/R127 reaparece aqui na
   camada de configuração/segredo.
3. "Melhorar a gestão de tokens" com OpenAI é um equívoco comum: a Token
   Economy do ecossistema é interna/virtual (não billing); quem reduz
   custo real é o roteamento para o **Ollama local** (custo zero), com a
   OpenAI como fallback de qualidade. Por isso o `.env.example` e o
   doctor deixam explícita a preferência Ollama → OpenAI.

## Score

**8.6/10**

- Corrige um risco real de segurança (.env fora do gitignore), atende a
  restrição de acessibilidade sem versionar segredo, e ativa de fato o
  LLM local (Ollama/llama3.2) + o fallback OpenAI, tudo verificado E2E.
- Não toca a frente SPEC-108 (`opencode.json`/`integrations`), mantendo o
  escopo limpo; o bloco `openai` do OpenCode CLI fica documentado no
  `.env.example`, não editado.
- Não resolve o lado do OpenCode CLI como binário externo (que lê o
  ambiente do shell) — a ativação lá depende do `export` no perfil do
  shell, deixado como orientação, não automatizado neste ciclo.
