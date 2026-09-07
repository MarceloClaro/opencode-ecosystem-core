# SPEC-935-R467: Inferência Real do runai via Daemon HTTP (serve)

## Objetivo
Fechar o elo de **inferência real** (não apenas provisionamento) da integração
do `runai`, expondo a API OpenAI-compatível do daemon `serve` através da ponte
`RunAIProvisioner`, do `ModelRouter` e do orquestrador — com validação real de
ponta a ponta.

## Descobertas empíricas que motivam esta spec

1. **Geração vazia com GGUFs Qwen 3 (causa raiz isolada):** testando
   node-llama-cpp 3.20.0 diretamente, `qwen3-0.6b` e `qwen3.5-2b` retornam
   `content: ""` / `completion_tokens: 0` com `finish_reason: "stop"`. O
   callback `onTextChunk` é disparado (os tokens SÃO gerados), mas cada chunk
   é `""`. A inspeção do tokenizer mostra que os GGUFs Qwen 3 usam
   `tokenizer.ggml.model = gpt2` com `tokenizer.ggml.pre = qwen2`; a
   detokenização de tokens de controle (BOS/EOS/`</s>`) retorna string vazia,
   e o modelo está prevendo tokens de controle no início da geração.
   **Embeddings funcionam** (forward pass sem sampling/detokenization).
2. **Modelo com tokenizer maduro funciona:** `llama3.2-1b` (Q8_0, 1,2 GB,
   tokenizer Llama 3) gerou texto corretamente pelo mesmo caminho de código:
   "I'm happy to help, but I need a bit more information…" via
   `LlamaChatSession.prompt()`.
3. **`runai bench` não conclui em ambiente CPU-only** (timeout em 2 execuções);
   não é usado como critério de saúde desta spec.
4. **Daemon real validado:** `runai serve --detach` (PID 95471, porta 11435)
   com `llama3.2-1b` respondeu:
   - `POST /v1/chat/completions` → `{"content":"Paris"}` (capital da França)
   - `POST /v1/completions` → `{"text":"France's capital is Paris."}`
   - `POST /v1/embeddings` → vetores reais (1536+ dimensões)
   - `GET /v1/models` → `["auto", "llama3.2-1b", "qwen3-0.6b", "qwen3.5-2b"]`
   - Streaming SSE → chunks `1`, `,`, ` `, `2`, `,`, ` `, `3` (contagem)

## Escopo
### Incluído
- `RunAIProvisioner` com métodos HTTP de inferência real:
  `serve()`, `stop()`, `is_serving()`, `api_health()`, `chat()`, `complete()`,
  `embed()`, `list_server_models()`, `http_base_url()`.
- `ModelRouter`: rota real para `runai` quando o daemon está ativo;
  `ValueError` claro (com instrução) quando está apenas provisionando.
- Orquestrador: `runai_serve/runai_stop/runai_is_serving/runai_chat/
  runai_complete/runai_embed` + status com `serving`/`api_base`.
- Testes com mocks HTTP (payload, URL, offline) + smoke real opt-in
  (`RUNAI_REAL=1`) que consome o daemon HTTP quando disponível.
- Documentação honesta: GGUFs Qwen 3 geram vazio neste ambiente (ver anti-overclaim).

### Excluído
- Streaming SSE pelo cliente `chat()` (retorna erro explícito
  `stream_unsupported` em vez de fingir suporte).
- `runai bench` como critério de saúde (timeout conhecido em CPU-only).
- Correção dos GGUFs Qwen 3 / upgrade de node-llama-cpp (fora do controle
  do ecossistema; documentado para o usuário).
- Download automático de modelos pesados por padrão.

## Critérios de Aceitação
- [E1] `RunAIProvisioner.is_serving()` detecta o daemon ativo via `/health`.
- [E2] `chat()`/`complete()`/`embed()` retornam erro estruturado
      `daemon_offline` quando o daemon não está ativo (sem exceção).
- [E3] `chat()` posta o payload correto em `/v1/chat/completions` e devolve
      a resposta OpenAI-compatível.
- [E4] `complete()` posta `prompt` em `/v1/completions`.
- [E5] `embed()` posta `input` em `/v1/embeddings`.
- [E6] `ModelRouter.route(force_provider="runai", ...)` lança `ValueError`
      com instrução quando o daemon está offline e permite rota real
      (`mock_mode=False`) quando está ativo.
- [E7] `status()["providers"]["runai"]` expõe `serving` e
      `provisioning_only` dinâmico.
- [E8] Orquestrador expõe `runai_serve/stop/is_serving/chat/complete/embed`.
- [E9] Smoke real `RUNAI_REAL=1` consome o daemon HTTP e verifica conteúdo
      não vazio em chat e completions, e vetor não vazio em embeddings.
- [E10] Nenhum teste toca `evolution/cycles.json` real (isolamento por
       instância).

## Anti-overclaim
- A compatibilidade com **Qwen 3 GGUF é limitada** neste ambiente: embeddings
  funcionam, mas **geração retorna vazio** (tokens de controle com
  detokenização vazia em node-llama-cpp 3.20.0). Não alegamos suporte de
  geração para esses GGUFs.
- "Inferência real" refere-se a `llama3.2-1b` (e modelos com tokenizer
  maduro/bem suportado), validada por smoke real automatizado.
- O daemon serve é um processo local do `runai`, não infraestrutura gerenciada
  por nós; `serve`/`stop` apenas delegam ao CLI.
- O sucesso do smoke real depende de o daemon estar ativo; o teste pula (não
  falha) quando ausente.

## Registro
- Autores: Marcelo Claro Laranjeira (orquestração), runai/canirun.ai (upstream)
- Data: 07 de setembro de 2026
- Ciclo: R467
- Especificações relacionadas: R464 (provisionamento), R465 (hardening),
  R466 (source fallback)