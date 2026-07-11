# R120 — Comando `pesquisa` no CLI + Visibilidade do Fallback Sci-Hub

## Objetivo

Expor no CLI interativo do `marceloclaro` o pipeline de pesquisa
científica multiplataforma (11 fontes, R111) que até aqui só era
acessível programaticamente, e tornar visível na documentação de
arquitetura e no `doctor()` o fallback Sci-Hub que já existia no
código de download de PDFs.

## Contexto

Usuário perguntou se o "Research Hub — 11 fontes: +PubMed/bioRxiv/CORE
(R111)" estava integrado à arquitetura do ecossistema. Rastreamento da
cadeia completa confirmou que sim: `research/searchers.py` (11
buscadores) → `MultiSearcher` → `research/hub.py::ResearchHub` →
`research/__init__.py` → `marceloclaro/orchestrator.py::research()`/
`research_search()`, com reflexão registrada na memória metacognitiva
ao final de cada execução. **Porém**: `marceloclaro/cli.py` não
expunha nenhum comando para isso — nem no menu interativo, nem como
comando direto.

Em seguida, pedido para adicionar Sci-Hub. Investigação mostrou que
`research/downloader.py` já delega para o pacote de terceiros
`scihub-cli` (Oxidane-bot) como fallback de download para artigos
pagos sem acesso aberto direto — já existia antes desta sessão, só não
estava documentado nem verificado pelo `doctor()`.

## Mudanças Entregues

1. **`marceloclaro/cli.py`**:
   - Comando direto `pesquisa "<tema>"` (alias `research`), com flags
     `--max-papers N`, `--platforms a,b,c`, `--no-download`
   - Opção `[9]` no menu interativo com prompts guiados e resumo
     amigável (artigos selecionados, PDFs baixados, fichamentos,
     resenhas, pasta de saída)
   - `_parse_pesquisa_flags()` isolado para parsing testável
   - `AJUDA_TEXT`/`MENU` atualizados

2. **`marceloclaro/doctor.py`**: `scihub-cli` adicionado a
   `EXTERNAL_CLIS` (mesmo padrão do R116 — sempre `warn`, nunca
   `fail`, com sugestão de instalação exata).

3. **Documentação sincronizada** (README.md + ARCHITECTURE.md — os
   dois diagramas Mermaid mantidos em paridade desde o achado do R117
   — e MANUAL.md): nó Research Hub ganha menção ao CLI `pesquisa`
   (R120) e ao fallback Sci-Hub; tabela do menu em MANUAL.md ganha a
   linha `[9]`; FAQ de CLIs opcionais menciona `scihub-cli`.

4. **Testes**: `tests/test_r120_cli_pesquisa_command.py` (13 testes) —
   parsing de flags, comando direto (com/sem tema, alias, flags),
   menu interativo (opção 9, incluindo cancelamento com tema vazio),
   registro e comportamento do check `scihub-cli` no doctor. Nenhuma
   chamada de rede real — `orchestrator.research()` sempre mockado via
   monkeypatch na classe `MarceloClaroOrchestrator`.

## Verificação

- `python3 -m pytest tests/test_r120_cli_pesquisa_command.py -v` →
  13 passed
- `python3 -m marceloclaro.cli ajuda` — confirma o novo texto da opção
  `[9]` e do comando direto `pesquisa`
- `run_doctor()` manual — confirma `external_clis` reportando
  `scihub-cli` quando ausente
- `python3 -m pytest tests/ -q` completo

## Lições

1. Um subsistema pode estar perfeitamente integrado na cadeia de
   chamadas internas (orchestrator → research hub → searchers) e ainda
   assim ser invisível para quem só usa o CLI — vale sempre checar não
   só "isso está conectado no código?" mas "isso está alcançável pela
   interface que o usuário realmente usa?".
2. "Adicionar Sci-Hub" já estava parcialmente feito (fallback de
   download já implementado) — a lacuna real era de *visibilidade*
   (documentação, `doctor()`), não de implementação. Vale sempre
   verificar o que já existe antes de construir algo do zero.
3. Reaproveitar o padrão já estabelecido em R116 (`EXTERNAL_CLIS` +
   `_check_external_clis()` genérico) custou uma linha de dicionário
   em vez de uma função nova — o padrão generalizava bem.

## Score

**8.8/10**

- Resolve uma lacuna real e específica encontrada por investigação
  (não hipotética)
- Reaproveita padrões já estabelecidos (R116 doctor checks) em vez de
  duplicar lógica
- Documentação mantida em paridade nos três lugares que descrevem o
  CLI (README, ARCHITECTURE, MANUAL), consistente com a disciplina de
  dupla-registro já praticada desde o R117
