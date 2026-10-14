---
spec_id: SPEC-935-R887
title: Piloto de code-intelligence local com um único provedor MCP
component: integrations.code_context
status: proposed
test_file: tests/test_r887_code_context.py
---

# R887 — Piloto especificado, ainda não instalado

## Decisão e estado

Selecionar somente `context-link-mcp/context-link`, revisão
`e5af49c11c5b2228c6b611dd3594d93014997306` / tag `v1.1.0`, Apache-2.0.
Esta especificação reserva R887; não registra uma implementação ou ciclo de
evolução concluído. O código e a configuração do piloto ainda não existem.
R886 permanece um trabalho separado de memória/reflexão, sem este provedor.
O `test_file` reservado ainda não existe: tentar aceitar uma entrega por esta
spec deve manter o gate fechado até a implementação e o histórico RED/GREEN.

O levantamento e as fontes estão em
`docs/AVALIACAO_CODE_INTELLIGENCE_R887.md`. A compatibilidade do binário e as
alegações de economia ainda precisam de execução local.

## Contrato de integração

- Um provedor de contexto de código, subordinado ao primário; não adicionar
  outro coordenador, memória de agentes, LLM ou sumarizador remoto.
- Instalação isolada do binário Linux amd64 com digest conferido contra o
  asset fixado no levantamento; preservar licença e origem.
- Corpus materializado de fontes de produção selecionadas do Git. Excluir
  segredos, estado, binários, histórico, terceiros, templates e symlinks. O
  manifesto liga cada arquivo exportado ao caminho e hash de origem.
- Índice, configuração e caches privados fora das fontes originais. Não
  carregar configuração YAML nem notas/memórias do checkout ou de outro DB.
- Sem watcher, inferência externa ou download automático de pesos. A
  afirmação de operação sem rede depende de bloqueio e teste do ambiente;
  processo local, por si, não demonstra isolamento de rede.
- Expor somente `ping`, `semantic_search_symbols`, `get_code_by_symbol`,
  `get_file_skeleton`, `get_symbol_usages`, `get_call_tree`, `get_blast_radius`.
  Bloquear `reindex`, ferramentas de memória e demais operações. Começar com
  parâmetros escalares compatíveis com os schemas publicados.
- O primário define consulta e orçamento. O retorno inclui fonte, hash,
  limites, provedor e estado de indexação. Tool indisponível, timeout,
  caminho inválido ou índice obsoleto deve produzir estado explícito.
- Configuração MCP deriva do gerador canônico do Core, com testes de
  reprodução; não editar somente `opencode.json` nem duplicar servidores.

## Critérios de aceite do piloto

1. RED antes da implementação para: allowlist, caminhos, corpus, índice
   obsoleto, timeout, schema inválido e indisponibilidade do provedor.
2. Smoke real MCP: `initialize`, `tools/list`, `ping` e consultas de símbolo,
   skeleton, uso e chamadas sobre fixture local com resultado conhecido.
3. Confirmar que todas as consultas permitidas preservam os hashes dos
   arquivos originais; escrita somente no índice/cache declarado.
4. Confirmar isolamento de rede, ou reportar bloqueio/degradação sem alegar
   operação totalmente offline quando o ambiente não fornecer o controle.
5. Exercitar a consulta pelo caminho do primário e manter IDs/proveniência
   quando o contexto apoiar uma tarefa de codificação.
6. Medir, em perguntas fixas equivalentes, chamadas de ferramenta e bytes
   retornados contra `rg` + trechos de fonte. Registrar expansões, schemas,
   fallback e acerto das respostas. Não usar o contador interno `bytes/4`
   como consumo real de tokens, economia financeira ou ganho de precisão.
7. Medir tokens reais somente quando houver tokenizer/uso do modelo declarado;
   separar instalação, consulta correta e benefício ao agente.
8. GREEN, regressões, recibo local e ciclo de evolução R887 somente após a
   implementação e a execução dos critérios aplicáveis.

## Fronteira desta especificação

Não há ganho comprovado, instalação, federação funcional ou novo MCP ativo
por existir este documento. Adoção de Knowl, Laya, OpenShell ou Feynman não é
pré-requisito do piloto. Outros harnesses e decodificação especulativa ficam
fora deste escopo.
