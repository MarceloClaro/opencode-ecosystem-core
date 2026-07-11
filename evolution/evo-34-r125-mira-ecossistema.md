# R125 — MIRA como parte de primeira classe do ecossistema

## Objetivo

Tornar o pipeline MIRA de apresentações (R123) alcançável e visível em
todas as superfícies do ecossistema: expor `orchestrator.present()` no
CLI (comando direto + opção de menu), atualizar os textos de ajuda e
documentar o subsistema no README, no ARCHITECTURE e no mapa 3D,
conectando-o aos agent cards MIRA que já existem no catálogo.

## Motivação

Pedido do usuário: "quero mira como parte do ecossistema".

O R123 entregou o motor executável (`MiraDeckPipeline`) e o método
`present()` — mas sem **nenhum ponto de entrada para o usuário**: não
havia comando de CLI nem opção de menu que o disparasse. Ao mesmo tempo,
o catálogo **já continha** os agent cards do método MIRA (`mira-extract`,
`mira-planner`, `mira-copywriter`, `mira-builder`, `mira-animator`,
`mira-validator`, além de `37_agente_apresentacao_slides_banca`),
registrados por `register_catalog_agents`. O elo faltante era de
**exposição/ativação**, não de implementação.

## Mudanças Entregues

1. **`marceloclaro/cli.py`**:
   - Comando direto `apresentacao` (aliases `present`, `mira`):
     `python3 -m marceloclaro.cli apresentacao <pasta>` → chama
     `orchestrator.present(pasta)` e imprime o resultado; sem pasta,
     imprime uso e sai com código 1.
   - Opção de menu `[10] Apresentação MIRA` com prompt guiado pela pasta;
     pasta vazia cancela sem chamar `present`.
   - `MENU`, `AJUDA_TEXT` e a dica de "comando desconhecido" atualizados
     (linguagem simples: "transforma o manuscrito de uma produção num
     deck de slides animados").
2. **`README.md`**: bullet de feature (R123/R125) + bullet da capa TikZ
   (R124); nó `MiraDeck` e `Publishing` (+TikZ) no diagrama Mermaid;
   linha 6 da tabela de camadas; contagens atualizadas (83 ciclos
   R47–R125, 1332 testes, 44 specs, score médio 9.21 recalculado).
3. **`ARCHITECTURE.md`**: nó `Illus` enriquecido (deck MIRA + CLI),
   `Publishing` (+TikZ); tabela de specs formais ganhou R122/R123/R124/
   R125.
4. **`docs/architecture_map.html`**: stats (1332/83 R1–R125/44 specs); nó
   da CLI (+[10]); nós Illustrations/Evolution Registry/resumo phd.
5. **`tests/test_r125_mira_cli_integration.py`**: 9 testes TDD.

## Verificação

- TDD: testes escritos antes → vermelho (9 failed) → verde (9 passed),
  com `present()` mockado (sem I/O real de deck).
- `node --check` no JS do mapa 3D → OK; balanceamento Mermaid
  (README 79/79 colchetes, 23/23 parênteses; ARCHITECTURE 74/74, 41/41).
- Testes de conteúdo de docs (R104b/R110/R116) e do CLI (R120) verdes.
- Contagens conferidas contra a fonte real (`cycles.json`, `ls specs`,
  `pytest --collect-only`), não hardcodadas por estimativa.
- `python3 -m pytest tests/ -q` completo.

## Lições

1. "Parte do ecossistema" tem duas faces: o **motor** (R123 já o tinha) e
   a **exposição** (CLI + docs + diagramas). Um recurso implementado mas
   não alcançável pelas portas de entrada do usuário é, na prática,
   invisível — a lacuna do R125 era exatamente essa casca de ativação.
2. Os agent cards MIRA já estavam no catálogo desde antes, mas
   desconectados do pipeline executável. Registrar cards não basta:
   é preciso um caminho executável real que os "encarne" (aqui, o
   `present()`), e um ponto de entrada que o dispare. O acoplamento
   formal entre um agente-executor do runtime e o pipeline continua
   sendo evolução natural para ciclo futuro.
3. As contagens "vivas" (testes/ciclos/specs) já estavam defasadas em
   R121 porque R123/R124 não fizeram doc-sync. Reforça a lição do R122:
   vale gerar esses números a partir da fonte real em vez de
   hardcodá-los — aproveitei este ciclo para reconciliá-los de fato.

## Score

**8.5/10**

- Fecha o pedido direto do usuário (MIRA alcançável e documentado como
  parte do sistema), conectando o motor R123 às superfícies reais.
- TDD real (vermelho→verde), docs com paridade de diagrama verificada e
  contagens reconciliadas contra a fonte, não estimadas.
- É sobretudo integração/exposição — não introduz um agente-executor do
  runtime acoplado ao pipeline (deixado explícito como ciclo futuro).
