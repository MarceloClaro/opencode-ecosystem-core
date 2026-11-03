# Governança de custo de tokens — SPEC-981

**Revisão:** 2026-10-30 · **Registro:** `integrations/cost_registry.json` ·
**Motor:** `integrations/cost_governance.py` · **Comando:** `/custos` ·
**CLI:** `python3 -m marceloclaro.cli custos`

Este guia responde a uma pergunta prática: **quanto custa a inferência do
Core, em cada superfície, e como usar o modelo mais barato que ainda resolve
a tarefa?** Ele não substitui a fatura do provedor: mede custo **estimado** a
partir de tarifas declaradas por catálogo consultado.

> `/custos` (custo monetário) e `/economy` (token economy: stakes, slashing,
> fees) medem grandezas **diferentes**. Somar as duas é erro de leitura.

---

## 1. As seis superfícies e o que cada uma cobra

| Superfície | Tipo | O que é cobrado | Observação |
|---|---|---|---|
| `local-ollama` | compute local | nada por token | energia/VRAM do operador |
| `local-litert-lm` | compute local | nada por token | janela contratada: 20 480 tokens (R211) |
| `local-colibri` | compute local | nada por token | faixa curta: triagem, não entrega |
| `nvidia-nim` | API metered | token (0/0 publicado em 19 modelos) | **não habilitada** — ver §6 |
| `opencode-zen` | API metered | token | 41 modelos com 0/0 publicado |
| `opencode-go` | API metered | token | plano Go: mesma id, tarifa menor |
| `gemini-api` | API metered | token | camada gratuita tem cota própria |
| `gemini-cli` | free tier | cota do plano | não é preço por token |
| `openai-api` | API metered | token | API ≠ créditos de assinatura |
| `openai-codex` | assinatura | créditos do plano | não é preço por token |
| `antigravity` | assinatura | cota do plano | sem tarifa por token publicada |

**Leitura honesta do `0/0`:** o catálogo publica custo zero tanto para
modelos realmente gratuitos quanto para modelos sem preço publicado. Por isso
o registro marca a origem (`published: free` ou `metered`) e o relatório não
promete conta grátis — promete tarifa declarada.

---

## 2. Como o Core escolhe o modelo

Complexidade → cadeia ordenada. O primeiro degrau é o modelo **fixado** do
agente; os seguintes são fallbacks declarados em
`agent.<id>.options.model_fallbacks`.

| Complexidade | Cabeça | Cadeia | Quem entra |
|---|---|---|---|
| `trivial` | `litert-lm/…gemma-4-E2B…` (local) | + colibri + `mimo-v2.6-flash-free` | extração, classificação, formatação |
| `simples` | `opencode-zen/mimo-v2.6-flash-free` | + `mimo-v2.6-flash` + `deepseek-v4.1-flash` | redação, documentação, revisão leve |
| `media` | `opencode-go/mimo-v2.6-flash` | + `deepseek-v4.1-flash` + `minimax-m3.1-flash` | implementação, testes, refatoração |
| `complexa` | `opencode-go/deepseek-v4.1-flash` | + `mimo-v2.6-flash` + `deepseek-v4-pro` + `kimi-k2.7-code` | arquitetura, SDD/TDD, pesquisa crítica |
| `critica` | `opencode-go/deepseek-v4-pro` | + `kimi-k2.7-code` + `opencode-zen/deepseek-v4-pro` | auditoria, prova, release |

**Por que free não é a cabeça da implementação:** medido no Core, não por
opinião. R499 (tarefa IMO com scaffold MASWOS) — `mimo-v2.5-free` 0,987,
acurácia 1,0 em matemática. R506 (benchmark de código) — `mimo-v2.5-free`
**1/9**, `big-pickle` **0/9**, `nemotron-3-ultra-free` **2/9** corretos, com
`code_missing` e `IndentationError`. Free entra como cauda (onde a falha é
barata), não como cabeça de código.

A complexidade é classificada do **cartão declarado** do agente (id,
categoria, tipo, tags). As capabilities **derivadas** pelo loader só entram
como segundo passe — sem isso, rótulos amplos como `code_review` jogavam o
`coder` na faixa crítica.

---

