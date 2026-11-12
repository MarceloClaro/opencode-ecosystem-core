# SPEC-935-R1107 — OpenCodeCliAdapter com isolamento

Data: 2026-11-12. Estado: implementação e teste de segurança; execução real
dependente de provider/credencial.

Origem: `specs/SPEC-935-R1106-ecosystem-run-adapter.md`.

## Escopo

Executar o OpenCode CLI como subprocesso isolado para uma tarefa reservada,
sem recursão no orquestrador e sem ferramentas.

Travas obrigatórias:

- projeto temporário com `opencode.json` próprio;
- agente `sandboxed-responder` com todas as ferramentas desabilitadas;
- `--pure` para não carregar plugins externos;
- `OPENCODE_PERMISSION='{"*":"deny"}'` no ambiente do filho;
- `OPENCODE_CONFIG` apontando para o projeto temporário;
- `--dir` no projeto temporário, `stdin=DEVNULL`;
- `--print-logs --log-level ERROR` para classificar falhas do provider;
- timeout obrigatório e kill do subprocesso;
- prompt sem `expected_action`, `expected_answer` ou `required_citations`;
- `cost=None` quando o CLI não fornece custo financeiro;
- `unauthorized_actions=0` por construção, pois nenhuma ferramenta é executada.

## Fora do escopo

Não instalar plugins, não habilitar MCP, não usar `--auto`, não alterar o
`opencode.json` do projeto principal, não promover trust e não declarar
resultado de modelo quando o provider bloquear.

## Critérios de aceitação

- CA01: sucesso com JSON válido produz `Response` com ação, resposta,
  confiança e citações.
- CA02: exit não zero, timeout, JSON inválido, ação inválida e resposta
  ausente resultam em `abstain` com `error_type`.
- CA03: limite de uso do provider é classificado como `provider_limit`, não
  como resposta do modelo.
- CA04: o subprocesso recebe `--pure`, `--agent`, `--dir`, `--model` e
  `OPENCODE_PERMISSION` deny-all.
- CA05: o prompt não contém o gabarito.
- CA06: `cost=None`; o harness não calcula custo por acerto como zero.
- CA07: testes usam executável falso; nenhuma chamada real nos testes.
- CA08: tentativa real de uma tarefa registra bloqueio do provider sem
  fabricar resposta.
- CA09: estado de produção do Core permanece inalterado.

## Plano TDD

1. `tests/test_r1107_opencode_cli_adapter.py` com executável falso.
2. RED.
3. Implementar `benchmarks/opencode_cli_adapter.py`.
4. GREEN e regressão P0/P1/R1106.
5. Tentar uma tarefa real com timeout curto; registrar resultado/falha.
