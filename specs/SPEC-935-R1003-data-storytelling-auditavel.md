---
spec_id: SPEC-935-R1003
title: Data storytelling auditável com legenda, fonte e nota
component: skills.data_storytelling
status: implemented
test_file: tests/test_r1003_data_storytelling.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    perfil:
      - "tests/test_r1003_data_storytelling.py::test_profile_infers_field_kinds"
      - "tests/test_r1003_data_storytelling.py::test_profile_counts_missing_and_ragged_rows"
      - "tests/test_r1003_data_storytelling.py::test_profile_hash_is_deterministic_and_sensitive"
      - "tests/test_r1003_data_storytelling.py::test_profile_mixed_field_is_explicit"
      - "tests/test_r1003_data_storytelling.py::test_profile_fails_closed[bad0-empty_dataset]"
      - "tests/test_r1003_data_storytelling.py::test_profile_fails_closed[bad1-invalid_row]"
      - "tests/test_r1003_data_storytelling.py::test_profile_fails_closed[bad2-row_limit_exceeded]"
      - "tests/test_r1003_data_storytelling.py::test_profile_treats_non_finite_as_missing"
    recomendacao:
      - "tests/test_r1003_data_storytelling.py::test_recommend_trend_prefers_line"
      - "tests/test_r1003_data_storytelling.py::test_recommend_ranking_prefers_sorted_horizontal_bar"
      - "tests/test_r1003_data_storytelling.py::test_recommend_composition_rejects_crowded_pie"
      - "tests/test_r1003_data_storytelling.py::test_recommend_composition_keeps_small_pie"
      - "tests/test_r1003_data_storytelling.py::test_recommend_relationship_prefers_scatter"
      - "tests/test_r1003_data_storytelling.py::test_recommend_without_compatible_field_fails_closed"
    gate:
      - "tests/test_r1003_data_storytelling.py::test_clean_spec_is_approved"
      - "tests/test_r1003_data_storytelling.py::test_truncated_bar_axis_is_blocked"
      - "tests/test_r1003_data_storytelling.py::test_undeclared_baseline_requires_revision"
      - "tests/test_r1003_data_storytelling.py::test_dual_axis_and_three_d_are_blocked"
      - "tests/test_r1003_data_storytelling.py::test_pie_overload_and_contract"
      - "tests/test_r1003_data_storytelling.py::test_causal_claim_is_blocked_only_in_observational_design"
      - "tests/test_r1003_data_storytelling.py::test_missing_source_note_sample_and_units"
      - "tests/test_r1003_data_storytelling.py::test_uncertainty_and_overplotting_are_flagged"
      - "tests/test_r1003_data_storytelling.py::test_color_and_title_contracts"
      - "tests/test_r1003_data_storytelling.py::test_unknown_chart_fails_closed"
      - "tests/test_r1003_data_storytelling.py::test_audit_is_deterministic_and_does_not_mutate_the_spec"
    narrativa:
      - "tests/test_r1003_data_storytelling.py::test_narrative_causal_and_absolute_claims"
      - "tests/test_r1003_data_storytelling.py::test_narrative_percent_hype_and_limit"
    legenda:
      - "tests/test_r1003_data_storytelling.py::test_caption_builds_four_layers"
      - "tests/test_r1003_data_storytelling.py::test_caption_without_legend_omits_the_layer"
      - "tests/test_r1003_data_storytelling.py::test_caption_validation_rejects_placeholders_and_untraceable_source"
      - "tests/test_r1003_data_storytelling.py::test_caption_without_number_fails_validation"
      - "tests/test_r1003_data_storytelling.py::test_caption_formats_elaboration_prefix"
      - "tests/test_r1003_data_storytelling.py::test_caption_includes_unit_when_legend_is_absent"
      - "tests/test_r1003_data_storytelling.py::test_caption_warns_when_note_lacks_method"
      - "tests/test_r1003_data_storytelling.py::test_caption_escapes_html"
      - "tests/test_r1003_data_storytelling.py::test_caption_rejects_invalid_number_and_long_title"
      - "tests/test_r1003_data_storytelling.py::test_caption_from_spec_pulls_chart_contract"
    render:
      - "tests/test_r1003_data_storytelling.py::test_svg_is_valid_deterministic_and_accessible"
      - "tests/test_r1003_data_storytelling.py::test_svg_refuses_truncated_bar_and_unsupported_chart"
      - "tests/test_r1003_data_storytelling.py::test_svg_line_renders_points"
      - "tests/test_r1003_data_storytelling.py::test_number_format_ptbr"
    manifesto:
      - "tests/test_r1003_data_storytelling.py::test_manifest_is_deterministic_and_detects_tampering"
      - "tests/test_r1003_data_storytelling.py::test_manifest_normalizes_non_string_names"
    cli:
      - "tests/test_r1003_data_storytelling.py::test_cli_demo_generates_verifiable_dossier"
