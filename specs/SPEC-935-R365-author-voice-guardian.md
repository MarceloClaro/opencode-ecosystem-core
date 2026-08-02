---
spec_id: SPEC-935-R365
title: AuthorVoiceGuardian — guarda de voz autoral em tradução
component: translation/author_voice.py + agents/catalog/author-voice-guardian.md
status: draft
test_file: tests/test_r365_author_voice_guardian.py
---

# SPEC-935-R365 — AuthorVoiceGuardian

**Contrato funcional:** OCB-AUTHOR-VOICE-001
**Data:** 2026-08-02
**Posição no pipeline:** entre o texto-base congelado e a análise do
CulturalEpistemeAgent (§5 do plano OpenCode Books Global); consome o
`author_voice_profile` já presente no contrato do R359 e o estende para um
perfil de voz versionado e auditável.

## 1. Objetivo

Detectar, por regras observáveis, indícios de perda de voz autoral em
traduções: apagamento de marcadores regionais/orais, modernismos proibidos e
mudança de registro pragmático (interrogação/exclamação/reticências).

**Limite epistêmico:** instrumento heurístico. Não mede "fidelidade de voz";
aponta indícios com severidade e exige revisão humana para tudo que for alto
risco. Ausência de achado significa apenas que nenhum indício foi observado
pelas regras no escopo examinado.

## 2. Perfil de voz (contrato)

`validate_voice_profile(payload)` — campos obrigatórios, fail-closed:

- `schema_version` (= "1.0.0"), `profile_id`, `work_id`;
- `register`: descrição textual não vazia;
- `voice_markers`: lista não vazia de marcadores, cada um com `marker`
  (termo/expressão fonte), `kind` (`regionalism` | `orality` | `symbol` |
  `institution`), `strategy` (`preserve` | `gloss` | `adapt`) e, quando
  `strategy=adapt`, `approved_renderings` não vazio por idioma-alvo
  (`en`, `zh_cn`);
- `forbidden_modernisms`: lista (pode ser vazia) de termos proibidos no alvo;
- `provenance`: lista não vazia (mesma forma do R359).

## 3. Revisão de segmentos

`review_segment(profile, source_text, translated_text, target_language)`:

1. Marcador presente no fonte:
   - `strategy=preserve` e marcador ausente do alvo → `VOICE_SHIFT` (high);
   - `strategy=adapt` e nenhum `approved_renderings[lang]` presente no alvo →
     `VOICE_SHIFT` (high);
   - `strategy=gloss` e marcador ausente do alvo → `VOICE_SHIFT` (medium,
     "glosa esperada");
2. `forbidden_modernisms` presente no alvo → `ANACHRONISM` (high);
3. Deriva pragmática: contagem de `?`, `!` e `...`/`……` difere entre fonte e
   alvo → `REGISTER_SHIFT` (medium) com os números observados no detalhe;
4. Códigos exclusivamente de `cultural_episteme.ISSUE_CODES`; todo achado
   carrega `requires_human_review=True`; achados `high` ⇒
   `human_gate="required"` no envelope de saída.
5. Entrada inválida → `ContractError` (fail-closed); textos vazios →
   `analysis_status="insufficient_context"`, sem achados fabricados.

## 4. Saída

Envelope com `schema_version`, `profile_id`, `analysis_status`
(`complete` | `insufficient_context`), `findings[]`, `human_gate`
(`required` | `recommended`) e `disclaimer` fixo de limite epistêmico.

## 5. Critérios de aceitação

1. Perfil válido aceito; faltas/valores inválidos → `ContractError`
   (incluindo `adapt` sem `approved_renderings`).
2. Os cinco padrões de achado da §3 detectados nos casos de teste.
3. Segmento com marcadores respeitados → zero achados e
   `human_gate="recommended"`.
4. Textos vazios → `insufficient_context` sem achados.
5. Determinismo (mesma entrada, mesma saída).
6. Agent card A2A com `episteme: hermeneutico_interpretativo` carregável
   pelo catálogo.
