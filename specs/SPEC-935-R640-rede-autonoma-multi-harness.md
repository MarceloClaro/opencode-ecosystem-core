---
spec_id: SPEC-935-R640
title: Rede coordenada Transformer e execução multi-harness
status: green
component: marceloclaro/autonomous.py + integrations/harness_runtime.py + integrations/ecosystem_mcp.py
test_file: tests/test_r640_autonomous.py
---

# SPEC-935-R640 — Rede coordenada e execução multi-harness

## Problema observado

O comando de abertura usa o OpenCode instalado no Ubuntu. A configuração não
define `default_agent`, permitindo iniciar em `build` em vez do orquestrador.
A federação R621 descobre e ranqueia artefatos, mas não os executa e não está
exposta ao OpenCode por um MCP que coordene Blackboard, Transformer e MetaBus.
Detectar arquivos de instruções ou emitir um ranking não comprova execução.

## Contrato

1. Selecionar `marceloclaro` por padrão na configuração gerada e disponibilizar
   um MCP do ecossistema com diagnóstico, roteamento e execução coordenada.
2. Manter o `MarceloClaroOrchestrator` como entrada; reutilizar sua atenção,
   delegação, despacho, conclusão e memória para acompanhar tarefas reais.
3. Reutilizar artefatos Claude, Antigravity e Codex como instruções com
   proveniência; não executar comandos de hooks ou scripts importados.
4. Detectar os executáveis no ambiente do processo MCP, inclusive instalações
   do usuário ausentes do PATH de um processo WSL sem shell de login.
5. Usar adaptadores externos com prazo finito, retorno estruturado e falha
   explícita para binário ausente, timeout, código não zero ou saída vazia.
   A execução inicial destina-se a análise e geração de texto com acesso de
   leitura; não usar opções de bypass de permissões.
6. O coordenador tem limite de passos e de tempo; não despacha para executor
   indisponível e não anuncia sucesso de tarefas apenas enfileiradas.
7. Codex é uma CLI distinta: presença de `AGENTS.md` não significa instalação.
   O aplicativo ChatGPT não é controlado por esta ponte; eventual alias
   `chatgpt` deve declarar que usa a CLI Codex e sua disponibilidade real.
8. Explicar que Transformer aqui significa roteamento multiagente inspirado
   em atenção, não treinamento ou criação de uma rede neural.
9. Os relatórios legados não podem afirmar sincronização nem exportação de
   agentes sem realizar escrita ou execução. Separar preview, inventário,
   configuração presente, instalação e validação de execução.

## Aceitação

- Testes RED/GREEN herméticos de disponibilidade, argumentos, falhas, prazo,
  conclusão das tarefas, seleção do orquestrador e exposição MCP.
- Regressões do Transformer, federação R621 e configuração OpenCode.
- Validação do OpenCode instalado: configuração efetiva, agente padrão e
  conexão MCP. Verificação real dos executores disponíveis separada dos mocks.
- Registrar resultado e limitações observadas; manter alterações anteriores.

## Resultado observado — 2026-10-03

- Gate final: **185 passed, 1 skipped** nos testes R640, Transformer, R621,
  configuração/permissões, catálogo, documentação, ponte e handshake MCP.
  O teste pulado é opt-in externo; os testes herméticos não substituem os
  probes reais abaixo. Lint F/E9 e `git diff --check` sem erros.
- OpenCode 1.18.34: configuração efetiva confirma `default_agent=marceloclaro`,
  oito MCPs e comando `ecosystem`; todos os oito MCPs conectaram.
- Codex Windows via WSL e Antigravity: respostas reais aos probes limitados.
- MCP real: tarefa `task-a71ade19` concluída por `auditor`, executada no Codex
  com instruções federadas de origem Claude; conclusão e reflexão registradas.
- MCP automático: tarefa `task-6982c2d5` concluiu em dois passos com fallback
  Claude→Codex; recusa de saldo preservada no relatório.
- Claude: instalação e flags confirmadas, execução recusada por saldo
  insuficiente da conta. Nenhuma alteração de credencial ou cobrança.
- Provas resumidas e logs locais ficam em `.backups/r640/`. O roteamento é
  inspirado em atenção e a nota textual é heurística; sem treinamento neural,
  daemon contínuo ou validação científica externa.