---

# SPEC-935-R1003 — Data Storytelling Auditável (legenda, fonte e nota)

**Status:** Implementado (RED → GREEN; gate SDD em verificação)
**Versão:** 1.0.0
**Data:** 2026-11-01
**Agente:** marceloclaro (Orquestrador Central Metacognitivo)
**Testes de aceitação:** `tests/test_r1003_data_storytelling.py`
**Módulo:** `skills/data_storytelling/`
**Skill:** `.opencode/skills/data-storytelling-auditavel/SKILL.md`

## 1. Objetivo

Entregar uma skill e um motor determinístico para transformar dados em uma
narrativa visual **auditável**, com quatro camadas obrigatórias de legenda:

1. **Rótulo** — `Figura 1 –` / `Gráfico 1 –` / `Tabela 1 –`.
2. **Título-mensagem** — o que o leitor deve concluir, não o tipo de gráfico.
3. **Chave visual** — codificação, unidades, rótulos diretos e leitura de cores.
4. **Fonte + Nota** — proveniência rastreável e método (n, período, filtros,
   definições, missing, limitações).

O motor não desenha "bonito": ele **reprova** decisões que induzem erro de
leitura e **sela** cada entrega com SHA-256.

## 2. Contrato de saída (dossiê)

| Artefato | Conteúdo | Obrigatório |
|---|---|---|
| `dossie.json` | storyline + perfil + recomendação + auditoria + legenda | sim |
| `grafico.svg` | figura determinística com `<title>`/`<desc>` e rótulos diretos | quando `render_svg` suportar o gráfico |
| `legenda.md` | legenda completa (4 camadas) | sim |
| `auditoria.json` | achados com código, severidade, evidência e remédio | sim |
| `MANIFESTO.json` | hashes de todos os artefatos + `manifest_sha256` | sim |

`SCHEMA_VERSION = "r1003.v1"`.

## 3. Perfil de dados (`profile_dataset`)

- Entrada: sequência de mapeamentos (linhas). Teto `max_rows=50_000`.
- Infere `numeric`, `temporal`, `categorical`, `identifier`, `text`, `mixed`.
- Trata como ausente: `None`, string vazia/só espaços, `float('nan')`.
  **Não** trata `"NA"` como ausente (ambíguo) — decisão documentada.
- Reporta `n_rows`, `fields[]`, `missing`, `ragged_rows`, `source_sha256`.
- Falha fechada: vazio, linha não-mapeamento, acima do teto.
- Limite: descreve apenas os bytes fornecidos; não valida veracidade,
  representatividade nem causalidade.

## 4. Recomendação de codificação (`recommend_chart`)

Intenções: `trend`, `comparison`, `ranking`, `composition`, `distribution`,
`relationship`, `deviation`.

Regras mínimas:

| Intenção | 1ª escolha | Rejeições explícitas |
|---|---|---|
| `trend` | `line` (temporal + numérico) | pizza |
| `comparison` | `bar` | pizza > 4 categorias |
| `ranking` | `bar` horizontal ordenada | pizza |
| `composition` | `stacked_bar` (5+ categorias) | pizza > 4 categorias |
| `distribution` | `histogram` (n ≥ 30) / `dot` (n < 30) | pizza |
| `relationship` | `scatter` (2 numéricos) | pizza |
| `deviation` | `diverging_bar` | pizza |

