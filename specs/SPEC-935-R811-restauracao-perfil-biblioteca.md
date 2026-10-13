---
spec_id: SPEC-935-R811
title: Restauração do contrato do especialista de entradas vazias da biblioteca
component: agents/catalog/library-empty-input-audit
status: implemented
round_id: R811
test_file: tests/test_r678_library_empty_input_specialist.py
---

# SPEC-935-R811 — Restauração do perfil R678

## Falha observada

A suíte do ecossistema encontrou o perfil
`agents/catalog/library-empty-input-audit.md` ausente, embora a especificação
R678 e os testes de carregamento, permissões e atribuição A2A existam.
Reexecução isolada reproduziu quatro falhas e dois erros de preparação antes
da restauração. O registro desse RED está em
`outputs/rea-r808/r811-library-card-red.txt`.

## Requisitos

1. Restaurar o perfil com nome de apresentação exato **Library empty input
   audit**, idioma pt-BR, capacidade declarada e referência à SPEC R678.
2. Preservar as capacidades `library_empty_input_audit` e
   `empty_input_abstention`, carta estendida A2A e skill com exemplo explícito.
3. Orientar somente os métodos existentes de MarceloClaroOrchestrator:
   library_status, library_query, library_page e integration_status.
4. Permitir leitura, glob e grep, além dos comandos exatos dos testes R678,
   R677 e R669. Negar outros comandos, edição, acesso web e delegação direta.
5. Confirmar por R678/R669 o carregamento e a atribuição isolada pelo
   orquestrador, Blackboard/A2A e MetaBus. A tarefa permanece atribuída;
   registro ou encaminhamento não são inferência nem conclusão simulada.
6. Regenerar a configuração OpenCode pelo gerador existente no fechamento
   da revisão do ecossistema e conferir sua reprodução por R678. A restauração
   do perfil não altera o gerador, os testes ou outros cartões.

## Limites

A correção do comportamento de consultas vazias pertence a R677; esta rodada
restaura o perfil que orienta sua auditoria. Os testes de registro e roteamento
com entradas sintéticas são evidência operacional local, sem execução de LLM
ou validação científica externa. Nenhum método novo de orquestração é criado.
