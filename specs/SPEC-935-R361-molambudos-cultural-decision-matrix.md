---
spec_id: SPEC-935-R361
title: Matriz editorial cultural e correções mecânicas de Molambudos
component: validacao_externa/cultural_episteme/molambudos_r361_* + fragmentos EN/ZH selecionados
status: green
test_file: tests/test_r361_molambudos_cultural_decision_matrix.py
external_validation: false
human_review_required: true
release_gate: blocked
quality_verdict_allowed: false
---

# SPEC-935-R361 — Matriz editorial cultural de Molambudos

**Estado:** green interno — release bloqueado
**Data:** 2026-08-01
**Base:** SPEC-935-R355, R356, R358, R359 e R360

## 1. Objetivo

Transformar os alertas heurísticos R360 em uma matriz de decisão humana com
fontes externas rastreáveis e aplicar somente correções mecânicas que não
decidam equivalência cultural, nome histórico, símbolo ou neologismo.

Pesquisa externa informa opções; ela não constitui validação cultural, parecer
nativo, consenso histórico ou autorização de publicação.

## 2. Termos de decisão humana

1. `Curral do Governo` — categoria histórica + metáfora animalizante.
2. `retirante(s)` — categoria regional/histórica de deslocamento pela seca.
3. `Rasga Mortalha` — nome popular, ave agourenta e símbolo recorrente.
4. `molambudo(s)` — raiz lexical, insulto, neologismo e título.
5. `Hospital Colônia / Colônia` — nome próprio institucional e forma curta.

Para cada termo e idioma-alvo, a matriz deve apresentar: forma atual, no mínimo
duas opções, ganhos, perdas, riscos, evidência, preferência condicionada e
pergunta binária ou enumerada ao autor/editor.

## 3. Pesquisa e proveniência

- Priorizar fontes primárias, institucionais, acadêmicas e obras publicadas.
- Registrar URL, título, instituição/autoria, data quando disponível, data de
  acesso, claim sustentado, limitações, grupo independente e escopo da
  evidência (`source_fact`, `target_usage`, `target_equivalence` ou `metadata`).
- Não usar snippets de busca como evidência final.
- Não inventar DOI, tradução oficial, nome institucional ou consenso.
- Wikipedia e agregadores podem orientar busca, mas não bastam como única fonte
  para uma decisão histórica ou folclórica.
- Fonte inacessível, contraditória ou secundária deve ser marcada como tal.
- Versões linguísticas da mesma publicação e verbetes do mesmo dicionário
  compartilham grupo independente e não contam como corroboração autônoma.
- Uso publicado em língua-alvo é `target_usage`, não prova de equivalência.
- Ausência de fonte ZH-CN ou revisão nativa deve ser declarada, não inferida.

### 3.1 Gate de contradição factual descoberta

Se a pesquisa revelar conflito entre o corpus e fontes qualificadas, a rodada
deve registrar um `historical_blocker` com locais afetados e opções autorais,
sem corrigir silenciosamente cronologia, geografia ou estatuto institucional.

Bloqueios já confirmados para formalização no dossiê:

1. `patu_1915_chronology`: Alagadiço/Fortaleza é associado a 1915; Patu em
   Senador Pompeu, a 1932--1933.
2. `hospital_closed_1980`: a FHEMIG registra reestruturação nos anos 1980 e
   continuidade institucional como CHPB, não fechamento simples em 1980.
3. `rasga_mortalha_beak_etiology`: fontes lidas sustentam nome, som e agouro,
   mas não confirmam como tradição documentada o bico rasgando a mortalha para
   libertar a alma; a passagem pode permanecer como crença de personagem ou
   variante ficcional, desde que não seja apresentada como fato externo.
4. `molambudo_absolute_neologism`: dicionários atestam `molambudo`; a inovação
   da obra está no uso recorrente como insulto, categoria e título, não na
   criação absoluta do vocábulo. Primeira atestação e uso histórico em 1915
   continuam abertos.
5. `victim_count_category_drift`: o corpus alterna mortos, internados, corpos
   enterrados, exumados, vendidos e desaparecidos; 1.853 é sustentado pela
   fonte lida como corpos negociados com faculdades, não como exumações.
6. `pseudoarchive_authenticity`: documentos ficcionais usam nomes de arquivos
   e instituições reais e precisam de marcação inequívoca de ficcionalidade,
   proveniência e permissões.
7. `fictional_victim_insertion`: Joaquim é declarado ficcional, mas também é
   incorporado ao conjunto memorial de vítimas reais; isso exige arbitragem
   ética e não pode ser tratado como corroboração testemunhal.
