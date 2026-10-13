---
spec_id: SPEC-935-R863
title: Prontidão local e diagnóstico estrutural sem aprovação indevida
component: marceloclaro.doctor
status: implemented
test_file: tests/test_r863_local_provider_readiness.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    prontidao_local:
    - tests/test_r863_local_provider_readiness.py::test_binario_presente_nao_aprova_daemon_parado
    - tests/test_r863_local_provider_readiness.py::test_sonda_real_get_modelos_sem_inferencia
    - tests/test_r863_local_provider_readiness.py::test_sonda_recusa_catalogo_invalido
    - tests/test_r863_local_provider_readiness.py::test_sonda_recusa_redirect_sem_visitar_destino
    - tests/test_r863_local_provider_readiness.py::test_sonda_recusa_endpoint_nao_local_ou_com_segredo
    - tests/test_r863_local_provider_readiness.py::test_sonda_ignora_proxy_herdado
    - tests/test_r863_local_provider_readiness.py::test_sonda_recusa_resposta_acima_do_limite
    - tests/test_r863_local_provider_readiness.py::test_timeout_de_sonda_e_finito
    escopo:
    - tests/test_r863_local_provider_readiness.py::test_modo_estrutural_nao_sonda_http
    - tests/test_r863_local_provider_readiness.py::test_check_live_relata_prontidao_sem_inferencia
    - tests/test_r863_local_provider_readiness.py::test_check_live_indisponivel_avisa_sem_vazar_endpoint
    estrutura:
    - tests/test_r863_local_provider_readiness.py::test_specs_ambiguas_falham_mesmo_com_specs_unicas
    - tests/test_r863_local_provider_readiness.py::test_config_exige_primario_e_default_agent_corretos
    - tests/test_r863_local_provider_readiness.py::test_config_primario_valido_passa
---

# R863 — Prontidão operacional local

O diagnóstico `live=True` de Ollama não pode aprovar um daemon apenas por
localizar sua CLI. A sonda executa exclusivamente GET do catálogo `/api/tags`
em endpoint HTTP(S) loopback, com prazo finito, tamanho limitado, proxy herdado
desativado e redirects recusados. Catálogo vazio, formato inválido, falha de
conexão, prazo excedido ou configuração não local produzem estado tipado de
indisponibilidade; mensagens não reproduzem credenciais, URLs ou exceções.

GET e presença de modelos comprovam somente resposta HTTP e catálogo nesse
instante. Não comprovam carregamento do modelo, autenticação nem inferência.
O modo padrão `live=False` continua estrutural e não inicia a sonda.

Especificações com identidades ambíguas impedem aprovação do check formal,
mesmo quando outras especificações carregam. A configuração precisa definir
`agent.marceloclaro.mode=primary` e `default_agent=marceloclaro`. Nenhum gate SDD
é flexibilizado. RED e GREEN devem conservar contagem, fonte anterior e escopo;
resultado local não é validação externa do ecossistema.
