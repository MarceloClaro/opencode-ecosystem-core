---
spec_id: SPEC-935-R860
title: Correção de encaminhamento JavaScript e ativação isolada do agente REA
component: integrations.rea_assistant, integrations.rea_local_worker, marceloclaro.rea_cli
status: implemented
test_file: tests/test_r860_rea_runtime_review.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    encaminhamento:
    - tests/test_r860_rea_runtime_review.py::test_javascript_avulso_preserva_bytes_no_diretorio_estatico
    - tests/test_r860_rea_runtime_review.py::test_diretorio_e_asar_nao_sao_reempacotados
    configuracao:
    - tests/test_r860_rea_runtime_review.py::test_perfil_define_primario_e_modelo_auxiliar_locais
    - tests/test_r860_rea_runtime_review.py::test_lancamento_isola_configuracoes_e_credenciais
    - tests/test_r860_rea_runtime_review.py::test_lancamento_recusa_configuracao_resolvida_divergente
    - tests/test_r860_rea_runtime_review.py::test_cli_encaminha_agente_check_ao_primario
    - tests/test_r860_rea_runtime_review.py::test_servidor_mcp_reutiliza_primario
    relato:
    - tests/test_r860_rea_runtime_review.py::test_setup_texto_mostra_caminhos_sem_alegar_inspecao
    - tests/test_r860_rea_runtime_review.py::test_status_nao_aprova_guard_falho
    - tests/test_r860_rea_runtime_review.py::test_worker_preserva_erro_local_estruturado
    - tests/test_r860_rea_runtime_review.py::test_timeout_booleano_recusado
    - tests/test_r860_rea_runtime_review.py::test_explicacao_expoe_metadados_reais_sem_inventar_comportamento
    - tests/test_r860_rea_runtime_review.py::test_explicacao_expoe_funcao_nativa_com_limite_estatico
---

# R860 — Revisão da integração REA por execução real

A inspeção de `app.js` retornou `unsupported_target`: o REA aceita diretório ou
`.asar` em `analyze_javascript_application`. O assistente deve preparar uma cópia
temporária dos mesmos bytes para esse contrato, registrar a adaptação e limitar
conclusões sobre imports/arquivos vizinhos ausentes. Diretórios e `.asar` seguem
sem reempacotamento. Nenhuma aplicação alvo é executada.

`opencode debug config` executado com `OPENCODE_CONFIG` demonstrou que a
configuração do projeto sobrepõe o modelo e reativa os 16 MCPs herdados. Portanto
o arquivo gerado sozinho não comprova ativação. O lançamento deve usar diretório
de trabalho temporário fora do projeto, HOME/XDG próprios sem credenciais ou
plugins herdados, configuração inline local, primário e modelo auxiliar locais,
atualização/downloads automáticos desligados. `rea agent --check` confere a
configuração resolvida no OpenCode instalado antes de qualquer conversa.

## Critérios de Aceitação Executáveis

- `encaminhamento` — bytes originais conservados e caminho compatível com REA;
  adaptação explícita e remoção do diretório temporário ao sair.
- `configuracao` — fluxo CLI pelo primário, ambiente próprio, nenhuma credencial
  externa herdada; perfil somente modelo loopback e quatro tools locais. O modo
  check não executa inferência e recusa configurações resolvidas divergentes.
- `relato` — setup legível com caminhos; guard falho não resulta em prontidão
  aprovada; erros estruturados e prazo inválido são recusados, sem sucesso falso.

O cliente e o servidor de modelo precisam permanecer locais. O worker analítico
continua isolado em namespaces de rede/PID; isso não constitui sandbox universal
do filesystem. Testes com adaptadores não são inferência de agente: separar do
check real da configuração, análises CLI/MCP e inspeção visual do site.
