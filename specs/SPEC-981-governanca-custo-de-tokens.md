---
spec_id: SPEC-981
title: Governança de custo de tokens multi-superfície com cadeias free→capaz por agente
version: 1.0.0
status: green
test_file: tests/test_r981_cost_governance.py
---

# SPEC-981 — governança de custo de tokens

## Objetivo e escopo

O Core executa em seis superfícies de inferência (Ollama/NVIDIA on-device,
OpenCode Zen/Go, Gemini, OpenAI, Antigravity) com semânticas de custo
heterogêneas: token cobrado, cota de assinatura, tier gratuito ou compute
local. Antes desta spec não existia registro de tarifas nem contabilidade de
dinheiro: o comando `economy` mede *stakes* da token economy
(`economy/token_economy.py`), que é garantia de comportamento, não gasto.

Entregas: (1) registro declarado de tarifas por superfície, com procedência;
(2) motor de estimativa e de orçamento fail-closed; (3) classificação de
complexidade por agente e cadeia ordenada de fallback free→capaz; (4) anual
da configuração do OpenCode por provider e por agente; (5) comando `custos`
separado da token economy.

Fora de escopo: alterar o modelo global da sessão; habilitar provider novo
sem chave; medir cobrança observada; comparar qualidade entre modelos.

## Extração das fontes

Tarifas primárias: catálogo público `https://models.dev/api.json`, consultado em
2026-10-30 (234 providers; `opencode`, `opencode-go`, `nvidia`, `openai`,
`google`, `anthropic`, `moonshotai` verificados). Secundária: tabela de tarifas
enviada pelo operador (OpenCode Zen/Go, 2026-10-30), usada para confronto.

Divergências registradas sem conciliação silenciosa: `deepseek-v4-pro` aparece
como 1,32/3,96/0,044 na tabela do operador e 1,74/3,48/0,145 no catálogo
consultado; a linha "chave" (0,24 sem saída) é ambígua e não foi usada. O
catálogo publica `cost 0/0` tanto para modelos gratuitos quanto para modelos
sem preço publicado — a ressalva acompanha o registro.

Procedência local: `integrations/cost_registry.json` (dados),
`integrations/cost_governance.py` (motor), `integrations/opencode_cli.py`
(anual). Cada tarifa carrega `source` e `source_date`; registro sem
proveniência é rejeitado.

## Regras invioláveis

1. Tarifa desconhecida não é tarifa zero: `estimate_cost` devolve `usd=None`
   com `basis="tariff_unknown"`.
2. Preço de API não é preço de assinatura: superfícies `subscription` e
   `free_tier` devolvem `usd=None` com a base correta e ressalvas.
3. Nada aqui é cobrança observada: toda estimativa sai marcada como
   estimativa, com fonte e data.
4. Falha fechada: registro malformado levanta `CostRegistryError`; o
   orçamento bloqueia quando o custo não é verificável.
5. O modelo global não muda em silêncio; agente com `model` declarado no
   cartão permanece autoritativo; o primário não recebe fixação de modelo.

## Aceitação

1. RED em `tests/test_r917_cost_governance.py` antes da implementação; GREEN
   deve demonstrar: registro válido com as seis famílias de superfície;
   rejeição de registro malformado, sem `billable` ou sem procedência;
   gratuidade declarada (local, 0/0 publicado) e não-gratuito para modelo
   pago e para modelo desconhecido; estimativa conferida a mão
   (mimo-v2.6-flash Go: 1M de entrada com 80% em cache + 100k de saída =
   US$ 0,0582); `usd=None` para assinatura, free tier e tarifa desconhecida;
   ordenação por custo blended; classificação determinística de cartões reais
   (`coder`→media, `auditor`→critica, `academic_writer`→simples,
   `researcher`→complexa); cadeia sem repetição e terminando em modelo capaz;
   plano começando por superfície gratuita na complexidade trivial e não
   começando por gratuita na crítica; orçamento bloqueando acima do teto,
   permitindo local e bloqueando custo não verificável; ledger persistindo
   entre instâncias e sem registrar custo desconhecido como zero.
2. A configuração gerada expõe a tarifa declarada por provider (mesmo id,
   tarifas diferentes entre Go e Zen), os modelos free publicados com custo
   zero, cadeia de fallback em todos os agentes, o modelo global inalterado
   (`ollama-local/llama3.2`) e o modelo declarado de agente autoritativo
   preservado. Nenhum id de cadeia pode ficar pendurado fora do catálogo.
3. O comando `custos` responde com superfície, tarifa, cadeia e gasto
   estimado, e declara que a token economy mede grandeza diferente.
4. A NVIDIA permanece declarada e não habilitada: o bloco de provider é
   oferecido como sugestão para aplicação explícita, com a chave de
   ambiente exigida.
5. Verificação: testes R981 e regressão dos contratos de catálogo (R622,
   R500), regeneração do `opencode.json` e `doctor` sem regressão.

## Evidência de implementação

RED registrado: `ModuleNotFoundError: No module named 'integrations.cost_governance'`.
GREEN: 41/41 em `tests/test_r917_cost_governance.py`; 67/67 com R622 e R500.

Defeitos encontrados e corrigidos durante o ciclo, todos por contraprova:
(a) `literature_review` casava com a regra `review` e mandava o `researcher`
para a faixa crítica; (b) capabilities *derivadas* do loader dominavam os
campos declarados do cartão e jogavam o `coder` em crítica — corrigido com
classificação em duas passagens (declarado → derivado); (c) `bioinformatica`
casava com `format`; (d) ids de superfície divergiam do id de provider no
registro (`nvidia` vs `nvidia-nim`, `openai` vs `openai-api`, `google` vs
`gemini-api`).

Limites: nenhuma chamada de inferência foi executada; nenhuma cobrança foi
observada; o catálogo do provedor continua sendo lista, não entitlement; a
fixação de modelo por agente é reversível por
`policy.apply_head_model` no registro.
