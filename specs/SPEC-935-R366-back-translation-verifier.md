---
spec_id: SPEC-935-R366
title: BackTranslationVerifier — verificação determinística de retrotradução
component: translation/back_translation.py + agents/catalog/back-translation-verifier.md
status: verified
test_file: tests/test_r366_back_translation_verifier.py
---

# SPEC-935-R366 — BackTranslationVerifier

**Contrato funcional:** OCB-BACK-TRANSLATION-001
**Data:** 2026-08-02
**Posição no pipeline:** etapa 9 do pipeline do plano OpenCode Books Global
(retrotradução e verificação de consistência), até então interface externa
não implementada no R359.

## 1. Objetivo

Comparar o texto original com a retrotradução (tradução de volta ao idioma
fonte, produzida por humano ou por sistema externo) e apontar divergências
**observáveis por regra**: números e datas, entidades declaradas, polaridade
de negação, marcas pragmáticas, razão de comprimento e termos do grafo
terminológico ausentes no ciclo completo.

**Limite epistêmico:** o verificador não mede equivalência semântica.
Retrotradução limpa não prova tradução correta; divergência apontada é
indício para revisão humana, não veredito. O verificador **nunca aprova** —
apenas reporta ausência ou presença de indícios.

## 2. Entrada

`verify(payload)` com envelope obrigatório (fail-closed via `ContractError`):

- `schema_version` (= "1.0.0"), `review_id`, `segment_id`;
- `source_text` (original), `back_translated_text` (retrotradução no idioma
  fonte); `translated_text` (alvo intermediário, informativo, opcional);
- `source_language`, `pivot_language` (BCP-47);
- `declared_entities`: lista (pode ser vazia) de nomes próprios que devem
  sobreviver ao ciclo;
- `glossary_terms`: lista (pode ser vazia) de termos com
  `{source_term, preserve_portuguese}` — compatível com entradas do
  TerminologyGraph (R364);
- `provenance`: lista não vazia.

Textos vazios → `analysis_status="insufficient_context"`, sem achados.

## 3. Verificações determinísticas

| Verificação | Código (ISSUE_CODES do R359) | Severidade |
|---|---|---|
| Números/anos presentes no original e ausentes na retrotradução (e vice-versa) | `CULTURAL_LOSS` | high |
| Entidade declarada ausente da retrotradução | `CULTURAL_LOSS` | high |
| Contagem de negadores diverge além de ±1 (não/nunca/nada/ninguém/nem/jamais/sem) | `PRAGMATIC_FAILURE` | high |
| Marcas pragmáticas (?, !, reticências) divergem | `PRAGMATIC_FAILURE` | medium |
| Razão de comprimento fora de [0.5, 2.0] | `CULTURAL_LOSS` | medium |
| Termo com `preserve_portuguese` presente no original e ausente da retrotradução | `TERM_CONFLICT` | high |

Todo achado: `requires_human_review=True` e detalhe com os valores
observados. Achado high ⇒ `human_gate="required"`.

## 4. Saída

Envelope determinístico: `schema_version`, `review_id`, `segment_id`,
`analysis_status` (`complete` | `insufficient_context`), `findings[]`,
`human_gate`, `disclaimer` (limite epistêmico explícito, incluindo que
retrotradução limpa não prova equivalência).

## 5. Critérios de aceitação

1. Envelope inválido/incompleto → `ContractError`; textos vazios →
   `insufficient_context`.
2. Cada uma das seis verificações da §3 detectada em caso de teste dedicado.
3. Ciclo limpo → zero achados, `human_gate="recommended"` e disclaimer
   negando prova de equivalência.
4. Determinismo bit a bit.
5. Agent card A2A com `episteme: hermeneutico_interpretativo` carregável.
