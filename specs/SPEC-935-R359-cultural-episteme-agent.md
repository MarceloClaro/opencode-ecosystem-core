---
spec_id: SPEC-935-R359
title: CulturalEpistemeAgent
component: translation/cultural_episteme.py + agents/catalog/cultural-episteme-agent.md
status: verified
test_file: tests/test_r359_cultural_episteme_agent.py
---

# SPEC-935-R359 — CulturalEpistemeAgent

**Contrato funcional:** OCB-CULTURAL-EPISTEME-001
**Versão:** 1.0.0
**Estado:** verified
**Data:** 2026-08-01
**Orquestrador:** marceloclaro

## 1. Objetivo

Implementar o **CulturalEpistemeAgent** — Agente de Epistemes Culturais e
Equivalência Interpretativa — como gate pós-tradução capaz de mediar fidelidade
semântica, voz autoral, contexto histórico-cultural, função pragmática e
consistência simbólica.

O agente recomenda e justifica; não substitui tradutor, editor, autor,
especialista histórico nem revisor humano nativo.

**Limite epistêmico:** trata-se de instrumento heurístico de apoio editorial.
Ele identifica indícios e propõe alternativas condicionais; não determina
autenticidade, naturalidade, correção histórica, qualidade literária,
equivalência interpretativa ou prontidão para publicação. Ausência de alerta
significa apenas que nenhum indício foi encontrado nos dados, regras e escopo
examinados.

## 2. Posição contratual no pipeline

```text
Manuscrito-base
  → AuthorVoiceGuardian (interface externa; ainda não implementada)
  → TerminologyGraphAgent (interface de delta; ainda não implementada)
  → TranslationAgent (interface externa; ainda não implementada)
  → CulturalEpistemeAgent (objeto desta spec)
  → BackTranslationVerifier (interface externa; ainda não implementada)
  → Revisor humano nativo (gate obrigatório em alto risco)
  → CJKTypesettingAgent (interface externa; ainda não implementada)
  → Publicação
```

Não será alegada integração runtime com componentes ainda ausentes. O agente
expõe contratos explícitos para integração futura e produz deltas estruturados
para o grafo terminológico.

## 3. Entradas obrigatórias e versionadas

- `schema_version`
- `review_id`
- `segment_id`
- `source_language` (BCP-47)
- `source_text`
- `translated_text`
- `target_language` (BCP-47)
- `author_voice_profile`
- `terminology_graph`
- `historical_context`
- `cultural_dossier`
- `previous_translation_decisions`

Contextos históricos e culturais devem registrar proveniência, responsável,
data, limitações e grau de sustentação (`documented`, `contested`, `uncertain`,
`fictional` ou `authorial`). Entrada incompleta ou contraditória falha fechada.

## 4. Saída obrigatória

`cultural_episteme_review` deve conter:

- línguas de origem e destino;
- excertos fonte e traduzido;
- `analysis_status`: `complete`, `insufficient_context` ou
  `invalid_agent_output`;
- `candidate_concerns` com código, severidade, força da evidência, spans,
  detector (`rule`/`agent`), evidência e justificativa;
- contexto cultural/histórico/disciplinar;
- alternativas justificadas;
- alternativas candidatas e eventual preferência **condicionada**, nunca
  tradução “aprovada”;
- `heuristic_signals` e `process_checks`, sem semântica de probabilidade ou nota
  de qualidade;
- `evidence_sufficiency` e `uncertainty_reasons`;
- `terminology_graph_updates`;
- `human_review_required`;
- `release_gate: blocked`;
- limites e dados faltantes.

A saída nunca pode ser vazia. Dados insuficientes devem produzir
`analysis_status: insufficient_context`, lista explícita de lacunas e revisão
humana. O estado `approved`, `verified` ou `publication_ready` é inválido.

## 5. Taxonomia de alertas

- `LITERALISM`
- `CULTURAL_LOSS`
- `ANACHRONISM`
- `VOICE_SHIFT`
- `REGISTER_SHIFT`
- `SYMBOL_DRIFT`
- `TERM_CONFLICT`
- `PRAGMATIC_FAILURE`
- `CJK_UNNATURALNESS`
- `TARGET_VARIETY_USAGE_RISK` (código canônico; o anterior é alias legado)
- `OVERLOCALIZATION`
- `UNDERLOCALIZATION`
- `ETHICAL_RISK`
- `HISTORICAL_SOURCE_GAP`
- `HISTORICAL_CONTESTATION`
- `EXOTICIZATION_RISK`
- `DOMESTICATION_ERASURE_RISK`
- `RELAY_TRANSLATION_RISK`
- `REPRESENTATION_HARM_RISK`
- `UNCLASSIFIED_RISK`

Severidades: `low`, `medium`, `high`, `critical`.

## 6. Quality gates fail-closed

- omissões críticas: `0`;
- conflitos terminológicos não resolvidos: `0`;
- sinais heurísticos abaixo de consistência simbólica `0.98`, fidelidade
  cultural `0.90` ou similaridade de voz autoral `0.88` forçam revisão; sinais
  acima desses valores **não** aprovam nem desbloqueiam publicação;
