---
spec_id: SPEC-935-R622
title: "Contrato Canônico de Metadados do Catálogo de Modelos (schema uniforme em ModelRouter.list_all_models)"
component: integrations/model_router.py + integrations/litert_lm.py + integrations/litert_lm_provider.py + integrations/runai.py
test_file: tests/test_r622_model_catalog_contract.py
status: green
depends_on: [SPEC-935-R211, SPEC-935-R500, SPEC-935-R499]
---

# SPEC-935-R622 — Contrato Canônico de Metadados do Catálogo de Modelos
=====================================================================

## 1. Visão Geral

`ModelRouter.list_all_models()` agrega os catálogos de seis provedores
(`opencode-go`, `opencode-zen`, `litert-lm`, `openai`, `runai` e o catálogo
free curado R499). A agregação hoje é uma **concatenação crua** de dicionários:
cada provider devolve o que sua própria fachada considera suficiente, e o
router repassa a divergência ao consumidor sem qualquer reconciliação.

Medição real do baseline (`list_all_models()`, 46 entradas):

| Anomalia | Alcance observado | Evidência |
|---|---|---|
| **A1** — chave de identidade `id` em vez de `model_id` | 3 modelos (`runai`) | `KeyError` em qualquer consumidor que padronize |
| **A2** — dois campos de contexto conflitantes | 4 modelos (`litert-lm`) | `context=20480` **e** `context_window=32768` no mesmo dict |
| **A3** — família declarada incorreta | 1 modelo | `litert-community/Qwen3-0.6B` reporta `family="google"` |
| **A4** — flag `free` ausente | 26 de 46 modelos | `openai`, `opencode`, `opencode-go` e 1 `opencode-zen` |

Nenhuma delas é cosmética. A2 e A3 são **falsificação de metadado** — o
catálogo afirma duas verdades contraditórias e atribui a um modelo Qwen a
procedência de um Gemma. A1 e A4 quebram o contrato de acesso.

## 2. Causa-Raiz

### 2.1 A1 — `runai.py:672`
`RunAIProvisioner.list_models()` emite `{"id": model_id, **meta}`. É o único
provider do ecossistema que nomeia a identidade assim; os outros cinco usam
`model_id`. O `id` não pode ser removido: `model_info()`, `health_check()` e
consumidores externos dependem dele.

### 2.2 A2 — o merge legado `litert_lm.py:336-360`
`integrations/litert_lm.py` mantém um catálogo legado (`MODELS` com IDs curtos)
e o funde por alias nos IDs canônicos de `litert_lm_provider.MODELS`. O campo
`context_window` **não existe** no catálogo canônico — lá o campo contracted se
chama `context`. O laço usa `setdefault`, então injeta `context_window: 32_768`
(stale, anterior à política R211) ao lado do `context: 20480` contratado.

> **Restrição dura (R211):** `test_r211_remaining_politica_contexto_20480_e_consistente_em_todas_as_fontes`
> exige `integrations.litert_lm_provider.MODELS[*]["context"] == 20_480`,
> concordante com `opencode.json`, o plugin TypeScript e o runtime. Logo
> `context` **não pode ser renomeado** e 20480 **não pode mudar**. O defeito é
> a *injeção do segundo campo*, não o campo contratado.

### 2.3 A3 — o mesmo laço, campo `family`
O alias `gemma-3-1B-it → litert-community/Qwen3-0.6B` faz o `setdefault`
copiar `family: "google"` do Gemma para o Qwen. `family` é **atributo de
identidade** do modelo físico, não dica de roteamento: ele jamais deve atravessar
o boundary de alias.

### 2.4 A4 — catálogos incompletos
`opencode_go.MODELS` (16 chaves) e `openai_provider.MODELS` (5 chaves) não
declaram `free`. A ausência é ambígua: `model.get("free")` retorna `None`, e
`bool(None)` é `False` — o mesmo valor de um provedor explicitamente pago, por
caminho de código diferente.

## 3. Requisitos Funcionais

### RF1 — `normalize_model_entry()` (novo, em `model_router.py`)
Função pura e testável isoladamente, com assinatura:
```python
def normalize_model_entry(entry: Mapping[str, Any]) -> Dict[str, Any]
```
Regras, aplicadas nesta ordem:
1. **Identidade** — a entrada DEVE conter `model_id`. Se contiver apenas `id`,
   `model_id` é preenchido a partir dele. Se contiver ambos e divergirem, a
   entrada é marcada `contract_errors += ["identity_mismatch"]` e
   `model_id` **prevalece sobre** `id` (é a chave canônica).
