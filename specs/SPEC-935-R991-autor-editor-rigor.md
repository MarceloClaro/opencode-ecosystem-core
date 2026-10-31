---
spec_id: SPEC-935-R991
title: Autor e Editor de alto rigor com estrutura, estilo anti-plágio e raciocínio
component: academic.author_editor
status: green
test_file: tests/test_r991_author_editor.py
---

# R991 — Autor/Editor de alto rigor acadêmico-científico

## Objetivo

Criar uma camada de autoria e edição que formaliza a produção de manuscritos
científicos a partir de padrões de estrutura (IMRaD expandido), estilo de escrita
academicamente aceito e raciocínio científico (axiomas, teoremas, lemas, leis,
tradições aristotélica/cartesiana/peirceana/popperiana e teoria dos jogos).

Não é um gerador que "imita Qualis A1" nem um copiador de trechos. É um contrato
de autoria assistida: estrutura, plano de raciocínio e perfil de estilo, sempre
explicitando que a redação final e o aceite editorial dependem de revisão humana.

## Fatos de contexto (não promessas)

- `https://innovationmap.at` é um gráfico interativo (Envisioning "Innovation Map"),
  não um repositório de artigos. Não há corpus de papers a baixar nessa URL. Os
  temas exibidos ali podem servir de semente de busca nas fontes OA autorizadas
  (OpenAlex/Crossref/arXiv/EuropePMC) via `research/searchers.py`.
- O Core já possui MASWOS (16 estágios), banca rigorosa, rubrica AUTO_SCORE e
  12+ motores de raciocínio (`reasoning/`), além de lógicas dedutiva/indutiva/
  abdutiva e teoria dos jogos em `research/simulated_reviews_v2.py`.
- Esta camada não substitui esses componentes; registra e reusa.

## Critérios de aceitação

1. `MANUSCRIPT_SECTIONS` define a estrutura IMRaD expandida em ordem canônica:
   título, resumo, introdução, objetivos, fundamentação teórica, metodologia,
   resultados, discussão, conclusão e referências. Cada seção declara função e
   movimentos argumentativos esperados.
2. `extract_structure(text)` identifica seções por cabeçalho PT/EN, informa as
   presentes, as ausentes e a ordem observada; texto sem cabeçalhos não inventa
   seções. Nunca devolve trechos verbatim como saída de estrutura.
3. `style_fingerprint(text)` extrai somente características estruturais e
   lexicais de estilo (registro, pessoa, hedging, conectivos, densidade de
   citações, movimentos de parágrafo, razão tipo-token aproximada). É proibido
   devolver spans verbatim: o perfil é anti-plágio por construção.
4. `reasoning_registry()` expõe frameworks nomeados com axiomas/leis/teoremas/
   lemas e o motor mapeado do Core. Inclui aristotélico (silogismo), cartesiano
   (dúvida metódica), axiomático (axioma/teorema/lema/corolário), peirceano
   (dedução/indução/abdução), popperiano (falsificabilidade), teoria dos jogos
   (minimax/Nash/Pareto), bayesiano, causal, dialético e difuso. Cada entrada
   declara `scope` e nunca afirma que o raciocínio "prova" a verdade empírica.
5. `author_brief(topic, sources)` devolve um plano estruturado (não um manuscrito
   pronto): esboço de seções, plano de raciocínio aplicável, plano de estilo e
   contrato anti-plágio. Sem fontes, o plano marca a etapa de busca como
   pendente, sem inventar referências.
6. CLI `author-editor` (structure|style|brief) pela fachada científica; não usa
   o fallback externo v4.1 nem rede/LLM nos testes. Pontuações não são aceite
   editorial nem "Qualis A1"; `scientific_acceptance=false` e revisão humana.
7. Testes cobrem extração real de seções, anti-plágio (ausência de verbatim),
   registro de raciocínio mapeado a motores existentes e limites de entrada.

## Limites

Sem plágio: nenhuma saída contém sentenças copiadas; o "estilo" é descrito por
características, não reproduzido. Sem autoavaliação de qualidade: nota interna
não vira Qualis/aceite. Sem rede nesta camada: busca real permanece nos
conectores autorizados do primário. Raciocínio formal é instrumento de clareza,
não substituto da evidência empírica nem de revisão por pares.

## Verificação

RED antes da implementação; GREEN e gates locais em recibos separados. Suíte
não usa LLM nem rede; fixtures sintéticas explicitamente identificadas.

## Evidência de execução

RED: contra o teste final, 14 testes falharam por ausência do módulo
`academic.author_editor` (asserção "Módulo R991 ausente") — recibo aceito
`tdd-802e166d257e42aaaea542f06e0f62bd`. GREEN: `tests/test_r991_author_editor.py`
— **14 passed**; `red_history_valid=true`, evidência `14 passed in 2.58s`.
Regressão combinada R991+R989+R990+SDD/TDD: **68 passed**.

A camada `academic/author_editor.py` implementa: `MANUSCRIPT_SECTIONS` (IMRaD
expandido, 10 seções), `extract_structure` (por cabeçalho PT/EN, sem fabricação),
`style_fingerprint` (anti-plágio por construção: `verbatim_spans=[]`), e
`reasoning_registry` (10 tradições mapeadas a motores do Core). CLI
`author-editor` exposta pela fachada científica. Nenhum LLM, rede ou execução
MASWOS foi acionado; a busca externa e o aceite editorial continuam externos.

Sobre `https://innovationmap.at`: é um gráfico interativo (Envisioning), sem
corpus de artigos; nenhum paper foi baixado ou "extraído" dessa URL. Temas dali
podem virar sementes de busca nas fontes OA autorizadas (OpenAlex/Crossref/
arXiv/EuropePMC) — etapa não executada nesta entrega.
