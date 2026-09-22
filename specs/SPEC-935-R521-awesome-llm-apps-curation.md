---
spec_id: SPEC-935-R521
title: Curadoria da paisagem de agentes — awesome-llm-apps (extensão multi-coleção do landscape-curator)
component: landscape (manifest_awesome_llm_apps + curator), agents/catalog/landscape-curator, THIRD_PARTY_NOTICES
test_file: tests/test_r521_awesome_llm_apps_curation.py
status: green
estoque: rc
data: 2026-09-17
---

# SPEC-935-R521 — Curadoria da paisagem de agentes: awesome-llm-apps

## Objetivo
Estender o `landscape-curator` (R482) para **múltiplas coleções externas** e
registrar o repositório `MarceloClaro/awesome-llm-apps` (fork Apache-2.0 do
upstream `Shubhamsaboo/awesome-llm-apps` — 1.240 commits, 100+ templates de
agentes/skills/RAG) como **referência de paisagem auditável**, com manifest
curado de **15 templates representativos** das categorias de maior afinidade
com o Core (agent skills, RAG, multi-agente/trust, MCP, otimização de tokens,
always-on, meta-loop).

## Não-objetivos
- Não importar código-fonte, requirements, env-examples ou prompts dos templates.
- Não prometer "100+ integrados": o README externo cita dezenas de templates;
  o manifest curado cobre 15 entradas de maior valor — nada além disso é
  tratado como integração (contexto de paisagem, como na R482).
- Não adotar rótulos não validados do upstream: o README menciona modelos sem
  verificação externa ("Claude Fable 5.1", "GPT-6 Astra", "Gemini 3.8 Flash");
  essas entradas ficam com veredito **não-adotar/observar** e nota explícita
  de anti-overclaim (gate R142).
- Não alterar roteamento default do Core nem o comportamento da R482
  (compatibilidade regressiva obrigatória).
- Não alegar validação externa de qualidade dos templates.

## Critérios de aceitação
- CA1: `LandscapeCurator` continua funcional com o manifest default da R482
  (20 agentes, MIT) — nenhum teste R482 quebra (regressão).
- CA2: novo manifest `landscape/manifest_awesome_llm_apps.json` carrega com
  **15 entradas**; cada uma tem `id`, `title`, `category`, `industry`,
  `framework`, `license="Apache-2.0"`, `reference_url` (github.com/MarceloClaro/awesome-llm-apps/tree/main/...), `keywords` e `note`.
- CA3: keywords por entrada (fallback para `CASE_KEYWORDS` da R482 quando
  ausentes) permitem cruzamento lexical auditável com o catálogo do Core;
  casos sem afinidade real entram em `unmatched` — nunca inventados.
- CA4: relatório JSON + Markdown parametrizado pela coleção (título e contagem
  por coleção), com disclaimer "não constitui certificação externa".
- CA5: anti-overclaim — `scope_note` declara 15/100+; termos proibidos
  (`superhuman`, `verificado`, `qualis a1`, `superação`) ausentes do relatório;
  a entrada meta-loop (adversarial) registra nota de modelos não validados.
- CA6: hermetismo — sem código externo copiado (sem "import openai", sem "def "
  de funções externas, sem env/credenciais); testes sem rede.
- CA7: THIRD_PARTY_NOTICES registra a coleção (Apache-2.0); agent card
  `landscape-curator` atualizado para multi-coleção; opencode.json regenerado;
  ciclo R521 registrado no EvolutionRegistry; suíte completa verde.

## Fonte
https://github.com/MarceloClaro/awesome-llm-apps (fork Apache-2.0 do
Shubhamsaboo/awesome-llm-apps; upstream www.theunwindai.com). Referência
curada em 2026-09-17. Lições aplicadas: R472 (auditar licença antes de
integrar — Apache-2.0 compatível), R474 (comunidade fornece padrões, não
código embutível; veredito explícito por item).