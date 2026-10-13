---
spec_id: SPEC-935-R861
title: Aceite integrado local do assistente REA após revisão R860
component: integrations.rea_assistant, webapp.rea_assistant_site, marceloclaro.rea_cli
status: implemented
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    assistente:
    - tests/test_r850_rea_assistant_local.py::test_ida_rejeita_endpoint_remoto
    - tests/test_r850_rea_assistant_local.py::test_url_local_rejeita_porta_invalida
    - tests/test_r850_rea_assistant_local.py::test_camada_rejeita_dict_sem_evidence
    - tests/test_r850_rea_assistant_local.py::test_descoberta_observa_instalacao_no_mesmo_processo
    - tests/test_r850_rea_assistant_local.py::test_ambiente_de_worker_nao_leva_credenciais
    - tests/test_r850_rea_assistant_local.py::test_namespace_real_isola_rede_do_host
    - tests/test_r850_rea_assistant_local.py::test_detecta_tipos_sem_executar_alvo
    - tests/test_r850_rea_assistant_local.py::test_explicacao_distingue_achados_e_limites
    - tests/test_r850_rea_assistant_local.py::test_cli_encaminha_setup_e_inspect_ao_primario
    - tests/test_r850_rea_assistant_local.py::test_setup_registra_perfil_local_sem_alterar_config_global
    - tests/test_r850_rea_assistant_local.py::test_setup_rejeita_endpoint_de_modelo_remoto
    - tests/test_r850_rea_assistant_local.py::test_mcp_expoe_somente_interface_local
    site:
    - tests/test_r851_rea_assistant_site.py::test_loopback_e_recursos_publicos
    - tests/test_r851_rea_assistant_site.py::test_host_externo_duplicado_ou_ausente_e_recusado
    - tests/test_r851_rea_assistant_site.py::test_origin_externo_e_recusado
    - tests/test_r851_rea_assistant_site.py::test_caminhos_do_repositorio_nao_sao_expostos
    - tests/test_r851_rea_assistant_site.py::test_traversal_e_caminho_nao_canonico_sao_recusados
    - tests/test_r851_rea_assistant_site.py::test_metodos_que_podem_enviar_dados_sao_recusados
    - tests/test_r851_rea_assistant_site.py::test_politica_do_navegador_bloqueia_conexoes_e_enquadramento
    - tests/test_r851_rea_assistant_site.py::test_pagina_tem_recursos_locais_e_comandos_associados
    - tests/test_r851_rea_assistant_site.py::test_copia_comando_e_informa_sucesso_no_cliente
    - tests/test_r851_rea_assistant_site.py::test_falha_de_copia_informa_como_prosseguir
    - tests/test_r851_rea_assistant_site.py::test_copia_alternativa_sem_clipboard_api
    revisao:
    - tests/test_r860_rea_runtime_review.py::test_javascript_avulso_preserva_bytes_no_diretorio_estatico
    - tests/test_r860_rea_runtime_review.py::test_diretorio_e_asar_nao_sao_reempacotados
    - tests/test_r860_rea_runtime_review.py::test_perfil_define_primario_e_modelo_auxiliar_locais
    - tests/test_r860_rea_runtime_review.py::test_lancamento_isola_configuracoes_e_credenciais
    - tests/test_r860_rea_runtime_review.py::test_lancamento_recusa_configuracao_resolvida_divergente
    - tests/test_r860_rea_runtime_review.py::test_cli_encaminha_agente_check_ao_primario
    - tests/test_r860_rea_runtime_review.py::test_servidor_mcp_reutiliza_primario
    - tests/test_r860_rea_runtime_review.py::test_setup_texto_mostra_caminhos_sem_alegar_inspecao
    - tests/test_r860_rea_runtime_review.py::test_status_nao_aprova_guard_falho
    - tests/test_r860_rea_runtime_review.py::test_worker_preserva_erro_local_estruturado
    - tests/test_r860_rea_runtime_review.py::test_timeout_booleano_recusado
    - tests/test_r860_rea_runtime_review.py::test_explicacao_expoe_metadados_reais_sem_inventar_comportamento
    - tests/test_r860_rea_runtime_review.py::test_explicacao_expoe_funcao_nativa_com_limite_estatico
---

# R861 — Aceite integrado local do REA

Consolida os contratos de backend R850, site R851 e correções R860 sem alterar
os oráculos existentes. O gate do primário executa somente os nodeids explícitos
das três baterias, não a pasta inteira. Não equivale a validação externa.

## Critérios de Aceitação Executáveis

- `assistente` — ambiente sem credenciais, namespace real sem conexão ao host,
  caminhos/formatos e Evidence identificada, setup e MCP restritos.
- `site` — HTTP loopback com allowlist, origem/caminho/métodos recusados, assets
  locais e interação de cópia; inspeção visual real registrada separadamente.
- `revisao` — arquivo JS avulso adaptado ao contrato REA, cliente fora do projeto
  com configuração efetiva conferida, guard/erros/prazos sem sucesso falso e
  explicações baseadas nos campos presentes na Evidence.

O RED integrado é uma reexecução do baseline R860 conservado antes das correções:
alguns contratos R850/R851 já passavam nesse baseline. Ela não recria eventos
históricos ausentes. Os REDs anteriores, incluindo bootstrap e scaffold da
interface, permanecem preservados e classificados. GREEN exige os mesmos
oráculos, fontes estáveis e aceitação pelo SpecVerifier do primário.

O worker e seus descendentes usam rede privada. O cliente MCP e o servidor de
modelo precisam conservar processamento local. Configuração resolvida não
comprova inferência, e alvos controlados não demonstram qualidade universal.
