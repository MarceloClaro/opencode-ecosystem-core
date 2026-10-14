# Plano de implementação R887

**Objetivo:** prover contexto estrutural de código local ao primário, com índices
privados, fontes rastreáveis e ausência de rede durante indexação/consulta.
**Spec:** `specs/SPEC-935-R887-code-intelligence-local.md`.
**Arquitetura:** um processo filho context-link sob a fachada MCP existente;
MetaBus canônico, sem outro coordenador. Python 3.14, MCP stdio e binário fixado.

## Restrições e revisão

Não executar código dos alvos. Filtrar corpus Git, symlinks e segredos. Fixar
asset/digest/licença. Processos limitados a dois workers e prazo explícito.
Falhar diante de schema inválido, tool fora da lista, índice obsoleto, timeout
ou isolamento indisponível. Não confundir bytes com tokens ou instalação com
benefício. Evitar compiladores/modelos e a suíte global simultâneos: a execução
global anterior consumiu recursos até interromper a VM WSL; serão usadas
regressões dirigidas e sondagens isoladas.

## 1. Provedor e corpus

- Escrever `tests/test_r887_code_context.py` e observar RED.
- Implementar `integrations/code_context.py::CodeContextProvider.run(config)`:
  operações setup/index/status/query, arquivo de estado privado, consulta por
  tool/arguments, sem instalação automática em consulta.
- Conferir digest, isolamento de rede e smoke MCP sobre fixture conhecida;
  executar casos negativos e registrar GREEN em `outputs/core-r887`.

## 2. Fluxo conectado

- Escrever `tests/test_r887_orchestration.py` antes das alterações.
- Adicionar `MarceloClaroOrchestrator.code_context_action(config)`;
  persistir observação mínima, sem promoção de confiança.
- Anexar contexto de código limitado e tratado como dado aos briefings de
  delegações de software quando disponível; indisponibilidade explícita.
- Expor status/query em `ecosystem_code_context`, reutilizando o primário
  compartilhado; CLI `marceloclaro code-context` para setup/index/query/status.
- Acrescentar comando ao gerador canônico e reproduzir `opencode.json`.

## 3. Aceite local e publicação

- Executar regressões de R886, primário, MCP, configuração e documentação.
- Indexar corpus filtrado do Core e consultar símbolo conhecido pelo primário.
- Comparar bytes e chamadas com busca textual/trechos equivalentes; informar
  ganho, perda ou ausência de conclusão conforme os dados.
- Atualizar instruções/README, recibo local e ciclo R887 sem reescrever o
  recibo histórico R886. Revisar diff e publicar commit na branch autorizada.