Sem campo compatível → `DataStoryError("no_compatible_chart")` (fail-closed).

## 5. Gate de auditoria (`audit_chart`)

Cada achado: `{code, severity, message, evidence, remedy}`.
Severidades: `critical`, `high`, `medium`, `low`.

Status: `blocked` (crítico), `revise` (alto), `pass_with_notes`
(médio/baixo), `approved` (nenhum).

| Código | Severidade | Condição |
|---|---|---|
| `MISSING_TITLE` | critical | título vazio |
| `TRUNCATED_AXIS` | critical | barra/área/coluna com base ≠ 0 |
| `UNDECLARED_BASELINE` | high | família de barras sem `y.zero` declarado |
| `DUAL_AXIS` | critical | dois eixos Y |
| `THREE_D` | critical | perspectiva 3D |
| `PIE_OVERLOAD` | critical/high | pizza > 5 / = 5 fatias |
| `PIE_NOT_PART_TO_WHOLE` | high | pizza sem `part_to_whole=true` |
| `OVERPLOTTING` | high | dispersão n > 500 sem controle |
| `MISSING_UNCERTAINTY` | high | estimativa sem incerteza exibida |
| `MISSING_SAMPLE_SIZE` | high | `sample_n` ausente/inválido |
| `MISSING_SOURCE` | critical | fonte vazia |
| `SOURCE_NOT_TRACEABLE` | high | fonte sem ano, DOI ou URL |
| `MISSING_NOTE` | high | nota vazia |
| `NOTE_TOO_THIN` | high | nota < 40 caracteres ou sem número |
| `CAUSAL_CLAIM_OBSERVATIONAL` | critical | verbo causal em desenho não causal |
| `UNQUANTIFIED_SUPERLATIVE` | high | hipérbole sem número |
| `ABSOLUTE_CLAIM` | high | absoluto sem escopo declarado |
| `COLOR_ONLY_ENCODING` | high | cor como único canal |
| `COLORBLIND_RISK` | high/medium | paleta não segura / par vermelho-verde |
| `TITLE_NOT_MESSAGE` | medium | título é nome de gráfico ou curto demais |
| `NO_ALT_TEXT` | medium | ausência de texto alternativo |
| `MISSING_UNITS` | high | eixo numérico sem unidade e sem `dimensionless` |
| `INCONSISTENT_PRECISION` | low | > 2 casas sem justificativa |
| `LOG_SCALE_UNDECLARED` | high | escala log sem declaração |
| `MISSING_MISSING_POLICY` | medium | dados ausentes sem política |
| `UNSORTED_RANKING` | medium | ranking não ordenado |
| `NO_LEGEND` | medium | cor/tamanho sem legenda e sem rótulo direto |
| `CROWDED_SERIES` | medium | linha com > 5 séries |
| `CROWDED_CATEGORIES` | medium | barras com > 12 categorias |
| `UNLABELED_AXIS_BREAK` | high | quebra de eixo não sinalizada |

`score = max(0, 100 − 25·critical − 10·high − 3·medium − 1·low)` é
**heurístico de prontidão**, não medida de qualidade científica.

## 6. Auditoria de narrativa (`audit_narrative`)

- `CAUSAL_CLAIM_OBSERVATIONAL` (critical) — léxico causal sem desenho causal.
- `ABSOLUTE_CLAIM` (high) — "sempre", "nunca", "todos", "prova", "garante",
  salvo `scope_declared=True`.
- `PERCENT_WITHOUT_BASE` (high) — `%` sem denominador declarado.
- `HYPE_WITHOUT_NUMBER` (high) — hipérbole sem âncora numérica.
- `NO_STATED_LIMIT` (medium) — narrativa sem limite/abstenção.

## 7. Legenda e nota (`build_caption` / `validate_caption`)

