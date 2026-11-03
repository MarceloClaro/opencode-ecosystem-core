---
spec_id: SPEC-935-R931
title: Contrato documental de piloto bibliográfico supervisionado
component: docs/piloto-pesquisa-r931
status: proposed
test_file: tests/test_r931_research_pilot_contract.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    fronteira:
    - tests/test_r931_research_pilot_contract.py::test_protocol_is_not_execution_or_release
    - tests/test_r931_research_pilot_contract.py::test_missing_human_inputs_are_explicit
    - tests/test_r931_research_pilot_contract.py::test_permissions_remain_closed
    desenho:
    - tests/test_r931_research_pilot_contract.py::test_proposed_limits_are_not_measured_or_authorized
    - tests/test_r931_research_pilot_contract.py::test_metrics_have_denominators_and_no_results
    - tests/test_r931_research_pilot_contract.py::test_bibliographic_audit_requires_source_support_and_legal_access
    passagem:
    - tests/test_r931_research_pilot_contract.py::test_gates_require_evidence_and_human_acceptance
    - tests/test_r931_research_pilot_contract.py::test_stop_and_recovery_are_planned_not_claimed
    rastreio:
    - tests/test_r931_research_pilot_contract.py::test_historical_evidence_is_separate_and_matches_receipts
    - tests/test_r931_research_pilot_contract.py::test_document_explains_scope_and_next_decision
---

# R931 — protocolo com pendências, não execução do piloto

## Escopo autorizado nesta etapa

O usuário pediu continuidade depois da recomendação de piloto bibliográfico.
Formalizar o protocolo e os gates é uma continuação segura; a frase não escolhe
tema, corpus, provedor, orçamento, destino de produção nem autoriza dados reais.
Entregar `docs/piloto-pesquisa-r931/contrato.json` e
`docs/PILOTO_PESQUISA_SUPERVISIONADO_R931.md`, com testes de integridade documental.
Não adicionar endpoint, executor, conector, agente permanente ou permissão.

Ler somente evidências Core explicitadas. Não iniciar buscas, baixar PDFs ou
checkpoints, treinar, publicar serviços, acessar dados pessoais/credenciais ou
alterar `.its-fine/policy.json`. Revisão de texto por agente já configurado não
é busca bibliográfica, execução do piloto ou revisão humana independente.

## Critérios de Aceitação Executáveis

- `fronteira` — status `protocol_with_pending_inputs`; execução, publicação,
  produção e validação externa falsas; escolhas não fornecidas permanecem nulas.
- `desenho` — propor 1 operador, 1 tarefa por vez e até 20 referências sem
  tratá-los como capacidade medida ou orçamento aprovado. Métricas propostas
  possuem unidade, população/denominador e resultados nulos. Corpus vazio não
  passa por verdade vacuosa; metadados corretos não comprovam suporte de alegação.
- `passagem` — gates G0–G5 pendentes, dependências explícitas, artefatos exigidos,
  responsável por papel e aceite humano ainda ausente. Parada/recuperação descritas
  como ensaios futuros, não controles end-to-end já comprovados. Nenhum gate ou
  teste documental concede autorização operacional.
- `rastreio` — contar R928=469 e R929=643 separadamente como evidências históricas;
  ler recibos arquivados sem reexecutar/revalidar suas árvores de fontes atuais.
  Manter advertência das 78 entradas e limitações de suíte upstream/GPU. Não
  transformar quantização sintética em qualidade de tarefa, SLA ou validade científica.

## Verificação desta entrega

Testes primeiro; RED observado por ausência dos entregáveis, depois GREEN.
Usar TDDHistory/SpecVerifier existentes, sem recibos retrospectivos fabricados.
O rótulo técnico `software_delivery_gate` do verificador aplica-se apenas ao
contrato documental R931: não é aceite de produção, estudo empírico ou validação
científica. Registrar gates, revisão recebida (ou bloqueio), lições e ciclo sem
score de qualidade. Preservar trabalho anterior/concomitante e não fazer commit.