## 3. Custo por superfície (1M de entrada, 80% em cache + 100k de saída)

| Modelo | Superfície | US$ |
|---|---|---:|
| `mimo-v2.6-flash` | opencode-go | **0,0582** |
| `deepseek-v4.1-flash` | opencode-go | 0,0924 |
| `mimo-v2.5` | opencode-go | 0,0582 |
| `minimax-m3.1-flash` | opencode-go | 0,1020 |
| `deepseek-v4.1-flash` | opencode-zen | 0,3048 |
| `gpt-5-nano` | openai-api | 0,0540 |
| `gemini-2.5-flash` | gemini-api | 0,3340 |
| `deepseek-v4-pro` | opencode-go | 0,1965 |

O valor real depende de **três** coisas, não só do preço de tabela: a fração
de entrada em cache, a razão saída/entrada e quantas tentativas a tarefa
custa. Por isso o gate do Core exige medir custo **por tarefa aceita**
(entrada + saída + raciocínio + cache + ferramentas + falhas + retrabalho).

---

## 4. Orçamento fail-closed

```python
from integrations.cost_governance import BudgetLedger, Usage, estimate_cost

ledger = BudgetLedger()                      # .mci_state/cost_ledger.jsonl
est = estimate_cost("opencode-go", "kimi-k3", Usage(input_tokens=1_000_000, output_tokens=1_000_000))
decisao = ledger.check("opencode-go", ceiling_usd=1.00, pending=est)
if not decisao.allowed:
    print(decisao.reason, "→", decisao.alternative)
```

Regras: acima do teto **bloqueia**; superfície local **não bloqueia** (custo de
token zero); custo **não verificável** (tarifa desconhecida) **bloqueia** —
nunca se presume barato o que não se sabe precificar.

---

## 5. Como desligar ou ajustar

`integrations/cost_registry.json` → `policy`:

```json
"policy": {
  "apply_head_model": true,
  "ceiling": "capaz"
}
```

- `apply_head_model: false` → os agentes mantêm o modelo global e apenas
  **publicam** a cadeia (nada de fixação de modelo).
- `ceiling` → teto de faixa permitido por complexidade.
- Agente com `model:` no próprio cartão continua autoritativo (10 agentes).
- O primário (`marceloclaro`) **nunca** recebe fixação de modelo: conserva o
  modelo global da sessão.

---

## 6. NVIDIA: declarada, não habilitada

`nvidia-nim` entra no registro com 20 modelos (19 deles com 0/0 publicado,
incluindo `minimaxai/minimax-m3.1-flash`, `nvidia/nemotron-3-ultra-550b-a55b`,
`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, `deepseek-ai/deepseek-v4.1-flash`,
`z-ai/glm-5.3-flash`, `moonshotai/kimi-k3`, `openai/gpt-oss-20b`).

O provider **não** é habilitado automaticamente: exigiria `NVIDIA_API_KEY` e
uma superfície nova no `opencode.json`. O bloco pronto está em
`cost_governance.suggested_provider_blocks()` — a aplicação é do operador,
explícita, e pode ser revertida sem tocar no resto.

---

## 7. Limites conhecidos

1. Tarifas são **declaradas**, não observadas: confira a fatura real.
2. Superfícies de assinatura e free tier não têm preço por token.
3. `0/0` pode significar "sem preço publicado" em vez de "gratuito".
4. O catálogo do provedor é lista, não entitlement: a chamada real é que
   confirma acesso.
5. O `ledger` registra estimativas: ele serve para decidir, não para atestar.
6. Nenhum benchmark de qualidade foi executado por esta spec; a justificativa
   free/não-free para código vem do R506 já medido no Core.

---

## Fontes

- Primária — `https://models.dev/api.json`, consultada em 2026-10-30.
- Secundária — tabela de tarifas enviada pelo operador (OpenCode Zen/Go),
  2026-10-30, usada para confronto.
- Schema da configuração — `https://opencode.ai/config.json` (`agent.options`
  livre; `provider.models.<id>.cost` com `input`/`output`/`cache_read`).
- Spec — `specs/SPEC-981-governanca-custo-de-tokens.md`.
- Testes — `tests/test_r917_cost_governance.py` (46 casos).