2. **Contexto** — resolve uma única fonte de verdade:
   - se `context_window` e `context` estiverem ambos presentes **e divergirem**,
     registra `contract_errors += ["context_conflict"]` e **prevalece
     `context`** (o campo contracted por R211);
   - se apenas `context_window` existir, adota-o;
   - se apenas `context` existir, adota-o;
   - **se nenhum existir**, o valor vem de `CONTEXT_DEFAULTS` e a entrada é
     marcada `context_unknown` (ver RF2b) — a chave nunca fica ausente, e o
     número nunca é inventado em silêncio;
   - o resultado é sempre publicado em `context_window`; `context` é removido.
3. **Família** — se ausente, ausente permanece. RF1 **não inventa** família.
4. **Gratuidade** — se `free` ausente, o valor vem da política explícita
   `FREE_DEFAULTS` indexada por `provider`. A chave `free` fica **sempre
   presente** na saída.
5. **Nenhuma chave é apagada** exceto a duplicata de contexto resolvida.
   Metadados específicos de provider (`size_gb`, `backend`, `task_types`,
   `description`, `score`, `source`, `accessible`) atravessam intactos.

### RF2 — `FREE_DEFAULTS` (novo, em `model_router.py`)
Política **explícita e auditável**, com a justificativa de cada entrada em
comentário. Sem fallback silencioso: um provider ausente do dicionário recebe
`free=False` **e** `contract_errors += ["free_unknown"]` — o default é
*pessimista* (fail-closed) e sinalizado, nunca silenciosamente verdadeiro.

| provider | `free` | Justificativa |
|---|---|---|
| `litert-lm` | `True` | on-device, CPU, sem billing |
| `runai` | `True` | binário local/daemon do próprio operador |
| `openai` | `False` | BYO-key, consumo token meterizado pela OpenAI |
| `opencode-go` | `False` | plano/assinatura OpenCode Go |
| `opencode` | `False` | catálogo curado free R499, mas provedor com plano |
| `opencode-zen` | `False` | curadoria mista; default pessimista |

### RF2b — `CONTEXT_DEFAULTS` (novo, em `model_router.py`)
A medição do baseline revelou um **quinto defeito** que a análise inicial não
previu: os 3 modelos de `runai` **não publicam janela de contexto alguma**. Sem
a regra acima, eles permaneceriam sem `context_window` e o contrato de CA3 seria
inatingível — mas inventar um número seria afirmar algo não medido sobre a
capacidade do modelo.

Solução: um **piso declarado e sinalizado**, com o mesmo caráter fail-closed de
RF2.

| provider | piso | Justificativa |
|---|---|---|
| `runai` | 4 096 | Catálogo local de 2B–4B. O `runai` não publica limite e **não está instalado no ambiente** (`which runai` → ausente), logo não há como medir. O piso é deliberadamente conservador: um chamador que confie nele nunca estoura o limite real. O valor verdadeiro deve ser lido do modelo servido. |

Toda entrada que recebe o piso carrega `context_unknown` em `contract_errors`.
Um provider **ausente** de `CONTEXT_DEFAULTS` fica sem `context_window` — melhor
ausência explícita do que uma cifra inventada; nenhum provider do catálogo atual
cai nesse caso.

### RF3 — `list_all_models()` normalizado
Todo item de `list_all_models()` passa por `normalize_model_entry`. Nenhum
consumidor deve precisar conhecer a fachada de origem. A lista continua sendo a
concatenação das mesmas fontes (nenhum modelo é ganho ou perdido por esta spec).

### RF4 — Fontes corrigidas na origem
- `runai.list_models()` emite **as duas** chaves (`id` e `model_id`) com o mesmo
  valor — retrocompatível, sem quebrar `model_info()`.
- O laço de merge legado **não** copia `family` nem `context_window` entre
  aliases. `family` passa a ser declarado **no catálogo canônico**, tornando-o
  autossuficiente.
- `litert_lm_provider.MODELS` ganha `family` e `free` declarados por modelo,
  preservando `context: 20480` intacto (R211).