- Título sem ponto final, ≤ 140 caracteres, espaço normalizado.
- Fonte rastreável: ano de 4 dígitos, DOI ou URL.
- Nota com número (n, período ou medida) e método.
- Placeholders (`TODO`, `TBD`, `XXX`, `lorem`, `preencher`) = erro.
- HTML escapado; Markdown com rótulo em negrito.
- `sha256` do texto plano para custódia.

## 8. Render determinístico (`render_svg`)

- Primitivas suportadas: `bar` (vertical/horizontal) e `line`.
- Barra exige base zero; recusa `y.zero=false`.
- `<title>`, `<desc>`, rótulos diretos, eixo com ticks determinísticos.
- Texto XML escapado; `metadata` com `spec_sha256`.
- Mesma entrada → mesma saída (sem relógio, sem aleatoriedade).

## 9. Manifesto (`build_manifest` / `verify_manifest`)

- Ordena artefatos por nome; aceita `str` (UTF-8) ou `bytes`.
- `manifest_sha256` sobre o JSON canônico sem o próprio campo.
- `verify_manifest` detecta ausência e adulteração por hash.

## 10. Critérios de Aceitação Executáveis

- `perfil` — tipos, ausentes, hash determinístico e falha fechada em entrada inválida.
- `recomendacao` — tendência, ranking, composição, relação e abstenção sem campo compatível.
- `gate` — bloqueio de eixo truncado, duplo eixo, 3D, pizza, causalidade e fonte ausente; aprovação limpa.
- `narrativa` — causalidade, absolutos, percentual sem base, hipérbole e limite declarado.
- `legenda` — quatro camadas, placeholders, fonte rastreável, número e escape HTML.
- `render` — SVG válido, determinístico, acessível, base zero e formatação pt-BR.
- `manifesto` — determinismo, presença e detecção de adulteração.
- `cli` — dossiê sintético completo com manifesto verificável.

### 10.1 Verificação executada (2026-11-01)

- **RED controlado:** stub sem comportamento; toda a suíte é coletada, falha
  por asserção em cada chamada e mantém 0 erros. Recibo arquivado em
  `.mci_state/tdd-history/`.
- **GREEN:** toda a suíte aprovada; recibo no mesmo diretório.
- **SpecVerifier:** 8/8 critérios, `runtime_evidence_valid=true`,
  `evidence_contract_valid=true`, status `green`. Recibos e hashes constam em
  `VALIDATION_R1003.md`.
- **Motivo do RED controlado:** o primeiro RED real foi `ImportError`, com
  coleta vazia; o `TDDHistory` exige os mesmos 42 nodeids nas duas fases.
  O stub preserva a coleta e falha por asserção, sem simular aprovação.
- **Escopo:** gate local de software. Não é validação externa, revisão por
  pares ou atestado científico.

## 11. Critérios de aceitação narrativos

- **AC1** Perfil infere tipos, missing, hash e falha fechada em entrada inválida.
- **AC2** Recomendação distingue tendência, composição, ranking, relação e
  distribuição; rejeita pizza sobrecarregada.
- **AC3** Auditoria bloqueia eixo truncado, duplo eixo, 3D, pizza > 5,
  causalidade observational, fonte ausente e título ausente.
- **AC4** Auditoria aprova especificação limpa sem falsos positivos.
- **AC5** Legenda contém rótulo, título, chave, fonte e nota com n/período.
- **AC6** Validação rejeita placeholder, fonte não rastreável e nota sem número.
- **AC7** SVG é XML válido, determinístico, acessível e recusa base ≠ 0.
- **AC8** Manifesto detecta adulteração.
- **AC9** CLI `demo` gera dossiê completo e manifesto verificável.
- **AC10** Nenhuma operação usa rede, LLM ou relógio.

## 12. Não-objetivos

- Não declara qualidade estética, aceite editorial, Qualis ou revisão por pares.
- Não valida a veracidade dos dados de entrada.
- Não implementa mapas, redes, treemaps ou animações.
- Não substitui revisão humana, estatística ou desenho causal.

## 13. Anti-overclaim

Toda saída carrega `limits[]`. O status `approved` significa apenas que a
especificação passou nas regras declaradas nesta versão — jamais que a
conclusão narrativa é verdadeira.
