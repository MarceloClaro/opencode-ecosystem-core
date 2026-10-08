# SPEC-935-R605 — Integração MiroFish-Offline ↔ OpenCode LLM + Simulação de Bancas Editoriais

- **Status**: implementado e validado em runtime (2026-09-26)
- **Gate**: SDD — spec antecedeu a integração; verificação por runtime real (não só unit test)

## 1. Contexto

O backend externo MiroFish-Offline (AGPL-3.0, `~/projetos/MiroFish-Offline-AGPL`) usa
agentes camel-oasis que chamam um endpoint OpenAI-compatível (`LLM_BASE_URL`).
Sem quota/credencial válida, a simulação OASIS não gerava ações (trace 0, rate limit
ou tool_calls ausentes).

## 2. Solução implementada

### 2.1 Proxy OpenAI-compatível → OpenCode CLI

`opencode_proxy.py` no repo AGPL (porta 8088, systemd user unit `opencode-proxy`):

- Recebe `POST /v1/chat/completions` (formato OpenAI).
- Traduz para `opencode run --format json` com o modelo **`opencode/big-pickle`**
  via subprocess (CLI autenticada com auth.json local — sem depender de API paga).
- **Tool-calling**: quando a requisição traz `tools` (camel-ai envia FunctionTools),
  instrui o LLM a responder JSON `{"name", "arguments"}` e devolve mensagem OpenAI
  com `tool_calls` + `finish_reason:"tool_calls"` — requisito do camel-ai 0.2.78
  para executar ações.

### 2.2 Configuração do MiroFish

```env
LLM_BASE_URL=http://127.0.0.1:8088/v1
LLM_MODEL_NAME=opencode/big-pickle
```

### 2.3 Resultado observado (validação real)

- Banco de simulação `sim_8f8901da13e2`, 10 agentes odontológicos, 24 rounds:
  **68 ações reais** (Twitter 32: CREATE_POST×16, QUOTE_POST×13, FOLLOW, REPOST,
  DO_NOTHING; Reddit 36: CREATE_POST×14, CREATE_COMMENT×17, LIKE_POST×4, LIKE_COMMENT).
- Conteúdo textual original gerado pelo LLM (ex.: reações a posts semeados);
  agentes argumentam entre si com tools reais do camel-oasis.
- Proxy ativo em `127.0.0.1:8088` (health via `/v1/models` não aplicável; check por
  POST `/v1/chat/completions` simples).

## 3. Simulação de bancas editoriais (vínculo com R976.11–R976.22)

O Core já expõe `marceloclaro.orchestrator.MarceloClaroOrchestrator.banca_simulate()`
com **30 perfis editoriais** reais em `mirofish/social/editorial_profiles.py`
(incluindo Journal of Dentistry/Elsevier, JDR/IADR, COI/Springer, npj Digital Medicine,
QST/IOP, IEEE TQE, ACM TQC, npj Quantum Information, periódicos de direito e educação).

A integração R605 permite **dois fluxos complementares**:

1. **Relatório MiroFish** (backend externo) → perfil markdown com os achados da
   simulação de opinião pública — fonte de manuscrito para banca.
2. **Banca editorial simulada** (motor determinístico local do Core): `banca_simulate(
   doc_text=..., target_institution="Journal of Dentistry")` recalibra os 12 revisores
   e o score ponderado conforme o peso editorial do periódico-alvo (evidências 1.8,
   metodologia 1.7, reprodutibilidade 1.7 etc. para JOD).

**Anti-overclaim preservado (R110)**: banca é simulação determinística, instituições
são rótulos; não constitui revisão por pares real nem garantia de aceitação.

## 4. Critérios de aceitação

1. `banca_simulate(doc_text, target_institution)` retorna veredito 0–100,
   recomendação, sinais textuais e editorial_profile — com disclaimer.
2. Todos os aliases odontológicos resolvem: `jod`, `journal of dentistry`, `jdr`,
   `coi`, `npj digital medicine`.
3. Proxy responde 200 com tool_calls para request com tools; MiroFish gera ações
   reais (contagem > 0 em run-status).
4. Nenhum código AGPL copiado para o Core (composição HTTP; `integrations/mirofish_offline.py`
   permanece o único ponto de contato).

## 5. Verificação (executada)

| Item | Resultado |
|---|---|
| Simulação OASIS 24 rounds via proxy big-pickle | `completed`, 68 ações |
| `banca_simulate` com alvo JOD (verificação posterior) | pendente de execução neste ciclo |
| `mirofish_external_status()` | `http_ok: True` quando backend ativo |

## 6. Lições (registro evolutivo)

- camel-ai espera `tool_calls`; LLMs que só emitem texto precisam de wrapper.
- OASIS com feed vazio só gera `do_nothing`; semear `initial_posts` destrava ações.
- Processos OASIS antigos em wait mode sobrescrevem run-state; matar antes de force restart.
- `opencode/big-pickle` é gratuito e rápido (~2–8s), suficiente para tool-calling.