8. `living_memory_erasure`: Patu e CHPB são descritos como esquecidos,
   desaparecidos ou integralmente abandonados, em tensão com ruínas tombadas,
   romarias, museu, reforma e continuidade institucional.
9. `psychiatric_stigma_horror`: a combinação paciente–violência–possessão–
   contágio pode reforçar estigma e instrumentalizar trauma psiquiátrico.
10. `reader_consent_visual_provenance`: avisos, imagens pseudoarquivísticas,
    direitos e conteúdos de violência extrema exigem auditoria específica.

## 4. Correções mecânicas permitidas

Somente estas classes podem alterar o manuscrito nesta rodada:

1. EN: restaurar metros onde a fonte PT diz metros e o alvo manteve os mesmos
   números com `yards` (`MEM-06` e duplicatas editoriais exatas, se houver).
2. EN: corrigir `walked days` para `walked for days` no par de DOC-17 e
   duplicatas editoriais exatas, se houver.
3. ZH: restaurar a farpa de `arame farpado` como `带刺铁丝网` onde o alvo possui
   apenas `铁丝网` no mesmo segmento (`MEM-06` e duplicatas exatas).

Essas correções não autorizam modificar `Government Pen`, `政府牲畜圈`,
`retirantes`, `逃荒者`, `Shroud-Ripper`, `裹尸布撕裂者`, `molambudos`,
`莫兰布多斯`, `破衣人`, `Hospital-Colony`, `the Colony`, `收容院` ou
`科洛尼亚` nesta rodada.

## 5. Entregáveis

1. `validacao_externa/cultural_episteme/molambudos_r361_decision_matrix.json`.
2. `validacao_externa/cultural_episteme/molambudos_r361_decision_matrix.md`.
3. `validacao_externa/cultural_episteme/molambudos_r361_sources.json`.
4. `validacao_externa/cultural_episteme/molambudos_r361_provenance_drift.json`,
   preservando os hashes R360 e registrando os novos hashes sem reescrever o
   snapshot anterior.
5. Correções mecânicas do §4, com mapa exato de arquivos e antes/depois.
6. Testes R361 e evidências de builds/rotas.

## 6. Critérios de aceitação

1. Exatamente cinco conceitos e dez decisões alvo (EN-US/ZH-CN).
2. Cada conceito possui ao menos dois registros substantivos de dois grupos
   independentes; decisões históricas ou folclóricas possuem ao menos uma
   fonte institucional/acadêmica/primária. Isso não basta para equivalência.
3. Cada fonte possui proveniência e limitação; URLs são HTTP(S) e foram lidas,
   não apenas encontradas por snippet.
4. Cada decisão apresenta ao menos duas opções; opções são hipóteses
   tradutórias, enquanto ganhos, perdas e riscos são inferências editoriais.
5. Preferências são `conditional`; decisões permanecem `pending_human`.
6. O dossiê contém anti-overclaim explícito e separa fato documentado,
   inferência editorial e hipótese tradutória.
7. Os dez bloqueios do §3.1 aparecem com categoria epistemológica, fontes ou
   base interna, ocorrências afetadas,
   opções autorais e `status: blocked_author_decision`; nenhuma cronologia,
   geografia ou história institucional é alterada.
8. Apenas as três classes mecânicas do §4 são modificadas; termos de alto risco
   mantêm hash/forma anterior na rodada.
9. A deriva de exatamente três arquivos R360 é explicitamente encadeada a R361;
   hashes antigos permanecem no artefato R360, hashes novos são conferidos e os
   cinco pareceres afetados são marcados como snapshot ou rechecados.
10. Testes verificam correções, matriz, fontes, bloqueios e ausência de edições
   culturais automáticas.
11. Normalizador de aspas continua idempotente; rotas permanecem 540/540.
12. Builds PT, EN, ZH, TRI e KDP TRI concluem sem erro fatal, referências
    indefinidas ou caracteres ausentes.
13. Regressão R358--R361 passa.
14. `release_gate: blocked`, `human_review_required: true`,
    `external_validation: false` e `quality_verdict_allowed: false` constam em
    todos os artefatos; nenhum gate interno comunica validação externa.

## 7. TDD

1. **RED:** testes da matriz e das três correções antes de editar corpus/artefatos.
2. **GREEN:** pesquisa, alterações permitidas e artefatos mínimos válidos.
3. **REFACTOR:** deduplicar fontes/opções sem apagar divergências.

## 8. Não escopo

- decidir sozinho qualquer um dos cinco termos;
- aplicar deltas R360 ao glossário;
- reescrever voz, registro, ameaça ou símbolo;
- declarar tradução culturalmente validada;
- substituir revisão humana EN-US/ZH-CN e competência histórica/folclórica.
