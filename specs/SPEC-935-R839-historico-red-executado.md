---
spec_id: SPEC-935-R839
title: Histórico RED executado e gate de entrega
status: proposed
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    historico:
    - tests/test_r839_tdd_history.py::test_ciclo_real_preserva_teste_e_ignora_status_mutavel
    - tests/test_r839_tdd_history.py::test_green_sem_red_nao_e_entrega_aceita
    - tests/test_r839_tdd_history.py::test_falha_sem_assercao_executada_nao_e_red
    - tests/test_r839_tdd_history.py::test_timeout_nao_e_red
    - tests/test_r839_tdd_history.py::test_mudar_teste_ou_spec_nao_reutiliza_par
    - tests/test_r839_tdd_history.py::test_par_nao_cruza_identificador_de_spec
    - tests/test_r839_tdd_history.py::test_adulteracao_de_payload_e_junit_e_detectada
    - tests/test_r839_tdd_history.py::test_adulteracao_da_cadeia_ou_traversal_e_detectada
    - tests/test_r839_tdd_history.py::test_red_aposteriori_nao_autentica_green_anterior
    - tests/test_r839_tdd_history.py::test_alteracao_de_fonte_durante_pytest_nao_e_red
    - tests/test_r839_tdd_history.py::test_chave_privada_fora_de_outputs_e_sem_leitura_publica
    - tests/test_r839_tdd_history.py::test_processos_filhos_da_fase_sao_encerrados_apos_saida_do_pytest
    - tests/test_r839_tdd_history.py::test_mudar_fixture_do_oraculo_nao_converte_red_em_green
    - tests/test_r839_tdd_history.py::test_green_nao_autentica_codigo_typescript_posteriormente_alterado
    - tests/test_r839_tdd_history.py::test_mudar_suporte_ou_configuracao_do_oraculo_invalida_red
    - tests/test_r839_tdd_history.py::test_addopts_nao_desvia_execucao_do_alvo_da_spec
    - tests/test_r839_tdd_history.py::test_escopo_fora_da_arvore_tests_e_recusado
    entrega:
    - tests/test_r839_red_delivery.py::test_green_real_sem_red_historico_nao_conclui_entrega
    - tests/test_r839_red_delivery.py::test_par_red_green_real_permite_entrega_da_mesma_spec
    - tests/test_r839_red_delivery.py::test_autocorrecao_sem_red_bloqueia_antes_de_aplicar_patch
    - tests/test_r839_red_delivery.py::test_refactor_que_quebra_codigo_nao_conclui_ciclo
    - tests/test_r839_red_delivery.py::test_autocorrecao_com_red_real_aplica_e_registra_green
    - tests/test_r839_red_delivery.py::test_preflight_recusa_historico_de_outra_raiz
    verificador:
    - tests/test_r839_verifier_delivery.py::test_spec_r839_possui_contrato_executavel_valido
    - tests/test_r839_verifier_delivery.py::test_programmatic_software_spec_is_not_delivery_without_red_or_green
    - tests/test_r839_verifier_delivery.py::test_runtime_green_object_cannot_replace_executed_red
    - tests/test_r839_verifier_delivery.py::test_criteria_inspection_is_explicit_and_does_not_promote_confidence
    - tests/test_r839_verifier_delivery.py::test_inspecao_de_software_nao_promove_estado_nem_evento
component: sdd.tdd_history
---

# R839 — Histórico RED→GREEN executado

Pedido explícito: resolver a exigência de RED histórico que permanecia pendente.
Não é permitido reconstruir um RED inexistente nem aceitar hash/flag fornecido
pelo agente como prova de uma execução anterior.

## Contrato de execução

1. `sdd.tdd_history.TDDHistory.run(spec, phase, timeout_seconds)` executa pytest
   real com JUnit, captura saída, bytes dos testes, fingerprint da especificação,
   revisão e hashes das fontes, timestamps e código de retorno. Não chama um LLM.
2. RED válido exige falha de asserção na execução de pelo menos um teste, sem
   erro de coleta/importação, timeout, skip ou xfail. GREEN válido exige execução
   aprovada do mesmo conjunto de testes. Contadores são derivados do JUnit.
3. A conclusão do RED precede o início do GREEN. ID/fingerprint da spec, alvos
   e hashes dos testes devem coincidir; mudar o teste ou critério invalida o par.
   Mudanças da implementação são esperadas e registradas, sem exigir hash de
   implementação idêntico entre fases.
   A árvore `tests`, conftests e configurações de raiz integram a versão do
   oráculo; arquivos de cache são excluídos. Pytest não carrega conftests acima
   da raiz (`confcutdir`). O manifesto cobre
   fontes Python/TypeScript/JavaScript/C/C++/Rust/Go/Lean e as configurações
   enumeradas pelo runtime; o GREEN não autentica alterações posteriores.
4. Recibos e artefatos ficam em histórico local com assinatura, cadeia de hashes
   e escrita atômica. Validação recusa adulteração, travessia de caminho, fases
   inconsistentes, pares de specs diferentes e histórico ausente. A chave local
   não é exibida nem armazenada junto de artefatos públicos.
5. O gate de entrega de software do primário exige esse par, além da evidência
   GREEN emitida pelo runner. Verificação de critérios/planejamento separada
   pode permanecer disponível, mas não pode ser confundida com aceite de entrega.
   Contratos com `test_file` e contratos Markdown exigentes não possuem bypass
   por modo legado, flag `tests_green` ou dados trazidos pelo executor.
   `SpecVerifier` usa esse gate por padrão para software. Inspeção explícita com
   `require_red_history=False` declara `criteria_only` e não promove confiança;
   o primário não usa essa exceção para entregas de software.
   Execução autônoma estrita confere spec/RED antes da inferência e permite
   vincular `--spec`. Autocorreção confere antes do patch. Refatoração reprovada
   fecha o ciclo sem declarar rollback inexistente.
6. O comando coordenado permite registrar RED antes da edição. Se a versão atual
   já está verde e não há RED histórico autenticável, o gate permanece fechado.
   Reprodução de uma versão anterior deve ser identificada como reexecução local
   dessa versão, com proveniência; não se inventa uma execução no passado.

## Verificação

## Critérios de Aceitação Executáveis

- `historico` — as fases reais, seus vínculos e casos adversariais passam.
- `entrega` — GREEN isolado é negado; par real autoriza a mesma spec.
- `verificador` — default de software exige histórico; inspeção é explícita.

Testes novos R839: ciclo real em projeto temporário com implementação incorreta
e teste estável; depois correção e GREEN. Casos de negação: somente GREEN,
importação/coleta, zero testes, skips, alteração dos testes/spec, receipt/payload
adulterado, cruzamento de spec, ordem temporal e falha de persistência.
Integração do primário deve negar recompensa e conclusão quando faltar RED,
inclusive com GREEN real. Regressão dos contratos SDD existentes distingue
inspeção estrutural de gate de entrega. Logs em `outputs/core-r839/`.

## Limites

Evidência de processo local não valida a qualidade do oráculo de teste nem é
atestação externa. Usuário/processo com acesso à mesma chave ou ao código pode
subverter o runtime; a assinatura detecta alterações de artefatos, não fornece
isolamento contra o dono do host. Histórico anterior incompleto permanece
identificado como incompleto, sem backfill fictício.
