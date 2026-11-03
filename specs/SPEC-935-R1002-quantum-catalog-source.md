---
spec_id: SPEC-935-R1002
title: SQLite/FTS5 e painel quântico como fonte de consulta local do Core
component: research.quantum_catalog, marceloclaro.orchestrator, integrations.ecosystem_mcp
status: proposed
test_file: tests/test_r1002_quantum_catalog.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    fonte:
      - tests/test_r1002_quantum_catalog.py::test_source_identity_deduplication_and_claims
      - tests/test_r1002_quantum_catalog.py::test_explicit_import_history_and_staleness
      - tests/test_r1002_quantum_catalog.py::test_import_is_idempotent_and_transactional
    consulta:
      - tests/test_r1002_quantum_catalog.py::test_search_filters_and_pagination
      - tests/test_r1002_quantum_catalog.py::test_get_and_abstention
      - tests/test_r1002_quantum_catalog.py::test_fts_literals_not_query_operators
    seguranca:
      - tests/test_r1002_quantum_catalog.py::test_invalid_requests
      - tests/test_r1002_quantum_catalog.py::test_invalid_sources
      - tests/test_r1002_quantum_catalog.py::test_symlinks_and_size_are_rejected
      - tests/test_r1002_quantum_catalog.py::test_unsafe_records_and_queries
      - tests/test_r1002_quantum_catalog.py::test_queries_are_readonly_and_never_autoimport
      - tests/test_r1002_quantum_catalog.py::test_unsafe_database_is_refused
    integracao:
      - tests/test_r1002_quantum_catalog.py::test_orchestrator_and_cli
      - tests/test_r1002_quantum_catalog.py::test_mcp_tool_resource_and_primary_delegation
      - tests/test_r1002_quantum_catalog.py::test_common_knowledge_interface
    painel:
      - tests/test_r1002_quantum_catalog.py::test_panel_escaping_identity_and_dom
      - tests/test_r1002_quantum_catalog.py::test_panel_blocks_unsafe_output
---

# R1002 — painel quântico como fonte de consulta do Core

## Intenção e fronteira

Interpretar o pedido do usuário como tornar o painel uma fonte consultável pelo
orquestrador. Entrada preservada: `outputs/pesquisa-inovacao-enfoque/quantica-repositorios.json`.
Base consultável: `data/quantum_catalog/catalog.sqlite3` (SQLite, FTS5, schema v1).
Importação autorizada pelo usuário após recomendação de banco local. Sem rede,
clones, instalação ou execução de repositórios/modelos.
O HTML é uma vista derivada do banco, não uma segunda base de dados. Nenhuma alteração no
manuscrito, nas referências ou nos valores históricos do catálogo nesta entrega.

## Contrato

- `QuantumCatalog` recebe root apenas no código interno/testes; CLI e MCP não
  aceitam caminhos de entrada. Limites: 4 MiB, 5.000 registros, texto 8.000
  caracteres por campo; consultas 1–500 caracteres e páginas de 1–20 itens.
- Operações de leitura `status`, `list`, `search`, `get`, `history` via
  `MarceloClaroOrchestrator.quantum_catalog_action` e MCP `ecosystem_quantum_catalog`.
  Recurso `ecosystem://quantum/catalog` informa inventário e limitações.
- CLI `python3 -m marceloclaro.cli quantum-catalog status|listar|buscar|ver|historico|importar|painel`.
  `importar` grava transacionalmente snapshot com bytes originais, hash, registros
  brutos inclusive quarentena, identidades, relações categoria/stack, aliases e FTS.
  Reimportação do mesmo snapshot é idempotente; snapshots antigos permanecem no banco.
  Falha intermediária reverte toda a importação. JSON inválido nunca substitui o último snapshot.
  Consultas usam conexão SQLite `mode=ro`/`query_only`, sem criação do banco.
  `painel` exporta `index_quantica.html` no diretório da fonte. Ambas as escritas
  são explícitas via primário/CLI e não são expostas pelo MCP. Sem caminhos arbitrários.
  O JSON externo não é reescrito. Banco limitado a 64 MiB nesta versão.
