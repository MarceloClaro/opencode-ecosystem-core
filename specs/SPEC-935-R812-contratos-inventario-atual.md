---
spec_id: SPEC-935-R812
title: Reconciliação dos contratos de inventário e configuração local
component: tests, documentação operacional
status: implemented
round_id: R812
test_file: tests/test_r448_documentation_reconciliation.py
---

# SPEC-935-R812 — Inventário atual

## Evidência RED

A suíte geral R808 encontrou números fixados em ciclos antigos: catálogo R380
esperava 212 registros, documentos anunciavam 248 agentes/15 MCPs, e testes
R211/R652 exigiam `uvx` no PATH apesar da resolução portátil por runtime R644.
Os arquivos reais tinham 253 agentes antes desta tarefa. A conexão real falhou
para arXiv até resolver o launcher instalado, e passou nos 16 MCPs após a correção.

## Contratos

1. O catálogo deve carregar cada arquivo Markdown uma única vez; os 46 perfis
   migrados em R380 conservam descrição concreta e proveniência. A adição de
   agentes fora desse conjunto não pode invalidar uma migração histórica.
2. Launchers podem ser resolvidos a partir da instalação local; caminhos de
   scripts continuam relativos. O filesystem recebe apenas a raiz explícita
   do workspace. Nenhum caminho específico de uma máquina é fixado no gerador.
3. Inventários atuais dos documentos operacionais devem corresponder ao
   `build_config` e à quantidade de checks do doctor. Snapshots históricos
   continuam identificados como históricos.
4. Não editar manuscritos nem relaxar gates editoriais para corrigir contagens
   operacionais. Falhas científicas/editoriais permanecem no relatório da revisão.

## Validação

Reexecutar R211, R380, R448, R455 e R652; comparar o arquivo OpenCode regenerado
ao gerador, inclusive o perfil restaurado por R811. Testes não substituem a
conectividade MCP real, registrada separadamente.
