---
spec_id: SPEC-935-R944
title: MCPs e agentes especializados para o corpus Airam Veras
component: integrations.airam_education_mcp_agents
status: implemented
test_file: tests/test_r944_airam_mcp_agents.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    matrix_mcp:
    - tests/test_r944_airam_mcp_agents.py::test_matrix_mcp_reads_only_allowlisted_databases
    - tests/test_r944_airam_mcp_agents.py::test_matrix_mcp_lists_and_searches_with_bounded_parameterized_queries
    - tests/test_r944_airam_mcp_agents.py::test_workspace_airam_matrix_corpus_smoke_when_present
    law_mcp:
    - tests/test_r944_airam_mcp_agents.py::test_law_catalog_is_explicit_non_exhaustive_and_temporally_cautious
    - tests/test_r944_airam_mcp_agents.py::test_law_fetch_uses_only_fixed_official_sources_and_does_not_write
    mcp_surface:
    - tests/test_r944_airam_mcp_agents.py::test_mcp_servers_expose_only_the_declared_read_only_tools
    managed_agents:
    - tests/test_r944_airam_mcp_agents.py::test_specialist_profiles_are_managed_read_only_and_bound_to_mcp_contracts
    integrated_profile:
    - tests/test_r944_airam_mcp_agents.py::test_existing_integrated_agent_uses_local_corpus_and_excludes_restricted_data
    opencode_registration:
    - tests/test_r944_airam_mcp_agents.py::test_generated_config_registers_mcp_servers_and_specialists
---

# R944 — MCPs e agentes especializados para o corpus Airam Veras

## Objetivo

Integrar ao OpenCode Ecosystem Core o corpus local `PROJETO 1/Airam veras` com
dois MCPs read-only e dois agentes especializados. O agente integrado existente
`caed-spaece-educacao-ceara` passa a usar o corpus local e os novos MCPs. O
projeto externo `p2p.kiwi` continua separado: é um aplicativo de compartilhamento
de tela, não fonte de dados educacionais nem dependência dos MCPs deste contrato.

## Critérios de aceitação

- **MCP de matrizes `caed-spaece-data`** — expõe status, catálogo por sistema/ano/
  edição/etapa/série/componente, recuperação de uma matriz e busca limitada por
  descritores. Usa apenas `caed-dados/dados/caed.sqlite` e
  `spaece-dados/dados/spaece.sqlite` sob `PROJETO 1/Airam veras/`, sempre em
  modo SQLite read-only, com tabelas/colunas allowlisted, consultas
  parametrizadas, limites de resultados e sem aceitar caminho, SQL ou tabela do
  chamador. Cada resultado preserva sistema, edição/ano se conhecido, matriz,
  componente, etapa/série, código, localizador, origem e hash disponível. SPAECE
  legado sem ano explícito retorna ano não informado, não inventado.
- **Privacidade fail-closed** — nenhum MCP ou agente lê/processa
  `resultados-caed-ciclo-i-2026/`, `resultados-saap-ciclo-i-2026/`, arquivos
  `RESTRITO`, datasets completos de alunos, microdados, nomes, matrículas ou
  resultados individuais. A indexação pública limita-se a matrizes, descritores
  e metadados de documentos. Não executar scripts, notebooks, testes, SQL de
  terceiros, builds ou dependências dentro de Airam Veras ou `p2p.kiwi`.
- **MCP de fontes legais `educacao-legislacao`** — lista fontes por identificador
  fixo (ECA, LDB, LBI, PNE, PEE/CE e normas diretamente relacionadas à inclusão)
  e, quando solicitado, faz somente GET de fontes oficiais allowlisted, com
  limite de bytes/tempo, sem aceitar URLs do chamador, sem redirecionamento para
  hosts externos e sem gravar cache/arquivos. Retorna URL final validada, HTTP
  status, data/hora, hash do conteúdo, recorte e truncamento. Não determina
  revogação, vigência ou sucessão apenas por 404, silêncio do portal ou presença
  no catálogo. PNE/PEE ficam `vigência não verificada` até evidência legal
  adequada; Lei estadual 16.025/2016 tem período declarado 2016–2024.
- **Agentes** — criar `caed-spaece-matrix-specialist` e
  `educacao-legislacao-ceara-specialist` como perfis `managed-v1` pelo primário;
  manter `caed-spaece-educacao-ceara` como perfil integrado. Todos são
  somente-leitura, não delegam, não executam shell arbitrário e têm contratos
  de status/findings/evidence/limitations. Os prompts exigem declarar lacunas,
  diferenciar programa/edição e norma histórica de vigente, e não alegar
  completude além do corpus verificável.
- **Corpus local** — os READMEs do usuário reportam `caed-dados` com 54 PDFs,
  129 matrizes e anos 2017, 2018, 2019, 2022–2026; o snapshot SPAECE anterior
  contém 7 matrizes/146 descritores. Esses são metadados declarados pelo corpus,
  não validação independente integral. Anos ausentes no arquivo local não
  provam que matrizes nunca tenham sido publicadas. Avalie.CE, SPAECE, CNCA,
  diagnóstica, formativa e somativa permanecem identificados separadamente.
- **OpenCode preservador** — acrescentar os servidores e agentes tanto em
  `integrations/opencode_cli.build_config()` quanto em `opencode.json`, sem
  restaurar ou reformatar semanticamente configurações preexistentes do operador.
  As configurações MCP ficam limitadas aos comandos fixos do Core e não recebem
  dados pessoais como argumentos.
- **REA** — registrar o uso apenas como análise estática. REA examinou o clone
  `p2p.kiwi` sem executar seu código; o retorno foi parcial por limite de
  transporte, com grafos/relacionamentos declarados incompletos. Não usar esse
  resultado para criar integração P2P ou concluir comportamento runtime.
- **Verificação** — os testes R944 passam sem rede; doctor não tem falhas novas;
  MCP de leis é testado com transporte simulado. Testes locais não provam
  vigência jurídica, autorização dos detentores das matrizes, completude
  histórica nem segurança externa.

## Fora de escopo

Não ingerir ou publicar microdados, não alterar os arquivos do usuário em
`PROJETO 1/Airam veras`, não executar o aplicativo `p2p.kiwi`, não criar
compartilhamento de tela/controle remoto, não fazer parecer jurídico e não
prometer que a lista seed de normas contém todas as normas educacionais em
vigor. A aquisição de novas matrizes ou legislação permanece sujeita a
proveniência/licença e revisão humana.