- revisão humana obrigatória em qualquer alerta `high`/`critical`, em
  `ETHICAL_RISK`, `UNCLASSIFIED_RISK` e em decisão histórica sensível;
- toda tradução destinada à publicação exige revisão humana documentada;
- retrotradução serve apenas para levantar discrepâncias: nunca encerra alertas,
  aumenta status ou comprova fidelidade, nem isoladamente nem em conjunto com
  outros sinais.

Sinais são internos, não calibrados externamente e não constituem evidência de
mérito, probabilidade, competência cultural ou validação externa. Alertas
históricos, éticos ou representacionais nunca podem ser compensados por média.

## 7. Regras invioláveis

1. Não domesticar tudo; termos culturais podem permanecer em português com
   contextualização.
2. Não exotizar o sertão nem comunidades historicamente marginalizadas.
3. Não modernizar silenciosamente conceitos históricos.
4. Não apagar oralidade, idade, classe ou registro de personagem.
5. Não corrigir repetição, fragmentação ou ambiguidade literária intencional.
6. Não secularizar expressão religiosa sem justificativa autoral/documental.
7. Não aprovar automaticamente conteúdo de alto risco.
8. Toda alteração terminológica deve gerar delta auditável para o grafo.
9. Deltas nascem sempre como `proposed`, com versão-base, proveniência,
   idempotência e aprovação humana futura.
10. “Falante nativo” não é selo suficiente; revisão exige proficiência no par,
    variante, gênero e, quando aplicável, competência histórica/cultural.

## 8. Entregáveis

1. `agents/catalog/cultural-episteme-agent.md` com prompt, contrato de saída e
   permissões somente leitura.
2. `translation/cultural_episteme.py` com taxonomia, validação contratual,
   preflight determinístico, quality gate e adaptador de estágio com executor
   injetável.
3. `translation/__init__.py` exportando a API pública.
4. `tests/test_r359_cultural_episteme_agent.py`.
5. `opencode.json` regenerado pelo gerador canônico.
6. Integração documental no orquestrador literário sem alegar componentes
   ausentes.

## 9. Critérios de aceitação (SDD)

1. O agente existe no catálogo com slug `cultural-episteme-agent`, modo
   `subagent`, sem modelo explícito e com `edit`/`bash` negados.
2. O contrato rejeita saídas vazias, estados aprovativos, códigos desconhecidos
   não mapeados para `UNCLASSIFIED_RISK`, sinais não finitos/fora de `[0,1]` e
   campos obrigatórios ausentes.
3. Alto risco sem `human_review_required: true` reprova o gate.
4. O gate mantém `release_gate: blocked` até revisão humana documentada; sinais
   abaixo dos limiares aumentam o bloqueio, e sinais altos nunca o removem.
5. Preflight detecta, no mínimo:
   - `retirante → migrant` sem contextualização;
   - tradução proibida de `Curral do Governo`;
   - fala infantil artificialmente acadêmica;
   - modernização histórica indicada pelo dossiê;
   - metáfora transformada em afirmação;
   - chinês com espaçamento artificial entre ideogramas;
   - ameaça enfraquecida por modalização;
   - símbolo/termo divergente de decisão humana anterior.
6. Deltas do TerminologyGraph validam ID, grafo/revisão-base, idempotência,
   `source_term`, tipo, preferências, traduções proibidas, contexto, proveniência
   e `approval_state: proposed`.
7. `build_config()` e `opencode.json` contêm o novo agente com prompt por arquivo.
8. Testes R359 passam; configuração OpenCode é válida.
9. O adaptador com executor fake é declarado apenas como contrato testado, não
   como ponte runtime prompt→Python nem pipeline ponta a ponta.
10. Smoke runtime só pode ser declarado validado após reinício do OpenCode e
    resposta não vazia submetida ao validador Python independente.
11. Registro R359 no EvolutionRegistry e reflexão no MetaBus ao concluir.

## 10. Estratégia TDD

1. **RED:** escrever testes de contrato, preflight e integração antes dos arquivos
   de implementação.
2. **GREEN:** implementar apenas o necessário para satisfazer os casos.
3. **REFACTOR:** consolidar validação e tornar os deltas serializáveis sem alterar
   os resultados.

## 11. Verificação runtime pós-reinício

- Data: 2026-08-01.
- Slug executado: `cultural-episteme-agent`.
- Entrada: amostra controlada PT-BR→EN-US com voz infantil sertaneja.
- Resultado: saída JSON não vazia, sem estado aprovativo, com
  `human_review_required: true` e `release_gate: blocked`.
- Gate independente: contrato válido; preflight `LITERALISM`; decisão derivada
  `revise`.
- Evidência: `validacao_externa/cultural_episteme/r359_runtime_smoke.json`.
- Limite: o smoke comprova carregamento e aderência contratual no caso testado;
  não comprova competência cultural ampla, naturalidade nativa ou qualidade de
  tradução.
