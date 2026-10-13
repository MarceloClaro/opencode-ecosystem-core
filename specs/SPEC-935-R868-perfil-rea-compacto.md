---
spec_id: SPEC-935-R868
title: Perfil local REA com instrução própria compacta e conferência efetiva
component: integrations.rea_assistant
status: implemented
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    perfil:
    - tests/test_r868_rea_profile_prompt.py::test_setup_has_own_bounded_local_prompt
    efetivo:
    - tests/test_r868_rea_profile_prompt.py::test_resolved_prompt_is_part_of_launch_guard
    evidencia:
    - tests/test_r868_rea_profile_prompt.py::test_free_model_text_is_never_accepted_as_analysis
    - tests/test_r868_rea_profile_prompt.py::test_tool_error_and_spoofed_text_event_are_rejected
    - tests/test_r868_rea_profile_prompt.py::test_readiness_tool_is_not_promoted_to_target_analysis
    - tests/test_r868_rea_profile_prompt.py::test_actual_receipt_wins_over_model_text
    padrao:
    - tests/test_r868_rea_profile_prompt.py::test_generated_default_uses_local_tool_capable_model
    argumentos:
    - tests/test_r868_mcp_arguments.py::test_empty_optional_arguments_use_declared_defaults
    - tests/test_r868_mcp_arguments.py::test_invalid_timeout_never_reaches_primary
    - tests/test_r868_mcp_arguments.py::test_numeric_timeout_is_preserved
    limpeza:
    - tests/test_r868_agent_process_cleanup.py::test_timeout_encerra_cliente_e_filho_em_sessao_independente
    - tests/test_r868_agent_process_cleanup.py::test_debug_config_timeout_encerra_descendentes
    - tests/test_r868_agent_process_cleanup.py::test_saida_normal_do_lider_encerra_filho_independente
    - tests/test_r868_agent_process_cleanup.py::test_cancelamento_antes_do_cliente_nao_inicia_processos
    - tests/test_r868_agent_process_cleanup.py::test_cancelamento_durante_cliente_aguarda_limpeza
    - tests/test_r868_agent_process_cleanup.py::test_modo_interativo_tambem_limpa_no_cancelamento
    - tests/test_r868_agent_process_cleanup.py::test_cliente_bloqueia_sem_namespace_linux
---

# R868 — Perfil local utilizável

O perfil REA não declarava prompt próprio. O OpenCode aplicava seu prompt geral
de programação, grande para a máquina local. A tentativa com Qwen3 8B excedeu
300 segundos e coincidiu com perda de resposta do WSL durante compilação Lean.
Essas tentativas não foram aprovadas. O perfil dedicado deve conter instrução
compacta de análise local, sem a carga do agente de programação geral.

## Critérios de Aceitação Executáveis

- `perfil` — setup declara prompt local próprio, conciso, ferramentas MCP,
  evidências/limitações e ausência de execução de aplicações alvo. O modelo
  declara capacidade de ferramentas e limites de contexto/saída no perfil,
  sem habilitar um executor genérico de scripts. Capacidade declarada não é
  prova de chamada; a execução real permanece requisito separado.
- `efetivo` — launcher confere o prompt resolvido juntamente com os demais
  campos do modo local, mapas completos de ferramentas/permissões e limites;
  uma permissão específica inesperada não passa por ter curingas restritivos.
  Divergência impede iniciar inferência.
- `evidencia` — saída --prompt usa eventos estruturados e recibo local íntegro;
  não publica achados inventados após erro de ferramenta. Explicação publicada
  é determinística e baseada no recibo, mesmo quando o texto do modelo diverge.
  Status bem-sucedido é somente prontidão, nunca análise de alvo.
- `padrao` — a configuração gerada usa o modelo Ollama local com capacidade de
  ferramentas, disponível na sonda executada, conservando as demais opções.
- `limpeza` — debug config, execução finita e cliente interativo possuem grupo
  exclusivo e namespace PID Linux/WSL, conservando a rede do host para o modelo
  loopback. Timeout, cancelamento e saída normal encerram seus descendentes,
  inclusive os que criam nova sessão; a limpeza termina antes do retorno.
  Cancelamento anterior não inicia o cliente. Sem namespace, o modo local fica
  bloqueado. Essa supervisão de processos não constitui sandbox de arquivos ou
  isolamento de rede do cliente; análise continua usando seu worker separado.
- `argumentos` — MCP recusa booleanos, strings numéricas, valores nulos,
  não finitos e prazos fora de zero exclusivo a 180 inclusivo antes do primário.
  O único marcador textual vazio significa ausência do argumento opcional e
  recebe o default declarado de 60 segundos; vazio em kind/procedure recebe
  auto/main. Nenhum outro valor é convertido para simular entrada válida.

Teste de configuração não comprova inferência. A operação real precisa de
modelo disponível e recibos da ferramenta. Instalações e estado do perfil são
locais e não integram o commit. Não se promete desempenho ou qualidade universal.
