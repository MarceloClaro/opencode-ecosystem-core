---
spec_id: SPEC-935-R869
title: Entregar o prompt pela entrada padrão dos executores CLI
component: integrations.harness_runtime
status: implemented
test_file: tests/test_r869_cli_real_transport.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    entrada:
    - tests/test_r869_cli_real_transport.py::test_prompt_unicode_vai_pela_entrada_padrao
    - tests/test_r869_cli_real_transport.py::test_prompt_grande_preserva_bytes_apos_communicate_retornar_timeout
    - tests/test_r869_cli_real_transport.py::test_entrada_vazia_fecha_pipe_sem_bloquear
    execucao:
    - tests/test_r869_cli_real_transport.py::test_executor_controlado_recebe_contexto_sem_prompt_em_argv
    cancelamento:
    - tests/test_r869_cli_real_transport.py::test_cancelamento_antes_da_cli_nao_inicia_processo
    - tests/test_r869_cli_real_transport.py::test_cancelamento_durante_envio_encerra_processo
    caminhos:
    - tests/test_r869_cli_real_transport.py::test_caminho_windows_permanece_canonico
---

# R869 — Transporte real de texto para a CLI

A chamada retirava `input` das opções, mas não criava `stdin=PIPE` no Popen.
Assim, o prompt não chegava ao executor que espera texto pela entrada padrão;
o Codex Windows registrou a recusa "No prompt provided via stdin.". Inventário
e testes com runner substituído não detectavam esse defeito de transporte.

## Critérios de Aceitação Executáveis

- `entrada` — processo Python real lê os mesmos bytes UTF-8 enviados pelo
  chamador. Payload grande e retomadas de `communicate` após timeout parcial
  não descartam nem duplicam bytes. Entrada vazia fornece EOF sem bloquear.
- `execucao` — executor controlado recebe o contexto, preserva modo somente de
  leitura e argumentos separados; o prompt não é acrescentado aos argumentos.
- `cancelamento` — cancelamento anterior não inicia a CLI; cancelamento durante
  o envio aguarda seu encerramento e não deixa a fixture executando.
- `caminhos` — conversões Windows existentes são absolutas e canônicas segundo
  PureWindowsPath. UNC possui duas barras iniciais físicas; quatro caracteres
  de escape numa representação JSON não são quatro barras no caminho real.

As contraprovas executam somente fixtures conhecidas, sem inferência ou alvo de
terceiros. A correção não altera sandbox, permissões, roteamento ou construção
de caminhos já canônicos. A execução real do agente exige validação separada.