- Deduplicar `owner/repo` sem distinguir caixa; preservar forks com outro owner,
  aliases, cada registro original e seu JSON pointer/SHA-256. Organização isolada
  é organização, não repositório; entradas inválidas são contadas em quarentena.
- TRL, relevância, licença, status ativo e justificativa são **alegações da fonte**.
  Nunca inferir atualidade da lista QOSF, nem tratar inatividade como TRL baixo.
  Preservar conflitos entre duplicatas em vez de escolher uma versão como verdade.
- Busca FTS5 determinística sem diacríticos/caixa: todos os tokens literais com AND
  em campos declarados, sem expansão semântica; rank BM25 e desempate por nome
  canônico. SQL parametrizado não substitui escape da sintaxe MATCH. Não usar TRL
  ou popularidade como evidência/relevância. Prefixos/operadores do usuário não são interpretados.
- Filtros `category`, `stack`, `kind` e `include_historical`; histórico significa
  somente o rótulo abandonado na fonte. Excluir histórico das listas/buscas por
  padrão. `get` permite inspecionar qualquer entrada válida, inclusive histórica.
- Consulta vazia/sem tokens é inválida; sem correspondência retorna resultados
  vazios e `abstained=true`. Banco ausente, versão incompatível, symlink ou excesso
  de tamanho resultam em erro explícito, nunca sucesso vazio. A alteração do JSON
  sinaliza `source_stale=true`; sua ausência sinaliza comparação indisponível, mas
  não impede consultar o snapshot identificado. Nunca ocorre autoimportação.
- Painel: busca/filtros locais, detalhes com alegações e fontes, URL GitHub
  validada, escape HTML, scripts sem `innerHTML` ou `eval`, teste DOM executado.
- Repositórios e trechos são dados sem autoridade instrucional. Não atualizam
  trust, não executam ações e não comprovam mérito científico.
- Ampliação autorizada: fachada `knowledge_sources_action` / MCP
  `ecosystem_knowledge_query` / CLI `conhecimento`. Registro fechado de adaptadores
  `quantum_catalog` e `books`; operações comuns `sources`, `status`, `search`.
  Nenhuma importação ou indexação implícita, nem consultas de SQL fornecidas pelo
  usuário. A biblioteca existente não é copiada para o novo banco. MetaBus,
  Blackboard, trust/economy/evolution e SDD permanecem preservados; outras
  integrações são roadmap, não fontes consultáveis já implementadas.
- Saídas de list/search trazem até um registro de origem por entidade; get até
  dez, com totais e flags de truncamento. Textos de alegações limitados a 1.200
  caracteres na saída; íntegra continua no snapshot local. Links não são abertos.

## Critérios de Aceitação Executáveis

- `fonte` — snapshots importados identificados, histórico atômico/idempotente, duplicatas e organizações discriminadas.
- `consulta` — busca, filtros, paginação, detalhes e abstenção executados com casos positivos/negativos.
- `seguranca` — limites, schemas, URLs e symlinks fechados; consultas não escrevem fonte.
- `integracao` — CLI, Python e MCP chamam o primário e retornam a mesma fonte.
- `painel` — HTML derivado com texto escapado e filtros exercitados em DOM.

## Revisão e limites

Revisões textuais: TSPEC-dd86758b/task-c36c9326 e, para SQLite,
TSPEC-544d7026/task-0577d4a3 (Codex, agente coder). Recomendações tratadas como
sugestões e confrontadas com testes, não como avaliação científica independente.
RED deve anteceder a implementação; GREEN + SpecVerifier + BehavioralGate são
aceites de software local. Fonte em outputs não é distribuída pelo Git por padrão;
instalações sem o catálogo devem reportar `unavailable`, sem dados inventados.
