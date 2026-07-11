# R123 — Pipeline MIRA de Apresentações Científicas (artigo → deck animado)

## Objetivo

Implementar no ecossistema a linha de montagem de apresentações do
método MIRA (livro "MIRA" + `sandeco/mira-animator`): os 6 estágios
`extract → planner → copywriter → builder → animator → validator`,
transformando um manuscrito científico num deck HTML navegável de cards
de vidro animados, com relatório de conformidade, e expondo isso no
orquestrador via `MarceloClaroOrchestrator.present()`.

## Motivação

Pedido do usuário: "avalie o ecossistema e aprimore para o agente possa
fazer de artigo a animações e apresentações científicas com o mira".
Referência apontada pelo usuário: <https://github.com/sandeco/mira-animator>.

A avaliação encontrou a lacuna real: `illustrations/mira_engine.py` já
gerava **cards MIRA avulsos** (metáfora animada por seção, Regra Zero,
título ≤6 palavras) — mas cada card era um HTML isolado, sem navegação.
Faltava o **pipeline de deck**, que é o coração do método: a linha de
montagem de 6 postos com fronteiras limpas, produção card-a-card em vidro
translúcido, repertório de tipos de card e um inspetor final de
conformidade. Não existia `present()` — o elo artigo→apresentação estava
ausente (`produce_scientific_work()` faz o artigo, `illustrate()` faz
figuras avulsas, nada montava a apresentação).

## Mudanças Entregues

1. **`illustrations/mira_deck.py` (novo)** — a esteira MIRA:
   - Dataclasses `Section`, `Briefing`, `SlideSpec`, `SlidePlan`, `Deck`,
     `ConformityReport` (esta com `to_markdown()`).
   - `MiraDeckPipeline` com os 6 estágios como métodos públicos e
     chamáveis isoladamente (a esteira para nas juntas — consertar a
     peça, não a fábrica):
     - `extract(markdown)` → `Briefing`: 1 seção por `##`, detectando
       citações (`>`), blocos de código (```` ``` ````) e itens paralelos.
     - `plan(briefing)` → `SlidePlan`: capa + 1 slide por seção +
       encerramento, com o tipo do card seguindo o formato da ideia
       (citação→`quote`, código→`code`, itens paralelos→`grid`, padrão→
       `concept` com metáfora do catálogo do `MiraEngine`).
     - `copywrite(plan)`: títulos clipados a ≤6 palavras, subtítulos
       enxutos (heurístico; LLM opcional fica para ciclo futuro).
     - `build(plan)` → `Deck`: UM HTML autocontido, cards de vidro
       (`backdrop-filter`), navegação card-a-card (setas do teclado +
       botões prev/next), **sem** animação ainda.
     - `animate(deck)`: aplica a Regra Zero (coreografia de entrada +
       loop perpétuo `infinite` por card) e injeta a cena SVG da
       metáfora nos cards de conceito.
     - `validate(deck)` → `ConformityReport`: inspetor final (Regra Zero
       de entrada e loop, títulos ≤6 palavras, navegação presente,
       autocontido, cards de vidro).
     - `run(markdown, output_dir)`: executa a esteira inteira e grava
       `deck.html` + `CONFORMIDADE.md`.
2. **`illustrations/__init__.py`** — exporta `MiraDeckPipeline` e as
   dataclasses do deck.
3. **`marceloclaro/orchestrator.py::present(production_folder)` (novo)** —
   lê `manuscrito.md` da produção, roda a esteira em `apresentacao/`,
   registra reflexão na memória metacognitiva (mesmo padrão de
   `illustrate()`/`research()`); retorna erro gracioso se o manuscrito
   não existir.
4. **`tests/test_r123_mira_deck_pipeline.py` (novo)** — 26 testes
   escritos ANTES da implementação (TDD), cobrindo cada estágio
   isoladamente, a linha completa (`run`) e a integração com o
   orquestrador (`present()` com pasta sintética, sem rede).

## Verificação

- TDD: testes escritos antes → vermelho (2 failed, 24 errors) → verde
  (26 passed) após a implementação.
- Deck de demonstração gerado e inspecionado: 6 slides, 4 loops
  `infinite`, glassmorphism presente, 1 cena SVG de metáfora injetada,
  `CONFORMIDADE.md` com resultado ✅ CONFORME.
- `python3 -m pytest tests/ -q` completo.

## Lições

1. O `MiraEngine` existente (cards avulsos) e o novo `MiraDeckPipeline`
   (deck navegável) compartilham a mesma "alma" (catálogo de metáforas,
   Regra Zero, título ≤6 palavras) sem duplicá-la — o pipeline reusa
   `pick_metaphor()` e o `CATALOG`. Manter os dois estágios `build` e
   `animate` separados (build monta a estrutura estática; animate injeta
   os loops) tornou a fronteira verificável por teste ("build ainda não
   tem loop; animate garante a Regra Zero"), que é exatamente o valor da
   linha de montagem: cada posto tem entrada/saída limpas.
2. Fora de escopo consciente (extensões naturais para ciclos futuros): os
   agentes visuais do cap. 4 do livro (`mira-3d`, `mira-qrcode`,
   `mira-chart-race`, `mira-survey`), vídeos de fundo, copywriting via
   LLM e aprovação interativa estágio-a-estágio no CLI — a API por posto
   já suporta o fluxo supervisionado, falta só a casca interativa.

## Score

**8.7/10**

- Fecha uma lacuna real e nomeada pelo usuário (elo artigo→apresentação
  ausente), não cosmética; entrega os 6 postos do método com fronteiras
  limpas e verificáveis.
- Disciplina TDD real (vermelho documentado antes do verde), 26 testes
  cobrindo estágios isolados + linha completa + integração, deck
  inspecionado de fato.
- Estágio `copywrite` é heurístico (sem LLM) e o repertório de cards
  cobre o essencial (cover/concept/quote/code/grid/closing) mas não os
  agentes visuais avançados do cap. 4 — deixado explícito como escopo
  futuro, não escondido.
