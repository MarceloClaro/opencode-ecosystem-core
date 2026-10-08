---
spec_id: SPEC-935-R678
title: Especialista de auditoria de entradas vazias da biblioteca
status: red
validation_scope: local_a2a_routing
test_file: tests/test_r678_library_empty_input_specialist.py
---

# R678 — Library empty input audit

## Solicitação e contrato

Registrar o especialista solicitado com o nome de apresentação exato
**Library empty input audit**, linguagem pt-BR e capacidade declarada.
O ponto de entrada permanece MarceloClaroOrchestrator: registro e atribuição
de tarefa pelo Blackboard/A2A, com memória metacognitiva no MetaBus.

O procedimento examina o comportamento corrigido em R677: consultas sem
conteúdo útil devem produzir abstenção e solicitação inválida antes de acessar
PDFs ou o índice. O cartão orienta somente os métodos centrais existentes
library_status, library_query, library_page e integration_status.
O especialista possui leitura e execução explícita dos testes de auditoria,
sem permissão para edição ou delegação direta a outros perfis.

## Critérios de aceitação

1. RED real antes de criar o cartão; GREEN após sua implementação.
2. Carregamento do catálogo, bootstrap e compilação OpenCode concordam com
   nome, skills, tags, métodos e permissões explícitas.
3. Atribuição real isolada ALL_OF seleciona o novo perfil; capacidade ausente
   preserva tarefa sem atribuição.
4. Eventos de CFP e atribuição passam pelo orquestrador e Blackboard; nenhuma
   tarefa é marcada como concluída nem se declara inferência executada.
5. opencode.json reproduz a configuração gerada e inclui o perfil.
6. Contagens atuais da documentação acompanham a configuração; contagens
   históricas permanecem preservadas.

## Limites da evidência

Estes testes provam os contratos do perfil e o encaminhamento central local.
A correção de entradas vazias e suas contraprovas pertencem a R677.
Nem atribuição A2A nem permissão para testes constituem auditoria científica
externa, treinamento ou melhoria cognitiva medida.