- O fallback remoto `_fetch_remote_models` deixa de assumir `32_768` cru e usa
  o valor contratado.

## 4. Contrato de Aceitação (CA)

| ID | Critério | Verificação |
|---|---|---|
| CA1 | Todo item de `list_all_models()` possui `model_id` não vazio | `test_todo_modelo_tem_identidade` |
| CA2 | Nenhum item possui `id` divergente de `model_id` | `test_todo_modelo_tem_identidade` |
| CA3 | Todo item possui `context_window` inteiro positivo | `test_todo_modelo_tem_contexto_unico` |
| CA4 | Nenhum item possui a chave `context` residual | `test_todo_modelo_tem_contexto_unico` |
| CA5 | Nenhum item tem conflito de contexto não sinalizado | `test_todo_modelo_tem_contexto_unico` |
| CA6 | Todo item possui `free` booleano | `test_todo_modelo_declara_gratuidade` |
| CA7 | `free` ausente na origem → política explícita, nunca `None` | `test_free_desconhecido_e_sinalizado` |
| CA8 | `Qwen3-0.6B` reporta família de sua família real, não do alias | `test_familia_nao_atravessa_alias` |
| CA9 | `context: 20480` do catálogo canônico **preservado** (R211) | `test_r211_politica_de_contexto_preservada` |
| CA10 | Normalização é **fail-closed e aditiva**: não apaga metadados de provider | `test_normalizacao_preserva_metadados_especificos` |
| CA11 | Normalização é **idempotente** | `test_normalizacao_e_idempotente` |
| CA12 | Normalização é **pura**: não muta o dict de entrada | `test_normalizacao_nao_muta_entrada` |
| CA13 | `normalize_model_entry` funciona em provider isolado sem router | `test_normalizacao_pura_com_entrada_minima` |
| CA14 | `runai.list_models()` emite `id` e `model_id` coerentes | `test_runai_emite_ambas_as_chaves` |
| CA15 | Contagem de modelos preservada (nenhum ganho/perda) | `test_normalizacao_nao_altera_contagem` |
| CA16 | Catálogo canônico LiteRT autossuficiente (declara `family`/`free`) | `test_catalogo_canonico_litert_autossuficiente` |
| CA17 | Contexto suprimido pela política é **sinalizado** (`context_unknown`) e nunca confundido com contexto publicado | `test_contexto_ausente_vira_piso_declarado_e_sinalizado` + `test_contexto_publicado_nao_e_marcado_como_desconhecido` |

## 5. Fora de Escopo

- **Não** renomear `context` → `context_window` no catálogo canônico: violaria R211.
- **Não** alterar o valor 20480 nem qualquer `limit.context` publicado.
- **Não** decidir se um modelo pago é "de fato" gratuito por inferência de
  preço — RF2 é política declarada, não medição.
- **Não** afirmar a janela de contexto real dos modelos `runai`: o piso de
  RF2b é política rotulada, e o valor verdadeiro exige ler o modelo servido.
- **Não** remover `id` de `runai` (retrocompatibilidade).
- **Não** alterar o roteamento (`route()`, `route_free()`): esta spec é
  ortogonal ao choix do modelo e toca apenas a superfície de *listagem*.
- **Não** adicionar famílias inferidas por heurística de nome.

## 6. Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Consumidor legado dependia de `context` na saída do router | `context` era duplicata contraditória; a remoção é o conserto. Nenhum leitor em `integrations/`, `transformer/` ou `tests/` consome `["context"]` de `list_all_models()` (verificado por varredura) |
| Remoção da cópia de `family` deixa a entrada canônica sem família | RF4 declara `family` explicitamente no catálogo canônico (CA16) |
| `FREE_DEFAULTS` vira fonte paralela de verdade | É política de *exibição*, não de *roteamento*; `route()` não a consulta (verificado) |
| Contagens variam com a disponibilidade de provider no ambiente | CA15 compara antes/depois na **mesma** instância, nunca contra constante absoluta |

## 7. Rastreabilidade

- **SPEC-935-R211** → CA9 (política de contexto 20480 élei superior e preservada).
- **SPEC-935-R499 / R500** → CA6, CA7 (catálogo free curado passa a declarar `free` de forma uniforme).
- **AGENTS.md §4 (anti-overclaim)** → CA7 (`free_unknown` é sinalizado, não escondido) e §5 da Seção 2.4 (default pessimista).
